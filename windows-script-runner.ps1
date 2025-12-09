# run-QTranslator.ps1

# Enable UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Exit on error
$ErrorActionPreference = "Stop"

# Check if venv exists
if (-Not (Test-Path "venv")) {
    Write-Host "venv folder not exist" -ForegroundColor Red -BackgroundColor Black

    Write-Host "Creating virtual environment..." -ForegroundColor Yellow -BackgroundColor Black
    try {
        python -m venv venv
        Write-Host "Virtual environment created." -ForegroundColor Green -BackgroundColor Black
    } catch {
        Write-Host "Failed to create venv." -ForegroundColor Red -BackgroundColor Black
        exit 1
    }
}

# Activate virtual environment
$activatePath = "venv\Scripts\Activate.ps1"
if (Test-Path $activatePath) {
    & $activatePath
} elseif (Test-Path "venv\Scripts\activate.bat") {
    # Fallback for cmd activation
    cmd /c "call venv\Scripts\activate.bat && python -c `"import sys; print('Virtual environment activated')`""
} else {
    Write-Host "Activation file not found." -ForegroundColor Red -BackgroundColor Black
    exit 1
}

# Check and install dependencies
try {
    python -c "import deep_translator, arabic_reshaper, bidi, gtts, pygame, pynput, pyperclip, termcolor" 2>&1 | Out-Null
} catch {
    Write-Host "Dependencies need to download..." -ForegroundColor Yellow -BackgroundColor Black
    try {
        pip install deep-translator arabic-reshaper python-bidi gtts pygame pynput pyperclip termcolor
        if ($LASTEXITCODE -ne 0) {
            throw "pip install failed"
        }
    } catch {
        Write-Host "Failed to install dependencies." -ForegroundColor Red -BackgroundColor Black
        exit 1
    }
}

Clear-Host
Write-Host "Dependencies are ready!" -ForegroundColor Green -BackgroundColor Black

# Run the main Python script
python QTranslator.py

# Keep window open if script exits with error
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
