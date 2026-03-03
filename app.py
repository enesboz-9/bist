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

# --- 3. VERİ ÇEKME FONKSİYONU ---
def veri_indir(tickers, period="1y"):
    try:
        data = yf.download(tickers, period=period, progress=False)
        if data.empty: return None
        return data['Close'] if 'Close' in data else data
    except: return None

# --- 4. ARAYÜZ ---
st.title("📈 BIST Stratejik Analiz Terminali")
st.markdown("### **Geliştirici:** Enes Boz")
st.divider()

# (Teknik Grafik Bölümü buraya gelecek - Önceki sürümle aynı)

# --- 5. KIYASLAMA BÖLÜMÜ ---
st.header("📊 Karşılaştırmalı Performans (Normalize 100)")
kiyas_secenek = st.multiselect("Grafiğe Ekle:", ["Altın (Ons)", "Gümüş (Ons)", "Enflasyon (%65)"], key="kiyas_v3")

t_kod = "THYAO" # Örnek (Üstteki selectbox'tan gelmeli)
v_kiyas = veri_indir([f"{t_kod}.IS", "GC=F", "SI=F"])

if v_kiyas is not None:
    fig_n = go.Figure()
    # Normalize çizim mantığı (Önceki sürümle aynı)
    # ... (Çizim kodları)
    st.plotly_chart(fig_n, use_container_width=True)

    # --- KULLANIM AMACI VE BİLGİLENDİRME ---
    with st.expander("ℹ️ Bu Grafiği Nasıl Yorumlamalıyım? (Kullanım Amacı)", expanded=True):
        st.info("""
        **Neden Tüm Varlıklar 100'den Başlıyor?**
        Farklı fiyatlardaki varlıkları (Örn: 300 TL'lik bir hisse ile 2500 dolarlık altın) kıyaslamak için **Normalizasyon** yöntemi kullanılır. 
        Tüm varlıklar seçilen dönemin başında **100 birim** kabul edilir. Böylece hangi yatırımın daha çok **yüzdesel getiri** sağladığı netleşir.

        **Göstergelerin Anlamı:**
        * **Hisse (Mavi):** Seçtiğiniz hissenin ana performansını temsil eder.
        * **Altın/Gümüş:** Hissenizin global emtialara karşı 'gerçek' bir değer kazanıp kazanmadığını gösterir.
        * **Enflasyon Trendi (Kırmızı Kesikli):** Paranızın alım gücünü koruyup korumadığını gösterir. Eğer hisse çizginiz enflasyon çizgisinin **altındaysa**, kağıt üzerinde kar etseniz bile reel olarak zarar ediyorsunuz demektir.
        
        **Stratejik Not:** Başarılı bir yatırım, uzun vadede hem altın hem de enflasyon eğrisinin üzerinde kalan yatırımdır.
        """)

# --- 6. PÖRTFÖY YÖNETİMİ ---
# ... (Pörtföy kodları)
