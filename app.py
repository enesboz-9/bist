import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Analiz - Enes Boz", layout="wide")

# --- 2. HİSSE İSİM-KOD EŞLEŞTİRME SÖZLÜĞÜ (BIST 100 Seçkisi) ---
# Kullanıcı tam ad girerse koda çevirmek için
HİSSE_SÖZLÜĞÜ = {
    "TÜRK HAVA YOLLARI": "THYAO", "THY": "THYAO",
    "ASELSAN": "ASELS",
    "EREĞLİ DEMİR ÇELİK": "EREGL", "EREGLI": "EREGL",
    "TÜPRAŞ": "TUPRS", "TUPRAS": "TUPRS",
    "KOÇ HOLDİNG": "KCHOL", "KOC HOLDING": "KCHOL",
    "SASA POLYESTER": "SASA",
    "ŞİŞECAM": "SISE", "SISECAM": "SISE",
    "GARANTİ BANKASI": "GARAN", "GARANTI": "GARAN",
    "AKBANK": "AKBNK",
    "BİM MAĞAZALAR": "BIMAS", "BIM": "BIMAS"
}

def kodu_bul(giris):
    giris_ust = giris.upper().strip()
    # Eğer direkt kod girildiyse onu döndür
    if len(giris_ust) <= 5 and not any(char.isdigit() for char in giris_ust):
        return giris_ust
    # Sözlükte tam ad araması yap
    for isim, kod in HİSSE_SÖZLÜĞÜ.items():
        if isim in giris_ust:
            return kod
    return giris_ust # Eşleşme yoksa olduğu gibi dene

# --- 3. VERİ FONKSİYONLARI ---
@st.cache_data(ttl=300)
def veri_cek_stabil(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", progress=False)
        if data is None or data.empty: return None
        if isinstance(data.columns, pd.MultiIndex):
            return data['Close'][ticker].dropna()
        return data['Close'].dropna()
    except:
        return None

# --- 4. ARAYÜZ ---
st.title("📈 BIST Stratejik Analiz Paneli")
st.subheader("Geliştirici: Enes Boz")
st.divider()

# --- 5. GRAFİK VE AKILLI ARAMA ---
st.header("📊 Karşılaştırmalı Grafik Analizi")

g_col1, g_col2 = st.columns([1, 2])
with g_col1:
    user_input = st.text_input("Hisse Adı veya Kodu Girin:", "Türk Hava Yolları")
    grafik_hisse = kodu_bul(user_input)
    kiyas_secenek = st.multiselect("Yanına Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"])

# Veriyi Çek
h_fiyat = veri_cek_stabil(f"{grafik_hisse}.IS")

if h_fiyat is not None and not h_fiyat.empty:
    fig = go.Figure()
    # Normalize Et (Başlangıç = 100)
    h_norm = (h_fiyat / h_fiyat.iloc[0]) * 100
    fig.add_trace(go.Scatter(x=h_norm.index, y=h_norm, name=f"{grafik_hisse}", line=dict(width=3)))

    # Altın/Gümüş Ekleme (Düzeltilmiş Semboller)
    if "Altın (Ons)" in kiyas_secenek:
        a_f = veri_cek_stabil("GC=F")
        if a_f is not None:
            fig.add_trace(go.Scatter(x=a_f.index, y=(a_f/a_f.iloc[0])*100, name="Altın", line=dict(color='gold')))
            
    if "Gümüş (Ons)" in kiyas_secenek:
        g_f = veri_cek_stabil("SI=F")
        if g_f is not None:
            fig.add_trace(go.Scatter(x=g_f.index, y=(g_f/g_f.iloc[0])*100, name="Gümüş", line=dict(color='silver')))

    if "Enflasyon (%65)" in kiyas_secenek:
        enf = [100 * (1 + 0.65 * (i/len(h_norm))) for i in range(len(h_norm))]
        fig.add_trace(go.Scatter(x=h_norm.index, y=enf, name="Enflasyon Trendi", line=dict(dash='dash', color='red')))

    fig.update_layout(template="plotly_white", height=600, yaxis_title="Getiri Endeksi (100)")
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"Analiz Edilen Hisse Kodu: {grafik_hisse}")
else:
    st.error("Hisse bulunamadı. Lütfen tam adı veya kodu kontrol edin.")
