import json
import pandas as pd
from haversine import haversine
import folium
import streamlit as st
from streamlit_folium import st_folium

with open("data/maemul_clear.json", encoding="utf-8") as maemul:
    maemul = json.load(maemul)

comb = pd.read_excel("data/송파구편의시설.xlsx", sheet_name="송파구편의시설")
combs = list(comb.itertuples(name=None, index=None))


def pri(s):
    pr = s * 10000
    djr = pr // 100000000
    pr %= 100000000
    aks = pr // 10000
    if djr != 0 and aks != 0:
        return f"{djr}억 {aks}만 원"
    if djr != 0 and aks == 0:
        return f"{djr}억 원"
    if djr == 0 and aks != 0:
        return f"{aks}만 원"
    if djr == 0 and aks == 0:
        return "가격 정보 없음"


def VusdmlTop(li, nu):
    sorted_locations = sorted(li, key=lambda x: x[1], reverse=False)
    top_locations = sorted_locations[:nu]
    re = []
    for aaa in top_locations:
        dlfma = aaa[0]
        rjfl = round(aaa[1], 2)
        re.append(f"{dlfma} ({rjfl}km)")
    return re


# AI2의 추천 매물 메타데이터의 이름 활용, 원 데이터에서 편의시설 거리 계산 함수
def RecommendInfo(li):
    infos = []
    matching_items = []
    for item in maemul:
        for re in li:
            if item.get("이름") == re:
                matching_items.append(item)

    for mi in matching_items:
        name = mi["이름"]
        ty = mi["유형"]
        minarea = round(float(mi["최소 면적"]) / 3.3)
        maxarea = round(float(mi["최대 면적"]) / 3.3)
        minprice = pri(mi["최소 매매 가격"])
        maxprice = pri(mi["최대 매매 가격"])
        minlease = pri(mi["최소 전세 보증금"])
        maxlease = pri(mi["최대 전세 보증금"])
        lat = mi["위도"]
        lon = mi["경도"]
        if minarea == maxarea:
            area = minarea
        else:
            area = f"{minarea} ~ {maxarea}"
        if minprice == maxprice:
            price = minprice
        else:
            price = f"{minprice} ~ {maxprice}"
        if minlease == maxlease:
            lease = minlease
        else:
            lease = f"{minlease} ~ {maxlease}"

        vusdml = []
        rjsrkd = []
        rydbr = []
        rhddnjs = []
        anjdla = []
        tyvld = []
        ryxhd = []

        for c in combs:
            if c[5] == "건강":
                if haversine(c[2:4], (lat, lon)) <= 1.3:
                    rjsrkd.append((c[0], haversine(c[2:4], (lat, lon))))
            elif c[5] == "교육":
                if haversine(c[2:4], (lat, lon)) <= 0.5:
                    rydbr.append((c[0], haversine(c[2:4], (lat, lon))))
            elif c[4] == "공원":
                if haversine(c[2:4], (lat, lon)) <= 0.3:
                    rhddnjs.append((c[0], haversine(c[2:4], (lat, lon))))
            elif c[4] in ("노인복지", "문화", "체육"):
                if haversine(c[2:4], (lat, lon)) <= 0.5:
                    anjdla.append((c[0], haversine(c[2:4], (lat, lon))))
            elif c[5] == "편의":
                if haversine(c[2:4], (lat, lon)) <= 1:
                    tyvld.append((c[0], haversine(c[2:4], (lat, lon))))
            elif c[4] == "교통":
                if haversine(c[2:4], (lat, lon)) <= 0.25:
                    ryxhd.append((c[0], haversine(c[2:4], (lat, lon))))

        if len(rjsrkd) >= 1:
            vusdml.append(f"[건강] {', '.join(VusdmlTop(rjsrkd, 2))}")
        if len(rydbr) >= 1:
            vusdml.append(f"[교육] {', '.join(VusdmlTop(rydbr, 2))}")
        if len(rhddnjs) >= 1:
            vusdml.append(f"[공원] {', '.join(VusdmlTop(rhddnjs, 3))}")
        if len(anjdla) >= 1:
            vusdml.append(f"[문화] {', '.join(VusdmlTop(anjdla, 1))}")
        if len(tyvld) >= 1:
            vusdml.append(f"[쇼핑] {', '.join(VusdmlTop(tyvld, 2))}")
        if len(ryxhd) >= 1:
            vusdml.append(f"[교통] {', '.join(VusdmlTop(ryxhd, 3))}")

        infos.append(
            {
                "name": name,
                "type": ty,
                "info": f"{area}평형<br>매매가 : {price}<br>전세가 : {lease}",
                "conv_info": "<br>".join(vusdml),
                "location": (lat, lon),
            }
        )

    return infos


def display_map_and_list(li):
    if not li:
        st.warning("지도에 표시할 매물이 없습니다.")
        return None
    col1, col2 = st.columns([2, 1])
    with col1:
        average_lat = sum(item["location"][0] for item in li) / len(li)
        average_lon = sum(item["location"][1] for item in li) / len(li)
        average_loc = (average_lat, average_lon)

        m = folium.Map(location=average_loc, zoom_start=15)
        for item in li:
            tooltip_text = (
                f"<b>매물명:</b> {item['name']}<br>"
                f"<b>유형:</b> {item['type']}<br>"
                f"<b>분양가격:</b> {item['info']}<br>"
                f"<b>편의시설:</b> {item['conv_info']}<br>"
            )
            folium.Marker(
                location=item["location"],
                tooltip=tooltip_text,
                icon=folium.DivIcon(html=f"""<div style="font-size: 40px;">🏠</div>"""),
            ).add_to(m)

        m.fit_bounds([item["location"] for item in li])
        st_folium(m, width=700, height=500, key=f"map_{id(li)}")

    with col2:
        st.markdown("### 📋 매물 리스트")
        for item in li:

            st.markdown(
                f"""
                <div style="padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px; background-color:#f9f9f9;">
                    🏢 이름: {item['name']}<br>
                    📍 유형: {item['type']}<br>
                    💰 가격: {item['info']}<br>
                    🗓️ 주변 편의시설<br>
                    {item['conv_info']}<br>
                </div>
                """,
                unsafe_allow_html=True
            )
