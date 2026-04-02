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

/* Ana arka plan */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0f !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background-color: #0f0f1a !important;
    border-right: 1px solid #1e2a3a !important;
}

/* Header */
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

/* Ticker bandı */
.ticker-bar {
    background: #050510;
    border: 1px solid #1e2a3a;
    border-radius: 6px;
    padding: 8px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    margin-bottom: 16px;
    overflow: hidden;
    white-space: nowrap;
}

/* Metrik kartları */
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

/* AI Analiz kutusu */
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

/* Haber kartları */
.news-card {
    background: #0f1520;
    border: 1px solid #1e2a3a;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 6px 0;
    cursor: pointer;
    transition: all 0.2s;
}
.news-card:hover {
    border-color: #00d4ff44;
    background: #141e2e;
}
.news-title {
    font-size: 13px;
    font-weight: 500;
    color: #c8d8e8;
    margin-bottom: 4px;
}
.news-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4a6080;
}
.news-positive { border-left: 3px solid #00ff88; }
.news-negative { border-left: 3px solid #ff4444; }
.news-neutral  { border-left: 3px solid #888; }

/* Alarm kutusu */
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

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* İndikatör renkleri */
.ind-buy  { color: #00ff88; font-weight: 700; }
.ind-sell { color: #ff4444; font-weight: 700; }
.ind-hold { color: #ffaa00; font-weight: 700; }

/* Tab stili */
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

/* Selectbox / Input */
.stSelectbox > div > div, .stTextInput > div > div {
    background-color: #0f1520 !important;
    border-color: #1e2a3a !important;
    color: #e2e8f0 !important;
}

/* Genel buton */
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

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 2px; }

/* Divider */
hr { border-color: #1e2a3a !important; }

/* Section başlığı */
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

/* Portföy satırı */
.portfoy-row {
    display: flex;
    align-items: center;
    background: #0f1520;
    border: 1px solid #1e2a3a;
    border-radius: 6px;
    padding: 10px 16px;
    margin: 4px 0;
    transition: border-color 0.2s;
}
.portfoy-row:hover { border-color: #00d4ff33; }

/* Sinyal badge */
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
</style>
""", unsafe_allow_html=True)

# ============================================================
# BIST 100 LİSTESİ
# ============================================================
# ============================================================
# TÜM BIST HİSSELERİ (Dinamik + Geniş Statik Yedek)
# ============================================================

# Geniş statik liste — yedek olarak kullanılır
BIST_STATIK = {
    # BIST 100
    "AEFES":"Anadolu Efes","AGHOL":"Anadolu Grubu Holding","AKBNK":"Akbank","AKCNS":"Akçansa",
    "AKFGY":"Akfen GYO","AKSA":"Aksa","AKSEN":"Aksa Enerji","ALARK":"Alarko Holding",
    "ALBRK":"Albaraka Türk","ALFAS":"Alfa Solar Enerji","ARCLK":"Arçelik","ASELS":"Aselsan",
    "ASTOR":"Astor Enerji","ASUZU":"Anadolu Isuzu","AYDEM":"Aydem Enerji","BAGFS":"Bagfaş",
    "BERA":"Bera Holding","BIENY":"Bien Yapı Ürünleri","BIMAS":"Bim Mağazalar","BRSAN":"Borusan Boru",
    "BRYAT":"Borusan Yatırım","BUCIM":"Bursa Çimento","CANTE":"Çan2 Termik","CCOLA":"Coca-Cola İçecek",
    "CIMSA":"Çimsa","CWENE":"Cw Enerji","DOAS":"Doğuş Otomotiv","DOHOL":"Doğan Holding",
    "EGEEN":"Ege Endüstri","EKGYO":"Emlak Konut GYO","ENJSA":"Enerjisa Enerji","ENKAI":"Enka İnşaat",
    "EREGL":"Ereğli Demir Çelik","EUPWR":"Europower Enerji","FROTO":"Ford Otosan","GARAN":"Garanti Bankası",
    "GESAN":"Girişim Elektrik","GUBRF":"Gübre Fabrikaları","GWIND":"Galata Wind","HALKB":"Halkbank",
    "HEKTS":"Hektaş","IPEKE":"İpek Doğal Enerji","ISCTR":"İş Bankası (C)","ISDMR":"İskenderun Demir Çelik",
    "ISGYO":"İş GYO","ISMEN":"İş Yatırım","IZENR":"İzdemir Enerji","KAYSE":"Kayseri Şeker",
    "KCHOL":"Koç Holding","KENT":"Kent Gıda","KONTR":"Kontrolmatik Teknoloji","KORDS":"Kordsa",
    "KOZAA":"Koza Madencilik","KOZAL":"Koza Altın","KRDMD":"Kardemir (D)","MAVI":"Mavi Giyim",
    "MGROS":"Migros","MIATK":"Mia Teknoloji","ODAS":"Odaş Elektrik","OTKAR":"Otokar",
    "OYAKC":"Oyak Çimento","PENTA":"Penta Teknoloji","PETKM":"Petkim","PGSUS":"Pegasus",
    "QUAGR":"Qua Granite","SAHOL":"Sabancı Holding","SASA":"Sasa Polyester","SAYAS":"Say Yenilenebilir",
    "SDTTR":"Sdt Uzay Ve Savunma","SISE":"Şişecam","SKBNK":"Şekerbank","SMRTG":"Smart Güneş",
    "SOKM":"Şok Marketler","TARKM":"Tarkim Bitki Koruma","TAVHL":"Tav Havalimanları","TCELL":"Turkcell",
    "THYAO":"Türk Hava Yolları","TKFEN":"Tekfen Holding","TOASO":"Tofaş Oto.","TSKB":"Tskb",
    "TTKOM":"Türk Telekom","TTRAK":"Türk Traktör","TUPRS":"Tüpraş","TURSG":"Türkiye Sigorta",
    "ULKER":"Ülker Bisküvi","VAKBN":"Vakıfbank","VESBE":"Vestel Beyaz Eşya","VESTL":"Vestel",
    "YEOTK":"Yeo Teknoloji","YKBNK":"Yapı Kredi Bankası","YYLGD":"Yaylatepe Gıda","ZOREN":"Zorlu Enerji",
    # BIST 50 / Diğer popüler
    "ADEL":"Adel Kalemcilik","ADESE":"Adese AVM","AKMGY":"Akiş GYO","AKLEASE":"Ak Finansal Kiralama",
    "AKGRT":"Aksigorta","ANACM":"Anadolu Cam","ARC":"Ar Çelik","ARSAN":"Arsan Tekstil",
    "ATEKS":"Altın Tekstil","ATPET":"Atlantis Petrol","AVGYO":"Avrasya GYO","AVHOL":"Avrasya Holding",
    "AYEN":"Ayen Enerji","AZGYO":"Ağaoğlu GYO","BAKAB":"Bak Ambalaj","BANVT":"Banvit",
    "BFREN":"Bosch Fren","BIOEN":"Biotrend Enerji","BIZIM":"Bizim Toptan","BNTAS":"Bntaş Ambalaj",
    "BOBET":"Boğaziçi Beton","BOSSA":"Bossa Tic. ve San.","BRKO":"Burçelik Kablo","BTCIM":"Batıçim",
    "BURCE":"Burçelik","BURVA":"Bursa Bulut Yatırım","BVSAN":"Burçelik Vana","CEMAS":"Çemaş Döküm",
    "CEMTS":"Çemtaş","CLEBI":"Çelebi Hava Servisi","CMBTN":"Çimbeton","CMENT":"Çimentaş",
    "DAGHL":"Doğan Holding","DAGI":"Dagi Giyim","DARDL":"Dardanel Önentaş","DENGE":"Denge Yatırım",
    "DENIZ":"Denizbank (Hisse Yok-örnek)","DERIM":"Derimod","DESA":"Desa Deri","DEVA":"Deva Holding",
    "DGATE":"Datagate Bilgisayar","DGNMO":"Doğan Müzik","DGZTE":"Doğan Gazetecilik","DIRIT":"Diriteks",
    "DITAS":"Ditaş Doğan","DJIST":"Dow Jones İst.","DMRGD":"Demir-Girişim","DNISI":"Deniz Gayrimenkul",
    "DOKTA":"Döktaş","DURDO":"Durdökmez","DYOBY":"Dyo Boya","DZGYO":"Deniz GYO",
    "ECILC":"Eczacıbaşı İlaç","ECZYT":"Eczacıbaşı Yatırım","EGPRO":"Ege Profil","EGSER":"Ege Seramik",
    "EMKEL":"Emkel Elektrik","EMNIS":"Eminiş Ambalaj","ERBOS":"Erbosan","ERCB":"Erce Boya",
    "ERSU":"Ersu Meyve","ESCOM":"Escort Teknoloji","ESEMS":"Es-Em Elektrik","ESEN":"Esen Tarım",
    "ESGYO":"Esenyurt GYO","ETILR":"Etibank Altın","ETYAT":"Etkin Yatırım","EUHOL":"Eurohold",
    "EUKYO":"Euromoda Konfeksiyon","EUREN":"Euro Yenilenebilir","FENER":"Fenerbahçe","FLAP":"Flap Kongre",
    "FMIZP":"F/M İzmir","FONET":"Fonet Bilgi","FORMT":"Formteks","FORTE":"Forte Bilişim",
    "FRIGO":"Frigo-Pak","FZLGY":"Fazilet GYO","GARAN":"Garanti Bankası","GARFA":"Garanti Faktoring",
    "GEDIK":"Gedik Yatırım","GEDZA":"Gediz Ambalaj","GEMAS":"Gemsan Elektrik","GENIL":"Genel Metal",
    "GENTS":"Gentaş","GLBMD":"Global Menkul Değerler","GLRYH":"Glory Giyim","GLYHO":"Global Yatırım Holding",
    "GOKNR":"Göknel Enerji","GOLTS":"Göltaş Çimento","GOODY":"Goodyear","GOZDE":"Gözde Girişim",
    "GSDDE":"GSD Denizcilik","GSDHO":"GSD Holding","GSRAY":"Galatasaray","GUBRF":"Gübre Fabrikaları",
    "GUNDG":"Güneydoğu Turizm","HDFGS":"Hedef Girişim","HEDEF":"Hedef Menkul","HILAL":"Hilal Madencilik",
    "HTTBT":"Hat Turizm","HUNER":"Hünkar Enerji","ICBCT":"ICBC Turkey","IDEAS":"İdeas Mühendislik",
    "IDGYO":"İdealist GYO","IEYHO":"İEYHO","IHAAS":"İhlas Holding","IHEVA":"İhlas Ev Aletleri",
    "IHGZT":"İhlas Gazetecilik","IHLGM":"İhlas Madencilik","IHYAY":"İhlas Yayın","INDES":"İndeks Bilgisayar",
    "INFO":"İnfo Yatırım","INTEM":"İntema İnşaat","INVEO":"Inveo Varlık Yönetimi","IPEKE":"İpek Enerji",
    "ISATR":"İş Gayrimenkul","ISBTR":"İş Bankası B","ISFIN":"İş Finansal Kiralama","ISGSY":"İş GY Ortaklığı",
    "ISKPL":"İskenderun Pelet","ITTFH":"İttifak Holding","IZFAS":"İzmir Fuar","IZOCM":"İzoçam",
    "JANTS":"Jantsa Jant","KAPLM":"Kaplamin Ambalaj","KAREL":"Karel Elektronik","KARSN":"Karsan",
    "KATMR":"Katmerciler","KCAER":"KCA Enerji","KERVN":"Kervan Gıda","KGYO":"Kiler GYO",
    "KLGYO":"Kiler GYO","KLKIM":"Kalekim","KLNMA":"Kalkınma Yatırım","KLSYN":"Kalısın Yapı",
    "KNFRT":"Konfrut Gıda","KONYA":"Konya Çimento","KORDS":"Kordsa","KPHOL":"KP Holding",
    "KRDMA":"Kardemir A","KRDMB":"Kardemir B","KRPLS":"Karbosan","KRSAN":"Karsan Otomotiv",
    "KTLEV":"Katılım Emeklilik","KUTPO":"Kütahya Porselen","LIDER":"Lider Faktoring","LIDFA":"Lidya Madencilik",
    "LINK":"Link Bilgisayar","LKMNH":"Lokman Hekim","LOGO":"Logo Yazılım","LRSHO":"Lüks Kadife",
    "LUKSK":"Lüks Kadife","MAALT":"Maalt","MACKO":"Mackolik","MAKIM":"Makina Takım",
    "MAKTK":"Maktek","MANAS":"Manas Enerji","MARBL":"Marble","MARTI":"Martı Otel",
    "MAVI":"Mavi Giyim","MEDTR":"Meditera Tıp","MEGAP":"Mega Polietilen","MEKAG":"Mekanik Enerji",
    "MERKO":"Merko Gıda","METRO":"Metro Holding","METUR":"Metur Turizm","MIPAZ":"Mipaş AVM",
    "MNDRS":"Menderes Tekstil","MNDTR":"Menderes Turizm","MOBTL":"Mobtelecom","MOGAN":"Mogaz Petrol",
    "MSGYO":"MS GYO","MTRKS":"Matriks Bilgi","MZHLD":"Mozaik Holding","NATEN":"Naturel Enerji",
    "NETAS":"Netaş Telekomünikasyon","NIBAS":"Niğbaş Niğde","NILYT":"Nil Yatırım","NRBNK":"NR Sigorta",
    "NTHOL":"Net Holding","NTTUR":"Net Turizm","NUGYO":"Nurol GYO","NUHCM":"Nuh Çimento",
    "OBASE":"Obase","OCAS":"Otokar","OFSYM":"Ofis Makineleri","ONCSM":"Oncosim",
    "ONRYT":"Onur-YT","ORCAY":"Orca Yatırım","ORGE":"Orge Enerji","ORMA":"Orma Orman Ürünleri",
    "OSMEN":"Osmaniye Elektrik","OSTIM":"Ostim Endüstri","OYLUM":"Oylum Tarım","OZGYO":"Özak GYO",
    "OZKGY":"Özak GYO","OZRDN":"Özderici Holding","PAGYO":"Pasha GYO","PAMEL":"Pamel Yenilenebilir",
    "PAPIL":"Papilion","PARSN":"Parsan","PCILT":"Petro Çimento İnşaat","PDMR":"Podravka",
    "PEGYO":"Pera GYO","PENGD":"Penguen Gıda","PENTA":"Penta Teknoloji","PERCY":"Percy Jackson (örnek)",
    "PETKM":"Petkim","PETUN":"Pınar Et ve Un","PINSU":"Pınar Su","PKART":"Plastkart",
    "PLTUR":"Palmiye Turizm","PNLSN":"Panelsan","POLHO":"Polisan Holding","POLTK":"Politeknik Metal",
    "PRDGS":"Perdegüneş","PRZMA":"Prizma Pres","PSGYO":"Panora GYO","PSGRS":"Pasaport GYO",
    "RDFGY":"Roda GYO","RGYAS":"Reysaş GYO","RKTIN":"Rektim","RODRG":"Rodrigo Tekstil",
    "ROYAL":"Royal Halı","RTALB":"Rota Alüminyum","RUBNS":"Rubenis Tekstil","RYGYO":"Raysal GYO",
    "SAMAT":"Samatya Cam","SANFM":"Sanifoam","SARTN":"Sarıtaş Altın","SBTAH":"Sebahat Turizm",
    "SELEC":"Selçuk Ecza","SELGD":"Selçuk Gıda","SELVA":"Selva Gıda","SEYKM":"Seyitler Kimya",
    "SILVR":"Silver Yatırım","SNGYO":"Sinpaş GYO","SNKRN":"Sanko Enerji","SNPAM":"Sanko Pazarlama",
    "SODSN":"Soda Sanayii","SOLAR":"Solar Yatırım","SONME":"Sönmez Pamuklu","SRVGY":"Servet GYO",
    "SUWEN":"Süwen Tekstil","TABGD":"Taba Gıda","TBORG":"Türk Tuborg","TCELL":"Turkcell",
    "TDGYO":"Trend GYO","TEKTU":"Tektur Turizm","TMPOL":"Tem Polimer","TMSN":"Timsan",
    "TNZTP":"Tüneztepe","TOASO":"Tofaş","TRCAS":"Türkiye Çelik Cas.","TRGYO":"Torunlar GYO",
    "TRILC":"Trilogi","TRNSK":"Tureks Saraciye","TRPAP":"Türk Prysmian Kablo","TSGYO":"Türkiye Sigorta GYO",
    "TSPOR":"Trabzonspor","TTRAK":"Türk Traktör","TUCLK":"Tuçlik Metalurji","TUKAS":"Tukaş",
    "TULFA":"Tülfar","TURGG":"Türk Havacılık","TURSG":"Türkiye Sigorta","TUYAP":"Tüyap",
    "UCAK":"Uçak Servisi","ULUFA":"Ulu Finans","ULUSE":"Ulusoy Elektrik","ULUUN":"Ulusoy Un",
    "UMPAS":"Umpaş Holding","UNLU":"Ünlü Yatırım","USAK":"Uşak Seramik","USDTR":"USD Tracker",
    "VAKFN":"Vakıf Finansal","VAKGY":"Vakıf GYO","VAKKO":"Vakko Tekstil","VANGD":"Van Gölü Gıda",
    "VBTYZ":"VBT Yazılım","VERUS":"Verusa Holding","VKFYO":"Vakıf FYO","VKGYO":"Vakıf GYO",
    "YBTAS":"Yıbıtaş","YESIL":"Yeşil Gayrimenkul","YGGYO":"Yeni Gimat GYO","YGYO":"Yeni GYO",
    "YLGYO":"Yıldız GYO","YLTKS":"Yıldız Teknik","YNSYT":"Yensayt","YONGA":"Yonga Mobilya",
    "YUNSA":"Yünsa","ZEDUR":"Zedur Enerji","ZRGYO":"Ziraat GYO","ZSEGY":"ZSE Güneş Enerji",
}

@st.cache_data(ttl=86400)
def bist_hisse_listesi_getir():
    """Wikipedia'dan tüm BIST hisselerini çekmeye çalış, başarısız olursa statik listeyi döndür."""
    try:
        url = "https://tr.wikipedia.org/wiki/BIST_100_Endeksi"
        resp = requests.get(url, timeout=8,
                            headers={"User-Agent": "Mozilla/5.0"})
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
                    # Statik listeyle birleştir
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
    # Aynı alarm için tekrar tekrar mail gitmesini önler: {alarm_key: timestamp}
    st.session_state.mail_gonderildi = {}

# ============================================================
# MAİL GÖNDERME FONKSİYONU (Gmail SMTP)
# ============================================================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def alarm_maili_gonder(alici_mail, hisse, tur, alarm_fiyat, gercek_fiyat):
    """Streamlit Secrets'tan Gmail bilgilerini alarak alarm maili gönderir."""
    try:
        gonderen  = st.secrets["GMAIL_USER"]
        sifre     = st.secrets["GMAIL_APP_PASSWORD"]
    except Exception:
        return False, "Secrets bulunamadı (GMAIL_USER / GMAIL_APP_PASSWORD)"

    yon_emoji = "🚀" if tur == "Üstüne Çıkarsa" else "📉"
    konu = f"{yon_emoji} BIST Alarm: {hisse} fiyat hedefine ulaştı!"

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#0a0a0f;color:#e2e8f0;padding:24px">
      <div style="max-width:480px;margin:auto;background:#0f1520;border:1px solid #1e2a3a;border-radius:10px;padding:28px">
        <div style="font-size:22px;font-weight:700;color:#00d4ff;margin-bottom:4px">◈ BIST Terminal Pro</div>
        <div style="font-size:12px;color:#4a6080;margin-bottom:24px">Otomatik Fiyat Alarmı</div>
        <div style="background:#1a1a2e;border-left:4px solid {'#00ff88' if tur == 'Üstüne Çıkarsa' else '#ff4444'};
                    border-radius:6px;padding:16px;margin-bottom:20px">
          <div style="font-size:28px;font-weight:700;color:{'#00ff88' if tur == 'Üstüne Çıkarsa' else '#ff4444'}">
            {yon_emoji} {hisse}
          </div>
          <div style="font-size:14px;color:#8899aa;margin-top:6px">{tur} alarmı tetiklendi</div>
        </div>
        <table style="width:100%;border-collapse:collapse">
          <tr>
            <td style="padding:8px 0;color:#4a6080;font-size:13px">Alarm Fiyatı</td>
            <td style="padding:8px 0;color:#e2e8f0;font-weight:600;text-align:right">{alarm_fiyat:.2f} TL</td>
          </tr>
          <tr style="border-top:1px solid #1e2a3a">
            <td style="padding:8px 0;color:#4a6080;font-size:13px">Gerçekleşen Fiyat</td>
            <td style="padding:8px 0;color:#00d4ff;font-weight:700;text-align:right">{gercek_fiyat:.2f} TL</td>
          </tr>
          <tr style="border-top:1px solid #1e2a3a">
            <td style="padding:8px 0;color:#4a6080;font-size:13px">Tarih / Saat</td>
            <td style="padding:8px 0;color:#8899aa;font-size:12px;text-align:right">{datetime.now().strftime('%d.%m.%Y %H:%M')}</td>
          </tr>
        </table>
        <div style="margin-top:24px;padding:12px;background:#0a0a0f;border-radius:6px;
                    font-size:11px;color:#2a3a4a;line-height:1.6">
          Bu mail BIST Terminal Pro tarafından otomatik gönderilmiştir.<br>
          Bu bir yatırım tavsiyesi değildir. Tüm yatırım kararları kullanıcının sorumluluğundadır.
        </div>
      </div>
    </body></html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = konu
        msg["From"]    = gonderen
        msg["To"]      = alici_mail
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gonderen, sifre)
            server.sendmail(gonderen, alici_mail, msg.as_string())
        return True, "Mail gönderildi"
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail kimlik doğrulama hatası — App Password doğru mu?"
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

@st.cache_data(ttl=300)
def fiyat_serisi(ticker, period="1y", interval="1d"):
    data = veri_indir(ticker, period, interval)
    if data is None: return None
    if isinstance(data.columns, pd.MultiIndex):
        return data['Close'][ticker] if ticker in data['Close'].columns else None
    return data['Close']

# --- TEKNİK İNDİKATÖRLER ---
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
    histogram = macd - signal
    return macd, signal, histogram

def hesapla_bollinger(seri, periyot=20, std=2):
    ort = seri.rolling(periyot).mean()
    standart = seri.rolling(periyot).std()
    ust = ort + std * standart
    alt = ort - std * standart
    return ust, ort, alt

def hesapla_stochastic(data, k_periyot=14, d_periyot=3):
    low_min  = data['Low'].rolling(k_periyot).min()
    high_max = data['High'].rolling(k_periyot).max()
    k = 100 * (data['Close'] - low_min) / (high_max - low_min)
    d = k.rolling(d_periyot).mean()
    return k, d

def hesapla_atr(data, periyot=14):
    high = data['High']
    low  = data['Low']
    close_prev = data['Close'].shift(1)
    tr = pd.concat([high - low,
                    (high - close_prev).abs(),
                    (low  - close_prev).abs()], axis=1).max(axis=1)
    return tr.rolling(periyot).mean()

def teknik_sinyal_hesapla(seri, data):
    sinyaller = {}
    skor = 0

    try:
        rsi = hesapla_rsi(seri).iloc[-1]
        sinyaller['RSI'] = {
            'deger': f"{rsi:.1f}",
            'sinyal': 'AL' if rsi < 30 else ('SAT' if rsi > 70 else 'BEKLE'),
            'renk': '#00ff88' if rsi < 30 else ('#ff4444' if rsi > 70 else '#ffaa00')
        }
        skor += 1 if rsi < 30 else (-1 if rsi > 70 else 0)
    except: pass

    try:
        macd, signal, _ = hesapla_macd(seri)
        macd_son, signal_son = macd.iloc[-1], signal.iloc[-1]
        macd_prev, signal_prev = macd.iloc[-2], signal.iloc[-2]
        kesisim = (macd_son > signal_son) and (macd_prev <= signal_prev)
        sinyaller['MACD'] = {
            'deger': f"{macd_son:.3f}",
            'sinyal': 'AL' if kesisim else ('SAT' if macd_son < signal_son else 'BEKLE'),
            'renk': '#00ff88' if kesisim else ('#ff4444' if macd_son < signal_son else '#ffaa00')
        }
        skor += 1 if macd_son > signal_son else -1
    except: pass

    try:
        ust, ort, alt = hesapla_bollinger(seri)
        fiyat = seri.iloc[-1]
        bb_sinyal = 'AL' if fiyat < alt.iloc[-1] else ('SAT' if fiyat > ust.iloc[-1] else 'BEKLE')
        sinyaller['Bollinger'] = {
            'deger': f"Ort:{ort.iloc[-1]:.2f}",
            'sinyal': bb_sinyal,
            'renk': '#00ff88' if bb_sinyal == 'AL' else ('#ff4444' if bb_sinyal == 'SAT' else '#ffaa00')
        }
        skor += 1 if bb_sinyal == 'AL' else (-1 if bb_sinyal == 'SAT' else 0)
    except: pass

    try:
        ma20  = seri.rolling(20).mean().iloc[-1]
        ma50  = seri.rolling(50).mean().iloc[-1]
        ma200 = seri.rolling(200).mean().iloc[-1]
        fiyat = seri.iloc[-1]
        sinyaller['MA Trendi'] = {
            'deger': f"MA50:{ma50:.2f}",
            'sinyal': 'AL' if fiyat > ma20 > ma50 else ('SAT' if fiyat < ma20 < ma50 else 'BEKLE'),
            'renk': '#00ff88' if fiyat > ma20 > ma50 else ('#ff4444' if fiyat < ma20 < ma50 else '#ffaa00')
        }
        skor += 1 if fiyat > ma50 else -1
    except: pass

    try:
        if data is not None:
            k, d = hesapla_stochastic(data)
            k_son, d_son = k.iloc[-1], d.iloc[-1]
            sinyaller['Stochastic'] = {
                'deger': f"K:{k_son:.1f} D:{d_son:.1f}",
                'sinyal': 'AL' if k_son < 20 else ('SAT' if k_son > 80 else 'BEKLE'),
                'renk': '#00ff88' if k_son < 20 else ('#ff4444' if k_son > 80 else '#ffaa00')
            }
            skor += 1 if k_son < 20 else (-1 if k_son > 80 else 0)
    except: pass

    genel = 'GÜÇLÜ AL' if skor >= 3 else ('AL' if skor >= 1 else ('GÜÇLÜ SAT' if skor <= -3 else ('SAT' if skor <= -1 else 'BEKLE')))
    return sinyaller, skor, genel


# ============================================================
# AI ANALİZ FONKSİYONU (Groq API)
# ============================================================
def ai_analiz_yap(kod, ad, fiyat, degisim, rsi, genel_sinyal, hacim_ort, seri):
    cache_key = f"{kod}_{datetime.now().strftime('%Y%m%d%H')}"
    if cache_key in st.session_state.ai_cache:
        return st.session_state.ai_cache[cache_key]

    try:
        groq_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return "⚠ Groq API key bulunamadı. Streamlit Cloud → Settings → Secrets bölümüne GROQ_API_KEY ekleyin."

    try:
        son_7_gun  = seri.iloc[-7:].pct_change().dropna() * 100
        trend_ozet = f"{son_7_gun.mean():.2f}% ort günlük değişim"
        yuksek_52h = seri.rolling(252).max().iloc[-1]
        dusuk_52h  = seri.rolling(252).min().iloc[-1]

        prompt = f"""Sen deneyimli bir BIST analistisin. Aşağıdaki verilere göre {kod} ({ad}) hissesi için kısa ve net bir piyasa analizi yaz.

Güncel Fiyat: {fiyat:.2f} TL
Günlük Değişim: {degisim:+.2f}%
RSI (14): {rsi:.1f}
Genel Teknik Sinyal: {genel_sinyal}
Son 7 Gün Trend: {trend_ozet}
52 Hafta Yüksek: {yuksek_52h:.2f} TL
52 Hafta Düşük: {dusuk_52h:.2f} TL

Analizi şu başlıklar altında yaz (her biri 1-2 cümle, toplam max 150 kelime):
1. Teknik Görünüm
2. Kısa Vadeli Beklenti
3. Risk Faktörleri
4. Sonuç ve Öneri

Türkçe yaz, profesyonel ve objektif ol. Kesin garanti verme, olasılık dilini kullan."""

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {groq_key}"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 1024,
                "temperature": 0.7,
                "messages": [
                    {"role": "system", "content": "Sen profesyonel bir Türk borsa analistisin. Türkçe, net ve objektif analiz yaparsın."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            st.session_state.ai_cache[cache_key] = text
            return text
        else:
            return f"⚠ Groq API hatası: {response.status_code} — {response.text[:200]}"

    except Exception as e:
        return f"⚠ Bağlantı hatası: {str(e)}"


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
        st.session_state.alarmlar.append({
            'hisse'    : alarm_kod,
            'tur'      : alarm_tur,
            'fiyat'    : alarm_fiyat,
            'mail'     : alarm_mail.strip(),
            'aktif'    : True,
            'eklenme'  : datetime.now().strftime('%d.%m %H:%M')
        })
        st.success("✅ Alarm eklendi!")

    # ---- Alarm kontrolü ----
    if st.session_state.alarmlar:
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;margin:8px 0 4px">AKTİF ALARMLAR</div>', unsafe_allow_html=True)
        silinecek = []
        for i, alarm in enumerate(st.session_state.alarmlar):
            try:
                d = yf.download(f"{alarm['hisse']}.IS", period="1d", progress=False)
                if d.empty:
                    continue
                if isinstance(d.columns, pd.MultiIndex):
                    g_fiyat = float(d['Close'].iloc[-1].iloc[0])
                else:
                    g_fiyat = float(d['Close'].iloc[-1])

                tetiklendi = (
                    (alarm['tur'] == "Üstüne Çıkarsa" and g_fiyat >= alarm['fiyat']) or
                    (alarm['tur'] == "Altına Düşerse"  and g_fiyat <= alarm['fiyat'])
                )

                # Mail gönder (aynı alarm için günde 1 kez)
                if tetiklendi and alarm.get('mail'):
                    mail_key = f"{alarm['hisse']}_{alarm['fiyat']}_{alarm['tur']}"
                    son_gonderim = st.session_state.mail_gonderildi.get(mail_key)
                    simdi = datetime.now()
                    gonder = (son_gonderim is None or
                              (simdi - son_gonderim).total_seconds() > 3600)
                    if gonder:
                        basari, mesaj = alarm_maili_gonder(
                            alarm['mail'], alarm['hisse'],
                            alarm['tur'], alarm['fiyat'], g_fiyat
                        )
                        if basari:
                            st.session_state.mail_gonderildi[mail_key] = simdi
                            st.toast(f"📧 {alarm['hisse']} alarmı {alarm['mail']} adresine gönderildi!", icon="✅")
                        else:
                            st.toast(f"⚠ Mail gönderilemedi: {mesaj}", icon="❌")

                # Görsel
                if tetiklendi:
                    st.markdown(f"""
                    <div class="alarm-triggered">
                        🚨 <b>{alarm['hisse']}</b> → {g_fiyat:.2f} TL<br>
                        <span style="font-size:10px">{alarm['tur']} {alarm['fiyat']:.2f} TL
                        {'• 📧 ' + alarm['mail'] if alarm.get('mail') else ''}</span>
                    </div>""", unsafe_allow_html=True)
                else:
                    pct = ((alarm['fiyat'] - g_fiyat) / g_fiyat) * 100
                    yon = "▲" if alarm['tur'] == "Üstüne Çıkarsa" else "▼"
                    st.markdown(f"""
                    <div class="alarm-active">
                        🔔 <b>{alarm['hisse']}</b> {yon} {alarm['fiyat']:.2f} TL<br>
                        <span style="font-size:10px">Şu an: {g_fiyat:.2f} TL &nbsp;•&nbsp; Fark: %{abs(pct):.1f}
                        {'&nbsp;•&nbsp; 📧' if alarm.get('mail') else ''}</span>
                    </div>""", unsafe_allow_html=True)

            except Exception:
                pass

            if st.button("✕ Sil", key=f"al_del_{i}", use_container_width=True):
                silinecek.append(i)

        for i in reversed(silinecek):
            st.session_state.alarmlar.pop(i)
        if silinecek:
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">⚖ KARŞILAŞTIRMA</div>', unsafe_allow_html=True)
    kiyas_secenek = st.multiselect("Ekle:", ["Altın (TL)", "Gümüş (TL)", "Dolar/TL", "Enflasyon"])


# ============================================================
# ANA PANEL - TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  TEKNİK ANALİZ",
    "🤖  AI RAPORU",
    "📰  HABERLER",
    "⚖   KARŞILAŞTIRMA",
    "💼  PORTFÖY"
])

# ============================================================
# TAB 1: TEKNİK ANALİZ
# ============================================================
with tab1:
    data_raw = veri_indir(f"{t_kod}.IS", secilen_periyot, secilen_aralik)

    if data_raw is not None and not data_raw.empty:
        # Seri hazırla
        if isinstance(data_raw.columns, pd.MultiIndex):
            close_col = data_raw['Close']
            if isinstance(close_col, pd.DataFrame):
                seri = close_col.iloc[:, 0]
            else:
                seri = close_col
        else:
            seri = data_raw['Close']

        seri = seri.dropna()

        fiyat_son  = float(seri.iloc[-1])
        fiyat_prev = float(seri.iloc[-2]) if len(seri) > 1 else fiyat_son
        degisim_yuzde = ((fiyat_son - fiyat_prev) / fiyat_prev) * 100

        # Hacim
        try:
            if isinstance(data_raw.columns, pd.MultiIndex):
                hacim = data_raw['Volume'].iloc[:, 0].mean()
            else:
                hacim = data_raw['Volume'].mean()
        except:
            hacim = 0

        # İndikatörler
        sinyaller, skor, genel_sinyal = teknik_sinyal_hesapla(seri, data_raw)
        rsi_val = hesapla_rsi(seri).iloc[-1] if len(seri) > 14 else 50.0

        # ÜST METRİK SATIRLARI
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        with mc1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">SON FİYAT</div>
                <div class="metric-value">{fiyat_son:.2f} <span style="font-size:12px;color:#4a6080">TL</span></div>
            </div>""", unsafe_allow_html=True)
        with mc2:
            renk = "metric-positive" if degisim_yuzde >= 0 else "metric-negative"
            yon = "▲" if degisim_yuzde >= 0 else "▼"
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">GÜNLÜK DEĞİŞİM</div>
                <div class="metric-value {renk}">{yon} {abs(degisim_yuzde):.2f}%</div>
            </div>""", unsafe_allow_html=True)
        with mc3:
            rsi_cls = "metric-positive" if rsi_val < 30 else ("metric-negative" if rsi_val > 70 else "metric-neutral")
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">RSI (14)</div>
                <div class="metric-value {rsi_cls}">{rsi_val:.1f}</div>
            </div>""", unsafe_allow_html=True)
        with mc4:
            sinyal_cls = "metric-positive" if "AL" in genel_sinyal else ("metric-negative" if "SAT" in genel_sinyal else "metric-neutral")
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">TEKNİK SİNYAL</div>
                <div class="metric-value {sinyal_cls}" style="font-size:16px">{genel_sinyal}</div>
            </div>""", unsafe_allow_html=True)
        with mc5:
            hacim_m = hacim / 1_000_000
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">ORT. HACİM</div>
                <div class="metric-value metric-neutral">{hacim_m:.1f}M</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # İNDİKATÖR SEÇİMİ
        ic1, ic2 = st.columns([3, 1])
        with ic2:
            goster_bb  = st.checkbox("Bollinger Bantları", value=True)
            goster_ma  = st.checkbox("Hareketli Ortalamalar", value=True)
            goster_vol = st.checkbox("Hacim", value=True)
            goster_rsi_chart  = st.checkbox("RSI Grafiği", value=True)
            goster_macd_chart = st.checkbox("MACD Grafiği", value=False)

        with ic1:
            # Subplot sayısını belirle
            rows = 1
            row_heights = [0.6]
            if goster_vol:         rows += 1; row_heights.append(0.15)
            if goster_rsi_chart:   rows += 1; row_heights.append(0.125)
            if goster_macd_chart:  rows += 1; row_heights.append(0.125)

            specs = [[{"secondary_y": False}]] * rows
            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                                vertical_spacing=0.03, row_heights=row_heights, specs=specs)

            cur_row = 1

            # Mum grafiği
            if isinstance(data_raw.columns, pd.MultiIndex):
                high_s = data_raw['High'].iloc[:, 0]
                low_s  = data_raw['Low'].iloc[:, 0]
                open_s = data_raw['Open'].iloc[:, 0]
            else:
                high_s = data_raw['High']
                low_s  = data_raw['Low']
                open_s = data_raw['Open']

            fig.add_trace(go.Candlestick(
                x=seri.index, open=open_s, high=high_s, low=low_s, close=seri,
                name=t_kod,
                increasing=dict(line=dict(color='#00ff88', width=1)),
                decreasing=dict(line=dict(color='#ff4444', width=1))
            ), row=cur_row, col=1)

            if goster_bb:
                ust, ort_bb, alt = hesapla_bollinger(seri)
                fig.add_trace(go.Scatter(x=seri.index, y=ust, line=dict(color='#4444ff', width=1, dash='dot'), name='BB Üst', showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=alt, line=dict(color='#4444ff', width=1, dash='dot'), name='BB Alt', fill='tonexty', fillcolor='rgba(68,68,255,0.05)', showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=ort_bb, line=dict(color='#8888ff', width=1), name='BB Orta', showlegend=False), row=cur_row, col=1)

            if goster_ma:
                for ma_p, renk_ma in [(20, '#ffaa00'), (50, '#ff6688'), (200, '#88aaff')]:
                    if len(seri) >= ma_p:
                        ma_seri = seri.rolling(ma_p).mean()
                        fig.add_trace(go.Scatter(x=seri.index, y=ma_seri, line=dict(color=renk_ma, width=1.5), name=f'MA{ma_p}'), row=cur_row, col=1)

            # Hacim
            if goster_vol:
                cur_row += 1
                try:
                    if isinstance(data_raw.columns, pd.MultiIndex):
                        vol_s = data_raw['Volume'].iloc[:, 0]
                    else:
                        vol_s = data_raw['Volume']
                    vol_colors = ['#00ff8888' if c >= o else '#ff444488' for c, o in zip(seri, open_s)]
                    fig.add_trace(go.Bar(x=seri.index, y=vol_s, name='Hacim', marker_color=vol_colors, showlegend=False), row=cur_row, col=1)
                    fig.update_yaxes(title_text="Hacim", row=cur_row, col=1, title_standoff=5)
                except:
                    pass

            # RSI Grafiği
            if goster_rsi_chart:
                cur_row += 1
                rsi_full = hesapla_rsi(seri)
                fig.add_trace(go.Scatter(x=seri.index, y=rsi_full, line=dict(color='#aa88ff', width=1.5), name='RSI'), row=cur_row, col=1)
                fig.add_hline(y=70, line=dict(color='#ff4444', width=1, dash='dot'), row=cur_row, col=1)
                fig.add_hline(y=30, line=dict(color='#00ff88', width=1, dash='dot'), row=cur_row, col=1)
                fig.update_yaxes(title_text="RSI", range=[0, 100], row=cur_row, col=1, title_standoff=5)

            # MACD Grafiği
            if goster_macd_chart:
                cur_row += 1
                macd, signal_line, histogram = hesapla_macd(seri)
                hist_colors = ['#00ff88' if v >= 0 else '#ff4444' for v in histogram]
                fig.add_trace(go.Bar(x=seri.index, y=histogram, name='MACD Hist', marker_color=hist_colors, showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=macd, line=dict(color='#00d4ff', width=1.5), name='MACD'), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=signal_line, line=dict(color='#ff8800', width=1.5), name='Signal'), row=cur_row, col=1)
                fig.update_yaxes(title_text="MACD", row=cur_row, col=1, title_standoff=5)

            fig.update_layout(
                title=f"{t_kod} — {t_ad} | {t_sure_etiket}",
                template="plotly_dark",
                plot_bgcolor='#0a0a0f',
                paper_bgcolor='#0a0a0f',
                xaxis_rangeslider_visible=False,
                legend=dict(bgcolor='#0f1520', bordercolor='#1e2a3a', font=dict(size=11, family='JetBrains Mono')),
                font=dict(family='JetBrains Mono', color='#8899aa'),
                height=600,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            fig.update_xaxes(gridcolor='#1e2a3a', linecolor='#1e2a3a')
            fig.update_yaxes(gridcolor='#1e2a3a', linecolor='#1e2a3a')
            st.plotly_chart(fig, use_container_width=True)

        # İNDİKATÖR SINYAL TABLOSU
        st.markdown('<div class="section-title">İNDİKATÖR SİNYALLERİ</div>', unsafe_allow_html=True)
        cols = st.columns(len(sinyaller))
        for i, (ind_ad, ind_data) in enumerate(sinyaller.items()):
            badge_cls = 'badge-buy' if ind_data['sinyal'] == 'AL' else ('badge-sell' if ind_data['sinyal'] == 'SAT' else 'badge-hold')
            cols[i].markdown(f"""
            <div class="metric-card" style="text-align:center">
                <div class="metric-label">{ind_ad}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#c8d8e8;margin:4px 0">{ind_data['deger']}</div>
                <span class="badge {badge_cls}">{ind_data['sinyal']}</span>
            </div>""", unsafe_allow_html=True)

    else:
        st.warning(f"⚠ {t_kod} için veri indirilemedi. Lütfen farklı bir periyot veya hisse seçin.")


# ============================================================
# TAB 2: AI RAPORU
# ============================================================
with tab2:
    st.markdown('<div class="section-title">🤖 YAPAY ZEKA ANALİZ RAPORU</div>', unsafe_allow_html=True)

    data_ai = veri_indir(f"{t_kod}.IS", "1y", "1d")

    if data_ai is not None and not data_ai.empty:
        if isinstance(data_ai.columns, pd.MultiIndex):
            seri_ai = data_ai['Close'].iloc[:, 0].dropna()
        else:
            seri_ai = data_ai['Close'].dropna()

        fiyat_ai   = float(seri_ai.iloc[-1])
        fiyat_prev_ai = float(seri_ai.iloc[-2]) if len(seri_ai) > 1 else fiyat_ai
        degisim_ai = ((fiyat_ai - fiyat_prev_ai) / fiyat_prev_ai) * 100
        rsi_ai     = hesapla_rsi(seri_ai).iloc[-1]
        _, _, gs_ai = teknik_sinyal_hesapla(seri_ai, data_ai)

        ai_kol1, ai_kol2 = st.columns([2, 1])

        with ai_kol2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">ANALİZ EDİLEN HİSSE</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:18px;color:#00d4ff;font-weight:700">{t_kod}</div>
                <div style="font-size:12px;color:#4a6080">{t_ad}</div>
            </div>
            <div class="metric-card" style="margin-top:8px">
                <div class="metric-label">GÜNCEL FİYAT</div>
                <div class="metric-value">{fiyat_ai:.2f} TL</div>
                <div style="font-size:12px;color:{'#00ff88' if degisim_ai >= 0 else '#ff4444'}">{'▲' if degisim_ai >= 0 else '▼'} {abs(degisim_ai):.2f}%</div>
            </div>
            <div class="metric-card" style="margin-top:8px">
                <div class="metric-label">TEKNİK SİNYAL</div>
                <div class="metric-value" style="font-size:16px;color:{'#00ff88' if 'AL' in gs_ai else ('#ff4444' if 'SAT' in gs_ai else '#ffaa00')}">{gs_ai}</div>
            </div>
            """, unsafe_allow_html=True)

        with ai_kol1:
            if st.button("🤖 AI Analizi Üret", use_container_width=True, key="ai_btn"):
                with st.spinner("Yapay zeka raporu hazırlanıyor..."):
                    sonuc = ai_analiz_yap(t_kod, t_ad, fiyat_ai, degisim_ai, rsi_ai, gs_ai, 0, seri_ai)
                    if sonuc:
                        st.session_state[f"ai_sonuc_{t_kod}"] = sonuc
                    else:
                        st.error("AI servisi şu an kullanılamıyor.")

            cache_key = f"ai_sonuc_{t_kod}"
            if cache_key in st.session_state:
                st.markdown(f"""
                <div class="ai-box">
                    <div class="ai-box-header">⬡ CLAUDE AI ANALİZİ • {t_kod} • {datetime.now().strftime('%d.%m.%Y')}</div>
                    {st.session_state[cache_key].replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="ai-box" style="text-align:center;color:#4a6080;padding:40px">
                    <div style="font-size:32px;margin-bottom:12px">🤖</div>
                    <div>AI analizi başlatmak için yukarıdaki butona tıklayın.</div>
                    <div style="font-size:12px;margin-top:8px">Groq — Llama 3.3 70B modeli kullanılır • Saatlik önbellek</div>
                </div>
                """, unsafe_allow_html=True)

        # ÖZET GRAFİK: Son 30 günlük fiyat + RSI
        st.markdown('<div class="section-title" style="margin-top:24px">SON 30 GÜN GÖRÜNÜMÜ</div>', unsafe_allow_html=True)
        son30 = seri_ai.iloc[-30:]
        rsi30 = hesapla_rsi(seri_ai).iloc[-30:]
        fig_ai = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig_ai.add_trace(go.Scatter(x=son30.index, y=son30, fill='tozeroy',
                                     fillcolor='rgba(0,212,255,0.08)', line=dict(color='#00d4ff', width=2)), row=1, col=1)
        fig_ai.add_trace(go.Scatter(x=rsi30.index, y=rsi30, line=dict(color='#aa88ff', width=1.5)), row=2, col=1)
        fig_ai.add_hline(y=70, line=dict(color='#ff4444', width=1, dash='dot'), row=2, col=1)
        fig_ai.add_hline(y=30, line=dict(color='#00ff88', width=1, dash='dot'), row=2, col=1)
        fig_ai.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                              height=300, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        fig_ai.update_xaxes(gridcolor='#1e2a3a'); fig_ai.update_yaxes(gridcolor='#1e2a3a')
        st.plotly_chart(fig_ai, use_container_width=True)
    else:
        st.warning("Veri yüklenemedi.")


# ============================================================
# TAB 3: HABERLER (RSS FEED)
# ============================================================

import xml.etree.ElementTree as ET
import html
import re

RSS_KAYNAKLAR = [
    {"ad": "Investing.com TR",  "url": "https://tr.investing.com/rss/news.rss"},
    {"ad": "Borsa Gündem",      "url": "https://www.borsagundem.com/feed"},
    {"ad": "Para Analiz",       "url": "https://www.paraanaliz.com/feed/"},
    {"ad": "Ekonomim",          "url": "https://www.ekonomim.com/rss.xml"},
    {"ad": "Bloomberg HT",      "url": "https://www.bloomberght.com/rss"},
]

@st.cache_data(ttl=600)
def rss_haberleri_cek(hisse_kodu):
    """Birden fazla RSS kaynağından haberleri çek, hisse koduna göre filtrele."""
    tum_haberler = []
    pozitif_kw = ['artış', 'yüksel', 'rekor', 'büyüme', 'kâr', 'kazanç', 'güçlü', 'olumlu', 'yatırım', 'artı']
    negatif_kw = ['düşüş', 'kayıp', 'zarar', 'risk', 'endişe', 'kriz', 'çöküş', 'olumsuz', 'baskı', 'sert']

    headers = {"User-Agent": "Mozilla/5.0 (compatible; BISTTerminal/1.0)"}

    for kaynak in RSS_KAYNAKLAR:
        try:
            resp = requests.get(kaynak["url"], headers=headers, timeout=8)
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            for item in items:
                baslik = item.findtext("title", "").strip()
                link   = item.findtext("link", "#").strip()
                tarih  = item.findtext("pubDate", "").strip()
                ozet   = item.findtext("description", "").strip()
                # HTML tag temizle
                ozet = re.sub(r'<[^>]+>', '', html.unescape(ozet))[:200]

                # Hisse kodu veya genel borsa haberi filtresi
                arama = baslik.lower() + ozet.lower()
                hisse_eslesme = (
                    hisse_kodu.lower() in arama or
                    "bist" in arama or "borsa" in arama or
                    "hisse" in arama or "endeks" in arama or
                    "piyasa" in arama or "ekonomi" in arama
                )
                if not hisse_eslesme:
                    continue

                # Tarih parse
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(tarih)
                    tarih_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    tarih_str = tarih[:16] if len(tarih) > 10 else "-"

                # Duygu analizi
                bl = baslik.lower()
                sentiment = "news-neutral"
                if any(k in bl for k in pozitif_kw): sentiment = "news-positive"
                if any(k in bl for k in negatif_kw): sentiment = "news-negative"

                tum_haberler.append({
                    "baslik": baslik,
                    "link": link,
                    "kaynak": kaynak["ad"],
                    "tarih": tarih_str,
                    "ozet": ozet,
                    "sentiment": sentiment
                })
        except Exception:
            continue

    # Tekrarları kaldır (başlığa göre)
    goruldu = set()
    benzersiz = []
    for h in tum_haberler:
        anahtar = h["baslik"][:60].lower()
        if anahtar not in goruldu:
            goruldu.add(anahtar)
            benzersiz.append(h)

    return benzersiz[:20]


with tab3:
    st.markdown('<div class="section-title">📰 PİYASA HABERLERİ VE ANALİZ</div>', unsafe_allow_html=True)

    haber_kol1, haber_kol2 = st.columns([2, 1])

    with haber_kol1:
        h_btn_col, h_info_col = st.columns([1, 2])
        with h_btn_col:
            haber_yukle = st.button("🔄 Haberleri Yükle / Güncelle", use_container_width=True)
        with h_info_col:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;padding-top:10px">📡 Kaynak: Borsa RSS feed\'leri • 10 dk önbellek</div>', unsafe_allow_html=True)

        if haber_yukle:
            with st.spinner(f"Haberler yükleniyor..."):
                haberler = rss_haberleri_cek(t_kod)
                st.session_state[f"rss_{t_kod}"] = haberler

        haberler_cache = st.session_state.get(f"rss_{t_kod}", None)

        if haberler_cache is not None:
            if haberler_cache:
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;margin-bottom:12px">{len(haberler_cache)} haber bulundu</div>', unsafe_allow_html=True)
                for haber in haberler_cache:
                    st.markdown(f"""
                    <a href="{haber['link']}" target="_blank" style="text-decoration:none">
                        <div class="news-card {haber['sentiment']}">
                            <div class="news-title">{haber['baslik']}</div>
                            {'<div style="font-size:12px;color:#6a7d90;margin:4px 0">' + haber['ozet'] + '...</div>' if haber['ozet'] else ''}
                            <div class="news-meta">📰 {haber['kaynak']} &nbsp;•&nbsp; 🕐 {haber['tarih']}</div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-box" style="text-align:center;color:#4a6080;padding:30px">
                    <div style="font-size:28px;margin-bottom:10px">📭</div>
                    <div>{t_kod} için haber bulunamadı.</div>
                    <div style="font-size:11px;margin-top:6px">RSS kaynakları geçici olarak erişilemez olabilir.</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ai-box" style="text-align:center;color:#4a6080;padding:40px">
                <div style="font-size:32px;margin-bottom:12px">📰</div>
                <div>Haberleri görmek için yukarıdaki butona tıklayın.</div>
                <div style="font-size:11px;margin-top:8px">Investing.com, Borsa Gündem, Bloomberg HT ve daha fazlasından çeker</div>
            </div>
            """, unsafe_allow_html=True)

    with haber_kol2:
        # Piyasa özeti widget
        st.markdown('<div class="section-title">PIYASA ÖZETİ</div>', unsafe_allow_html=True)
        endeksler = {"BIST 100": "XU100.IS", "Dolar/TL": "USDTRY=X", "Euro/TL": "EURTRY=X", "Altın (TL)": "GC=F"}
        for ad, ticker_k in endeksler.items():
            try:
                d = yf.download(ticker_k, period="2d", progress=False)
                if not d.empty and len(d) >= 2:
                    if isinstance(d.columns, pd.MultiIndex):
                        son = float(d['Close'].iloc[-1].iloc[0])
                        prev = float(d['Close'].iloc[-2].iloc[0])
                    else:
                        son = float(d['Close'].iloc[-1])
                        prev = float(d['Close'].iloc[-2])
                    deg = ((son - prev) / prev) * 100
                    renk = '#00ff88' if deg >= 0 else '#ff4444'
                    yon  = '▲' if deg >= 0 else '▼'
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-label">{ad}</div>
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{son:,.2f}</div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{renk}">{yon} {abs(deg):.2f}%</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
            except:
                pass


# ============================================================
# TAB 4: KARŞILAŞTIRMA
# ============================================================
with tab4:
    st.markdown('<div class="section-title">⚖ TL BAZLI PERFORMANS KARŞILAŞTIRMASI</div>', unsafe_allow_html=True)

    indir_list = [f"{t_kod}.IS", "USDTRY=X"]
    if "Altın (TL)"  in kiyas_secenek: indir_list.append("GC=F")
    if "Gümüş (TL)" in kiyas_secenek: indir_list.append("SI=F")
    if "Dolar/TL"   in kiyas_secenek: indir_list.append("USDTRY=X")

    @st.cache_data(ttl=300)
    def indir_coklu(tickers_tuple, period):
        try:
            data = yf.download(list(tickers_tuple), period=period, auto_adjust=True, progress=False)
            if data.empty: return None
            return data['Close'].ffill() if isinstance(data.columns, pd.MultiIndex) else data
        except:
            return None

    veriler = indir_coklu(tuple(sorted(set(indir_list))), secilen_periyot)

    if veriler is not None:
        if isinstance(veriler, pd.Series):
            veriler = veriler.to_frame(name=indir_list[0])

        veriler = veriler.ffill().dropna()

        if not veriler.empty and f"{t_kod}.IS" in veriler.columns:
            fig_k = go.Figure()
            ozet = []

            h_s = veriler[f"{t_kod}.IS"]
            norm = (h_s / h_s.iloc[0]) * 100
            fig_k.add_trace(go.Scatter(x=h_s.index, y=norm, name=f"{t_kod}", line=dict(color='#00d4ff', width=2.5)))
            ozet.append({"Varlık": f"{t_kod} (Hisse)", "Başlangıç": "100 TL", "Güncel": f"{norm.iloc[-1]:.2f} TL", "Getiri": f"{norm.iloc[-1]-100:+.2f}%"})

            kur = veriler.get("USDTRY=X", pd.Series(dtype=float))

            if "Altın (TL)" in kiyas_secenek and "GC=F" in veriler.columns and not kur.empty:
                a_tl = veriler["GC=F"] * kur
                a_norm = (a_tl / a_tl.iloc[0]) * 100
                fig_k.add_trace(go.Scatter(x=a_tl.index, y=a_norm, name="Altın (TL)", line=dict(color='#ffd700', width=2)))
                ozet.append({"Varlık": "Altın (TL)", "Başlangıç": "100 TL", "Güncel": f"{a_norm.iloc[-1]:.2f} TL", "Getiri": f"{a_norm.iloc[-1]-100:+.2f}%"})

            if "Gümüş (TL)" in kiyas_secenek and "SI=F" in veriler.columns and not kur.empty:
                g_tl = veriler["SI=F"] * kur
                g_norm = (g_tl / g_tl.iloc[0]) * 100
                fig_k.add_trace(go.Scatter(x=g_tl.index, y=g_norm, name="Gümüş (TL)", line=dict(color='#c0c0c0', width=2)))
                ozet.append({"Varlık": "Gümüş (TL)", "Başlangıç": "100 TL", "Güncel": f"{g_norm.iloc[-1]:.2f} TL", "Getiri": f"{g_norm.iloc[-1]-100:+.2f}%"})

            if "Dolar/TL" in kiyas_secenek and not kur.empty:
                k_norm = (kur / kur.iloc[0]) * 100
                fig_k.add_trace(go.Scatter(x=kur.index, y=k_norm, name="Dolar/TL", line=dict(color='#88ff88', width=2)))
                ozet.append({"Varlık": "Dolar/TL", "Başlangıç": "100 TL", "Güncel": f"{k_norm.iloc[-1]:.2f} TL", "Getiri": f"{k_norm.iloc[-1]-100:+.2f}%"})

            if "Enflasyon" in kiyas_secenek:
                enf_oranlari = {2020: 0.14, 2021: 0.19, 2022: 0.72, 2023: 0.65, 2024: 0.55, 2025: 0.45, 2026: 0.35}
                cumulative = [100]
                val = 100
                for i in range(1, len(veriler.index)):
                    yil = veriler.index[i].year
                    oran = enf_oranlari.get(yil, 0.45)
                    val *= (1 + oran) ** (1/252)
                    cumulative.append(val)
                fig_k.add_trace(go.Scatter(x=veriler.index, y=cumulative, name="Enflasyon", line=dict(color='#ff4444', width=1.5, dash='dot')))
                ozet.append({"Varlık": "Enflasyon Eşdeğeri", "Başlangıç": "100 TL", "Güncel": f"{cumulative[-1]:.2f} TL", "Getiri": f"{cumulative[-1]-100:+.2f}%"})

            fig_k.update_layout(
                title=f"100 TL Yatırımın Performansı — {t_sure_etiket}",
                template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                yaxis_title="Değer (TL)", height=420,
                legend=dict(bgcolor='#0f1520', bordercolor='#1e2a3a', font=dict(family='JetBrains Mono', size=11)),
                font=dict(family='JetBrains Mono', color='#8899aa'),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            fig_k.update_xaxes(gridcolor='#1e2a3a'); fig_k.update_yaxes(gridcolor='#1e2a3a')
            st.plotly_chart(fig_k, use_container_width=True)

            # Özet tablo
            st.markdown('<div class="section-title">PERFORMANS ÖZETİ</div>', unsafe_allow_html=True)
            ozet_df = pd.DataFrame(ozet)
            st.dataframe(ozet_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Karşılaştırma için yeterli veri bulunamadı.")
    else:
        st.info("Sol panelden karşılaştırmak istediğiniz varlıkları seçin.")


# ============================================================
# TAB 5: PORTFÖY
# ============================================================
with tab5:
    st.markdown('<div class="section-title">💼 GELİŞMİŞ PORTFÖY TAKİBİ</div>', unsafe_allow_html=True)

    p_kol1, p_kol2 = st.columns([1, 2])

    with p_kol1:
        with st.expander("➕ Hisse Ekle", expanded=True):
            p_hisse  = st.selectbox("Hisse:", hisse_listesi, key="p_ek")
            p_maliyet = st.number_input("Alış Fiyatı (TL):", min_value=0.01, format="%.2f", key="p_mal")
            p_adet   = st.number_input("Adet:", min_value=1, step=1, key="p_adet")
            p_hedef  = st.number_input("Hedef Fiyat (TL):", min_value=0.0, format="%.2f", key="p_hedef",
                                       help="Hedef fiyata ulaşıldığında uyarı görürsünüz")
            p_stop   = st.number_input("Stop-Loss (TL):", min_value=0.0, format="%.2f", key="p_stop",
                                       help="Stop-loss seviyesine düşünce uyarı görürsünüz")

            if st.button("Portföye Ekle", use_container_width=True):
                pkod = p_hisse.split(" - ")[0]
                yeni = pd.DataFrame([{
                    'Hisse': pkod, 'Maliyet': p_maliyet,
                    'Adet': p_adet, 'Hedef': p_hedef, 'Stop': p_stop
                }])
                st.session_state.portfoy = pd.concat([st.session_state.portfoy, yeni], ignore_index=True)
                st.rerun()

    with p_kol2:
        if not st.session_state.portfoy.empty:
            t_maliyet, t_guncel = 0.0, 0.0
            portfoy_data = []

            for idx, row in st.session_state.portfoy.iterrows():
                try:
                    g_veri = yf.download(f"{row['Hisse']}.IS", period="2d", auto_adjust=True, progress=False)
                    if not g_veri.empty:
                        if isinstance(g_veri.columns, pd.MultiIndex):
                            g_fiyat = float(g_veri['Close'].iloc[-1].iloc[0])
                            g_prev  = float(g_veri['Close'].iloc[-2].iloc[0]) if len(g_veri) > 1 else g_fiyat
                        else:
                            g_fiyat = float(g_veri['Close'].iloc[-1])
                            g_prev  = float(g_veri['Close'].iloc[-2]) if len(g_veri) > 1 else g_fiyat

                        m_toplam = row['Maliyet'] * row['Adet']
                        g_toplam = g_fiyat * row['Adet']
                        kz_tl    = g_toplam - m_toplam
                        kz_yuzde = (kz_tl / m_toplam) * 100
                        gun_deg  = ((g_fiyat - g_prev) / g_prev) * 100

                        t_maliyet += m_toplam
                        t_guncel  += g_toplam

                        # Hedef / Stop uyarıları
                        hedef_uyari = ""
                        stop_uyari  = ""
                        hedef_val = float(row.get('Hedef', 0))
                        stop_val  = float(row.get('Stop', 0))

                        if hedef_val > 0 and g_fiyat >= hedef_val:
                            hedef_uyari = f'<span style="color:#00ff88;font-size:10px">🎯 HEDEF AŞILDI ({hedef_val:.2f})</span>'
                        elif hedef_val > 0:
                            kalan_yuzde = ((hedef_val - g_fiyat) / g_fiyat) * 100
                            hedef_uyari = f'<span style="color:#4a6080;font-size:10px">🎯 Hedefe %{kalan_yuzde:.1f}</span>'

                        if stop_val > 0 and g_fiyat <= stop_val:
                            stop_uyari = f'<span style="color:#ff4444;font-size:10px">🛑 STOP TETİKLENDİ ({stop_val:.2f})</span>'
                        elif stop_val > 0:
                            stop_uyari = f'<span style="color:#4a6080;font-size:10px">🛑 Stop: {stop_val:.2f}</span>'

                        portfoy_data.append({
                            'idx': idx, 'hisse': row['Hisse'],
                            'maliyet': row['Maliyet'], 'adet': row['Adet'],
                            'g_fiyat': g_fiyat, 'm_toplam': m_toplam,
                            'g_toplam': g_toplam, 'kz_tl': kz_tl, 'kz_yuzde': kz_yuzde,
                            'gun_deg': gun_deg, 'hedef_uyari': hedef_uyari, 'stop_uyari': stop_uyari
                        })
                except Exception as e:
                    pass

            # Portföy satırları
            for p in portfoy_data:
                kz_renk = '#00ff88' if p['kz_tl'] >= 0 else '#ff4444'
                gun_renk = '#00ff88' if p['gun_deg'] >= 0 else '#ff4444'
                gun_yon  = '▲' if p['gun_deg'] >= 0 else '▼'

                r1, r2 = st.columns([5, 1])
                with r1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
                            <div>
                                <span style="font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;color:#00d4ff">{p['hisse']}</span>
                                <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#4a6080;margin-left:8px">{p['adet']} adet @ {p['maliyet']:.2f}</span>
                            </div>
                            <div style="text-align:right">
                                <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{p['g_fiyat']:.2f} TL</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{gun_renk}">{gun_yon} {abs(p['gun_deg']):.2f}% bugün</div>
                            </div>
                        </div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;flex-wrap:wrap;gap:6px">
                            <div>
                                {p['hedef_uyari']}
                                {'&nbsp;&nbsp;' if p['hedef_uyari'] and p['stop_uyari'] else ''}
                                {p['stop_uyari']}
                            </div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:{kz_renk};font-weight:700">
                                {p['kz_tl']:+,.2f} TL ({p['kz_yuzde']:+.2f}%)
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with r2:
                    if st.button("🗑", key=f"del_{p['idx']}"):
                        st.session_state.portfoy = st.session_state.portfoy.drop(p['idx']).reset_index(drop=True)
                        st.rerun()

            # TOPLAM METRİKLER
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            toplam_kz = t_guncel - t_maliyet
            toplam_kz_yuzde = ((t_guncel / t_maliyet) - 1) * 100 if t_maliyet > 0 else 0

            with m1:
                st.markdown(f"""<div class="metric-card" style="text-align:center">
                    <div class="metric-label">TOPLAM MALİYET</div>
                    <div class="metric-value metric-neutral">{t_maliyet:,.0f} TL</div>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card" style="text-align:center">
                    <div class="metric-label">GÜNCEL DEĞER</div>
                    <div class="metric-value">{t_guncel:,.0f} TL</div>
                </div>""", unsafe_allow_html=True)
            with m3:
                kz_cls = "metric-positive" if toplam_kz >= 0 else "metric-negative"
                st.markdown(f"""<div class="metric-card" style="text-align:center">
                    <div class="metric-label">NET KAR / ZARAR</div>
                    <div class="metric-value {kz_cls}">{toplam_kz:+,.0f} TL</div>
                </div>""", unsafe_allow_html=True)
            with m4:
                st.markdown(f"""<div class="metric-card" style="text-align:center">
                    <div class="metric-label">TOPLAM GETİRİ</div>
                    <div class="metric-value {'metric-positive' if toplam_kz_yuzde >= 0 else 'metric-negative'}">{toplam_kz_yuzde:+.2f}%</div>
                </div>""", unsafe_allow_html=True)

            # Portföy dağılım pastası
            if len(portfoy_data) > 1:
                st.markdown('<div class="section-title" style="margin-top:20px">PORTFÖY DAĞILIMI</div>', unsafe_allow_html=True)
                labels = [p['hisse'] for p in portfoy_data]
                values = [p['g_toplam'] for p in portfoy_data]
                fig_pie = go.Figure(go.Pie(
                    labels=labels, values=values, hole=0.5,
                    marker=dict(colors=['#00d4ff', '#00ff88', '#ff8800', '#ff4444', '#aa88ff', '#ffdd00'],
                                line=dict(color='#0a0a0f', width=2)),
                    textfont=dict(family='JetBrains Mono', size=11)
                ))
                fig_pie.update_layout(
                    template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                    height=280, showlegend=True,
                    legend=dict(bgcolor='#0f1520', bordercolor='#1e2a3a', font=dict(family='JetBrains Mono', size=10)),
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.markdown("""
            <div class="ai-box" style="text-align:center;color:#4a6080;padding:60px">
                <div style="font-size:40px;margin-bottom:12px">💼</div>
                <div style="font-size:15px">Portföyünüz boş.</div>
                <div style="font-size:12px;margin-top:8px">Sol panelden hisse ekleyerek başlayın.</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# YASAL UYARI & FOOTER
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
        Uygulama içindeki veriler, grafikler, teknik indikatörler ve yapay zeka analizleri
        <b style="color:#8899aa">alım-satım kararı için esas alınamaz.</b>
        Sermaye piyasası araçlarına yatırım yapmak kayıp riski içerir;
        geçmiş performans gelecekteki sonuçların göstergesi değildir.
        Yatırım kararlarınızı vermeden önce lisanslı bir yatırım danışmanına başvurmanız tavsiye edilir.
        <br><br>
        Veriler <b style="color:#8899aa">Yahoo Finance</b> üzerinden alınmakta olup
        gerçek zamanlı değil, gecikmeli olabilir. Veri doğruluğu garanti edilmez.
        Uygulamayı kullanan kişi bu koşulları kabul etmiş sayılır.
    </div>
</div>
<div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:10px;color:#2a3a4a;padding:8px">
   BIST TERMINAL PRO &nbsp;•&nbsp; Geliştirici: Enes Boz &nbsp;•&nbsp; """ + str(datetime.now().year) + """ &nbsp;•&nbsp;
    Veriler Yahoo Finance kaynaklıdır
</div>
""", unsafe_allow_html=True)
