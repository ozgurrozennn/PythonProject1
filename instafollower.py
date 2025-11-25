import streamlit as st
import requests
import sqlite3
from datetime import datetime
import pandas as pd
import time

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

# Instagram Profile Scraper API (instagram-scraper-api2.p.rapidapi.com)
def fetch_instagram_v1(username, api_key):
    """İlk API denemesi"""
    try:
        url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
        
        querystring = {"username_or_id_or_url": username}
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            user = data['data']
            
            return {
                'username': user['username'],
                'followers': user['follower_count'],
                'following': user['following_count'],
                'posts': user['media_count'],
                'full_name': user.get('full_name', ''),
                'biography': user.get('biography', ''),
                'is_private': user.get('is_private', False),
                'is_verified': user.get('is_verified', False)
            }, None
        else:
            return None, f"Hata {response.status_code}: {response.text[:100]}"
    
    except Exception as e:
        return None, str(e)

# Instagram Profile by username API
def fetch_instagram_v2(username, api_key):
    """İkinci API denemesi"""
    try:
        url = "https://instagram-profile1.p.rapidapi.com/getprofile"
        
        payload = {"username": username}
        
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram-profile1.p.rapidapi.com"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'username': data['username'],
                'followers': data['followers'],
                'following': data['following'],
                'posts': data['posts'],
                'full_name': data.get('full_name', ''),
                'biography': data.get('biography', ''),
                'is_private': data.get('is_private', False),
                'is_verified': data.get('is_verified', False)
            }, None
        else:
            return None, f"Hata {response.status_code}"
    
    except Exception as e:
        return None, str(e)

# Instagram Scraper 2024
def fetch_instagram_v3(username, api_key):
    """Üçüncü API denemesi"""
    try:
        url = "https://instagram-scraper-20222.p.rapidapi.com/profile_info"
        
        querystring = {"username": username}
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram-scraper-20222.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            user = data['data']['user']
            
            return {
                'username': user['username'],
                'followers': user['edge_followed_by']['count'],
                'following': user['edge_follow']['count'],
                'posts': user['edge_owner_to_timeline_media']['count'],
                'full_name': user.get('full_name', ''),
                'biography': user.get('biography', ''),
                'is_private': user.get('is_private', False),
                'is_verified': user.get('is_verified', False)
            }, None
        else:
            return None, f"Hata {response.status_code}"
    
    except Exception as e:
        return None, str(e)

# Instagram Looter API
def fetch_instagram_v4(username, api_key):
    """Dördüncü API denemesi"""
    try:
        url = "https://instagram-looter2.p.rapidapi.com/user"
        
        querystring = {"username": username}
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram-looter2.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'username': data['username'],
                'followers': data['followerCount'],
                'following': data['followingCount'],
                'posts': data['postsCount'],
                'full_name': data.get('fullName', ''),
                'biography': data.get('biography', ''),
                'is_private': data.get('isPrivate', False),
                'is_verified': data.get('isVerified', False)
            }, None
        else:
            return None, f"Hata {response.status_code}"
    
    except Exception as e:
        return None, str(e)

# Tüm API'leri sırayla dene
def fetch_instagram_profile(username, api_key):
    apis = [
        ("Instagram Scraper API v2", fetch_instagram_v1),
        ("Instagram Profile API", fetch_instagram_v2),
        ("Instagram Scraper 2024", fetch_instagram_v3),
        ("Instagram Looter API", fetch_instagram_v4)
    ]
    
    progress_placeholder = st.empty()
    
    for i, (api_name, api_func) in enumerate(apis):
        progress_placeholder.info(f"🔄 {api_name} deneniyor... ({i+1}/{len(apis)})")
        
        result, error = api_func(username, api_key)
        
        if result:
            progress_placeholder.success(f"✅ {api_name} başarılı!")
            time.sleep(0.5)
            progress_placeholder.empty()
            return result, None
        else:
            progress_placeholder.warning(f"⚠️ {api_name} başarısız: {error}")
            time.sleep(1)
    
    progress_placeholder.error("❌ Tüm API'ler başarısız oldu")
    return None, "Tüm API'ler başarısız"

# Veritabanını başlat
init_db()

# Streamlit UI
st.title("Instagram Takipçi Tracker")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("API Ayarları")
    
    api_key = st.text_input(
        "RapidAPI Key:", 
        value="c7bc53f7afmshe7f072a01c54e07p1fe6d5jsn21d488701f1f", 
        type="password"
    )
    
    if api_key:
        st.success("✅ API Key kaydedildi")
        st.session_state['api_key'] = api_key
    
    st.markdown("---")
    
    st.info("""
    **4 Farklı API denenir:**
    
    1️⃣ Instagram Scraper API v2
    2️⃣ Instagram Profile API  
    3️⃣ Instagram Scraper 2024
    4️⃣ Instagram Looter API
    
    Biri çalışmazsa diğerine otomatik geçer.
    """)
    
    st.markdown("---")
    page = st.radio("Sayfa Seç", ["Profil Sorgula", "Geçmiş Veriler"])

# Ana içerik
if page == "Profil Sorgula":
    st.header("Instagram Profil Sorgula")
    
    if 'api_key' not in st.session_state or not st.session_state['api_key']:
        st.warning("⚠️ Lütfen sol menüden API Key girin")
        st.stop()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        username = st.text_input("Instagram kullanıcı adını girin:", placeholder="cristiano")
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("🔍 Sorgula", use_container_width=True)
    
    if search_button and username:
        profile_data, error = fetch_instagram_profile(username, st.session_state['api_key'])
        
        if profile_data:
            save_profile_data(profile_data)
            
            st.success("✅ Profil bilgileri başarıyla kaydedildi!")
            
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
            
            with st.expander("📋 Detaylı Profil Bilgileri", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Kullanıcı Adı:** @{profile_data['username']}")
                    st.write(f"**Tam Ad:** {profile_data['full_name']}")
                    st.write(f"**Özel Hesap:** {'Evet' if profile_data['is_private'] else 'Hayır'}")
                    st.write(f"**Onaylı Hesap:** {'Evet' if profile_data['is_verified'] else 'Hayır'}")
                
                with col2:
                    if profile_data['biography']:
                        st.write(f"**Biyografi:**")
                        st.info(profile_data['biography'])
        
        else:
            st.error(f"❌ Profil çekilemedi: {error}")
            st.warning("""
            **Olası Çözümler:**
            
            1. RapidAPI'da bu API'lere subscribe olduğunuzdan emin olun
            2. API limitinizi kontrol edin
            3. Farklı bir kullanıcı adı deneyin
            4. Birkaç dakika bekleyip tekrar deneyin
            """)

elif page == "Geçmiş Veriler":
    st.header("Geçmiş Sorgular")
    
    df = get_all_profiles()
    
    if not df.empty:
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
        
        users = df['username'].unique().tolist()
        selected_user = st.selectbox("Kullanıcı Seç:", ["Tümü"] + users)
        
        if selected_user != "Tümü":
            df_filtered = get_profile_history(selected_user)
            st.subheader(f"@{selected_user} Geçmişi")
            
            if len(df_filtered) > 1:
                df_chart = df_filtered.copy()
                df_chart['created_at'] = pd.to_datetime(df_chart['created_at'])
                df_chart = df_chart.sort_values('created_at')
                
                st.line_chart(df_chart.set_index('created_at')['followers'])
        else:
            df_filtered = df
        
        st.subheader("Sorgulanan Profiller")
        
        display_df = df_filtered[['username', 'followers', 'following', 'posts', 'is_verified', 'created_at']].copy()
        display_df.columns = ['Kullanıcı Adı', 'Takipçi', 'Takip', 'Gönderi', 'Onaylı', 'Tarih']
        display_df['Onaylı'] = display_df['Onaylı'].apply(lambda x: 'Evet' if x else 'Hayır')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 CSV olarak İndir",
            data=csv,
            file_name=f"instagram_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 Henüz sorgulama yapılmamış.")

st.markdown("---")
st.caption("Instagram Takipçi Tracker - Multi API v2")
