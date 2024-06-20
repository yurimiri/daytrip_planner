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
    반드시 포함해야 하는 내용 : 장소, 이동 동선, 간단한 설명. 
    장소를 알려줄 때 실제 존재하는 곳을 명확하게 알려줘.
    마지막에 각 장소이름과 경도 위도를 출력해줘.
    1. 장소 : 경도, 위도 
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

# 여행 계획 생성 함수
def generate_plan():
    travel_plan = fetch_travel_plan(destination, style)
    
    if travel_plan and hasattr(travel_plan, 'candidates'):
        content_part = travel_plan.candidates[0].content.parts[0]
        st.session_state.travel_plan = content_part.text
        
        # 장소 정보 추출
        st.session_state.places = extract_places(content_part.text)

# Streamlit 앱
st.set_page_config(layout="wide")
st.title("당일치기 여행 일정 추천")

# 초기 상태 설정
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'places' not in st.session_state:
    st.session_state.places = []

# 레이아웃 및 스타일 설정
st.markdown(
    """
    <style>
    body {
        font-family: 'Helvetica Neue', sans-serif;
        background-color: #f0f8ff;
        color: #333;
    }
    .main-title {
        font-size: 48px;
        color: #008080;
        text-align: center;
        margin-top: 20px;
        font-weight: bold;
    }
    .sidebar-content, .content, .map-container {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #008080;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
    }
    .stButton button:hover {
        background-color: #006666;
    }
    .stTextInput input {
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ccc;
        width: 100%;
        box-sizing: border-box;
    }
    .stTextArea textarea {
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ccc;
        width: 100%;
        box-sizing: border-box;
        height: 150px; 
        resize: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([2, 4, 4])

with col1:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.header("입력창")
    destination = st.text_input("여행지 입력", "대구 근처 바다")
    style = st.text_area("여행 스타일 입력", "바다 구경도 하고 회도 먹고 싶은데 날이 더우니까 실내 위주로 놀고 싶어.")
    if st.button("여행 계획 생성"):
        st.session_state.travel_plan = None
        st.session_state.places = []
        generate_plan()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="content">', unsafe_allow_html=True)
    st.header("계획")
    if st.session_state.travel_plan:
        st.write(st.session_state.travel_plan)
    else:
        st.write("여행 계획이 생성되지 않았습니다. 입력 후 '여행 계획 생성' 버튼을 눌러주세요.")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st.header("지도")
    if st.session_state.places:
        m = folium.Map(location=[st.session_state.places[0]['latitude'], st.session_state.places[0]['longitude']], zoom_start=13)
        for place in st.session_state.places:
            folium.Marker(
                [place['latitude'], place['longitude']],
                popup=f"{place['name']}"
            ).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.write("여행 계획이 생성되지 않았습니다.")
    st.markdown('</div>', unsafe_allow_html=True)
