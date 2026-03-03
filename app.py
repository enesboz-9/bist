import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz Terminali - Enes Boz", layout="wide")

# --- CSS TASARIM ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_index=True)

# --- OTURUM YÖNETİMİ (Portföy Kaydı) ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet'])

# --- VERİ ÇEKME FONKSİYONLARI ---
@st.cache_data(ttl=600)
def veri_indir_guvenli(ticker, period="1y"):
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty or 'Close' not in data:
            return pd.Series()
        return data['Close']
    except:
        return pd.Series()

def rsi_hesapla(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- ARAYÜZ ---
st.title("📊 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# --- 1. PORTFÖY YÖNETİMİ ---
st.header("💰 Portföyüm")
col_e1, col_e2, col_e3, col_e4 = st.columns([2, 1, 1, 1])

with col_e1: h_input = st.text_input("Hisse Kodu (Örn: THYAO, ASELS)", "THYAO").upper()
with col_e2: m_input = st.number_input("Alış Maliyeti", min_value=0.0, step=0.01)
with col_e3: a_input = st.number_input("Adet", min_value=0, step=1)
with col_e4:
    st.write("##")
    if st.button("Portföye Ekle"):
        new_data = pd.DataFrame([{'Hisse': h_input, 'Maliyet': m_input, 'Adet': a_input}])
        st.session_state.portfoy = pd.concat([st.session_state.portfoy, new_data], ignore_index=True)

# Portföy Listeleme ve Toplam Hesaplama
if not st.session_state.portfoy.empty:
    st.subheader("Varlık Listesi")
    t_maliyet, t_deger = 0.0, 0.0
    
    for idx, row in st.session_state.portfoy.iterrows():
        fiyat_serisi = veri_indir_guvenli(f"{row['Hisse']}.IS", period="5d")
        if not fiyat_serisi.empty:
            guncel_f = fiyat_serisi.iloc[-1]
            h_maliyet = row['Maliyet'] * row['Adet']
            h_deger = guncel_f * row['Adet']
            t_maliyet += h_maliyet
            t_deger += h_deger
            
            c_h, c_m, c_kz, c_s = st.columns([1, 1, 1, 1])
            c_h.write(f"**{row['Hisse']}**")
            c_m.write(f"{row['Adet']} Adet @ {row['Maliyet']:.2f}")
            kz_tl = h_deger - h_maliyet
            c_kz.write(f"K/Z: {kz_tl:,.2f} TL")
            if c_s.button("Sil", key=f"del_{idx}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(idx)
                st.rerun()
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Değer", f"{t_deger:,.2f} TL")
    m2.metric("Toplam K/Z", f"{t_deger - t_maliyet:,.2f} TL")
    if t_maliyet > 0:
        m3.metric("Yüzdesel Başarı", f"%{((t_deger/t_maliyet)-1)*100:.2f}")

# --- 2. TEKNİK SİNYALLER ---
st.divider()
st.header("🎯 Çoklu Zaman Dilimi Sinyalleri")
if st.button("İndikatörleri Analiz Et"):
    intervals = {"15 Dakika": "15m", "1 Saat": "1h", "1 Gün": "1d"}
    scs = st.columns(3)
    for i, (label, period) in enumerate(intervals.items()):
        try:
            h = yf.download(f"{h_input}.IS", period="5d" if "m" in period else "1mo", interval=period, progress=False)
            if not h.empty:
                rsi_v = rsi_hesapla(h['Close']).iloc[-1]
                if rsi_v < 30: msg = "🟢 AL"
                elif rsi_v > 70: msg = "🔴 SAT"
                else: msg = "🟡 BEKLE"
                scs[i].metric(label, msg, delta=f"RSI: {rsi_v:.1f}")
        except:
            scs[i].write(f"{label}: Veri Hatası")

# --- 3. KIYASLAMA VE GRAFİK ---
st.divider()
st.header("📉 Karşılaştırmalı Analiz (Normalize)")
kıyas = st.multiselect("Grafiğe Ekle:", ["Altın (Gram)", "Gümüş (Gram)", "Enflasyon (Tahmini)"])

h_data = veri_indir_guvenli(f"{h_input}.IS")
if not h_data.empty:
    fig = go.Figure()
    # Başlangıcı 100'e sabitle
    h_norm = (h_data / h_data.iloc[0]) * 100
    fig.add_trace(go.Scatter(x=h_norm.index, y=h_norm, name=f"{h_input}"))

    if "Altın (Gram)" in kıyas:
        a_data = veri_indir_guvenli("GAU=X") # Altın/USD yaklaşık takibi
        if not a_data.empty:
            a_norm = (a_data / a_data.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=a_norm.index, y=a_norm, name="Altın", line=dict(color='gold')))

    if "Gümüş (Gram)" in kıyas:
        g_data = veri_indir_guvenli("XAGUSD=X")
        if not g_data.empty:
            g_norm = (g_data / g_data.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=g_norm.index, y=g_norm, name="Gümüş", line=dict(color='silver')))

    if "Enflasyon (Tahmini)" in kıyas:
        # Türkiye yıllık enflasyon trend simülasyonu (Yaklaşık %65)
        enf = [100 * (1 + 0.65 * (i/len(h_norm))) for i in range(len(h_norm))]
        fig.add_trace(go.Scatter(x=h_norm.index, y=enf, name="Enflasyon Trendi", line=dict(dash='dash', color='red')))

    fig.update_layout(template="plotly_white", height=600, yaxis_title="Getiri Endeksi (Başlangıç=100)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Hisse verisi çekilemedi. Lütfen sembolü kontrol edin.")
