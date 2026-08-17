---
name: build-pipeline
description: Use quando for compilar, empacotar ou solucionar problemas de builds de executáveis PyInstaller para Windows ou Linux neste projeto.
---

# Pipeline de Build do PyInstaller

## Visão Geral
Diretrizes para criação de executáveis de arquivo único (`--onefile`) do Castle Night mantendo integridade estrita de caminhos relativos para assets estáticos.

## Regra de Ouro
O PyInstaller **NÃO** faz compilação cruzada (Cross-Compilation).
- Para gerar um `.exe` para Windows, execute o PyInstaller dentro do Windows.
- Para gerar um binário para Linux, execute o PyInstaller dentro do Linux.

## Fluxo de Execução

```bash
# 1. Ativar ambiente virtual
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# 2. Executar PyInstaller na raiz apontando para o run_game.py
pyinstaller --noconsole --onefile --name "CastleNight" --hidden-import pygame run_game.py
```

## Alocação Crítica de Assets
Após a compilação:
1. Diretório do artefato gerado: `dist/`
2. **Passo Obrigatório:** Copie a pasta `assets/` da raiz do projeto para dentro de `dist/`, de modo que `dist/assets/` resida lado a lado com o executável.

## Resolução de Falhas de Caminhos (Paths)
Garanta que o `AssetLoader` resolva caminhos dinamicamente verificando `sys.frozen`:
```python
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
```
