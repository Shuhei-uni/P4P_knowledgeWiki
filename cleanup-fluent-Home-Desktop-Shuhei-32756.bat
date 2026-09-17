echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v252\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v252\fluent\ntbin\win64\tell.exe" Home-Desktop-Shuhei 64411 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v252\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 39352)
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 32756)
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 2812)
del "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\cleanup-fluent-Home-Desktop-Shuhei-32756.bat"
