"""
Google Sheets에 데이터를 기록하는 모듈

시트 구조:
- 탭: DashBoard(Weekly_FY25)
- 6행: 날짜 (M/D 형식, G6=1/1 즉 2025.01.01부터 시작)
- 327행: Q&A 문의 수
- 328행: 인바운드 콜 인입 수
"""

import logging
from datetime import date

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SPREADSHEET_ID = "1TZiqBvutsozibzfIxxbn_n-q1rkqArjFCw2XhFb8HW0"
SHEET_NAME = "DashBoard(Weekly_FY25)"
DATE_ROW = 6
QA_ROW = 327
INBOUND_CALL_ROW = 328
DATE_START_COL = 7  # G열 = 7 (1-indexed)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_client(service_account_key_path: str) -> gspread.Client:
    """서비스 계정 키로 인증된 gspread 클라이언트를 반환한다."""
    creds = Credentials.from_service_account_file(
        service_account_key_path, scopes=SCOPES
    )
    return gspread.authorize(creds)


def find_column_for_date(worksheet: gspread.Worksheet, target_date: date) -> int | None:
    """6행에서 target_date에 해당하는 열 번호(1-indexed)를 찾는다.

    날짜 형식은 M/D (예: 1/1, 2/23, 12/31)
    """
    # 6행 전체를 가져온다
    row_values = worksheet.row_values(DATE_ROW)
    target_str = f"{target_date.month}/{target_date.day}"

    for col_idx, cell_value in enumerate(row_values, start=1):
        cell_value_stripped = str(cell_value).strip()
        if cell_value_stripped == target_str:
            logger.info(f"날짜 '{target_str}' → 열 {col_idx} 에서 발견")
            return col_idx

    logger.error(f"날짜 '{target_str}'을 6행에서 찾을 수 없습니다.")
    return None


def write_daily_stats(
    service_account_key_path: str,
    target_date: date,
    qa_count: int,
    inbound_call_count: int,
) -> None:
    """Google 시트에 일일 통계를 기록한다.

    Args:
        service_account_key_path: 서비스 계정 JSON 키 파일 경로
        target_date: 기록할 날짜
        qa_count: Q&A 문의 수
        inbound_call_count: 인바운드 콜 인입 수
    """
    client = get_client(service_account_key_path)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.worksheet(SHEET_NAME)

    col = find_column_for_date(worksheet, target_date)
    if col is None:
        raise ValueError(
            f"날짜 {target_date.strftime('%m/%d')} 에 해당하는 열을 찾을 수 없습니다. "
            f"시트의 6행에 해당 날짜가 있는지 확인하세요."
        )

    # 327행, 328행에 값 기록
    worksheet.update_cell(QA_ROW, col, qa_count)
    logger.info(f"Q&A 문의 수 {qa_count} → 행 {QA_ROW}, 열 {col} 기록 완료")

    worksheet.update_cell(INBOUND_CALL_ROW, col, inbound_call_count)
    logger.info(f"인바운드 콜 인입 수 {inbound_call_count} → 행 {INBOUND_CALL_ROW}, 열 {col} 기록 완료")
