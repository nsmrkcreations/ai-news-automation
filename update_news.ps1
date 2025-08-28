# Set working directory to script location
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptPath

# Activate Python environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
}

# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Add project root to Python path
$env:PYTHONPATH = "$scriptPath"

# Run the Python script
python src/scheduled_update.py

# Deactivate Python environment if it was activated
if (Get-Command deactivate -errorAction SilentlyContinue) {
    deactivate
}
