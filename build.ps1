# ==============================================================================
# Castle Night — Script de Build e Empacotamento para Windows (PowerShell)
# ==============================================================================
# Compatibilidade: Windows 10/11 (PowerShell 5.1+ / PowerShell Core).
# Para Linux / macOS: Utilize o script equivalente 'build.sh' (Bash).
# Documentação completa: docs/guide-compilation.md
# ==============================================================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🏰 Compilando Castle Night (Windows .exe)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Ativar ambiente virtual se existir
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
} elseif (Test-Path ".\venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
}

# 2. Executar compilação com PyInstaller
pyinstaller --clean --noconsole --onefile --name "CastleNight" --hidden-import pygame run_game.py

# 3. Copiar pasta de assets lado a lado com o executável (.exe)
Write-Host "📦 Copiando pasta assets/ para dist/..." -ForegroundColor Yellow
Copy-Item -Path "assets" -Destination "dist\assets" -Recurse -Force

Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ Build concluído com sucesso em: dist\" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
