import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz - Enes Boz", layout="wide")

# --- 2. OTURUM YÖNETİMİ ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet'])

# --- 3. VERİ FONKSİYONLARI ---
@st.cache_data(ttl=300)
def veri_cek_garanti(ticker):
    try:
        # Veriyi indir ve sadece kapanış sütununu al
        data = yf.download(ticker, period="1y", interval="1d", progress=False)
        if data.empty:
            return None
        # Multi-index yapısını düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            return data['Close'][ticker]
        return data['Close']
    except:
        return None

def rsi_hesapla(series, window=14):
    if series is None or len(series) < window: return 50.0
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return float(100 - (100 / (1 + rs)).iloc[-1])

# --- 4. ARAYÜZ BAŞLIĞI ---
st.title("📈 BIST Stratejik Analiz Paneli")
st.subheader("Geliştirici: Enes Boz")
st.divider()

# --- 5. PORTFÖY BÖLÜMÜ ---
st.header("💰 Portföy Yönetimi")
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1: h_input = st.text_input("Hisse Kodu (Örn: THYAO)", "THYAO").upper()
with c2: m_input = st.number_input("Maliyet", min_value=0.0, step=0.01)
with c3: a_input = st.number_input("Adet", min_value=0, step=1)
with c4:
    st.write("##")
    if st.button("Hisse Ekle"):
        new_row = pd.DataFrame([{'Hisse': h_input, 'Maliyet': m_input, 'Adet': a_input}])
        st.session_state.portfoy = pd.concat([st.session_state.portfoy, new_row], ignore_index=True)

# Portföy Hesaplamaları
toplam_m, toplam_d = 0.0, 0.0

if not st.session_state.portfoy.empty:
    for idx, row in st.session_state.portfoy.iterrows():
        fiyatlar = veri_cek_garanti(f"{row['Hisse']}.IS")
        if fiyatlar is not None:
            guncel_f = float(fiyatlar.iloc[-1])
            h_m = float(row['Maliyet'] * row['Adet'])
            h_d = float(guncel_f * row['Adet'])
            toplam_m += h_m
            toplam_d += h_d
            
            p_col = st.columns([1, 1, 1, 1])
            p_col[0].write(f"**{row['Hisse']}**")
            p_col[1].write(f"{row['Adet']} Adet")
            p_col[2].write(f"K/Z: {h_d - h_m:,.2f} TL")
            if p_col[3].button("Sil", key=f"btn_{idx}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(idx).reset_index(drop=True)
                st.rerun()

    st.divider()
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Toplam Portföy Değeri", f"{toplam_d:,.2f} TL")
    m_col2.metric("Toplam Kar/Zarar", f"{toplam_d - toplam_m:,.2f} TL", 
                  delta=f"{((toplam_d/toplam_m)-1)*100:.2f}%" if toplam_m > 0 else "0%")

# --- 6. KIYASLAMA VE GRAFİK ---
st.header("📊 Karşılaştırmalı Grafik")
secenekler = st.multiselect("Ekle:", ["Altın", "Gümüş", "Enflasyon"])

h_fiyat = veri_cek_garanti(f"{h_input}.IS")
if h_fiyat is not None:
    fig = go.Figure()
    # Normalize Et
    h_norm = (h_fiyat / h_fiyat.iloc[0]) * 100
    fig.add_trace(go.Scatter(x=h_norm.index, y=h_norm, name=f"{h_input}"))

    if "Altın" in secenekler:
        a_f = veri_cek_garanti("GC=F")
        if a_f is not None:
            a_n = (a_f / a_f.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=a_n.index, y=a_n, name="Altın", line=dict(color='gold')))

    if "Enflasyon" in secenekler:
        enf = [100 * (1 + 0.65 * (i/len(h_norm))) for i in range(len(h_norm))]
        fig.add_trace(go.Scatter(x=h_norm.index, y=enf, name="Enflasyon (%65)", line=dict(dash='dash', color='red')))

    st.plotly_chart(fig, use_container_width=True)

# --- 7. SİNYALLER ---
st.header("🎯 Al-Sat Sinyalleri")
if st.button("Analiz Et"):
    zamanlar = {"15 Dakika": "15m", "1 Saat": "1h", "1 Gün": "1d"}
    s_cols = st.columns(3)
    for i, (label, interval) in enumerate(zamanlar.items()):
        p = "5d" if "m" in interval else "1mo"
        data_s = yf.download(f"{h_input}.IS", period=p, interval=interval, progress=False)
        if not data_s.empty:
            # Multi-index düzeltme
            close_s = data_s['Close'][f"{h_input}.IS"] if isinstance(data_s.columns, pd.MultiIndex) else data_s['Close']
            r = rsi_hesapla(close_s)
            txt = "🟢 AL" if r < 35 else "🔴 SAT" if r > 65 else "🟡 BEKLE"
            s_cols[i].metric(label, txt, delta=f"RSI: {r:.1f}")
