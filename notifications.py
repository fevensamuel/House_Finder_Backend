import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FCM_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)

def send_push_notification(user, title, body, data=None):
    if not user.fcm_token:
        print(f"No FCM token for {user.email}")
        return None
    initialize_firebase()
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user.fcm_token,
        data=data or {},
    )
    try:
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Push failed: {e}")
        return None