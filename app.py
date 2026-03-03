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

# --- 3. VERİ ÇEKME FONKSİYONU ---
def veri_cek_teknik(ticker, periyot="1y", aralik="1d"):
    try:
        data = yf.download(ticker, period=periyot, interval=aralik, progress=False)
        if data.empty: return None
        # Multi-index yapısını güvenli okuma
        if isinstance(data.columns, pd.MultiIndex):
            return data['Close'][ticker]
        return data['Close']
    except:
        return None

# --- 4. ARAYÜZ ---
st.title("📈 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# --- 5. TEKNİK GRAFİK VE SÜRE BUTONLARI ---
st.header("🔍 Hisse Teknik Analizi")
t_col1, t_col2 = st.columns([1, 2])

with t_col1:
    teknik_secim = st.selectbox("Analiz Edilecek Hisse:", hisse_listesi, index=76)
    t_kod = teknik_secim.split(" - ")[0]
    
    # Süre Butonları (Radio butonu ile daha şık durur)
    sure_secimi = st.radio("Zaman Aralığı Seçin:", 
                           ["1 Gün", "1 Ay", "1 Yıl", "5 Yıl", "Maksimum"], 
                           index=2, horizontal=True)

# Süre eşleştirme
periyot_map = {"1 Gün": "1d", "1 Ay": "1mo", "1 Yıl": "1y", "5 Yıl": "5y", "Maksimum": "max"}
aralik_map = {"1 Gün": "1m", "1 Ay": "1h", "1 Yıl": "1d", "5 Yıl": "1wk", "Maksimum": "1wk"}

with st.spinner("Veri hazırlanıyor..."):
    hisse_fiyatlari = veri_cek_teknik(f"{t_kod}.IS", 
                                     periyot=periyot_map[sure_secimi], 
                                     aralik=aralik_map[sure_secimi])

if hisse_fiyatlari is not None:
    fig_teknik = go.Figure()
    fig_teknik.add_trace(go.Scatter(x=hisse_fiyatlari.index, y=hisse_fiyatlari, 
                                   name=t_kod, line=dict(color='#00d1b2', width=2)))
    
    fig_teknik.update_layout(
        title=f"{t_kod} - {sure_secimi} Grafiği",
        template="plotly_white",
        height=500,
        xaxis_rangeslider_visible=False,
        yaxis_title="Fiyat (TL)"
    )
    st.plotly_chart(fig_teknik, use_container_width=True)
    
else:
    st.warning(f"{t_kod} için {sure_secimi} aralığında veri bulunamadı. Lütfen piyasa saatlerini veya sembolü kontrol edin.")

# --- 6. KARŞILAŞTIRMALI ANALİZ ---
st.divider()
st.header("📊 Kıyaslama (Normalize 100)")
kiyas_secenek = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"])

def kiyas_indir(tickers):
    d = yf.download(tickers, period="1y", progress=False)
    return d['Close'] if not d.empty else None

veriler_kiyas = kiyas_indir([f"{t_kod}.IS", "GC=F", "SI=F"])

if veriler_kiyas is not None:
    fig_norm = go.Figure()
    # Ana Hisse
    h_data = veriler_kiyas[f"{t_kod}.IS"].dropna()
    fig_norm.add_trace(go.Scatter(x=h_data.index, y=(h_data/h_data.iloc[0])*100, name=t_kod))
    
    if "Altın (Ons)" in kiyas_secenek:
        a_data = veriler_kiyas["GC=F"].dropna()
        fig_norm.add_trace(go.Scatter(x=a_data.index, y=(a_data/a_data.iloc[0])*100, name="Altın", line=dict(color="gold")))
    
    if "Enflasyon (%65)" in kiyas_secenek:
        idx = h_data.index
        fig_norm.add_trace(go.Scatter(x=idx, y=[100*(1+0.65*(i/len(idx))) for i in range(len(idx))], name="Enflasyon", line=dict(dash='dash', color='red')))
    
    st.plotly_chart(fig_norm, use_container_width=True)

# --- 7. PORTFÖY YÖNETİMİ ---
st.divider()
st.header("💰 Portföyüm")
col1, col2, col3 = st.columns([2, 1, 1])
with col1: p_hisse = st.selectbox("Hisse Seç:", hisse_listesi, key="p_sel")
with col2: p_maliyet = st.number_input("Maliyet", min_value=0.0)
with col3: p_adet = st.number_input("Adet", min_value=1)

if st.button("Portföye Ekle"):
    pkod = p_hisse.split(" - ")[0]
    st.session_state.portfoy = pd.concat([st.session_state.portfoy, 
                                          pd.DataFrame([{'Hisse': pkod, 'Maliyet': p_maliyet, 'Adet': p_adet}])], 
                                         ignore_index=True)
    st.rerun()

# Portföy Listesi (Basit Tablo)
if not st.session_state.portfoy.empty:
    st.dataframe(st.session_state.portfoy, use_container_width=True)
