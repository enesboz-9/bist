import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Terminal - Enes Boz", layout="wide")

# --- 2. BIST 100 LİSTESİ ---
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

def veri_indir_guvenli(tickers, period="1y", interval="1d"):
    try:
        data = yf.download(tickers, period=period, interval=interval, auto_adjust=True, progress=False)
        if data.empty: return None
        return data['Close'].ffill() if isinstance(data.columns, pd.MultiIndex) else data['Close']
    except: return None

st.title("📈 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

t_col1, t_col2 = st.columns([1, 3])
with t_col1:
    ana_secim = st.selectbox("Analiz Edilecek Hisse:", hisse_listesi, index=76)
    t_kod = ana_secim.split(" - ")[0]
    t_sure_etiket = st.radio("Süre Seçin:", ["1 Ay", "1 Yıl", "5 Yıl"], index=1, horizontal=True)

t_periyot = {"1 Ay": "1mo", "1 Yıl": "1y", "5 Yıl": "5y"}
t_aralik = {"1 Ay": "1h", "1 Yıl": "1d", "5 Yıl": "1wk"}
secilen_periyot = t_periyot[t_sure_etiket]

# --- TEKNİK ANALİZ ---
h_fiyat_raw = veri_indir_guvenli(f"{t_kod}.IS", secilen_periyot, t_aralik[t_sure_etiket])
if h_fiyat_raw is not None:
    seri = h_fiyat_raw[f"{t_kod}.IS"] if isinstance(h_fiyat_raw, pd.DataFrame) else h_fiyat_raw
    fig_raw = go.Figure(data=[go.Scatter(x=seri.index, y=seri, line=dict(color='#00d1b2', width=2))])
    fig_raw.update_layout(title=f"{t_kod} Fiyat Hareketleri", template="plotly_white", height=400)
    st.plotly_chart(fig_raw, use_container_width=True)

# --- KIYASLAMA ---
st.divider()
st.header(f"📊 TL Bazlı Performans - {t_sure_etiket}")
kiyas_secenek = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon"], key="kiyas_ms")

indir_list = [f"{t_kod}.IS", "USDTRY=X"]
if "Altın (Ons)" in kiyas_secenek: indir_list.append("GC=F")
if "Gümüş (Ons)" in kiyas_secenek: indir_list.append("SI=F")

veriler = veri_indir_guvenli(indir_list, period=secilen_periyot)

if veriler is not None and isinstance(veriler, pd.DataFrame):
    veriler = veriler.ffill().dropna()
    kur = veriler["USDTRY=X"]
    fig_norm = go.Figure()

    h_seri = veriler[f"{t_kod}.IS"]
    fig_norm.add_trace(go.Scatter(x=h_seri.index, y=(h_seri/h_seri.iloc[0])*100, name=f"{t_kod}", line=dict(width=3)))

    if "Altın (Ons)" in kiyas_secenek:
        altin_tl = veriler["GC=F"] * kur
        fig_norm.add_trace(go.Scatter(x=altin_tl.index, y=(altin_tl/altin_tl.iloc[0])*100, name="Altın (TL)", line=dict(color="gold")))

    if "Gümüş (Ons)" in kiyas_secenek:
        gumus_tl = veriler["SI=F"] * kur
        fig_norm.add_trace(go.Scatter(x=gumus_tl.index, y=(gumus_tl/gumus_tl.iloc[0])*100, name="Gümüş (TL)", line=dict(color="silver")))

    if "Enflasyon" in kiyas_secenek:
        yillar = veriler.index.year.unique()
        enf_oranlari = {2020: 0.14, 2021: 0.19, 2022: 0.72, 2023: 0.65, 2024: 0.55, 2025: 0.45, 2026: 0.35}
        cumulative_enf = [100]
        current_val = 100
        for i in range(1, len(veriler.index)):
            yil = veriler.index[i].year
            oran = enf_oranlari.get(yil, 0.45)
            gunluk_artis = (1 + oran) ** (1/252)
            current_val *= gunluk_artis
            cumulative_enf.append(current_val)
        fig_norm.add_trace(go.Scatter(x=veriler.index, y=cumulative_enf, name="Enflasyon", line=dict(dash='dot', color='red')))

    fig_norm.update_layout(template="plotly_white", height=500, yaxis_title="Getiri Endeksi (100)")
    st.plotly_chart(fig_norm, use_container_width=True)

# --- PÖRTFÖY YÖNETİMİ ---
st.divider()
st.header("💰 Pörtföyüm & Kar-Zarar")

with st.expander("➕ Yeni Hisse Ekle", expanded=True):
    e1, e2, e3 = st.columns([2, 1, 1])
    with e1: p_hisse = st.selectbox("Hisse:", hisse_listesi, key="p_ek")
    with e2: p_maliyet = st.number_input("Maliyet:", min_value=0.01, format="%.2f")
    with e3: p_adet = st.number_input("Adet:", min_value=1, step=1)
    if st.button("Pörtföye Ekle", use_container_width=True):
        pkod = p_hisse.split(" - ")[0]
        st.session_state.portfoy = pd.concat([st.session_state.portfoy, 
                                              pd.DataFrame([{'Hisse': pkod, 'Maliyet': p_maliyet, 'Adet': p_adet}])], 
                                             ignore_index=True)
        st.rerun()

if not st.session_state.portfoy.empty:
    t_maliyet, t_guncel = 0.0, 0.0
    for idx, row in st.session_state.portfoy.iterrows():
        g_veri = yf.download(f"{row['Hisse']}.IS", period="1d", auto_adjust=True, progress=False)
        if not g_veri.empty:
            g_fiyat = float(g_veri['Close'].iloc[-1])
            m_toplam = row['Maliyet'] * row['Adet']
            g_toplam = g_fiyat * row['Adet']
            kz_tl = g_toplam - m_toplam
            t_maliyet += m_toplam
            t_guncel += g_toplam
            renk = "green" if kz_tl >= 0 else "red"
            c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 2, 0.5])
            c1.write(f"**{row['Hisse']}**"); c2.write(f"{row['Maliyet']:.2f}"); c3.write(f"{g_fiyat:.2f}")
            c4.markdown(f":{renk}[{kz_tl:,.2f} TL (%{ (kz_tl/m_toplam)*100 :.2f})]")
            if c5.button("🗑️", key=f"s_{idx}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(idx).reset_index(drop=True)
                st.rerun()
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Yatırım", f"{t_maliyet:,.2f} TL")
    m2.metric("Güncel Değer", f"{t_guncel:,.2f} TL")
    m3.metric("Net Kar/Zarar", f"{t_guncel - t_maliyet:,.2f} TL", delta=f"{((t_guncel/t_maliyet)-1)*100:.2f}%" if t_maliyet > 0 else "0%")
