import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
import re

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
api_key = os.environ.get('API_KEY')
genai.configure(api_key=api_key)

# Google Gemini API 호출 함수
def fetch_travel_plan(destination, style):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    query = f"""
    목적지 : {destination}
    여행 스타일 : {style}
    이 입력값에 맞는 당일치기 여행 계획을 짜주세요.
    장소 추천은 정확한 위치와 이름을 포함해주세요.
    
    여행 계획을 다음 형식에 맞춰 작성해 주세요:
    
    시원한 바다 당일치기 여행

    🌞 아침 (10:00) : 집에서 출발 - 🌊 영덕 해맞이 공원 (실내 전망대)
    * 대구에서 영덕까지는 차로 약 1시간 30분 소요됩니다.
    * 영덕 해맞이 공원은 탁 트인 동해 바다를 한눈에 조망할 수 있는 곳입니다.
    * 특히, 해맞이 전망대는 엘리베이터를 이용하여 편리하게 오를 수 있으며, 시원한 바닷바람과 함께 멋진 파노라마를 감상할 수 있습니다.
    * 더운 날씨에도 실내에서 시원하게 바다를 즐길 수 있는 최고의 장소입니다.
    
    🐠 점심 (12:00) : 영덕 강구항 - 🐟 영덕 대게 직판장
    * 영덕 해맞이 공원에서 차로 약 10분 거리에 위치한 강구항은 영덕 대게의 주산지입니다.
    * 영덕 대게 직판장에서 신선한 대게를 저렴하게 구매하여 맛볼 수 있습니다.
    * 싱싱한 해산물을 맛보며 푸짐한 점심 식사를 즐겨보세요.
    
    🍦 후식 (14:00) : 영덕 해맞이 공원 - ☕ 카페 '오션뷰'
    * 점심 식사 후 다시 영덕 해맞이 공원으로 돌아와 '오션뷰' 카페에서 시원한 커피와 디저트를 즐기세요.
    * 바다를 바라보며 여유로운 시간을 보내고,
    * 탁 트인 동해 바다를 배경으로 인생샷을 남겨보세요.
    
    🚗 저녁 (17:00) : 집으로 출발
    * 아름다운 영덕 바다를 만끽하고 대구로 출발합니다.
    * 대구까지는 약 1시간 30분 소요됩니다.

    장소 정보
    1. 영덕 해맞이 공원 : 129.2222, 36.2993
    2. 영덕 대게 직판장 : 129.2463, 36.3081
    3. 카페 '오션뷰' : 129.2239, 36.3007
    """
    response = model.generate_content(query)
    return response

# 응답에서 텍스트 추출 및 디코딩 함수
def extract_text(response):
    if response and hasattr(response, 'candidates'):
        content_part = response.candidates[0].content.parts[0]
        text = content_part.text
        return text
    else:
        st.error("API 응답이 올바르지 않습니다.")
        return None

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
def generate_plan(destination, style):
    plan_response = fetch_travel_plan(destination, style)
    if plan_response:
        plan_text = extract_text(plan_response)
        st.session_state.travel_plan = plan_text
        st.session_state.places = extract_places(plan_text)
    else:
        st.session_state.travel_plan = "여행 계획을 가져오지 못했습니다."
        st.session_state.places = []

# 지도 그리기 함수
def draw_map(places):
    if places:
        # 첫 번째 장소의 위치를 중심으로 지도 생성
        m = folium.Map(location=[places[0]['latitude'], places[0]['longitude']], zoom_start=13)
        
        # 각 장소에 마커 추가
        for place in places:
            folium.Marker(
                [place['latitude'], place['longitude']],
                popup=f"{place['name']}"
            ).add_to(m)
        
        return m
    else:
        print("추출된 장소가 없습니다.")
        return None


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
    destination = st.text_input("여행지 입력", "대구에서 가까운 바다")
    style = st.text_area("여행 스타일 입력", "바다 구경도 하고 회도 먹고 싶은데 날이 더우니까 실내 위주로 놀고 싶어.")
    if st.button("여행 계획 생성"):
        generate_plan(destination, style)
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
        map_ = draw_map(st.session_state.places)
        if map_:
            st_folium(map_, width=700, height=500)
    else:
        st.write("여행 계획이 생성되지 않았습니다.")
    st.markdown('</div>', unsafe_allow_html=True)
