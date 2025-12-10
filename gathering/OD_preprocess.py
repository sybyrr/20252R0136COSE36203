import pandas as pd
import glob
import os

def process_batters_data_preserve_order():
    # 1. 파일 목록 가져오기
    files = glob.glob("kbo_starters_batters_*.csv")
    files = [f for f in files if "_final" not in f]
    
    print(f"총 {len(files)}개의 데이터 파일을 발견했습니다.")
    
    for filename in files:
        print(f"\n[처리 중] {filename}")
        
        try:
            df = pd.read_csv(filename)

            df['original_order_idx'] = df.index
            
           
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            # 1. 2024년 10월 1일 KT vs SSG 타이브레이커 경기 제거
            mask_date = (df['date'] == '2024-10-01')
            mask_team = (df['team'].str.contains('KT')) | (df['team'].str.contains('SSG'))
            mask_remove = mask_date & mask_team
            
            if mask_remove.any():
                count = mask_remove.sum()
                print(f"  -> [삭제] 2024-10-01 KT/SSG 타이브레이커 경기 데이터 {count}행을 제거합니다.")
                df = df[~mask_remove].copy()
            
 
            # 2. AVG(타율) 시점 변경 (경기 후 -> 경기 전)
            
            df['avg'] = pd.to_numeric(df['avg'], errors='coerce').fillna(0.0)
            
            
            sort_cols = ['name', 'team', 'date']
            if 'game_no' in df.columns:
                sort_cols.append('game_no')
                
            df_sorted = df.sort_values(by=sort_cols)

            df_sorted['pre_game_avg'] = df_sorted.groupby(['name', 'team'])['avg'].shift(1).fillna(0.000)

            df['avg'] = df_sorted['pre_game_avg']
            

            # 3. 원래 순서 복구 및 저장

            df = df.sort_values(by='original_order_idx')
            
            
            df = df.drop(columns=['original_order_idx'])
            
            
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            output_filename = filename.replace(".csv", "_final.csv")
            df.to_csv(output_filename, index=False, encoding="utf-8-sig")
            print(f"  -> [완료] {output_filename} 저장됨 (원래 파일 순서 유지됨)")
            
        except Exception as e:
            print(f"  -> [에러] 파일 처리 중 문제 발생: {e}")

if __name__ == "__main__":
    process_batters_data_preserve_order()