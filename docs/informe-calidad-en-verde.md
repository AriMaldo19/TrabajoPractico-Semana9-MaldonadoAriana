# Informe de Calidad en Verde

Trabajo Práctico Semana 3: Automatización de Calidad y Blindaje.

Repositorio: https://github.com/AriMaldo19/TrabajoPractico-Semana9-MaldonadoAriana

Fecha de las mediciones: 29 de septiembre de 2026.

## 1. Enlace entre el Issue y el Pull Request

Issue abierto:

https://github.com/AriMaldo19/TrabajoPractico-Semana9-MaldonadoAriana/issues/1

Título: `Automatizacion de Calidad y Blindaje`.

El Pull Request todavía no existe. No se inventa esa dirección. El enlace trazable queda cerrado cuando el Pull Request cite este Issue, por ejemplo con `Closes #1`. Hasta ese momento, la evidencia de GitHub es solo el Issue.

## 2. Logs del hook de pre-commit

El script es `.githooks/pre-commit`. Git usa la copia `.git/hooks/pre-commit`. Orden obligatorio: Black, Ruff, pytest.

Ejecución en verde, código de salida 0. Archivo: `evidencias/hook-en-verde.txt`.

- Black: 3 archivos sin cambios de formato.
- Ruff: `All checks passed!`
- pytest: `20 passed in 0.30s`.
- Cierre del script: `Todos los controles pasaron. El commit puede continuar.`

Ejecución con fallo del formatter, código de salida 1. Archivo: `evidencias/hook-fallo-formatter.txt`.

Black detectó un archivo temporal mal formateado. El script informó el rechazo y no ejecutó Ruff ni pytest. El archivo temporal se eliminó después de registrar el log. La explicación del corte y de la protección de la rama principal está en `docs/explicacion-pre-commit.md`.

## 3. Reporte de cobertura

Archivo: `evidencias/cobertura.txt`.

Comando medido por ese archivo: pytest 9.1.1 con pytest-cov 7.1.0, cobertura de ramas activada (`--cov-branch`).

| Archivo | Sentencias | Sin ejecutar | Ramas | Ramas parciales | Cover |
|---|---:|---:|---:|---:|---:|
| src/calidad/__init__.py | 2 | 0 | 0 | 0 | 100% |
| src/calidad/procesador.py | 68 | 0 | 30 | 0 | 100% |
| TOTAL | 70 | 0 | 30 | 0 | 100% |

Resultado de esa corrida: 20 pruebas pasadas, en 0.42 segundos. La corrida del hook, unos segundos después, volvió a dar 20 pruebas pasadas y 100% de Cover, en 0.30 segundos. Son dos ejecuciones distintas; las dos quedaron en verde.

El código inicial de `auditoria/` no entra en esta cobertura. Es el material de la auditoría, no el código que se propone integrar.

## 4. Diagnóstico de análisis estático

No se ejecutó SonarQube. El diagnóstico sale de Radon, Ruff, Pylint, PyPI y OSV. El detalle y la estrategia están en `docs/estrategia-refactorizacion.md`.

Código inicial:

- Pylint R0801: bloque de mensaje duplicado entre `registro_rechazo.py` y `procesador_legacy.py`. Calificación 9.83/10.
- Radon: `procesar_transferencia_legacy` en D (22). Promedio B (6.25).
- Ruff C901: la misma función en 18, sobre un límite de 10.
- `requests==2.20.0` (última en PyPI: 2.34.2, 8 avisos OSV) y `urllib3==1.25.11` (última en PyPI: 2.8.0, 18 avisos OSV). Esas versiones no están instaladas.

Código integrado (`src/calidad/procesador.py`):

- Radon: promedio A (3.1). La función más alta es `validar_transferencia`, B (10).
- Ruff sobre `src` y `tests`: sin errores, incluido C901.
- Sin dependencia de `requests` ni de `urllib3`.

## 5. Conclusión

El código de `src` y `tests` pasó el hook completo: formato, linter y 20 pruebas, con Cover de 100% en sentencias y ramas. El código inicial queda archivado en `auditoria/` como evidencia de los problemas y de la refactorización ya aplicada en `src`.

La integración en GitHub sigue pendiente del Pull Request enlazado al Issue #1.
La rama usada para el Pull Request es entrega.
