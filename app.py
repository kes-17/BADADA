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

# 2. API 데이터 호출 수정 (포털 상세 정보에 맞춘 정확한 호출)
if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {
        "serviceKey": api_key,
        "numOfRows": "300",
        "pageNo": "1",
        "resultType": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 데이터 구조 확인 (response -> body -> items -> item)
            if 'response' in data and 'body' in data['response'] and 'items' in data['response']['body']:
                items = data['response']['body']['items']['item']
                df_api = pd.DataFrame(items)
                # 데이터 병합을 위해 컬럼명 확인 후 필요 시 이름 통일
                df = pd.merge(df, df_api, on='해수욕장명', how='left')
    except:
        pass

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
    
    # 수질 데이터 출력 (자동 탐색)
    water_col = next((c for c in df.columns if '적합' in c or '수질' in c), None)
    if water_col and pd.notnull(beach_data[water_col]):
        st.markdown(f"### 수질 상태: {beach_data[water_col]}")
    else:
        st.warning("API 정보를 불러오는 중입니다.")

if water_col and water_col in df.columns:
    st.divider()
    st.subheader("📊 전국 수질 현황")
    fig = px.pie(df.dropna(subset=[water_col]), names=water_col, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
