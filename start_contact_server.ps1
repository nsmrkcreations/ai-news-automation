# PowerShell script to start the NewSurgeAI Contact Server

Write-Host "🚀 Starting NewSurgeAI Contact Server..." -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Install/update dependencies
Write-Host "📥 Installing/updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✏️  Please edit .env file to configure email settings" -ForegroundColor Cyan
}

# Start the server
Write-Host "🌐 Starting contact server on http://localhost:5000" -ForegroundColor Green
Write-Host "📧 Contact form will be available at: http://localhost:5000/#contact" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

python contact_server.py