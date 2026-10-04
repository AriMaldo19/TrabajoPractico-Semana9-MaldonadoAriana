"""Copia del armado de mensajes del codigo inicial."""


def registrar_rechazo(motivo, cuenta, monto):
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
