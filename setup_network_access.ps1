# Script to setup network access for Medicine ERP
# Run as Administrator

Write-Host "=== Medicine ERP - Network Access Setup ===" -ForegroundColor Green
Write-Host ""

# Get local IP address
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*" | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"})[0].IPAddress

if (-not $ipAddress) {
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*"})[0].IPAddress
}

Write-Host "Detected IP Address: $ipAddress" -ForegroundColor Yellow
Write-Host ""

# Confirm IP
$confirmIP = Read-Host "Is this IP address correct? (Y/n)"
if ($confirmIP -eq 'n' -or $confirmIP -eq 'N') {
    $ipAddress = Read-Host "Enter your IP address manually"
}

Write-Host ""
Write-Host "Configuring Medicine ERP for network access..." -ForegroundColor Green

# Update .env file
$envPath = ".env"
if (Test-Path $envPath) {
    Write-Host "Updating .env file..." -ForegroundColor Yellow
    
    $envContent = Get-Content $envPath -Raw
    
    # Update or add VITE_API_URL
    if ($envContent -match 'VITE_API_URL=') {
        $envContent = $envContent -replace 'VITE_API_URL=.*', "VITE_API_URL=http://${ipAddress}:8000/api/v1"
    } else {
        $envContent += "`nVITE_API_URL=http://${ipAddress}:8000/api/v1"
    }
    
    # Update or add VITE_WS_URL
    if ($envContent -match 'VITE_WS_URL=') {
        $envContent = $envContent -replace 'VITE_WS_URL=.*', "VITE_WS_URL=ws://${ipAddress}:8001"
    } else {
        $envContent += "`nVITE_WS_URL=ws://${ipAddress}:8001"
    }
    
    Set-Content -Path $envPath -Value $envContent
    Write-Host "✓ .env file updated" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found. Creating from env.example..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    
    $envContent = Get-Content ".env" -Raw
    $envContent += "`nVITE_API_URL=http://${ipAddress}:8000/api/v1"
    $envContent += "`nVITE_WS_URL=ws://${ipAddress}:8001"
    Set-Content -Path ".env" -Value $envContent
    Write-Host "✓ .env file created" -ForegroundColor Green
}

Write-Host ""
Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow

# Add firewall rules
try {
    # Remove old rules if exist
    Remove-NetFirewallRule -DisplayName "Medicine ERP Frontend" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "Medicine ERP Backend" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "Medicine ERP WebSocket" -ErrorAction SilentlyContinue
    
    # Add new rules
    New-NetFirewallRule -DisplayName "Medicine ERP Frontend" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow | Out-Null
    New-NetFirewallRule -DisplayName "Medicine ERP Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow | Out-Null
    New-NetFirewallRule -DisplayName "Medicine ERP WebSocket" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow | Out-Null
    
    Write-Host "✓ Firewall rules added successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not add firewall rules. Please run as Administrator." -ForegroundColor Red
    Write-Host "  Or add rules manually:" -ForegroundColor Yellow
    Write-Host "  - Port 5173 (Frontend)" -ForegroundColor Yellow
    Write-Host "  - Port 8000 (Backend)" -ForegroundColor Yellow
    Write-Host "  - Port 8001 (WebSocket)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  From this computer:  http://localhost:5173" -ForegroundColor White
Write-Host "  From other computers: http://${ipAddress}:5173" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart Docker containers:" -ForegroundColor White
Write-Host "   docker-compose down" -ForegroundColor Gray
Write-Host "   docker-compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open browser on another computer and go to:" -ForegroundColor White
Write-Host "   http://${ipAddress}:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Login with:" -ForegroundColor White
Write-Host "   Username: admin" -ForegroundColor Gray
Write-Host "   Password: admin123" -ForegroundColor Gray
Write-Host ""

# Ask if user wants to restart Docker now
$restart = Read-Host "Restart Docker containers now? (Y/n)"
if ($restart -ne 'n' -and $restart -ne 'N') {
    Write-Host ""
    Write-Host "Restarting Docker containers..." -ForegroundColor Yellow
    docker-compose down
    docker-compose up -d
    Write-Host ""
    Write-Host "✓ Docker containers restarted" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now access the application from:" -ForegroundColor Cyan
    Write-Host "http://${ipAddress}:5173" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Please restart Docker manually when ready:" -ForegroundColor Yellow
    Write-Host "docker-compose down && docker-compose up -d" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

