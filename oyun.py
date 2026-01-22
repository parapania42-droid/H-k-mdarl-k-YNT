import os
import json
import time
import pandas as pd
import streamlit as st
import plotly.express as px

# ==================== VERİ MERKEZİ ====================
DB_FILE = "empire_data.json"

def load_game():
    sablon = {
        "para": 31470000, "yakit": 100, "kuyruk": [],
        "binalar": {
            "Demir Madeni": 3, "Bakır İşletmesi": 1, "Petrol Kuyusu": 1, 
            "Silikon Arıtma": 0, "Titanyum Tesisi": 0, "Altın Ocağı": 0
        },
        "envanter": {
            "Demir": 5510, "Bakır": 0, "Petrol": 0, "Silikon": 0, 
            "Titanyum": 0, "Altın": 0, "Uranyum": 0
        },
        "mamul_stok": {
            "Çelik Levha": 0, "İşlemci": 0, "Lityum Batarya": 0,
            "Robotik Kol": 0, "İHA Kanadı": 0, "Güç Modülü": 0, "AI Çipi": 0
        },
        "depo": {
            "Demir Madeni": 5510, "Bakır İşletmesi": 0, "Petrol Kuyusu": 0, 
            "Silikon Arıtma": 0, "Titanyum Tesisi": 0, "Altın Ocağı": 0
        },
        "gecmis": [31470000], "drone_lvl": 1, "son_tik": time.time()
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in sablon.items():
                    if k not in data: data[k] = v
                return data
        except: return sablon
    return sablon

def save_game(p):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=4)

# ==================== ARAYÜZ TASARIMI ====================
st.set_page_config(page_title="EMPIRE OS V17", layout="wide")

st.markdown("""
<style>
    /* Sabit Üst Panel */
    [data-testid="stHeader"] { display: none; }
    .fixed-header {
        position: fixed; top: 0; left: 0; width: 100%; height: 50px;
        background: #121417; border-bottom: 2px solid #2d3436;
        display: flex; align-items: center; justify-content: space-around;
        z-index: 1000; color: #dfe6e9; font-family: 'Segoe UI', sans-serif;
    }
    .header-item { font-size: 14px; font-weight: bold; }
    .main-content { margin-top: 70px; }
    
    /* Endüstriyel Tema */
    .stApp { background-color: #0f1113; color: #bdc3c7; }
    .factory-card {
        background: #1a1d21; padding: 15px; border-radius: 4px;
        border-left: 5px solid #4b5563; margin-bottom: 10px;
    }
    .res-tag {
        background: #2d3436; padding: 2px 6px; border-radius: 3px;
        font-size: 10px; margin-right: 4px; border: 1px solid #485460;
    }
    .stButton>button { 
        background: #2d3436; color: #dfe6e9; border: 1px solid #485460;
        border-radius: 2px; transition: 0.2s; font-size: 12px;
    }
    .stButton>button:hover { background: #485460; border-color: #d2dae2; }
</style>
""", unsafe_allow_html=True)

if 'p' not in st.session_state:
    st.session_state.p = load_game()

p = st.session_state.p
suan = time.time()
fark_dk = (suan - p.get('son_tik', suan)) / 60
p['son_tik'] = suan

# ==================== VERİ TANIMLARI ====================
MADENLER = {
    "Demir Madeni": {"urun": "Demir", "hiz": 50, "icon": "⚒️", "maliyet": 800000},
    "Bakır İşletmesi": {"urun": "Bakır", "hiz": 35, "icon": "🔌", "maliyet": 2500000},
    "Petrol Kuyusu": {"urun": "Petrol", "hiz": 25, "icon": "🛢️", "maliyet": 5000000},
    "Silikon Arıtma": {"urun": "Silikon", "hiz": 15, "icon": "💎", "maliyet": 15000000},
    "Titanyum Tesisi": {"urun": "Titanyum", "hiz": 8, "icon": "🛡️", "maliyet": 45000000},
    "Altın Ocağı": {"urun": "Altın", "hiz": 4, "icon": "🥇", "maliyet": 120000000}
}

MAMULLER = {
    "Çelik Levha": {"kaynak": {"Demir": 100}, "fiyat": 25000, "icon": "🏗️", "desc": "Temel sanayi malzemesi."},
    "Lityum Batarya": {"kaynak": {"Petrol": 50, "Bakır": 40}, "fiyat": 75000, "icon": "🔋", "desc": "Yüksek kapasiteli güç ünitesi."},
    "İşlemci": {"kaynak": {"Silikon": 25, "Bakır": 30, "Altın": 2}, "fiyat": 180000, "icon": "🧠", "desc": "Mikro işlem birimi."},
    "Robotik Kol": {"kaynak": {"Çelik Levha": 2, "İşlemci": 1}, "fiyat": 450000, "icon": "🦾", "desc": "Hassas sanayi otomasyonu."},
    "İHA Kanadı": {"kaynak": {"Titanyum": 20, "Çelik Levha": 1}, "fiyat": 600000, "icon": "✈️", "desc": "Aerodinamik titanyum parça."},
    "AI Çipi": {"kaynak": {"İşlemci": 5, "Altın": 10}, "fiyat": 2500000, "icon": "👁️‍🗨️", "desc": "Nöral ağ işlemcisi."}
}

# Maden Motoru
for isim, d in MADENLER.items():
    lvl = p['binalar'].get(isim, 0)
    if lvl > 0:
        uretim = d['hiz'] * lvl * fark_dk
        p['depo'][isim] = p['depo'].get(isim, 0) + uretim
        if p.get('drone_lvl', 0) > 0:
            toplanan = p['depo'][isim] * (p['drone_lvl'] * 0.12)
            p['envanter'][d['urun']] += toplanan
            p['depo'][isim] -= toplanan

# ==================== SABİT ÜST PANEL ====================
st.markdown(f"""
<div class="fixed-header">
    <div class="header-item">🏛️ HÜKÜMDAR: PARAMEN42</div>
    <div class="header-item">💰 {int(p['para']):,} ₺</div>
    <div class="header-item">⛽ YAKIT: %{int(p['yakit'])}</div>
    <div class="header-item">🛸 DRONE: S{p['drone_lvl']}</div>
    <div class="header-item" style="color:#2ecc71;">● SİSTEM AKTİF</div>
</div>
""", unsafe_allow_html=True)

# ==================== ANA KOMUTA MERKEZİ ====================
st.markdown('<div class="main-content">', unsafe_allow_html=True)
tabs = st.tabs(["⛏️ MADENLER", "🏭 FABRİKA", "📦 AMBAR", "📊 EKONOMİ"])

with tabs[0]:
    st.subheader("⛏️ Kaynak Çıkarma Üniteleri")
    for isim, d in MADENLER.items():
        lvl = p['binalar'].get(isim, 0)
        kap = (lvl + 1) * 40000
        with st.container():
            st.markdown(f"""
            <div class="factory-card">
                <div style="display:flex; justify-content:space-between;">
                    <b>{d['icon']} {isim.upper()} (S{lvl})</b>
                    <span style="color:#95a5a6; font-size:11px;">HIZ: +{d['hiz']*lvl}/dk</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2, c3 = st.columns([4, 1, 1])
            with c1: st.progress(min(p['depo'].get(isim,0)/kap, 1.0), f"Depo: {int(p['depo'].get(isim,0))}/{kap}")
            with c2:
                if st.button("TOPLA", key=f"t_{isim}"):
                    p['envanter'][d['urun']] += p['depo'][isim]; p['depo'][isim] = 0; save_game(p); st.rerun()
            with c3:
                up_cost = (lvl + 1) * d['maliyet']
                if st.button(f"GELİŞTİR ({up_cost/1000000:.1f}M)", key=f"u_{isim}"):
                    if p['para'] >= up_cost: p['para'] -= up_cost; p['binalar'][isim] += 1; save_game(p); st.rerun()

with tabs[1]:
    st.subheader("🏭 Üretim Bantları")
    for mamul, d in MAMULLER.items():
        with st.container():
            st.markdown(f"""
            <div class="factory-card" style="border-left-color: #3498db;">
                <div style="display:flex; justify-content:space-between;">
                    <b>{d['icon']} {mamul.upper()}</b>
                    <span style="color:#f1c40f;">DEĞER: {d['fiyat']:,} ₺</span>
                </div>
                <div style="font-size:11px; color:#7f8c8d; margin-top:5px;">{d['desc']}</div>
                <div style="margin-top:10px;">
                    {" ".join([f'<span class="res-tag">{k}: {v}</span>' for k, v in d['kaynak'].items()])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns([5, 1])
            with c2:
                if st.button("İMAL ET", key=f"i_{mamul}", use_container_width=True):
                    can_make = all(p['envanter'].get(k, 0) >= v or p['mamul_stok'].get(k, 0) >= v for k, v in d['kaynak'].items())
                    if can_make:
                        for k, v in d['kaynak'].items():
                            if k in p['envanter']: p['envanter'][k] -= v
                            else: p['mamul_stok'][k] -= v
                        p['mamul_stok'][mamul] += 1
                        st.toast(f"{mamul} üretildi."); save_game(p); st.rerun()
                    else: st.error("Eksik kaynak!")

with tabs[2]:
    st.subheader("📦 Ambar ve Lojistik")
    ca, cb = st.columns(2)
    with ca:
        st.write("#### 💎 Hammaddeler")
        st.dataframe(pd.DataFrame(p['envanter'].items(), columns=["Tür", "Miktar"]), use_container_width=True, hide_index=True)
    with cb:
        st.write("#### 🏗️ Üretilen Mallar")
        st.dataframe(pd.DataFrame(p['mamul_stok'].items(), columns=["Ürün", "Adet"]), use_container_width=True, hide_index=True)
    if st.button("💰 TÜMÜNÜ GLOBAL PAZARDA SAT", use_container_width=True):
        kazanc = sum(count * MAMULLER[m]['fiyat'] for m, count in p['mamul_stok'].items())
        p['para'] += kazanc
        for m in p['mamul_stok']: p['mamul_stok'][m] = 0
        st.success(f"Satış başarılı: +{kazanc:,} ₺"); save_game(p); st.rerun()

with tabs[3]:
    st.subheader("📊 Ekonomik Analiz")
    p['gecmis'].append(p['para'])
    if len(p['gecmis']) > 100: p['gecmis'].pop(0)
    fig = px.area(y=p['gecmis'], template="plotly_dark")
    fig.update_traces(line_color='#3498db', fillcolor='rgba(52, 152, 219, 0.1)')
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
save_game(p)