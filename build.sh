#!/usr/bin/env bash
# ==============================================================================
# Castle Night — Script de Build e Empacotamento para Linux & macOS
# ==============================================================================
# Compatibilidade: Linux (Ubuntu, Debian, Mint, Fedora, Arch) e macOS.
# Para Windows: Utilize o script equivalente 'build.ps1' (PowerShell).
# Documentação completa: docs/guide-compilation.md
# ==============================================================================
set -e

echo "=========================================="
echo "🏰 Compilando Castle Night (Linux / macOS)"
echo "=========================================="

# 1. Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# 2. Executar compilação com PyInstaller
pyinstaller --clean --noconsole --onefile --name "CastleNight" --hidden-import pygame run_game.py

# 3. Copiar pasta de assets lado a lado com o executável
echo "📦 Copiando pasta assets/ para dist/..."
cp -r assets dist/

# 4. Ajustar permissão de execução no binário
chmod +x dist/CastleNight

echo "=========================================="
echo "✅ Build concluído com sucesso em: dist/"
echo "=========================================="
