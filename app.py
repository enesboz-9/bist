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
        data = yf.download(ticker, period="1y", interval="1d", progress=False)
        if data.empty:
            return None
        if isinstance(data.columns, pd.MultiIndex):
            return data['Close'][ticker]
        return data['Close']
    except:
        return None

# --- 4. ARAYÜZ BAŞLIĞI ---
st.title("📈 BIST Stratejik Analiz Paneli")
st.subheader("Geliştirici: Enes Boz")
st.divider()

# --- 5. PORTFÖY BÖLÜMÜ ---
st.header("💰 Portföy Yönetimi")
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1: h_input = st.text_input("Hisse Kodu Ekle (Örn: THYAO)", "THYAO").upper()
with c2: m_input = st.number_input("Maliyet", min_value=0.0, step=0.01)
with c3: a_input = st.number_input("Adet", min_value=0, step=1)
with c4:
    st.write("##")
    if st.button("Hisse Ekle"):
        new_row = pd.DataFrame([{'Hisse': h_input, 'Maliyet': m_input, 'Adet': a_input}])
        st.session_state.portfoy = pd.concat([st.session_state.portfoy, new_row], ignore_index=True)

toplam_m, toplam_d = 0.0, 0.0
if not st.session_state.portfoy.empty:
    for idx, row in st.session_state.portfoy.iterrows():
        fiyatlar = veri_cek_garanti(f"{row['Hisse']}.IS")
        if fiyatlar is not None:
            guncel_f = float(fiyatlar.iloc[-1])
            h_m, h_d = float(row['Maliyet'] * row['Adet']), float(guncel_f * row['Adet'])
            toplam_m += h_m
            toplam_d += h_d
            p_col = st.columns([1, 1, 1, 1])
            p_col[0].write(f"**{row['Hisse']}**")
            p_col[1].write(f"{row['Adet']} Adet")
            p_col[2].write(f"K/Z: {h_d - h_m:,.2f} TL")
            if p_col[3].button("Sil", key=f"btn_{idx}"):
                st.session_state.portfoy = st.session_state.portfoy.drop(idx).reset_index(drop=True)
                st.rerun()
    st.info(f"Toplam Portföy Değeri: {toplam_d:,.2f} TL | Toplam K/Z: {toplam_d - toplam_m:,.2f} TL")

# --- 6. BAĞIMSIZ KARŞILAŞTIRMA GRAFİĞİ ---
st.divider()
st.header("📊 Karşılaştırmalı Grafik Analizi")
st.write("Seçtiğiniz varlıkların son 1 yıllık performansını başlangıç noktasını (100) eşitleyerek kıyaslar.")

g_col1, g_col2 = st.columns([1, 2])
with g_col1:
    grafik_hisse = st.text_input("Kıyaslanacak Hisse Kodu (Örn: EREGL, ASELS)", "THYAO").upper()
    kiyas_secenek = st.multiselect("Yanına Ekle:", ["Altın (Gram)", "Gümüş (Gram)", "Enflasyon (%65)"])

# Grafik Çizimi
h_fiyat = veri_cek_garanti(f"{grafik_hisse}.IS")
if h_fiyat is not None:
    fig = go.Figure()
    # Normalize Et (İlk gün değerini 100 yap)
    h_norm = (h_fiyat / h_fiyat.iloc[0]) * 100
    fig.add_trace(go.Scatter(x=h_norm.index, y=h_norm, name=f"{grafik_hisse}", line=dict(width=3)))

    if "Altın (Gram)" in kiyas_secenek:
        # GAU=X genellikle Gram Altın/TL simülasyonu için kullanılır
        a_f = veri_cek_garanti("GAU=X")
        if a_f is not None:
            a_n = (a_f / a_f.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=a_n.index, y=a_n, name="Altın (Gram)", line=dict(color='gold')))

    if "Gümüş (Gram)" in kiyas_secenek:
        g_f = veri_cek_garanti("XAGUSD=X") # Gümüş Ons takibi üzerinden TL simülasyonu
        if g_f is not None:
            g_n = (g_f / g_f.iloc[0]) * 100
            fig.add_trace(go.Scatter(x=g_n.index, y=g_n, name="Gümüş", line=dict(color='silver')))

    if "Enflasyon (%65)" in kiyas_secenek:
        enf = [100 * (1 + 0.65 * (i/len(h_norm))) for i in range(len(h_norm))]
        fig.add_trace(go.Scatter(x=h_norm.index, y=enf, name="Yıllık Enflasyon Trendi", line=dict(dash='dash', color='red')))

    fig.update_layout(
        title=f"{grafik_hisse} vs Diğer Yatırım Araçları",
        xaxis_title="Tarih",
        yaxis_title="Getiri Endeksi (Başlangıç = 100)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"{grafik_hisse} için veri çekilemedi. Lütfen kodu doğru yazdığınızdan emin olun.")

# --- 7. ALT BİLGİ ---
st.divider()
st.caption("Veriler yfinance kütüphanesi üzerinden çekilmektedir ve 15 dakika gecikmeli olabilir.")
