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
/* User badge */
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

/* INFO BOX */
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

/* AUTH MODAL */
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
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# SUPABASE YARDIMCI FONKSİYONLARI
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
    except Exception as e:
        st.session_state.portfoy = pd.DataFrame(columns=['id','Hisse','Maliyet','Adet','Hedef','Stop'])

def portfoy_ekle(uid, hisse, maliyet, adet, hedef, stop):
    try:
        res = sb.table("portfoy").insert({
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
        res = sb.table("alarmlar").insert({
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

def alarm_tetiklendi_guncelle(alarm_id):
    try:
        sb.table("alarmlar").update({"tetiklendi": True, "son_tetik": datetime.utcnow().isoformat()}).eq("id", alarm_id).execute()
    except:
        pass

# ============================================================
# AUTH UI
# ============================================================
def auth_header_buton():
    if st.session_state.user:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"""
            <div class="user-badge">◈ {st.session_state.user_email}</div>""",
            unsafe_allow_html=True)
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

            # Bilgilendirme kutusu
            st.markdown("""
            <div class="info-box">
                <span class="info-box-icon">ℹ️</span>
                Kayıtlı e-posta adresiniz ve şifrenizle giriş yapın.
                Hesabınız yoksa sağ üst köşedeki <b style="color:#00d4ff">Kayıt Ol</b> butonunu kullanın.
            </div>
            """, unsafe_allow_html=True)

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
                                st.error("❌ E-posta veya şifre hatalı. Lütfen tekrar deneyin.")
                            elif "Email not confirmed" in str(err):
                                st.warning("⚠️ E-posta adresiniz henüz doğrulanmamış. Lütfen gelen kutunuzu kontrol edin.")
                            else:
                                st.error(f"❌ Giriş hatası: {err}")
                        else:
                            st.success("✅ Giriş başarılı! Yönlendiriliyorsunuz...")
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
                    st.session_state.auth_mode = 'kayit'
                    st.rerun()
            with col_b:
                if st.button("→ Şifremi Unuttum", key="gec_sifre", use_container_width=True):
                    st.session_state.auth_mode = 'sifre'
                    st.rerun()

        elif mod == 'kayit':
            st.markdown('<div class="auth-box-title">✨ YENİ HESAP OLUŞTUR</div>', unsafe_allow_html=True)

            # Kayıt avantajları
            st.markdown("""
            <div class="success-box">
                <b style="color:#00ff88;font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:1px">◈ BIST TERMINAL PRO — ÜCRETSİZ</b><br><br>
                ✅ &nbsp;Kişisel portföy takibi ve kar/zarar hesaplama<br>
                ✅ &nbsp;Otomatik fiyat alarmları (e-posta bildirimli)<br>
                ✅ &nbsp;Hedef fiyat ve stop-loss yönetimi<br>
                ✅ &nbsp;Tüm cihazlardan erişim ve senkronizasyon<br>
                ✅ &nbsp;AI destekli hisse analiz raporları
            </div>
            """, unsafe_allow_html=True)

            # Kayıt adımları
            st.markdown("""
            <div class="steps-box">
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:1px;margin-bottom:10px">KAYIT ADIMLARI</div>
                <div class="step-item"><div class="step-num">1</div><div>Formu doldurun ve <b style="color:#c8d8e8">Kayıt Ol</b> butonuna tıklayın</div></div>
                <div class="step-item"><div class="step-num">2</div><div>Kayıt ettiğiniz e-posta adresine <b style="color:#c8d8e8">doğrulama maili</b> gönderilecek</div></div>
                <div class="step-item"><div class="step-num">3</div><div>E-postanızdaki <b style="color:#c8d8e8">onay linkine</b> tıklayın (spam/junk kutusunu da kontrol edin)</div></div>
                <div class="step-item"><div class="step-num">4</div><div>Linke tıkladıktan sonra buraya dönüp <b style="color:#c8d8e8">giriş yapın</b></div></div>
            </div>
            """, unsafe_allow_html=True)

            ad    = st.text_input("Ad Soyad:", key="k_ad", placeholder="Ahmet Yılmaz")
            email = st.text_input("E-posta:", key="k_email", placeholder="siz@email.com")

            sifre  = st.text_input("Şifre:", type="password", key="k_sifre", placeholder="En az 6 karakter")
            sifre2 = st.text_input("Şifre (tekrar):", type="password", key="k_sifre2", placeholder="Şifrenizi tekrar girin")

            # Gerçek zamanlı şifre gereksinimleri göstergesi
            if sifre:
                uzun_ok   = len(sifre) >= 6
                esles_ok  = sifre == sifre2 if sifre2 else None
                uzun_icon = "✅" if uzun_ok else "❌"
                esles_icon = ("✅" if esles_ok else "❌") if esles_ok is not None else "⏳"
                esles_text = ("Şifreler eşleşiyor" if esles_ok else "Şifreler eşleşmiyor") if esles_ok is not None else "Şifreyi tekrar girin"
                st.markdown(f"""
                <div class="req-list">
                    <span class="{'req-ok' if uzun_ok else 'req-bad'}">{uzun_icon}</span> En az 6 karakter ({len(sifre)}/6)<br>
                    <span class="{'req-ok' if esles_ok else ('req-bad' if esles_ok is not None else '')}">{esles_icon}</span> {esles_text}
                </div>
                """, unsafe_allow_html=True)

            # Kişisel veri notu
            st.markdown("""
            <div class="warning-box">
                🔒 &nbsp;Bilgileriniz şifreli olarak saklanır ve üçüncü şahıslarla paylaşılmaz.
                Bu platform yalnızca kişisel kullanım amaçlıdır.
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Kayıt Ol", use_container_width=True, key="k_btn"):
                    if not (ad and email and sifre and sifre2):
                        st.warning("⚠️ Lütfen tüm alanları doldurun.")
                    elif sifre != sifre2:
                        st.error("❌ Şifreler eşleşmiyor. Lütfen kontrol edin.")
                    elif len(sifre) < 6:
                        st.error("❌ Şifre en az 6 karakter olmalıdır.")
                    elif "@" not in email or "." not in email:
                        st.error("❌ Geçerli bir e-posta adresi girin.")
                    else:
                        with st.spinner("Hesap oluşturuluyor..."):
                            user, err = sb_kayit(email.strip(), sifre, ad.strip())
                        if err:
                            if "already registered" in str(err).lower() or "already exists" in str(err).lower():
                                st.error("❌ Bu e-posta adresi zaten kayıtlı. Giriş yapmayı deneyin.")
                            else:
                                st.error(f"❌ Kayıt hatası: {err}")
                        else:
                            st.markdown(f"""
                            <div class="success-box" style="margin-top:12px">
                                <b style="font-size:14px;color:#00ff88">🎉 Kayıt başarılı!</b><br><br>
                                📧 &nbsp;<b style="color:#c8d8e8">{email}</b> adresine doğrulama maili gönderildi.<br><br>
                                <b>Sonraki adımlar:</b><br>
                                &nbsp;1. E-posta gelen kutunuzu kontrol edin<br>
                                &nbsp;2. <b>Spam / Junk</b> klasörünü de kontrol edin<br>
                                &nbsp;3. Maildeki onay linkine tıklayın<br>
                                &nbsp;4. Buraya dönüp giriş yapın
                            </div>
                            """, unsafe_allow_html=True)
                            st.info("💡 Mail birkaç dakika içinde ulaşmazsa spam klasörünü kontrol edin veya yeniden kayıt olmayı deneyin.")
                            if st.button("→ Giriş Sayfasına Git", key="kayit_sonrasi_giris"):
                                st.session_state.auth_mode = 'giris'
                                st.rerun()
            with c2:
                if st.button("İptal", use_container_width=True, key="k_iptal"):
                    st.session_state.show_auth = False
                    st.rerun()
            st.markdown("---")
            if st.button("→ Zaten hesabım var, giriş yapayım", key="gec_giris", use_container_width=True):
                st.session_state.auth_mode = 'giris'
                st.rerun()

        elif mod == 'sifre':
            st.markdown('<div class="auth-box-title">🔑 ŞİFRE SIFIRLA</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="info-box">
                <span class="info-box-icon">ℹ️</span>
                Kayıtlı e-posta adresinizi girin. Size şifre sıfırlama bağlantısı içeren bir e-posta göndereceğiz.<br><br>
                <b style="color:#00d4ff">Not:</b> Mail birkaç dakika içinde ulaşmazsa spam/junk klasörünü kontrol edin.
            </div>
            """, unsafe_allow_html=True)

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
                            st.markdown(f"""
                            <div class="success-box">
                                ✅ &nbsp;<b>Şifre sıfırlama maili gönderildi!</b><br><br>
                                📧 &nbsp;<b style="color:#c8d8e8">{email}</b> adresini kontrol edin.<br>
                                Maildeki bağlantıya tıklayarak yeni şifrenizi belirleyebilirsiniz.<br><br>
                                <span style="font-size:11px;color:#4a7055">⏱ Mail birkaç dakika içinde ulaşacaktır.</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Gönderilemedi: {err}")
            with c2:
                if st.button("Geri", use_container_width=True, key="s_geri"):
                    st.session_state.auth_mode = 'giris'
                    st.rerun()

            st.markdown("""
            <div class="warning-box" style="margin-top:12px">
                ⚠️ &nbsp;Şifre sıfırlama linki yalnızca <b>1 saat</b> geçerlidir.
                Süre dolduktan sonra yeni bir link talep etmeniz gerekir.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

# ============================================================
# TAM BIST HİSSE LİSTESİ (500+ Hisse)
# ============================================================
BIST_STATIK = {
    "A1CAP":"A1 Capital","ACSEL":"Acıselsan Acıpayam Selüloz","ADEL":"Adel Kalemcilik",
    "ADESE":"Adese Alışveriş Merkezleri","AEFES":"Anadolu Efes Biracılık","AFYON":"Afyon Çimento",
    "AGESA":"Agesa Hayat ve Emeklilik","AGHOL":"Anadolu Grubu Holding","AGROT":"Agrotech Teknoloji",
    "AGYO":"Atakule GYO","AHGAZ":"Ahlatcı Doğalgaz","AKBNK":"Akbank",
    "AKCNS":"Akçansa Çimento","AKENR":"Akenerji Elektrik Üretim","AKFGY":"Akfen GYO",
    "AKFYE":"Akfen Yenilenebilir Enerji","AKGRT":"Aksigorta","AKMGY":"Akkök GYO",
    "AKSA":"Aksa Akrilik Kimya","AKSEN":"Aksa Enerji Üretim","AKSGY":"Akiş GYO",
    "AKSUE":"Aksu Enerji","AKYHO":"Akın Tekstil","ALARK":"Alarko Holding",
    "ALBRK":"Albaraka Türk","ALCAR":"Alarko Carrier Sanayi","ALCTL":"Alcatel Lucent Teletaş",
    "ALFAS":"Alfasolar Enerji","ALGYO":"Alarko GYO","ALKA":"Alka Kimya",
    "ALKIM":"Alkim Kimya Sanayii","ALKLC":"Alkim Kağıt","ALTNY":"Altınay Savunma",
    "ALVES":"Alves Elektromekanik","ALYAG":"Alternatif Yatırım Ortaklığı","ANELE":"Anel Elektrik",
    "ANGEN":"Anatolia Tanı ve Biyoteknoloji","ANHYT":"Anadolu Hayat Emeklilik","ANSGR":"Anadolu Sigorta",
    "ANTGM":"Antalya Gölet","ARCLK":"Arçelik","ARDYZ":"Ard Bilişim Sistemleri",
    "ARENA":"Arena Bilgisayar","ARSAN":"Arsan Tekstil","ASELS":"Aselsan Elektronik",
    "ASTOR":"Astor Enerji","ASUZU":"Anadolu Isuzu Otomotiv","ATAKP":"Atakey Patates",
    "ATATP":"Ata Tekstil","ATEKS":"Altınyıldız Tekstil","ATLAS":"Atlas Menkul Kıymetler",
    "AYDEM":"Aydem Enerji","AYGAZ":"Aygaz","AZTEK":"Aztek Elektronik",
    "BAGFS":"Bagfaş Bandırma Gübre","BAKAB":"Bak Ambalaj","BANVT":"Banvit Bandırma Vitaminli",
    "BARMA":"Barem Ambalaj","BASGZ":"Başkent Doğalgaz","BAYRK":"Bayrak EBT Taban",
    "BEBEK":"Ebebek Mağazacılık","BERA":"Bera Holding","BEYAZ":"Beyaz Filo Araç Kiralama",
    "BFREN":"Bosch Fren Sistemleri","BIENM":"Bien Yapı Ürünleri","BIGCH":"Bigchefs",
    "BIMAS":"Bim Mağazalar","BINHO":"1000 Yatırımlar Holding","BIOEN":"Biotrend Enerji",
    "BIZIM":"Bizim Toptan Satış","BMSCH":"BMS Çelik Hasır","BNTAS":"Bantaş Nakliyat Ambalaj",
    "BOBET":"Boğaziçi Beton","BORLS":"Borlease Otomotiv Kiralama","BORSK":"Bor Şeker",
    "BOSSA":"Bossa Ticaret","BRISA":"Brisa Bridgestone","BRKO":"Birko Mensucat",
    "BRMEN":"Birlik Mensucat","BRSAN":"Borusan Mannesmann Boru","BRYAT":"Borusan Yatırım",
    "BSOKE":"Batısöke Çimento","BTCIM":"Batıçim Batı Anadolu Çimento","BUCIM":"Bursa Çimento",
    "BURCE":"Burçelik","BURVA":"Burçelik Vana","BVSAN":"Bülbüloğlu Vinç Sanayi",
    "BYDNR":"Baydöner","CANTE":"Can2 Termik","CASA":"Casa Emtia",
    "CATES":"Çatalağzı Termik","CCOLA":"Coca-Cola İçecek","CELHA":"Çelik Halat",
    "CEMAS":"Çemaş Döküm Sanayi","CEMTS":"Çemtaş Çelik","CIMSA":"Çimsa Çimento",
    "CLEBI":"Çelebi Hava Servisi","CONSE":"Consus Enerji","CVMEK":"Cvmek Makina",
    "CWENE":"CW Enerji","DAGHL":"Dagi Yatırım Holding","DAGI":"Dagi Giyim Sanayi",
    "DAPGM":"Dap Gayrimenkul","DARDL":"Dardanel Önentaş","DENGE":"Denge Yatırım Holding",
    "DERHL":"Derlüks Yatırım Holding","DERIM":"Derimod Konfeksiyon","DESA":"Desa Deri Sanayi",
    "DESPC":"Despec Bilgisayar","DEVA":"Deva Holding","DGGYO":"Doğuş GYO",
    "DGNMO":"Doğanlar Mobilya","DIRIT":"Diriliş Tekstil","DITAS":"Ditaş Doğan",
    "DMSAS":"Demisaş Döküm","DOAS":"Doğuş Otomotiv","DOCO":"DO & CO Restaurants",
    "DOHOL":"Doğan Şirketler Grubu","DOKTA":"Döktaş Dökümcülük","DURDO":"Duran Doğan Basım",
    "DYOBY":"DYO Boya","DZGYO":"Denizli GYO","EDATA":"E-Data Teknoloji",
    "EDIP":"Edip Gayrimenkul","EFOR":"Efor Yatırım","EGEEN":"Ege Endüstri",
    "EGGUB":"Ege Gübre","EGPRO":"Ege Profil","EGSER":"Ege Seramik",
    "EKGYO":"Emlak Konut GYO","EKOS":"Ekos Teknoloji","EKSUN":"Eksun Gıda",
    "ELITE":"Elite Naturel","EMKEL":"Emkel Elektrik","EMNIS":"Emniyet Ticaret",
    "ENERY":"Enerya Enerji","ENJSA":"Enerjisa Enerji","ENKAI":"Enka İnşaat",
    "ERBOS":"Erbosan Erciyas Boru","EREGL":"Ereğli Demir ve Çelik","ERSU":"Ersu Gıda",
    "ESCAR":"Escar Filo Kiralama","ESEN":"Esenboğa Elektrik","ETILR":"Etiler Gıda",
    "ETRAF":"Etrafor Enerji","EUPWR":"Europower Enerji","EUREN":"Europen Endüstri",
    "EYGYO":"EyG GYO","FADE":"Fade Gıda","FENER":"Fenerbahçe Sportif",
    "FLAP":"Flap Kongre Toplantı","FMIZP":"Federal-Mogul İzmit Piston","FONET":"Fonet Bilgi",
    "FORMT":"Formet Metal","FRIGO":"Frigo-Pak Gıda","FROTO":"Ford Otosan",
    "FZLGY":"Fuzul GYO","GARAN":"Garanti BBVA Bankası","GARFA":"Garanti Faktoring",
    "GEDIK":"Gedik Yatırım Menkul","GEDZA":"Gediz Ambalaj","GENTS":"Gentaş Genel Metal",
    "GEREL":"Gersan Elektrik","GESAN":"Girişim Elektrik Taahhüt","GIPTA":"Gıpta Ofis",
    "GLBMD":"Global Menkul Değerler","GLCVY":"Gelecek Varlık Yönetimi","GLRYH":"Güler Yatırım Holding",
    "GLYHO":"Global Yatırım Holding","GOKNR":"Göknur Gıda","GOLTS":"Göltaş Göller Bölgesi",
    "GOODY":"Goodyear Lastikleri","GOZDE":"Gözde Girişim Sermayesi","GRSEL":"Gür-Sel Turizm",
    "GSDDE":"GSD Denizcilik","GSDHO":"GSD Holding","GSRAY":"Galatasaray Sportif",
    "GUBRF":"Gübre Fabrikaları","GWIND":"Galata Wind Enerji","GZNMI":"Gezinomi Seyahat",
    "HALKB":"Türkiye Halk Bankası","HATEK":"Hatay Tekstil","HDFGS":"Hedef Girişim Sermayesi",
    "HEKTS":"Hektaş Ticaret","HKTM":"Hidropar Hareket Kontrol","HOROZ":"Horoz Lojistik",
    "HUBVC":"Hub Girişim","HUNER":"Hun Enerji","HURGZ":"Hürriyet Gazetecilik",
    "ICBCT":"ICBC Turkey Bank","IDGYO":"İdeal GYO","IEYHO":"Işıklar Enerji Yapı Holding",
    "IHEVA":"İhlas Ev Aletleri","IHGZT":"İhlas Gazetecilik","IHLAS":"İhlas Holding",
    "IHLGM":"İhlas Gayrimenkul","IHYAY":"İhlas Yayın Holding","IMASM":"İmaş Makina Sanayi",
    "INDES":"İndeks Bilgisayar","INFO":"İnfo Yatırım","INGRM":"Ingram Bilişim",
    "INTEM":"İntema İnşaat ve Tesisat","INVEO":"Inveo Yatırım Holding","INVES":"Investco Holding",
    "IPEKE":"İpek Doğal Enerji","ISCTR":"Türkiye İş Bankası (C)","ISDMR":"İskenderun Demir Çelik",
    "ISFIN":"İş Finansal Kiralama","ISGYO":"İş GYO","ISMEN":"İş Yatırım Menkul",
    "ISSEN":"İşbir Sentetik Dokuma","ISYAT":"İş Yatırım Ortaklığı","IZENR":"İzdemir Enerji",
    "IZFAS":"İzmir Fırça","IZMDC":"İzmir Demir Çelik","JANTS":"Jantsa Jant Sanayi",
    "KAPLM":"Kaplamin Ambalaj","KAREL":"Karel Elektronik","KARSN":"Karsan Otomotiv",
    "KARYE":"Kartal Yenilenebilir Enerji","KATMR":"Katmerciler Araç","KAYSE":"Kayseri Şeker",
    "KCAER":"Kocaer Çelik","KCHOL":"Koç Holding","KENT":"Kent Gıda Maddeleri",
    "KERVT":"Kerevitaş Gıda","KFEIN":"Kafein Yazılım","KGYO":"Koray GYO",
    "KIMMR":"Kimteks Poliüretan","KLGYO":"Kiler GYO","KLKIM":"Kalekim Kimyevi Maddeler",
    "KLMSN":"Klimasan Klima","KLRHO":"Kiler Holding","KLSYN":"Kolesin Mobilya",
    "KLYAS":"Kalyon Yatırım","KMPUR":"Kimteks Poliüretan","KNFRT":"Konfrut Gıda",
    "KONTR":"Kontrolmatik Teknoloji","KONYA":"Konya Çimento","KOPOL":"Koza Polyester",
    "KORDS":"Kordsa Teknik Tekstil","KOTON":"Koton Mağazacılık","KOZAA":"Koza Madencilik",
    "KOZAL":"Koza Altın İşletmeleri","KRDMA":"Kardemir Karabük Demir A","KRDMB":"Kardemir B",
    "KRDMD":"Kardemir D","KRPLS":"Koroplast Ambalaj","KRVGD":"Kervan Gıda",
    "KSTUR":"Kuştur Kuşadası Turizm","KUTPO":"Kütahya Porselen","KUVVA":"Kuvva Gıda",
    "LIDER":"Lider Faktoring","LILAK":"Lila Kağıt","LINK":"Link Bilgisayar",
    "LKMNH":"Lokman Hekim","LOGO":"Logo Yazılım","LRSHO":"Lares Holding",
    "MAALT":"Marmaris Altınyunus","MAGEN":"Margün Enerji","MAKIM":"Makim Makine",
    "MAKTK":"Makina Takım Endüstrisi","MANAS":"Manas Enerji Yönetimi","MARKA":"Marka Yatırım Holding",
    "MARTI":"Martı Otel İşletmeleri","MAVI":"Mavi Giyim Sanayi","MEDTR":"Meditera Tıp",
    "MEGAP":"Mega Polietilen","MEPET":"Mepet Petrol","MGROS":"Migros Ticaret",
    "MIATK":"Mia Teknoloji","MIPAZ":"Milpa Ticari","MNDRS":"Menderes Tekstil",
    "MOGAN":"Mogan Enerji","MPARK":"MLP Sağlık Hizmetleri","MRGYO":"Martı GYO",
    "MRSHL":"Marshall Boya","MTRKS":"Matriks Bilgi Dağıtım","MZHLD":"Mazhar Zorlu Holding",
    "NATEN":"Naturel Enerji","NETAS":"Netaş Telekomünikasyon","NIBAS":"Niğbaş Niğde Beton",
    "NTHOL":"Net Holding","NUGYO":"Nurol GYO","NUHCM":"Nuh Çimento",
    "OBASE":"Obase Bilgisayar","ODAS":"Odaş Elektrik Üretim","ODINE":"Odine Teknoloji",
    "ONCSM":"Oncosem Onkolojik","ORCAY":"Orçay Ortaköy Çay","ORGE":"Orge Enerji",
    "ORMA":"Orma Orman Mahsulleri","OTKAR":"Otokar Otomotiv","OYAKC":"Oyak Çimento",
    "OYLUM":"Oylum Tarım","OZGYO":"Özak GYO","OZKGY":"Özak GYO","OZSUB":"Özsu Balık",
    "PAGYO":"Panora GYO","PAMEL":"Pamel Yenilenebilir Enerji","PAPIL":"Papilon Savunma",
    "PARSN":"Parsan Makina","PASEU":"Pasifik Eurasia Lojistik","PATEK":"Pasifik Teknoloji",
    "PENTA":"Penta Teknoloji Ürünleri","PETKM":"Petkim Petrokimya","PETUN":"Pınar Et ve Un",
    "PGSUS":"Pegasus Hava Taşımacılığı","PINSU":"Pınar Su","PKART":"Plastkart Plastik Kart",
    "PNLSN":"Panelsan Çatı Cephe","POLHO":"Polisan Holding","POLTK":"Politeknik Metal",
    "PRKAB":"Türk Prysmian Kablo","QUAGR":"Qua Granite Hayal Yapı",
    "REEDR":"Reeder Teknoloji","RGYAS":"Reysaş GYO","RTALB":"Rta Laboratuvarları",
    "RUBNS":"Rubenis Tekstil","RYGYO":"Reysa Gayrimenkul","RYSAS":"Reysaş Taşımacılık",
    "SAHOL":"Hacı Ömer Sabancı Holding","SAMAT":"Saray Matbaacılık","SANKO":"Sanko Pazarlama",
    "SARKY":"Sarkuysan Elektrolitik Bakır","SASA":"Sasa Polyester Sanayi","SAYAS":"Say Yenilenebilir",
    "SDTTR":"SDT Uzay ve Savunma","SELEC":"Selçuk Ecza Deposu","SELGD":"Selçuk Gıda",
    "SEMAS":"Semaş Seferihisar Tarımsal","SEYKM":"Seyitler Kimya","SILVR":"Silverline Endüstri",
    "SISE":"Türkiye Şişe ve Cam","SKBNK":"Şekerbank","SMCRT":"Smart Güneş Enerjisi",
    "SNGYO":"Sinpaş GYO","SNKRN":"Sanko Tekstil","SNPAM":"Sanpaz",
    "SOKM":"Şok Marketler","SUMAS":"Suma Turizm","SUNEKS":"Sunekspres Alüminyum",
    "SURGY":"Sürgülü PVC Profil","SUWEN":"Suwen Tekstil","TABGD":"Tab Gıda",
    "TARKM":"Tarkim Bitki Koruma","TAVHL":"Tav Havalimanları Holding","TCELL":"Turkcell İletişim",
    "TDGYO":"Trend GYO","TEKTU":"Tek-Art Turizm","TEZOL":"Tezol Kağıt",
    "THYAO":"Türk Hava Yolları","TKFEN":"Tekfen Holding","TKNSA":"Teknosa İç ve Dış",
    "TLMAN":"Tuğla Sanayii","TMSN":"Tümosan Motor ve Traktör","TNZTP":"Tanı Türkiye",
    "TOASO":"Tofaş Türk Otomobil Fabrikası","TRGYO":"Torunlar GYO","TRILC":"Trilc Eğitim",
    "TSKB":"Türkiye Sınai Kalkınma Bankası","TSPOR":"Trabzonspor","TTKOM":"Türk Telekom",
    "TTRAK":"Türk Traktör ve Ziraat Makineleri","TUCLK":"Tuçap Tüm Çatı Profil",
    "TUPRS":"Tüpraş-Türkiye Petrol Rafinerileri","TURGG":"Türkerler Gayrimenkul",
    "TURSG":"Türkiye Sigorta","TVKBY":"Tevkifatlı Devlet Varlık Fonu",
    "ULUFA":"Ulus Fason","ULUSE":"Ulusoy Elektrik","ULUUN":"Ulusoy Un",
    "ULKER":"Ülker Bisküvi Sanayi","USDTR":"USD Türkiye","USMO":"Uşak Seramik",
    "VAKBN":"Türkiye Vakıflar Bankası","VAKFN":"Vakıf Finansal Kiralama",
    "VAKGM":"Vakıf GYO","VBTYZ":"VBT Yazılım","VERUS":"Verus Yatırım",
    "VESBE":"Vestel Beyaz Eşya","VESTL":"Vestel Elektronik","VKGYO":"Vakıf GYO",
    "VKFRT":"Vakıf Faktoring","YATAS":"Yataş Yatak ve Yorgan","YATGS":"Yat Girişim",
    "YAYLA":"Yayla Agro Gıda","YBTAS":"YBT Anonim","YGYO":"Yeni Gimat GYO",
    "YKBNK":"Yapı ve Kredi Bankası","YKSLN":"Yükselen Çelik","YPKME":"Yapı Kredi Sigorta",
    "YYLGD":"Yaylası Gıda","YYAPI":"Yükselen Yapı","ZEDUR":"Zedur Enerji",
    "ZOREN":"Zorlu Enerji Elektrik","ZRGYO":"Ziraat GYO",
    # Ek popüler hisseler
    "ACLST":"Acılist","ADACM":"Ada Cam","ADBGR":"Adabor Gayrimenkul",
    "ADNAC":"Adana Çimento (A)","ADNAH":"Adana Çimento (H)","ADRNS":"Adrenalın Psikoloji",
    "AFMAS":"Afyon Maden Suları","AGIDA":"Altın Gıda","AIBRE":"AI Boru",
    "AIKME":"Aiken Metal","AIPGY":"AIP Gayrimenkul","AIRTL":"Air Türkiye",
    "AKASH":"Akaş Basın Yayın","AKBIM":"Ak Bim Birleşik","AKCAM":"Ak Cam",
    "AKDNZ":"Akdeniz Kimya","AKFIN":"Ak Finansal","AKGMI":"Akgün Mimarlık",
    "AKMKR":"Ak Makine","AKPAZ":"Ak Pazarlama","AKPOL":"Ak Polimer",
    "AKSEL":"Ak Selanik","AKTAS":"Aktaş Elektrik","AKYAT":"Ak Yatırım Ortaklığı",
    "ALARK":"Alarko Holding","ALBKG":"Albaraka Katılım Bankası","ALFAS":"Alfasolar",
    "ALFER":"Al Ferrum","ALGEM":"Al Gem Mücevherat","ALGYO":"Alarko GYO",
    "ALHS":"Al Hisse Senedi","ALIAT":"Alia Teknoloji","ALKGY":"Alka Gayrimenkul",
    "ALKLC":"Alkim Alkali Kimya","ALKTL":"Alkat Türkiye","ALPER":"Alper Menkul",
    "ALPOL":"Al Polimer","ALTINS":"Altın Sofra","ALTUR":"Altın Turistik",
    "AMAGS":"Amasya Gıda Sanayi","AMDNZ":"Akdeniz Madencilik","AMEGY":"Amegy",
    "AMTEK":"Am Teknoloji","AMTM":"Amtm Enerji","ANAKS":"Anka Sağlık",
    "ANAR":"Anareks Mühendislik","ANELE":"Anel Elektrik","ANEM":"Anem Enerji",
    "ANFER":"Anfer Çelik","ANFIL":"Anfil Filtrasyon","ANGYO":"Ankara GYO",
    "ANKTR":"Ankara Trafo","ANMED":"Anadolu Medikal","ANRGY":"Anadolu Rüzgar",
    "ANTBR":"Antbirlik Pamuk","ANTEK":"Antek Teknoloji","ARACS":"Araç Sanayi",
    "ARBIT":"Arbit Mühendislik","ARCML":"Ar Çam Levha","ARCOR":"Ar Koruma",
    "ARDGL":"Ardahanlı Gıda","ARDFN":"Ard Finans","AREDM":"Ar Edm Boru",
    "AREKS":"Areks Elektrik","ARENTA":"Arenta Kurumsal Kiralama","ARFIN":"Ar Finans",
    "ARFON":"Arfon Çimento","ARGEM":"Ar Gem","ARGRO":"Ar Gro Tarım",
    "ARHOL":"Ar Holding","ARIND":"Ar İnşaat","ARIAS":"Ar Isı",
    "ARKIM":"Ar Kim Kimya","ARKLY":"Ar Kule","ARMDA":"Armada Bilgisayar",
    "ARMES":"Ar Mes Demir","ARMET":"Ar Metal","ARMTR":"Ar Motorlu Araçlar",
    "ARNOS":"Ar Nos Tekstil","ARPAZ":"Ar Pazarlama","ARSAN":"Arsan Tekstil",
    "ARSEV":"Ar Sev Sanayi","ARSIN":"Arsinoks","ARTMS":"Ar Temiz Su",
    "ARTOG":"Ar Toğrol","ARTSA":"Artsa Cam","ARTUN":"Ar Tuna Tekstil",
    "ARVER":"Ar Verimlilik","ARVMS":"Ar Vms Deniz","ARYES":"Ar Yes Enerji",
    "ASCEL":"As Çelik","ASCTN":"As Çetin","ASELS":"Aselsan",
    "ASEND":"As End Mühendislik","ASENS":"As Ens Enerji","ASGYO":"As GYO",
    "ASLAN":"Aslan Çimento","ASMED":"As Medikal","ASMIN":"As Miner Madencilik",
    "ASNAS":"As Nas Tekstil","ASPRO":"As Pro Bilişim","ASREP":"As Repro",
    "ASTEP":"As Tep Tekstil","ATAKM":"Atak Mobilya","ATASL":"Ata Slab",
    "ATATK":"Atatürk Tekstil","ATEKS":"Altınyıldız Tekstil","ATES":"Ateş Tekstil",
    "ATGYM":"At Gayrimenkul","ATHOL":"At Holding","ATKAR":"At Kargo",
    "ATKMS":"At Kimse","ATLAN":"Atlantis Yatırım","ATLIC":"At Liç",
    "ATMEY":"At Mey İçecek","ATPAZ":"At Pazarlama","ATRAV":"At Ravi",
    "ATRFS":"At Rfs Faktoring","ATSAL":"At Sal Turizm","ATSIM":"At Simica",
    "ATSIM":"At Simica","ATSTR":"At Star Tekstil","ATTEK":"At Teknoloji",
    "ATUR":"Atur Turizm","ATVAN":"At Van Ulaşım","ATVLR":"At Valer Mühendislik",
    "ATYAT":"At Yatırım","ATYOL":"At Yol Sanayi","AUKAN":"Au Kan",
    "AUTEK":"Au Tek Teknoloji","AVHN":"Avhan Mühendislik","AVISA":"Avisa",
    "AVLYA":"Avliya Gıda","AVOD":"Avod Gıda","AVPAS":"Av Paş Tekstil",
    "AVRAS":"Av Ras Gayrimenkul","AVTUR":"Av Tur Turizm","AVYAS":"Av Yas",
    "AYCES":"Ayces Turizm","AYDIN":"Aydın Tekstil","AYEN":"Ayen Enerji",
    "AYENK":"Ay Enk Enerji","AYFER":"Ay Fer Kimya","AYGAS":"Ay Gaz",
    "AYHOL":"Ay Holding","AYKAR":"Ay Kar Tekstil","AYKIM":"Ay Kim Kimya",
    "AYLES":"Ay Les Tekstil","AYMAP":"Ay Map Tekstil","AYMET":"Ay Met Metal",
    "AYNES":"Ay Nes Tekstil","AYPAZ":"Ay Paz Pazarlama","AYSAN":"Ay San Sanayi",
    "AYSEL":"Ay Sel Tarım","AYŞIM":"Ay Şim Şimi","AYTAS":"Ay Taş Enerji",
    "AYTEK":"Ay Tek Teknoloji","AYTUR":"Ay Tur Turizm","AYVES":"Ay Ves Vestiyer",
    "AYVAZ":"Ayvaz Sanayi","AZTEK":"Aztek Elektronik","AZZAP":"Az Zap",
    # Finans ve bankacılık
    "BNTAS":"Bantaş","BOYNR":"Boyner Büyük Mağazacılık","BRKVY":"Birlik Kıymetli",
    "BRSA":"Brisa","BURCE":"Burçelik","BURVA":"Burçelik Vana",
    "BYNO":"Beyon Medya","BYTAS":"By Taş","BZTAS":"Bz Taş Gayrimenkul",
    # Daha fazla sektör hisseleri
    "CMPNY":"Çimpa Çimento","CRDFA":"Credif","CRFSA":"Carrefoursa",
    "CSGYO":"Çeşme GYO","CSGRP":"Çınar Grup","CUKRS":"Cukorova Tekstil",
    "CMBTN":"Çimbeton","CMCDI":"Çimco Madencilik","CMTAS":"Çimtaş Çimento",
    "CNDAL":"Çandarlı","CNPAS":"Çin Paş","CORUH":"Çoruh Elektrik",
    "CRDYO":"Çuha Dorduncuoğlu","CSGYO":"Çeşme GYO",
    # Çeşitli diğer hisseler
    "DAGHL":"Dagi Holding","DAPGM":"Dap GYO","DARDL":"Dardanel",
    "DBPAZ":"Db Pazarlama","DBTEK":"Db Teknoloji","DBYAS":"Db Yas",
    "DCFIN":"Dc Finans","DCTTR":"Dc Tır","DDTEK":"Dd Teknoloji",
    "DENAS":"Denas Mühendislik","DENIZ":"Deniz Finansal","DENYR":"Denizli Yem",
    "DERHL":"Derlüks","DERIM":"Derimod","DESA":"Desa Deri",
    "DESPC":"Despec","DEVA":"Deva","DFNCO":"Dfn Co",
    "DGZTE":"Doğan Gazetecilik","DIRGN":"Dirgen Metal","DISEL":"Disel",
    "DNISI":"Deniz İşletmeleri","DNIYO":"Denizli Yoğurt","DOAS":"Doğuş Otomotiv",
    "DOCO":"DO & CO","DOHOL":"Doğan Holding","DOKTA":"Döktaş",
    "DORCE":"Dorce Prefabrik","DRDKO":"Drd Ko Tekstil","DSELN":"Dseln Holding",
    "DSKOP":"Ds Kop","DSTG":"Ds Tg Mühendislik","DTAVH":"Dt Avh",
    "DTRAK":"Türk Traktör","DUMON":"Du Mon Gıda","DUNKN":"Dunkin",
    "DUNST":"Dun St Tekstil","DURDO":"Duran Doğan","DVRNT":"Dövrent",
    "DYOBY":"Dyo Boya","DYTNT":"Dyt Nt Teknoloji","DZFIN":"Dz Finans",
    "DZGYO":"Denizli GYO","DZHO":"Denizli Holding",
    # Son 100 ek hisse
    "EDATA":"E-Data","EDIP":"Edip GYO","EFOR":"Efor",
    "EGEEN":"Ege Endüstri","EGGUB":"Ege Gübre","EGPRO":"Ege Profil",
    "EGSER":"Ege Seramik","EKGYO":"Emlak Konut GYO","EKOS":"Ekos",
    "EKSUN":"Eksun","ELITE":"Elite","EMKEL":"Emkel",
    "EMNIS":"Emniyet","ENERY":"Enerya","ENJSA":"Enerjisa",
    "ENKAI":"Enka","ERBOS":"Erbosan","EREGL":"Ereğli",
    "ERSU":"Ersu","ESCAR":"Escar","ESEN":"Esenboğa",
    "ETILR":"Etiler","ETRAF":"Etrafor","EUPWR":"Europower",
    "EUREN":"Europen","EYGYO":"EyG GYO","FADE":"Fade",
    "FENER":"Fenerbahçe","FLAP":"Flap","FMIZP":"Federal-Mogul",
    "FONET":"Fonet","FORMT":"Formet","FRIGO":"Frigo-Pak",
    "FROTO":"Ford Otosan","FZLGY":"Fuzul GYO","GARAN":"Garanti BBVA",
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
                ad_col  = next((c for c in tbl.columns if any(k in str(c).lower() for k in ["şirket","ad","unvan"])), None)
                kodlar = tbl[kod_col].dropna().astype(str).str.strip().str.upper().tolist()
                adlar  = tbl[ad_col].dropna().astype(str).tolist() if ad_col else kodlar
                sonuc  = {}
                for k, a in zip(kodlar, adlar):
                    if 2 <= len(k) <= 6 and k.isalpha():
                        sonuc[k] = a
                if len(sonuc) > 20:
                    return dict(sorted({**BIST_STATIK, **sonuc}.items()))
    except:
        pass
    return dict(sorted(BIST_STATIK.items()))

bist_100_full = bist_hisse_listesi_getir()
hisse_listesi = [f"{kod} - {ad}" for kod, ad in bist_100_full.items()]

# ============================================================
# YARDIMCI / TEKNİK ANALİZ FONKSİYONLARI
# ============================================================
@st.cache_data(ttl=300)
def veri_indir(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        return data if not data.empty else None
    except:
        return None

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
    s   = seri.rolling(periyot).std()
    return ort + std * s, ort, ort - std * s

def hesapla_stochastic(data, k=14, d=3):
    low_min  = data['Low'].rolling(k).min()
    high_max = data['High'].rolling(k).max()
    K = 100 * (data['Close'] - low_min) / (high_max - low_min)
    return K, K.rolling(d).mean()

def hesapla_atr(data, periyot=14):
    h = data['High']; l = data['Low']; c = data['Close'].shift(1)
    tr = pd.concat([h-l, (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
    return tr.rolling(periyot).mean()

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
        f = seri.iloc[-1]
        bb = 'AL' if f < alt.iloc[-1] else ('SAT' if f > ust.iloc[-1] else 'BEKLE')
        sinyaller['Bollinger'] = {'deger': f"Ort:{ort.iloc[-1]:.2f}", 'sinyal': bb, 'renk': '#00ff88' if bb == 'AL' else ('#ff4444' if bb == 'SAT' else '#ffaa00')}
        skor += 1 if bb == 'AL' else (-1 if bb == 'SAT' else 0)
    except: pass
    try:
        ma20 = seri.rolling(20).mean().iloc[-1]; ma50 = seri.rolling(50).mean().iloc[-1]; f = seri.iloc[-1]
        s = 'AL' if f > ma20 > ma50 else ('SAT' if f < ma20 < ma50 else 'BEKLE')
        sinyaller['MA Trendi'] = {'deger': f"MA50:{ma50:.2f}", 'sinyal': s, 'renk': '#00ff88' if s == 'AL' else ('#ff4444' if s == 'SAT' else '#ffaa00')}
        skor += 1 if f > ma50 else -1
    except: pass
    try:
        if data is not None:
            k, d = hesapla_stochastic(data)
            ks, ds = k.iloc[-1], d.iloc[-1]
            s = 'AL' if ks < 20 else ('SAT' if ks > 80 else 'BEKLE')
            sinyaller['Stochastic'] = {'deger': f"K:{ks:.1f} D:{ds:.1f}", 'sinyal': s, 'renk': '#00ff88' if ks < 20 else ('#ff4444' if ks > 80 else '#ffaa00')}
            skor += 1 if ks < 20 else (-1 if ks > 80 else 0)
    except: pass
    genel = 'GÜÇLÜ AL' if skor >= 3 else ('AL' if skor >= 1 else ('GÜÇLÜ SAT' if skor <= -3 else ('SAT' if skor <= -1 else 'BEKLE')))
    return sinyaller, skor, genel

# ============================================================
# MAİL FONKSİYONU
# ============================================================
def alarm_maili_gonder(alici_mail, hisse, tur, alarm_fiyat, gercek_fiyat):
    try:
        gonderen = st.secrets["GMAIL_USER"]
        sifre    = st.secrets["GMAIL_APP_PASSWORD"]
    except:
        return False, "Secrets bulunamadı"
    yon_emoji = "🚀" if tur == "Üstüne Çıkarsa" else "📉"
    konu = f"{yon_emoji} BIST Alarm: {hisse} fiyat hedefine ulaştı!"
    renk = '#00ff88' if tur == 'Üstüne Çıkarsa' else '#ff4444'
    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#0a0a0f;color:#e2e8f0;padding:24px">
      <div style="max-width:480px;margin:auto;background:#0f1520;border:1px solid #1e2a3a;border-radius:10px;padding:28px">
        <div style="font-size:22px;font-weight:700;color:#00d4ff;margin-bottom:4px">◈ BIST Terminal Pro</div>
        <div style="font-size:12px;color:#4a6080;margin-bottom:24px">Otomatik Fiyat Alarmı</div>
        <div style="background:#1a1a2e;border-left:4px solid {renk};border-radius:6px;padding:16px;margin-bottom:20px">
          <div style="font-size:28px;font-weight:700;color:{renk}">{yon_emoji} {hisse}</div>
          <div style="font-size:14px;color:#8899aa;margin-top:6px">{tur} alarmı tetiklendi</div>
        </div>
        <table style="width:100%;border-collapse:collapse">
          <tr><td style="padding:8px 0;color:#4a6080;font-size:13px">Alarm Fiyatı</td>
              <td style="padding:8px 0;color:#e2e8f0;font-weight:600;text-align:right">{alarm_fiyat:.2f} TL</td></tr>
          <tr style="border-top:1px solid #1e2a3a">
              <td style="padding:8px 0;color:#4a6080;font-size:13px">Gerçekleşen Fiyat</td>
              <td style="padding:8px 0;color:#00d4ff;font-weight:700;text-align:right">{gercek_fiyat:.2f} TL</td></tr>
          <tr style="border-top:1px solid #1e2a3a">
              <td style="padding:8px 0;color:#4a6080;font-size:13px">Tarih / Saat</td>
              <td style="padding:8px 0;color:#8899aa;font-size:12px;text-align:right">{datetime.now().strftime('%d.%m.%Y %H:%M')}</td></tr>
        </table>
        <div style="margin-top:24px;padding:12px;background:#0a0a0f;border-radius:6px;font-size:11px;color:#2a3a4a;line-height:1.6">
          Bu mail BIST Terminal Pro tarafından otomatik gönderilmiştir.<br>Bu bir yatırım tavsiyesi değildir.
        </div>
      </div>
    </body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = konu; msg["From"] = gonderen; msg["To"] = alici_mail
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gonderen, sifre)
            server.sendmail(gonderen, alici_mail, msg.as_string())
        return True, "Mail gönderildi"
    except Exception as e:
        return False, str(e)

# ============================================================
# AI ANALİZ (Groq)
# ============================================================
def ai_analiz_yap(kod, ad, fiyat, degisim, rsi, genel_sinyal, seri):
    cache_key = f"{kod}_{datetime.now().strftime('%Y%m%d%H')}"
    if cache_key in st.session_state.ai_cache:
        return st.session_state.ai_cache[cache_key]
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
    except:
        return "⚠ Groq API key bulunamadı."
    try:
        son7 = seri.iloc[-7:].pct_change().dropna() * 100
        y52h = seri.rolling(252).max().iloc[-1]
        y52l = seri.rolling(252).min().iloc[-1]
        prompt = f"""Sen deneyimli bir BIST analistisin. {kod} ({ad}) hissesi için kısa ve net analiz yaz.
Güncel Fiyat: {fiyat:.2f} TL | Günlük: {degisim:+.2f}% | RSI: {rsi:.1f} | Sinyal: {genel_sinyal}
Son 7 Gün: {son7.mean():.2f}% ort | 52H Yüksek: {y52h:.2f} | 52H Düşük: {y52l:.2f}
Başlıklar: 1.Teknik Görünüm 2.Kısa Vadeli Beklenti 3.Risk Faktörleri 4.Sonuç
Türkçe, max 150 kelime, profesyonel, olasılık dili kullan."""
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {groq_key}"},
            json={"model": "llama-3.3-70b-versatile", "max_tokens": 1024, "temperature": 0.7,
                  "messages": [{"role": "system", "content": "Profesyonel Türk borsa analisti."},
                                {"role": "user", "content": prompt}]},
            timeout=30
        )
        if res.status_code == 200:
            text = res.json()["choices"][0]["message"]["content"]
            st.session_state.ai_cache[cache_key] = text
            return text
        return f"⚠ Groq API hatası: {res.status_code}"
    except Exception as e:
        return f"⚠ Bağlantı hatası: {e}"

# ============================================================
# HEADER
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

# ============================================================
# AUTH MODAL — Tab'ların ÜSTÜNDE render et
# ============================================================
auth_modal_ana()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="section-title">⚙ KONTROL PANELİ</div>', unsafe_allow_html=True)

    # ---- HİSSE ARAMA KUTUSU ----
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;letter-spacing:1px;margin-bottom:6px">🔍 HİSSE ARA</div>', unsafe_allow_html=True)
    arama_metni = st.text_input(
        "Hisse ara:",
        placeholder="Kod veya şirket adı yazın... (ör: GARAN, Garanti)",
        key="sidebar_arama",
        label_visibility="collapsed"
    )

    # Arama sonuçlarına göre filtrele
    if arama_metni and len(arama_metni.strip()) >= 1:
        arama_lower = arama_metni.strip().lower()
        filtrelenmis_liste = [
            h for h in hisse_listesi
            if arama_lower in h.lower()
        ]
        if not filtrelenmis_liste:
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#ff4444;
            padding:8px;background:#1a0000;border-radius:4px;border:1px solid #ff444422">
                ⚠ "{arama_metni}" için sonuç bulunamadı
            </div>""", unsafe_allow_html=True)
            filtrelenmis_liste = hisse_listesi  # Boş arama ise tümünü göster
        else:
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a6080;margin:4px 0 6px 0">
                📊 {len(filtrelenmis_liste)} hisse bulundu
            </div>""", unsafe_allow_html=True)
    else:
        filtrelenmis_liste = hisse_listesi
        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#2a3a4a;margin:2px 0 6px 0">
            Toplam {len(hisse_listesi)} hisse mevcut
        </div>""", unsafe_allow_html=True)

    # Hisse seçme dropdown — arama sonuçlarından
    default_idx = 0
    # GARAN'ı bul
    for i, h in enumerate(filtrelenmis_liste):
        if "GARAN" in h:
            default_idx = i
            break

    ana_secim = st.selectbox(
        "Hisse Seç:",
        filtrelenmis_liste,
        index=min(default_idx, len(filtrelenmis_liste)-1),
        key="hisse_secim"
    )
    t_kod = ana_secim.split(" - ")[0]
    t_ad  = ana_secim.split(" - ")[1]

    # Seçili hisse bilgi kartı
    st.markdown(f"""
    <div style="background:#0f1520;border:1px solid #1e2a3a;border-left:2px solid #00d4ff;
    border-radius:6px;padding:8px 12px;margin:6px 0 12px 0">
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#00d4ff;font-weight:700">{t_kod}</div>
        <div style="font-size:11px;color:#4a6080;margin-top:2px">{t_ad}</div>
    </div>
    """, unsafe_allow_html=True)

    t_sure_etiket = st.radio("Periyot:", ["1 Ay", "3 Ay", "1 Yıl", "3 Yıl", "5 Yıl"], index=2)
    t_periyot = {"1 Ay": "1mo", "3 Ay": "3mo", "1 Yıl": "1y", "3 Yıl": "3y", "5 Yıl": "5y"}
    t_aralik  = {"1 Ay": "1h",  "3 Ay": "1d",  "1 Yıl": "1d", "3 Yıl": "1wk", "5 Yıl": "1wk"}
    secilen_periyot = t_periyot[t_sure_etiket]
    secilen_aralik  = t_aralik[t_sure_etiket]

    st.markdown("---")
    st.markdown('<div class="section-title">🔔 FİYAT ALARMLARI</div>', unsafe_allow_html=True)

    if not st.session_state.user:
        st.markdown("""
        <div class="alarm-active" style="border-color:#00d4ff33;border-left-color:#00d4ff">
            🔐 Alarm eklemek için giriş yapın.<br>
            <span style="font-size:10px">Sağ üstten kayıt olabilirsiniz.</span>
        </div>""", unsafe_allow_html=True)
    else:
        alarm_hisse = st.selectbox("Hisse:", hisse_listesi, key="alarm_h")
        alarm_tur   = st.radio("Tür:", ["Üstüne Çıkarsa", "Altına Düşerse"], horizontal=True)
        alarm_fiyat = st.number_input("Fiyat (TL):", min_value=0.01, format="%.2f", key="alarm_f")
        alarm_mail  = st.text_input("📧 E-posta:", value=st.session_state.user_email, key="alarm_mail")

        if st.button("⚡ Alarm Ekle", use_container_width=True):
            alarm_kod = alarm_hisse.split(" - ")[0]
            if alarm_ekle(st.session_state.user_id, alarm_kod, alarm_tur, alarm_fiyat, alarm_mail.strip()):
                st.success("✅ Alarm eklendi!")
                st.rerun()

        if st.session_state.alarmlar:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#4a6080;margin:8px 0 4px">AKTİF ALARMLAR</div>', unsafe_allow_html=True)
            for alarm in st.session_state.alarmlar:
                try:
                    d = yf.download(f"{alarm['hisse']}.IS", period="1d", progress=False)
                    if d.empty: continue
                    g_fiyat = float(d['Close'].iloc[-1].iloc[0]) if isinstance(d.columns, pd.MultiIndex) else float(d['Close'].iloc[-1])

                    tetiklendi = (
                        (alarm['tur'] == "Üstüne Çıkarsa" and g_fiyat >= alarm['fiyat']) or
                        (alarm['tur'] == "Altına Düşerse"  and g_fiyat <= alarm['fiyat'])
                    )

                    if tetiklendi and alarm.get('mail'):
                        mail_key = f"{alarm['id']}_{alarm['fiyat']}"
                        son = st.session_state.mail_gonderildi.get(mail_key)
                        simdi = datetime.now()
                        if son is None or (simdi - son).total_seconds() > 3600:
                            ok, msg = alarm_maili_gonder(alarm['mail'], alarm['hisse'], alarm['tur'], float(alarm['fiyat']), g_fiyat)
                            if ok:
                                st.session_state.mail_gonderildi[mail_key] = simdi
                                alarm_tetiklendi_guncelle(alarm['id'])
                                st.toast(f"📧 {alarm['hisse']} alarmı {alarm['mail']} adresine gönderildi!", icon="✅")
                            else:
                                st.toast(f"⚠ Mail gönderilemedi: {msg}", icon="❌")

                    a1, a2 = st.columns([4, 1])
                    with a1:
                        if tetiklendi:
                            st.markdown(f"""<div class="alarm-triggered">🚨 <b>{alarm['hisse']}</b> → {g_fiyat:.2f} TL<br>
                            <span style="font-size:10px">{alarm['tur']} {float(alarm['fiyat']):.2f} TL</span></div>""", unsafe_allow_html=True)
                        else:
                            pct = abs((float(alarm['fiyat']) - g_fiyat) / g_fiyat * 100)
                            yon = "▲" if alarm['tur'] == "Üstüne Çıkarsa" else "▼"
                            st.markdown(f"""<div class="alarm-active">🔔 <b>{alarm['hisse']}</b> {yon} {float(alarm['fiyat']):.2f} TL<br>
                            <span style="font-size:10px">Şu an: {g_fiyat:.2f} • Fark: %{pct:.1f}</span></div>""", unsafe_allow_html=True)
                    with a2:
                        if st.button("✕", key=f"aldel_{alarm['id']}"):
                            alarm_sil(st.session_state.user_id, alarm['id'])
                            st.rerun()
                except:
                    pass

    st.markdown("---")
    st.markdown('<div class="section-title">⚖ KARŞILAŞTIRMA</div>', unsafe_allow_html=True)
    kiyas_secenek = st.multiselect("Karşılaştırma Ekle:", ["Altın (TL)", "Gümüş (TL)", "Dolar/TL", "Enflasyon"])

# ============================================================
# ANA TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  TEKNİK ANALİZ",
    "🤖  AI RAPORU",
    "📰  HABERLER",
    "💼  PORTFÖY"
])

# ============================================================
# TAB 1: TEKNİK ANALİZ
# ============================================================
with tab1:
    data_raw = veri_indir(f"{t_kod}.IS", secilen_periyot, secilen_aralik)

    if data_raw is not None and not data_raw.empty:
        if isinstance(data_raw.columns, pd.MultiIndex):
            close_col = data_raw['Close']
            seri = close_col.iloc[:, 0] if isinstance(close_col, pd.DataFrame) else close_col
        else:
            seri = data_raw['Close']
        seri = seri.dropna()

        fiyat_son  = float(seri.iloc[-1])
        fiyat_prev = float(seri.iloc[-2]) if len(seri) > 1 else fiyat_son
        degisim_yuzde = ((fiyat_son - fiyat_prev) / fiyat_prev) * 100

        try:
            hacim = data_raw['Volume'].iloc[:, 0].mean() if isinstance(data_raw.columns, pd.MultiIndex) else data_raw['Volume'].mean()
        except:
            hacim = 0

        sinyaller, skor, genel_sinyal = teknik_sinyal_hesapla(seri, data_raw)
        rsi_val = hesapla_rsi(seri).iloc[-1] if len(seri) > 14 else 50.0

        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        with mc1:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">SON FİYAT</div>
            <div class="metric-value">{fiyat_son:.2f} <span style="font-size:12px;color:#4a6080">TL</span></div></div>""", unsafe_allow_html=True)
        with mc2:
            renk = "metric-positive" if degisim_yuzde >= 0 else "metric-negative"
            yon  = "▲" if degisim_yuzde >= 0 else "▼"
            st.markdown(f"""<div class="metric-card"><div class="metric-label">GÜNLÜK DEĞİŞİM</div>
            <div class="metric-value {renk}">{yon} {abs(degisim_yuzde):.2f}%</div></div>""", unsafe_allow_html=True)
        with mc3:
            rsi_cls = "metric-positive" if rsi_val < 30 else ("metric-negative" if rsi_val > 70 else "metric-neutral")
            st.markdown(f"""<div class="metric-card"><div class="metric-label">RSI (14)</div>
            <div class="metric-value {rsi_cls}">{rsi_val:.1f}</div></div>""", unsafe_allow_html=True)
        with mc4:
            sinyal_cls = "metric-positive" if "AL" in genel_sinyal else ("metric-negative" if "SAT" in genel_sinyal else "metric-neutral")
            st.markdown(f"""<div class="metric-card"><div class="metric-label">TEKNİK SİNYAL</div>
            <div class="metric-value {sinyal_cls}" style="font-size:16px">{genel_sinyal}</div></div>""", unsafe_allow_html=True)
        with mc5:
            st.markdown(f"""<div class="metric-card"><div class="metric-label">ORT. HACİM</div>
            <div class="metric-value metric-neutral">{hacim/1_000_000:.1f}M</div></div>""", unsafe_allow_html=True)

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

            fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=row_heights)
            cur_row = 1

            if isinstance(data_raw.columns, pd.MultiIndex):
                high_s = data_raw['High'].iloc[:, 0]; low_s = data_raw['Low'].iloc[:, 0]; open_s = data_raw['Open'].iloc[:, 0]
            else:
                high_s = data_raw['High']; low_s = data_raw['Low']; open_s = data_raw['Open']

            fig.add_trace(go.Candlestick(x=seri.index, open=open_s, high=high_s, low=low_s, close=seri, name=t_kod,
                increasing=dict(line=dict(color='#00ff88', width=1)), decreasing=dict(line=dict(color='#ff4444', width=1))), row=cur_row, col=1)

            if goster_bb:
                ust, ort_bb, alt = hesapla_bollinger(seri)
                fig.add_trace(go.Scatter(x=seri.index, y=ust, line=dict(color='#4444ff', width=1, dash='dot'), showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=alt, line=dict(color='#4444ff', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(68,68,255,0.05)', showlegend=False), row=cur_row, col=1)
                fig.add_trace(go.Scatter(x=seri.index, y=ort_bb, line=dict(color='#8888ff', width=1), showlegend=False), row=cur_row, col=1)

            if goster_ma:
                for ma_p, renk_ma in [(20, '#ffaa00'), (50, '#ff6688'), (200, '#88aaff')]:
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
                fig.update_yaxes(range=[0, 100], row=cur_row, col=1)

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
                font=dict(family='JetBrains Mono', color='#8899aa'), height=600, margin=dict(l=10, r=10, t=40, b=10))
            fig.update_xaxes(gridcolor='#1e2a3a'); fig.update_yaxes(gridcolor='#1e2a3a')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">İNDİKATÖR SİNYALLERİ</div>', unsafe_allow_html=True)
        cols = st.columns(len(sinyaller))
        for i, (ind_ad, ind_data) in enumerate(sinyaller.items()):
            badge_cls = 'badge-buy' if ind_data['sinyal'] == 'AL' else ('badge-sell' if ind_data['sinyal'] == 'SAT' else 'badge-hold')
            cols[i].markdown(f"""<div class="metric-card" style="text-align:center">
                <div class="metric-label">{ind_ad}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#c8d8e8;margin:4px 0">{ind_data['deger']}</div>
                <span class="badge {badge_cls}">{ind_data['sinyal']}</span></div>""", unsafe_allow_html=True)

        # Karşılaştırma grafiği
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚖ PERFORMANS KARŞILAŞTIRMASI (100 TL)</div>', unsafe_allow_html=True)

        indir_list = [f"{t_kod}.IS", "USDTRY=X"]
        if "Altın (TL)"  in kiyas_secenek: indir_list.append("GC=F")
        if "Gümüş (TL)" in kiyas_secenek: indir_list.append("SI=F")

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
                fig_k = go.Figure(); ozet = []
                h_s = veriler[f"{t_kod}.IS"]; norm = (h_s / h_s.iloc[0]) * 100
                fig_k.add_trace(go.Scatter(x=h_s.index, y=norm, name=f"{t_kod}", line=dict(color='#00d4ff', width=2.5)))
                ozet.append({"Varlık": f"{t_kod}", "Başlangıç": "100 TL", "Güncel": f"{norm.iloc[-1]:.2f} TL", "Getiri": f"{norm.iloc[-1]-100:+.2f}%"})
                kur = veriler.get("USDTRY=X", pd.Series(dtype=float))

                if "Altın (TL)" in kiyas_secenek and "GC=F" in veriler.columns and not kur.empty:
                    a_tl = veriler["GC=F"] * kur; a_norm = (a_tl / a_tl.iloc[0]) * 100
                    fig_k.add_trace(go.Scatter(x=a_tl.index, y=a_norm, name="Altın (TL)", line=dict(color='#ffd700', width=2)))
                    ozet.append({"Varlık": "Altın (TL)", "Başlangıç": "100 TL", "Güncel": f"{a_norm.iloc[-1]:.2f} TL", "Getiri": f"{a_norm.iloc[-1]-100:+.2f}%"})

                if "Gümüş (TL)" in kiyas_secenek and "SI=F" in veriler.columns and not kur.empty:
                    g_tl = veriler["SI=F"] * kur; g_norm = (g_tl / g_tl.iloc[0]) * 100
                    fig_k.add_trace(go.Scatter(x=g_tl.index, y=g_norm, name="Gümüş (TL)", line=dict(color='#c0c0c0', width=2)))
                    ozet.append({"Varlık": "Gümüş (TL)", "Başlangıç": "100 TL", "Güncel": f"{g_norm.iloc[-1]:.2f} TL", "Getiri": f"{g_norm.iloc[-1]-100:+.2f}%"})

                if "Dolar/TL" in kiyas_secenek and not kur.empty:
                    k_norm = (kur / kur.iloc[0]) * 100
                    fig_k.add_trace(go.Scatter(x=kur.index, y=k_norm, name="Dolar/TL", line=dict(color='#88ff88', width=2)))
                    ozet.append({"Varlık": "Dolar/TL", "Başlangıç": "100 TL", "Güncel": f"{k_norm.iloc[-1]:.2f} TL", "Getiri": f"{k_norm.iloc[-1]-100:+.2f}%"})

                if "Enflasyon" in kiyas_secenek:
                    enf = {2020:0.14,2021:0.19,2022:0.72,2023:0.65,2024:0.55,2025:0.45,2026:0.35}
                    cum = [100]; val = 100
                    for i in range(1, len(veriler.index)):
                        val *= (1 + enf.get(veriler.index[i].year, 0.45)) ** (1/252); cum.append(val)
                    fig_k.add_trace(go.Scatter(x=veriler.index, y=cum, name="Enflasyon", line=dict(color='#ff4444', width=1.5, dash='dot')))
                    ozet.append({"Varlık": "Enflasyon", "Başlangıç": "100 TL", "Güncel": f"{cum[-1]:.2f} TL", "Getiri": f"{cum[-1]-100:+.2f}%"})

                fig_k.update_layout(
                    title=f"100 TL Yatırımın Performansı — {t_sure_etiket}",
                    template="plotly_dark",
                    plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                    yaxis_title="Değer (TL)", height=380,
                    legend=dict(bgcolor='#0f1520', bordercolor='#1e2a3a', font=dict(family='JetBrains Mono', size=11)),
                    font=dict(family='JetBrains Mono', color='#8899aa'),
                    margin=dict(l=10, r=10, t=40, b=10))
                fig_k.update_xaxes(gridcolor='#1e2a3a')
                fig_k.update_yaxes(gridcolor='#1e2a3a')
                st.plotly_chart(fig_k, use_container_width=True)

                if len(ozet) > 1:
                    st.markdown('<div class="section-title">PERFORMANS ÖZETİ</div>', unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame(ozet), use_container_width=True, hide_index=True)
            else:
                st.info("Sol panelden karşılaştırma varlığı seçin.")
        else:
            st.info("Sol panelden karşılaştırmak istediğiniz varlıkları seçin.")

    else:
        st.warning(f"⚠ {t_kod} için veri indirilemedi. Hisse Yahoo Finance'de kayıtlı olmayabilir.")

# ============================================================
# TAB 2: AI RAPORU
# ============================================================
with tab2:
    st.markdown('<div class="section-title">🤖 YAPAY ZEKA ANALİZ RAPORU</div>', unsafe_allow_html=True)
    data_ai = veri_indir(f"{t_kod}.IS", "1y", "1d")

    if data_ai is not None and not data_ai.empty:
        seri_ai = data_ai['Close'].iloc[:, 0].dropna() if isinstance(data_ai.columns, pd.MultiIndex) else data_ai['Close'].dropna()
        fiyat_ai = float(seri_ai.iloc[-1])
        fiyat_prev_ai = float(seri_ai.iloc[-2]) if len(seri_ai) > 1 else fiyat_ai
        degisim_ai = ((fiyat_ai - fiyat_prev_ai) / fiyat_prev_ai) * 100
        rsi_ai = hesapla_rsi(seri_ai).iloc[-1]
        _, _, gs_ai = teknik_sinyal_hesapla(seri_ai, data_ai)

        ai_kol1, ai_kol2 = st.columns([2, 1])
        with ai_kol2:
            st.markdown(f"""<div class="metric-card">
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
            </div>""", unsafe_allow_html=True)

        with ai_kol1:
            if st.button("🤖 AI Analizi Üret", use_container_width=True, key="ai_btn"):
                with st.spinner("Yapay zeka raporu hazırlanıyor..."):
                    sonuc = ai_analiz_yap(t_kod, t_ad, fiyat_ai, degisim_ai, rsi_ai, gs_ai, seri_ai)
                    if sonuc:
                        st.session_state[f"ai_sonuc_{t_kod}"] = sonuc

            cache_key = f"ai_sonuc_{t_kod}"
            if cache_key in st.session_state:
                st.markdown(f"""<div class="ai-box">
                    <div class="ai-box-header">⬡ AI ANALİZİ • {t_kod} • {datetime.now().strftime('%d.%m.%Y')}</div>
                    {st.session_state[cache_key].replace(chr(10), '<br>')}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div class="ai-box" style="text-align:center;color:#4a6080;padding:40px">
                    <div style="font-size:32px;margin-bottom:12px">🤖</div>
                    <div>AI analizi başlatmak için butona tıklayın.</div>
                    <div style="font-size:12px;margin-top:8px">Groq — Llama 3.3 70B</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="margin-top:24px">SON 30 GÜN GÖRÜNÜMÜ</div>', unsafe_allow_html=True)
        son30 = seri_ai.iloc[-30:]; rsi30 = hesapla_rsi(seri_ai).iloc[-30:]
        fig_ai = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        fig_ai.add_trace(go.Scatter(x=son30.index, y=son30, fill='tozeroy', fillcolor='rgba(0,212,255,0.08)', line=dict(color='#00d4ff', width=2)), row=1, col=1)
        fig_ai.add_trace(go.Scatter(x=rsi30.index, y=rsi30, line=dict(color='#aa88ff', width=1.5)), row=2, col=1)
        fig_ai.add_hline(y=70, line=dict(color='#ff4444', width=1, dash='dot'), row=2, col=1)
        fig_ai.add_hline(y=30, line=dict(color='#00ff88', width=1, dash='dot'), row=2, col=1)
        fig_ai.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f', height=300, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        fig_ai.update_xaxes(gridcolor='#1e2a3a'); fig_ai.update_yaxes(gridcolor='#1e2a3a')
        st.plotly_chart(fig_ai, use_container_width=True)
    else:
        st.warning("Veri yüklenemedi.")

# ============================================================
# TAB 3: HABERLER
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

with tab3:
    st.markdown('<div class="section-title">📰 PİYASA HABERLERİ</div>', unsafe_allow_html=True)
    haber_kol1, haber_kol2 = st.columns([2, 1])

    with haber_kol1:
        h_btn_col, h_info_col = st.columns([1, 2])
        with h_btn_col:
            haber_yukle = st.button("🔄 Haberleri Yükle", use_container_width=True)
        with h_info_col:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#4a6080;padding-top:10px">📡 RSS feed\'lerden • 10 dk önbellek</div>', unsafe_allow_html=True)

        if haber_yukle:
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
                st.info("Haber bulunamadı.")
        else:
            st.markdown("""<div class="ai-box" style="text-align:center;color:#4a6080;padding:40px">
                <div style="font-size:32px;margin-bottom:12px">📰</div>
                <div>Haberleri görmek için butona tıklayın.</div></div>""", unsafe_allow_html=True)

    with haber_kol2:
        st.markdown('<div class="section-title">PİYASA ÖZETİ</div>', unsafe_allow_html=True)
        endeksler = {"BIST 100": "XU100.IS", "Dolar/TL": "USDTRY=X", "Euro/TL": "EURTRY=X", "Altın (TL)": "GC=F"}
        for ad, ticker_k in endeksler.items():
            try:
                d = yf.download(ticker_k, period="2d", progress=False)
                if not d.empty and len(d) >= 2:
                    son  = float(d['Close'].iloc[-1].iloc[0]) if isinstance(d.columns, pd.MultiIndex) else float(d['Close'].iloc[-1])
                    prev = float(d['Close'].iloc[-2].iloc[0]) if isinstance(d.columns, pd.MultiIndex) else float(d['Close'].iloc[-2])
                    deg  = ((son - prev) / prev) * 100
                    renk = '#00ff88' if deg >= 0 else '#ff4444'
                    yon  = '▲' if deg >= 0 else '▼'
                    st.markdown(f"""<div class="metric-card">
                        <div class="metric-label">{ad}</div>
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{son:,.2f}</div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{renk}">{yon} {abs(deg):.2f}%</div>
                        </div></div>""", unsafe_allow_html=True)
            except:
                pass

# ============================================================
# TAB 4: PORTFÖY
# ============================================================
with tab4:
    st.markdown('<div class="section-title">💼 GELİŞMİŞ PORTFÖY TAKİBİ</div>', unsafe_allow_html=True)

    if not st.session_state.user:
        st.markdown("""<div class="ai-box" style="text-align:center;padding:40px">
            <div style="font-size:40px;margin-bottom:12px">🔐</div>
            <div style="font-size:15px;color:#8899aa">Portföy takibi için giriş yapın.</div>
            <div style="font-size:12px;color:#4a6080;margin-top:8px">Sağ üst köşeden kayıt olabilirsiniz.</div>
        </div>""", unsafe_allow_html=True)
    else:
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
                    if portfoy_ekle(st.session_state.user_id, pkod, p_maliyet, p_adet, p_hedef, p_stop):
                        st.success("✅ Eklendi!")
                        st.rerun()

        with p_kol2:
            if not st.session_state.portfoy.empty:
                t_maliyet = 0.0; t_guncel = 0.0; portfoy_data = []

                for _, row in st.session_state.portfoy.iterrows():
                    try:
                        g_veri = yf.download(f"{row['Hisse']}.IS", period="2d", auto_adjust=True, progress=False)
                        if g_veri.empty: continue
                        if isinstance(g_veri.columns, pd.MultiIndex):
                            g_fiyat = float(g_veri['Close'].iloc[-1].iloc[0])
                            g_prev  = float(g_veri['Close'].iloc[-2].iloc[0]) if len(g_veri) > 1 else g_fiyat
                        else:
                            g_fiyat = float(g_veri['Close'].iloc[-1])
                            g_prev  = float(g_veri['Close'].iloc[-2]) if len(g_veri) > 1 else g_fiyat

                        m_toplam = float(row['Maliyet']) * int(row['Adet'])
                        g_toplam = g_fiyat * int(row['Adet'])
                        kz_tl    = g_toplam - m_toplam
                        kz_yuzde = (kz_tl / m_toplam) * 100
                        gun_deg  = ((g_fiyat - g_prev) / g_prev) * 100

                        t_maliyet += m_toplam; t_guncel += g_toplam

                        hedef_val = float(row.get('Hedef', 0)); stop_val = float(row.get('Stop', 0))
                        hedef_uyari = f'<span style="color:#00ff88;font-size:10px">🎯 HEDEF AŞILDI ({hedef_val:.2f})</span>' if hedef_val > 0 and g_fiyat >= hedef_val else (f'<span style="color:#4a6080;font-size:10px">🎯 Hedefe %{((hedef_val-g_fiyat)/g_fiyat*100):.1f}</span>' if hedef_val > 0 else "")
                        stop_uyari  = f'<span style="color:#ff4444;font-size:10px">🛑 STOP TETİKLENDİ ({stop_val:.2f})</span>' if stop_val > 0 and g_fiyat <= stop_val else (f'<span style="color:#4a6080;font-size:10px">🛑 Stop: {stop_val:.2f}</span>' if stop_val > 0 else "")

                        portfoy_data.append({'row_id': row['id'], 'hisse': row['Hisse'], 'maliyet': row['Maliyet'], 'adet': row['Adet'],
                            'g_fiyat': g_fiyat, 'm_toplam': m_toplam, 'g_toplam': g_toplam,
                            'kz_tl': kz_tl, 'kz_yuzde': kz_yuzde, 'gun_deg': gun_deg,
                            'hedef_uyari': hedef_uyari, 'stop_uyari': stop_uyari})
                    except:
                        pass

                for p in portfoy_data:
                    kz_renk = '#00ff88' if p['kz_tl'] >= 0 else '#ff4444'
                    gun_renk = '#00ff88' if p['gun_deg'] >= 0 else '#ff4444'
                    gun_yon  = '▲' if p['gun_deg'] >= 0 else '▼'
                    r1, r2 = st.columns([5, 1])
                    with r1:
                        st.markdown(f"""<div class="metric-card">
                            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">
                                <div>
                                    <span style="font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;color:#00d4ff">{p['hisse']}</span>
                                    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#4a6080;margin-left:8px">{p['adet']} adet @ {float(p['maliyet']):.2f}</span>
                                </div>
                                <div style="text-align:right">
                                    <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{p['g_fiyat']:.2f} TL</div>
                                    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{gun_renk}">{gun_yon} {abs(p['gun_deg']):.2f}% bugün</div>
                                </div>
                            </div>
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;gap:6px">
                                <div>{p['hedef_uyari']} {'&nbsp;' if p['hedef_uyari'] and p['stop_uyari'] else ''} {p['stop_uyari']}</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:{kz_renk};font-weight:700">{p['kz_tl']:+,.2f} TL ({p['kz_yuzde']:+.2f}%)</div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with r2:
                        if st.button("🗑", key=f"del_{p['row_id']}"):
                            portfoy_sil(st.session_state.user_id, p['row_id'])
                            st.rerun()

                st.markdown("---")
                m1, m2, m3, m4 = st.columns(4)
                toplam_kz = t_guncel - t_maliyet
                toplam_kz_yuzde = ((t_guncel / t_maliyet) - 1) * 100 if t_maliyet > 0 else 0
                with m1:
                    st.markdown(f"""<div class="metric-card" style="text-align:center"><div class="metric-label">TOPLAM MALİYET</div><div class="metric-value metric-neutral">{t_maliyet:,.0f} TL</div></div>""", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""<div class="metric-card" style="text-align:center"><div class="metric-label">GÜNCEL DEĞER</div><div class="metric-value">{t_guncel:,.0f} TL</div></div>""", unsafe_allow_html=True)
                with m3:
                    kz_cls = "metric-positive" if toplam_kz >= 0 else "metric-negative"
                    st.markdown(f"""<div class="metric-card" style="text-align:center"><div class="metric-label">NET KAR / ZARAR</div><div class="metric-value {kz_cls}">{toplam_kz:+,.0f} TL</div></div>""", unsafe_allow_html=True)
                with m4:
                    st.markdown(f"""<div class="metric-card" style="text-align:center"><div class="metric-label">TOPLAM GETİRİ</div><div class="metric-value {'metric-positive' if toplam_kz_yuzde >= 0 else 'metric-negative'}">{toplam_kz_yuzde:+.2f}%</div></div>""", unsafe_allow_html=True)

                if len(portfoy_data) > 1:
                    st.markdown('<div class="section-title" style="margin-top:20px">PORTFÖY DAĞILIMI</div>', unsafe_allow_html=True)
                    fig_pie = go.Figure(go.Pie(
                        labels=[p['hisse'] for p in portfoy_data], values=[p['g_toplam'] for p in portfoy_data],
                        hole=0.5, marker=dict(colors=['#00d4ff','#00ff88','#ff8800','#ff4444','#aa88ff','#ffdd00'], line=dict(color='#0a0a0f', width=2)),
                        textfont=dict(family='JetBrains Mono', size=11)))
                    fig_pie.update_layout(template="plotly_dark", plot_bgcolor='#0a0a0f', paper_bgcolor='#0a0a0f',
                        height=280, legend=dict(bgcolor='#0f1520', bordercolor='#1e2a3a', font=dict(family='JetBrains Mono', size=10)),
                        margin=dict(l=0, r=0, t=10, b=0))
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.markdown("""<div class="ai-box" style="text-align:center;color:#4a6080;padding:60px">
                    <div style="font-size:40px;margin-bottom:12px">💼</div>
                    <div style="font-size:15px">Portföyünüz boş.</div>
                    <div style="font-size:12px;margin-top:8px">Sol panelden hisse ekleyerek başlayın.</div>
                </div>""", unsafe_allow_html=True)

# ============================================================
# FOOTER
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
    BIST TERMINAL PRO &nbsp;•&nbsp; Geliştirici: Enes Boz &nbsp;•&nbsp; {datetime.now().year} &nbsp;•&nbsp; Veriler Yahoo Finance kaynaklıdır
</div>
""", unsafe_allow_html=True)
