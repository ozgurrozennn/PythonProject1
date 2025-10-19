<<<<<<< HEAD
import streamlit as st
import pandas as pd

#Başlık ekliyoruz. Stream importu için st.(title)
st.title(" Gelir Vergisi Hesaplama ")

#st.selectbox olarak iniglizce olarakda anlayabiliriz select seçmek box kutu demek.Kutu secmek
#Misal "Gelir Unsuru Secin" string,[ücretli,Ücret dışı] ise list metodur ancak type ile bakarsanız tupple olacaktır.
#matrah_aylik olarak variable olusturduk ve buna numeric girebilmek için ise number metodunu sectık

gelir_unsuru = st.selectbox("Gelir Unsuru Seçin:", ["Ücretli", "Ücret Dışı"])
matrah_aylik = st.number_input(
    "Aylık Brüt Gelir (TL)",
    min_value=0.0, #Minimum Girilecek Değer
    value=20000.0,#Box daki değer
    step=500.0 # Sayı arttırmak için kullanılacak değerdir.
   


)
vergi_toplam=2400
# def metoduyla oluşturduk, matrah_aylik, gelir_unsuru fonksiyonlarını çağırdık
def hesapla_vergi_ve_net(matrah_aylik, gelir_unsuru):
    if gelir_unsuru == "Ücretli":
        yillik_matrah = matrah_aylik * 12 # Burada yıllık matrahı buluyoruz
        if yillik_matrah <= 158_000: 
            vergi = yillik_matrah * 0.15
           
        elif yillik_matrah <= 330_000:# Eğer yıllık matrah 158.000<yıllık_matrah<=330_000 ise demektir bu kosul . misal (15_000*12)=180_000(180_000-158_00)*0.20 +23_700
            vergi = 23_700 + 0.20 * (yillik_matrah - 158_000) 
            vergi+=vergi_toplam
        elif yillik_matrah <= 1_200_000:
            vergi = 58_100 + 0.27 * (yillik_matrah - 330_000)  
            vergi+=vergi_toplam
        elif yillik_matrah <= 4_300_000:
            vergi = 293_000 + 0.35 * (yillik_matrah - 1_200_000)
            vergi+=vergi_toplam
        else:
            vergi = 1_378_000 + 0.40 * (yillik_matrah - 4_300_000)
            vergi+=vergi_toplam
    
   
    net_yillik = yillik_matrah - vergi  #net yıllık gelir için örnek(33_000 X 12)=396_000=320_080
    net_aylik = (net_yillik / 12) if gelir_unsuru == "Ücretli" else None
    #ücretli için net ayliği bulmak (net yıllık/12) 320_080/12= 26_673 net_aylik
    tahakkuk_vergi=(matrah_aylik-net_aylik)if net_aylik is not None else None   # 33.000 - 26.673= 6.326
    # def ile oluşturduğum variable yani fonksiyonları return ile geri çağırıyorum
    return (float(f"{yillik_matrah:.2f}"),
            float(f"{vergi:.2f}"),
            float(f"{net_yillik:.2f}"),
            float(f"{net_aylik:.2f}"),
            float(f"{tahakkuk_vergi:.2f}")
           )

if st.button("Vergiyi Hesapla"):
    yillik_matrah, vergi, net_yillik, net_aylik,tahakkuk_vergi = hesapla_vergi_ve_net(matrah_aylik, gelir_unsuru)
    #st button iste bu işlemi gerçekleştirmek için oluşturulan kutucuk metodudur.
    # Gördüğünüz gibi yukarıdaki return ile çağırdım fonkz"iyonları bu butonun içine atıyorum.



  #Data_Frame denilen olay veriyi tablo haline çevirmedir.
    #import pandas as pd ile çekeriz
    # Misal Sütunlar(columns)
    #satırlar (rows) diye adlandırılır.
    # Aşağıdaki mantıkla sütunları doldururz
    df = pd.DataFrame({
        "Gelir Unsuru": [gelir_unsuru],  # Bu genellikle string, float yapmaya gerek yok
    "Aylık Brüt Gelir (₺)": [(matrah_aylik)],
    "Yıllık Matrah (₺)": [(yillik_matrah)],
    "Yıllık Vergi (₺)": [(vergi)],
    "Tahakkuk Eden Vergi (₺)": [(tahakkuk_vergi)],
    "Net Yıllık Gelir (₺)": [(net_yillik)],
    "Net Aylık Gelir (₺)": [(net_aylik)]
})



    st.subheader("Sonuc:")#altbaslık metodu ıcın st.subheader
    st.table(df)    # Streamda tablo ile göstermek içindir





















































=======
import streamlit as st
import pandas as pd



#Başlık ekliyoruz. Stream importu için st.(title)
st.title(" Gelir Vergisi Hesaplama ")

#st.selectbox olarak iniglizce olarakda anlayabiliriz select seçmek box kutu demek.Kutu secmek
#Misal "Gelir Unsuru Secin" string,[ücretli,Ücret dışı] ise list metodur ancak type ile bakarsanız tupple olacaktır.
#matrah_aylik olarak variable olusturduk ve buna numeric girebilmek için ise number metodunu sectık

gelir_unsuru = st.selectbox("Gelir Unsuru Seçin:", ["Ücretli", "Ücret Dışı"])
matrah_aylik = st.number_input(
    "Aylık Brüt Gelir (TL)",
    min_value=0.0, #Minimum Girilecek Değer
    value=20000.0,#Box daki değer
    step=500.0 # Sayı arttırmak için kullanılacak değerdir.


)
if (matrah_aylik) < (1000):         #eğer streamda ondalık hatasını almamak için misal 5000 yerine 500 girdiyse bin ile çarp 5000 eder
    (matrah_aylik) = (matrah_aylik * 1000)

# def metoduyla oluşturduk, matrah_aylik, gelir_unsuru fonksiyonlarını çağırdık
def hesapla_vergi_ve_net(matrah_aylik, gelir_unsuru):
    if gelir_unsuru == "Ücretli":   # Burda gelir unsuru ücretli seçildiğinde
        yillik_matrah = matrah_aylik * 12   # yıllık matrahı oluşturduk (33.000X12=396.000)
    else:
        yillik_matrah = matrah_aylik    # ücret dışı secmişs se çarpma işlemi yapılmaz Ücret dışını yıllık al direk 396.000


    if yillik_matrah <= 158_000:    #Eğer Yıllık Matrah 158000 eşit veya daha az ise
        vergi = yillik_matrah * 0.15 #vergi varaible olusturduk örnek:10_000 X 12 // yillık=(120_000 X 0.15)= 18_000. Yıllık  vergi
    elif yillik_matrah <= 330_000:  # Yıllık Matrah 330000 eşit veya daaha az ise
        vergi = 23_700 + (yillik_matrah - 158_000) * 0.20# Örnek: 22_000 X 12// yillik=(264_000-158_000)*0.20 + (23700)= 44.900 Yıllık vergi
    elif yillik_matrah <= 800_000:  #Yıllık matrah 800 bin eşit ve daha az ise
        vergi = 58_100 + (yillik_matrah - 330_000) * 0.27    # Örnek: 33_000 x 12 // yillık=(396_000-330_000)*0.27 +(58_100)=75_920 Yıllık Vergi
    elif yillik_matrah <= 4_300_000:    #Yıllık matrah 4milyon 300 bine eşit  veya daha az ise
        vergi = 185_000 + (yillik_matrah - 800_000) * 0.35  # 67_000 x 12=804.000 yıllık matrah //(804_000-800_000)*0.35 +(185.000)=186_400 Yıllık Vergi
    else:
        vergi = 1_410_000 + (yillik_matrah - 4_300_000) * 0.40  # 359_000 X 12=4_308_000 yıllık matrah // (4_308_000-4_300_000)*0.40+1_410_000=1_413_200

    net_yillik = yillik_matrah - vergi  #net yıllık gelir için örnek(33_000 X 12)=396_000=320_080
    net_aylik = (net_yillik / 12) if gelir_unsuru == "Ücretli" else None
    #ücretli için net ayliği bulmak (net yıllık/12) 320_080/12= 26_673 net_aylik
    tahakkuk_vergi=matrah_aylik-net_aylik   # 33.000 - 26.673= 6.326
    return yillik_matrah, vergi, net_yillik, net_aylik,tahakkuk_vergi
    # def ile oluşturduğum variable yani fonksiyonları return ile geri çağırıyorum


if st.button("Vergiyi Hesapla"):
    yillik_matrah, vergi, net_yillik, net_aylik,tahakkuk_vergi = hesapla_vergi_ve_net(matrah_aylik, gelir_unsuru)
    #st button iste bu işlemi gerçekleştirmek için oluşturulan kutucuk metodudur.
    # Gördüğünüz gibi yukarıdaki return ile çağırdım fonkz"iyonları bu butonun içine atıyorum.

  #Data_Frame denilen olay veriyi tablo haline çevirmedir.
    #import pandas as pd ile çekeriz
    # Misal Sütunlar(columns)
    #satırlar (rows) diye adlandırılır.
    # Aşağıdaki mantıkla sütunları doldururz
    df = pd.DataFrame({
        "Gelir Unsuru": [gelir_unsuru],
        "Aylık Brüt Gelir (₺)": [matrah_aylik],
        "Yıllık Matrah (₺)": [yillik_matrah],
        "Yıllık Vergi (₺)": [vergi],
        "Tahakkuk Eden Vergi":[tahakkuk_vergi],
    "Net Yıllık Gelir (₺)": [net_yillik],
        "Net Aylık Gelir (₺)": [net_aylik if net_aylik else 0]
        #Burda else sıfr mantığı if koşulda net aylık yoksa ücret dışı için geçerlidir bu nedenle else sıfır mantığını uyguladık

    })

    st.subheader("Hesaplama Sonuçları")
    st.table(df)    # Streamda tablo ile göstermek içindir

>>>>>>> 09208c1 (commit)
