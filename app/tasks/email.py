import logging

logger = logging.getLogger(__name__)


def send_welcome_email(email: str, username: str) -> None:
    """Эмуляция отправки приветственного email (просто логируем)."""
    logger.info(f"📧 Отправляю приветственный email на {email} для пользователя {username}")
    # В реальном проекте здесь был бы вызов SMTP-сервера или API почтового сервиса