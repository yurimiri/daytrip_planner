from dotenv import load_dotenv
import os
import json
import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import folium_static

# load .env
load_dotenv()

# API 키 설정
API_KEY = os.environ.get('API_KEY')
genai.configure(api_key=API_KEY)

# 가상의 Google Gemini API 호출 함수
def fetch_travel_plan(destination, style):
    # 여기서는 예시 데이터를 사용합니다.
    # 실제로는 Google Gemini API를 호출하여 데이터를 받아와야 합니다.
    travel_plan = [
        {"place": "Spot A", "lat": 37.5665, "lon": 126.9780, "description": "Beautiful park"},
        {"place": "Spot B", "lat": 37.5651, "lon": 126.9895, "description": "Historical site"},
        {"place": "Spot C", "lat": 37.5702, "lon": 126.9919, "description": "Shopping district"}
    ]
    return travel_plan

# Streamlit 앱
st.title("당일 치기 여행 플래너")

# 입력 받기
destination = st.text_input("여행지 입력", "서울")
style = st.selectbox("여행 스타일 선택", ["휴식", "탐험", "문화", "쇼핑"])

# 여행 계획 생성 버튼
if st.button("여행 계획 생성"):
    travel_plan = fetch_travel_plan(destination, style)
    
    st.subheader("여행 계획")
    
    for place in travel_plan:
        st.write(f"### {place['place']}")
        st.write(f"{place['description']}")
    
    # 지도 표시
    m = folium.Map(location=[travel_plan[0]['lat'], travel_plan[0]['lon']], zoom_start=13)
    for place in travel_plan:
        folium.Marker([place['lat'], place['lon']], popup=f"{place['place']}: {place['description']}").add_to(m)
    
    st_folium(m, width=700, height=500)