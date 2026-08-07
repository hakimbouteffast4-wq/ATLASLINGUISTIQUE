with tab3:
    st.subheader("🗺️ خريطة أطلس اللهجات التفاعلية")
    if lat_col != "لا يوجد" and lon_col != "لا يوجد":
        valid_coords = df.dropna(subset=[lat_col, lon_col])
        if not valid_coords.empty:
            avg_lat = pd.to_numeric(valid_coords[lat_col], errors='coerce').mean()
            avg_lon = pd.to_numeric(valid_coords[lon_col], errors='coerce').mean()
            
            # 1️⃣ إنشاء الخريطة الأساسية (مع تمكين التبديل بين الطبقات)
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=9, tiles=None)

            # 2️⃣ إضافة طبقة الأقمار الصناعية (Google Satellite) - خريطة أطلس الفضائية
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                attr='Google Satellite',
                name='🛰️ خريطة أطلس الفضائية (Satellite)',
                overlay=False,
                control=True
            ).add_to(m)

            # 3️⃣ إضافة الطبقة الجغرافية العادية (OpenStreetMap)
            folium.TileLayer(
                tiles='OpenStreetMap',
                name='🗺️ الخريطة العادية (Street Map)',
                overlay=False,
                control=True
            ).add_to(m)

            # 4️⃣ إضافة العلامات والنوافذ المنبثقة للبيانات اللهجية
            for idx, row in valid_coords.iterrows():
                try:
                    # بناء بطاقة عرض المفردات للهجة عند الضغط على الموقع
                    info_html = f"<div style='font-family: Arial; direction: rtl; text-align: right; min-width: 150px;'>"
                    info_html += f"<h4 style='margin:0; color:#1a73e8;'>📍 {row[loc_col]}</h4><hr style='margin:5px 0;'>"
                    for col in feature_cols:
                        info_html += f"<b>{col}:</b> {row[col]}<br>"
                    info_html += "</div>"

                    folium.Marker(
                        location=[float(row[lat_col]), float(row[lon_col])],
                        popup=folium.Popup(info_html, max_width=250),
                        tooltip=str(row[loc_col]),
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(m)
                except Exception as e:
                    pass

            # 5️⃣ إضافة أداة التبديل بين الطبقتين أعلى الخريطة
            folium.LayerControl(position='topright').add_to(m)

            # عرض الخريطة الشاملة
            st_folium(m, width="100%", height=550)
