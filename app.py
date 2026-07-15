import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. 페이지 및 디자인 설정 (수정 없음)
st.set_page_config(page_title="바다로 떠나자! 🏖️", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #b3e5fc, #fff9c4); }
    h1, h2, h3 { color: #006064; text-shadow: 1px 1px 2px #fff; }
    .stMetric { background-color: rgba(255, 255, 255, 0.8); padding: 20px; border-radius: 15px; border-left: 5px solid #ffcc80; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

st.title("🌊 전국 해수욕장 수질 가이드")
st.markdown("### 🏖️ 가고 싶은 해수욕장의 수질을 확인해보세요!")

df = load_data()
api_key = st.sidebar.text_input("공공데이터 API 키", type="password")

# 2. 데이터 항목 확인용 코드
if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {"serviceKey": api_key, "numOfRows": "5", "pageNo": "1", "resultType": "json", "RES_YEAR": "2026"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'getOceansBeachSeawaterInfo' in data:
                items = data['getOceansBeachSeawaterInfo']['item']
                # API 데이터가 가진 모든 항목 이름(Key)을 사이드바에 출력
                st.sidebar.write("API 데이터 항목(Key) 리스트:", list(items[0].keys()))
                st.sidebar.success("항목을 확인하여 수정하세요!")
    except Exception as e:
        st.sidebar.error(f"연결 오류: {e}")

# 3. 지도 및 선택 (수정 없음)
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    st.map(df[df['해수욕장명'] == selected_beach], latitude='위도', longitude='경도')

with col2:
    st.metric(label="🌊 해수욕장명", value=beach_data['해수욕장명'])
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    st.warning("사이드바에 뜬 항목 리스트를 알려주세요!")
