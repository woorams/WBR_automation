"""
매일 전일자 Q&A 문의 수, 인바운드 콜 인입 수를 수집하여 Google 시트에 기록하는 메인 스크립트

사용법:
    python daily_tracker.py              # 전일자 데이터 수집 및 기록
    python daily_tracker.py 2025-03-15   # 특정 날짜 데이터 수집 및 기록
"""

import logging
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from scraper import scrape_daily_stats
from sheets_writer import write_daily_stats

# .env 파일 로드 (스크립트 위치 기준)
load_dotenv(Path(__file__).parent / ".env")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(__file__).parent / "daily_tracker.log", encoding="utf-8"
        ),
    ],
)
logger = logging.getLogger(__name__)


def main():
    # 환경 변수 확인
    barunson_id = os.getenv("BARUNSON_ID")
    barunson_pw = os.getenv("BARUNSON_PW")
    sa_key_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "service_account.json")

    if not barunson_id or not barunson_pw:
        logger.error("BARUNSON_ID, BARUNSON_PW 환경변수를 .env 파일에 설정하세요.")
        sys.exit(1)

    if not Path(sa_key_path).is_absolute():
        sa_key_path = str(Path(__file__).parent / sa_key_path)

    if not Path(sa_key_path).exists():
        logger.error(f"서비스 계정 키 파일을 찾을 수 없습니다: {sa_key_path}")
        sys.exit(1)

    # 대상 날짜 결정 (인자 또는 전일자)
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"날짜 형식이 올바르지 않습니다: {sys.argv[1]} (YYYY-MM-DD 형식 필요)")
            sys.exit(1)
    else:
        target_date = date.today() - timedelta(days=1)

    logger.info(f"=== 일일 데이터 수집 시작 (대상 날짜: {target_date}) ===")

    # 1. 웹에서 데이터 스크래핑
    try:
        stats = scrape_daily_stats(barunson_id, barunson_pw, target_date)
        logger.info(f"스크래핑 결과: Q&A 문의 수={stats['qa_count']}, 인바운드 콜={stats['inbound_call_count']}")
    except Exception as e:
        logger.error(f"웹 스크래핑 실패: {e}", exc_info=True)
        sys.exit(1)

    # 2. Google 시트에 기록
    try:
        write_daily_stats(
            sa_key_path,
            target_date,
            stats["qa_count"],
            stats["inbound_call_count"],
        )
        logger.info("Google 시트 기록 완료!")
    except Exception as e:
        logger.error(f"Google 시트 기록 실패: {e}", exc_info=True)
        sys.exit(1)

    logger.info("=== 일일 데이터 수집 완료 ===")


if __name__ == "__main__":
    main()
