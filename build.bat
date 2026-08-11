@echo off
echo ========================================
echo  Building CRISPR Guide Designer
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate
echo ✅ Activated.
echo.

echo Installing dependencies...
pip install PyQt5 biopython pandas numpy matplotlib seaborn requests openpyxl pyinstaller
echo ✅ Done.
echo.

echo Building executable using build.spec...
echo This will take 2-5 minutes...
pyinstaller build.spec
echo.

if exist "dist\CRISPR_Guide_Designer.exe" (
    echo ========================================
    echo  ✅ BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your app is at: dist\CRISPR_Guide_Designer.exe
    echo.
    echo To run: start dist\CRISPR_Guide_Designer.exe
) else (
    echo ========================================
    echo  ❌ BUILD FAILED
    echo ========================================
)

pause