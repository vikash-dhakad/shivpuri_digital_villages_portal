@echo off
echo ===================================================
echo Starting MySQL Server (VillageConnect)...
echo ===================================================
start "" /B "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --defaults-file="C:\ProgramData\MySQL\MySQL Server 8.4\my.ini"
timeout /t 2 /nobreak >nul
echo MySQL Server is running on port 3306!
