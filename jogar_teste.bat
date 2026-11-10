@echo off
rem Abre o Minecraft 26.3 de desenvolvimento com o mod carregado (nao precisa de launcher).
set "TEMP=%~dp0.tmp\jtmp"
set "TMP=%~dp0.tmp\jtmp"
set "GRADLE_USER_HOME=%~dp0.tmp\gradle-home"
set "GRADLE_OPTS=-Djdk.net.unixdomain.tmpdir=%~dp0.tmp\jtmp"
if not exist "%TEMP%" mkdir "%TEMP%"
cd /d "%~dp0"
call "%~dp0gradlew.bat" runClient
pause
