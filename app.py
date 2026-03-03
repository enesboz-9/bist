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

# --- 3. OTURUM YÖNETİMİ (Portföy Hafızası) ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet'])

# --- 4. VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=300)
def veri_indir(tickers):
    try:
        data = yf.download(tickers, period="1y", interval="1d", progress=False)
        return data['Close'] if not data.empty else None
    except:
        return None

# --- 5. ARAYÜZ BAŞLANGIÇ ---
st.title("📈 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# --- 6. TEKNİK ANALİZ GRAFİĞİ (BAĞIMSIZ) ---
st.header("🔍 Hisse Teknik Analizi")
secilen_hisse_str = st.selectbox("Teknik Grafik İçin Hisse Seçin:", hisse_listesi, index=76)
secilen_kod = secilen_hisse_str.split(" - ")[0]

hisse_verisi = veri_indir(f"{secilen_kod}.IS")
if hisse_verisi is not None:
    fig_raw = go.Figure()
    fig_raw.add_trace(go.Scatter(x=hisse_verisi.index, y=hisse_verisi, name="Fiyat", line=dict(color='#00ff00', width=2)))
    fig_raw.update_layout(title=f"{secilen_kod} Günlük Fiyat Grafiği", template="plotly_white", height=400)
    st.plotly_chart(fig_raw, use_container_width=True)

# --- 7. KARŞILAŞTIRMALI ANALİZ GRAFİĞİ ---
st.divider()
st.header("📊 Kıyaslama (Normalize 100)")
kiyas_secenek = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"], key="kiyas_multiselect")

indirilecekler = [f"{secilen_kod}.IS"]
if "Altın (Ons)" in kiyas_secenek: indirilecekler.append("GC=F")
if "Gümüş (Ons)" in kiyas_secenek: indirilecekler.append("SI=F")

veriler_kiyas = veri_indir(indirilecekler)
if veriler_kiyas is not None:
    fig_norm = go.Figure()
    def norm_ciz(col, label, color=None):
        series = veriler_kiyas[col].dropna() if isinstance(veriler_kiyas, pd.DataFrame) else veriler_kiyas.dropna()
        if not series.empty:
            fig_norm.add_trace(go.Scatter(x=series.index, y=(series/series.iloc[0])*100, name=label, line=dict(color=color)))

    norm_ciz(f"{secilen_kod}.IS" if isinstance(veriler_kiyas, pd.DataFrame) else None, secilen_kod, "#1f77b4")
    if "Altın (Ons)" in kiyas_secenek: norm_ciz("GC=F", "Altın", "gold")
    if "Gümüş (Ons)" in kiyas_secenek: norm_ciz("SI=F", "Gümüş", "silver")
    if "Enflasyon (%65)" in kiyas_secenek:
        idx = veriler_kiyas.index
        fig_norm.add_trace(go.Scatter(x=idx, y=[100*(1+0.65*(i/len(idx))) for i in range(len(idx))], name="Enflasyon", line=dict(dash='dash', color='red')))
    
    st.plotly_chart(fig_norm, use_container_width=True)

# --- 8. PORTFÖY TAKİP SİSTEMİ ---
st.divider()
st.header("💰 Portföy Yönetim Masası")

# Ekleme Formu
with st.container():
    p1, p2, p3, p4 = st.columns([2, 1, 1, 1])
    with p1: p_hisse = st.selectbox("Portföye Eklenecek Hisse:", hisse_listesi, key="p_add")
    with p2: p_maliyet = st.number_input("Alış Fiyatı (TL)", min_value=0.0, step=0.01, format="%.2f")
    with p3: p_adet = st.number_input("Adet", min_value=1, step=1)
    with p4:
        st.write("##")
        if st.button("Hisse Ekle"):
            kod = p_hisse.split(" - ")[0]
            yeni_hisse = pd.DataFrame([{'Hisse': kod, 'Maliyet': p_maliyet, 'Adet': p_adet}])
            st.session_state.portfoy = pd.concat([st.session_state.portfoy, yeni_hisse], ignore_index=True)
            st.rerun()

# Liste ve Kar/Zarar Hesaplama
if not st.session_state.portfoy.empty:
    st.subheader("Varlıklarım")
    toplam_maliyet, toplam_guncel = 0.0, 0.0
    
    for idx, row in st.session_state.portfoy.iterrows():
        fiyat_bilgi = yf.download(f"{row['Hisse']}.IS", period="1d", progress=False)
        if not fiyat_bilgi.empty:
            guncel_f = float(fiyat_bilgi['Close'].iloc[-1])
            alis_tutar = row['Maliyet'] * row['Adet']
            guncel_tutar = guncel_f * row['Adet']
            kz_tl = guncel_tutar - alis_tutar
            toplam_maliyet += alis_tutar
            toplam_guncel += guncel_tutar

            r1, r2, r3, r4, r5 = st.columns([1, 1, 1, 1, 0.5])
            r1.write(f"**{row['Hisse']}**")
            r2.write(f"Maliyet: {row['Maliyet']:.2f}")
            r3.write(f"Güncel: {guncel_f:.2f}")
            r4.write(f"K/Z: {kz_tl:,.2f} TL")
            if r5.button("❌", key=f"del_{idx}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(idx).reset_index(drop=True)
                st.rerun()

    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Toplam Alış Tutarı", f"{toplam_maliyet:,.2f} TL")
    res2.metric("Toplam Güncel Değer", f"{toplam_guncel:,.2f} TL")
    res3.metric("Toplam Kar/Zarar", f"{toplam_guncel - toplam_maliyet:,.2f} TL", 
                delta=f"{((toplam_guncel/toplam_maliyet)-1)*100:.2f}%" if toplam_maliyet > 0 else "0%")
