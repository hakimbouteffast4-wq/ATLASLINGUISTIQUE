import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم العالي الاحترافية
# ---------------------------------------------------------
st.set_page_config(
    page_title="Linguistic Atlas & Amazigh Dictionary | الأطلس اللغوي",
    page_icon="🌍",
    layout="wide"
)

# قاموس اللغات للواجهة العالمية
LANG_DICT = {
    'AR': {
        'title': "🌾 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي",
        'subtitle': "منصة رقمية استكشافية لمعجم عتاد الفلاحة وتقنيات السقي والرعي - إقليم بولمان",
        'badge': "🎓 مشروع أطروحة الدكتوراه في اللسانيات الأمازيغية",
        'filter_title': "🏛️ أدوات الضبط وتصفية الأطلس",
        'cat_label': "🎯 الحقل المعجمي:",
        'loc_label': "📍 الموقع الجغرافي / القبيلة:",
        'all_cats': "جميع الحقول المعجمية",
        'all_locs': "جميع القبائل والمواقع",
        'search_ph': "🔍 ابحث بالتيفيناغ، اللاتينية، المعنى العربي، أو الشواهد...",
        'reset': "🔄 إعادة ضبط",
        'stat_items': "المواد المعروضة",
        'stat_cats': "الحقول المعجمية",
        'stat_locs': "المواقع الميدانية",
        'stat_cov': "نسبة التغطية",
        'tab1': "📚 المدونة المعجمية والبطاقات",
        'tab2': "🗺️ الأطلس الجغرافي اللغوي",
        'tab3': "📊 التحليل الإحصائي واللساني",
        'export': "📄 تصدير البيانات (CSV/Excel)",
        'meaning': "المعنى بالعربية",
        'ipa': "الترميز الصوتي الدولي (IPA)",
        'desc': "الوصف الميداني واللساني",
        'proverb': "الشاهد النصي / المثل",
        'cite': "📖 التوثيق والاستشهاد الأكاديمي العالمي (APA 7th):",
        'rights': "جميع الحقوق محفوظة للباحث © 2026 | أطروحة الدكتوراه في اللسانيات الرقمية والأمازيغية"
    },
    'FR': {
        'title': "🌾 Atlas Linguistique et Dictionnaire Amazigh",
        'subtitle': "Plateforme numérique exploratoire du lexique de l'agriculture et de l'élevage - Province de Boulemane",
        'badge': "🎓 Projet de Thèse de Doctorat en Linguistique Amazighe",
        'filter_title': "🏛️ Outils de filtrage et contrôle",
        'cat_label': "🎯 Champ lexical :",
        'loc_label': "📍 Localité / Tribu :",
        'all_cats': "Tous les champs lexicaux",
        'all_locs': "Toutes les localités",
        'search_ph': "🔍 Rechercher en Tifinagh, Latin, sens, ou proverbes...",
        'reset': "🔄 Réinitialiser",
        'stat_items': "Entrées affichées",
        'stat_cats': "Champs lexicaux",
        'stat_locs': "Sites de collecte",
        'stat_cov': "Couverture",
        'tab1': "📚 Corpus & Fiches Lexicales",
        'tab2': "🗺️ Atlas Cartographique",
        'tab3': "📊 Analyse Statistique",
        'export': "📄 Exporter les données (CSV)",
        'meaning': "Signification",
        'ipa': "Transcription Phonétique (API)",
        'desc': "Description linguistique",
        'proverb': "Proverbe / Attestation",
        'cite': "📖 Citation académique (APA 7th) :",
        'rights': "Tous droits réservés © 2026 | Thèse de Doctorat en Linguistique Numérique"
    },
    'EN': {
        'title': "🌾 Linguistic Atlas & Amazigh Lexicon",
        'subtitle': "Digital Exploratory Platform for Agricultural & Pastoral Lexicon - Boulemane Province",
        'badge': "🎓 Ph.D. Research Project in Amazigh Linguistics",
        'filter_title': "🏛️ Control & Filter Tools",
        'cat_label': "🎯 Lexical Field:",
        'loc_label': "📍 Location / Tribe:",
        'all_cats': "All Lexical Fields",
        'all_locs': "All Locations",
        'search_ph': "🔍 Search by Tifinagh, Latin, Arabic meaning, or proverb...",
        'reset': "🔄 Reset",
        'stat_items': "Entries Shown",
        'stat_cats': "Lexical Fields",
        'stat_locs': "Field Sites",
        'stat_cov': "Coverage Rate",
        'tab1': "📚 Lexical Entries & Corpus",
        'tab2': "🗺️ Linguistic Atlas Map",
        'tab3': "📊 Statistical Analytics",
        'export': "📄 Export Data (CSV)",
        'meaning': "Meaning / Translation",
        'ipa': "International Phonetic Alphabet (IPA)",
        'desc': "Field Description",
        'proverb': "Textual Evidence / Proverb",
        'cite': "📖 Academic Citation (APA 7th):",
        'rights': "All Rights Reserved © 2026 | Ph.D. Dissertation in Digital Dialectology"
    }
}

# اختيار اللغة من القائمة الجانبية
st.sidebar.markdown("### 🌐 Language / اللغة")
lang_choice = st.sidebar.selectbox("", ["العربية (AR)", "Français (FR)", "English (EN)"], index=0)
lang_code = "AR" if "AR" in lang_choice else ("FR" if "FR" in lang_choice else "EN")
L = LANG_DICT[lang_code]

# CSS عالمي وأنيق
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {{
        direction: {"rtl" if lang_code == "AR" else "ltr"};
        text-align: {"right" if lang_code == "AR" else "left"};
        font-family: 'Cairo', 'Inter', sans-serif;
        background-color: #f8fafc;
    }}
    
    div[data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-{"left" if lang_code == "AR" else "right"}: 1px solid #e2e8f0;
    }}

    .hero-header {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 3rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
        border-bottom: 5px solid #d97706;
        margin-bottom: 2rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .hero-header h1 {{
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.8rem 0;
    }}
    .hero-header p {{
        color: #cbd5e1;
        font-size: 1.1rem;
        margin: 0;
    }}
    .academic-badge {{
        background-color: rgba(217, 119, 6, 0.2);
        color: #fef3c7;
        border: 1px solid #d97706;
        padding: 6px 18px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }}

    .stat-card {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        border-top: 4px solid #0f172a;
    }}
    .stat-number {{ font-size: 2rem; font-weight: 700; color: #0f172a; }}
    .stat-label {{ font-size: 0.85rem; color: #64748b; font-weight: 600; }}

    .lexical-card {{
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
    }}
    .lexical-card:hover {{
        border-color: #d97706;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.08);
    }}
    .word-tifinagh {{ font-size: 2.2rem; font-weight: 700; color: #0f172a; }}
    .word-latin {{ font-size: 1.2rem; color: #64748b; font-style: italic; }}
    .ref-tag {{ font-family: monospace; background-color: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; }}

    .badge-cat {{ background-color: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }}
    .badge-loc {{ background-color: #fef3c7; color: #b45309; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }}
    .ipa-box {{ font-family: monospace; background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 2px 8px; border-radius: 6px; }}

    .proverb-container {{ background-color: #f8fafc; border-{"right" if lang_code == "AR" else "left"}: 4px solid #0f172a; padding: 0.8rem 1rem; margin-top: 0.8rem; font-style: italic; }}
    .citation-box {{ background-color: #f8fafc; border: 1px dashed #cbd5e1; padding: 8px 12px; font-size: 0.85rem; color: #475569; margin-top: 12px; border-radius: 6px; }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. قراءة قاعدة البيانات
# ---------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv', dtype=str, encoding='utf-8')
        df = df.fillna('')
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 3. الترويسة العالمية
# ---------------------------------------------------------
st.markdown(f"""
    <div class="hero-header">
        <span class="academic-badge">{L['badge']}</span>
        <h1>{L['title']}</h1>
        <p>{L['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. أدوات التصفية والتحكم
# ---------------------------------------------------------
st.sidebar.markdown(f"### {L['filter_title']}")
st.sidebar.markdown("---")

if not df.empty:
    categories = [L['all_cats']] + sorted([str(x) for x in df['category'].unique() if str(x).strip() != ''])
    selected_category = st.sidebar.selectbox(L['cat_label'], categories)

    locations = [L['all_locs']] + sorted([str(x) for x in df['location'].unique() if str(x).strip() != ''])
    selected_location = st.sidebar.selectbox(L['loc_label'], locations)

    filtered_df = df.copy()

    if selected_category != L['all_cats']:
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    if selected_location != L['all_locs']:
        filtered_df = filtered_df[filtered_df['location'] == selected_location]

    st.sidebar.markdown("---")
    csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label=L['export'],
        data=csv_data,
        file_name="atlas_data_export.csv",
        mime="text/csv",
        use_container_width=True
    )

# ---------------------------------------------------------
# 5. محرك البحث والمؤشرات
# ---------------------------------------------------------
if not df.empty:
    col_s, col_r = st.columns([5, 1])
    with col_s:
        search_query = st.text_input("Search:", placeholder=L['search_ph'], label_visibility="collapsed")
    with col_r:
        if st.button(L['reset'], use_container_width=True):
            st.rerun()

    if search_query:
        query = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df['arabic_meaning'].astype(str).str.contains(query, case=False) |
            filtered_df['word_tifinagh'].astype(str).str.contains(query, case=False) |
            filtered_df['word_latin'].astype(str).str.contains(query, case=False) |
            filtered_df['description'].astype(str).str.contains(query, case=False) |
            filtered_df['proverb'].astype(str).str.contains(query, case=False)
        ]

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(filtered_df)}</div><div class="stat-label">{L["stat_items"]}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len([x for x in filtered_df["category"].unique() if str(x).strip() != ""])}</div><div class="stat-label">{L["stat_cats"]}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len([x for x in filtered_df["location"].unique() if str(x).strip() != ""])}</div><div class="stat-label">{L["stat_locs"]}</div></div>', unsafe_allow_html=True)
    with c4:
        coverage = int((len(filtered_df)/len(df))*100) if len(df)>0 else 0
        st.markdown(f'<div class="stat-card"><div class="stat-number">{coverage}%</div><div class="stat-label">{L["stat_cov"]}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 6. التبويبات التفاعلية
    # ---------------------------------------------------------
    tab1, tab2, tab3 = st.tabs([L['tab1'], L['tab2'], L['tab3']])

    # --- التبويب 1: البطاقات المعجمية ---
    with tab1:
        if filtered_df.empty:
            st.info("⚠️ No results found.")
        else:
            for idx, row in filtered_df.iterrows():
                entry_id = f"REF-{str(idx+1).zfill(3)}"
                tifinagh = str(row['word_tifinagh'])
                latin = str(row['word_latin'])
                meaning = str(row['arabic_meaning'])
                ipa = str(row['ipa']) if 'ipa' in row else ''
                category = str(row['category']) if 'category' in row else ''
                location = str(row['location']) if 'location' in row else ''
                description = str(row['description']) if 'description' in row else ''
                proverb = str(row['proverb']) if 'proverb' in row else ''

                st.markdown(f"""
                <div class="lexical-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div>
                            <span class="word-tifinagh">{tifinagh}</span>
                            <span class="word-latin">({latin})</span>
                        </div>
                        <span class="ref-tag">{entry_id}</span>
                    </div>
                    <div style="margin-bottom: 0.8rem;">
                        {f'<span class="badge-cat">{category}</span> ' if category else ''}
                        {f'<span class="badge-loc">📍 {location}</span>' if location else ''}
                    </div>
                    <p style="font-size: 1.1rem; margin-bottom: 0.4rem; color: #0f172a;"><b>{L['meaning']}:</b> {meaning}</p>
                    {f'<p style="margin-bottom: 0.4rem;"><b>{L["ipa"]}:</b> <span class="ipa-box">[{ipa}]</span></p>' if ipa else ''}
                    {f'<p style="color: #475569; margin-bottom: 0.4rem;"><b>{L["desc"]}:</b> {description}</p>' if description else ''}
                    {f'<div class="proverb-container"><b>{L["proverb"]}:</b> "{proverb}"</div>' if proverb else ''}
                    
                    <div class="citation-box">
                        {L['cite']}<br>
                        <i>Author. (2026). Lexical Entry "{tifinagh}" ({latin}). Boulemane Linguistic Atlas. ID: {entry_id}.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- التبويب 2: الخريطة التفاعلية الاحترافية ---
    with tab2:
        st.subheader(L['tab2'])
        map_df = filtered_df.dropna(subset=['lat', 'lon'])
        
        # خريطة متطورة بـ TileLayers و MarkerCluster
        m = folium.Map(location=[33.25, -4.50], zoom_start=9)
        folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite View').add_to(m)
        
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in map_df.iterrows():
            try:
                popup_html = f"""
                <div style="font-family: sans-serif; text-align: right; width: 180px;">
                    <h4 style="color: #0f172a; margin: 0;">{str(row['word_tifinagh'])} ({str(row['word_latin'])})</h4>
                    <b>{L['meaning']}:</b> {str(row['arabic_meaning'])}<br>
                    <b>Location:</b> {str(row['location'])}
                </div>
                """
                folium.Marker(
                    location=[float(row['lat']), float(row['lon'])],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{str(row['word_tifinagh'])} - {str(row['arabic_meaning'])}",
                    icon=folium.Icon(color="darkblue", icon="info-sign")
                ).add_to(marker_cluster)
            except Exception:
                continue

        folium.LayerControl().add_to(m)
        st_folium(m, width="100%", height=550)

    # --- التبويب 3: الإحصائيات ---
    with tab3:
        st.subheader(L['tab3'])
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown(f"#### {L['stat_cats']}")
            st.bar_chart(filtered_df['category'].value_counts())
        with col_chart2:
            st.markdown(f"#### {L['stat_locs']}")
            st.bar_chart(filtered_df['location'].value_counts())

# ---------------------------------------------------------
# 7. التذييل
# ---------------------------------------------------------
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.88rem; padding: 1rem 0;">
        {L['rights']}
    </div>
""", unsafe_allow_html=True)
