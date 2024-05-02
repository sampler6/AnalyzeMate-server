from config import FCM_KEY
from pyfcm import FCMNotification


class FCMManager:
    def __init__(self) -> None:
        self.app = FCMNotification(api_key=f"{FCM_KEY}")

    def send_notifications(self, registrations_tokens: list[str], title: str, body: str) -> None:
        self.app.notify_multiple_devices(registrations_tokens, message_title=title, message_body=body)


manager = FCMManager()
