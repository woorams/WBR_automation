@echo off
REM ============================================================
REM Windows 작업 스케줄러에 매일 자동 실행 작업을 등록합니다.
REM 매일 오전 9시에 daily_tracker.py를 실행합니다.
REM 관리자 권한으로 실행하세요.
REM ============================================================

SET TASK_NAME=WBR_DailyTracker
SET SCRIPT_DIR=%~dp0
SET PYTHON_PATH=python

echo [정보] 작업 스케줄러에 '%TASK_NAME%' 작업을 등록합니다...
echo [정보] 스크립트 경로: %SCRIPT_DIR%daily_tracker.py
echo [정보] 매일 오전 9:00에 실행됩니다.
echo.

schtasks /create /tn "%TASK_NAME%" /tr "%PYTHON_PATH% \"%SCRIPT_DIR%daily_tracker.py\"" /sc daily /st 09:00 /f

if %errorlevel%==0 (
    echo.
    echo [성공] 작업이 등록되었습니다!
    echo [정보] 작업 확인: schtasks /query /tn "%TASK_NAME%"
    echo [정보] 작업 삭제: schtasks /delete /tn "%TASK_NAME%" /f
) else (
    echo.
    echo [실패] 작업 등록에 실패했습니다. 관리자 권한으로 다시 실행하세요.
)

pause
