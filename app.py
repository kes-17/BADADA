import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. 페이지 및 디자인 설정
st.set_page_config(page_title="바다로 떠나자! 🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #e0f7fa, #ffffff); }
    h1 { color: #006064; text-shadow: 2px 2px 4px #aaa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 병합
@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

# 헤더
st.title("🌊 전국 해수욕장 수질 가이드")
st.markdown("### 🏖️ 가고 싶은 해수욕장의 수질을 확인해보세요!")

# 3. 데이터 로드 및 병합 (사이드바 API)
df = load_data()
api_key = st.sidebar.text_input("공공데이터 API 키", type="password")

if api_key:
    url = f"http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality?serviceKey={api_key}&numOfRows=100&pageNo=1&resultType=json"
    try:
        response = requests.get(url).json()
        df_api = pd.DataFrame(response['body']['items'])
        df = pd.merge(df, df_api, on='해수욕장명', how='left')
        st.sidebar.success("데이터 업데이트 완료! ✅")
    except:
        st.sidebar.error("API 키를 확인해주세요.")

# 4. 지도 시각화 (Interactive)
st.subheader("📍 해수욕장 위치와 상세 정보")
# 지도에서 선택된 정보를 보기 위한 세팅
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())

# 선택된 해수욕장 데이터 추출
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

# 5. 대시보드 레이아웃
col1, col2 = st.columns([2, 1])

with col1:
    # 지도 위에 선택된 장소 표시
    st.map(df, latitude='위도', longitude='경도')

with col2:
    # 선택된 장소의 정보카드
    st.metric(label="🌊 해수욕장명", value=beach_data['해수욕장명'])
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    
    # 수질 데이터가 있는 경우 강조
    if '수질적합여부' in beach_data:
        status = beach_data['수질적합여부']
        color = "green" if status == '적합' else "red"
        st.markdown(f"### 수질 상태: :{color}[{status}]")
    else:
        st.warning("API 정보를 불러와야 수질 상태를 볼 수 있어요!")

# 전체 통계
if '수질적합여부' in df.columns:
    st.divider()
    st.subheader("📊 전국 수질 현황 그래프")
    fig = px.pie(df, names='수질적합여부', color='수질적합여부', 
                 color_discrete_map={'적합':'#20B2AA', '부적합':'#FF6347'}, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
