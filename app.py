import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz - Enes Boz", layout="wide")

# --- 2. OTURUM YÖNETİMİ ---
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet'])

# --- 3. VERİ FONKSİYONLARI (Geliştirilmiş) ---
@st.cache_data(ttl=300)
def veri_cek_stabil(ticker):
    try:
        # Altın ve Gümüş için daha stabil olan '1mo' (aylık) yerine '1y' kullanıyoruz
        data = yf.download(ticker, period="1y", interval="1d", progress=False)
        if data is None or data.empty:
            return None
        
        # Multi-index yapısını kontrol et ve temizle
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close'][ticker]
        else:
            close_data = data['Close']
            
        return close_data.dropna()
    except Exception as e:
        return None

# --- 4. ARAYÜZ BAŞLIĞI ---
st.title("📈 BIST Stratejik Analiz Paneli")
st.subheader("Geliştirici: Enes Boz")
st.divider()

# --- 5. PORTFÖY YÖNETİMİ (Kısa Özet) ---
# (Önceki portföy kodlarını burada tutabilirsin, odak noktamız grafik sorunu)

# --- 6. BAĞIMSIZ KARŞILAŞTIRMA GRAFİĞİ (Düzeltilmiş) ---
st.header("📊 Karşılaştırmalı Grafik Analizi")

g_col1, g_col2 = st.columns([1, 2])
with g_col1:
    grafik_hisse = st.text_input("Kıyaslanacak Hisse Kodu (Örn: THYAO)", "THYAO").upper()
    kiyas_secenek = st.multiselect("Yanına Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"])

# Ana Hisse Verisi
h_fiyat = veri_cek_stabil(f"{grafik_hisse}.IS")

if h_fiyat is not None and not h_fiyat.empty:
    fig = go.Figure()
    # Normalize Et (Başlangıç noktasını 100 yap)
    h_norm = (h_fiyat / h_fiyat.iloc[0]) * 100
    fig.add_trace(go.Scatter(x=h_norm.index, y=h_norm, name=f"{grafik_hisse}", line=dict(width=3)))

    # ALTIN EKLEME
    if "Altın (Ons)" in kiyas_secenek:
        # GC=F (Altın Vadeli İşlemler) en stabil veridir
        altin_fiyat = veri_cek_stabil("GC=F")
        if altin_fiyat is not None and not altin_fiyat.empty:
            # Tarihleri hisse senedi tarihleriyle eşitlemek için 'reindex' kullanılabilir 
            # ancak basitlik için doğrudan normalize ediyoruz
            a_norm = (altin_fiyat / altin_fiyat.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=a_norm.index, y=a_norm, name="Altın (Ons)", line=dict(color='gold')))
        else:
            st.warning("Altın verisi şu an piyasadan çekilemiyor.")

    # GÜMÜŞ EKLEME
    if "Gümüş (Ons)" in kiyas_secenek:
        # SI=F (Gümüş Vadeli İşlemler)
        gumus_fiyat = veri_cek_stabil("SI=F")
        if gumus_fiyat is not None and not gumus_fiyat.empty:
            g_norm = (gumus_fiyat / gumus_fiyat.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=g_norm.index, y=g_norm, name="Gümüş (Ons)", line=dict(color='silver')))
        else:
            st.warning("Gümüş verisi şu an piyasadan çekilemiyor.")

    # ENFLASYON EKLEME
    if "Enflasyon (%65)" in kiyas_secenek:
        enf_cizgisi = [100 * (1 + 0.65 * (i/len(h_norm))) for i in range(len(h_norm))]
        fig.add_trace(go.Scatter(x=h_norm.index, y=enf_cizgisi, name="Enflasyon Trendi", line=dict(dash='dash', color='red')))

    fig.update_layout(
        template="plotly_white",
        height=600,
        xaxis_title="Tarih",
        yaxis_title="Getiri Endeksi (Başlangıç = 100)",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"{grafik_hisse} verisi çekilemedi. İnternet bağlantınızı veya hisse kodunu kontrol edin.")
