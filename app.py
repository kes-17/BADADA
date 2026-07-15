import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 1. 페이지 설정 (바다 테마)
st.set_page_config(page_title="🌊 해양 환경 대시보드", layout="wide")

# CSS 디자인
st.markdown("""
    <style>
    .stApp { background-color: #eef6f7; }
    h1 { color: #005b96; }
    </style>
""", unsafe_allow_html=True)

st.title("🌊 전국 해수욕장 수질 적합성 대시보드 🏖️")

# 2. 사이드바 설정
st.sidebar.header("⚙️ 설정 및 인증")
api_key = st.sidebar.text_input("공공데이터 API 인증키 입력", type="password")
selected_year = st.sidebar.selectbox("조사연도 선택", ["2026", "2025", "2024"])

if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {
        "ServiceKey": api_key,
        "resultType": "json",
        "numOfRows": 500,
        "RES_YEAR": selected_year
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            if 'getOceansBeachSeawaterInfo' in data and 'item' in data['getOceansBeachSeawaterInfo']:
                df = pd.DataFrame(data['getOceansBeachSeawaterInfo']['item'])
                # 필드명 표준화 (대문자 변환)
                df.columns = [col.upper() for col in df.columns]
                
                st.success(f"데이터 로드 성공! 총 {len(df)}개의 해수욕장 정보가 확인되었습니다.")

                # 3. 레이아웃 구성
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📊 수질 적합 비율")
                    fig_pie = px.pie(df, names='ADPT_YN', hole=0.4, 
                                     color_discrete_sequence=['#0077b6', '#caf0f8'])
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col2:
                    st.subheader("📍 지역별 적합 현황")
                    # 적합 여부로 그룹화
                    chart_data = df.groupby(['SIDO_NM', 'ADPT_YN']).size().reset_index(name='COUNT')
                    fig_bar = px.bar(chart_data, x='SIDO_NM', y='COUNT', color='ADPT_YN', barmode='group')
                    st.plotly_chart(fig_bar, use_container_width=True)

                # 지도 시각화 (위도/경도 데이터 활용)
                if 'LAT' in df.columns and 'LON' in df.columns:
                    st.subheader("🗺️ 해수욕장 위치 분포")
                    df['LAT'] = pd.to_numeric(df['LAT'])
                    df['LON'] = pd.to_numeric(df['LON'])
                    st.map(df[['LAT', 'LON']])

            else:
                st.warning("데이터가 없습니다. API 키나 연도를 확인하세요.")
        else:
            st.error(f"API 연결 실패 (코드: {response.status_code})")
    except Exception as e:
        st.error(f"처리 중 오류 발생: {e}")
else:
    st.info("👈 사이드바에서 API 인증키를 입력하면 대시보드가 활성화됩니다.")
