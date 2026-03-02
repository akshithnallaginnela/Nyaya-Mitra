@echo off
echo Fixing frontend dependencies...
echo.

echo Step 1: Removing node_modules and package-lock.json...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
echo Done!
echo.

echo Step 2: Clearing npm cache...
call npm cache clean --force
echo Done!
echo.

echo Step 3: Installing dependencies...
call npm install
echo Done!
echo.

echo Step 4: Installing missing type definitions...
call npm install --save-dev @types/node
echo Done!
echo.

echo All done! You can now run: npm run dev
pause
