
param(
    [string]$Type = "all"
)

$timestamp = Get-Date -Format "yyyyMMddHHmmss"

if ($Type -eq "all" -or $Type -eq "html") {
    Write-Host "Обновление версии HTML..."
    $htmlContent = Get-Content "frontend/index.html" -Raw
    $htmlContent = $htmlContent -replace 'js/app\.js\?v=\d+', "js/app.js?v=$timestamp"
    $htmlContent = $htmlContent -replace 'css/style\.css\?v=\d+', "css/style.css?v=$timestamp"
    Set-Content "frontend/index.html" $htmlContent
    Write-Host "HTML обновлен с версией $timestamp"
}

if ($Type -eq "all" -or $Type -eq "js") {
    Write-Host "Обновление версии JavaScript..."
    $jsContent = Get-Content "frontend/index.html" -Raw
    $jsContent = $jsContent -replace 'js/app\.js\?v=\d+', "js/app.js?v=$timestamp"
    Set-Content "frontend/index.html" $jsContent
    Write-Host "JavaScript обновлен с версией $timestamp"
}

if ($Type -eq "all" -or $Type -eq "css") {
    Write-Host "Обновление версии CSS..."
    $cssContent = Get-Content "frontend/index.html" -Raw
    $cssContent = $cssContent -replace 'css/style\.css\?v=\d+', "css/style.css?v=$timestamp"
    Set-Content "frontend/index.html" $cssContent
    Write-Host "CSS обновлен с версией $timestamp"
}

Write-Host "Перезапуск фронтенда..."
docker-compose restart frontend

Write-Host "Готово! Версия обновлена до $timestamp"
