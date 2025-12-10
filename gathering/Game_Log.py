import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
OUT_DIR = Path("./")

def setup_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,2000")
    opts.add_argument("--lang=ko-KR")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.implicitly_wait(2)
    return driver

def find_select_by_partial_id(driver, partial_id):
    elems = driver.find_elements(By.XPATH, f"//select[contains(@id,'{partial_id}')]")
    return elems[0] if elems else None

def click_search_if_exists(driver):
    btns = driver.find_elements(By.XPATH, "//*[contains(@id,'btnSearch') and (self::a or self::button or self::input)]")
    if btns:
        btns[0].click()
        return True
    btns = driver.find_elements(By.XPATH, "//*[self::a or self::button or self::input][contains(.,'검색')]")
    if btns:
        btns[0].click()
        return True
    try:
        month_sel = find_select_by_partial_id(driver, "ddlMonth")
        if month_sel:
            name_attr = month_sel.get_attribute("name") or month_sel.get_attribute("id")
            if name_attr:
                driver.execute_script("if (window.__doPostBack) { __doPostBack(arguments[0], ''); }", name_attr)
                return True
    except Exception:
        pass
    return False

def wait_tbody_change(driver, old_html, timeout=8):
    end = time.time() + timeout
    while time.time() < end:
        html = driver.page_source
        if html != old_html:
            return True
        time.sleep(0.3)
    return False

def set_series_regular(driver):
    sel = find_select_by_partial_id(driver, "ddlSeries")
    if not sel:
        return
    s = Select(sel)
    try:
        s.select_by_value("0")
        return
    except Exception:
        pass
    for opt in s.options:
        if "정규" in opt.text:
            s.select_by_visible_text(opt.text)
            return

def set_year_month(driver, year, month):
    year_sel = find_select_by_partial_id(driver, "ddlYear")
    month_sel = find_select_by_partial_id(driver, "ddlMonth")
    if year_sel:
        Select(year_sel).select_by_visible_text(str(year))
    if month_sel:
        s = Select(month_sel)
        try:
            s.select_by_value(str(month))
        except Exception:
            mm = f"{int(month):02d}"
            try:
                s.select_by_value(mm)
            except Exception:
                s.select_by_visible_text(str(month))
    old = driver.page_source
    clicked = click_search_if_exists(driver)
    if not clicked:
        try:
            driver.execute_script("document.forms[0].submit();")
        except Exception:
            pass
    wait_tbody_change(driver, old_html=old, timeout=8)

def parse_month_table(html, season_year):
    soup = BeautifulSoup(html, "lxml")
    tbodies = soup.find_all("tbody")
    if not tbodies:
        return []
    records = []
    date_in_row = None
    re_mmdd = re.compile(r"(\d{2})\.(\d{2})")
    for tbody in tbodies:
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if not tds:
                continue
            day_td = tr.find("td", {"class": "day"})
            if day_td:
                m = re_mmdd.search(day_td.get_text(strip=True))
                if not m:
                    continue
                mm, dd = m.group(1), m.group(2)
                try:
                    date_in_row = datetime(season_year, int(mm), int(dd)).strftime("%Y-%m-%d")
                except Exception:
                    date_in_row = None
            play_td = tr.find("td", {"class": "play"})
            if not (play_td and date_in_row):
                continue
            spans_direct = play_td.find_all("span", recursive=False)
            if len(spans_direct) < 2:
                all_spans = play_td.find_all("span")
                if len(all_spans) >= 2:
                    away_team = all_spans[0].get_text(strip=True)
                    home_team = all_spans[-1].get_text(strip=True)
                else:
                    continue
            else:
                away_team = spans_direct[0].get_text(strip=True)
                home_team = spans_direct[-1].get_text(strip=True)
            em = play_td.find("em")
            nums = []
            if em:
                for s in em.find_all("span"):
                    txt = s.get_text(strip=True)
                    if txt.isdigit():
                        nums.append(int(txt))
            if len(nums) < 2:
                continue
            away_runs, home_runs = nums[0], nums[1]
            records.append({
                "date": date_in_row,
                "season": season_year,
                "home_team": home_team,
                "away_team": away_team,
                "home_runs": home_runs,
                "away_runs": away_runs,
            })
    return records

def scrape_regular_season(year_from=2001, year_to=2025, out_dir=OUT_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    driver = setup_driver(headless=True)
    driver.get(BASE_URL)
    all_by_year = defaultdict(list)
    try:
        set_series_regular(driver)
        for year in range(year_from, year_to + 1):
            year_records = []
            for month in tqdm(range(1, 13), desc=f"{year}", leave=False):
                try:
                    set_year_month(driver, year, month)
                except Exception:
                    continue
                html = driver.page_source
                recs = parse_month_table(html, season_year=year)
                if recs:
                    year_records.extend(recs)
            if year_records:
                df = pd.DataFrame(year_records).drop_duplicates(
                    subset=["date", "home_team", "away_team", "home_runs", "away_runs"]
                ).sort_values(["date", "away_team", "home_team"]).reset_index(drop=True)
                out_path = out_dir / f"games_{year}.csv"
                df.to_csv(out_path, index=False, encoding="utf-8-sig")
                print(f"[OK] {year}: {len(df)} games → {out_path}")
            else:
                print(f"[WARN] {year}: no regular-season games found")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_regular_season(2001, 2025, OUT_DIR)
