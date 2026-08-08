import os
import geopandas as gpd

# مسار مجلد التقسيم الإداري
folder_name = "Découpage administratif du Maroc 2015_2"

# 1. البحث التلقائي عن ملف .shp داخل المجلد
shp_file = None
for root, dirs, files in os.walk(folder_name):
    for file in files:
        if file.endswith(".shp"):
            shp_file = os.path.join(root, file)
            break

if not shp_file:
    print("❌ لم يتم العثور على ملف .shp داخل المجلد! تأكد من وجوده.")
else:
    print(f"⏳ جاري قراءة الملف: {shp_file} ...")
    gdf = gpd.read_file(shp_file)

    # 2. تحديد عمود الإقليم تلقائياً
    prov_col = None
    for col in gdf.columns:
        if any(
            k in col.lower()
            for k in ['prov', 'nom_prov', 'name_2', 'province', 'nom_provin']
        ):
            prov_col = col
            break

    if not prov_col:
        print("⚠️ لم نتعرف على عمود الإقليم، أسماء الأعمدة هي:", gdf.columns)
        prov_col = input("اكتب اسم العمود الخاص بالإقليم يدويًا: ")

    # 3. تصفية حدود إقليم بولمان فقط
    print(f"🔍 جاري فلترة إقليم بولمان باستخدام العمود [{prov_col}]...")
    boulemane_gdf = gdf[
        gdf[prov_col].astype(str).str.contains('Boulemane|بولمان', case=False)
    ]

    # 4. حفظ كـ GeoJSON
    output_name = "boundaries.geojson"
    boulemane_gdf.to_file(output_name, driver="GeoJSON")
    print(
        f"🎉 تم بنجاح! تم استخراج {len(boulemane_gdf)} جماعة لإقليم بولمان وحفظها في: {output_name}"
    )
