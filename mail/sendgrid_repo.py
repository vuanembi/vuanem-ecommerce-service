import os

import requests

FROM_EMAIL = "bi@vuanem.com"


def send_email(to: list[str], subject: str, content: list[dict[str, str]]):
    requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {os.getenv('SENDGRID_API_KEY')}",
            "Content-type": "application/json",
        },
        json={
            "personalizations": [{"to": [{"email": email} for email in to]}],
            "from": {"email": FROM_EMAIL},
            "subject": subject,
            "content": content,
        },
    )
