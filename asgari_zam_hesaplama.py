bordro=True
brüt_ücret=35_000  #Buraya İstediğiniz Brüt ücret Maaşı giin
yıllık_brüt=brüt_ücret*12   #Misal Brüt maaş{33_000*12}=420.000 Tl

vergi1=(158_000*0.15)   # %15 kısma giren vergi
vergi2=(330_000-158_000)*0.20   # %20 Kısma Giren Vergi
vergi3=(1_200_000-330_000)*0.27 #%27 Kısma Giren Vergi
vergi4=(4_300_000-1_200_000)*0.35   #%35 Kısma Giren Vergi
vergi5=(800_000-330_000)*0.27   #%27 kısma giren ücret dışı
vergi6=(4_300_000-800_000)*0.35 #%35 Kısma giren ücret dışı

sgk_oranı=0.14  # Sgk Oranı %14
işsizlik_sigorta_primi=0.01 #Sgk oranı %1

sgk_işçi = brüt_ücret * sgk_oranı   # Sgk isci maliyeti=örnek 30_000 X 0.14=4200
işsizlik_işçi = brüt_ücret * işsizlik_sigorta_primi # issizlik maliyeti=30_000 X 0.01=300 olacaktır


if bordro:
    if yıllık_brüt < 158_000:   #0.15 vergi dilimi
        gelir_vergisi = (yıllık_brüt * 0.15)
    elif yıllık_brüt < 330_000: #0.20 vergi dilimi
        gelir_vergisi = vergi1 + ((yıllık_brüt - 158_000) * 0.20)
    elif yıllık_brüt < 1_200_000:   #.27 vergi dilimi
        gelir_vergisi = vergi1 + vergi2 + ((yıllık_brüt - 330_000) * 0.27)
    elif yıllık_brüt < 4_300_00: #0.35 Vergi Dilimi
        gelir_vergisi = vergi1 + vergi2 + vergi3 + ((yıllık_brüt - 4_300_000) * 0.35)
    else:
        gelir_vergisi = vergi1 + vergi2 + vergi3 + vergi4 + ((yıllık_brüt - 4_300_000) * 0.40) ##0.40 vergi dilimi
else:
    if yıllık_brüt < 158_000:   #Ücret dışı olarak 0.15
        gelir_vergisi = yıllık_brüt * 0.15 # Ücret dışı olarak 0.20
    elif yıllık_brüt < 330_000:
        gelir_vergisi = vergi1 + ((yıllık_brüt - 158_000) * 0.20)
    elif yıllık_brüt < 800_000: #Ücret dışı olarak 0.27
        gelir_vergisi = vergi1 + vergi2 + ((yıllık_brüt - 330_000) * 0.27)
    elif yıllık_brüt < 4_300_000: #ücret dışı olarak 0.35
        gelir_vergisi = vergi1 + vergi2 + vergi5 + ((yıllık_brüt - 800_000) * 0.35)
    else:
        gelir_vergisi = vergi1 + vergi2 + vergi5 + vergi6 + ((yıllık_brüt - 4_300_000) * 0.40)  #ücret dışı 0.40

aylık_gelir_vergisi = gelir_vergisi / 12
#Oluşturduğumuz yıllık gelirvergisi/12 dersek aylık_gelir Vergisini buluruz
#35 bin gelir vergisi hesaplama =35 X 12=420_000.
# vergi1+vergi2+(420_000-330_000*0.27)= Buna Göre 6 bin küsurat cıkar ama
#Biz aylık vergiiyi=gelir matrahı*015 sabitledik
# gelir matrahı bulma formulune bakalım
#gelir_matrahı=brüt ücret -(işsizlik+sgk_oran_maliyet)
#35_000(350+4900)=29.750 gelir matrahıdır
# aylık gelir verisini gelir matrahının yuzde 0.15 esıtledığımız için 29.750 x0.15 =4.462 cıvarı bır sey olacaktı

# Gelir matrahı (aylık)
gelir_matrahı = brüt_ücret - (sgk_işçi + işsizlik_işçi)
#Zaten yukarıda anlattık

aylık_gelir_vergisi = gelir_matrahı * 0.15

# Aylık net (gelir vergisi dahil)
aylık_net = brüt_ücret - (sgk_işçi + işsizlik_işçi + aylık_gelir_vergisi)
#Burada ise ayık net maas formuludur
# Brüt 35_000(450+4_900+4_462)
#25_288 civarı net maaş olacaktır
for ay in range(1, 13):
# burada 1 den 12 aya kadar alacaktır bır eksıgını alır yanı 1,12 deseydık 1,11 kadar alacaktır
# 12 ayı alması ıcın 1,13 kullandık .



    print(f" {ay:<3}   {aylık_gelir_vergisi:>15,.2f}   {aylık_net:>15,.2f}")

yıllık_net = aylık_net * 12

print(f"\nYıllık Brüt Ücret : {yıllık_brüt:,.2f} TL")
print(f"Gelir Matrahı     : {gelir_matrahı:,.2f} TL")
print(f"Gelir Vergisi     : {gelir_vergisi:,.2f} TL")
print(f"SGK Kesintisi     : {sgk_işçi:,.2f} TL")
print(f"İşsizlik Sigortası: {işsizlik_işçi:,.2f} TL")
print(f"Yıllık Net Ücret  : {yıllık_net:,.2f} TL")
print(f"Aylık Net Ücret   : {aylık_net:,.2f} TL")
