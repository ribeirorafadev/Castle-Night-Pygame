#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🏰 Compilando Castle Night com PyInstaller"
echo "=========================================="

# 1. Ativar venv se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 2. Executar compilação limpa
pyinstaller --clean --noconsole --onefile --name "CastleNight" --hidden-import pygame run_game.py

# 3. Copiar assets lado a lado com o binário
echo "📦 Copiando pasta assets/ para dist/..."
cp -r assets dist/

# 4. Ajustar permissão de execução
chmod +x dist/CastleNight

echo "=========================================="
echo "✅ Build concluído com sucesso em: dist/"
echo "=========================================="
