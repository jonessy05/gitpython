"""
Logging Konfiguration für Reservierungen API
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Logging Level aus Umgebungsvariable (Default: INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Erstelle Logger
logger = logging.getLogger("reservations_api")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Handler: Konsole (stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL))

# Handler: Datei (mit Rotation)
log_file = "logs/reservations_api.log"
os.makedirs("logs", exist_ok=True)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10_000_000,  # 10 MB
    backupCount=5  # Keep 5 backup files
)
file_handler.setLevel(logging.DEBUG)  # Datei speichert alles

# Format: [TIMESTAMP] [LEVEL] [LOGGER] [OPERATION] [USER] [OBJECT] [ID] - MESSAGE
class AuditFormatter(logging.Formatter):
    """Custom Formatter für Audit-Logs"""

    def format(self, record):
        # Standardformat
        timestamp = datetime.utcnow().isoformat()
        level = record.levelname

        # Extra Attribute für Audit-Logs
        operation = getattr(record, "operation", "-")
        user_id = getattr(record, "user_id", "-")
        object_type = getattr(record, "object_type", "-")
        object_id = getattr(record, "object_id", "-")

        audit_string = (
            f"[{timestamp}] [{level}] "
            f"[operation:{operation}] [user:{user_id}] "
            f"[object:{object_type}] [id:{object_id}] "
            f"- {record.getMessage()}"
        )
        return audit_string


# Setze Custom Formatter
formatter = AuditFormatter()
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Füge Handler zu Logger hinzu
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("Logger initialized", extra={
    "operation": "INIT",
    "user_id": "system",
    "object_type": "logger",
    "object_id": "reservations_api"
})


def log_operation(operation: str, user_id: str, object_type: str, object_id: str, message: str = None):
    """
    Logging Helper für Audit-Logs

    Args:
        operation: CREATE, READ, UPDATE, DELETE
        user_id: Benutzer-ID aus JWT Token
        object_type: z.B. 'reservation'
        object_id: z.B. '123' oder 'N/A'
        message: Optional zusätzliche Nachricht
    """
    msg = message or f"Operation {operation} on {object_type}"
    logger.info(msg, extra={
        "operation": operation,
        "user_id": user_id,
        "object_type": object_type,
        "object_id": object_id
    })
