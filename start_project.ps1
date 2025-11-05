# Medicine ERP - Quick Start Script
# Run this AFTER starting Docker Desktop

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   Medicine ERP - Quick Start" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    docker ps | Out-Null
    $dockerRunning = $true
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is NOT running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Docker Desktop and run this script again." -ForegroundColor Yellow
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""

# Navigate to project directory
$projectPath = "C:\Users\Kudarov Umar\Desktop\My Projects\Medicine"
Write-Host "Navigating to project: $projectPath" -ForegroundColor Yellow
Set-Location $projectPath

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Start all services
Write-Host "Starting all services..." -ForegroundColor Green
docker-compose up -d

# Wait for services to initialize
Write-Host "Waiting for services to initialize (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check if database is ready
Write-Host "Checking database health..." -ForegroundColor Yellow
$dbReady = $false
for ($i = 1; $i -le 5; $i++) {
    try {
        $result = docker-compose exec -T db pg_isready -U postgres 2>&1
        if ($result -match "accepting connections") {
            $dbReady = $true
            Write-Host "✓ Database is ready" -ForegroundColor Green
            break
        }
    } catch {}
    Write-Host "  Attempt $i/5 - waiting..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

if (-not $dbReady) {
    Write-Host "✗ Database is not responding" -ForegroundColor Red
    Write-Host "Check logs: docker-compose logs db" -ForegroundColor Yellow
}

Write-Host ""

# Apply migrations
Write-Host "Applying database migrations..." -ForegroundColor Green
docker-compose exec -T backend python manage.py migrate

Write-Host ""

# Show container status
Write-Host "Container Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   Project Started Successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor White
Write-Host "  Frontend:    " -NoNewline; Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend API: " -NoNewline; Write-Host "http://localhost:8000/api/v1/" -ForegroundColor Cyan
Write-Host "  Admin Panel: " -NoNewline; Write-Host "http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "  API Docs:    " -NoNewline; Write-Host "http://localhost:8000/api/docs/" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view logs:" -ForegroundColor White
Write-Host "  docker-compose logs -f backend" -ForegroundColor Gray
Write-Host "  docker-compose logs -f frontend" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop the project:" -ForegroundColor White
Write-Host "  docker-compose down" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

