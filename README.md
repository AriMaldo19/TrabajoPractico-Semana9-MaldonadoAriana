# Automatizacion de Calidad y Blindaje

Trabajo Practico Semana 3. El codigo que se propone integrar esta en `src/`. El codigo inicial, usado solo para la auditoria, esta en `auditoria/`.

## Como correr el control

En PowerShell, parada en esta carpeta:

```powershell
.\.venv\Scripts\python.exe -m black --check src tests
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m pytest --cov=calidad --cov-branch --cov-report=term-missing
```

El hook que Git ejecuta antes de cada commit es `.git/hooks/pre-commit`. El original versionado esta en `.githooks/pre-commit`.

No instales `requirements-legacy.txt`. Esas versiones viejas forman parte de la auditoria y no se usan para correr las pruebas.

## Documentos

- `docs/explicacion-pre-commit.md`
- `docs/estrategia-refactorizacion.md`
- `docs/informe-calidad-en-verde.md`
- `evidencias/`
