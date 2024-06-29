import datetime

from bupa import UserInfo

user = UserInfo(
    hapID="123456",
    email="test@example.com",
    firstName="John",
    surname="Doe",
    dob="23/07/1999",
)


def on_earliest_appointment_found(earliest_appointment: datetime.datetime):
    msg = f"Earliest appointment found: {earliest_appointment}"
    # Telegram bot example
    # requests.post(
    #     "https://api.telegram.org/bot<token>/sendMessage",
    #     data={"chat_id": "<chat_id>", "text": msg},
    # )
