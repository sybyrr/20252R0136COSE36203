import pandas as pd

# 1. CSV 파일 불러오기
df = pd.read_csv('kbo_starters_regular_season.csv')

# 2. 'team' 컬럼 정리
df['team'] = df['team'].str.replace('  기록', '')

# 3. 'date' 컬럼 날짜 형식 변환
df['date'] = pd.to_datetime(df['date'])


# 4. 날짜별로 등장 순서대로 두 경기씩 묶어서 번호 부여
df['game_no'] = df.groupby('date').cumcount() // 2 + 1

# 5. 연도 추출
df['year'] = df['date'].dt.year
unique_years = df['year'].unique()

# 6. 연도별 파일 분리 저장
for year in unique_years:
    season_df = df[df['year'] == year]
    
    filename = f'kbo_starters_regular_season_{year}.csv'
    
    # year 컬럼 제외하고 저장
    season_df.drop(columns=['year']).to_csv(filename, index=False, encoding="utf-8-sig")
    
    print(f"{filename} 저장 완료")

print("모든 작업 완료")