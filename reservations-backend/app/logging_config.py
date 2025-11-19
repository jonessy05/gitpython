"""
Logging Konfiguration für Reservierungen API mit JSON-Format
Follows Elastic Common Schema (ECS) principles for structured logging
"""
import logging
import os
import json
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import Optional

# Logging Level aus Umgebungsvariable (Default: INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json").lower()  # json or text

# Erstelle Logger
logger = logging.getLogger("reservations_api")
logger.setLevel(getattr(logging, LOG_LEVEL))


class JSONFormatter(logging.Formatter):
    """
    JSON Formatter für strukturierte Logs nach ECS-Prinzipien
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "log.level": record.levelname,
            "log.logger": record.name,
            "message": record.getMessage(),
            "ecs.version": "1.12.0"
        }

        # Add extra fields for audit logging
        if hasattr(record, "operation"):
            log_data["event.action"] = getattr(record, "operation", None)
        if hasattr(record, "user_id"):
            log_data["user.id"] = getattr(record, "user_id", None)
        if hasattr(record, "object_type"):
            log_data["labels.object_type"] = getattr(record, "object_type", None)
        if hasattr(record, "object_id"):
            log_data["labels.object_id"] = getattr(record, "object_id", None)

        # Add source location for debugging
        if LOG_LEVEL == "DEBUG":
            log_data["log.origin"] = {
                "file.name": record.filename,
                "file.line": record.lineno,
                "function": record.funcName
            }

        # Add exception info if present
        if record.exc_info:
            log_data["error.type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
            log_data["error.message"] = str(record.exc_info[1]) if record.exc_info[1] else None
            log_data["error.stack_trace"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """
    Text Formatter für lesbare Logs (development)
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as human-readable text"""
        timestamp = datetime.now(timezone.utc).isoformat()
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


# Handler: Konsole (stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, LOG_LEVEL))

# Handler: Datei (mit Rotation) - nur wenn LOG_FILE gesetzt
log_file = os.getenv("LOG_FILE", None)
if log_file:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10_000_000,  # 10 MB
        backupCount=5  # Keep 5 backup files
    )
    file_handler.setLevel(logging.DEBUG)  # Datei speichert alles
    file_handler.setFormatter(JSONFormatter() if LOG_FORMAT == "json" else TextFormatter())
    logger.addHandler(file_handler)

# Setze Formatter basierend auf Konfiguration
if LOG_FORMAT == "json":
    console_handler.setFormatter(JSONFormatter())
else:
    console_handler.setFormatter(TextFormatter())

# Füge Console Handler zu Logger hinzu
logger.addHandler(console_handler)

# Verhindere doppelte Logs
logger.propagate = False

logger.info("Logger initialized", extra={
    "operation": "INIT",
    "user_id": "system",
    "object_type": "logger",
    "object_id": "reservations_api"
})


def log_operation(
    operation: str,
    user_id: str,
    object_type: str,
    object_id: str,
    message: Optional[str] = None,
    level: str = "INFO"
):
    """
    Logging Helper für Audit-Logs

    Args:
        operation: CREATE, READ, UPDATE, DELETE
        user_id: Benutzer-ID aus JWT Token
        object_type: z.B. 'reservation'
        object_id: z.B. '123' or UUID
        message: Optional zusätzliche Nachricht
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    msg = message or f"Operation {operation} on {object_type}"
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logger.log(log_level, msg, extra={
        "operation": operation,
        "user_id": user_id,
        "object_type": object_type,
        "object_id": object_id
    })

