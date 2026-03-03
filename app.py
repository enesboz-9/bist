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

if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet'])

# --- 3. VERİ ÇEKME FONKSİYONU (GARANTİLİ YÖNTEM) ---
def veri_indir_teknik(ticker, periyot="1y", aralik="1d"):
    try:
        data = yf.download(ticker, period=periyot, interval=aralik, progress=False)
        if data.empty: return None
        
        # Multi-index'i temizle: Sadece Kapanış (Close) sütununu al
        if isinstance(data.columns, pd.MultiIndex):
            data = data['Close']
            
        # Eğer DataFrame ise sütun ismine göre Series'e çevir
        if isinstance(data, pd.DataFrame):
            if ticker in data.columns:
                return data[ticker].dropna()
            else:
                return data.iloc[:, 0].dropna()
        return data.dropna()
    except Exception as e:
        st.error(f"Veri hatası: {e}")
        return None

# --- 4. ARAYÜZ ---
st.title("📈 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# --- 5. TEKNİK ANALİZ GRAFİĞİ (BAĞIMSIZ) ---
st.header("🔍 Hisse Teknik Analizi")
t_col1, t_col2 = st.columns([1, 3])

with t_col1:
    teknik_secim = st.selectbox("Analiz Edilecek Hisse:", hisse_listesi, index=76)
    t_kod = teknik_secim.split(" - ")[0]
    sure_secimi = st.radio("Zaman Aralığı:", ["1 Ay", "1 Yıl", "5 Yıl"], index=1, horizontal=True)

# Periyot ve Aralık Ayarları
p_map = {"1 Ay": "1mo", "1 Yıl": "1y", "5 Yıl": "5y"}
a_map = {"1 Ay": "1h", "1 Yıl": "1d", "5 Yıl": "1wk"}

# Veriyi Çek
h_fiyat = veri_indir_teknik(f"{t_kod}.IS", p_map[sure_secimi], a_map[sure_secimi])

if h_fiyat is not None and not h_fiyat.empty:
    fig_teknik = go.Figure()
    fig_teknik.add_trace(go.Scatter(x=h_fiyat.index, y=h_fiyat, name=t_kod, line=dict(color='#00ff00', width=2.5)))
    
    fig_teknik.update_layout(
        title=f"{t_kod} - {sure_secimi} Teknik Görünüm",
        template="plotly_white",
        height=450,
        xaxis_title="Zaman",
        yaxis_title="Fiyat (TL)",
        hovermode="x unified"
    )
    st.plotly_chart(fig_teknik, use_container_width=True)
else:
    st.warning(f"{t_kod} için veri çekilemedi. Piyasalar kapalı olabilir veya Yahoo Finance verisi güncelleniyor.")

# --- 6. KIYASLAMA BÖLÜMÜ ---
st.divider()
st.header("📊 Karşılaştırmalı Performans (Normalize 100)")
kiyas_secenek = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"])

# Kıyaslama Verileri
kiyas_tickers = [f"{t_kod}.IS"]
if "Altın (Ons)" in kiyas_secenek: kiyas_tickers.append("GC=F")
if "Gümüş (Ons)" in kiyas_secenek: kiyas_tickers.append("SI=F")

v_kiyas = yf.download(kiyas_tickers, period="1y", progress=False)
if not v_kiyas.empty:
    v_kiyas = v_kiyas['Close']
    fig_n = go.Figure()
    
    # Normalizasyon ve Çizim
    def ciz(col, label, color=None):
        if col in v_kiyas.columns:
            s = v_kiyas[col].dropna()
            if not s.empty:
                fig_n.add_trace(go.Scatter(x=s.index, y=(s/s.iloc[0])*100, name=label, line=dict(color=color)))

    ciz(f"{t_kod}.IS", t_kod, "#1f77b4")
    if "Altın (Ons)" in kiyas_secenek: ciz("GC=F", "Altın", "gold")
    if "Gümüş (Ons)" in kiyas_secenek: ciz("SI=F", "Gümüş", "silver")
    
    if "Enflasyon (%65)" in kiyas_secenek:
        idx = v_kiyas.index
        fig_n.add_trace(go.Scatter(x=idx, y=[100*(1+0.65*(i/len(idx))) for i in range(len(idx))], name="Enflasyon", line=dict(dash='dash', color='red')))
    
    fig_n.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig_n, use_container_width=True)

# --- 7. PÖRTFÖY YÖNETİMİ ---
st.divider()
st.header("💰 Pörtföyüm & Kar-Zarar")
# (Pörtföy kodlarını buraya olduğu gibi ekleyebilirsin, teknik grafik sorunu yukarıdaki blokta çözüldü)
