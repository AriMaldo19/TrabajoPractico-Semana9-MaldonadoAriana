"""Pruebas del procesador de transferencias.

Cada prueba sigue el patron AAA: Arrange, Act, Assert.
La cotizacion fija actua como Stub. El notificador se verifica como Mock.
"""

from unittest.mock import Mock

from calidad.procesador import (
    EstadoTransferencia,
    construir_mensaje,
    monto_en_pesos,
    procesar_transferencia,
    validar_transferencia,
)


def cotizacion_fija():
    return 1000


def datos_validos(**cambios):
    base = {
        "saldo": 500_000,
        "monto": 10_000,
        "cuenta_destino": "1234567890",
        "moneda": "ARS",
        "canal": "web",
        "cliente_vip": False,
        "cuentas_bloqueadas": set(),
        "limite_diario": 300_000,
        "acumulado_diario": 0,
    }
    base.update(cambios)
    return base


def test_monto_invalido_cuando_no_es_entero_positivo():
    # Arrange
    datos = datos_validos(monto=0)

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.MONTO_INVALIDO


def test_monto_bool_no_cuenta_como_entero_valido():
    # Arrange
    datos = datos_validos(monto=True)

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.MONTO_INVALIDO


def test_saldo_invalido_cuando_es_negativo():
    # Arrange
    datos = datos_validos(saldo=-1)

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.SALDO_INVALIDO


def test_saldo_insuficiente():
    # Arrange
    datos = datos_validos(saldo=100, monto=150)

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.SALDO_INSUFICIENTE


def test_cuenta_invalida_cuando_no_tiene_diez_digitos():
    # Arrange
    datos = datos_validos(cuenta_destino="123")

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.CUENTA_INVALIDA


def test_cuenta_bloqueada():
    # Arrange
    datos = datos_validos(cuentas_bloqueadas={"1234567890"})

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.CUENTA_BLOQUEADA


def test_moneda_invalida():
    # Arrange
    datos = datos_validos(moneda="EUR")

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.MONEDA_INVALIDA


def test_canal_invalido():
    # Arrange
    datos = datos_validos(canal="telefono")

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.CANAL_INVALIDO


def test_supera_limite_comun_si_no_es_vip():
    # Arrange
    datos = datos_validos(monto=200_001, saldo=500_000, cliente_vip=False)

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.SUPERA_LIMITE_COMUN


def test_vip_puede_superar_el_limite_comun():
    # Arrange
    datos = datos_validos(monto=200_001, saldo=500_000, cliente_vip=True)

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.APROBADA


def test_supera_limite_diario():
    # Arrange
    datos = datos_validos(monto=10_000, acumulado_diario=295_000, limite_diario=300_000)

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.SUPERA_LIMITE_DIARIO


def test_transferencia_valida_en_pesos():
    # Arrange
    datos = datos_validos()

    # Act
    estado = validar_transferencia(**datos)

    # Assert
    assert estado is EstadoTransferencia.APROBADA


def test_mensaje_reune_los_datos_en_un_solo_formato():
    # Arrange
    estado = "aprobada"
    cuenta = "1234567890"
    monto = 10_000

    # Act
    mensaje = construir_mensaje(estado, cuenta, monto)

    # Assert
    assert mensaje == (
        "TRANSFERENCIA | estado=aprobada | cuenta=1234567890 | "
        "monto=10000 | canal=web | origen=procesador"
    )


def test_monto_en_pesos_no_consulta_cotizacion():
    # Arrange
    obtener_cotizacion = Mock(return_value=1000)

    # Act
    pesos = monto_en_pesos(10_000, "ARS", obtener_cotizacion)

    # Assert
    assert pesos == 10_000
    obtener_cotizacion.assert_not_called()


def test_monto_en_dolares_usa_la_cotizacion_fija():
    # Arrange
    obtener_cotizacion = cotizacion_fija

    # Act
    pesos = monto_en_pesos(10, "USD", obtener_cotizacion)

    # Assert
    assert pesos == 10_000


def test_monto_en_moneda_desconocida_falla():
    # Arrange
    obtener_cotizacion = cotizacion_fija

    # Act / Assert
    try:
        monto_en_pesos(10, "EUR", obtener_cotizacion)
    except ValueError as error:
        assert str(error) == "moneda_invalida"
    else:
        raise AssertionError("Se esperaba ValueError")


def test_procesar_aprobada_en_pesos_notifica_una_vez():
    # Arrange
    notificador = Mock()
    obtener_cotizacion = Mock(return_value=1000)

    # Act
    estado = procesar_transferencia(
        **datos_validos(),
        obtener_cotizacion=obtener_cotizacion,
        notificador=notificador,
    )

    # Assert
    assert estado is EstadoTransferencia.APROBADA
    notificador.notificar.assert_called_once_with(
        "TRANSFERENCIA | estado=aprobada | cuenta=1234567890 | "
        "monto=10000 | canal=web | origen=procesador"
    )
    obtener_cotizacion.assert_not_called()


def test_procesar_rechazada_no_notifica():
    # Arrange
    notificador = Mock()

    # Act
    estado = procesar_transferencia(
        **datos_validos(monto=0),
        obtener_cotizacion=cotizacion_fija,
        notificador=notificador,
    )

    # Assert
    assert estado is EstadoTransferencia.MONTO_INVALIDO
    notificador.notificar.assert_not_called()


def test_procesar_dolares_rechaza_si_los_pesos_superan_el_saldo():
    # Arrange
    notificador = Mock()

    # Act
    estado = procesar_transferencia(
        **datos_validos(monto=10, moneda="USD", saldo=5_000),
        obtener_cotizacion=cotizacion_fija,
        notificador=notificador,
    )

    # Assert
    assert estado is EstadoTransferencia.SALDO_INSUFICIENTE
    notificador.notificar.assert_not_called()


def test_procesar_dolares_aprobada_notifica_el_monto_en_pesos():
    # Arrange
    notificador = Mock()

    # Act
    estado = procesar_transferencia(
        **datos_validos(monto=10, moneda="USD", saldo=20_000),
        obtener_cotizacion=cotizacion_fija,
        notificador=notificador,
    )

    # Assert
    assert estado is EstadoTransferencia.APROBADA
    notificador.notificar.assert_called_once()
    mensaje = notificador.notificar.call_args.args[0]
    assert "monto=10000" in mensaje
