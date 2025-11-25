import streamlit as st
import instaloader
import sqlite3
from datetime import datetime
import pandas as pd
import os
import time

# Sayfa yapılandırması
st.set_page_config(page_title="Instagram Takipçi Tracker", page_icon="--", layout="wide")

# Veritabanı fonksiyonları
def init_db():
    conn = sqlite3.connect('instagram_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instagram_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        followers INTEGER,
        following INTEGER,
        posts INTEGER,
        full_name TEXT,
        biography TEXT,
        is_private BOOLEAN,
        is_verified BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def save_profile(profile):
    conn = sqlite3.connect('instagram_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO instagram_profiles 
    (username, followers, following, posts, full_name, biography, is_private, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        profile.username,
        profile.followers,
        profile.followees,
        profile.mediacount,
        profile.full_name,
        profile.biography,
        profile.is_private,
        profile.is_verified
    ))
    conn.commit()
    conn.close()

def get_all_profiles():
    conn = sqlite3.connect('instagram_data.db')
    df = pd.read_sql_query('SELECT * FROM instagram_profiles ORDER BY created_at DESC', conn)
    conn.close()
    return df

def get_profile_history(username):
    conn = sqlite3.connect('instagram_data.db')
    df = pd.read_sql_query(
        'SELECT * FROM instagram_profiles WHERE username = ? ORDER BY created_at DESC', 
        conn, 
        params=(username,)
    )
    conn.close()
    return df

# Instagram loader oluşturma
@st.cache_resource
def get_instaloader():
    L = instaloader.Instaloader()
    # Rate limiting için bekleme süreleri
    L.max_connection_attempts = 3
    return L

# Veritabanını başlat
init_db()

# Streamlit UI
st.title("Instagram Takipçi Tracker")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Ayarlar")
    
    st.info("""
    **Not:** Instagram bot koruması nedeniyle:
    - Çok sık sorgu yapmayın
    - Aralarında 5-10 saniye bekleyin
    - Büyük hesaplar için login gerekebilir
    """)
    
    # Rate limiting ayarı
    rate_limit = st.slider("Sorgular arası bekleme (saniye)", 5, 30, 10)
    st.session_state['rate_limit'] = rate_limit
    
    st.markdown("---")
    page = st.radio("Sayfa Seç", ["Profil Sorgula", "Geçmiş Veriler"])

# Ana içerik
if page == "Profil Sorgula":
    st.header("Instagram Profil Sorgula")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        username = st.text_input("Instagram kullanıcı adını girin:", placeholder="örn: cristiano")
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("Sorgula", use_container_width=True)
    
    if search_button and username:
        # Rate limiting kontrolü
        if 'last_query_time' in st.session_state:
            elapsed = time.time() - st.session_state['last_query_time']
            if elapsed < st.session_state.get('rate_limit', 10):
                wait_time = int(st.session_state.get('rate_limit', 10) - elapsed)
                st.warning(f"Lütfen {wait_time} saniye bekleyin...")
                st.stop()
        
        with st.spinner(f'@{username} profili sorgulanıyor...'):
            try:
                L = get_instaloader()
                
                # Profil bilgilerini çek (login olmadan)
                profile = instaloader.Profile.from_username(L.context, username)
                
                # Son sorgu zamanını kaydet
                st.session_state['last_query_time'] = time.time()
                
                # Veritabanına kaydet
                save_profile(profile)
                
                st.success("Profil bilgileri başarıyla kaydedildi!")
                
                # Profil bilgilerini göster
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Takipçi", f"{profile.followers:,}")
                
                with col2:
                    st.metric("Takip", f"{profile.followees:,}")
                
                with col3:
                    st.metric("Gönderi", f"{profile.mediacount:,}")
                
                with col4:
                    engagement = (profile.followers / profile.mediacount) if profile.mediacount > 0 else 0
                    st.metric("Ort. Etkileşim", f"{engagement:.0f}")
                
                st.markdown("---")
                
                # Detaylı bilgiler
                with st.expander("Detaylı Profil Bilgileri", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Kullanıcı Adı:** @{profile.username}")
                        st.write(f"**Tam Ad:** {profile.full_name}")
                        st.write(f"**Özel Hesap:** {'Evet' if profile.is_private else 'Hayır'}")
                        st.write(f"**Onaylı Hesap:** {'Evet' if profile.is_verified else 'Hayır'}")
                    
                    with col2:
                        if profile.biography:
                            st.write(f"**Biyografi:**")
                            st.info(profile.biography)
                
            except instaloader.exceptions.ProfileNotExistsException:
                st.error("Bu kullanıcı adı bulunamadı!")
            except instaloader.exceptions.ConnectionException as e:
                st.error(f"Bağlantı hatası! Instagram geçici olarak engellemiş olabilir.")
                st.info("Çözüm: Birkaç dakika bekleyin veya daha az sıklıkta sorgu yapın.")
            except instaloader.exceptions.QueryReturnedBadRequestException:
                st.error("Instagram sorgu limitine ulaştınız. Lütfen 15-30 dakika bekleyin.")
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
                st.info("Instagram bot koruması nedeniyle geçici olarak erişim engellenmiş olabilir.")

elif page == "Geçmiş Veriler":
    st.header("Geçmiş Sorgular")
    
    df = get_all_profiles()
    
    if not df.empty:
        # İstatistikler
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Toplam Sorgu", len(df))
        
        with col2:
            unique_users = df['username'].nunique()
            st.metric("Benzersiz Kullanıcı", unique_users)
        
        with col3:
            total_followers = df['followers'].sum()
            st.metric("Toplam Takipçi", f"{total_followers:,}")
        
        st.markdown("---")
        
        # Kullanıcı seçimi
        users = df['username'].unique().tolist()
        selected_user = st.selectbox("Kullanıcı Seç:", ["Tümü"] + users)
        
        if selected_user != "Tümü":
            df_filtered = get_profile_history(selected_user)
            st.subheader(f"@{selected_user} Geçmişi")
            
            if len(df_filtered) > 1:
                # Takipçi değişim grafiği
                df_chart = df_filtered.copy()
                df_chart['created_at'] = pd.to_datetime(df_chart['created_at'])
                df_chart = df_chart.sort_values('created_at')
                
                st.line_chart(df_chart.set_index('created_at')['followers'])
        else:
            df_filtered = df
        
        # Tablo gösterimi
        st.subheader("Sorgulanan Profiller")
        
        display_df = df_filtered[['username', 'followers', 'following', 'posts', 'is_verified', 'created_at']].copy()
        display_df.columns = ['Kullanıcı Adı', 'Takipçi', 'Takip', 'Gönderi', 'Onaylı', 'Tarih']
        display_df['Onaylı'] = display_df['Onaylı'].apply(lambda x: 'Evet' if x else 'Hayır')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # CSV indirme
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="CSV olarak İndir",
            data=csv,
            file_name=f"instagram_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Henüz sorgulama yapılmamış. Profil sorgula sayfasından başlayın!")

st.markdown("---")
st.caption("Instagram Takipçi Tracker - Streamlit ile geliştirildi")
