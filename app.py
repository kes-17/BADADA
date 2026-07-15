import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="🌊 전국 해수욕장 수질 현황", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    h1 { color: #0077be; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌊 전국 해수욕장 수질 적합성 대시보드 🏖️")

# 2. 데이터 로드 (업로드한 CSV 파일 활용)
@st.cache_data
def load_data():
    # 파일 인코딩 확인 후 로드
    df = pd.read_csv('해수욕장_환경정보_공간.csv', encoding='utf-8')
    return df

df = load_data()

# 3. 사이드바: 해수욕장 선택
st.sidebar.header("🐬 데이터 필터링")
api_key = st.sidebar.text_input("공공데이터 API 인증키", type="password")

selected_beaches = st.sidebar.multiselect(
    "조회할 해수욕장을 선택하세요",
    options=df['해수욕장명'].unique(),
    default=df['해수욕장명'].unique()
)

# 선택된 데이터 필터링
df_filtered = df[df['해수욕장명'].isin(selected_beaches)]

# 4. 대시보드 출력
if api_key:
    tab1, tab2 = st.tabs(["📊 통계 대시보드", "📍 지도 시각화"])
    
    with tab1:
        st.subheader(f"선택된 해수욕장: {len(df_filtered)}개")
        # 데이터가 실제 파일 기반으로 표시됨
        st.dataframe(df_filtered[['해수욕장명', '위도', '경도']], use_container_width=True)

    with tab2:
        st.subheader("지도에서 보는 해수욕장 위치 🗺️")
        # st.map 인식용 컬럼명 변경
        map_data = df_filtered.rename(columns={'위도': 'lat', '경도': 'lon'})
        st.map(map_data)
else:
    st.info("사이드바에 API 인증키를 입력하면 대시보드가 활성화됩니다.")
