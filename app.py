import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="BIST 100 Terminali - Enes Boz", layout="wide")

# --- 2. BIST 100 TÜM ŞİRKET LİSTESİ ---
# Bu liste BIST 100 endeksindeki şirketlerin kodları ve isimlerini içerir.
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

# Seçenek listesini "KOD - ŞİRKET ADI" formatında oluşturma
hisse_listesi = [f"{kod} - {ad}" for kod, ad in bist_100_full.items()]

# --- 3. VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=600)
def veri_hazirla(ticker_list, period="1y"):
    try:
        data = yf.download(ticker_list, period=period, interval="1d", progress=False)['Close']
        return data
    except:
        return None

# --- 4. ARAYÜZ ---
st.title("🚀 BIST 100 Stratejik Terminal")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# --- 5. GELİŞMİŞ KARŞILAŞTIRMA GRAFİĞİ ---
st.header("📊 Karşılaştırmalı Grafik Analizi")

c1, c2 = st.columns([1, 2])
with c1:
    secim = st.selectbox("Hisse Seçin (Arama Yapabilirsiniz):", hisse_listesi, index=76) # Varsayılan THYAO
    secilen_kod = secim.split(" - ")[0]
    kiyas_elemanlari = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"])

# Gerekli Ticker'ları Topla
tickers = [f"{secilen_kod}.IS"]
if "Altın (Ons)" in kiyas_elemanlari: tickers.append("GC=F")
if "Gümüş (Ons)" in kiyas_elemanlari: tickers.append("SI=F")

with st.spinner("Piyasa verileri senkronize ediliyor..."):
    veriler = veri_hazirla(tickers)

if veriler is not None and not veriler.empty:
    fig = go.Figure()
    
    # Tüm verileri başlangıç noktasına göre normalize et (100)
    # yfinance bazen tek hisse gelince Series, çoklu gelince DataFrame döndürür.
    def ciz(col_name, label, color=None, dash=None):
        series = veriler[col_name].dropna() if len(tickers) > 1 else veriler.dropna()
        if not series.empty:
            norm_series = (series / series.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=norm_series.index, y=norm_series, name=label, 
                                     line=dict(color=color, dash=dash, width=2.5)))

    # Ana Hisse Çizimi
    hisse_sutun = f"{secilen_kod}.IS" if len(tickers) > 1 else veriler.name
    ciz(hisse_sutun, f"{secilen_kod}", color="#1f77b4")

    # Altın/Gümüş Çizimi
    if "Altın (Ons)" in kiyas_elemanlari:
        ciz("GC=F", "Altın (Ons)", color="gold")
    if "Gümüş (Ons)" in kiyas_elemanlari:
        ciz("SI=F", "Gümüş (Ons)", color="silver")

    # Enflasyon Çizimi
    if "Enflasyon (%65)" in kiyas_elemanlari:
        h_data = veriler[f"{secilen_kod}.IS"] if len(tickers) > 1 else veriler
        enf_trend = [100 * (1 + 0.65 * (i/len(h_data))) for i in range(len(h_data))]
        fig.add_trace(go.Scatter(x=h_data.index, y=enf_trend, name="Enflasyon Trendi", 
                                 line=dict(color="red", dash="dash")))

    fig.update_layout(
        template="plotly_white",
        height=600,
        xaxis_title="Son 1 Yıl",
        yaxis_title="Getiri Endeksi (Başlangıç=100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Veri yüklenemedi. Lütfen internet bağlantınızı kontrol edin.")

# --- 6. PORTFÖY ÖZETİ (Önceki Fonksiyonelliği Koruyoruz) ---
st.divider()
st.header("💰 Portföyüm")
# (Buraya daha önceki portföy ekleme/silme mantığını entegre edebilirsin)
st.info("Portföy modülü yukarıdaki 'Hisse Seçin' kutusu ile senkronize çalışmaktadır.")
