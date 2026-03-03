import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz - Enes Boz", layout="wide")

# --- PORTFÖY HAFIZASI (Session State) ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet'])

# --- YARDIMCI FONKSİYONLAR ---
@st.cache_data(ttl=600)
def veri_indir(ticker, period="1y", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval)
    return data['Close']

def rsi_hesapla(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def sinyal_uret(ticker):
    # Farklı zaman dilimleri için simüle edilmiş indikatör analizi
    intervals = {"15 Dakika": "15m", "1 Saat": "1h", "1 Gün": "1d", "1 Hafta": "1wk"}
    sinyaller = {}
    
    for label, period in intervals.items():
        # Kısa vadeli periyotlar için sınırlı veri çekilir
        hist = yf.download(ticker, period="5d" if "m" in period else "1y", interval=period, progress=False)
        if len(hist) > 20:
            close = hist['Close'].iloc[-1]
            sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            rsi = rsi_hesapla(hist['Close']).iloc[-1]
            
            if rsi < 35 and close > sma20: sinyaller[label] = "✅ GÜÇLÜ AL"
            elif rsi < 45: sinyaller[label] = "🟢 AL"
            elif rsi > 65: sinyaller[label] = "🔴 SAT"
            elif rsi > 75: sinyaller[label] = "❌ GÜÇLÜ SAT"
            else: sinyaller[label] = "🟡 BEKLE"
        else:
            sinyaller[label] = "Veri Yetersiz"
    return sinyaller

# --- ANA BAŞLIK ---
st.title("📈 BIST Stratejik Analiz Paneli")
st.caption("Enes Boz Tarafından Geliştirildi")

# --- 1. BÖLÜM: PORTFÖY YÖNETİMİ (EKLE/SİL) ---
st.header("💰 Portföy Yönetimi")
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1: hisse_sec = st.text_input("Hisse Kodu (Örn: THYAO)", "THYAO").upper()
with c2: m_input = st.number_input("Maliyet", min_value=0.0)
with c3: a_input = st.number_input("Adet", min_value=0)
with c4: 
    st.write("##")
    if st.button("Hisse Ekle"):
        yeni_satir = pd.DataFrame([{'Hisse': hisse_sec, 'Maliyet': m_input, 'Adet': a_input}])
        st.session_state.portfoy = pd.concat([st.session_state.portfoy, yeni_satir], ignore_index=True)

if not st.session_state.portfoy.empty:
    st.subheader("Mevcut Varlıklar")
    toplam_guncel_deger = 0.0
    toplam_maliyet = 0.0
    
    for index, row in st.session_state.portfoy.iterrows():
        try:
            guncel_fiyat = yf.download(f"{row['Hisse']}.IS", period="1d", progress=False)['Close'].iloc[-1]
            hisse_deger = guncel_fiyat * row['Adet']
            hisse_maliyet = row['Maliyet'] * row['Adet']
            
            toplam_guncel_deger += hisse_deger
            toplam_maliyet += hisse_maliyet
            
            col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 1])
            col_a.write(f"**{row['Hisse']}**")
            col_b.write(f"{row['Adet']} Adet | Maliyet: {row['Maliyet']}")
            col_c.write(f"K/Z: {hisse_deger - hisse_maliyet:.2f} TL")
            if col_d.button("Sil", key=f"sil_{index}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(index)
                st.rerun()
        except: st.error(f"{row['Hisse']} verisi alınamadı.")

    st.divider()
    m1, m2 = st.columns(2)
    m1.metric("Toplam Portföy Değeri", f"{toplam_guncel_deger:,.2f} TL")
    m2.metric("Toplam Kar/Zarar", f"{toplam_guncel_deger - toplam_maliyet:,.2f} TL", 
              delta=f"{((toplam_guncel_deger/toplam_maliyet)-1)*100:.2f}%" if toplam_maliyet > 0 else "0%")

# --- 2. BÖLÜM: AL-SAT SİNYALLERİ ---
st.header("🎯 İndikatör Sinyalleri (RSI & SMA)")
if st.button("Seçili Hisse İçin Sinyal Üret"):
    sinyaller = sinyal_uret(f"{hisse_sec}.IS")
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("15 Dakika", sinyaller["15 Dakika"])
    sc2.metric("1 Saat", sinyaller["1 Saat"])
    sc3.metric("1 Gün", sinyaller["1 Gün"])
    sc4.metric("1 Hafta", sinyaller["1 Hafta"])

# --- 3. BÖLÜM: KIYASLAMALI GRAFİK ---
st.header("📊 Teknik Kıyaslama")
karsilastirma = st.multiselect("Kıyaslama Varlıkları Ekleyin:", ["Altın (Gram)", "Gümüş (Gram)", "Enflasyon (TÜFE Tahmini)"])

hisse_kapanis = veri_indir(f"{hisse_sec}.IS")
# Normalizasyon (Başlangıç noktasını 100 yapma)
hisse_norm = (hisse_kapanis / hisse_kapanis.iloc[0]) * 100

fig = go.Figure()
fig.add_trace(go.Scatter(x=hisse_norm.index, y=hisse_norm, name=f"{hisse_sec} (Normalize)"))

if "Altın (Gram)" in karsilastirma:
    altin = veri_indir("GAU=X") # Gram Altın / USD benzeri veya XAUUSD üzerinden simüle
    altin_norm = (altin / altin.iloc[0]) * 100
    fig.add_trace(go.Scatter(x=altin_norm.index, y=altin_norm, name="Altın", line=dict(color='gold')))

if "Gümüş (Gram)" in karsilastirma:
    gumus = veri_indir("XAGUSD=X")
    gumus_norm = (gumus / gumus.iloc[0]) * 100
    fig.add_trace(go.Scatter(x=gumus_norm.index, y=gumus_norm, name="Gümüş", line=dict(color='silver')))

if "Enflasyon (TÜFE Tahmini)" in karsilastirma:
    # Yıllık %65 enflasyon varsayımı ile doğrusal grafik
    enf_cizgi = [100 * (1 + 0.65 * (i/len(hisse_norm))) for i in range(len(hisse_norm))]
    fig.add_trace(go.Scatter(x=hisse_norm.index, y=enf_cizgi, name="Yıllık Enflasyon Trendi", line=dict(dash='dash', color='red')))

st.plotly_chart(fig, use_container_width=True)
st.info("Grafikteki tüm varlıklar, karşılaştırma yapabilmeniz için başlangıç tarihinde 100 değerine eşitlenmiştir (Normalize).")
