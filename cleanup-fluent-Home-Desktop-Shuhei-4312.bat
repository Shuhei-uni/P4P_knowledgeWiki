echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v252\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v252\fluent\ntbin\win64\tell.exe" Home-Desktop-Shuhei 49450 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v252\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 41776)
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 37424)
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 4312)
if /i "%LOCALHOST%"=="Home-Desktop-Shuhei" (%KILL_CMD% 4964)
del "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\cleanup-fluent-Home-Desktop-Shuhei-4312.bat"
