import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. 페이지 및 디자인 설정 (바다 + 모래사장 느낌)
st.set_page_config(page_title="바다로 떠나자! 🏖️", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경: 바다(위)에서 모래사장(아래)으로 그라데이션 */
    .stApp { 
        background: linear-gradient(to bottom, #b3e5fc, #fff9c4); 
    }
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

# API 연동 (경로 수정)
if api_key:
    url = f"http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality?serviceKey={api_key}&numOfRows=300&pageNo=1&resultType=json"
    try:
        response = requests.get(url).json()
        # API 경로 확인: 보통 response -> body -> items -> item 리스트 형태
        if 'response' in response and 'body' in response['response']:
            items = response['response']['body']['items']['item']
            df_api = pd.DataFrame(items)
            df = pd.merge(df, df_api, on='해수욕장명', how='left')
            st.sidebar.success("데이터 업데이트 완료! ✅")
        else:
            st.sidebar.error("API 응답 형식이 다릅니다. 키를 확인하세요.")
    except Exception as e:
        st.sidebar.error(f"오류: {e}")

# 지도 및 선택
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    st.map(df, latitude='위도', longitude='경도')

with col2:
    st.metric(label="🌊 해수욕장명", value=beach_data['해수욕장명'])
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    
    # 수질 데이터 체크 (컬럼명은 API 응답에 맞춰 수정 필요할 수 있음)
    if 'stdDay' in beach_data: # API 응답 확인 후 컬럼명 매칭
        st.markdown(f"### 수질 상태: {beach_data['stdDay']}")
    else:
        st.warning("API 정보를 불러오는 중입니다.")

if 'stdDay' in df.columns:
    st.divider()
    st.subheader("📊 전국 수질 현황")
    fig = px.pie(df.dropna(subset=['stdDay']), names='stdDay', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
