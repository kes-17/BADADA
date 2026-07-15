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

# 2. API 호출 로직 (필수 파라미터 추가)
if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {
        "serviceKey": api_key,
        "numOfRows": "300",
        "pageNo": "1",
        "resultType": "json",
        "SIDO_NM": "인천", # 필수값 강제 입력
        "RES_YEAR": "2025" # 필수값 강제 입력
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'body' in data['response'] and data['response']['body']['items'] != '':
                items = data['response']['body']['items']['item']
                df_api = pd.DataFrame(items)
                df = pd.merge(df, df_api, on='해수욕장명', how='left')
                st.sidebar.success("데이터 로드 완료!")
            else:
                st.sidebar.error("데이터가 비어 있습니다. 파라미터 확인 필요.")
        else:
            st.sidebar.error(f"서버 응답 오류: {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"연결 실패: {str(e)}")

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
    
    target_col = next((c for c in df.columns if '적합' in c or '수질' in c), None)
    if target_col and pd.notnull(beach_data[target_col]):
        st.markdown(f"### 수질 상태: {beach_data[target_col]}")
    else:
        st.warning("API 키를 입력했으나 수질 정보를 가져오지 못했습니다.")

if target_col and target_col in df.columns:
    st.divider()
    st.subheader("📊 전국 수질 현황")
    fig = px.pie(df.dropna(subset=[target_col]), names=target_col, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
