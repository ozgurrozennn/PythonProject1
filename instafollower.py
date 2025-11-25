import streamlit as st
import requests
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

# Farklı API denemeleri
def fetch_with_api1(username, api_key):
    """Instagram Bulk Profile Data API"""
    try:
        url = "https://instagram-bulk-profile-scrapper.p.rapidapi.com/clients/api/ig/ig_profile"
        
        querystring = {"ig": username, "response_type": "short"}
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram-bulk-profile-scrapper.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'username': data[0]['username'],
                'followers': data[0]['follower_count'],
                'following': data[0]['following_count'],
                'posts': data[0]['media_count'],
                'full_name': data[0].get('full_name', ''),
                'biography': data[0].get('biography', ''),
                'is_private': data[0].get('is_private', False),
                'is_verified': data[0].get('is_verified', False)
            }, None
        else:
            return None, f"API1 Hata: {response.status_code}"
    except Exception as e:
        return None, f"API1 Exception: {str(e)}"

def fetch_with_api2(username, api_key):
    """Instagram Data API"""
    try:
        url = "https://instagram-data1.p.rapidapi.com/user/info"
        
        querystring = {"username": username}
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram-data1.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'username': data['username'],
                'followers': data['follower_count'],
                'following': data['following_count'],
                'posts': data['media_count'],
                'full_name': data.get('full_name', ''),
                'biography': data.get('biography', ''),
                'is_private': data.get('is_private', False),
                'is_verified': data.get('is_verified', False)
            }, None
        else:
            return None, f"API2 Hata: {response.status_code}"
    except Exception as e:
        return None, f"API2 Exception: {str(e)}"

def fetch_with_api3(username, api_key):
    """Instagram API V1"""
    try:
        url = "https://instagram-api-20231.p.rapidapi.com/api/profile_info"
        
        querystring = {"username": username}
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "instagram-api-20231.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
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
            return None, f"API3 Hata: {response.status_code}"
    except Exception as e:
        return None, f"API3 Exception: {str(e)}"

# Tüm API'leri dene
def fetch_instagram_profile(username, api_key):
    st.info("API 1 deneniyor...")
    result, error = fetch_with_api1(username, api_key)
    if result:
        return result, None
    
    st.warning(f"API 1 başarısız: {error}")
    st.info("API 2 deneniyor...")
    result, error = fetch_with_api2(username, api_key)
    if result:
        return result, None
    
    st.warning(f"API 2 başarısız: {error}")
    st.info("API 3 deneniyor...")
    result, error = fetch_with_api3(username, api_key)
    if result:
        return result, None
    
    return None, f"Tüm API'ler başarısız"

# Veritabanını başlat
init_db()

# Streamlit UI
st.title("Instagram Takipçi Tracker")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("API Ayarları")
    
    api_key = st.text_input("RapidAPI Key:", value="c7bc53f7afmshe7f072a01c54e07p1fe6d5jsn21d488701f1f", type="password")
    
    if api_key:
        st.success("API Key kaydedildi")
        st.session_state['api_key'] = api_key
    
    st.info("""
    **Denenen API'ler:**
    1. Instagram Bulk Profile Scrapper
    2. Instagram Data API
    3. Instagram API V1
    
    Biri çalışmazsa diğerleri denenir.
    """)
    
    st.markdown("---")
    page = st.radio("Sayfa Seç", ["Profil Sorgula", "Geçmiş Veriler"])

# Ana içerik
if page == "Profil Sorgula":
    st.header("Instagram Profil Sorgula")
    
    if 'api_key' not in st.session_state or not st.session_state['api_key']:
        st.warning("Lütfen sol menüden API Key girin")
        st.stop()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        username = st.text_input("Instagram kullanıcı adını girin:", placeholder="cristiano")
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("Sorgula", use_container_width=True)
    
    if search_button and username:
        with st.spinner(f'@{username} profili sorgulanıyor...'):
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
                
                with st.expander("Detaylı Profil Bilgileri", expanded=True):
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
                st.error(f"❌ Hata: {error}")
                st.warning("Hiçbir API çalışmadı. Manuel giriş önerilir.")

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
            label="CSV olarak İndir",
            data=csv,
            file_name=f"instagram_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Henüz sorgulama yapılmamış.")

st.markdown("---")
st.caption("Instagram Takipçi Tracker - Multi API")
