import time
import pandas as pd
import os
import glob
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_batter_info(driver, game_date):
    results = []
    date_str = game_date.strftime('%Y%m%d')
    url = f"https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx?gameDate={date_str}"
    
    print(f"\n[{game_date.strftime('%Y-%m-%d')}] 접속 중...")
    driver.get(url)
    time.sleep(1.5) 

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul[class*='game-list'] > li.game-cont"))
        )
        game_items = driver.find_elements(By.CSS_SELECTOR, "ul[class*='game-list'] > li.game-cont")
        
        if not game_items:
            print("  -> 경기 목록을 찾을 수 없습니다.")
            return results

        print(f"  -> {len(game_items)}개의 경기 박스 발견")
        
        for idx in range(len(game_items)):
            game_no = idx + 1
            
            # DOM 요소 갱신
            game_items = driver.find_elements(By.CSS_SELECTOR, "ul[class*='game-list'] > li.game-cont")
            if idx >= len(game_items): break
            
            target_game = game_items[idx]
            
            try:
                status_text = target_game.find_element(By.CLASS_NAME, "staus").text.strip()
                if "취소" in status_text:
                    print(f"    경기 {game_no}: 취소됨")
                    continue
            except:
                pass 

            print(f"    경기 {game_no} 데이터 수집 시도...")
            
            driver.execute_script("arguments[0].click();", target_game)
            time.sleep(1) 

            try:
                record_tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '리뷰')]"))
                )
                driver.execute_script("arguments[0].click();", record_tab)
                time.sleep(1)
            except Exception as e:
                print(f"    -> '리뷰' 탭 진입 실패 (경기 전 또는 데이터 없음)")
                continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            def extract_starters(team_type):
                name_table_id = f"tbl{team_type}Hitter1"
                stat_table_id = f"tbl{team_type}Hitter3"

                name_table = soup.find('table', {'id': name_table_id})
                stat_table = soup.find('table', {'id': stat_table_id})

                if not name_table or not stat_table:
                    return

                header_id = f"lbl{team_type}Hitter"
                team_header = soup.find('h6', {'id': header_id})
                if team_header:
                    team_name = team_header.get_text().replace('타자 기록', '').strip()
                else:
                    team_name = team_type

                name_rows = name_table.find('tbody').find_all('tr')
                stat_rows = stat_table.find('tbody').find_all('tr')

                seen_orders = set()

                for i, row in enumerate(name_rows):
                    cols = row.find_all(['th', 'td'])
                    if not cols: continue

                    order_text = row.find('th').text.strip()
                    if order_text in seen_orders or not order_text.isdigit():
                        continue

                    seen_orders.add(order_text)
                    player_name = row.find('td').text.strip()

                    avg = "-"
                    if i < len(stat_rows):
                        stat_cols = stat_rows[i].find_all('td')
                        if stat_cols:
                            avg = stat_cols[-1].text.strip()

                    
                    
                    results.append({
                        'date': game_date.strftime('%Y-%m-%d'),
                        'game_no': game_no,
                        'team': team_name,
                        'order': int(order_text),
                        'name': player_name,
                        'avg': avg
                    })

            extract_starters('Away')
            extract_starters('Home')

    except Exception as e:
        print(f"  에러 발생: {e}")

    return results

if __name__ == "__main__":
    start_year = 2002
    end_year = 2025
    
    print(f"[{start_year} ~ {end_year}] 데이터 수집 작업을 시작합니다.")
    
    for year in range(start_year, end_year + 1):
        input_filename = f"games_{year}.csv"
        
        # 해당 연도의 파일이 있는지 확인
        if not os.path.exists(input_filename):
            print(f"\n[{year}년] {input_filename} 파일이 없습니다. 건너뜁니다.")
            continue
            
        print(f"\n{'='*40}")
        print(f"[{year}년] 데이터 수집 시작 (파일: {input_filename})")
        print(f"{'='*40}")
        
        # 1. 일정 파일 읽기
        try:
            df_schedule = pd.read_csv(input_filename)
            if 'date' not in df_schedule.columns:
                print(f" -> 에러: {input_filename}에 'date' 컬럼이 없습니다.")
                continue
                
            dates = sorted(df_schedule['date'].unique())
            print(f" -> 총 {len(dates)}일의 경기 일정을 확인했습니다.")
            
            driver = setup_driver()
            year_data = []
            
            # 2. 날짜별 크롤링
            for date_str in dates:
                try:
                    current_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                    daily_data = get_batter_info(driver, current_date)
                    year_data.extend(daily_data)
                except Exception as e:
                    print(f" -> {date_str} 처리 중 에러: {e}")
                    continue
            
            driver.quit() 
            
            # 3. 연도별 결과 저장
            if year_data:
                df_result = pd.DataFrame(year_data)
                
                # 컬럼 순서 정리
                cols = ['date', 'game_no', 'team', 'order', 'name', 'avg']
                df_result = df_result[cols]
                
                output_filename = f"kbo_starters_batters_{year}.csv"
                df_result.to_csv(output_filename, index=False, encoding="utf-8-sig")
                print(f"\n[완료] {output_filename} 저장 완료! (데이터 {len(df_result)}건)")
            else:
                print(f"\n[알림] {year}년에는 수집된 데이터가 없습니다.")
                
        except Exception as e:
            print(f"\n[{year}년] 치명적 오류 발생: {e}")
            if 'driver' in locals():
                driver.quit()

    print("\n모든 작업이 종료되었습니다.")