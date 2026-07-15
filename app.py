import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. 페이지 디자인 설정
st.set_page_config(page_title="바다로 떠나자! 🏖️", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #e0f7fa, #ffffff); }
    h1 { color: #006064; text-shadow: 2px 2px 4px #aaa; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 병합 (캐시 처리)
@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

st.title("🌊 전국 해수욕장 수질 가이드")
st.markdown("### 🏖️ 가고 싶은 해수욕장의 수질을 확인해보세요!")

# 3. API 키 설정 (Secrets 우선)
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    api_key = st.sidebar.text_input("공공데이터 API 키를 입력하세요", type="password")

df = load_data()

# 4. API 데이터 연동
if api_key:
    url = f"http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality?serviceKey={api_key}&numOfRows=100&pageNo=1&resultType=json"
    try:
        response = requests.get(url).json()
        if 'body' in response and 'items' in response['body']:
            df_api = pd.DataFrame(response['body']['items'])
            # 병합: 수질 데이터가 있으면 합치기
            df = pd.merge(df, df_api, on='해수욕장명', how='left')
            st.sidebar.success("데이터 업데이트 완료! ✅")
        else:
            st.sidebar.error("데이터를 가져올 수 없습니다. API 키를 확인하세요.")
    except:
        st.sidebar.error("API 연결 중 오류 발생.")

# 5. UI 구성
selected_beach = st.selectbox("확인할 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    st.map(df, latitude='위도', longitude='경도')

with col2:
    st.subheader(f"ℹ️ {beach_data['해수욕장명']}")
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    
    if '수질적합여부' in beach_data:
        status = beach_data['수질적합여부']
        st.metric("수질 상태", status)
    else:
        st.warning("API 키를 통해 수질 정보를 불러오세요.")

if '수질적합여부' in df.columns:
    st.divider()
    fig = px.pie(df.dropna(subset=['수질적합여부']), names='수질적합여부', 
                 color='수질적합여부', color_discrete_map={'적합':'#20B2AA', '부적합':'#FF6347'}, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
