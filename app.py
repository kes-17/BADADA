import requests
import pandas as pd
import datetime

def get_latest_seawater_data(api_key, sido):
    # 현재 연도부터 과거 5년까지 탐색
    current_year = datetime.datetime.now().year
    
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    
    for year in range(current_year, current_year - 5, -1):
        params = {
            'ServiceKey': api_key,
            'pageNo': '1',
            'numOfRows': '10',
            'resultType': 'json',
            'SIDO_NM': sido,
            'RES_YEAR': str(year)
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 응답 데이터가 존재하는지 확인
            if 'response' in data and 'body' in data['response'] and data['response']['body']['totalCount'] > 0:
                print(f"성공: {year}년 데이터를 찾았습니다.")
                items = data['response']['body']['items']['item']
                return pd.DataFrame(items), str(year)
            else:
                print(f"알림: {year}년 데이터는 아직 준비되지 않았습니다.")
        except Exception as e:
            print(f"오류: {year}년 데이터 조회 중 문제 발생 - {e}")
            
    return pd.DataFrame(), None

# 사용 예시
api_key = "a15b376187c0d83fcdb32b2bebebd20dc1bddd655f7268f142003f6c6da3859c"
sido = "강원도"

df, found_year = get_latest_seawater_data(api_key, sido)

if not df.empty:
    print(f"\n조회된 {found_year}년 데이터 미리보기:")
    print(df[['해수욕장명', '적합여부']].head())
else:
    print("데이터를 찾을 수 없습니다.")
