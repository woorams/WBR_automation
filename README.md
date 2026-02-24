# WBR_automation

매일 전일자 **Q&A 문의 수**와 **인바운드 콜 인입 수**를 bbarunsonweb에서 자동 수집하여 Google 시트에 기록하는 자동화 도구입니다.

## 사전 준비

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Chrome 브라우저

Selenium이 Chrome을 사용합니다. Chrome이 설치되어 있어야 합니다. (ChromeDriver는 webdriver-manager가 자동 관리)

### 3. Google Sheets API 서비스 계정 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 프로젝트 생성 (또는 기존 프로젝트 선택)
3. **API 및 서비스 > 라이브러리**에서 `Google Sheets API` 사용 설정
4. **API 및 서비스 > 사용자 인증 정보 > 사용자 인증 정보 만들기 > 서비스 계정** 선택
5. 서비스 계정 생성 후, **키 > 키 추가 > JSON** 으로 키 파일 다운로드
6. 다운로드한 JSON 파일을 프로젝트 폴더에 `service_account.json`으로 저장
7. 서비스 계정의 이메일 주소 (예: `xxx@xxx.iam.gserviceaccount.com`)를 Google 시트에 **편집자** 권한으로 공유

### 4. 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 만들고 값을 입력합니다:

```bash
cp .env.example .env
```

```env
BARUNSON_ID=your_id
BARUNSON_PW=your_password
GOOGLE_SERVICE_ACCOUNT_KEY=service_account.json
```

## 사용법

### 수동 실행

```bash
# 전일자 데이터 수집 및 기록
python daily_tracker.py

# 특정 날짜 지정
python daily_tracker.py 2025-03-15
```

### Windows 작업 스케줄러 등록 (매일 자동 실행)

`setup_scheduler.bat`을 **관리자 권한**으로 실행하면 매일 오전 9시에 자동 실행됩니다.

## 파일 구조

| 파일 | 설명 |
|------|------|
| `daily_tracker.py` | 메인 실행 스크립트 |
| `scraper.py` | bbarunsonweb 웹 스크래핑 모듈 |
| `sheets_writer.py` | Google Sheets 기록 모듈 |
| `setup_scheduler.bat` | Windows 작업 스케줄러 등록 스크립트 |
| `.env.example` | 환경변수 템플릿 |

## 대상 Google 시트

- **시트**: `DashBoard(Weekly_FY25)` 탭
- **327행**: Q&A 문의 수
- **328행**: 인바운드 콜 인입 수
- **6행**: 날짜 기준 (G열부터, M/D 형식)

## 참고

- **Barunn_AP WiFi**에 연결된 상태에서 실행해야 bbarunsonweb에 접속 가능합니다.
- 웹사이트 HTML 구조가 변경되면 `scraper.py`의 CSS/XPath 셀렉터를 조정해야 할 수 있습니다.
- 실행 로그는 `daily_tracker.log` 파일에 저장됩니다.
