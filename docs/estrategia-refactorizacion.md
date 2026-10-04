# Estrategia de refactorización

El código de partida está en `auditoria/codigo_inicial/`. El código que pasa el hook y se propone integrar está en `src/calidad/procesador.py`. Las métricas de abajo salen de las herramientas, el 29 de septiembre de 2026. Los archivos completos están en `evidencias/`.

## Puntos críticos del código inicial

**Duplicación.** Pylint 4.0.9, mensaje R0801, calificación 9.83/10. Marcó líneas parecidas en dos archivos:

- `auditoria/codigo_inicial/registro_rechazo.py`, rango indicado por Pylint: [4:14]
- `auditoria/codigo_inicial/procesador_legacy.py`, rango indicado por Pylint: [13:36]

El bloque repetido arma el mensaje con `linea_1` hasta `linea_7`. En `registrar_aprobacion` la segunda línea sigue diciendo `estado=rechazada`, igual que en el rechazo. La copia arrastró el texto del otro caso.

**Complejidad ciclomática.** `procesar_transferencia_legacy` concentra todas las decisiones en una sola función.

| Herramienta | Resultado |
|---|---|
| Radon 6.0.1 | D (22). Promedio del código inicial: B (6.25) |
| Ruff 0.16.9, regla C901 | 18, por encima del límite de 10 configurado en el proyecto |

**Dependencias desactualizadas.** `requirements-legacy.txt` fija `requests==2.20.0` y `urllib3==1.25.11`. `cotizacion_usd` llama a `requests.get`. Esas versiones no están instaladas en `.venv`. La consulta a PyPI y a OSV, el 29 de septiembre de 2026, dio:

| Paquete | Versión fijada | Última en PyPI | Avisos devueltos por OSV |
|---|---|---|---|
| requests | 2.20.0 | 2.34.2 | 8 |
| urllib3 | 1.25.11 | 2.8.0 | 18 |

Los identificadores están en `evidencias/dependencias.txt`. Este proyecto no ejecuta esas versiones: el aviso indica que no hay que instalar `requirements-legacy.txt`.

## Estrategia aplicada en el código integrado

1. **Un solo armado de mensaje.** `construir_mensaje` recibe el estado como dato. Aprobación y rechazo dejan de copiar el mismo bloque, y el texto `rechazada` no queda pegado en la aprobación.
2. **Decisiones separadas.** El monto, el saldo, la cuenta, la moneda, el canal y los límites están en funciones cortas. `validar_transferencia` las llama en orden. Radon mide esa función como B (10). El promedio del archivo integrado es A (3.1). Ruff, con el límite de 10, no reporta C901 sobre `src` ni sobre `tests`.
3. **La cotización entra desde afuera.** `procesar_transferencia` recibe `obtener_cotizacion`. El código integrado no importa `requests` ni declara dependencias de ejecución. `requirements-legacy.txt` queda solo como evidencia de la auditoría.

Las pruebas cubren cada resultado y usan el patrón AAA. `cotizacion_fija` aporta un valor preparado (stub). `Mock` comprueba si el notificador fue llamado (mock).
