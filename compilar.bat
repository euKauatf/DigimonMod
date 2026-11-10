@echo off
rem Compila o mod. O .jar final fica em build\libs\
rem A pasta temporaria sem acentos evita um erro do Java no Windows
rem quando o nome do usuario tem acento (ex.: Usuario).
set "TEMP=%~dp0.tmp\jtmp"
set "TMP=%~dp0.tmp\jtmp"
set "GRADLE_USER_HOME=%~dp0.tmp\gradle-home"
set "GRADLE_OPTS=-Djdk.net.unixdomain.tmpdir=%~dp0.tmp\jtmp"
if not exist "%TEMP%" mkdir "%TEMP%"
cd /d "%~dp0"
call "%~dp0gradlew.bat" build
echo.
echo Pronto. O mod esta em build\libs\
pause
