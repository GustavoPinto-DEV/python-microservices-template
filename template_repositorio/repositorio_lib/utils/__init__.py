"""Utility functions - Shared utilities across all services"""

# date_utils
from .date_utils import (
    parse_flexible_date,
    parse_flexible_time,
    calcular_edad,
    validar_coherencia_fecha_edad,
    validar_fecha_razonable,
)

# email_sender
from .email_sender import send_notification_email, send_email

# retry
from .retry import (
    retry_with_exponential_backoff,
    retry_async,
    retry_until_success,
    retry_sync_until_success,
)

# rut_utils
from .rut_utils import (
    validar_rut,
    limpiar_rut,
    formatear_rut_con_puntos,
    formatear_rut_sin_puntos,
    formatear_rut_completo,
    separar_rut,
    extraer_numero_rut,
    extraer_digito_verificador,
    validar_rut_con_detalles,
    normalizar_rut_lista,
    es_rut_empresa,
)


__all__ = [
    # date_utils
    "parse_flexible_date",
    "parse_flexible_time",
    "calcular_edad",
    "validar_coherencia_fecha_edad",
    "validar_fecha_razonable",
    # email_sender
    "send_notification_email",
    "send_email",
    # retry
    "retry_with_exponential_backoff",
    "retry_async",
    "retry_until_success",
    "retry_sync_until_success",
    # rut_utils
    "validar_rut",
    "limpiar_rut",
    "formatear_rut_con_puntos",
    "formatear_rut_sin_puntos",
    "formatear_rut_completo",
    "separar_rut",
    "extraer_numero_rut",
    "extraer_digito_verificador",
    "validar_rut_con_detalles",
    "normalizar_rut_lista",
    "es_rut_empresa",
]
