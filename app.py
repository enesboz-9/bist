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

# --- 3. VERİ FONKSİYONU ---
def veri_indir_guvenli(ticker, periyot="1y", aralik="1d"):
    try:
        data = yf.download(ticker, period=periyot, interval=aralik, progress=False)
        if data.empty: return None
        if isinstance(data.columns, pd.MultiIndex): return data['Close'][ticker]
        return data['Close']
    except: return None

# --- 4. ARAYÜZ ÜST PANEL ---
st.title("🚀 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# --- 5. TEKNİK ANALİZ ---
st.header("🔍 Hisse Teknik Analizi")
t_col1, t_col2 = st.columns([1, 3])
with t_col1:
    ana_secim = st.selectbox("Analiz Edilecek Hisse:", hisse_listesi, index=76)
    t_kod = ana_secim.split(" - ")[0]
    t_sure = st.radio("Süre:", ["1 Ay", "1 Yıl", "5 Yıl"], index=1, horizontal=True)

p_map = {"1 Ay": "1mo", "1 Yıl": "1y", "5 Yıl": "5y"}
a_map = {"1 Ay": "1h", "1 Yıl": "1d", "5 Yıl": "1wk"}

h_fiyat = veri_indir_guvenli(f"{t_kod}.IS", p_map[t_sure], a_map[t_sure])
if h_fiyat is not None:
    fig_raw = go.Figure(data=[go.Scatter(x=h_fiyat.index, y=h_fiyat, line=dict(color='#00d1b2', width=2))])
    fig_raw.update_layout(template="plotly_white", height=400, yaxis_title="Fiyat (TL)")
    st.plotly_chart(fig_raw, use_container_width=True)

# --- 6. KIYASLAMA VE BİLGİLENDİRME ---
st.divider()
st.header("📊 Karşılaştırmalı Performans (Normalize 100)")
kiyas_secenek = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"])

k_tickers = [f"{t_kod}.IS"]
if "Altın (Ons)" in kiyas_secenek: k_tickers.append("GC=F")
if "Gümüş (Ons)" in kiyas_secenek: k_tickers.append("SI=F")

v_kiyas = yf.download(k_tickers, period="1y", progress=False)
if not v_kiyas.empty:
    v_kiyas = v_kiyas['Close']
    fig_n = go.Figure()
    def ciz(tic, label, col):
        if tic in v_kiyas.columns or (len(k_tickers) == 1):
            s = v_kiyas[tic].dropna() if len(k_tickers) > 1 else v_kiyas.dropna()
            if not s.empty:
                fig_n.add_trace(go.Scatter(x=s.index, y=(s/s.iloc[0])*100, name=label, line=dict(color=col)))
    
    ciz(f"{t_kod}.IS" if len(k_tickers) > 1 else None, t_kod, "#1f77b4")
    if "Altın (Ons)" in kiyas_secenek: ciz("GC=F", "Altın", "gold")
    if "Gümüş (Ons)" in kiyas_secenek: ciz("SI=F", "Gümüş", "silver")
    if "Enflasyon (%65)" in kiyas_secenek:
        idx = v_kiyas.index
        fig_n.add_trace(go.Scatter(x=idx, y=[100*(1+0.65*(i/len(idx))) for i in range(len(idx))], name="Enflasyon", line=dict(dash='dash', color='red')))
    
    st.plotly_chart(fig_n, use_container_width=True)

    with st.expander("ℹ️ Kullanım Amacı ve Grafik Yorumlama", expanded=True):
        st.info("Bu grafik, farklı varlıkları **100** baz puanına eşitleyerek hangisinin daha yüksek **yüzdesel getiri** sağladığını gösterir. Kırmızı kesikli çizginin (enflasyon) altında kalan varlıklar reel olarak zarar ettirmektedir.")

# --- 7. PÖRTFÖY YÖNETİMİ (DÜZELTİLMİŞ KAR-ZARAR) ---
st.divider()
st.header("💰 Pörtföyüm & Kar-Zarar Analizi")

with st.expander("➕ Hisse Ekle", expanded=True):
    e1, e2, e3 = st.columns([2, 1, 1])
    with e1: p_hisse = st.selectbox("Hisse:", hisse_listesi, key="p_ek")
    with e2: p_maliyet = st.number_input("Maliyet:", min_value=0.01, format="%.2f")
    with e3: p_adet = st.number_input("Adet:", min_value=1, step=1)
    if st.button("Pörtföye Kaydet", use_container_width=True):
        pkod = p_hisse.split(" - ")[0]
        st.session_state.portfoy = pd.concat([st.session_state.portfoy, pd.DataFrame([{'Hisse': pkod, 'Maliyet': p_maliyet, 'Adet': p_adet}])], ignore_index=True)
        st.rerun()

if not st.session_state.portfoy.empty:
    t_maliyet, t_guncel = 0.0, 0.0
    
    # Başlıklar
    h1, h2, h3, h4, h5 = st.columns([1, 1, 1, 1.5, 0.5])
    h1.write("**Hisse**"); h2.write("**Maliyet**"); h3.write("**Güncel**"); h4.write("**Kar/Zarar (TL / %)**"); h5.write("")

    for idx, row in st.session_state.portfoy.iterrows():
        g_veri = yf.download(f"{row['Hisse']}.IS", period="1d", progress=False)
        if not g_veri.empty:
            g_fiyat = float(g_veri['Close'].iloc[-1])
            alis_toplam = row['Maliyet'] * row['Adet']
            guncel_toplam = g_fiyat * row['Adet']
            kz_tl = guncel_toplam - alis_toplam
            kz_yuzde = (kz_tl / alis_toplam) * 100
            
            t_maliyet += alis_toplam
            t_guncel += guncel_toplam

            renk = "green" if kz_tl >= 0 else "red"
            c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.5, 0.5])
            c1.write(f"**{row['Hisse']}**")
            c2.write(f"{row['Maliyet']:.2f} TL")
            c3.write(f"{g_fiyat:.2f} TL")
            c4.markdown(f":{renk}[{kz_tl:,.2f} TL (%{kz_yuzde:.2f})]")
            if c5.button("🗑️", key=f"s_{idx}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(idx).reset_index(drop=True)
                st.rerun()

    # Özet Metrik Kartları
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Yatırım", f"{t_maliyet:,.2f} TL")
    m2.metric("Pörtföy Değeri", f"{t_guncel:,.2f} TL")
    m3.metric("Net Kar/Zarar", f"{t_guncel - t_maliyet:,.2f} TL", delta=f"{((t_guncel/t_maliyet)-1)*100:.2f}%" if t_maliyet > 0 else "0%")
