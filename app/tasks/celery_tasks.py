from app.core.celery_app import celery
from app.tasks.email import send_welcome_email


@celery.task(name="send_welcome_email_task")
def send_welcome_email_task(email: str, username: str) -> None:
    send_welcome_email(email, username)