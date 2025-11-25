import streamlit as st
import instaloader
import sqlite3
from datetime import datetime
import pandas as pd

# Sayfa yapılandırması
st.set_page_config(page_title="Instagram Takipçi Tracker", page_icon="📱", layout="wide")

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

# Instagram login fonksiyonu
@st.cache_resource
def get_instaloader_session(ig_username, ig_password):
    try:
        L = instaloader.Instaloader()
        L.login(ig_username, ig_password)
        return L, None
    except Exception as e:
        return None, str(e)

# Veritabanını başlat
init_db()

# Streamlit UI
st.title("Instagram Takipçi Tracker")
st.markdown("---")

# Sidebar - Login
with st.sidebar:
    st.header("Ayarlar")
    
    # Instagram Login
    with st.expander("Instagram Girişi", expanded=True):
        ig_username = st.text_input("Instagram Kullanıcı Adı", key="ig_user")
        ig_password = st.text_input("Instagram Şifre", type="password", key="ig_pass")
        login_button = st.button("Giriş Yap")
        
        if login_button and ig_username and ig_password:
            with st.spinner("Giriş yapılıyor..."):
                L, error = get_instaloader_session(ig_username, ig_password)
                if L:
                    st.session_state['logged_in'] = True
                    st.session_state['loader'] = L
                    st.success("Giriş başarılı!")
                else:
                    st.error(f"Giriş başarısız: {error}")
        
        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            st.success("Giriş yapıldı")
    
    st.markdown("---")
    page = st.radio("Sayfa Seç", ["Profil Sorgula", "Geçmiş Veriler"])

# Ana içerik
if page == "Profil Sorgula":
    st.header("Instagram Profil Sorgula")
    
    # Login kontrolü
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Lütfen önce Instagram hesabınızla giriş yapın (Sol menüden)")
        st.stop()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        username = st.text_input("Instagram kullanıcı adını girin:", placeholder="örn: cristiano")
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("Sorgula", use_container_width=True)
    
    if search_button and username:
        with st.spinner(f'@{username} profili sorgulanıyor...'):
            try:
                L = st.session_state['loader']
                profile = instaloader.Profile.from_username(L.context, username)
                
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
            except instaloader.exceptions.ConnectionException:
                st.error("Bağlantı hatası! Lütfen tekrar giriş yapın.")
            except instaloader.exceptions.TwoFactorAuthRequiredException:
                st.error("İki faktörlü doğrulama gerekli!")
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")

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
