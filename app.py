import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz Pro", layout="wide")

# --- TEKNİK HESAPLAMA FONKSİYONLARI ---
def teknik_verileri_hesapla(df):
    # 20 Günlük Hareketli Ortalama
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # RSI (14) Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

@st.cache_data(ttl=3600)
def veri_cek(semboller):
    yf_semboller = [f"{s}.IS" for s in semboller]
    data = yf.download(yf_semboller, period="1y")['Close']
    return data

# --- ARAYÜZ BAŞLANGIÇ ---
st.title("📈 BIST 100 Teknik Analiz & Portföy")

# 1. Liste Yükleme
try:
    bist_list = pd.read_csv("bist100_listesi.csv")['Sembol'].tolist()
except:
    st.error("bist100_listesi.csv bulunamadı!")
    st.stop()

# 2. Veri Çekme
with st.spinner("Borsa verileri yükleniyor..."):
    fiyat_verileri = veri_cek(bist_list)

# 3. Yıllık Performans ve Renkli Tablo Hazırlığı
perf_data = []
for s in bist_list:
    hisse_serisi = fiyat_verileri[f"{s}.IS"].dropna()
    if not hisse_serisi.empty:
        guncel = hisse_serisi.iloc[-1]
        eski = hisse_serisi.iloc[0]
        degisim = ((guncel - eski) / eski) * 100
        perf_data.append({"Hisse": s, "Fiyat": round(guncel, 2), "Yıllık Değişim (%)": round(degisim, 2)})

df_perf = pd.DataFrame(perf_data).sort_values(by="Yıllık Değişim (%)", ascending=False)

# --- PANEL 1: EN'LER VE TABLO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏆 Performans Sıralaması")
    def renkli_hucre(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}; font-weight: bold'
    
    st.dataframe(df_perf.style.applymap(renkli_hucre, subset=['Yıllık Değişim (%)']), height=400)

with col2:
    st.subheader("🔍 Hisse Detay ve Teknik Analiz")
    secilen = st.selectbox("Analiz edilecek hisseyi seçin:", bist_list)
    
    hisse_df = pd.DataFrame(fiyat_verileri[f"{secilen}.IS"]).dropna()
    hisse_df.columns = ['Close']
    hisse_df = teknik_verileri_hesapla(hisse_df)
    
    # Teknik Analiz Grafiği (Plotly)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hisse_df.index, y=hisse_df['Close'], name='Fiyat'))
    fig.add_trace(go.Scatter(x=hisse_df.index, y=hisse_df['SMA20'], name='SMA 20', line=dict(dash='dash')))
    fig.update_layout(title=f"{secilen} Fiyat ve Hareketli Ortalama", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- PANEL 2: PORTFÖY VE KAR/ZARAR ---
st.divider()
st.header("💰 Portföy Takip")

p_col1, p_col2, p_col3 = st.columns(3)
with p_col1:
    p_hisse = st.selectbox("Portföydeki Hisse", bist_list, key="portfolio_select")
with p_col2:
    p_maliyet = st.number_input("Alış Fiyatı (Maliyet)", min_value=0.0)
with p_col3:
    p_adet = st.number_input("Adet", min_value=0)

if p_maliyet > 0 and p_adet > 0:
    guncel_f = df_perf[df_perf['Hisse'] == p_hisse]['Fiyat'].values[0]
    toplam_m = p_maliyet * p_adet
    toplam_d = guncel_f * p_adet
    kz_tl = toplam_d - toplam_m
    kz_yuzde = (kz_tl / toplam_m) * 100
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Güncel Değer", f"{toplam_d:,.2f} TL")
    m2.metric("Kar/Zarar (TL)", f"{kz_tl:,.2f} TL", delta=f"{kz_yuzde:.2f}%")
    
    # RSI Uyarısı
    rsi_son = hisse_df['RSI'].iloc[-1]
    if rsi_son > 70:
        st.warning(f"⚠️ {p_hisse} için RSI {rsi_son:.2f}: Aşırı alım bölgesinde, dikkatli olun!")
    elif rsi_son < 30:
        st.success(f"✅ {p_hisse} için RSI {rsi_son:.2f}: Aşırı satım (fırsat) bölgesinde olabilir.")
