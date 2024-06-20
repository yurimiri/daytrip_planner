from dotenv import load_dotenv
import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import google.generativeai as genai
import re

# load .env
load_dotenv()

# API 키 설정
API_KEY = os.environ.get('API_KEY')
genai.configure(api_key=API_KEY)

# Google Gemini API 호출 함수
def fetch_travel_plan(destination, style):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    query = f"""
    목적지 : {destination}
    여행 스타일 : {style}
    이 입력값에 맞는 당일치기 여행 계획을 짜줘.
    내용에 반드시 포함 : 장소(맛집이나 명소), 이동 동선, 간단한 설명.
    마지막에 각 장소이름과 경도 위도를 출력해줘
    1. 장소 경도 위도 이런 식으로 
    """
    response = model.generate_content(query)
    return response

# 장소 정보를 추출하는 함수
def extract_places(content):
    places = []
    # 정규 표현식: 장소 이름 뒤에 콜론(:), 경도와 위도는 쉼표(,)로 구분
    pattern = re.compile(r'\d+\.\s*(.*?):\s*([\d.]+),\s*([\d.]+)')
    matches = pattern.findall(content)
    
    for match in matches:
        name = match[0].strip()
        longitude = float(match[1].strip())
        latitude = float(match[2].strip())
        place = {
            "name": name,
            "latitude": latitude,
            "longitude": longitude
        }
        places.append(place)

    return places

# Streamlit 앱
st.title("당일 치기 여행 플래너")

# 초기 상태 설정
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'places' not in st.session_state:
    st.session_state.places = []

# 입력 받기
destination = st.text_input("여행지 입력", "서울")
style = st.text_input("여행 스타일 입력", "활동적인 동선")

# 여행 계획 생성 함수
def generate_plan():
    travel_plan = fetch_travel_plan(destination, style)
    
    if travel_plan and hasattr(travel_plan, 'candidates'):
        content_part = travel_plan.candidates[0].content.parts[0]
        st.session_state.travel_plan = content_part.text

        # 장소 정보 추출
        st.session_state.places = extract_places(content_part.text)

# 여행 계획 생성 버튼
st.button("여행 계획 생성", on_click=generate_plan)

# 여행 계획 출력
if st.session_state.travel_plan:
    st.subheader("여행 계획")
    st.write(st.session_state.travel_plan)
    
    # 지도 표시
    if st.session_state.places:
        m = folium.Map(location=[st.session_state.places[0]['latitude'], st.session_state.places[0]['longitude']], zoom_start=13)
        for place in st.session_state.places:
            folium.Marker(
                [place['latitude'], place['longitude']], 
                popup=f"{place['name']}"
            ).add_to(m)
        
        # 지도 객체를 Streamlit에 표시
        st_data = st_folium(m, width=700, height=500)
else:
    st.write("여행 계획이 생성되지 않았습니다. 입력 후 '여행 계획 생성' 버튼을 눌러주세요.")
