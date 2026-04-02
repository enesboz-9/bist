import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import json
import xml.etree.ElementTree as ET
import html as html_lib
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================
# SAYFA AYARLARI
# ============================================================
st.set_page_config(
    page_title="BIST Terminal Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# BLOOMBERG KARANLIK TEMA CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0f !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] {
    background-color: #0f0f1a !important;
    border-right: 1px solid #1e2a3a !important;
}
.terminal-header {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0f0f1a 100%);
    border-bottom: 1px solid #00d4ff33;
    padding: 16px 24px;
    margin: -20px -20px 20px -20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.terminal-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 2px;
    text-shadow: 0 0 20px #00d4ff66;
}
.terminal-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #4a6080;
    letter-spacing: 1px;
}
.metric-card {
    background: linear-gradient(145deg, #0f1520, #141e2e);
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 16px;
    margin: 4px 0;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #00d4ff44; }
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4a6080;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
}
.metric-positive { color: #00ff88 !important; }
.metric-negative { color: #ff4444 !important; }
.metric-neutral  { color: #00d4ff !important; }
.ai-box {
    background: linear-gradient(135deg, #0a1628 0%, #0f1f35 100%);
    border: 1px solid #00d4ff33;
    border-left: 3px solid #00d4ff;
    border-radius: 8px;
    padding: 20px;
    margin: 12px 0;
    font-size: 14px;
    line-height: 1.7;
    color: #b0c4de;
}
.ai-box-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #00d4ff;
    letter-spacing: 2px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.news-card {
    background: #0f1520;
    border: 1px solid #1e2a3a;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 6px 0;
    cursor: pointer;
    transition: all 0.2s;
}
.news-card:hover { border-color: #00d4ff44; background: #141e2e; }
.news-title { font-size: 13px; font-weight: 500; color: #c8d8e8; margin-bottom: 4px; }
.news-meta { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #4a6080; }
.news-positive { border-left: 3px solid #00ff88; }
.news-negative { border-left: 3px solid #ff4444; }
.news-neutral  { border-left: 3px solid #888; }
.alarm-active {
    background: #1a0f00;
    border: 1px solid #ff880033;
    border-left: 3px solid #ff8800;
    border-radius: 6px;
    padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #ffaa44;
    margin: 4px 0;
}
.alarm-triggered {
    background: #1a0000;
    border: 1px solid #ff444433;
    border-left: 3px solid #ff4444;
    border-radius: 6px;
    padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #ff6666;
    margin: 4px 0;
    animation: pulse 1s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
.ind-buy  { color: #00ff88; font-weight: 700; }
.ind-sell { color: #ff4444; font-weight: 700; }
.ind-hold { color: #ffaa00; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] {
    background-color: #0a0a0f !important;
    border-bottom: 1px solid #1e2a3a !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    color: #4a6080 !important;
}
.stTabs [aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
}
.stSelectbox > div > div, .stTextInput > div > div {
    background-color: #0f1520 !important;
    border-color: #1e2a3a !important;
    color: #e2e8f0 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #00d4ff22, #0057ff22) !important;
    border: 1px solid #00d4ff44 !important;
    color: #00d4ff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    border-radius: 4px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00d4ff44, #0057ff44) !important;
    border-color: #00d4ff88 !important;
    box-shadow: 0 0 12px #00d4ff22 !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 2px; }
hr { border-color: #1e2a3a !important; }
.section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #00d4ff;
    letter-spacing: 3px;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2a3a;
    padding-bottom: 8px;
    margin-bottom: 16px;
}
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-buy  { background: #00ff8822; color: #00ff88; border: 1px solid #00ff8844; }
.badge-sell { background: #ff444422; color: #ff4444; border: 1px solid #ff444444; }
.badge-hold { background: #ffaa0022; color: #ffaa00; border: 1px solid #ffaa0044; }
.screener-row {
    background: #0f1520;
    border: 1px solid #1e2a3a;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 3px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: border-color 0.2s;
}
.screener-row:hover { border-color: #00d4ff33; }
.fundamental-card {
    background: linear-gradient(145deg, #0f1520, #141e2e);
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 4px 0;
}
.fundamental-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #1a2535;
    font-size: 13px;
}
.fundamental-row:last-child { border-bottom: none; }
.frow-label { color: #4a6080; font-family: 'JetBrains Mono', monospace; font-size: 11px; }
.frow-value { color: #e2e8f0; font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; }
.frow-positive { color: #00ff88 !important; }
.frow-negative { color: #ff4444 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# BIST HİSSE LİSTESİ
# ============================================================
BIST_STATIK = {
    "AEFES":"Anadolu Efes","AGHOL":"Anadolu Grubu Holding","AKBNK":"Akbank","AKCNS":"Akçansa",
    "AKSA":"Aksa","AKSEN":"Aksa Enerji","ALARK":"Alarko Holding","ALBRK":"Albaraka Türk",
    "ARCLK":"Arçelik","ASELS":"Aselsan","ASTOR":"Astor Enerji","AYDEM":"Aydem Enerji",
    "BIMAS":"Bim Mağazalar","BRSAN":"Borusan Boru","CCOLA":"Coca-Cola İçecek","CIMSA":"Çimsa",
    "DOAS":"Doğuş Otomotiv","DOHOL":"Doğan Holding","EKGYO":"Emlak Konut GYO",
    "ENJSA":"Enerjisa Enerji","ENKAI":"Enka İnşaat","EREGL":"Ereğli Demir Çelik",
    "FROTO":"Ford Otosan","GARAN":"Garanti Bankası","GUBRF":"Gübre Fabrikaları",
    "GWIND":"Galata Wind","HALKB":"Halkbank","HEKTS":"Hektaş","ISCTR":"İş Bankası (C)",
    "ISDMR":"İskenderun Demir Çelik","ISGYO":"İş GYO","ISMEN":"İş Yatırım",
    "KCHOL":"Koç Holding","KORDS":"Kordsa","KOZAA":"Koza Madencilik","KOZAL":"Koza Altın",
    "KRDMD":"Kardemir (D)","MAVI":"Mavi Giyim","MGROS":"Migros","OTKAR":"Otokar",
    "OYAKC":"Oyak Çimento","PENTA":"Penta Teknoloji","PETKM":"Petkim","PGSUS":"Pegasus",
    "SAHOL":"Sabancı Holding","SASA":"Sasa Polyester","SISE":"Şişecam","SKBNK":"Şekerbank",
    "SOKM":"Şok Marketler","TAVHL":"Tav Havalimanları","TCELL":"Turkcell",
    "THYAO":"Türk Hava Yolları","TKFEN":"Tekfen Holding","TOASO":"Tofaş Oto.",
    "TSKB":"Tskb","TTKOM":"Türk Telekom","TTRAK":"Türk Traktör","TUPRS":"Tüpraş",
    "TURSG":"Türkiye Sigorta","ULKER":"Ülker Bisküvi","VAKBN":"Vakıfbank",
    "VESBE":"Vestel Beyaz Eşya","VESTL":"Vestel","YKBNK":"Yapı Kredi Bankası",
    "ZOREN":"Zorlu Enerji","ANACM":"Anadolu Cam","AYEN":"Ayen Enerji","BIZIM":"Bizim Toptan",
    "BTCIM":"Batıçim","BURCE":"Burçelik","CLEBI":"Çelebi Hava Servisi","DAGI":"Dagi Giyim",
    "DEVA":"Deva Holding","ECILC":"Eczacıbaşı İlaç","ECZYT":"Eczacıbaşı Yatırım",
    "EGPRO":"Ege Profil","EGSER":"Ege Seramik","ERBOS":"Erbosan","FENER":"Fenerbahçe",
    "GSRAY":"Galatasaray","GOODY":"Goodyear","GSDHO":"GSD Holding","IHEVA":"İhlas Ev Aletleri",
    "INDES":"İndeks Bilgisayar","KAREL":"Karel Elektronik","KARSN":"Karsan",
    "KATMR":"Katmerciler","KONYA":"Konya Çimento","KRDMA":"Kardemir A","KRDMB":"Kardemir B",
    "LOGO":"Logo Yazılım","MARIM":"Maritim Elektrik","MERKO":"Merko Gıda","METRO":"Metro Holding",
    "NETAS":"Netaş Telekomünikasyon","NUHCM":"Nuh Çimento","OYLUM":"Oylum Tarım",
    "PARSN":"Parsan","PENGD":"Penguen Gıda","PETUN":"Pınar Et ve Un","PINSU":"Pınar Su",
    "POLHO":"Polisan Holding","RTALB":"Rota Alüminyum","ROYAL":"Royal Halı",
    "SELEC":"Selçuk Ecza","SELGD":"Selçuk Gıda","SNGYO":"Sinpaş GYO","SODSN":"Soda Sanayii",
    "TBORG":"Türk Tuborg","TRGYO":"Torunlar GYO","TSPOR":"Trabzonspor","TUKAS":"Tukaş",
    "ULUSE":"Ulusoy Elektrik","ULUUN":"Ulusoy Un","USAK":"Uşak Seramik","VAKGY":"Vakıf GYO",
    "VAKKO":"Vakko Tekstil","YUNSA":"Yünsa","ZRGYO":"Ziraat GYO",
}

@st.cache_data(ttl=86400)
def bist_hisse_listesi_getir():
    try:
        url = "https://tr.wikipedia.org/wiki/BIST_100_Endeksi"
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        tables = pd.read_html(resp.text)
        for tbl in tables:
            cols = [str(c).lower() for c in tbl.columns]
            if any("kod" in c or "sembol" in c or "ticker" in c for c in cols):
                kod_col = next(c for c in tbl.columns if any(k in str(c).lower() for k in ["kod","sembol","ticker"]))
                ad_col  = next((c for c in tbl.columns if any(k in str(c).lower() for k in ["şirket","şirket adı","ad","unvan"])), None)
                kodlar = tbl[kod_col].dropna().astype(str).str.strip().str.upper().tolist()
                adlar  = tbl[ad_col].dropna().astype(str).tolist() if ad_col else kodlar
                sonuc  = {}
                for k, a in zip(kodlar, adlar):
                    if 2 <= len(k) <= 6 and k.isalpha():
                        sonuc[k] = a
                if len(sonuc) > 20:
                    merged = {**BIST_STATIK, **sonuc}
                    return dict(sorted(merged.items()))
    except Exception:
        pass
    return dict(sorted(BIST_STATIK.items()))

bist_100_full = bist_hisse_listesi_getir()
hisse_listesi = [f"{kod} - {ad}" for kod, ad in bist_100_full.items()]

# ============================================================
# SESSION STATE
# ============================================================
if 'portfoy' not in st.session_state:
    st.session_state.portfoy = pd.DataFrame(columns=['Hisse', 'Maliyet', 'Adet', 'Hedef', 'Stop'])
if 'alarmlar' not in st.session_state:
    st.session_state.alarmlar = []
if 'ai_cache' not in st.session_state:
    st.session_state.ai_cache = {}
if 'mail_gonderildi' not in st.session_state:
    st.session_state.mail_gonderildi = {}
if 'screener_sonuc' not in st.session_state:
    st.session_state.screener_sonuc = None

# ============================================================
# MAİL GÖNDERME
# ============================================================
def alarm_maili_gonder(alici_mail, hisse, tur, alarm_fiyat, gercek_fiyat):
    try:
        gonderen = st.secrets["GMAIL_USER"]
        sifre = st.secrets["GMAIL_APP_PASSWORD"]
    except Exception:
        return False, "Secrets bulunamadı"
    yon_emoji = "🚀" if tur == "Üstüne Çıkarsa" else "📉"
    konu = f"{yon_emoji} BIST Alarm: {hisse} fiyat hedefine ulaştı!"
    html_body = f"""<html><body style="font-family:Arial,sans-serif;background:#0a0a0f;color:#e2e8f0;padding:24px">
      <div style="max-width:480px;margin:auto;background:#0f1520;border:1px solid #1e2a3a;border-radius:10px;padding:28px">
        <div style="font-size:22px;font-weight:700;color:#00d4ff;margin-bottom:4px">◈ BIST Terminal Pro</div>
        <div style="font-size:28px;font-weight:700;color:{'#00ff88' if tur == 'Üstüne Çıkarsa' else '#ff4444'}">{yon_emoji} {hisse}</div>
        <p>Alarm Fiyatı: {alarm_fiyat:.2f} TL | Gerçekleşen: {gercek_fiyat:.2f} TL</p>
        <p style="font-size:11px;color:#2a3a4a">Bu mail BIST Terminal Pro tarafından otomatik gönderilmiştir. Yatırım tavsiyesi değildir.</p>
      </div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = konu
        msg["From"] = gonderen
        msg["To"] = alici_mail
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gonderen, sifre)
            server.sendmail(gonderen, alici_mail, msg.as_string())
        return True, "Mail gönderildi"
    except Exception as e:
        return False, str(e)

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================
@st.cache_data(ttl=300)
def veri_indir(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        return data if not data.empty else None
    except:
        return None

def get_seri(data_raw, ticker=None):
    if data_raw is None:
        return None
    if isinstance(data_raw.columns, pd.MultiIndex):
        close = data_raw['Close']
        if isinstance(close, pd.DataFrame):
            return close.iloc[:, 0].dropna()
        return close.dropna()
    return data_raw['Close'].dropna()

# ============================================================
# TEKNİK İNDİKATÖRLER (Mevcut + Yeni)
# ============================================================
def hesapla_rsi(seri, periyot=14):
    delta = seri.diff()
    gain = delta.clip(lower=0).rolling(periyot).mean()
    loss = (-delta.clip(upper=0)).rolling(periyot).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def hesapla_macd(seri, h=12, y=26, s=9):
    ema_h = seri.ewm(span=h, adjust=False).mean()
    ema_y = seri.ewm(span=y, adjust=False).mean()
    macd = ema_h - ema_y
    signal = macd.ewm(span=s, adjust=False).mean()
    return macd, signal, macd - signal

def hesapla_bollinger(seri, periyot=20, std=2):
    ort = seri.rolling(periyot).mean()
    standart = seri.rolling(periyot).std()
    return ort + std * standart, ort, ort - std * standart

def hesapla_stochastic(data, k_periyot=14, d_periyot=3):
    low_min = data['Low'].rolling(k_periyot).min()
    high_max = data['High'].rolling(k_periyot).max()
    k = 100 * (data['Close'] - low_min) / (high_max - low_min)
    return k, k.rolling(d_periyot).mean()

def hesapla_atr(data, periyot=14):
    h = data['High']; l = data['Low']; c = data['Close'].shift(1)
    tr = pd.concat([h - l, (h - c).abs(), (l - c).abs()], axis=1).max(axis=1)
    return tr.rolling(periyot).mean()

def hesapla_cci(data, periyot=20):
    tp = (data['High'] + data['Low'] + data['Close']) / 3
    ma = tp.rolling(periyot).mean()
    md = tp.rolling(periyot).apply(lambda x: np.mean(np.abs(x - x.mean())))
    return (tp - ma) / (0.015 * md)

def hesapla_williams_r(data, periyot=14):
    hh = data['High'].rolling(periyot).max()
    ll = data['Low'].rolling(periyot).min()
    return -100 * (hh - data['Close']) / (hh - ll)

def hesapla_obv(data):
    obv = [0]
    for i in range(1, len(data)):
        if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
            obv.append(obv[-1] + data['Volume'].iloc[i])
        elif data['Close'].iloc[i] < data['Close'].iloc[i-1]:
            obv.append(obv[-1] - data['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=data.index)

def hesapla_ichimoku(data):
    h9 = data['High'].rolling(9).max(); l9 = data['Low'].rolling(9).min()
    h26 = data['High'].rolling(26).max(); l26 = data['Low'].rolling(26).min()
    h52 = data['High'].rolling(52).max(); l52 = data['Low'].rolling(52).min()
    tenkan = (h9 + l9) / 2
    kijun = (h26 + l26) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((h52 + l52) / 2).shift(26)
    chikou = data['Close'].shift(-26)
    return tenkan, kijun, senkou_a, senkou_b, chikou

def hesapla_fibonacci(seri, period=100):
    son = seri.iloc[-period:]
    yuksek = son.max(); dusuk = son.min()
    fark = yuksek - dusuk
    seviyeler = {
        "0.0% (Yüksek)": yuksek,
        "23.6%": yuksek - 0.236 * fark,
        "38.2%": yuksek - 0.382 * fark,
        "50.0%": yuksek - 0.500 * fark,
        "61.8%": yuksek - 0.618 * fark,
        "78.6%": yuksek - 0.786 * fark,
        "100% (Düşük)": dusuk,
    }
    return seviyeler

def hesapla_pivot(data):
    yuksek = float(data['High'].iloc[-1])
    dusuk  = float(data['Low'].iloc[-1])
    kapanis = float(data['Close'].iloc[-1])
    pivot = (yuksek + dusuk + kapanis) / 3
    return {
        "R3": pivot + 2 * (yuksek - dusuk),
        "R2": pivot + (yuksek - dusuk),
        "R1": 2 * pivot - dusuk,
        "Pivot": pivot,
        "S1": 2 * pivot - yuksek,
        "S2": pivot - (yuksek - dusuk),
        "S3": pivot - 2 * (yuksek - dusuk),
    }

def teknik_sinyal_hesapla(seri, data):
    sinyaller = {}; skor = 0
    try:
        rsi = hesapla_rsi(seri).iloc[-1]
        sinyaller['RSI'] = {'deger': f"{rsi:.1f}", 'sinyal': 'AL' if rsi < 30 else ('SAT' if rsi > 70 else 'BEKLE'), 'renk': '#00ff88' if rsi < 30 else ('#ff4444' if rsi > 70 else '#ffaa00')}
        skor += 1 if rsi < 30 else (-1 if rsi > 70 else 0)
    except: pass
    try:
        macd, signal, _ = hesapla_macd(seri)
        ms, ss, mp, sp = macd.iloc[-1], signal.iloc[-1], macd.iloc[-2], signal.iloc[-2]
        kesisim = (ms > ss) and (mp <= sp)
        sinyaller['MACD'] = {'deger': f"{ms:.3f}", 'sinyal': 'AL' if kesisim else ('SAT' if ms < ss else 'BEKLE'), 'renk': '#00ff88' if kesisim else ('#ff4444' if ms < ss else '#ffaa00')}
        skor += 1 if ms > ss else -1
    except: pass
    try:
        ust, ort, alt = hesapla_bollinger(seri)
        fiyat = seri.iloc[-1]
        bb_s = 'AL' if fiyat < alt.iloc[-1] else ('SAT' if fiyat > ust.iloc[-1] else 'BEKLE')
        sinyaller['Bollinger'] = {'deger': f"Ort:{ort.iloc[-1]:.2f}", 'sinyal': bb_s, 'renk': '#00ff88' if bb_s == 'AL' else ('#ff4444' if bb_s == 'SAT' else '#ffaa00')}
        skor += 1 if bb_s == 'AL' else (-1 if bb_s == 'SAT' else 0)
    except: pass
    try:
        ma20 = seri.rolling(20).mean().iloc[-1]; ma50 = seri.rolling(50).mean().iloc[-1]
        fiyat = seri.iloc[-1]
        ma_s = 'AL' if fiyat > ma20 > ma50 else ('SAT' if fiyat < ma20 < ma50 else 'BEKLE')
        sinyaller['MA Trendi'] = {'deger': f"MA50:{ma50:.2f}", 'sinyal': ma_s, 'renk': '#00ff88' if ma_s == 'AL' else ('#ff4444' if ma_s == 'SAT' else '#ffaa00')}
        skor += 1 if fiyat > ma50 else -1
    except: pass
    try:
        if data is not None:
            k, d = hesapla_stochastic(data)
            ks, ds = k.iloc[-1], d.iloc[-1]
            sinyaller['Stochastic'] = {'deger': f"K:{ks:.1f}", 'sinyal': 'AL' if ks < 20 else ('SAT' if ks > 80 else 'BEKLE'), 'renk': '#00ff88' if ks < 20 else ('#ff4444' if ks > 80 else '#ffaa00')}
            skor += 1 if ks < 20 else (-1 if ks > 80 else 0)
    except: pass
    try:
        if data is not None:
            cci = hesapla_cci(data).iloc[-1]
            sinyaller['CCI'] = {'deger': f"{cci:.1f}", 'sinyal': 'AL' if cci < -100 else ('SAT' if cci > 100 else 'BEKLE'), 'renk': '#00ff88' if cci < -100 else ('#ff4444' if cci > 100 else '#ffaa00')}
            skor += 1 if cci < -100 else (-1 if cci > 100 else 0)
    except: pass
    try:
        if data is not None:
            wr = hesapla_williams_r(data).iloc[-1]
            sinyaller['Williams %R'] = {'deger': f"{wr:.1f}", 'sinyal': 'AL' if wr < -80 else ('SAT' if wr > -20 else 'BEKLE'), 'renk': '#00ff88' if wr < -80 else ('#ff4444' if wr > -20 else '#ffaa00')}
            skor += 1 if wr < -80 else (-1 if wr > -20 else 0)
    except: pass
    genel = 'GÜÇLÜ AL' if skor >= 4 else ('AL' if skor >= 2 else ('GÜÇLÜ SAT' if skor <= -4 else ('SAT' if skor <= -2 else 'BEKLE')))
    return sinyaller, skor, genel

# ============================================================
# TEMEL ANALİZ VERİLERİ
# ============================================================
@st.cache_data(ttl=3600)
def temel_veri_cek(kod):
    try:
        ticker = yf.Ticker(f"{kod}.IS")
        info = ticker.info
        return info
    except:
        return {}

def format_buyuk_sayi(sayi):
    if sayi is None or sayi == 0:
        return "—"
    try:
        s = float(sayi)
        if abs(s) >= 1e12: return f"{s/1e12:.2f}T"
        if abs(s) >= 1e9:  return f"{s/1e9:.2f}B"
        if abs(s) >= 1e6:  return f"{s/1e6:.2f}M"
        return f"{s:,.0f}"
    except:
        return "—"

def format_oran(deger, carpan=1, sonek=""):
    if deger is None:
        return "—"
    try:
        return f"{float(deger)*carpan:.2f}{sonek}"
    except:
        return "—"

# ============================================================
# SCREENER
# ============================================================
@st.cache_data(ttl=600)
def screener_hisse_tara(hisseler_tuple, min_rsi, max_rsi, sinyal_filtre, max_hisse=50):
    sonuclar = []
    hisseler = list(hisseler_tuple)[:max_hisse]
    for kod in hisseler:
        try:
            data = yf.download(f"{kod}.IS", period="3mo", interval="1d", auto_adjust=True, progress=False)
            if data is None or data.empty or len(data) < 30:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                seri = data['Close'].iloc[:, 0].dropna()
            else:
                seri = data['Close'].dropna()
            if len(seri) < 20:
                continue
            fiyat = float(seri.iloc[-1])
            fiyat_prev = float(seri.iloc[-2])
            degisim = ((fiyat - fiyat_prev) / fiyat_prev) * 100
            rsi_val = float(hesapla_rsi(seri).iloc[-1])
            if np.isnan(rsi_val):
                continue
            _, _, genel = teknik_sinyal_hesapla(seri, data)
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    hacim = float(data['Volume'].iloc[:, 0].mean())
                else:
                    hacim = float(data['Volume'].mean())
            except:
                hacim = 0
            # Filtreler
            if not (min_rsi <= rsi_val <= max_rsi):
                continue
            if sinyal_filtre != "Tümü":
                if sinyal_filtre == "AL Sinyalleri" and "AL" not in genel:
                    continue
                if sinyal_filtre == "SAT Sinyalleri" and "SAT" not in genel:
                    continue
                if sinyal_filtre == "Aşırı Satım (RSI<30)" and rsi_val >= 30:
                    continue
                if sinyal_filtre == "Aşırı Alım (RSI>70)" and rsi_val <= 70:
                    continue
            ad = bist_100_full.get(kod, kod)
            sonuclar.append({
                'Kod': kod, 'Şirket': ad[:25], 'Fiyat': fiyat,
                'Değişim%': degisim, 'RSI': rsi_val, 'Sinyal': genel, 'Hacim(M)': hacim / 1e6
            })
        except Exception:
            continue
    return sorted(sonuclar, key=lambda x: x['RSI'])

# ============================================================
# AI ANALİZ
# ============================================================
def ai_analiz_yap(kod, ad, fiyat, degisim, rsi, genel_sinyal, hacim_ort, seri):
    cache_key = f"{kod}_{datetime.now().strftime('%Y%m%d%H')}"
    if cache_key in st.session_state.ai_cache:
        return st.session_state.ai_cache[cache_key]
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
    except:
        return "⚠ Groq API key bulunamadı."
    try:
        son_7_gun = seri.iloc[-7:].pct_change().dropna() * 100
        trend_ozet = f"{son_7_gun.mean():.2f}% ort günlük değişim"
        yuksek_52h = seri.rolling(252).max().iloc[-1]
        dusuk_52h = seri.rolling(252).min().iloc[-1]
        prompt = f"""Sen deneyimli bir BIST analistisin. {kod} ({ad}) için analiz yap.
Fiyat: {fiyat:.2f} TL | Değişim: {degisim:+.2f}% | RSI: {rsi:.1f} | Sinyal: {genel_sinyal}
Son 7 Gün: {trend_ozet} | 52H Yüksek: {yuksek_52h:.2f} | 52H Düşük: {dusuk_52h:.2f}
Şu başlıklar: 1.Teknik Görünüm 2.Kısa Vadeli Beklenti 3.Risk Faktörleri 4.Sonuç (max 150 kelime, Türkçe)"""
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {groq_key}"},
            json={"model": "llama-3.3-70b-versatile", "max_tokens": 1024, "temperature": 0.7,
                  "messages": [{"role": "system", "content": "Profesyonel Türk borsa analisti."},
                                {"role": "user", "content": prompt}]}, timeout=30)
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"]
            st.session_state.ai_cache[cache_key] = text
            return text
        return f"⚠ Groq hatası: {response.status_code}"
    except Exception as e:
        return f"⚠ Bağlantı hatası: {str(e)}"

# ============================================================
# RSS HABERLER
# ============================================================
RSS_KAYNAKLAR = [
    {"ad": "Investing.com TR", "url": "https://tr.investing.com/rss/news.rss"},
    {"ad": "Borsa Gündem", "url": "https://www.borsagundem.com/feed"},
    {"ad": "Para Analiz", "url": "https://www.paraanaliz.com/feed/"},
    {"ad": "Bloomberg HT", "url": "https://www.bloomberght.com/rss"},
]

@st.cache_data(ttl=600)
def rss_haberleri_cek(hisse_kodu):
    tum_haberler = []
    pozitif_kw = ['artış','yüksel','rekor','büyüme','kâr','kazanç','güçlü','olumlu','yatırım']
    negatif_kw = ['düşüş','kayıp','zarar','risk','endişe','kriz','çöküş','olumsuz','baskı']
    headers = {"User-Agent": "Mozilla/5.0"}
    for kaynak in RSS_KAYNAKLAR:
        try:
            resp = requests.get(kaynak["url"], headers=headers, timeout=8)
            if resp.status_code != 200: continue
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item"):
                baslik = item.findtext("title", "").strip()
                link = item.findtext("link", "#").strip()
                tarih = item.findtext("pubDate", "").strip()
                ozet = re.sub(r'<[^>]+>', '', html_lib.unescape(item.findtext("description", "")))[:200]
                arama = baslik.lower() + ozet.lower()
                if not any(k in arama for k in [hisse_kodu.lower(), "bist", "borsa", "hisse", "endeks", "piyasa"]):
                    continue
                try:
                    from email.utils import parsedate_to_datetime
                    tarih_str = parsedate_to_datetime(tarih).strftime("%d.%m.%Y %H:%M")
                except:
                    tarih_str = tarih[:16]
                bl = baslik.lower()
                sentiment = "news-positive" if any(k in bl for k in pozitif_kw) else ("news-negative" if any(k in bl for k in negatif_kw) else "news-neutral")
                tum_haberler.append({"baslik": baslik, "link": link, "kaynak": kaynak["ad"], "tarih": tarih_str, "ozet": ozet, "sentiment": sentiment})
        except: continue
    goruldu = set(); benzersiz = []
    for h in tum_haberler:
        k = h["baslik"][:60].lower()
        if k not in goruldu:
            goruldu.add(k); benzersiz.append(h)
    return benzersiz[:20]

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="terminal-header">
    <div>
        <div class="terminal-logo">◈ BIST TERMINAL PRO</div>
        <div class="terminal-subtitle">GELİŞTİRİCİ: ENES BOZ • {datetime.now().strftime('%d.%m.%Y %H:%M')} IST</div>
    </div>
    <div style="text-align:right">
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#4a6080">BIST 100 • GERÇEK ZAMANLI</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00d4ff">● CANLI</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="section-title">⚙ KONTROL PANELİ</div>', unsafe_allow_html=True)
    ana_secim = st.selectbox("Hisse Seç:", hisse_listesi,
                             index=next((i for i, x in enumerate(hisse_listesi) if "GARAN" in x), 35))
    t_kod = ana_secim.split(" - ")[0]
    t_ad  = ana_secim.split(" - ")[1]
    t_sure_etiket = st.radio("Periyot:", ["1 Ay", "3 Ay", "1 Yıl", "3 Yıl", "5 Yıl"], index=2)
    t_periyot = {"1 Ay": "1mo", "3 Ay": "3mo", "1 Yıl": "1y", "3 Yıl": "3y", "5 Yıl": "5y"}
    t_aralik  = {"1 Ay": "1h",  "3 Ay": "1d",  "1 Yıl": "1d", "3 Yıl": "1wk", "5 Yıl": "1wk"}
    secilen_periyot = t_periyot[t_sure_etiket]
    secilen_aralik  = t_aralik[t_sure_etiket]
    st.markdown("---")
    st.markdown('<div class="section-title">🔔 FİYAT ALARMLARI</div>', unsafe_allow_html=True)
    alarm_hisse = st.selectbox("Hisse:", hisse_listesi, key="alarm_h")
    alarm_tur   = st.radio("Tür:", ["Üstüne Çıkarsa", "Altına Düşerse"], horizontal=True)
    alarm_fiyat = st.number_input("Fiyat (TL):", min_value=0.01, format="%.2f", key="alarm_f")
    alarm_mail  = st.text_input("📧 E-posta (opsiyonel):", placeholder="ornek@gmail.com", key="alarm_mail")
    if st.button("⚡ Alarm Ekle", use_container_width=True):
        alarm_kod = alarm_hisse.split(" - ")[0]
        st.session_state.alarmlar.append({'hisse': alarm_kod, 'tur': alarm_tur, 'fiyat': alarm_fiyat,
                                           'mail': alarm_mail.strip(), 'aktif': True, 'eklenme': datetime.now().strftime('%d.%m %H:%M')})
        st.success("✅ Alarm eklendi!")
    if st.session_state.alarmlar:
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;margin:8px 0 4px">AKTİF ALARMLAR</div>', unsafe_allow_html=True)
        silinecek = []
        for i, alarm in enumerate(st.session_state.alarmlar):
            try:
                d = yf.download(f"{alarm['hisse']}.IS", period="1d", progress=False)
                if d.empty: continue
                g_fiyat = float(d['Close'].iloc[-1].iloc[0]) if isinstance(d.columns, pd.MultiIndex) else float(d['Close'].iloc[-1])
                tetiklendi = (alarm['tur'] == "Üstüne Çıkarsa" and g_fiyat >= alarm['fiyat']) or (alarm['tur'] == "Altına Düşerse" and g_fiyat <= alarm['fiyat'])
                if tetiklendi and alarm.get('mail'):
                    mail_key = f"{alarm['hisse']}_{alarm['fiyat']}_{alarm['tur']}"
                    son_g = st.session_state.mail_gonderildi.get(mail_key)
                    if son_g is None or (datetime.now() - son_g).total_seconds() > 3600:
                        basari, mesaj = alarm_maili_gonder(alarm['mail'], alarm['hisse'], alarm['tur'], alarm['fiyat'], g_fiyat)
                        if basari:
                            st.session_state.mail_gonderildi[mail_key] = datetime.now()
                if tetiklendi:
                    st.markdown(f'<div class="alarm-triggered">🚨 <b>{alarm["hisse"]}</b> → {g_fiyat:.2f} TL<br><span style="font-size:10px">{alarm["tur"]} {alarm["fiyat"]:.2f} TL</span></div>', unsafe_allow_html=True)
                else:
                    pct = abs(((alarm['fiyat'] - g_fiyat) / g_fiyat) * 100)
                    yon = "▲" if alarm['tur'] == "Üstüne Çıkarsa" else "▼"
                    st.markdown(f'<div class="alarm-active">🔔 <b>{alarm["hisse"]}</b> {yon} {alarm["fiyat"]:.2f} TL<br><span style="font-size:10px">Şu an: {g_fiyat:.2f} TL • Fark: %{pct:.1f}</span></div>', unsafe_allow_html=True)
            except: pass
            if st.button("✕ Sil", key=f"al_del_{i}", use_container_width=True):
                silinecek.append(i)
        for i in reversed(silinecek):
            st.session_state.alarmlar.pop(i)
        if silinecek: st.rerun()
    st.markdown("---")
    st.markdown('<div class="section-title">⚖ KARŞILAŞTIRMA</div>', unsafe_allow_html=True)
    kiyas_secenek = st.multiselect("Ekle:", ["Altın (TL)", "Gümüş (TL)", "Dolar/TL", "Enflasyon"])

# ============================================================
# ANA PANEL — 7 SEKME
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 TEKNİK ANALİZ",
    "📐 İLERİ İNDİKATÖRLER",
    "🏢 TEMEL ANALİZ",
    "🔍 SCREENER",
    "🤖 AI RAPORU",
    "📰 HABERLER",
    "💼 PORTFÖY"
])

# ============================================================
# TAB 1: TEKNİK ANALİZ
# ============================================================
with tab1:
    data_raw = veri_indir(f"{t_kod}.IS", secilen_periyot, secilen_aralik)
    if data_raw is not None and not data_raw.empty:
        seri = get_seri(data_raw)
        fiyat_son  = float(seri.iloc[-1])
        fiyat_prev = float(seri.iloc[-2]) if len(seri) > 1 else fiyat_son
        degisim_yuzde = ((fiyat_son - fiyat_prev) / fiyat_prev) * 100
        try:
            hacim = (data_raw['Volume'].iloc[:, 0] if isinstance(data_raw.columns, pd.MultiIndex) else data_raw['Volume']).mean()
        except: hacim = 0
        sinyaller, skor, genel_sinyal = teknik_sinyal_hesapla(seri, data_raw)
        rsi_val = hesapla_rsi(seri).iloc[-1] if len(seri) > 14 else 50.0

        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        with mc1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">SON FİYAT</div><div class="metric-value">{fiyat_son:.2f} <span style="font-size:12px;color:#4a6080">TL</span></div></div>', unsafe_allow_html=True)
        with mc2:
            renk = "metric-positive" if degisim_yuzde >= 0 else "metric-negative"
            yon = "▲" if degisim_yuzde >= 0 else "▼"
            st.markdown(f'<div class="metric-card"><div class="metric-label">GÜNLÜK DEĞİŞİM</div><div class="metric-value {renk}">{yon} {abs(degisim_yuzde):.2f}%</div></div>', unsafe_allow_html=True)
        with mc3:
            rsi_cls = "metric-positive" if rsi_val < 30 else ("metric-negative" if rsi_val > 70 else "metric-neutral")
            st.markdown(f'<div class="metric-card"><div class="metric-label">RSI (14)</div><div class="metric-value {rsi_cls}">{rsi_val:.1f}</div></div>', unsafe_allow_html=True)
        with mc4:
            sinyal_cls = "metric-positive" if "AL" in genel_sinyal else ("metric-negative" if "SAT" in genel_sinyal else "metric-neutral")
            st.markdown(f'<div class="metric-card"><div class="metric-label">TEKNİK SİNYAL</div><div class="metric-value {sinyal_cls}" style="font-size:16px">{genel_sinyal}</div></div>', unsafe_allow_html=True)
        with mc5:
            st.markdown(f'<div class="metric-card"><div class="metric-label">ORT. HACİM</div><div class="metric-value metric-neutral">{hacim/1e6:.1f}M</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        ic1, ic2 = st.columns([3, 1])
        with ic2:
            goster_bb  = st.checkbox("Bollinger Bantları", value=True)
            goster_ma  = st.checkbox("Hareketli Ortalamalar", value=True)
            goster_vol = st.checkbox("Hacim", value=True)
            goster_rsi_chart  = st.checkbox("RSI Grafiği", value=True)
            goster_macd_chart = st.checkbox("MACD Grafiği", value=False)

        with ic1:
            rows = 1; row_heights = [0.6]
            if goster_vol:        rows += 1; row_heights.append(0.15)
            if goster_rsi_chart:  rows += 1; row_heights.append(0.125)
            if goster_macd_chart: rows += 1; row_heights.append(0.125)
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                                row_heights=row_heights, specs=[[{"secondary_y": False}]] * rows)
            cur_row = 1
            if isinstance(data_raw.columns, pd.MultiIndex):
                high_s = data_raw['High'].iloc[:, 0]; low_s = data_raw['Low'].iloc[:, 0]; open_s = data_raw['Open'].iloc[:, 0]
            else:
                high_s = data_raw['High']; low_s = data_raw['Low']; open_s = data_raw['Open']
            fig.add_trace(go.Candlestick(x=seri.index, open=open_s, high=high_s, low=low_s, close=seri,
                name=t_kod, increasing=dict(line=dict(color='#00ff88', width=1)), decreasing=dict(line=dict(color='#ff4444', width=1))), row=cur_row, col=1)
            if goster_bb:
                ust, ort_bb, alt = hesapla_bollinger(seri)
                fig.add_trace(go.Scatter(x=seri.index, y=ust, line=dict(color='#4444ff', width=1, dash='dot'), showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=alt, line=dict(color='#4444ff', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(68,68,255,0.05)', showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=ort_bb, line=dict(color='#8888ff', width=1), showlegend=False), row=cur_row, col=1)
            if goster_ma:
                for ma_p, renk_ma in [(20,'#ffaa00'),(50,'#ff6688'),(200,'#88aaff')]:
                    if len(seri) >= ma_p:
                        fig.add_trace(go.Scatter(x=seri.index, y=seri.rolling(ma_p).mean(), line=dict(color=renk_ma, width=1.5), name=f'MA{ma_p}'), row=cur_row, col=1)
            if goster_vol:
                cur_row += 1
                try:
                    vol_s = data_raw['Volume'].iloc[:, 0] if isinstance(data_raw.columns, pd.MultiIndex) else data_raw['Volume']
                    vol_colors = ['#00ff8888' if c >= o else '#ff444488' for c, o in zip(seri, open_s)]
                    fig.add_trace(go.Bar(x=seri.index, y=vol_s, marker_color=vol_colors, showlegend=False), row=cur_row, col=1)
                except: pass
            if goster_rsi_chart:
                cur_row += 1
                rsi_full = hesapla_rsi(seri)
                fig.add_trace(go.Scatter(x=seri.index, y=rsi_full, line=dict(color='#aa88ff', width=1.5), name='RSI'), row=cur_row, col=1)
                fig.add_hline(y=70, line=dict(color='#ff4444', width=1, dash='dot'), row=cur_row, col=1)
                fig.add_hline(y=30, line=dict(color='#00ff88', width=1, dash='dot'), row=cur_row, col=1)
                fig.update_yaxes(range=[0,100], row=cur_row, col=1)
            if goster_macd_chart:
                cur_row += 1
                macd, signal_line, histogram = hesapla_macd(seri)
                hist_colors = ['#00ff88' if v >= 0 else '#ff4444' for v in histogram]
                fig.add_trace(go.Bar(x=seri.index, y=histogram, marker_color=hist_colors, showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=macd, line=dict(color='#00d4ff', width=1.5), name='MACD'), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=signal_line, line=dict(color='#ff8800', width=1.5), name='Signal'), row=cur_row, col=1)
            fig.update_layout(title=f"{t_kod} — {t_ad} | {t_sure_etiket}", template="plotly_dark",
                plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f', xaxis_rangeslider_visible=False,
                legend=dict(bgcolor='#0f1520', bordercolor='#1e2a3a', font=dict(size=11, family='JetBrains Mono')),
                font=dict(family='JetBrains Mono', color='#8899aa'), height=600, margin=dict(l=10,r=10,t=40,b=10))
            fig.update_xaxes(gridcolor='#1e2a3a', linecolor='#1e2a3a')
            fig.update_yaxes(gridcolor='#1e2a3a', linecolor='#1e2a3a')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">İNDİKATÖR SİNYALLERİ</div>', unsafe_allow_html=True)
        cols = st.columns(len(sinyaller))
        for i, (ind_ad, ind_data) in enumerate(sinyaller.items()):
            badge_cls = 'badge-buy' if ind_data['sinyal'] == 'AL' else ('badge-sell' if ind_data['sinyal'] == 'SAT' else 'badge-hold')
            cols[i].markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">{ind_ad}</div><div style="font-family:JetBrains Mono,monospace;font-size:13px;color:#c8d8e8;margin:4px 0">{ind_data["deger"]}</div><span class="badge {badge_cls}">{ind_data["sinyal"]}</span></div>', unsafe_allow_html=True)
    else:
        st.warning(f"⚠ {t_kod} için veri indirilemedi.")

# ============================================================
# TAB 2: İLERİ İNDİKATÖRLER (Ichimoku, Fibonacci, Pivot, OBV, CCI, Williams %R)
# ============================================================
with tab2:
    st.markdown('<div class="section-title">📐 İLERİ TEKNİK İNDİKATÖRLER</div>', unsafe_allow_html=True)
    data_adv = veri_indir(f"{t_kod}.IS", "1y", "1d")

    if data_adv is not None and not data_adv.empty:
        seri_adv = get_seri(data_adv)

        ind_sec = st.radio("İndikatör Seç:", ["Ichimoku Bulutu", "Fibonacci Seviyeleri", "Pivot Noktaları", "OBV (Hacim Akışı)", "CCI & Williams %R"], horizontal=True)

        if ind_sec == "Ichimoku Bulutu":
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-bottom:12px">Ichimoku Kinko Hyo — Japonya kökenli trend ve destek/direnç sistemi</div>', unsafe_allow_html=True)
            tenkan, kijun, senkou_a, senkou_b, chikou = hesapla_ichimoku(data_adv)
            fig_ichi = go.Figure()
            fig_ichi.add_trace(go.Candlestick(x=seri_adv.index,
                open=data_adv['Open'].iloc[:,0] if isinstance(data_adv.columns, pd.MultiIndex) else data_adv['Open'],
                high=data_adv['High'].iloc[:,0] if isinstance(data_adv.columns, pd.MultiIndex) else data_adv['High'],
                low=data_adv['Low'].iloc[:,0] if isinstance(data_adv.columns, pd.MultiIndex) else data_adv['Low'],
                close=seri_adv, name=t_kod,
                increasing=dict(line=dict(color='#00ff88')), decreasing=dict(line=dict(color='#ff4444'))))
            fig_ichi.add_trace(go.Scatter(x=seri_adv.index, y=tenkan, line=dict(color='#ff6688', width=1.5), name='Tenkan-sen (9)'))
            fig_ichi.add_trace(go.Scatter(x=seri_adv.index, y=kijun, line=dict(color='#4488ff', width=1.5), name='Kijun-sen (26)'))
            fig_ichi.add_trace(go.Scatter(x=seri_adv.index, y=senkou_a, line=dict(color='#00ff8844', width=0), name='Senkou A', fill=None, showlegend=False))
            fig_ichi.add_trace(go.Scatter(x=seri_adv.index, y=senkou_b, line=dict(color='#ff444444', width=0), name='Kumo (Bulut)',
                fill='tonexty', fillcolor='rgba(0,255,136,0.08)'))
            fig_ichi.add_trace(go.Scatter(x=seri_adv.index, y=chikou, line=dict(color='#ffaa00', width=1, dash='dot'), name='Chikou'))
            fig_ichi.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                height=500, xaxis_rangeslider_visible=False, font=dict(family='JetBrains Mono', color='#8899aa'),
                legend=dict(bgcolor='#0f1520', bordercolor='#1e2a3a', font=dict(size=10, family='JetBrains Mono')),
                margin=dict(l=10,r=10,t=30,b=10))
            fig_ichi.update_xaxes(gridcolor='#1e2a3a'); fig_ichi.update_yaxes(gridcolor='#1e2a3a')
            st.plotly_chart(fig_ichi, use_container_width=True)

            # Ichimoku yorumu
            fiyat_son_adv = float(seri_adv.iloc[-1])
            sa_son = float(senkou_a.dropna().iloc[-1]) if not senkou_a.dropna().empty else 0
            sb_son = float(senkou_b.dropna().iloc[-1]) if not senkou_b.dropna().empty else 0
            t_son  = float(tenkan.dropna().iloc[-1]) if not tenkan.dropna().empty else 0
            k_son  = float(kijun.dropna().iloc[-1]) if not kijun.dropna().empty else 0
            bulut_ust = max(sa_son, sb_son); bulut_alt = min(sa_son, sb_son)
            yorum = "GÜÇLÜ AL 🚀" if fiyat_son_adv > bulut_ust and t_son > k_son else (
                    "SAT 📉" if fiyat_son_adv < bulut_alt and t_son < k_son else "NÖTR ⚖")
            renk_y = "#00ff88" if "AL" in yorum else ("#ff4444" if "SAT" in yorum else "#ffaa00")
            ic1, ic2, ic3 = st.columns(3)
            ic1.markdown(f'<div class="metric-card"><div class="metric-label">BULUT DURUMU</div><div class="metric-value" style="font-size:14px;color:{renk_y}">{yorum}</div></div>', unsafe_allow_html=True)
            ic2.markdown(f'<div class="metric-card"><div class="metric-label">TENKAN / KİJUN</div><div style="font-family:JetBrains Mono,monospace;font-size:13px;color:#e2e8f0">{t_son:.2f} / {k_son:.2f}</div></div>', unsafe_allow_html=True)
            ic3.markdown(f'<div class="metric-card"><div class="metric-label">BULUT (Üst/Alt)</div><div style="font-family:JetBrains Mono,monospace;font-size:13px;color:#e2e8f0">{bulut_ust:.2f} / {bulut_alt:.2f}</div></div>', unsafe_allow_html=True)

        elif ind_sec == "Fibonacci Seviyeleri":
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-bottom:12px">Son 100 günlük Fibonacci Geri Çekilme Seviyeleri</div>', unsafe_allow_html=True)
            periyot_fib = st.slider("Hesaplama periyodu (gün):", 50, 252, 100)
            fib_seviyeler = hesapla_fibonacci(seri_adv, periyot_fib)
            fig_fib = go.Figure()
            fig_fib.add_trace(go.Scatter(x=seri_adv.index[-periyot_fib:], y=seri_adv.iloc[-periyot_fib:],
                line=dict(color='#00d4ff', width=2), name=t_kod))
            renkler_fib = {'0.0% (Yüksek)':'#00ff88','23.6%':'#88ffcc','38.2%':'#ffdd00','50.0%':'#ffaa00','61.8%':'#ff8800','78.6%':'#ff6644','100% (Düşük)':'#ff4444'}
            for etiket, seviye in fib_seviyeler.items():
                renk_fib = renkler_fib.get(etiket, '#888888')
                fig_fib.add_hline(y=seviye, line=dict(color=renk_fib, width=1, dash='dash'),
                    annotation_text=f"  {etiket}: {seviye:.2f}", annotation_position="right",
                    annotation_font=dict(color=renk_fib, size=10, family='JetBrains Mono'))
            fig_fib.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                height=480, font=dict(family='JetBrains Mono', color='#8899aa'),
                legend=dict(bgcolor='#0f1520'), margin=dict(l=10,r=120,t=30,b=10))
            fig_fib.update_xaxes(gridcolor='#1e2a3a'); fig_fib.update_yaxes(gridcolor='#1e2a3a')
            st.plotly_chart(fig_fib, use_container_width=True)
            fiyat_son_adv = float(seri_adv.iloc[-1])
            destek = [(e,v) for e,v in fib_seviyeler.items() if v < fiyat_son_adv]
            direnc = [(e,v) for e,v in fib_seviyeler.items() if v > fiyat_son_adv]
            col_d, col_r = st.columns(2)
            with col_d:
                st.markdown('<div class="section-title" style="color:#00ff88">DESTEK SEVİYELERİ</div>', unsafe_allow_html=True)
                for e, v in reversed(destek[-3:]):
                    st.markdown(f'<div class="fundamental-card"><div class="fundamental-row"><span class="frow-label">{e}</span><span class="frow-value frow-positive">{v:.2f} TL</span></div></div>', unsafe_allow_html=True)
            with col_r:
                st.markdown('<div class="section-title" style="color:#ff4444">DİRENÇ SEVİYELERİ</div>', unsafe_allow_html=True)
                for e, v in direnc[:3]:
                    st.markdown(f'<div class="fundamental-card"><div class="fundamental-row"><span class="frow-label">{e}</span><span class="frow-value frow-negative">{v:.2f} TL</span></div></div>', unsafe_allow_html=True)

        elif ind_sec == "Pivot Noktaları":
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-bottom:12px">Klasik Pivot — Destek ve Direnç Seviyeleri</div>', unsafe_allow_html=True)
            pivot_seviyeler = hesapla_pivot(data_adv)
            fig_pv = go.Figure()
            fig_pv.add_trace(go.Scatter(x=seri_adv.index[-60:], y=seri_adv.iloc[-60:],
                line=dict(color='#00d4ff', width=2), name=t_kod))
            renkler_pv = {'R3':'#ff2222','R2':'#ff5555','R1':'#ff8888','Pivot':'#ffdd00','S1':'#88ff88','S2':'#55ff55','S3':'#22ff22'}
            for etiket, seviye in pivot_seviyeler.items():
                renk_pv = renkler_pv.get(etiket,'#888')
                fig_pv.add_hline(y=seviye, line=dict(color=renk_pv, width=1.5 if etiket=='Pivot' else 1, dash='solid' if etiket=='Pivot' else 'dash'),
                    annotation_text=f"  {etiket}: {seviye:.2f}", annotation_font=dict(color=renk_pv, size=10, family='JetBrains Mono'))
            fig_pv.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                height=460, font=dict(family='JetBrains Mono', color='#8899aa'), margin=dict(l=10,r=120,t=30,b=10))
            fig_pv.update_xaxes(gridcolor='#1e2a3a'); fig_pv.update_yaxes(gridcolor='#1e2a3a')
            st.plotly_chart(fig_pv, use_container_width=True)
            p_cols = st.columns(7)
            for i, (etiket, seviye) in enumerate(pivot_seviyeler.items()):
                renk_badge = "#ff4444" if etiket.startswith("R") else ("#ffdd00" if etiket == "Pivot" else "#00ff88")
                p_cols[i].markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">{etiket}</div><div style="font-family:JetBrains Mono,monospace;font-size:14px;font-weight:700;color:{renk_badge}">{seviye:.2f}</div></div>', unsafe_allow_html=True)

        elif ind_sec == "OBV (Hacim Akışı)":
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-bottom:12px">On-Balance Volume — Fiyat ve hacim uyumu analizi</div>', unsafe_allow_html=True)
            try:
                if isinstance(data_adv.columns, pd.MultiIndex):
                    data_obv = data_adv.copy()
                    data_obv.columns = data_obv.columns.get_level_values(0)
                    data_obv = data_obv.loc[:, ~data_obv.columns.duplicated()]
                else:
                    data_obv = data_adv
                obv_seri = hesapla_obv(data_obv)
                fig_obv = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.6,0.4])
                fig_obv.add_trace(go.Scatter(x=seri_adv.index, y=seri_adv, line=dict(color='#00d4ff', width=2), name=t_kod), row=1, col=1)
                obv_renk = '#00ff88' if obv_seri.iloc[-1] > obv_seri.iloc[-20] else '#ff4444'
                fig_obv.add_trace(go.Scatter(x=seri_adv.index, y=obv_seri, line=dict(color=obv_renk, width=1.5), name='OBV', fill='tozeroy', fillcolor=obv_renk.replace(')',',0.08)').replace('rgb','rgba') if 'rgb' in obv_renk else obv_renk+'22'), row=2, col=1)
                fig_obv.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                    height=460, font=dict(family='JetBrains Mono', color='#8899aa'),
                    legend=dict(bgcolor='#0f1520'), margin=dict(l=10,r=10,t=30,b=10))
                fig_obv.update_xaxes(gridcolor='#1e2a3a'); fig_obv.update_yaxes(gridcolor='#1e2a3a')
                st.plotly_chart(fig_obv, use_container_width=True)
                obv_trend = "YÜKSELİYOR ↑" if obv_seri.iloc[-1] > obv_seri.iloc[-20] else "DÜŞÜYOR ↓"
                fiyat_trend = "YÜKSELİYOR ↑" if seri_adv.iloc[-1] > seri_adv.iloc[-20] else "DÜŞÜYOR ↓"
                uyum = obv_trend == fiyat_trend
                st.markdown(f"""
                <div class="ai-box">
                    <div class="ai-box-header">◈ OBV ANALİZİ</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:8px">
                        <div><div class="metric-label">FİYAT TREND</div><div style="color:{'#00ff88' if 'YÜKSELİYOR' in fiyat_trend else '#ff4444'};font-family:JetBrains Mono,monospace;font-weight:700">{fiyat_trend}</div></div>
                        <div><div class="metric-label">OBV TREND</div><div style="color:{'#00ff88' if 'YÜKSELİYOR' in obv_trend else '#ff4444'};font-family:JetBrains Mono,monospace;font-weight:700">{obv_trend}</div></div>
                        <div><div class="metric-label">UYUM</div><div style="color:{'#00ff88' if uyum else '#ff4444'};font-family:JetBrains Mono,monospace;font-weight:700">{'✓ UYUMLU' if uyum else '✗ DİVERJANS'}</div></div>
                    </div>
                    <div style="margin-top:12px;font-size:13px">
                    {'✅ Fiyat ve hacim aynı yönde hareket ediyor — trend güçlü.' if uyum else '⚠ Fiyat-OBV diverjansı tespit edildi — trend zayıflıyor olabilir.'}
                    </div>
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"OBV hesaplanamadı: {e}")

        elif ind_sec == "CCI & Williams %R":
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-bottom:12px">CCI (Commodity Channel Index) & Williams %R — Aşırı alım/satım osilatörleri</div>', unsafe_allow_html=True)
            try:
                if isinstance(data_adv.columns, pd.MultiIndex):
                    data_osc = data_adv.copy(); data_osc.columns = data_osc.columns.get_level_values(0)
                    data_osc = data_osc.loc[:, ~data_osc.columns.duplicated()]
                else:
                    data_osc = data_adv
                cci_seri = hesapla_cci(data_osc)
                wr_seri  = hesapla_williams_r(data_osc)
                fig_osc = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5,0.25,0.25])
                fig_osc.add_trace(go.Scatter(x=seri_adv.index, y=seri_adv, line=dict(color='#00d4ff',width=2), name=t_kod), row=1, col=1)
                fig_osc.add_trace(go.Scatter(x=seri_adv.index, y=cci_seri, line=dict(color='#ffaa00',width=1.5), name='CCI'), row=2, col=1)
                fig_osc.add_hline(y=100, line=dict(color='#ff4444',width=1,dash='dot'), row=2, col=1)
                fig_osc.add_hline(y=-100, line=dict(color='#00ff88',width=1,dash='dot'), row=2, col=1)
                fig_osc.add_trace(go.Scatter(x=seri_adv.index, y=wr_seri, line=dict(color='#aa88ff',width=1.5), name='Williams %R'), row=3, col=1)
                fig_osc.add_hline(y=-20, line=dict(color='#ff4444',width=1,dash='dot'), row=3, col=1)
                fig_osc.add_hline(y=-80, line=dict(color='#00ff88',width=1,dash='dot'), row=3, col=1)
                fig_osc.update_yaxes(title_text="CCI", row=2, col=1)
                fig_osc.update_yaxes(title_text="W%R", range=[-100,0], row=3, col=1)
                fig_osc.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                    height=520, font=dict(family='JetBrains Mono',color='#8899aa'),
                    legend=dict(bgcolor='#0f1520'), margin=dict(l=10,r=10,t=30,b=10))
                fig_osc.update_xaxes(gridcolor='#1e2a3a'); fig_osc.update_yaxes(gridcolor='#1e2a3a')
                st.plotly_chart(fig_osc, use_container_width=True)
                cci_son = float(cci_seri.dropna().iloc[-1]); wr_son = float(wr_seri.dropna().iloc[-1])
                cci_yorum = "AŞIRI ALIM (SAT)" if cci_son > 100 else ("AŞIRI SATIM (AL)" if cci_son < -100 else "NÖTR")
                wr_yorum  = "AŞIRI ALIM (SAT)" if wr_son > -20 else ("AŞIRI SATIM (AL)" if wr_son < -80 else "NÖTR")
                cci_renk  = "#ff4444" if "SAT" in cci_yorum else ("#00ff88" if "AL" in cci_yorum else "#ffaa00")
                wr_renk   = "#ff4444" if "SAT" in wr_yorum  else ("#00ff88" if "AL" in wr_yorum  else "#ffaa00")
                c1, c2 = st.columns(2)
                c1.markdown(f'<div class="metric-card"><div class="metric-label">CCI ({cci_son:.1f})</div><div style="font-family:JetBrains Mono,monospace;font-size:14px;font-weight:700;color:{cci_renk}">{cci_yorum}</div></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="metric-card"><div class="metric-label">Williams %R ({wr_son:.1f})</div><div style="font-family:JetBrains Mono,monospace;font-size:14px;font-weight:700;color:{wr_renk}">{wr_yorum}</div></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Osilatör hesaplanamadı: {e}")
    else:
        st.warning(f"⚠ {t_kod} için veri indirilemedi.")

# ============================================================
# TAB 3: TEMEL ANALİZ
# ============================================================
with tab3:
    st.markdown('<div class="section-title">🏢 TEMEL ANALİZ & FİNANSAL VERİLER</div>', unsafe_allow_html=True)
    if st.button("📊 Temel Verileri Yükle", use_container_width=False, key="temel_btn"):
        with st.spinner("Yahoo Finance'den finansal veriler çekiliyor..."):
            info = temel_veri_cek(t_kod)
            st.session_state[f"temel_{t_kod}"] = info

    info = st.session_state.get(f"temel_{t_kod}", None)

    if info:
        t1, t2, t3 = st.columns(3)

        with t1:
            st.markdown('<div class="section-title">💰 DEĞERLEMEMETRİKLERİ</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="fundamental-card">
                <div class="fundamental-row"><span class="frow-label">F/K Oranı (P/E)</span><span class="frow-value">{format_oran(info.get('trailingPE'))}</span></div>
                <div class="fundamental-row"><span class="frow-label">İleriye Dönük F/K</span><span class="frow-value">{format_oran(info.get('forwardPE'))}</span></div>
                <div class="fundamental-row"><span class="frow-label">PD/DD (P/B)</span><span class="frow-value">{format_oran(info.get('priceToBook'))}</span></div>
                <div class="fundamental-row"><span class="frow-label">F/S (P/S)</span><span class="frow-value">{format_oran(info.get('priceToSalesTrailing12Months'))}</span></div>
                <div class="fundamental-row"><span class="frow-label">EV/FAVÖK</span><span class="frow-value">{format_oran(info.get('enterpriseToEbitda'))}</span></div>
                <div class="fundamental-row"><span class="frow-label">EV/Gelir</span><span class="frow-value">{format_oran(info.get('enterpriseToRevenue'))}</span></div>
                <div class="fundamental-row"><span class="frow-label">PEG Oranı</span><span class="frow-value">{format_oran(info.get('pegRatio'))}</span></div>
            </div>""", unsafe_allow_html=True)

        with t2:
            st.markdown('<div class="section-title">📈 BÜYÜME & KÂRLİLIK</div>', unsafe_allow_html=True)
            gm = info.get('grossMargins', 0); pm = info.get('profitMargins', 0); om = info.get('operatingMargins', 0)
            rg = info.get('revenueGrowth', 0); eg = info.get('earningsGrowth', 0)
            roe = info.get('returnOnEquity', 0); roa = info.get('returnOnAssets', 0)
            st.markdown(f"""
            <div class="fundamental-card">
                <div class="fundamental-row"><span class="frow-label">Brüt Kar Marjı</span><span class="frow-value {'frow-positive' if gm and gm>0 else 'frow-negative'}">{format_oran(gm, 100, '%')}</span></div>
                <div class="fundamental-row"><span class="frow-label">Net Kar Marjı</span><span class="frow-value {'frow-positive' if pm and pm>0 else 'frow-negative'}">{format_oran(pm, 100, '%')}</span></div>
                <div class="fundamental-row"><span class="frow-label">Faaliyet Marjı</span><span class="frow-value {'frow-positive' if om and om>0 else 'frow-negative'}">{format_oran(om, 100, '%')}</span></div>
                <div class="fundamental-row"><span class="frow-label">Gelir Büyümesi (YoY)</span><span class="frow-value {'frow-positive' if rg and rg>0 else 'frow-negative'}">{format_oran(rg, 100, '%')}</span></div>
                <div class="fundamental-row"><span class="frow-label">Kazanç Büyümesi</span><span class="frow-value {'frow-positive' if eg and eg>0 else 'frow-negative'}">{format_oran(eg, 100, '%')}</span></div>
                <div class="fundamental-row"><span class="frow-label">Özkaynak Getirisi (ROE)</span><span class="frow-value {'frow-positive' if roe and roe>0.1 else ''}">{format_oran(roe, 100, '%')}</span></div>
                <div class="fundamental-row"><span class="frow-label">Varlık Getirisi (ROA)</span><span class="frow-value">{format_oran(roa, 100, '%')}</span></div>
            </div>""", unsafe_allow_html=True)

        with t3:
            st.markdown('<div class="section-title">🏦 BİLANÇO & TEMETTÜ</div>', unsafe_allow_html=True)
            mc  = info.get('marketCap', 0); ev = info.get('enterpriseValue', 0)
            rev = info.get('totalRevenue', 0); ebitda = info.get('ebitda', 0)
            debt = info.get('totalDebt', 0); cash = info.get('totalCash', 0)
            div_y = info.get('dividendYield', 0); div_r = info.get('payoutRatio', 0)
            beta = info.get('beta', 0); emp = info.get('fullTimeEmployees', 0)
            st.markdown(f"""
            <div class="fundamental-card">
                <div class="fundamental-row"><span class="frow-label">Piyasa Değeri</span><span class="frow-value metric-neutral">{format_buyuk_sayi(mc)}</span></div>
                <div class="fundamental-row"><span class="frow-label">Firma Değeri (EV)</span><span class="frow-value">{format_buyuk_sayi(ev)}</span></div>
                <div class="fundamental-row"><span class="frow-label">Toplam Gelir</span><span class="frow-value">{format_buyuk_sayi(rev)}</span></div>
                <div class="fundamental-row"><span class="frow-label">FAVÖK</span><span class="frow-value">{format_buyuk_sayi(ebitda)}</span></div>
                <div class="fundamental-row"><span class="frow-label">Toplam Borç</span><span class="frow-value {'frow-negative' if debt and debt>0 else ''}">{format_buyuk_sayi(debt)}</span></div>
                <div class="fundamental-row"><span class="frow-label">Nakit & Benzeri</span><span class="frow-value frow-positive">{format_buyuk_sayi(cash)}</span></div>
                <div class="fundamental-row"><span class="frow-label">Temettü Verimi</span><span class="frow-value {'frow-positive' if div_y and div_y>0 else ''}">{format_oran(div_y, 100, '%')}</span></div>
                <div class="fundamental-row"><span class="frow-label">Beta (Volatilite)</span><span class="frow-value">{format_oran(beta)}</span></div>
                <div class="fundamental-row"><span class="frow-label">Çalışan Sayısı</span><span class="frow-value">{f'{emp:,}' if emp else '—'}</span></div>
            </div>""", unsafe_allow_html=True)

        # Şirket bilgisi
        if info.get('longBusinessSummary') or info.get('longName'):
            st.markdown('<div class="section-title" style="margin-top:20px">🏢 ŞİRKET BİLGİSİ</div>', unsafe_allow_html=True)
            long_name = info.get('longName', t_ad)
            sector = info.get('sector', '—'); industry = info.get('industry', '—')
            website = info.get('website', '')
            ozet = info.get('longBusinessSummary', '')[:600] + ('...' if len(info.get('longBusinessSummary','')) > 600 else '')
            st.markdown(f"""
            <div class="ai-box">
                <div class="ai-box-header">◈ {long_name}</div>
                <div style="display:flex;gap:20px;margin-bottom:12px;font-family:JetBrains Mono,monospace;font-size:11px">
                    <span style="color:#4a6080">Sektör: <span style="color:#00d4ff">{sector}</span></span>
                    <span style="color:#4a6080">Sanayi: <span style="color:#00d4ff">{industry}</span></span>
                    {f'<a href="{website}" target="_blank" style="color:#00d4ff;text-decoration:none">{website}</a>' if website else ''}
                </div>
                <div style="font-size:13px;color:#8899aa;line-height:1.7">{ozet}</div>
            </div>""", unsafe_allow_html=True)

        # 52 hafta fiyat aralığı
        low52 = info.get('fiftyTwoWeekLow', 0); high52 = info.get('fiftyTwoWeekHigh', 0)
        cur_p = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        if low52 and high52 and cur_p:
            st.markdown('<div class="section-title" style="margin-top:20px">52 HAFTA FİYAT ARALIĞI</div>', unsafe_allow_html=True)
            pct_pos = min(max(((cur_p - low52) / (high52 - low52)) * 100, 0), 100) if (high52 - low52) > 0 else 50
            st.markdown(f"""
            <div class="fundamental-card">
                <div style="display:flex;justify-content:space-between;font-family:JetBrains Mono,monospace;font-size:11px;margin-bottom:8px">
                    <span style="color:#00ff88">📉 {low52:.2f} TL (Düşük)</span>
                    <span style="color:#e2e8f0;font-weight:700">📍 {cur_p:.2f} TL</span>
                    <span style="color:#ff4444">📈 {high52:.2f} TL (Yüksek)</span>
                </div>
                <div style="background:#1e2a3a;border-radius:4px;height:8px;position:relative">
                    <div style="background:linear-gradient(90deg,#00ff88,#ffaa00,#ff4444);border-radius:4px;height:8px;width:100%"></div>
                    <div style="position:absolute;top:-4px;left:{pct_pos}%;transform:translateX(-50%);width:16px;height:16px;background:#00d4ff;border-radius:50%;border:2px solid #0a0a0f"></div>
                </div>
                <div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;margin-top:8px;text-align:center">
                    52 Hafta Aralığında Pozisyon: %{pct_pos:.1f}
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="ai-box" style="text-align:center;color:#4a6080;padding:50px">
            <div style="font-size:36px;margin-bottom:12px">🏢</div>
            <div style="font-size:15px">Temel verileri yüklemek için yukarıdaki butona tıklayın.</div>
            <div style="font-size:11px;margin-top:8px">F/K, PD/DD, EV/FAVÖK, temettü, büyüme oranları ve bilanço verileri</div>
        </div>""", unsafe_allow_html=True)

# ============================================================
# TAB 4: SCREENER
# ============================================================
with tab4:
    st.markdown('<div class="section-title">🔍 OTOMATİK HİSSE TARAYICI (SCREENER)</div>', unsafe_allow_html=True)

    scr1, scr2, scr3, scr4 = st.columns(4)
    with scr1:
        sinyal_filtre = st.selectbox("Sinyal Filtresi:", ["Tümü", "AL Sinyalleri", "SAT Sinyalleri", "Aşırı Satım (RSI<30)", "Aşırı Alım (RSI>70)"])
    with scr2:
        min_rsi = st.slider("Min RSI:", 0, 100, 0)
    with scr3:
        max_rsi = st.slider("Max RSI:", 0, 100, 100)
    with scr4:
        max_hisse_tara = st.selectbox("Kaç hisse taransın:", [30, 50, 75, 100], index=1)
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#ffaa00;margin-top:4px">⚠ Fazla hisse = uzun süre</div>', unsafe_allow_html=True)

    if st.button("🚀 Tara", use_container_width=True, key="screener_btn"):
        kodlar = list(bist_100_full.keys())
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080">Hisseler taranıyor...</div>', unsafe_allow_html=True)
        with st.spinner(f"⏳ {min(max_hisse_tara, len(kodlar))} hisse taranıyor — lütfen bekleyin..."):
            sonuclar = screener_hisse_tara(
                tuple(kodlar[:max_hisse_tara]),
                min_rsi, max_rsi, sinyal_filtre, max_hisse_tara
            )
            st.session_state.screener_sonuc = sonuclar
        progress_bar.empty()
        status_text.empty()

    sonuclar = st.session_state.screener_sonuc
    if sonuclar is not None:
        if sonuclar:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-bottom:12px">🔎 {len(sonuclar)} hisse kriterlere uydu</div>', unsafe_allow_html=True)

            # Özet istatistikler
            al_sayisi  = sum(1 for s in sonuclar if "AL" in s['Sinyal'])
            sat_sayisi = sum(1 for s in sonuclar if "SAT" in s['Sinyal'])
            bekle_sayisi = len(sonuclar) - al_sayisi - sat_sayisi

            sm1, sm2, sm3 = st.columns(3)
            sm1.markdown(f'<div class="metric-card" style="text-align:center;border-color:#00ff8844"><div class="metric-label">AL SİNYALLİ</div><div class="metric-value metric-positive">{al_sayisi}</div></div>', unsafe_allow_html=True)
            sm2.markdown(f'<div class="metric-card" style="text-align:center;border-color:#ff444444"><div class="metric-label">SAT SİNYALLİ</div><div class="metric-value metric-negative">{sat_sayisi}</div></div>', unsafe_allow_html=True)
            sm3.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">BEKLE</div><div class="metric-value metric-neutral">{bekle_sayisi}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Tablo başlığı
            h_cols = st.columns([1.2, 2.5, 1.2, 1.2, 1, 1.5, 1.2])
            basliklar = ["KOD", "ŞİRKET", "FİYAT", "DEĞİŞİM%", "RSI", "SİNYAL", "HACİM(M)"]
            for col, b in zip(h_cols, basliklar):
                col.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;padding:4px 0;border-bottom:1px solid #1e2a3a;letter-spacing:1px">{b}</div>', unsafe_allow_html=True)

            # Satırlar
            for s in sonuclar:
                deg_renk = "#00ff88" if s['Değişim%'] >= 0 else "#ff4444"
                deg_yon  = "▲" if s['Değişim%'] >= 0 else "▼"
                rsi_renk = "#00ff88" if s['RSI'] < 30 else ("#ff4444" if s['RSI'] > 70 else "#ffaa00")
                badge_cls = "badge-buy" if "AL" in s['Sinyal'] else ("badge-sell" if "SAT" in s['Sinyal'] else "badge-hold")

                r_cols = st.columns([1.2, 2.5, 1.2, 1.2, 1, 1.5, 1.2])
                r_cols[0].markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:13px;font-weight:700;color:#00d4ff;padding:6px 0">{s["Kod"]}</div>', unsafe_allow_html=True)
                r_cols[1].markdown(f'<div style="font-size:12px;color:#8899aa;padding:6px 0">{s["Şirket"]}</div>', unsafe_allow_html=True)
                r_cols[2].markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:12px;color:#e2e8f0;padding:6px 0">{s["Fiyat"]:.2f} TL</div>', unsafe_allow_html=True)
                r_cols[3].markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:12px;color:{deg_renk};padding:6px 0">{deg_yon} {abs(s["Değişim%"]):.2f}%</div>', unsafe_allow_html=True)
                r_cols[4].markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:12px;color:{rsi_renk};padding:6px 0;font-weight:700">{s["RSI"]:.1f}</div>', unsafe_allow_html=True)
                r_cols[5].markdown(f'<span class="badge {badge_cls}">{s["Sinyal"]}</span>', unsafe_allow_html=True)
                r_cols[6].markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;padding:6px 0">{s["Hacim(M)"]:.1f}M</div>', unsafe_allow_html=True)

            # Excel indirme
            df_exp = pd.DataFrame(sonuclar)
            csv = df_exp.to_csv(index=False).encode('utf-8')
            st.download_button("⬇ CSV İndir", csv, f"screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv", use_container_width=False)

        else:
            st.markdown("""
            <div class="ai-box" style="text-align:center;color:#4a6080;padding:40px">
                <div style="font-size:32px;margin-bottom:10px">🔍</div>
                <div>Seçilen kriterlere uyan hisse bulunamadı.</div>
                <div style="font-size:11px;margin-top:6px">Filtreleri gevşeterek tekrar deneyin.</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="ai-box" style="text-align:center;color:#4a6080;padding:50px">
            <div style="font-size:36px;margin-bottom:12px">🔍</div>
            <div style="font-size:15px">Filtreleri ayarlayın ve "Tara" butonuna basın.</div>
            <div style="font-size:11px;margin-top:8px">RSI filtresi, sinyal filtresi ve daha fazlası ile hisseleri tarayın</div>
        </div>""", unsafe_allow_html=True)

# ============================================================
# TAB 5: AI RAPORU
# ============================================================
with tab5:
    st.markdown('<div class="section-title">🤖 YAPAY ZEKA ANALİZ RAPORU</div>', unsafe_allow_html=True)
    data_ai = veri_indir(f"{t_kod}.IS", "1y", "1d")
    if data_ai is not None and not data_ai.empty:
        seri_ai = get_seri(data_ai)
        fiyat_ai = float(seri_ai.iloc[-1])
        fiyat_prev_ai = float(seri_ai.iloc[-2]) if len(seri_ai) > 1 else fiyat_ai
        degisim_ai = ((fiyat_ai - fiyat_prev_ai) / fiyat_prev_ai) * 100
        rsi_ai = hesapla_rsi(seri_ai).iloc[-1]
        _, _, gs_ai = teknik_sinyal_hesapla(seri_ai, data_ai)
        ai_kol1, ai_kol2 = st.columns([2, 1])
        with ai_kol2:
            st.markdown(f"""
            <div class="metric-card"><div class="metric-label">ANALİZ EDİLEN HİSSE</div>
            <div style="font-family:JetBrains Mono,monospace;font-size:18px;color:#00d4ff;font-weight:700">{t_kod}</div>
            <div style="font-size:12px;color:#4a6080">{t_ad}</div></div>
            <div class="metric-card" style="margin-top:8px"><div class="metric-label">GÜNCEL FİYAT</div>
            <div class="metric-value">{fiyat_ai:.2f} TL</div>
            <div style="font-size:12px;color:{'#00ff88' if degisim_ai>=0 else '#ff4444'}">{'▲' if degisim_ai>=0 else '▼'} {abs(degisim_ai):.2f}%</div></div>
            <div class="metric-card" style="margin-top:8px"><div class="metric-label">TEKNİK SİNYAL</div>
            <div class="metric-value" style="font-size:16px;color:{'#00ff88' if 'AL' in gs_ai else ('#ff4444' if 'SAT' in gs_ai else '#ffaa00')}">{gs_ai}</div></div>
            """, unsafe_allow_html=True)
        with ai_kol1:
            if st.button("🤖 AI Analizi Üret", use_container_width=True, key="ai_btn"):
                with st.spinner("Yapay zeka raporu hazırlanıyor..."):
                    sonuc = ai_analiz_yap(t_kod, t_ad, fiyat_ai, degisim_ai, rsi_ai, gs_ai, 0, seri_ai)
                    if sonuc:
                        st.session_state[f"ai_sonuc_{t_kod}"] = sonuc
            cache_key = f"ai_sonuc_{t_kod}"
            if cache_key in st.session_state:
                st.markdown(f'<div class="ai-box"><div class="ai-box-header">⬡ GROQ AI ANALİZİ • {t_kod} • {datetime.now().strftime("%d.%m.%Y")}</div>{st.session_state[cache_key].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ai-box" style="text-align:center;color:#4a6080;padding:40px"><div style="font-size:32px;margin-bottom:12px">🤖</div><div>AI analizi başlatmak için butona tıklayın.</div><div style="font-size:12px;margin-top:8px">Groq — Llama 3.3 70B</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="margin-top:24px">SON 30 GÜN GÖRÜNÜMÜ</div>', unsafe_allow_html=True)
        son30 = seri_ai.iloc[-30:]; rsi30 = hesapla_rsi(seri_ai).iloc[-30:]
        fig_ai = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7,0.3])
        fig_ai.add_trace(go.Scatter(x=son30.index, y=son30, fill='tozeroy', fillcolor='rgba(0,212,255,0.08)', line=dict(color='#00d4ff', width=2)), row=1, col=1)
        fig_ai.add_trace(go.Scatter(x=rsi30.index, y=rsi30, line=dict(color='#aa88ff', width=1.5)), row=2, col=1)
        fig_ai.add_hline(y=70, line=dict(color='#ff4444',width=1,dash='dot'), row=2, col=1)
        fig_ai.add_hline(y=30, line=dict(color='#00ff88',width=1,dash='dot'), row=2, col=1)
        fig_ai.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
            height=300, showlegend=False, margin=dict(l=10,r=10,t=10,b=10))
        fig_ai.update_xaxes(gridcolor='#1e2a3a'); fig_ai.update_yaxes(gridcolor='#1e2a3a')
        st.plotly_chart(fig_ai, use_container_width=True)
    else:
        st.warning("Veri yüklenemedi.")

# ============================================================
# TAB 6: HABERLER
# ============================================================
with tab6:
    st.markdown('<div class="section-title">📰 PİYASA HABERLERİ</div>', unsafe_allow_html=True)
    haber_kol1, haber_kol2 = st.columns([2, 1])
    with haber_kol1:
        if st.button("🔄 Haberleri Yükle / Güncelle", use_container_width=True):
            with st.spinner("Haberler yükleniyor..."):
                haberler = rss_haberleri_cek(t_kod)
                st.session_state[f"rss_{t_kod}"] = haberler
        haberler_cache = st.session_state.get(f"rss_{t_kod}", None)
        if haberler_cache is not None:
            if haberler_cache:
                for haber in haberler_cache:
                    st.markdown(f'<a href="{haber["link"]}" target="_blank" style="text-decoration:none"><div class="news-card {haber["sentiment"]}"><div class="news-title">{haber["baslik"]}</div>{"<div style=\"font-size:12px;color:#6a7d90;margin:4px 0\">" + haber["ozet"] + "...</div>" if haber["ozet"] else ""}<div class="news-meta">📰 {haber["kaynak"]} &nbsp;•&nbsp; 🕐 {haber["tarih"]}</div></div></a>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ai-box" style="text-align:center;color:#4a6080;padding:30px"><div style="font-size:28px">📭</div><div>Haber bulunamadı.</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ai-box" style="text-align:center;color:#4a6080;padding:40px"><div style="font-size:32px;margin-bottom:12px">📰</div><div>Haberleri görmek için butona tıklayın.</div></div>', unsafe_allow_html=True)
    with haber_kol2:
        st.markdown('<div class="section-title">PIYASA ÖZETİ</div>', unsafe_allow_html=True)
        for ad, ticker_k in [("BIST 100","XU100.IS"),("Dolar/TL","USDTRY=X"),("Euro/TL","EURTRY=X"),("Altın (TL)","GC=F")]:
            try:
                d = yf.download(ticker_k, period="2d", progress=False)
                if not d.empty and len(d) >= 2:
                    son = float(d['Close'].iloc[-1].iloc[0]) if isinstance(d.columns, pd.MultiIndex) else float(d['Close'].iloc[-1])
                    prev = float(d['Close'].iloc[-2].iloc[0]) if isinstance(d.columns, pd.MultiIndex) else float(d['Close'].iloc[-2])
                    deg = ((son - prev) / prev) * 100
                    renk = '#00ff88' if deg >= 0 else '#ff4444'
                    yon  = '▲' if deg >= 0 else '▼'
                    st.markdown(f'<div class="metric-card"><div class="metric-label">{ad}</div><div style="display:flex;justify-content:space-between"><div style="font-family:JetBrains Mono,monospace;font-size:14px;color:#e2e8f0;font-weight:600">{son:,.2f}</div><div style="font-family:JetBrains Mono,monospace;font-size:12px;color:{renk}">{yon} {abs(deg):.2f}%</div></div></div>', unsafe_allow_html=True)
            except: pass

# ============================================================
# TAB 7: PORTFÖY
# ============================================================
with tab7:
    st.markdown('<div class="section-title">💼 GELİŞMİŞ PORTFÖY TAKİBİ</div>', unsafe_allow_html=True)
    p_kol1, p_kol2 = st.columns([1, 2])
    with p_kol1:
        with st.expander("➕ Hisse Ekle", expanded=True):
            p_hisse   = st.selectbox("Hisse:", hisse_listesi, key="p_ek")
            p_maliyet = st.number_input("Alış Fiyatı (TL):", min_value=0.01, format="%.2f", key="p_mal")
            p_adet    = st.number_input("Adet:", min_value=1, step=1, key="p_adet")
            p_hedef   = st.number_input("Hedef Fiyat (TL):", min_value=0.0, format="%.2f", key="p_hedef")
            p_stop    = st.number_input("Stop-Loss (TL):", min_value=0.0, format="%.2f", key="p_stop")
            if st.button("Portföye Ekle", use_container_width=True):
                pkod = p_hisse.split(" - ")[0]
                yeni = pd.DataFrame([{'Hisse': pkod, 'Maliyet': p_maliyet, 'Adet': p_adet, 'Hedef': p_hedef, 'Stop': p_stop}])
                st.session_state.portfoy = pd.concat([st.session_state.portfoy, yeni], ignore_index=True)
                st.rerun()
    with p_kol2:
        if not st.session_state.portfoy.empty:
            t_maliyet, t_guncel = 0.0, 0.0; portfoy_data = []
            for idx, row in st.session_state.portfoy.iterrows():
                try:
                    g_veri = yf.download(f"{row['Hisse']}.IS", period="2d", auto_adjust=True, progress=False)
                    if not g_veri.empty:
                        g_fiyat = float(g_veri['Close'].iloc[-1].iloc[0]) if isinstance(g_veri.columns, pd.MultiIndex) else float(g_veri['Close'].iloc[-1])
                        g_prev  = float(g_veri['Close'].iloc[-2].iloc[0]) if (isinstance(g_veri.columns, pd.MultiIndex) and len(g_veri)>1) else (float(g_veri['Close'].iloc[-2]) if len(g_veri)>1 else g_fiyat)
                        m_t = row['Maliyet'] * row['Adet']; g_t = g_fiyat * row['Adet']
                        kz_tl = g_t - m_t; kz_yuzde = (kz_tl / m_t) * 100
                        gun_deg = ((g_fiyat - g_prev) / g_prev) * 100
                        t_maliyet += m_t; t_guncel += g_t
                        hedef_val = float(row.get('Hedef',0)); stop_val = float(row.get('Stop',0))
                        hedef_uyari = f'<span style="color:#00ff88;font-size:10px">🎯 HEDEF AŞILDI</span>' if hedef_val > 0 and g_fiyat >= hedef_val else (f'<span style="color:#4a6080;font-size:10px">🎯 Hedefe %{((hedef_val-g_fiyat)/g_fiyat)*100:.1f}</span>' if hedef_val > 0 else "")
                        stop_uyari = f'<span style="color:#ff4444;font-size:10px">🛑 STOP TETİKLENDİ</span>' if stop_val > 0 and g_fiyat <= stop_val else (f'<span style="color:#4a6080;font-size:10px">🛑 Stop: {stop_val:.2f}</span>' if stop_val > 0 else "")
                        portfoy_data.append({'idx':idx,'hisse':row['Hisse'],'maliyet':row['Maliyet'],'adet':row['Adet'],
                            'g_fiyat':g_fiyat,'m_toplam':m_t,'g_toplam':g_t,'kz_tl':kz_tl,'kz_yuzde':kz_yuzde,
                            'gun_deg':gun_deg,'hedef_uyari':hedef_uyari,'stop_uyari':stop_uyari})
                except: pass
            for p in portfoy_data:
                kz_renk = '#00ff88' if p['kz_tl'] >= 0 else '#ff4444'
                gun_renk = '#00ff88' if p['gun_deg'] >= 0 else '#ff4444'
                gun_yon  = '▲' if p['gun_deg'] >= 0 else '▼'
                r1, r2 = st.columns([5, 1])
                with r1:
                    st.markdown(f"""<div class="metric-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
                            <div><span style="font-family:JetBrains Mono,monospace;font-size:16px;font-weight:700;color:#00d4ff">{p['hisse']}</span>
                            <span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-left:8px">{p['adet']} adet @ {p['maliyet']:.2f}</span></div>
                            <div style="text-align:right"><div style="font-family:JetBrains Mono,monospace;font-size:14px;color:#e2e8f0;font-weight:600">{p['g_fiyat']:.2f} TL</div>
                            <div style="font-family:JetBrains Mono,monospace;font-size:11px;color:{gun_renk}">{gun_yon} {abs(p['gun_deg']):.2f}% bugün</div></div>
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;flex-wrap:wrap;gap:6px">
                            <div>{p['hedef_uyari']} {'&nbsp;&nbsp;' if p['hedef_uyari'] and p['stop_uyari'] else ''} {p['stop_uyari']}</div>
                            <div style="font-family:JetBrains Mono,monospace;font-size:14px;color:{kz_renk};font-weight:700">{p['kz_tl']:+,.2f} TL ({p['kz_yuzde']:+.2f}%)</div>
                        </div></div>""", unsafe_allow_html=True)
                with r2:
                    if st.button("🗑", key=f"del_{p['idx']}"):
                        st.session_state.portfoy = st.session_state.portfoy.drop(p['idx']).reset_index(drop=True)
                        st.rerun()
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            toplam_kz = t_guncel - t_maliyet
            toplam_kz_yuzde = ((t_guncel / t_maliyet) - 1) * 100 if t_maliyet > 0 else 0
            m1.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">TOPLAM MALİYET</div><div class="metric-value metric-neutral">{t_maliyet:,.0f} TL</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">GÜNCEL DEĞER</div><div class="metric-value">{t_guncel:,.0f} TL</div></div>', unsafe_allow_html=True)
            kz_cls = "metric-positive" if toplam_kz >= 0 else "metric-negative"
            m3.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">NET KAR / ZARAR</div><div class="metric-value {kz_cls}">{toplam_kz:+,.0f} TL</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">TOPLAM GETİRİ</div><div class="metric-value {"metric-positive" if toplam_kz_yuzde >= 0 else "metric-negative"}">{toplam_kz_yuzde:+.2f}%</div></div>', unsafe_allow_html=True)
            if len(portfoy_data) > 1:
                st.markdown('<div class="section-title" style="margin-top:20px">PORTFÖY DAĞILIMI</div>', unsafe_allow_html=True)
                fig_pie = go.Figure(go.Pie(labels=[p['hisse'] for p in portfoy_data], values=[p['g_toplam'] for p in portfoy_data], hole=0.5,
                    marker=dict(colors=['#00d4ff','#00ff88','#ff8800','#ff4444','#aa88ff','#ffdd00'], line=dict(color='#0a0a0f',width=2)),
                    textfont=dict(family='JetBrains Mono',size=11)))
                fig_pie.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                    height=280, showlegend=True, legend=dict(bgcolor='#0f1520',bordercolor='#1e2a3a',font=dict(family='JetBrains Mono',size=10)),
                    margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.markdown('<div class="ai-box" style="text-align:center;color:#4a6080;padding:60px"><div style="font-size:40px;margin-bottom:12px">💼</div><div style="font-size:15px">Portföyünüz boş.</div><div style="font-size:12px;margin-top:8px">Sol panelden hisse ekleyerek başlayın.</div></div>', unsafe_allow_html=True)

# ============================================================
# KARŞILAŞTIRMA (Ayrı bölüm — opsiyonel sidebar ile)
# ============================================================
with st.expander("⚖ Performans Karşılaştırması", expanded=False):
    indir_list = [f"{t_kod}.IS", "USDTRY=X"]
    if "Altın (TL)"  in kiyas_secenek: indir_list.append("GC=F")
    if "Gümüş (TL)" in kiyas_secenek: indir_list.append("SI=F")

    @st.cache_data(ttl=300)
    def indir_coklu(tickers_tuple, period):
        try:
            data = yf.download(list(tickers_tuple), period=period, auto_adjust=True, progress=False)
            if data.empty: return None
            return data['Close'].ffill() if isinstance(data.columns, pd.MultiIndex) else data
        except: return None

    veriler = indir_coklu(tuple(sorted(set(indir_list))), secilen_periyot)
    if veriler is not None and f"{t_kod}.IS" in veriler.columns:
        veriler = veriler.ffill().dropna()
        fig_k = go.Figure()
        h_s = veriler[f"{t_kod}.IS"]; norm = (h_s / h_s.iloc[0]) * 100
        fig_k.add_trace(go.Scatter(x=h_s.index, y=norm, name=t_kod, line=dict(color='#00d4ff', width=2.5)))
        kur = veriler.get("USDTRY=X", pd.Series(dtype=float))
        if "Altın (TL)" in kiyas_secenek and "GC=F" in veriler.columns and not kur.empty:
            a_tl = veriler["GC=F"] * kur; a_norm = (a_tl / a_tl.iloc[0]) * 100
            fig_k.add_trace(go.Scatter(x=a_tl.index, y=a_norm, name="Altın (TL)", line=dict(color='#ffd700', width=2)))
        if "Gümüş (TL)" in kiyas_secenek and "SI=F" in veriler.columns and not kur.empty:
            g_tl = veriler["SI=F"] * kur; g_norm = (g_tl / g_tl.iloc[0]) * 100
            fig_k.add_trace(go.Scatter(x=g_tl.index, y=g_norm, name="Gümüş (TL)", line=dict(color='#c0c0c0', width=2)))
        if "Dolar/TL" in kiyas_secenek and not kur.empty:
            k_norm = (kur / kur.iloc[0]) * 100
            fig_k.add_trace(go.Scatter(x=kur.index, y=k_norm, name="Dolar/TL", line=dict(color='#88ff88', width=2)))
        fig_k.update_layout(title=f"100 TL Yatırımın Performansı — {t_sure_etiket}", template="plotly_dark",
            plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f', yaxis_title="Değer (TL)", height=400,
            font=dict(family='JetBrains Mono', color='#8899aa'), margin=dict(l=10,r=10,t=40,b=10))
        fig_k.update_xaxes(gridcolor='#1e2a3a'); fig_k.update_yaxes(gridcolor='#1e2a3a')
        st.plotly_chart(fig_k, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="background:#0f0f1a;border:1px solid #1e2a3a;border-left:3px solid #ffaa00;
            border-radius:8px;padding:16px 20px;margin-bottom:12px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#ffaa00;
                letter-spacing:2px;margin-bottom:8px">⚠ YASAL UYARI / SORUMLULUK REDDİ</div>
    <div style="font-size:12px;color:#6a7d90;line-height:1.8">
        Bu uygulama <b style="color:#8899aa">yalnızca bilgilendirme amaçlıdır</b> ve
        <b style="color:#8899aa">yatırım tavsiyesi niteliği taşımamaktadır.</b>
        Veriler Yahoo Finance üzerinden alınmakta olup gecikmeli olabilir.
        Yatırım kararlarınızı vermeden önce lisanslı bir yatırım danışmanına başvurunuz.
    </div>
</div>
<div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:10px;color:#2a3a4a;padding:8px">
    BIST TERMINAL PRO &nbsp;•&nbsp; Geliştirici: Enes Boz &nbsp;•&nbsp; """ + str(datetime.now().year) + """ &nbsp;•&nbsp; Veriler Yahoo Finance
</div>
""", unsafe_allow_html=True)
