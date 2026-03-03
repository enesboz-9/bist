import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Terminal - Enes Boz", layout="wide")

# --- 2. BIST 100 TÜM ŞİRKET LİSTESİ ---
bist_100_full = {
    "AEFES": "Anadolu Efes", "AGHOL": "Anadolu Grubu Holding", "AKBNK": "Akbank", "AKCNS": "Akçansa",
    "AKFGY": "Akfen GYO", "AKSA": "Aksa", "AKSEN": "Aksa Enerji", "ALARK": "Alarko Holding",
    "ALBRK": "Albaraka Türk", "ALFAS": "Alfa Solar Enerji", "ARCLK": "Arçelik", "ASELS": "Aselsan",
    "ASTOR": "Astor Enerji", "ASUZU": "Anadolu Isuzu", "AYDEM": "Aydem Enerji", "BAGFS": "Bagfaş",
    "BERA": "Bera Holding", "BIENY": "Bien Yapı Ürünleri", "BIMAS": "Bim Mağazalar", "BRSAN": "Borusan Boru",
    "BRYAT": "Borusan Yatırım", "BUCIM": "Bursa Çimento", "CANTE": "Çan2 Termik", "CCOLA": "Coca-Cola İçecek",
    "CIMSA": "Çimsa", "CWENE": "Cw Enerji", "DOAS": "Doğuş Otomotiv", "DOHOL": "Doğan Holding",
    "EGEEN": "Ege Endüstri", "EKGYO": "Emlak Konut GYO", "ENJSA": "Enerjisa Enerji", "ENKAI": "Enka İnşaat",
    "EREGL": "Ereğli Demir Çelik", "EUPWR": "Europower Enerji", "FROTO": "Ford Otosan", "GARAN": "Garanti Bankası",
    "GESAN": "Girişim Elektrik", "GUBRF": "Gübre Fabrikaları", "GWIND": "Galata Wind", "HALKB": "Halkbank",
    "HEKTS": "Hektaş", "IPEKE": "İpek Doğal Enerji", "ISCTR": "İş Bankası (C)", "ISDMR": "İskenderun Demir Çelik",
    "ISGYO": "İş GYO", "ISMEN": "İş Yatırım Menkul Değerler", "IZENR": "İzdemir Enerji", "KAYSE": "Kayseri Şeker",
    "KCHOL": "Koç Holding", "KENT": "Kent Gıda", "KONTR": "Kontrolmatik Teknoloji", "KORDS": "Kordsa",
    "KOZAA": "Koza Madencilik", "KOZAL": "Koza Altın", "KRDMD": "Kardemir (D)", "MAVI": "Mavi Giyim",
    "MGROS": "Migros", "MIATK": "Mia Teknoloji", "ODAS": "Odaş Elektrik", "OTKAR": "Otokar",
    "OYAKC": "Oyak Çimento", "PENTA": "Penta Teknoloji", "PETKM": "Petkim", "PGSUS": "Pegasus",
    "QUAGR": "Qua Granite", "SAHOL": "Sabancı Holding", "SASA": "Sasa Polyester", "SAYAS": "Say Yenilenebilir Enerji",
    "SDTTR": "Sdt Uzay Ve Savunma", "SISE": "Şişecam", "SKBNK": "Şekerbank", "SMRTG": "Smart Güneş Enerjisi",
    "SOKM": "Şok Marketler", "TARKM": "Tarkim Bitki Koruma", "TAVHL": "Tav Havalimanları", "TCELL": "Turkcell",
    "THYAO": "Türk Hava Yolları", "TKFEN": "Tekfen Holding", "TOASO": "Tofaş Oto. Fab.", "TSKB": "Tskb",
    "TTKOM": "Türk Telekom", "TTRAK": "Türk Traktör", "TUPRS": "Tüpraş", "TURSG": "Türkiye Sigorta",
    "ULKER": "Ülker Bisküvi", "VAKBN": "Vakıfbank", "VESBE": "Vestel Beyaz Eşya", "VESTL": "Vestel",
    "YEOTK": "Yeo Teknoloji", "YKBNK": "Yapı Kredi Bankası", "YYLGD": "Yaylatepe Gıda", "ZOREN": "Zorlu Enerji"
}
hisse_listesi = [f"{kod} - {ad}" for kod, ad in bist_100_full.items()]

# --- 3. OTURUM YÖNETİMİ ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet'])

# --- 4. VERİ FONKSİYONLARI ---
def veri_cek(ticker, periyot="1y", aralik="1d"):
    try:
        data = yf.download(ticker, period=periyot, interval=aralik, progress=False)
        if data.empty: return None
        return data['Close'][ticker] if isinstance(data.columns, pd.MultiIndex) else data['Close']
    except: return None

# --- 5. ÜST PANEL (TEKNİK ANALİZ) ---
st.title("📈 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

st.header("🔍 Hisse Teknik Analizi")
t_col1, t_col2 = st.columns([1, 3])
with t_col1:
    teknik_secim = st.selectbox("Analiz Edilecek Hisse:", hisse_listesi, index=76)
    t_kod = teknik_secim.split(" - ")[0]
    sure_secimi = st.radio("Süre:", ["1 Ay", "1 Yıl", "5 Yıl"], index=1, horizontal=True)

periyot_map = {"1 Ay": "1mo", "1 Yıl": "1y", "5 Yıl": "5y"}
aralik_map = {"1 Ay": "1h", "1 Yıl": "1d", "5 Yıl": "1wk"}

hisse_fiyatlari = veri_cek(f"{t_kod}.IS", periyot_map[sure_secimi], aralik_map[sure_secimi])

if hisse_fiyatlari is not None:
    fig = go.Figure(data=[go.Scatter(x=hisse_fiyatlari.index, y=hisse_fiyatlari, line=dict(color='#00d1b2'))])
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

# --- 6. PÖRTFÖY YÖNETİMİ (RENKLİ ANALİZ) ---
st.divider()
st.header("💰 Pörtföyüm & Kar-Zarar Takibi")

# Hisse Ekleme Alanı
with st.expander("➕ Yeni Hisse Ekle", expanded=True):
    e1, e2, e3 = st.columns([2, 1, 1])
    with e1: p_hisse = st.selectbox("Hisse Seçiniz:", hisse_listesi, key="p_ekle")
    with e2: p_maliyet = st.number_input("Alış Fiyatı (TL):", min_value=0.01, format="%.2f")
    with e3: p_adet = st.number_input("Adet:", min_value=1, step=1)
    
    if st.button("Pörtföye Kaydet", use_container_width=True):
        pkod = p_hisse.split(" - ")[0]
        yeni_satir = pd.DataFrame([{'Hisse': pkod, 'Maliyet': p_maliyet, 'Adet': p_adet}])
        st.session_state.portfoy = pd.concat([st.session_state.portfoy, yeni_satir], ignore_index=True)
        st.rerun()

# Pörtföy Listeleme ve Hesaplama
if not st.session_state.portfoy.empty:
    toplam_maliyet = 0.0
    toplam_guncel_deger = 0.0

    st.subheader("Aktif Pozisyonlar")
    
    # Başlıklar
    h1, h2, h3, h4, h5, h6 = st.columns([1, 1, 1, 1.5, 1, 0.5])
    h1.write("**Hisse**")
    h2.write("**Maliyet**")
    h3.write("**Güncel**")
    h4.write("**K/Z Durumu**")
    h5.write("**Toplam Değer**")
    h6.write("")

    for idx, row in st.session_state.portfoy.iterrows():
        # Güncel fiyatı çek
        guncel_veri = yf.download(f"{row['Hisse']}.IS", period="1d", progress=False)
        if not guncel_veri.empty:
            guncel_f = float(guncel_veri['Close'].iloc[-1])
            maliyet_toplam = row['Maliyet'] * row['Adet']
            guncel_toplam = guncel_f * row['Adet']
            kz_tl = guncel_toplam - maliyet_toplam
            kz_yuzde = (kz_tl / maliyet_toplam) * 100
            
            toplam_maliyet += maliyet_toplam
            toplam_guncel_deger += guncel_toplam

            # Renk belirleme
            renk = "green" if kz_tl >= 0 else "red"
            isaret = "+" if kz_tl >= 0 else ""

            # Satır Çizimi
            c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1.5, 1, 0.5])
            c1.write(f"**{row['Hisse']}**")
            c2.write(f"{row['Maliyet']:.2f} TL")
            c3.write(f"{guncel_f:.2f} TL")
            c4.markdown(f":{renk}[{isaret}{kz_tl:,.2f} TL ({isaret}{kz_yuzde:.2f}%)]")
            c5.write(f"{guncel_toplam:,.2f} TL")
            if c6.button("🗑️", key=f"sil_{idx}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(idx).reset_index(drop=True)
                st.rerun()

    # --- EN ALTTA GENEL ÖZET (METRİKLER) ---
    st.divider()
    genel_kz = toplam_guncel_deger - toplam_maliyet
    genel_yuzde = (genel_kz / toplam_maliyet * 100) if toplam_maliyet > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Yatırım", f"{toplam_maliyet:,.2f} TL")
    m2.metric("Pörtföy Değeri", f"{toplam_guncel_deger:,.2f} TL")
    m3.metric("Toplam Kar / Zarar", 
              f"{genel_kz:,.2f} TL", 
              delta=f"{genel_yuzde:.2f}%",
              delta_color="normal") # Kendi rengini otomatik ayarlar (Pozitif yeşil, negatif kırmızı)

else:
    st.info("Pörtföyünüz henüz boş. Yukarıdaki formu kullanarak hisse ekleyebilirsiniz.")
