@echo off
rem Gera a pasta "distribuicao\mods" com tudo que voce e seus amigos precisam colocar na pasta mods:
rem   - o mod Digimon Aurity
rem   - o GeckoLib (biblioteca de modelos e animacoes que o mod usa)
set "TEMP=%~dp0.tmp\jtmp"
set "TMP=%~dp0.tmp\jtmp"
set "GRADLE_USER_HOME=%~dp0.tmp\gradle-home"
set "GRADLE_OPTS=-Djdk.net.unixdomain.tmpdir=%~dp0.tmp\jtmp"
if not exist "%TEMP%" mkdir "%TEMP%"
cd /d "%~dp0"
rem Apaga versoes antigas do mod para nao irem duas para a pasta mods
if exist "build\libs" del /q "build\libs\digimonaurity-*.jar"
call "%~dp0gradlew.bat" build
if errorlevel 1 (
    echo.
    echo A compilacao falhou. Nada foi copiado.
    pause
    exit /b 1
)
if exist "distribuicao\mods" rmdir /s /q "distribuicao\mods"
mkdir "distribuicao\mods"
copy /y "build\libs\digimonaurity-*.jar" "distribuicao\mods\" >nul
for /r "%GRADLE_USER_HOME%\caches\modules-2\files-2.1\com.geckolib" %%f in (geckolib-neoforge-26.3-*.jar) do (
    echo %%~nxf | findstr /i "sources" >nul || copy /y "%%f" "distribuicao\mods\" >nul
)
echo.
echo Pronto! Envie para seus amigos a pasta "distribuicao" (com o LEIA-ME e a pasta mods).
dir /b "distribuicao\mods"
pause
