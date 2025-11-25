import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import re

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

def save_profile_data(data):
    conn = sqlite3.connect('instagram_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO instagram_profiles 
    (username, followers, following, posts, full_name, biography, is_private, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['username'],
        data['followers'],
        data['following'],
        data['posts'],
        data.get('full_name', ''),
        data.get('biography', ''),
        data.get('is_private', False),
        data.get('is_verified', False)
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

# Web scraping deneme (bazen çalışır)
def try_scrape_instagram(username):
    try:
        url = f"https://www.instagram.com/{username}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # JSON verisi bul
            pattern = r'window\._sharedData = ({.*?});'
            match = re.search(pattern, response.text)
            
            if match:
                data = json.loads(match.group(1))
                user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
                
                return {
                    'username': user_data['username'],
                    'followers': user_data['edge_followed_by']['count'],
                    'following': user_data['edge_follow']['count'],
                    'posts': user_data['edge_owner_to_timeline_media']['count'],
                    'full_name': user_data['full_name'],
                    'biography': user_data['biography'],
                    'is_private': user_data['is_private'],
                    'is_verified': user_data['is_verified']
                }, None
        
        return None, "Scraping başarısız"
    
    except Exception as e:
        return None, str(e)

# Veritabanını başlat
init_db()

# Streamlit UI
st.title("Instagram Takipçi Tracker")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Veri Girişi Yöntemi")
    method = st.radio("Yöntem Seç:", ["Manuel Giriş", "Otomatik Deneme"])
    
    st.info("""
    **Manuel Giriş:**
    Instagram'da hesabı ziyaret edin ve bilgileri manuel girin.
    
    **Otomatik Deneme:**
    Web scraping dener (başarı şansı düşük)
    """)
    
    st.markdown("---")
    page = st.radio("Sayfa Seç", ["Profil Ekle", "Geçmiş Veriler"])

# Ana içerik
if page == "Profil Ekle":
    st.header("Instagram Profil Ekle")
    
    if method == "Manuel Giriş":
        st.info("Instagram'da hesabı açın ve bilgileri aşağıya girin:")
        
        with st.form("manual_entry"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Kullanıcı Adı (@ olmadan)*", placeholder="cristiano")
                followers = st.number_input("Takipçi Sayısı*", min_value=0, step=1)
                following = st.number_input("Takip Sayısı*", min_value=0, step=1)
                posts = st.number_input("Gönderi Sayısı*", min_value=0, step=1)
            
            with col2:
                full_name = st.text_input("Tam Ad", placeholder="Cristiano Ronaldo")
                biography = st.text_area("Biyografi", placeholder="Profil açıklaması...")
                is_private = st.checkbox("Özel Hesap")
                is_verified = st.checkbox("Onaylı Hesap")
            
            submit = st.form_submit_button("Kaydet", use_container_width=True)
            
            if submit:
                if username and followers >= 0 and following >= 0 and posts >= 0:
                    profile_data = {
                        'username': username,
                        'followers': followers,
                        'following': following,
                        'posts': posts,
                        'full_name': full_name,
                        'biography': biography,
                        'is_private': is_private,
                        'is_verified': is_verified
                    }
                    
                    save_profile_data(profile_data)
                    st.success(f"@{username} başarıyla kaydedildi!")
                    
                    # Özet göster
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Takipçi", f"{followers:,}")
                    with col2:
                        st.metric("Takip", f"{following:,}")
                    with col3:
                        st.metric("Gönderi", f"{posts:,}")
                    with col4:
                        engagement = (followers / posts) if posts > 0 else 0
                        st.metric("Ort. Etkileşim", f"{engagement:.0f}")
                else:
                    st.error("Lütfen zorunlu alanları doldurun!")
    
    else:  # Otomatik Deneme
        st.warning("Bu yöntem Instagram'ın engelleri nedeniyle çalışmayabilir")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            username = st.text_input("Instagram kullanıcı adı:", placeholder="cristiano")
        
        with col2:
            st.write("")
            st.write("")
            search_button = st.button("Dene", use_container_width=True)
        
        if search_button and username:
            with st.spinner(f"@{username} profili çekiliyor..."):
                profile_data, error = try_scrape_instagram(username)
                
                if profile_data:
                    save_profile_data(profile_data)
                    st.success("Profil başarıyla çekildi ve kaydedildi!")
                    
                    # Profil bilgilerini göster
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Takipçi", f"{profile_data['followers']:,}")
                    with col2:
                        st.metric("Takip", f"{profile_data['following']:,}")
                    with col3:
                        st.metric("Gönderi", f"{profile_data['posts']:,}")
                    with col4:
                        engagement = (profile_data['followers'] / profile_data['posts']) if profile_data['posts'] > 0 else 0
                        st.metric("Ort. Etkileşim", f"{engagement:.0f}")
                    
                    st.markdown("---")
                    
                    with st.expander("Detaylı Bilgiler", expanded=True):
                        st.write(f"**Kullanıcı:** @{profile_data['username']}")
                        st.write(f"**Tam Ad:** {profile_data['full_name']}")
                        st.write(f"**Biyografi:** {profile_data['biography']}")
                else:
                    st.error(f"Otomatik çekme başarısız: {error}")
                    st.info("Manuel giriş yöntemini kullanın")

elif page == "Geçmiş Veriler":
    st.header("Geçmiş Sorgular")
    
    df = get_all_profiles()
    
    if not df.empty:
        # İstatistikler
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Toplam Kayıt", len(df))
        
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
        st.subheader("Kayıtlı Profiller")
        
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
        st.info("Henüz kayıt yok. Profil ekle sayfasından başlayın!")

st.markdown("---")
st.caption("Instagram Takipçi Tracker - Manuel veri girişi")
