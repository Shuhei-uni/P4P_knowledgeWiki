echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v261\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v261\fluent\ntbin\win64\tell.exe" Home-Desktop-Shuhei 59554 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v261\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 17216) 
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 22840) 
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 12732)
del "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys\output\meshdat-semi-automated\cleanup-fluent-Home-Desktop-Shuhei-22840.bat"
