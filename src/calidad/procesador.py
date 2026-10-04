"""Procesador de transferencias listo para integrar.

Cada decision vive en una funcion corta. La cotizacion y el aviso al
cliente llegan desde afuera, asi este modulo no depende de una libreria
HTTP ni de un servicio externo.
"""

from enum import Enum
from typing import Protocol

LONGITUD_CUENTA = 10
LIMITE_COMUN = 200_000
MONEDAS_VALIDAS = ("ARS", "USD")
CANALES_VALIDOS = ("web", "app", "caja")


class EstadoTransferencia(str, Enum):
    APROBADA = "aprobada"
    MONTO_INVALIDO = "monto_invalido"
    SALDO_INVALIDO = "saldo_invalido"
    SALDO_INSUFICIENTE = "saldo_insuficiente"
    CUENTA_INVALIDA = "cuenta_invalida"
    CUENTA_BLOQUEADA = "cuenta_bloqueada"
    MONEDA_INVALIDA = "moneda_invalida"
    CANAL_INVALIDO = "canal_invalido"
    SUPERA_LIMITE_COMUN = "supera_limite_comun"
    SUPERA_LIMITE_DIARIO = "supera_limite_diario"


class Notificador(Protocol):
    def notificar(self, mensaje: str) -> None:
        """Envia el mensaje de una transferencia aprobada."""


def construir_mensaje(estado: str, cuenta: str, monto: int) -> str:
    return " | ".join(
        [
            "TRANSFERENCIA",
            f"estado={estado}",
            f"cuenta={cuenta}",
            f"monto={monto}",
            "canal=web",
            "origen=procesador",
        ]
    )


def cuenta_valida(cuenta: str) -> bool:
    return (
        isinstance(cuenta, str) and cuenta.isdigit() and len(cuenta) == LONGITUD_CUENTA
    )


def validar_monto(monto: int) -> EstadoTransferencia | None:
    if type(monto) is not int or monto <= 0:
        return EstadoTransferencia.MONTO_INVALIDO
    return None


def validar_saldo(saldo: int, monto: int) -> EstadoTransferencia | None:
    if type(saldo) is not int or saldo < 0:
        return EstadoTransferencia.SALDO_INVALIDO
    if monto > saldo:
        return EstadoTransferencia.SALDO_INSUFICIENTE
    return None


def monto_en_pesos(monto: int, moneda: str, obtener_cotizacion) -> int:
    if moneda == "ARS":
        return monto
    if moneda == "USD":
        return monto * obtener_cotizacion()
    raise ValueError("moneda_invalida")


def validar_transferencia(
    saldo: int,
    monto: int,
    cuenta_destino: str,
    moneda: str,
    canal: str,
    cliente_vip: bool,
    cuentas_bloqueadas: set[str],
    limite_diario: int,
    acumulado_diario: int,
) -> EstadoTransferencia:
    error = validar_monto(monto)
    if error is not None:
        return error
    error = validar_saldo(saldo, monto)
    if error is not None:
        return error
    if not cuenta_valida(cuenta_destino):
        return EstadoTransferencia.CUENTA_INVALIDA
    if cuenta_destino in cuentas_bloqueadas:
        return EstadoTransferencia.CUENTA_BLOQUEADA
    if moneda not in MONEDAS_VALIDAS:
        return EstadoTransferencia.MONEDA_INVALIDA
    if canal not in CANALES_VALIDOS:
        return EstadoTransferencia.CANAL_INVALIDO
    if not cliente_vip and monto > LIMITE_COMUN:
        return EstadoTransferencia.SUPERA_LIMITE_COMUN
    if acumulado_diario + monto > limite_diario:
        return EstadoTransferencia.SUPERA_LIMITE_DIARIO
    return EstadoTransferencia.APROBADA


def procesar_transferencia(
    saldo: int,
    monto: int,
    cuenta_destino: str,
    moneda: str,
    canal: str,
    cliente_vip: bool,
    cuentas_bloqueadas: set[str],
    limite_diario: int,
    acumulado_diario: int,
    obtener_cotizacion,
    notificador: Notificador,
) -> EstadoTransferencia:
    estado = validar_transferencia(
        saldo,
        monto,
        cuenta_destino,
        moneda,
        canal,
        cliente_vip,
        cuentas_bloqueadas,
        limite_diario,
        acumulado_diario,
    )
    if estado is not EstadoTransferencia.APROBADA:
        return estado
    pesos = monto_en_pesos(monto, moneda, obtener_cotizacion)
    if pesos > saldo:
        return EstadoTransferencia.SALDO_INSUFICIENTE
    notificador.notificar(construir_mensaje(estado.value, cuenta_destino, pesos))
    return estado
