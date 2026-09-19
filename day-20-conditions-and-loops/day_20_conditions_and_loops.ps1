# Day 20: Run all implementations and tests (PowerShell)

Write-Host "========================================" -ForegroundColor Green
Write-Host "Running Python Unit Tests..."
Write-Host "========================================" -ForegroundColor Green
python -m unittest test_day_20_conditions_and_loops.py

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Running Python Implementation..."
Write-Host "========================================" -ForegroundColor Green
python day_20_conditions_and_loops.py

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Running JavaScript Implementation..."
Write-Host "========================================" -ForegroundColor Green
node day_20_conditions_and_loops.js

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Compiling and Running C++ Implementation..."
Write-Host "========================================" -ForegroundColor Green
if (Get-Command g++ -ErrorAction SilentlyContinue) {
    g++ -std=c++11 day_20_conditions_and_loops.cpp -o day_20_cpp_app.exe
    .\day_20_cpp_app.exe
    Remove-Item day_20_cpp_app.exe
} else {
    Write-Host "g++ compiler not found. Skipping C++ execution." -ForegroundColor Yellow
}
