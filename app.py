import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="Linguistic Atlas & Amazigh Dictionary | الأطلس اللغوي",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# قاموس اللغات للواجهة العالمية
LANG_DICT = {
    'AR': {
        'title': "🌾 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي",
        'subtitle': "منصة رقمية استكشافية وتوثيقية لمعجم عتاد الفلاحة وتقنيات السقي والرعي - إقليم بولمان",
        'badge': "🎓 مشروع أطروحة الدكتوراه في اللسانيات الأمازيغية والرقمية",
        'filter_title': "🏛️ أدوات التصفية والتحكم",
        'cat_label': "🎯 الحقل المعجمي:",
        'loc_label': "📍 الموقع الجغرافي / القبيلة:",
        'all_cats': "جميع الحقول المعجمية",
        'all_locs': "جميع القبائل والمواقع",
        'search_ph': "🔍 ابحث بالتيفيناغ، اللاتينية، المعنى العربي...",
        'reset': "🔄 إعادة ضبط",
        'stat_items': "المواد المعروضة",
        'stat_cats': "الحقول المعجمية",
        'stat_locs': "المواقع الميدانية",
        'stat_cov': "نسبة التغطية",
        'tab1': "📚 المدونة المعجمية",
        'tab2': "🗺️ الأطلس والخرائط",
        'tab3': "📊 التحليل اللساني",
        'tab4': "✍️ الجمع الميداني",
        'export': "📄 تصدير البيانات (CSV)",
        'meaning': "المعنى بالعربية",
        'ipa': "الترميز الصوتي (IPA)",
        'desc': "الوصف الميداني",
        'proverb': "الشاهد النصي",
        'audio': "🎧 التسجيل الصوتي الميداني:",
        'cite': "📖 التوثيق الأكاديمي (APA 7th):",
        'rights': "جميع الحقوق محفوظة للباحث © 2026 | أطروحة الدكتوراه في اللسانيات الرقمية والأمازيغية"
    },
    'FR': {
        'title': "🌾 Atlas Linguistique et Dictionnaire Amazigh",
        'subtitle': "Plateforme numérique exploratoire du lexique de l'agriculture et de l'élevage - Boulemane",
        'badge': "🎓 Projet de Thèse de Doctorat en Linguistique Amazighe",
        'filter_title': "🏛️ Outils de filtrage",
        'cat_label': "🎯 Champ lexical :",
        'loc_label': "📍 Localité / Tribu :",
        'all_cats': "Tous les champs lexicaux",
        'all_locs': "Toutes les localités",
        'search_ph': "🔍 Rechercher en Tifinagh, Latin, sens...",
        'reset': "Réinitialiser",
        'stat_items': "Entrées affichées",
        'stat_cats': "Champs lexicaux",
        'stat_locs': "Sites de collecte",
        'stat_cov': "Couverture",
        'tab1': "📚 Corpus & Fiches",
        'tab2': "🗺️ Atlas & Cartes",
        'tab3': "📊 Dialectométrie",
        'tab4': "✍️ Fieldwork",
        'export': "📄 Exporter (CSV)",
        'meaning': "Signification",
        'ipa': "Transcription (API)",
        'desc': "Description",
        'proverb': "Proverbe",
        'audio': "🎧 Audio du Terrain :",
        'cite': "📖 Citation académique (APA 7th) :",
        'rights': "Tous droits réservés © 2026 | Thèse de Doctorat en Linguistique Numérique"
    },
    'EN': {
        'title': "🌾 Linguistic Atlas & Amazigh Lexicon",
        'subtitle': "Digital Exploratory Platform for Agricultural & Pastoral Lexicon - Boulemane Province",
        'badge': "🎓 Ph.D. Research Project in Amazigh Linguistics",
        'filter_title': "🏛️ Filter Tools",
        'cat_label': "🎯 Lexical Field:",
        'loc_label': "📍 Location / Tribe:",
        'all_cats': "All Lexical Fields",
        'all_locs': "All Locations",
        'search_ph': "🔍 Search by Tifinagh, Latin, Meaning...",
        'reset': "Reset",
        'stat_items': "Entries Shown",
        'stat_cats': "Lexical Fields",
        'stat_locs': "Field Sites",
        'stat_cov': "Coverage Rate",
        'tab1': "📚 Lexical Entries",
        'tab2': "🗺️ Atlas & Maps",
        'tab3': "📊 Analytics",
        'tab4': "✍️ Contribution",
        'export': "📄 Export Data (CSV)",
        'meaning': "Meaning",
        'ipa': "Phonetics (IPA)",
        'desc': "Description",
        'proverb': "Proverbe",
        'audio': "🎧 Audio Recording:",
        'cite': "📖 Academic Citation (APA 7th):",
        'rights': "All Rights Reserved © 2026 | Ph.D. Dissertation in Digital Dialectology"
    }
}

# اختيار اللغة من القائمة الجانبية
st.sidebar.markdown("### 🌐 Language / اللغة")
lang_choice = st.sidebar.selectbox("", ["العربية (AR)", "Français (FR)", "English (EN)"], index=0)
lang_code = "AR" if "AR" in lang_choice else ("FR" if "FR" in lang_choice else "EN")
L = LANG_DICT[lang_code]

is_rtl = (lang_code == "AR")
direction = "rtl" if is_rtl else "ltr"
text_align = "right" if is_rtl else "left"

# ---------------------------------------------------------
# 2. CSS المحسّن لنقل القائمة والأيقونة لأقصى اليمين المطلق
# ---------------------------------------------------------
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        direction: {direction} !important;
        text-align: {text_align} !important;
        font-family: 'Cairo', 'Inter', sans-serif;
        background-color: #f8fafc;
    }}

    /* 📌 تثبيت القائمة الجانبية تماماً على الشاطئ الأيمن للشاشة */
    {"section[data-testid='stSidebar'] { right: 0 !important; left: auto !important; border-left: 1px solid #e2e8f0 !important; border-right: none !important; position: fixed !important; z-index: 999990 !important; }" if is_rtl else ""}

    /* 📌 نقل زر فتح/إغلاق القائمة إلى أقصى اليمين عند حافة الشاشة (موقع السهم الأصفر) */
    {"[data-testid='stSidebarCollapseButton'], [data-testid='stSidebarToggle'], button[aria-label*='sidebar'] { position: fixed !important; right: 15px !important; top: 15px !important; left: auto !important; z-index: 999999 !important; background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important; }" if is_rtl else ""}

    /* 📌 تدوير سهم الأيقونة بيتجه لليمين */
    {"[data-testid='stSidebarCollapseButton'] svg, [data-testid='stSidebarToggle'] svg { transform: rotate(180deg) !important; }" if is_rtl else ""}

    /* 📌 تحريك المحتوى الرئيسي وتجنب تداخله */
    {"div[data-testid='stMain'] { max-width: 100% !important; padding-right: 1.5rem !important; padding-left: 1.5rem !important; }" if is_rtl else ""}

    /* الترويسة الرئيسية */
    .hero-header {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 2.5rem 1.2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
        border-bottom: 5px solid #d97706;
        margin-bottom: 1.5rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
    }}
    .hero-header h1 {{
        color: #ffffff !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.8rem 0;
        line-height: 1.3;
    }}
    .hero-header p {{
        color: #cbd5e1 !important;
        font-size: 1rem;
        margin: 0;
    }}
    .academic-badge {{
        background-color: rgba(217, 119, 6, 0.2);
        color: #fef3c7;
        border: 1px solid #d97706;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }}

    .stat-card {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        border-top: 4px solid #0f172a;
        margin-bottom: 10px;
    }}
    .stat-number {{ font-size: 1.8rem; font-weight: 700; color: #0f172a; }}
    .stat-label {{ font-size: 0.8rem; color: #64748b; font-weight: 600; }}

    .lexical-card {{
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
    }}
    .word-tifinagh {{ font-size: 1.8rem; font-weight: 700; color: #0f172a; line-height: 1.2; }}
    .word-latin {{ font-size: 1.1rem; color: #64748b; font-style: italic; }}
    .ref-tag {{ font-family: monospace; background-color: #f1f5f9; color: #475569; padding: 2px 6px; border-radius: 6px; font-size: 0.75rem; }}

    .badge-cat {{ background-color: #e0f2fe; color: #0369a1; padding: 3px 10px; border-radius: 15px; font-size: 0.78rem; font-weight: 600; display: inline-block; margin-bottom: 4px; }}
    .badge-loc {{ background-color: #fef3c7; color: #b45309; padding: 3px 10px; border-radius: 15px; font-size: 0.78rem; font-weight: 600; display: inline-block; margin-bottom: 4px; }}
    .ipa-box {{ font-family: monospace; background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 2px 6px; border-radius: 6px; }}

    .proverb-container {{ background-color: #f8fafc; border-{"right" if is_rtl else "left"}: 4px solid #0f172a; padding: 0.7rem; margin-top: 0.6rem; font-style: italic; font-size: 0.95rem; }}
    .citation-box {{ background-color: #f8fafc; border: 1px dashed #cbd5e1; padding: 8px 10px; font-size: 0.8rem; color: #475569; margin-top: 10px; border-radius: 6px; word-break: break-word; }}

    @media only screen and (max-width: 768px) {{
        .hero-header {{ padding: 1.8rem 0.8rem; }}
        .hero-header h1 {{ font-size: 1.4rem; }}
        .hero-header p {{ font-size: 0.9rem; }}
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. قراءة قاعدة البيانات
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
# 4. الترويسة الرئيسية
# ---------------------------------------------------------
st.markdown(f"""
    <div class="hero-header">
        <span class="academic-badge">{L['badge']}</span>
        <h1>{L['title']}</h1>
        <p>{L['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. أدوات التصفية والتحكم في الشريط الجانبي
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
# 6. محرك البحث والمؤشرات
# ---------------------------------------------------------
if not df.empty:
    col_s, col_r = st.columns([4, 1])
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
    # 7. التبويبات الرئيسية
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([L['tab1'], L['tab2'], L['tab3'], L['tab4']])

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
                audio_url = str(row['audio']).strip() if 'audio' in row else ''

                st.markdown(f"""
                <div class="lexical-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap;">
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
                    <p style="font-size: 1rem; margin-bottom: 0.4rem; color: #0f172a;"><b>{L['meaning']}:</b> {meaning}</p>
                    {f'<p style="margin-bottom: 0.4rem; font-size: 0.95rem;"><b>{L["ipa"]}:</b> <span class="ipa-box">[{ipa}]</span></p>' if ipa else ''}
                    {f'<p style="color: #475569; margin-bottom: 0.4rem; font-size: 0.95rem;"><b>{L["desc"]}:</b> {description}</p>' if description else ''}
                    {f'<div class="proverb-container"><b>{L["proverb"]}:</b> "{proverb}"</div>' if proverb else ''}
                """, unsafe_allow_html=True)

                if audio_url and audio_url.startswith("http"):
                    st.caption(L['audio'])
                    st.audio(audio_url)

                st.markdown(f"""
                    <div class="citation-box">
                        {L['cite']}<br>
                        <i>Author. (2026). Lexical Entry "{tifinagh}" ({latin}). Boulemane Linguistic Atlas. ID: {entry_id}.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- التبويب 2: الخريطة ---
    with tab2:
        st.subheader(L['tab2'])
        map_df = filtered_df.dropna(subset=['lat', 'lon'])
        
        map_type = st.radio("نوع العرض:", ["نقاط التوزيع (Clusters)", "الخريطة الحرارية (Heatmap)"], horizontal=True)

        m = folium.Map(location=[33.25, -4.50], zoom_start=9)
        folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite View').add_to(m)

        if "Heatmap" in map_type:
            heat_data = [[float(row['lat']), float(row['lon'])] for _, row in map_df.iterrows()]
            HeatMap(heat_data, radius=15, blur=10).add_to(m)
        else:
            marker_cluster = MarkerCluster().add_to(m)
            for _, row in map_df.iterrows():
                try:
                    popup_html = f"""
                    <div style="font-family: sans-serif; text-align: right; width: 160px;">
                        <h4 style="color: #0f172a; margin: 0; font-size: 1rem;">{str(row['word_tifinagh'])}</h4>
                        <b>{L['meaning']}:</b> {str(row['arabic_meaning'])}<br>
                        <b>Location:</b> {str(row['location'])}
                    </div>
                    """
                    folium.Marker(
                        location=[float(row['lat']), float(row['lon'])],
                        popup=folium.Popup(popup_html, max_width=220),
                        tooltip=f"{str(row['word_tifinagh'])} - {str(row['arabic_meaning'])}",
                        icon=folium.Icon(color="darkblue", icon="info-sign")
                    ).add_to(marker_cluster)
                except Exception:
                    continue

        folium.LayerControl().add_to(m)
        st_folium(m, width="100%", height=450)

    # --- التبويب 3: الإحصائيات ---
    with tab3:
        st.subheader("📊 التحليل اللساني")
        st.markdown("#### كثافة المفردات حسب الحقول المعجمية")
        st.bar_chart(filtered_df['category'].value_counts())
        st.markdown("#### التوزيع الميداني حسب القبائل والمواقع")
        st.bar_chart(filtered_df['location'].value_counts())

    # --- التبويب 4: الجمع الميداني ---
    with tab4:
        st.subheader("✍️ استمارة التوثيق والجمع الميداني")
        with st.form("crowdsourcing_form"):
            word_tif = st.text_input("الكلمة بتيفيناغ:")
            word_lat = st.text_input("الكلمة باللاتينية:")
            arabic_m = st.text_input("المعنى بالعربية:")
            field_loc = st.text_input("موقع الجمع / القبيلة:")
            field_cat = st.selectbox("الحقل المعجمي:", [x for x in df['category'].unique() if str(x).strip() != ''])
            field_desc = st.text_area("الوصف الميداني:")
            submit_btn = st.form_submit_button("📤 إرسال المادة")

            if submit_btn:
                st.success("✅ تم استلام المادة المعجمية بنجاح!")

# ---------------------------------------------------------
# 8. التذييل
# ---------------------------------------------------------
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 1rem 0;">
        {L['rights']}
    </div>
""", unsafe_allow_html=True)
