import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="BIST 100 Terminali - Enes Boz", layout="wide")

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

# --- 3. VERİ FONKSİYONU ---
@st.cache_data(ttl=600)
def veri_hazirla(ticker_list):
    try:
        data = yf.download(ticker_list, period="1y", interval="1d", progress=False)
        if data.empty:
            return None
        # Her zaman DataFrame döndür ve Close sütununa odaklan
        if 'Close' in data:
            return data['Close']
        return None
    except:
        return None

# --- 4. ARAYÜZ ---
st.title("🚀 BIST 100 Stratejik Terminal")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# --- 5. GRAFİK BÖLÜMÜ ---
st.header("📊 Karşılaştırmalı Grafik Analizi")

c1, c2 = st.columns([1, 2])
with c1:
    secim = st.selectbox("Hisse Seçin:", hisse_listesi, index=76)
    secilen_kod = secim.split(" - ")[0]
    kiyas_secenek = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"])

# Ticker listesini oluştur
ana_ticker = f"{secilen_kod}.IS"
indirilecekler = [ana_ticker]
if "Altın (Ons)" in kiyas_secenek: indirilecekler.append("GC=F")
if "Gümüş (Ons)" in kiyas_secenek: indirilecekler.append("SI=F")

veriler = veri_hazirla(indirilecekler)

if veriler is not None:
    fig = go.Figure()
    
    # Yardımcı Çizim Fonksiyonu
    def grafik_ekle(sutun_adi, etiket, renk=None, stil=None):
        # Tek hisse seçildiğinde veriler Series olabilir, çoklu ise DataFrame
        if isinstance(veriler, pd.Series):
            y_verisi = veriler.dropna()
        else:
            y_verisi = veriler[sutun_adi].dropna()
            
        if not y_verisi.empty:
            norm_y = (y_verisi / y_verisi.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=norm_y.index, y=norm_y, name=etiket, 
                                     line=dict(color=renk, dash=stil, width=2.5)))

    # Ana Hisse
    grafik_ekle(ana_ticker, secilen_kod, renk="#1f77b4")

    # Kıyaslamalar
    if "Altın (Ons)" in kiyas_secenek and "GC=F" in veriler.columns:
        grafik_ekle("GC=F", "Altın (Ons)", renk="gold")
    
    if "Gümüş (Ons)" in kiyas_secenek and "SI=F" in veriler.columns:
        grafik_ekle("SI=F", "Gümüş (Ons)", renk="silver")

    if "Enflasyon (%65)" in kiyas_secenek:
        # Enflasyon çizgisi için tarih eksenini ana hisseden al
        h_idx = veriler.index if isinstance(veriler, pd.Series) else veriler[ana_ticker].dropna().index
        enf_y = [100 * (1 + 0.65 * (i/len(h_idx))) for i in range(len(h_idx))]
        fig.add_trace(go.Scatter(x=h_idx, y=enf_y, name="Enflasyon Trendi", 
                                 line=dict(color="red", dash="dash")))

    fig.update_layout(template="plotly_white", height=600, yaxis_title="Getiri Endeksi (100)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Veri çekilemedi. Lütfen internet bağlantısını kontrol edin.")



# --- 6. PORTFÖY MODÜLÜ (Bağımsız Alan) ---
st.divider()
st.header("💰 Portföy Takip")
# Buraya daha önce çalışan portföy kodlarını ekleyebilirsin.
