from dotenv import load_dotenv
import os
import streamlit as st
import folium
from streamlit_folium import st_folium
import google.generativeai as genai

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
    내용에 반드시 포함 : 장소(맛집이나 명소), 이동 동선, 설명
    """
    response = model.generate_content(query)
    return response

# Streamlit 앱
st.title("당일 치기 여행 플래너")

# 입력 받기
destination = st.text_input("여행지 입력", "서울")
style = st.text_input("여행 스타일 입력", "활동적인 동선")

# 여행 계획 생성 버튼
if st.button("여행 계획 생성"):
    if API_KEY:
        travel_plan = fetch_travel_plan(destination, style)
        
        st.subheader("여행 계획")
        
        # 응답에서 여행 계획 텍스트 추출 및 출력
        if travel_plan and "candidates" in travel_plan.result:
            content = travel_plan.result['candidates'][0]['content']['parts'][0]['text']
            st.write(content)
        
        # 예시 데이터로 장소 정보 추출 (실제 응답 형식에 따라 수정 필요)
        places = [
            {"name": "맛집 A", "description": "맛있는 음식", "latitude": 37.5665, "longitude": 126.9780},
            {"name": "명소 B", "description": "아름다운 경치", "latitude": 37.5702, "longitude": 126.9919}
        ]
        
        # 지도 표시
        if places:
            m = folium.Map(location=[places[0]['latitude'], places[0]['longitude']], zoom_start=13)
            for place in places:
                folium.Marker(
                    [place['latitude'], place['longitude']], 
                    popup=f"{place['name']}: {place['description']}"
                ).add_to(m)
            
            st_folium(m, width=700, height=500)
    else:
        st.error("API 키를 설정하세요.")
