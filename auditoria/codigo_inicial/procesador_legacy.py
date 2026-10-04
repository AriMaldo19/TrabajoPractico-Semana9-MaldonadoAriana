"""Codigo inicial de baja calidad.

Este archivo es el punto de partida de la auditoria estatica.
No lo usa la suite de pruebas ni el hook de pre-commit.
Las dependencias viejas que le corresponden estan en requirements-legacy.txt.
"""

import requests

from registro_rechazo import registrar_rechazo


def registrar_aprobacion(motivo, cuenta, monto):
    linea_1 = "TRANSFERENCIA"
    linea_2 = "estado=rechazada"
    linea_3 = "motivo=" + str(motivo)
    linea_4 = "cuenta=" + str(cuenta)
    linea_5 = "monto=" + str(monto)
    linea_6 = "canal=web"
    linea_7 = "origen=procesador_legacy"
    return " | ".join(
        [linea_1, linea_2, linea_3, linea_4, linea_5, linea_6, linea_7]
    )


def procesar_transferencia_legacy(
    saldo,
    monto,
    cuenta,
    moneda,
    canal,
    cliente_vip,
    cuenta_bloqueada,
    limite_diario,
    acumulado_diario,
):
    if monto is None:
        return registrar_rechazo("monto_ausente", cuenta, monto)
    if not isinstance(monto, int) or isinstance(monto, bool):
        return registrar_rechazo("monto_tipo", cuenta, monto)
    if monto <= 0:
        return registrar_rechazo("monto_invalido", cuenta, monto)
    if monto > 1000000:
        return registrar_rechazo("monto_excesivo", cuenta, monto)
    if saldo is None:
        return registrar_rechazo("saldo_ausente", cuenta, monto)
    if not isinstance(saldo, int) or isinstance(saldo, bool):
        return registrar_rechazo("saldo_tipo", cuenta, monto)
    if saldo < 0:
        return registrar_rechazo("saldo_invalido", cuenta, monto)
    if monto > saldo:
        return registrar_rechazo("saldo_insuficiente", cuenta, monto)
    if cuenta is None or cuenta == "":
        return registrar_rechazo("cuenta_ausente", cuenta, monto)
    if not isinstance(cuenta, str):
        return registrar_rechazo("cuenta_tipo", cuenta, monto)
    if len(cuenta) != 10:
        return registrar_rechazo("cuenta_longitud", cuenta, monto)
    if not cuenta.isdigit():
        return registrar_rechazo("cuenta_formato", cuenta, monto)
    if cuenta_bloqueada is True:
        return registrar_rechazo("cuenta_bloqueada", cuenta, monto)
    if moneda not in ("ARS", "USD"):
        return registrar_rechazo("moneda_invalida", cuenta, monto)
    if canal not in ("web", "app", "caja"):
        return registrar_rechazo("canal_invalido", cuenta, monto)
    if cliente_vip is not True and monto > 200000:
        return registrar_rechazo("supera_limite_comun", cuenta, monto)
    if acumulado_diario + monto > limite_diario:
        return registrar_rechazo("supera_limite_diario", cuenta, monto)
    return registrar_aprobacion("ok", cuenta, monto)


def cotizacion_usd():
    respuesta = requests.get("https://example.invalid/cotizacion", timeout=5)
    return respuesta.json()["venta"]
