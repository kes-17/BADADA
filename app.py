import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. 페이지 및 디자인 설정 (완벽 유지)
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

# 2. 종합 오류 방어 및 데이터 연결 로직
if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {"serviceKey": api_key, "numOfRows": "300", "pageNo": "1", "resultType": "json", "RES_YEAR": "2026"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'getOceansBeachSeawaterInfo' in data and 'item' in data['getOceansBeachSeawaterInfo']:
                items = data['getOceansBeachSeawaterInfo']['item']
                
                # 데이터가 존재할 때만 처리 (오류 방지)
                if items and isinstance(items, list) and len(items) > 0:
                    df_api = pd.DataFrame(items)
                    # API의 해수욕장명 컬럼을 우리 데이터와 맞춤
                    if 'beachNm' in df_api.columns:
                        df_api = df_api.rename(columns={'beachNm': '해수욕장명'})
                    
                    if '해수욕장명' in df_api.columns:
                        df = pd.merge(df, df_api, on='해수욕장명', how='left')
                        st.sidebar.success("데이터 로드 완료!")
                    else:
                        st.sidebar.warning("데이터는 왔으나 '해수욕장명' 정보를 찾을 수 없습니다.")
                else:
                    st.sidebar.warning("API 서버에 데이터가 없습니다.")
    except Exception as e:
        st.sidebar.error(f"연결 오류 발생: {e}")

# 3. 지도 및 선택 (디자인 유지)
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    st.map(df[df['해수욕장명'] == selected_beach], latitude='위도', longitude='경도')

with col2:
    st.metric(label="🌊 해수욕장명", value=beach_data['해수욕장명'])
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    
    # 수질 데이터 표시 (항목 자동 탐색)
    water_cols = [c for c in df.columns if '적합' in c or '수질' in c]
    target_col = water_cols[0] if water_cols else None
    
    if target_col and target_col in beach_data and pd.notnull(beach_data[target_col]):
        st.markdown(f"### 수질 상태: {beach_data[target_col]}")
    else:
        st.warning("수질 정보를 불러오지 못했습니다. (데이터 미등록 구간)")

if target_col and target_col in df.columns:
    st.divider()
    st.subheader("📊 전국 수질 현황")
    fig = px.pie(df.dropna(subset=[target_col]), names=target_col, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
