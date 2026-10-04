# Hook de pre-commit

El archivo `.githooks/pre-commit` es el script local del control. La copia que Git ejecuta está en `.git/hooks/pre-commit`. Antes de guardar un commit, Git corre ese script. El script hace tres controles, siempre en este orden:

1. Formatter: Black
2. Linter: Ruff
3. Pruebas unitarias: pytest, con cobertura de ramas

Si un control falla, el script escribe el motivo y termina con código 1. Los controles que siguen no se ejecutan. Git, al recibir el código 1, no guarda el commit.

## Qué se ve en la consola cuando algo falla

Se probó el primer control con un archivo temporal mal formateado, `src/calidad/_mal_formato.py`. Ese archivo se borró después de la prueba. El resultado quedó en `evidencias/hook-fallo-formatter.txt` y el script terminó con código 1. En la consola, Black avisó `would reformat` sobre ese archivo y `1 file would be reformatted, 3 files would be left unchanged`. Después el script escribió:

```text
FALLO: Black encontro archivos sin el formato del proyecto.
El commit fue rechazado. El linter y las pruebas no se ejecutan.
```

En esa salida no aparecen Ruff ni pytest. El script se detuvo en Black.

El mismo corte ocurre en los otros dos controles:

- Si Black pasa y Ruff encuentra un problema, pytest no llega a ejecutarse.
- Si Black y Ruff pasan, y una prueba falla, el script termina en el paso 3.

## Cuando los tres controles pasan

La ejecución en verde quedó en `evidencias/hook-en-verde.txt`. Black dejó los archivos sin cambios, Ruff informó `All checks passed!` y pytest informó `20 passed`. Al final el script imprime: `Todos los controles pasaron. El commit puede continuar.` y termina con código 0.

## Por qué esto protege la rama principal

La rama principal debe recibir solo cambios que ya pasaron el formato, el linter y las pruebas. El hook corre en la máquina local, antes de que Git guarde el commit. Si el script termina con código 1, Git no guarda ese commit: el cambio no entra al historial, no se puede subir y no se puede fusionar. El fallo queda en la copia de trabajo de quien está programando.

En esta carpeta todavía no hay un commit. Una prueba de `git commit` se detuvo antes del hook porque Git todavía no tiene tu nombre y tu correo en este repositorio. Eso se configura en el paso siguiente, solo dentro de esta carpeta.
