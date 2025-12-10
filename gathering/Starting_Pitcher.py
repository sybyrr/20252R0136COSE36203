import time
import pandas as pd
import glob
from datetime import datetime, timedelta
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

def get_starter_info(driver, game_date):
    results = []
    date_str = game_date.strftime('%Y%m%d')
    url = f"https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx?gameDate={date_str}"
    
    print(f"\n[{game_date.strftime('%Y-%m-%d')}] 접속 중...")
    driver.get(url)
    time.sleep(2) 

    try:
        game_items = driver.find_elements(By.CSS_SELECTOR, "ul[class*='game-list'] > li.game-cont")
        
        if not game_items:
            print("  -> 경기 목록을 찾을 수 없습니다.")
            return results

        print(f"  -> {len(game_items)}개의 경기 박스 발견")
        
        for idx in range(len(game_items)):
            game_items = driver.find_elements(By.CSS_SELECTOR, "ul[class*='game-list'] > li.game-cont")
            if idx >= len(game_items): break
            
            target_game = game_items[idx]
            
            try:
                status_text = target_game.find_element(By.CLASS_NAME, "staus").text.strip()
                if "취소" in status_text:
                    print(f"    경기 {idx+1}: 취소됨")
                    continue
            except:
                pass 

            print(f"    경기 {idx+1} 클릭 및 데이터 수집 시도...")
            
            driver.execute_script("arguments[0].click();", target_game)
            time.sleep(1.5) 

            try:
                record_tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '리뷰')]"))
                )
                driver.execute_script("arguments[0].click();", record_tab)
                time.sleep(1.5)
            except Exception as e:
                print(f"    -> '리뷰' 탭 진입 실패 (아직 경기 전이거나 데이터 없음)")
                continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            def extract_pitcher(table_id):
                table = soup.find('table', {'id': table_id})
                if not table: return

                team_type = "원정" if "Away" in table_id else "홈"
                
                team_header_id = table_id.replace('tbl', 'lbl') 
                team_header = soup.find('h6', {'id': team_header_id})
                
                if team_header:
                    team_name = team_header.get_text().replace('투수', '').strip()
                else:
                    team_name = team_type

                rows = table.find('tbody').find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 2: continue
                    
                    role = cols[1].text.strip()
                    if role == '선발':
                        p_name = cols[0].text.strip()
                        era = cols[16].text.strip() if len(cols) > 16 else "-"
                        
                        print(f"      [{team_name}] 선발: {p_name} (ERA: {era})")
                        results.append({
                            'date': game_date.strftime('%Y-%m-%d'),
                            'team': team_name,
                            'name': p_name,
                            'era': era
                        })

            extract_pitcher('tblAwayPitcher')
            extract_pitcher('tblHomePitcher')

    except Exception as e:
        print(f"  에러 발생: {e}")

    return results

if __name__ == "__main__":
    driver = setup_driver() 
    
    csv_files = glob.glob("games_*.csv")
    target_dates = set()
    
    print("CSV 파일 읽는 중...")
    for f in csv_files:
        try:
            df_temp = pd.read_csv(f)
            target_dates.update(df_temp['date'].astype(str).tolist())
        except Exception as e:
            print(f"{f} 읽기 실패: {e}")
            
    sorted_dates = sorted(list(target_dates))
    print(f"총 {len(sorted_dates)}일의 경기 일정을 확인했습니다.")

    all_data = []
    
    for date_str in sorted_dates:
        try:
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            data = get_starter_info(driver, current_date)
            all_data.extend(data)
        except ValueError:
            continue
        
    driver.quit()
    
    if all_data:
        df = pd.DataFrame(all_data)
        print("\n=== 결과 ===")
        print(df.head())
        df.to_csv("kbo_starters_regular_season.csv", index=False, encoding="utf-8-sig")