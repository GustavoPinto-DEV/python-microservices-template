"""
Email Sender - Email notification system

Utilities to send notifications via SMTP email.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

# Direct imports to avoid circular dependency
from repositorio_lib.core import log_performance
from repositorio_lib.config import email_settings, logger


def send_email(
    recipients: List[str],
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    sender: Optional[str] = None,
    timeout: int = 30,
) -> bool:
    """
    Send an email via SMTP.

    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        html_body: Email body in HTML format
        text_body: Email body in plain text (optional)
        sender: Sender email (defaults to settings.SMTP_USER)
        timeout: SMTP connection timeout in seconds (default: 30)

    Returns:
        bool: True if email was sent successfully
    """
    if not recipients:
        logger.warning("No recipients provided for email")
        return False

    if not email_settings.SMTP_HOST:
        logger.error("SMTP_HOST not configured")
        return False

    if not sender:
        sender = email_settings.SMTP_USER

    server = None
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        if text_body:
            part_text = MIMEText(text_body, "plain", "utf-8")
            msg.attach(part_text)

        part_html = MIMEText(html_body, "html", "utf-8")
        msg.attach(part_html)

        with log_performance(
            logger, f"SMTP send to {len(recipients)} recipients", threshold_ms=5000
        ):
            if email_settings.SMTP_USE_TLS:
                server = smtplib.SMTP(
                    email_settings.SMTP_HOST,
                    email_settings.SMTP_PORT_TLS,
                    timeout=timeout,
                )
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(
                    email_settings.SMTP_HOST,
                    email_settings.SMTP_PORT_SSL,
                    timeout=timeout,
                )

            if email_settings.SMTP_USER and email_settings.SMTP_PASSWORD:
                server.login(email_settings.SMTP_USER, email_settings.SMTP_PASSWORD)

            server.sendmail(sender, recipients, msg.as_string())

        logger.info(
            f"Email sent successfully - Subject: '{subject}', Recipients: {len(recipients)}"
        )
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}", exc_info=True)
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}", exc_info=True)
        return False
    finally:
        if server:
            try:
                server.quit()
            except Exception as e:
                logger.warning(f"Error closing SMTP connection: {e}")


def send_notification_email(
    notification_type: str,
    data: dict,
    recipients: Optional[List[str]] = None,
) -> bool:
    """
    Send a standardized notification email.

    Args:
        notification_type: Notification type ("validacion_incompleta", "error_ocr", "reporte_mensual")
        data: Dictionary with data for the template
        recipients: List of recipient emails (defaults to settings.EMAIL_OPERATIONS)

    Returns:
        bool: True if email was sent successfully
    """
    if recipients is None:
        recipients = [email_settings.EMAIL_OPERATIONS]

    templates = {
        "validacion_incompleta": {
            "subject": "AMCA OCR - Incomplete Validation",
            "template": """
                <html>
                <body>
                    <h2>Validación Incompleta - Requiere Revisión Manual</h2>
                    <p>Se ha detectado una hoja de pabellón con validación incompleta que requiere revisión manual.</p>
                    <h3>Detalles:</h3>
                    <ul>
                        <li><strong>Archivo:</strong> {archivo}</li>
                        <li><strong>Paciente RUT:</strong> {paciente_rut}</li>
                        <li><strong>Código AMCA:</strong> {codigo_amca}</li>
                        <li><strong>Estado:</strong> {estado}</li>
                        <li><strong>Fecha Procesamiento:</strong> {fecha}</li>
                    </ul>
                    <h3>Discrepancias:</h3>
                    <ul>
                        {discrepancias}
                    </ul>
                    <p>Por favor, revise el documento en el módulo web de revisión manual.</p>
                </body>
                </html>
            """,
        },
        "error_ocr": {
            "subject": "AMCA OCR - Processing Error",
            "template": """
                <html>
                <body>
                    <h2>Error en Procesamiento OCR</h2>
                    <p>Se ha producido un error al procesar un archivo con OCR.</p>
                    <h3>Detalles:</h3>
                    <ul>
                        <li><strong>Archivo:</strong> {archivo}</li>
                        <li><strong>Error:</strong> {error}</li>
                        <li><strong>Fecha:</strong> {fecha}</li>
                        <li><strong>Intentos:</strong> {intentos}</li>
                    </ul>
                    <p>El archivo requiere revisión manual.</p>
                </body>
                </html>
            """,
        },
        "reporte_mensual": {
            "subject": "AMCA OCR - Monthly Validation Report",
            "template": """
                <html>
                <body>
                    <h2>Reporte Mensual - Sistema AMCA OCR</h2>
                    <p>Resumen de validaciones del período {periodo}:</p>
                    <h3>Estadísticas:</h3>
                    <ul>
                        <li><strong>Total Archivos Procesados:</strong> {total_archivos}</li>
                        <li><strong>Validaciones Completas:</strong> {validaciones_completas} ({porcentaje_completas}%)</li>
                        <li><strong>Validaciones Incompletas:</strong> {validaciones_incompletas}</li>
                        <li><strong>No Encontrados:</strong> {no_encontrados}</li>
                        <li><strong>Errores:</strong> {errores}</li>
                    </ul>
                    <h3>Registros Pendientes de Revisión:</h3>
                    <p>{registros_pendientes}</p>
                    <p>Puede revisar el detalle completo en el sistema.</p>
                </body>
                </html>
            """,
        },
    }

    if notification_type not in templates:
        logger.error(f"Unknown notification type: {notification_type}")
        return False

    template_info = templates[notification_type]
    subject = template_info["subject"]

    try:
        html_body = template_info["template"].format(**data)
    except KeyError as e:
        logger.error(
            f"Missing required key in template data for '{notification_type}': {e}",
            exc_info=True,
        )
        return False
    except Exception as e:
        logger.error(
            f"Error formatting template for '{notification_type}': {e}",
            exc_info=True,
        )
        return False

    return send_email(
        recipients=recipients,
        subject=subject,
        html_body=html_body,
    )
