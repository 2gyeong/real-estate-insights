import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium

# 📌 Streamlit 제목 설정
st.title("스트림릿 지도 - 클릭하면 정보 표시")

# 🌍 기본 지도 설정 (서울)
m = folium.Map(location=[37.5146, 127.1066], zoom_start=12)

# 📍 지도 클릭 이벤트 활성화
m.add_child(folium.LatLngPopup())

# 🔹 사용자 마커 리스트 저장
if "markers" not in st.session_state:
    st.session_state["markers"] = []

# 🚀 지도 출력 및 사용자 클릭 정보 수집
click_info = st_folium(m, width=700, height=500)

# 📌 사용자가 클릭한 좌표 가져오기 (None 체크 추가)
if click_info and click_info.get("last_clicked"):
    lat = click_info["last_clicked"]["lat"]
    lon = click_info["last_clicked"]["lng"]

    # 새로운 마커 추가
    new_marker = {"lat": lat, "lon": lon}
    st.session_state["markers"].append(new_marker)

# 🎯 기존 마커 다시 지도에 추가
m = folium.Map(location=[37.5146, 127.1066], zoom_start=12)
for marker in st.session_state["markers"]:
    folium.Marker(
        location=[marker["lat"], marker["lon"]],
        popup=f"위도: {marker['lat']}, 경도: {marker['lon']}",
        tooltip="📍 클릭하세요!"
    ).add_to(m)

# 📍 마커가 추가된 지도 다시 출력
folium_static(m)
