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
from supabase import create_client, Client

# ============================================================
# SUPABASE İSTEMCİSİ
# ============================================================
@st.cache_resource
def supabase_baglanti() -> Client:
    url  = st.secrets["SUPABASE_URL"]
    key  = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

sb: Client = supabase_baglanti()

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
# BLOOMBERG KARANLIK TEMA CSS (aynı, değişmedi)
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
.user-badge {
    background: linear-gradient(135deg, #0f1520, #141e2e);
    border: 1px solid #00d4ff33;
    border-radius: 8px;
    padding: 8px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #00d4ff;
    display: flex;
    align-items: center;
    gap: 8px;
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
.news-meta  { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #4a6080; }
.news-positive { border-left: 3px solid #00ff88; }
.news-negative { border-left: 3px solid #ff4444; }
.news-neutral  { border-left: 3px solid #888; }
.alarm-active {
    background: #1a0f00; border: 1px solid #ff880033; border-left: 3px solid #ff8800;
    border-radius: 6px; padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #ffaa44; margin: 4px 0;
}
.alarm-triggered {
    background: #1a0000; border: 1px solid #ff444433; border-left: 3px solid #ff4444;
    border-radius: 6px; padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #ff6666; margin: 4px 0;
    animation: pulse 1s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
.ind-buy  { color: #00ff88; font-weight: 700; }
.ind-sell { color: #ff4444; font-weight: 700; }
.ind-hold { color: #ffaa00; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { background-color: #0a0a0f !important; border-bottom: 1px solid #1e2a3a !important; }
.stTabs [data-baseweb="tab"] { font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; letter-spacing: 1px !important; color: #4a6080 !important; }
.stTabs [aria-selected="true"] { color: #00d4ff !important; border-bottom: 2px solid #00d4ff !important; }
.stSelectbox > div > div, .stTextInput > div > div { background-color: #0f1520 !important; border-color: #1e2a3a !important; color: #e2e8f0 !important; }
.stButton > button {
    background: linear-gradient(135deg, #00d4ff22, #0057ff22) !important;
    border: 1px solid #00d4ff44 !important; color: #00d4ff !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important;
    letter-spacing: 1px !important; border-radius: 4px !important; transition: all 0.2s !important;
}
.stButton > button:hover { background: linear-gradient(135deg, #00d4ff44, #0057ff44) !important; border-color: #00d4ff88 !important; box-shadow: 0 0 12px #00d4ff22 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 2px; }
hr { border-color: #1e2a3a !important; }
.section-title {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00d4ff;
    letter-spacing: 3px; text-transform: uppercase;
    border-bottom: 1px solid #1e2a3a; padding-bottom: 8px; margin-bottom: 16px;
}
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
.badge-buy  { background: #00ff8822; color: #00ff88; border: 1px solid #00ff8844; }
.badge-sell { background: #ff444422; color: #ff4444; border: 1px solid #ff444444; }
.badge-hold { background: #ffaa0022; color: #ffaa00; border: 1px solid #ffaa0044; }
.info-box {
    background: linear-gradient(135deg, #0a1628 0%, #0f1f35 100%);
    border: 1px solid #00d4ff22;
    border-left: 3px solid #00d4ff;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 12px;
    color: #7aa8cc;
    line-height: 1.6;
}
.info-box-icon { font-size: 14px; margin-right: 6px; }
.success-box {
    background: linear-gradient(135deg, #0a1e0f 0%, #0f2818 100%);
    border: 1px solid #00ff8822;
    border-left: 3px solid #00ff88;
    border-radius: 6px;
    padding: 14px 16px;
    margin: 10px 0;
    font-size: 13px;
    color: #66cc88;
    line-height: 1.7;
}
.warning-box {
    background: linear-gradient(135deg, #1a1200 0%, #1f1800 100%);
    border: 1px solid #ffaa0022;
    border-left: 3px solid #ffaa00;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 12px;
    color: #ccaa44;
    line-height: 1.6;
}
.steps-box {
    background: #0f1520;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 10px 0;
}
.step-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    font-size: 12px;
    color: #8899aa;
    border-bottom: 1px solid #1e2a3a11;
}
.step-num {
    background: #00d4ff22;
    color: #00d4ff;
    border: 1px solid #00d4ff44;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
}
.auth-box {
    background: linear-gradient(145deg, #0f1520, #141e2e);
    border: 1px solid #00d4ff44;
    border-radius: 12px;
    padding: 32px;
    max-width: 480px;
    margin: 0 auto;
}
.auth-box-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 2px;
    margin-bottom: 20px;
    border-bottom: 1px solid #1e2a3a;
    padding-bottom: 12px;
}
.req-list {
    background: #0a0e16;
    border: 1px solid #1e2a3a;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 6px 0 12px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #5a7090;
    line-height: 1.9;
}
.req-ok  { color: #00ff88; }
.req-bad { color: #ff4444; }

/* TWITTER EMBED STİLLERİ */
.twitter-section {
    background: linear-gradient(135deg, #0a0f1a 0%, #0d1520 100%);
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 16px;
    margin: 12px 0;
}
.twitter-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e2a3a;
}
.twitter-logo {
    font-size: 18px;
    color: #1da1f2;
}
.twitter-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #00d4ff;
    letter-spacing: 2px;
}
.twitter-search-links {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}
.twitter-link-btn {
    background: #0f1a2e;
    border: 1px solid #1da1f222;
    border-radius: 20px;
    padding: 5px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #1da1f2;
    text-decoration: none;
    transition: all 0.2s;
    display: inline-block;
}
.twitter-link-btn:hover {
    background: #1da1f222;
    border-color: #1da1f244;
}
.twitter-embed-container {
    background: #060d18;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 8px;
    min-height: 400px;
}
.nitter-frame {
    width: 100%;
    border: none;
    border-radius: 6px;
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    'user': None,
    'user_id': None,
    'user_email': None,
    'auth_mode': 'giris',
    'show_auth': False,
    'portfoy': pd.DataFrame(columns=['id','Hisse','Maliyet','Adet','Hedef','Stop']),
    'alarmlar': [],
    'ai_cache': {},
    'mail_gonderildi': {},
    'hisse_arama': '',
    'onceki_hisse': '',   # haberlerin otomatik yüklenmesi için
    'nitter_src': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# SUPABASE YARDIMCI FONKSİYONLARI (aynı)
# ============================================================
def sb_kayit(email: str, sifre: str, ad: str = ""):
    try:
        res = sb.auth.sign_up({"email": email, "password": sifre, "options": {"data": {"full_name": ad}}})
        return res.user, None
    except Exception as e:
        return None, str(e)

def sb_giris(email: str, sifre: str):
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": sifre})
        return res.user, res.session, None
    except Exception as e:
        return None, None, str(e)

def sb_cikis():
    try:
        sb.auth.sign_out()
    except:
        pass
    for k in ['user','user_id','user_email']:
        st.session_state[k] = None
    st.session_state.portfoy = pd.DataFrame(columns=['id','Hisse','Maliyet','Adet','Hedef','Stop'])
    st.session_state.alarmlar = []

def sb_sifirla(email: str):
    try:
        sb.auth.reset_password_email(email)
        return True, None
    except Exception as e:
        return False, str(e)

def oturum_ac(user):
    st.session_state.user       = user
    st.session_state.user_id    = user.id
    st.session_state.user_email = user.email
    st.session_state.show_auth  = False
    portfoy_yukle(user.id)
    alarmlari_yukle(user.id)

# ---- Portföy DB ----
def portfoy_yukle(uid):
    try:
        res = sb.table("portfoy").select("*").eq("user_id", uid).execute()
        rows = res.data or []
        if rows:
            df = pd.DataFrame(rows)[['id','hisse','maliyet','adet','hedef','stop']]
            df.columns = ['id','Hisse','Maliyet','Adet','Hedef','Stop']
            st.session_state.portfoy = df
        else:
            st.session_state.portfoy = pd.DataFrame(columns=['id','Hisse','Maliyet','Adet','Hedef','Stop'])
    except:
        st.session_state.portfoy = pd.DataFrame(columns=['id','Hisse','Maliyet','Adet','Hedef','Stop'])

def portfoy_ekle(uid, hisse, maliyet, adet, hedef, stop):
    try:
        sb.table("portfoy").insert({
            "user_id": uid, "hisse": hisse, "maliyet": maliyet,
            "adet": adet, "hedef": hedef, "stop": stop
        }).execute()
        portfoy_yukle(uid)
        return True
    except Exception as e:
        st.error(f"Portföy eklenemedi: {e}")
        return False

def portfoy_sil(uid, row_id):
    try:
        sb.table("portfoy").delete().eq("id", row_id).eq("user_id", uid).execute()
        portfoy_yukle(uid)
    except Exception as e:
        st.error(f"Silinemedi: {e}")

# ---- Alarm DB ----
def alarmlari_yukle(uid):
    try:
        res = sb.table("alarmlar").select("*").eq("user_id", uid).eq("aktif", True).execute()
        st.session_state.alarmlar = res.data or []
    except:
        st.session_state.alarmlar = []

def alarm_ekle(uid, hisse, tur, fiyat, mail):
    try:
        sb.table("alarmlar").insert({
            "user_id": uid, "hisse": hisse, "tur": tur,
            "fiyat": fiyat, "mail": mail, "aktif": True
        }).execute()
        alarmlari_yukle(uid)
        return True
    except Exception as e:
        st.error(f"Alarm eklenemedi: {e}")
        return False

def alarm_sil(uid, alarm_id):
    try:
        sb.table("alarmlar").delete().eq("id", alarm_id).eq("user_id", uid).execute()
        alarmlari_yukle(uid)
    except Exception as e:
        st.error(f"Silinemedi: {e}")

def alarm_tetiklendi_sil(uid, alarm_id):
    """Mail gönderildikten sonra alarmı tamamen sil"""
    try:
        sb.table("alarmlar").delete().eq("id", alarm_id).eq("user_id", uid).execute()
        alarmlari_yukle(uid)
    except:
        pass

# ============================================================
# AUTH UI (aynı, kısaltıldı)
# ============================================================
def auth_header_buton():
    if st.session_state.user:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f'<div class="user-badge">◈ {st.session_state.user_email}</div>', unsafe_allow_html=True)
        with col2:
            if st.button("Çıkış", key="cikis_btn"):
                sb_cikis()
                st.rerun()
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔐 Giriş Yap", key="giris_header", use_container_width=True):
                st.session_state.show_auth = True
                st.session_state.auth_mode = 'giris'
                st.rerun()
        with col2:
            if st.button("✨ Kayıt Ol", key="kayit_header", use_container_width=True):
                st.session_state.show_auth = True
                st.session_state.auth_mode = 'kayit'
                st.rerun()

def auth_modal_ana():
    if not st.session_state.show_auth or st.session_state.user:
        return
    mod = st.session_state.auth_mode
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if mod == 'giris':
            st.markdown('<div class="auth-box-title">🔐 GİRİŞ YAP</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box"><span class="info-box-icon">ℹ️</span>Kayıtlı e-posta adresiniz ve şifrenizle giriş yapın.</div>', unsafe_allow_html=True)
            email = st.text_input("E-posta:", key="g_email", placeholder="siz@email.com")
            sifre = st.text_input("Şifre:", type="password", key="g_sifre")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Giriş", use_container_width=True, key="g_btn"):
                    if email and sifre:
                        with st.spinner("Giriş yapılıyor..."):
                            user, session, err = sb_giris(email.strip(), sifre)
                        if err:
                            if "Invalid login" in str(err) or "invalid" in str(err).lower():
                                st.error("❌ E-posta veya şifre hatalı.")
                            elif "Email not confirmed" in str(err):
                                st.warning("⚠️ E-posta doğrulanmamış. Gelen kutunuzu kontrol edin.")
                            else:
                                st.error(f"❌ Giriş hatası: {err}")
                        else:
                            st.success("✅ Giriş başarılı!")
                            oturum_ac(user)
                            st.rerun()
                    else:
                        st.warning("⚠️ Lütfen e-posta ve şifrenizi girin.")
            with c2:
                if st.button("İptal", use_container_width=True, key="g_iptal"):
                    st.session_state.show_auth = False
                    st.rerun()
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("→ Kayıt Ol", key="gec_kayit", use_container_width=True):
                    st.session_state.auth_mode = 'kayit'; st.rerun()
            with col_b:
                if st.button("→ Şifremi Unuttum", key="gec_sifre", use_container_width=True):
                    st.session_state.auth_mode = 'sifre'; st.rerun()

        elif mod == 'kayit':
            st.markdown('<div class="auth-box-title">✨ YENİ HESAP OLUŞTUR</div>', unsafe_allow_html=True)
            st.markdown("""<div class="success-box">
                <b style="color:#00ff88;font-family:'JetBrains Mono',monospace;font-size:11px">◈ BIST TERMINAL PRO — ÜCRETSİZ</b><br><br>
                ✅ Kişisel portföy takibi ve kar/zarar hesaplama<br>
                ✅ Otomatik fiyat alarmları (e-posta bildirimli)<br>
                ✅ Hedef fiyat ve stop-loss yönetimi<br>
                ✅ Tüm cihazlardan erişim ve senkronizasyon<br>
                ✅ AI destekli hisse analiz raporları
            </div>""", unsafe_allow_html=True)
            st.markdown("""<div class="steps-box">
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:1px;margin-bottom:10px">KAYIT ADIMLARI</div>
                <div class="step-item"><div class="step-num">1</div><div>Formu doldurun ve <b style="color:#c8d8e8">Kayıt Ol</b> butonuna tıklayın</div></div>
                <div class="step-item"><div class="step-num">2</div><div>E-postanıza <b style="color:#c8d8e8">doğrulama maili</b> gönderilecek</div></div>
                <div class="step-item"><div class="step-num">3</div><div>Maildeki <b style="color:#c8d8e8">onay linkine</b> tıklayın</div></div>
                <div class="step-item"><div class="step-num">4</div><div>Linke tıkladıktan sonra <b style="color:#c8d8e8">giriş yapın</b></div></div>
            </div>""", unsafe_allow_html=True)
            ad    = st.text_input("Ad Soyad:", key="k_ad", placeholder="Ahmet Yılmaz")
            email = st.text_input("E-posta:", key="k_email", placeholder="siz@email.com")
            sifre  = st.text_input("Şifre:", type="password", key="k_sifre", placeholder="En az 6 karakter")
            sifre2 = st.text_input("Şifre (tekrar):", type="password", key="k_sifre2")
            if sifre:
                uzun_ok  = len(sifre) >= 6
                esles_ok = sifre == sifre2 if sifre2 else None
                st.markdown(f"""<div class="req-list">
                    <span class="{'req-ok' if uzun_ok else 'req-bad'}">{'✅' if uzun_ok else '❌'}</span> En az 6 karakter ({len(sifre)}/6)<br>
                    <span class="{'req-ok' if esles_ok else ('req-bad' if esles_ok is not None else '')}">{'✅' if esles_ok else ('❌' if esles_ok is not None else '⏳')}</span> {'Şifreler eşleşiyor' if esles_ok else ('Şifreler eşleşmiyor' if esles_ok is not None else 'Şifreyi tekrar girin')}
                </div>""", unsafe_allow_html=True)
            st.markdown('<div class="warning-box">🔒 Bilgileriniz şifreli saklanır ve üçüncü şahıslarla paylaşılmaz.</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Kayıt Ol", use_container_width=True, key="k_btn"):
                    if not (ad and email and sifre and sifre2):
                        st.warning("⚠️ Lütfen tüm alanları doldurun.")
                    elif sifre != sifre2:
                        st.error("❌ Şifreler eşleşmiyor.")
                    elif len(sifre) < 6:
                        st.error("❌ Şifre en az 6 karakter olmalıdır.")
                    elif "@" not in email or "." not in email:
                        st.error("❌ Geçerli bir e-posta adresi girin.")
                    else:
                        with st.spinner("Hesap oluşturuluyor..."):
                            user, err = sb_kayit(email.strip(), sifre, ad.strip())
                        if err:
                            if "already registered" in str(err).lower():
                                st.error("❌ Bu e-posta zaten kayıtlı.")
                            else:
                                st.error(f"❌ Kayıt hatası: {err}")
                        else:
                            st.markdown(f"""<div class="success-box">🎉 <b>Kayıt başarılı!</b><br><br>
                                📧 <b>{email}</b> adresine doğrulama maili gönderildi.<br>
                                Spam klasörünü de kontrol edin.</div>""", unsafe_allow_html=True)
                            if st.button("→ Giriş Sayfasına Git"):
                                st.session_state.auth_mode = 'giris'; st.rerun()
            with c2:
                if st.button("İptal", use_container_width=True, key="k_iptal"):
                    st.session_state.show_auth = False; st.rerun()
            st.markdown("---")
            if st.button("→ Zaten hesabım var", key="gec_giris", use_container_width=True):
                st.session_state.auth_mode = 'giris'; st.rerun()

        elif mod == 'sifre':
            st.markdown('<div class="auth-box-title">🔑 ŞİFRE SIFIRLA</div>', unsafe_allow_html=True)
            st.markdown('<div class="info-box"><span class="info-box-icon">ℹ️</span>Kayıtlı e-postanıza sıfırlama bağlantısı göndereceğiz.</div>', unsafe_allow_html=True)
            email = st.text_input("Kayıtlı E-posta:", key="s_email", placeholder="siz@email.com")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Link Gönder", use_container_width=True, key="s_btn"):
                    if not email or "@" not in email:
                        st.warning("⚠️ Geçerli bir e-posta adresi girin.")
                    else:
                        with st.spinner("Gönderiliyor..."):
                            ok, err = sb_sifirla(email.strip())
                        if ok:
                            st.success(f"✅ Şifre sıfırlama maili gönderildi: {email}")
                        else:
                            st.error(f"❌ Gönderilemedi: {err}")
            with c2:
                if st.button("Geri", use_container_width=True, key="s_geri"):
                    st.session_state.auth_mode = 'giris'; st.rerun()
    st.markdown("---")

# ============================================================
# TAM BIST HİSSE LİSTESİ (650+ Hisse) - aynı
# ============================================================
BIST_STATIK = {
    # ... (tüm liste aynen kalabilir, çok uzun olduğu için kısaltıyorum, siz kendi listenizi koyun)
    "ADNAC":"Adana Çimento (A)","ADNAH":"Adana Çimento (H)",
    # ... diğer hisseler
}

# Yinelenen girişleri temizle
BIST_STATIK = {k: v for k, v in BIST_STATIK.items() if k.isalpha() and 2 <= len(k) <= 6}
BIST_STATIK = dict(sorted(BIST_STATIK.items()))

@st.cache_data(ttl=86400)
def bist_hisse_listesi_getir():
    """Wikipedia'dan BIST listesini dinamik olarak çekmeye çalış, başarısız olursa statik listeyi kullan"""
    try:
        url = "https://tr.wikipedia.org/wiki/BIST_100_Endeksi"
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        tables = pd.read_html(resp.text)
        for tbl in tables:
            cols = [str(c).lower() for c in tbl.columns]
            if any("kod" in c or "sembol" in c or "ticker" in c for c in cols):
                kod_col = next(c for c in tbl.columns if any(k in str(c).lower() for k in ["kod","sembol","ticker"]))
                ad_col  = next((c for c in tbl.columns if any(k in str(c).lower() for k in ["şirket","ad","unvan"])), None)
                kodlar = tbl[kod_col].dropna().astype(str).str.strip().str.upper().tolist()
                adlar  = tbl[ad_col].dropna().astype(str).tolist() if ad_col else kodlar
                sonuc  = {}
                for k, a in zip(kodlar, adlar):
                    if 2 <= len(k) <= 6 and k.isalpha():
                        sonuc[k] = a
                if len(sonuc) > 20:
                    merged = {**BIST_STATIK, **sonuc}
                    return dict(sorted(merged.items()))
    except:
        pass
    return BIST_STATIK

bist_100_full = bist_hisse_listesi_getir()
hisse_listesi = [f"{kod} - {ad}" for kod, ad in bist_100_full.items()]

# ============================================================
# TEKNİK ANALİZ FONKSİYONLARI (aynı)
# ============================================================
# ---- YENİ: ALTERNATİF VERİ KAYNAĞI (COLIR) ----
def colir_ile_veri_al(ticker_symbol: str, period="1y", interval="1d"):
    """
    Colir kütüphanesini kullanarak BIST verisi çeker.
    period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'
    interval: '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'
    """
    try:
        from colir import BIST
        bist = BIST()
        # Colir period mapping
        period_map = {"1d":"1d","5d":"5d","1mo":"1mo","3mo":"3mo","6mo":"6mo","1y":"1y","2y":"2y","5y":"5y"}
        interval_map = {"1m":"1m","5m":"5m","15m":"15m","30m":"30m","1h":"1h","1d":"1d","1wk":"1wk","1mo":"1mo"}
        p = period_map.get(period, "1y")
        i = interval_map.get(interval, "1d")
        data = bist.get_hist_data(ticker_symbol, period=p, interval=i)
        if data is not None and not data.empty:
            # Colir, Date index ve OHLCV döndürür
            data.index = pd.to_datetime(data.index)
            return data
    except Exception as e:
        # Colir yüklü değilse veya hata alınırsa sessiz geç
        pass
    return None

@st.cache_data(ttl=300)
def veri_indir(ticker, period="1y", interval="1d"):
    # Önce yfinance dene
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        if data is not None and not data.empty:
            return data
    except:
        pass

    # yfinance boş döndüyse ve ticker .IS ile bitiyorsa Colir dene
    if ticker.endswith(".IS"):
        raw_ticker = ticker[:-3]
        colir_data = colir_ile_veri_al(raw_ticker, period, interval)
        if colir_data is not None and not colir_data.empty:
            # Colir verisini yfinance formatına dönüştür (MultiIndex olmasın)
            return colir_data
    return None

# Diğer teknik fonksiyonlar (rsi, macd, bollinger, stochastic, atr, sinyal) aynı
# (kod kalabalığı olmaması için buraya aynen kopyalanabilir, ama uzunluktan kısaltıyorum)
# NOT: Gerçek dosyada bu fonksiyonlar aynen kalacak. Ben sadece değişen kısmı gösteriyorum.
# Aşağıda hesapla_rsi, hesapla_macd, hesapla_bollinger, hesapla_stochastic, hesapla_atr, teknik_sinyal_hesapla
# fonksiyonlarının aynen kaldığını varsayıyorum.

# ============================================================
# MAİL FONKSİYONU (aynı)
# ============================================================
def alarm_maili_gonder(alici_mail, hisse, tur, alarm_fiyat, gercek_fiyat):
    # ... aynı kod
    pass

# ============================================================
# AI ANALİZ (Groq) (aynı)
# ============================================================
def ai_analiz_yap(kod, ad, fiyat, degisim, rsi, genel_sinyal, seri):
    # ... aynı
    pass

# ============================================================
# TWITTER / X SOSYAL MEDYA FONKSİYONU (GÜNCELLENDİ)
# ============================================================
def twitter_sosyal_medya_bolumu(hisse_kodu, hisse_adi):
    """
    Twitter/X için ücretsiz arama linkleri ve embed widget.
    - Çalışan Nitter instance'ları kullanılır.
    - ADNAC, ADNAH gibi hisseler için özel hashtag üretilir.
    """
    # Özel karakter temizliği
    temiz_kod = hisse_kodu.replace(".", "").replace("-", "")
    hashtag1 = f"#{temiz_kod}"
    hashtag2 = f"#{temiz_kod}hisse"
    hashtag3 = f"BIST {temiz_kod}"

    # Twitter/X resmi arama linkleri
    twitter_url1 = f"https://twitter.com/search?q=%23{temiz_kod}&src=typed_query&f=live"
    twitter_url2 = f"https://twitter.com/search?q=%23{temiz_kod}hisse&src=typed_query&f=live"
    twitter_url3 = f"https://twitter.com/search?q={temiz_kod}+BIST&src=typed_query&f=live"
    x_url        = f"https://x.com/search?q=%23{temiz_kod}&src=typed_query&f=live"

    # Çalışan Nitter instance'ları (güncel)
    nitter_instances = [
        f"https://nitter.net/search?q=%23{temiz_kod}&f=tweets",
        f"https://nitter.cz/search?q=%23{temiz_kod}&f=tweets",
        f"https://nitter.privacydev.net/search?q=%23{temiz_kod}&f=tweets",
        f"https://nitter.kavin.rocks/search?q=%23{temiz_kod}&f=tweets",
    ]

    st.markdown(f"""
    <div class="twitter-section">
        <div class="twitter-header">
            <span style="font-size:20px">𝕏</span>
            <div>
                <div class="twitter-title">SOSYAL MEDYA TAKİBİ — {hisse_kodu}</div>
                <div style="font-size:10px;color:#4a6080;font-family:'JetBrains Mono',monospace">Twitter/X'te {hisse_kodu} ile ilgili gönderiler</div>
            </div>
        </div>

        <div style="margin-bottom:14px">
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:1px;margin-bottom:8px">🔗 DOĞRUDAN ARAMA LİNKLERİ (Yeni sekmede açılır)</div>
            <div class="twitter-search-links">
                <a href="{twitter_url1}" target="_blank" class="twitter-link-btn">𝕏 #{temiz_kod}</a>
                <a href="{twitter_url2}" target="_blank" class="twitter-link-btn">𝕏 #{temiz_kod}hisse</a>
                <a href="{twitter_url3}" target="_blank" class="twitter-link-btn">𝕏 {temiz_kod} BIST</a>
                <a href="{x_url}" target="_blank" class="twitter-link-btn">𝕏 Canlı Akış</a>
            </div>
        </div>

        <div style="margin-bottom:10px">
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:1px;margin-bottom:8px">🔓 ÜCRETSİZ NITTER GÖRÜNTÜLEYICI (API gerektirmez)</div>
            <div style="font-size:11px;color:#5a6a7a;margin-bottom:8px;font-family:'JetBrains Mono',monospace">
                ℹ️ Nitter, Twitter'ın açık kaynaklı alternatif arayüzüdür. Aşağıdaki embed ücretsiz çalışır.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nitter iframe embed - butonlarla instance seçimi
    n1, n2, n3, n4 = st.columns(4)
    with n1:
        if st.button(f"Nitter.net → #{temiz_kod}", use_container_width=True, key="nitter1"):
            st.session_state['nitter_src'] = nitter_instances[0]
    with n2:
        if st.button(f"Nitter.cz → #{temiz_kod}", use_container_width=True, key="nitter2"):
            st.session_state['nitter_src'] = nitter_instances[1]
    with n3:
        if st.button(f"Nitter.privacydev", use_container_width=True, key="nitter3"):
            st.session_state['nitter_src'] = nitter_instances[2]
    with n4:
        if st.button(f"𝕏 Twitter Aç", use_container_width=True, key="twitter_open"):
            st.session_state['nitter_src'] = twitter_url1

    # Seçilen kaynak (varsayılan nitter.net)
    nitter_src = st.session_state.get('nitter_src', nitter_instances[0])

    # iframe embed
    st.markdown(f"""
    <div style="background:#060d18;border:1px solid #1e2a3a;border-radius:8px;overflow:hidden;margin-top:8px">
        <div style="padding:8px 12px;background:#0a1020;border-bottom:1px solid #1e2a3a;
            font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a6080;display:flex;
            align-items:center;justify-content:space-between">
            <span>🔴 CANLI • #{temiz_kod} Twitter Akışı</span>
            <span style="color:#1da1f2">{nitter_src[:60]}...</span>
        </div>
        <iframe
            src="{nitter_src}"
            width="100%"
            height="600"
            frameborder="0"
            style="display:block;background:#0a0a0f;"
            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
            loading="lazy"
        ></iframe>
    </div>

    <div style="margin-top:10px;padding:10px 14px;background:#0f1a0a;border:1px solid #2a3a1a;
        border-left:3px solid #44aa44;border-radius:6px;
        font-family:'JetBrains Mono',monospace;font-size:11px;color:#6a8a6a;line-height:1.7">
        💡 <b style="color:#88cc88">Nitter</b> çalışmıyorsa: Tarayıcınızda reklam engelleyici varsa izin verin veya
        yukarıdaki <b style="color:#88cc88">𝕏 Twitter Aç</b> butonunu kullanarak resmi Twitter'da #{temiz_kod} aramalarını görüntüleyin.
        <br>📌 Twitter/X'te hesap olmadan <b style="color:#88cc88">son 7 günlük</b> tweetler görüntülenebilir.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HABER FONKSİYONU (otomatik yükleme için değiştirildi)
# ============================================================
RSS_KAYNAKLAR = [
    {"ad": "Investing.com TR", "url": "https://tr.investing.com/rss/news.rss"},
    {"ad": "Borsa Gündem",     "url": "https://www.borsagundem.com/feed"},
    {"ad": "Para Analiz",      "url": "https://www.paraanaliz.com/feed/"},
    {"ad": "Ekonomim",         "url": "https://www.ekonomim.com/rss.xml"},
    {"ad": "Bloomberg HT",     "url": "https://www.bloomberght.com/rss"},
]

@st.cache_data(ttl=600)
def rss_haberleri_cek(hisse_kodu):
    tum_haberler = []
    pozitif_kw = ['artış','yüksel','rekor','büyüme','kâr','kazanç','güçlü','olumlu']
    negatif_kw = ['düşüş','kayıp','zarar','risk','endişe','kriz','çöküş','olumsuz']
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BISTTerminal/1.0)"}
    for kaynak in RSS_KAYNAKLAR:
        try:
            resp = requests.get(kaynak["url"], headers=headers, timeout=8)
            if resp.status_code != 200: continue
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item"):
                baslik = item.findtext("title", "").strip()
                link   = item.findtext("link", "#").strip()
                tarih  = item.findtext("pubDate", "").strip()
                ozet   = re.sub(r'<[^>]+>', '', html_lib.unescape(item.findtext("description", "")))[:200]
                arama  = baslik.lower() + ozet.lower()
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
        except:
            continue
    goruldu = set(); benzersiz = []
    for h in tum_haberler:
        k = h["baslik"][:60].lower()
        if k not in goruldu:
            goruldu.add(k); benzersiz.append(h)
    return benzersiz[:20]

# ============================================================
# HEADER (aynı)
# ============================================================
h_left, h_right = st.columns([3, 1])
with h_left:
    st.markdown(f"""
    <div style="padding:12px 0 8px 0">
        <div class="terminal-logo">◈ BIST TERMINAL PRO</div>
        <div class="terminal-subtitle">GELİŞTİRİCİ: ENES BOZ • {datetime.now().strftime('%d.%m.%Y %H:%M')} IST • ● CANLI</div>
    </div>""", unsafe_allow_html=True)
with h_right:
    auth_header_buton()

st.markdown('<hr style="margin:0 0 16px 0">', unsafe_allow_html=True)
auth_modal_ana()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="section-title">⚙ KONTROL PANELİ</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;letter-spacing:1px;margin-bottom:6px">🔍 HİSSE ARA</div>', unsafe_allow_html=True)
    arama_metni = st.text_input("Hisse ara:", placeholder="Kod veya şirket adı... (ör: GARAN)", key="sidebar_arama", label_visibility="collapsed")

    if arama_metni and len(arama_metni.strip()) >= 1:
        arama_lower = arama_metni.strip().lower()
        filtrelenmis_liste = [h for h in hisse_listesi if arama_lower in h.lower()]
        if not filtrelenmis_liste:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#ff4444;padding:8px;background:#1a0000;border-radius:4px">⚠ "{arama_metni}" bulunamadı</div>', unsafe_allow_html=True)
            filtrelenmis_liste = hisse_listesi
        else:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;margin:4px 0 6px 0">📊 {len(filtrelenmis_liste)} hisse bulundu</div>', unsafe_allow_html=True)
    else:
        filtrelenmis_liste = hisse_listesi
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#2a3a4a;margin:2px 0 6px 0">Toplam {len(hisse_listesi)} hisse mevcut</div>', unsafe_allow_html=True)

    default_idx = 0
    for i, h in enumerate(filtrelenmis_liste):
        if "GARAN" in h:
            default_idx = i
            break

    ana_secim = st.selectbox("Hisse Seç:", filtrelenmis_liste, index=min(default_idx, len(filtrelenmis_liste)-1), key="hisse_secim")
    t_kod = ana_secim.split(" - ")[0]
    t_ad  = ana_secim.split(" - ")[1]

    st.markdown(f"""
    <div style="background:#0f1520;border:1px solid #1e2a3a;border-left:2px solid #00d4ff;
    border-radius:6px;padding:8px 12px;margin:6px 0 12px 0">
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#00d4ff;font-weight:700">{t_kod}</div>
        <div style="font-size:11px;color:#4a6080;margin-top:2px">{t_ad}</div>
    </div>""", unsafe_allow_html=True)

    t_sure_etiket = st.radio("Periyot:", ["1 Ay", "3 Ay", "1 Yıl", "3 Yıl", "5 Yıl"], index=2)
    t_periyot = {"1 Ay": "1mo", "3 Ay": "3mo", "1 Yıl": "1y", "3 Yıl": "3y", "5 Yıl": "5y"}
    t_aralik  = {"1 Ay": "1h",  "3 Ay": "1d",  "1 Yıl": "1d", "3 Yıl": "1wk", "5 Yıl": "1wk"}
    secilen_periyot = t_periyot[t_sure_etiket]
    secilen_aralik  = t_aralik[t_sure_etiket]

    st.markdown("---")
    st.markdown('<div class="section-title">🔔 FİYAT ALARMLARI</div>', unsafe_allow_html=True)

    if not st.session_state.user:
        st.markdown('<div class="alarm-active" style="border-color:#00d4ff33;border-left-color:#00d4ff">🔐 Alarm eklemek için giriş yapın.<br><span style="font-size:10px">Sağ üstten kayıt olabilirsiniz.</span></div>', unsafe_allow_html=True)
    else:
        # YENİ: Seçili hisse için hızlı alarm kurma
        st.markdown(f"**Seçili Hisse: {t_kod}**")
        alarm_tur_hizli = st.radio("Alarm Türü:", ["Üstüne Çıkarsa", "Altına Düşerse"], horizontal=True, key="hizli_tur")
        alarm_fiyat_hizli = st.number_input("Fiyat (TL):", min_value=0.01, format="%.2f", key="hizli_fiyat", value=100.0)
        if st.button(f"⚡ {t_kod} için Alarm Kur", use_container_width=True, key="hizli_alarm"):
            if alarm_ekle(st.session_state.user_id, t_kod, alarm_tur_hizli, alarm_fiyat_hizli, st.session_state.user_email):
                st.success(f"✅ {t_kod} için alarm kuruldu!")
                st.rerun()

        st.markdown("---")
        # Eski alarm ekleme (istediği hisse için)
        with st.expander("➕ Başka Hisse için Alarm Ekle"):
            alarm_hisse = st.selectbox("Hisse:", hisse_listesi, key="alarm_h")
            alarm_tur   = st.radio("Tür:", ["Üstüne Çıkarsa", "Altına Düşerse"], horizontal=True, key="alarm_tur")
            alarm_fiyat = st.number_input("Fiyat (TL):", min_value=0.01, format="%.2f", key="alarm_f")
            alarm_mail  = st.text_input("📧 E-posta:", value=st.session_state.user_email, key="alarm_mail")
            if st.button("Alarm Ekle", use_container_width=True, key="alarm_ekle_btn"):
                alarm_kod = alarm_hisse.split(" - ")[0]
                if alarm_ekle(st.session_state.user_id, alarm_kod, alarm_tur, alarm_fiyat, alarm_mail.strip()):
                    st.success("✅ Alarm eklendi!")
                    st.rerun()

        if st.session_state.alarmlar:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;margin:8px 0 4px">AKTİF ALARMLAR</div>', unsafe_allow_html=True)
            alarmlar_silinecek = []

            for alarm in st.session_state.alarmlar:
                try:
                    d = veri_indir(f"{alarm['hisse']}.IS", period="1d", interval="1d")
                    if d is None or d.empty: continue
                    if isinstance(d.columns, pd.MultiIndex):
                        g_fiyat = float(d['Close'].iloc[-1].iloc[0])
                    else:
                        g_fiyat = float(d['Close'].iloc[-1])

                    tetiklendi = (
                        (alarm['tur'] == "Üstüne Çıkarsa" and g_fiyat >= float(alarm['fiyat'])) or
                        (alarm['tur'] == "Altına Düşerse"  and g_fiyat <= float(alarm['fiyat']))
                    )

                    if tetiklendi and alarm.get('mail'):
                        mail_key = f"{alarm['id']}_{alarm['fiyat']}"
                        son = st.session_state.mail_gonderildi.get(mail_key)
                        simdi = datetime.now()
                        if son is None or (simdi - son).total_seconds() > 3600:
                            ok, msg = alarm_maili_gonder(
                                alarm['mail'], alarm['hisse'], alarm['tur'],
                                float(alarm['fiyat']), g_fiyat
                            )
                            if ok:
                                st.session_state.mail_gonderildi[mail_key] = simdi
                                alarmlar_silinecek.append(alarm['id'])
                                st.toast(f"✅ {alarm['hisse']} alarmı tetiklendi → Mail gönderildi, alarm silindi!", icon="🔔")
                            else:
                                st.toast(f"⚠ Mail gönderilemedi: {msg}", icon="❌")

                    if alarm['id'] not in alarmlar_silinecek:
                        a1, a2 = st.columns([4, 1])
                        with a1:
                            if tetiklendi:
                                st.markdown(f"""<div class="alarm-triggered">🚨 <b>{alarm['hisse']}</b> → {g_fiyat:.2f} TL<br>
                                <span style="font-size:10px">{alarm['tur']} {float(alarm['fiyat']):.2f} TL • Mail gönderiliyor...</span></div>""", unsafe_allow_html=True)
                            else:
                                pct = abs((float(alarm['fiyat']) - g_fiyat) / g_fiyat * 100) if g_fiyat != 0 else 0
                                yon = "▲" if alarm['tur'] == "Üstüne Çıkarsa" else "▼"
                                st.markdown(f"""<div class="alarm-active">🔔 <b>{alarm['hisse']}</b> {yon} {float(alarm['fiyat']):.2f} TL<br>
                                <span style="font-size:10px">Şu an: {g_fiyat:.2f} • Fark: %{pct:.1f}</span></div>""", unsafe_allow_html=True)
                        with a2:
                            if st.button("✕", key=f"aldel_{alarm['id']}"):
                                alarm_sil(st.session_state.user_id, alarm['id'])
                                st.rerun()
                except:
                    pass

            if alarmlar_silinecek:
                for aid in alarmlar_silinecek:
                    alarm_tetiklendi_sil(st.session_state.user_id, aid)
                st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">⚖ KARŞILAŞTIRMA</div>', unsafe_allow_html=True)
    kiyas_secenek = st.multiselect("Karşılaştırma Ekle:", ["Altın (TL)", "Gümüş (TL)", "Dolar/TL", "Enflasyon"])

# ============================================================
# ANA TABS — 5 sekme
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  TEKNİK ANALİZ",
    "🤖  AI RAPORU",
    "📰  HABERLER",
    "💼  PORTFÖY",
    "𝕏  SOSYAL MEDYA",
])

# ============================================================
# TAB 1: TEKNİK ANALİZ (aynı, ancak veri_indir yeni haliyle)
# ============================================================
with tab1:
    data_raw = veri_indir(f"{t_kod}.IS", secilen_periyot, secilen_aralik)

    if data_raw is not None and not data_raw.empty:
        # ... (teknik analiz kodu aynen devam eder)
        # Uzun olduğu için kısaltıyorum, aslında aynı kalacak
        st.write("Teknik analiz grafikleri burada gösterilecek.")
    else:
        st.warning(f"⚠ {t_kod} için veri indirilemedi. Hisse senedi verisi yfinance veya Colir'de bulunamadı.")

# ============================================================
# TAB 2: AI RAPORU (aynı)
# ============================================================
with tab2:
    st.markdown('<div class="section-title">🤖 YAPAY ZEKA ANALİZ RAPORU</div>', unsafe_allow_html=True)
    # ... aynı kod

# ============================================================
# TAB 3: HABERLER (OTOMATİK YÜKLEME EKLENDİ)
# ============================================================
with tab3:
    st.markdown('<div class="section-title">📰 PİYASA HABERLERİ</div>', unsafe_allow_html=True)

    # Hisse değişti mi kontrol et
    if st.session_state.onceki_hisse != t_kod:
        st.session_state.onceki_hisse = t_kod
        with st.spinner("Haberler yükleniyor..."):
            haberler = rss_haberleri_cek(t_kod)
            st.session_state[f"rss_{t_kod}"] = haberler

    haberler_cache = st.session_state.get(f"rss_{t_kod}")
    if haberler_cache is not None:
        if haberler_cache:
            for haber in haberler_cache:
                st.markdown(f"""<a href="{haber['link']}" target="_blank" style="text-decoration:none">
                    <div class="news-card {haber['sentiment']}">
                        <div class="news-title">{haber['baslik']}</div>
                        {'<div style="font-size:12px;color:#6a7d90;margin:4px 0">' + haber['ozet'] + '...</div>' if haber['ozet'] else ''}
                        <div class="news-meta">📰 {haber['kaynak']} &nbsp;•&nbsp; 🕐 {haber['tarih']}</div>
                    </div></a>""", unsafe_allow_html=True)
        else:
            st.info("Bu hisse ile ilgili güncel haber bulunamadı.")
    else:
        st.info("Haberler yükleniyor... lütfen bekleyin.")

# ============================================================
# TAB 4: PORTFÖY (aynı)
# ============================================================
with tab4:
    # ... aynı
    st.write("Portföy içeriği")

# ============================================================
# TAB 5: SOSYAL MEDYA (güncellenmiş fonksiyon)
# ============================================================
with tab5:
    twitter_sosyal_medya_bolumu(t_kod, t_ad)

# ============================================================
# FOOTER (aynı)
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="background:#0f0f1a;border:1px solid #1e2a3a;border-left:3px solid #ffaa00;border-radius:8px;padding:16px 20px;margin-bottom:12px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#ffaa00;letter-spacing:2px;margin-bottom:8px">⚠ YASAL UYARI / SORUMLULUK REDDİ</div>
    <div style="font-size:12px;color:#6a7d90;line-height:1.8">
        Bu uygulama <b style="color:#8899aa">yalnızca bilgilendirme amaçlıdır</b> ve <b style="color:#8899aa">yatırım tavsiyesi niteliği taşımamaktadır.</b>
        Veriler Yahoo Finance kaynaklıdır; gerçek zamanlı olmayabilir. Yatırım kararlarınızı vermeden önce lisanslı bir danışmana başvurun.
    </div>
</div>
<div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:10px;color:#2a3a4a;padding:8px">
    BIST TERMINAL PRO &nbsp;•&nbsp; Geliştirici: Enes Boz &nbsp;•&nbsp; {datetime.now().year} &nbsp;•&nbsp; Veriler Yahoo Finance & Colir kaynaklıdır
</div>
""", unsafe_allow_html=True)
