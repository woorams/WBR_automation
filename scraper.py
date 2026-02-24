"""
bbarunsonweb.barunsoncard.com에서 Q&A 문의 수, 인바운드 콜 인입 수를 스크래핑하는 모듈
"""

import logging
from datetime import date, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

BASE_URL = "https://bbarunsonweb.barunsoncard.com"


def create_driver() -> webdriver.Chrome:
    """Chrome WebDriver를 생성한다."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def login(driver: webdriver.Chrome, user_id: str, password: str) -> None:
    """bbarunsonweb에 로그인한다."""
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 15)

    # 로그인 폼 요소 찾기 (사이트 구조에 따라 selector 조정 필요)
    # 일반적인 패턴: input[name="userId"], input[name="userPw"] 등
    id_field = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='text'], input[name*='id'], input[name*='Id']")
        )
    )
    pw_field = driver.find_element(
        By.CSS_SELECTOR, "input[type='password'], input[name*='pw'], input[name*='Pw']"
    )

    id_field.clear()
    id_field.send_keys(user_id)
    pw_field.clear()
    pw_field.send_keys(password)

    # 로그인 버튼 클릭
    login_btn = driver.find_element(
        By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .btn-login, .login-btn"
    )
    login_btn.click()

    # 로그인 성공 대기 (메인 페이지 로딩 or URL 변경)
    wait.until(lambda d: d.current_url != BASE_URL or d.find_elements(By.CSS_SELECTOR, ".sidebar, .gnb, .nav"))
    logger.info("로그인 성공")


def _navigate_to_menu(driver: webdriver.Chrome, menu_path: list[str]) -> None:
    """좌측 메뉴를 순서대로 클릭하여 해당 페이지로 이동한다.

    Args:
        menu_path: 클릭할 메뉴 텍스트 리스트. 예: ["통계 리포트", "CS 통계", "Q&A 통계"]
    """
    wait = WebDriverWait(driver, 10)
    for menu_text in menu_path:
        menu_el = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//a[contains(text(), '{menu_text}')] | //span[contains(text(), '{menu_text}')]/.. | //li[contains(text(), '{menu_text}')]")
            )
        )
        menu_el.click()
        logger.info(f"메뉴 클릭: {menu_text}")
        # 하위 메뉴 펼쳐지거나 페이지 이동 대기
        import time
        time.sleep(1)


def _set_date_and_search(driver: webdriver.Chrome, target_date: date) -> None:
    """조회 날짜를 설정하고 검색 버튼을 클릭한다."""
    wait = WebDriverWait(driver, 10)
    date_str = target_date.strftime("%Y-%m-%d")

    # 시작일/종료일 입력 필드 찾기 (사이트 구조에 따라 조정 필요)
    date_inputs = driver.find_elements(
        By.CSS_SELECTOR, "input[type='date'], input[type='text'][name*='date'], input[type='text'][name*='Date'], input.datepicker"
    )

    if len(date_inputs) >= 2:
        # 시작일, 종료일 모두 같은 날짜로 설정 (전일자 하루 조회)
        for date_input in date_inputs[:2]:
            date_input.clear()
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                date_input, date_str
            )
    elif len(date_inputs) == 1:
        date_input = date_inputs[0]
        date_input.clear()
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            date_input, date_str
        )

    logger.info(f"조회 날짜 설정: {date_str}")

    # 검색/조회 버튼 클릭
    search_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), '조회') or contains(text(), '검색')] | //input[@value='조회' or @value='검색']")
        )
    )
    search_btn.click()

    # 결과 로딩 대기
    import time
    time.sleep(2)


def get_qa_count(driver: webdriver.Chrome, target_date: date) -> int:
    """Q&A 통계 페이지에서 총 접수건 수를 가져온다.

    경로: 통계 리포트 > CS 통계 > Q&A 통계
    """
    _navigate_to_menu(driver, ["통계 리포트", "CS 통계", "Q&A 통계"])
    _set_date_and_search(driver, target_date)

    wait = WebDriverWait(driver, 10)

    # "총 접수건" 텍스트가 포함된 셀 다음의 숫자를 가져온다
    # 방법 1: 테이블에서 "총 접수건" 레이블 옆 값 찾기
    try:
        count_el = wait.until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//th[contains(text(), '총 접수건') or contains(text(), '총접수건')]/following-sibling::td[1]"
                 " | //td[contains(text(), '총 접수건') or contains(text(), '총접수건')]/following-sibling::td[1]")
            )
        )
        count_text = count_el.text.strip().replace(",", "")
        count = int(count_text)
    except Exception:
        # 방법 2: 테이블 첫 번째 행의 특정 열에서 값을 가져오기
        logger.warning("XPath로 '총 접수건'을 찾지 못해 대체 방법 시도")
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if rows:
            cells = rows[0].find_elements(By.TAG_NAME, "td")
            # 일반적으로 총합 행은 마지막 행이거나 첫 번째 행
            count_text = cells[0].text.strip().replace(",", "") if cells else "0"
            count = int(count_text) if count_text.isdigit() else 0
        else:
            raise ValueError("Q&A 통계 테이블에서 데이터를 찾을 수 없습니다.")

    logger.info(f"Q&A 총 접수건: {count}")
    return count


def get_inbound_call_count(driver: webdriver.Chrome, target_date: date) -> int:
    """콜센터 연결률 통계 페이지에서 총인바운드콜 수를 가져온다.

    경로: 통계 리포트 > 콜센터 > 콜센터 연결률 통계
    """
    _navigate_to_menu(driver, ["통계 리포트", "콜센터", "콜센터 연결률 통계"])
    _set_date_and_search(driver, target_date)

    wait = WebDriverWait(driver, 10)

    # "총인바운드콜" 텍스트가 포함된 셀 다음의 숫자를 가져온다
    try:
        count_el = wait.until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//th[contains(text(), '총인바운드콜') or contains(text(), '총 인바운드콜')]/following-sibling::td[1]"
                 " | //td[contains(text(), '총인바운드콜') or contains(text(), '총 인바운드콜')]/following-sibling::td[1]")
            )
        )
        count_text = count_el.text.strip().replace(",", "")
        count = int(count_text)
    except Exception:
        # 대체 방법: 테이블 헤더에서 "총인바운드콜" 열 인덱스를 찾아서 해당 열 값 가져오기
        logger.warning("XPath로 '총인바운드콜'을 찾지 못해 대체 방법 시도")
        headers = driver.find_elements(By.CSS_SELECTOR, "table thead th")
        col_idx = None
        for i, th in enumerate(headers):
            if "총인바운드콜" in th.text or "총 인바운드콜" in th.text:
                col_idx = i
                break

        if col_idx is not None:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            if rows:
                cells = rows[0].find_elements(By.TAG_NAME, "td")
                count_text = cells[col_idx].text.strip().replace(",", "")
                count = int(count_text) if count_text.isdigit() else 0
            else:
                raise ValueError("콜센터 통계 테이블에서 데이터 행을 찾을 수 없습니다.")
        else:
            raise ValueError("'총인바운드콜' 컬럼 헤더를 찾을 수 없습니다.")

    logger.info(f"총인바운드콜: {count}")
    return count


def scrape_daily_stats(user_id: str, password: str, target_date: date | None = None) -> dict:
    """전일자 Q&A 문의 수, 인바운드 콜 수를 스크래핑하여 반환한다.

    Args:
        user_id: 로그인 아이디
        password: 로그인 비밀번호
        target_date: 조회할 날짜 (기본값: 어제)

    Returns:
        {"qa_count": int, "inbound_call_count": int, "target_date": date}
    """
    if target_date is None:
        target_date = date.today() - timedelta(days=1)

    driver = create_driver()
    try:
        login(driver, user_id, password)
        qa_count = get_qa_count(driver, target_date)
        inbound_call_count = get_inbound_call_count(driver, target_date)
        return {
            "qa_count": qa_count,
            "inbound_call_count": inbound_call_count,
            "target_date": target_date,
        }
    finally:
        driver.quit()
