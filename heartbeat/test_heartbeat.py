import uuid
import pytest
from collections import Counter
from notifications_python_client.base import BaseAPIClient
from notifications_python_client.notifications import NotificationsAPIClient


@pytest.mark.parametrize(
    "templates, expected, errors",
    [
        (  # No missing variables
            {
                "email": {
                    "low": "9c59513f-91c5-4366-93fc-d8a84e6f6381",
                    "medium": "ee58ceff-633a-4302-a271-e757ceb827f6",
                    "high": "61d5c3d6-f293-4ce7-a344-c52c47a2879e",
                },
                "sms": {
                    "low": "fbdd470f-0330-4675-886a-4980be10be9d",
                    "medium": "cc3cd2c0-482e-4415-be94-87344d1dad77",
                    "high": "140ef5be-dcc1-454b-805b-9b6c450e30ec",
                },
            },
            {
                "email": {
                    "msg": "Email has been sent by url1!",
                    "count": 3,
                },
                "sms": {
                    "msg": "SMS has been sent by url1!",
                    "count": 3,
                },
            },
            {
                "err_msg": "",
                "count": 0,
            },
        ),
        (  # Low missing
            {
                "email": {
                    "low": "",
                    "medium": "ee58ceff-633a-4302-a271-e757ceb827f6",
                    "high": "61d5c3d6-f293-4ce7-a344-c52c47a2879e",
                },
                "sms": {
                    "low": "",
                    "medium": "cc3cd2c0-482e-4415-be94-87344d1dad77",
                    "high": "140ef5be-dcc1-454b-805b-9b6c450e30ec",
                },
            },
            {
                "email": {
                    "msg": "Email has been sent by url1!",
                    "count": 2,
                },
                "sms": {
                    "msg": "SMS has been sent by url1!",
                    "count": 2,
                },
            },
            {
                "err_msg": "Required parameters missing: template_type: {}, priority: {}, template_id: {}",
                "count": 2,
            },
        ),
        (  # Medium missing
            {
                "email": {
                    "low": "9c59513f-91c5-4366-93fc-d8a84e6f6381",
                    "medium": "",
                    "high": "61d5c3d6-f293-4ce7-a344-c52c47a2879e",
                },
                "sms": {
                    "low": "fbdd470f-0330-4675-886a-4980be10be9d",
                    "medium": "",
                    "high": "140ef5be-dcc1-454b-805b-9b6c450e30ec",
                },
            },
            {
                "email": {
                    "msg": "Email has been sent by url1!",
                    "count": 2,
                },
                "sms": {
                    "msg": "SMS has been sent by url1!",
                    "count": 2,
                },
            },
            {
                "err_msg": "Required parameters missing: template_type: {}, priority: {}, template_id: {}",
                "count": 2,
            },
        ),
        (  # High missing
            {
                "email": {
                    "low": "9c59513f-91c5-4366-93fc-d8a84e6f6381",
                    "medium": "ee58ceff-633a-4302-a271-e757ceb827f6",
                    "high": "",
                },
                "sms": {
                    "low": "fbdd470f-0330-4675-886a-4980be10be9d",
                    "medium": "cc3cd2c0-482e-4415-be94-87344d1dad77",
                    "high": "",
                },
            },
            {
                "email": {
                    "msg": "Email has been sent by url1!",
                    "count": 2,
                },
                "sms": {
                    "msg": "SMS has been sent by url1!",
                    "count": 2,
                },
            },
            {
                "err_msg": "Required parameters missing: template_type: {}, priority: {}, template_id: {}",
                "count": 2,
            },
        ),
        (  # Low and High missing
            {
                "email": {
                    "low": "",
                    "medium": "ee58ceff-633a-4302-a271-e757ceb827f6",
                    "high": "",
                },
                "sms": {
                    "low": "",
                    "medium": "cc3cd2c0-482e-4415-be94-87344d1dad77",
                    "high": "",
                },
            },
            {
                "email": {
                    "msg": "Email has been sent by url1!",
                    "count": 1,
                },
                "sms": {
                    "msg": "SMS has been sent by url1!",
                    "count": 1,
                },
            },
            {
                "err_msg": "Required parameters missing: template_type: {}, priority: {}, template_id: {}",
                "count": 4,
            },
        ),
        (  # Everything is wrong, send help.
            {
                "email": {
                    "low": "",
                    "medium": "",
                    "high": "",
                },
                "sms": {
                    "low": "",
                    "medium": "",
                    "high": "",
                },
            },
            {
                "email": {
                    "msg": "Email has been sent by url1!",
                    "count": 0,
                },
                "sms": {
                    "msg": "SMS has been sent by url1!",
                    "count": 0,
                },
            },
            {
                "err_msg": "Required parameters missing: template_type: {}, priority: {}, template_id: {}",
                "count": 6,
            },
        ),
    ],
)
def test_handler_template_id_presence(
    monkeypatch, mocker, capsys, templates, expected, errors
):
    monkeypatch.setenv(
        "heartbeat_api_key", f"ApiKey-v1 gcntfy-someKey-{uuid.uuid4()}-{uuid.uuid4()}"
    )
    monkeypatch.setenv("heartbeat_base_url", '["url1"]')
    import heartbeat

    mocker.patch.dict(
        "notifications_utils.system_status.TEMPLATES", templates, clear=True
    )

    email_mocked = mocker.patch(
        "notifications_python_client.notifications.NotificationsAPIClient.send_email_notification"
    )
    sms_mocked = mocker.patch(
        "notifications_python_client.notifications.NotificationsAPIClient.send_sms_notification"
    )

    heartbeat.handler("", "")

    msg_counts = Counter(capsys.readouterr().out.split("\n"))
    assert email_mocked.call_count == expected["email"]["count"]
    assert sms_mocked.call_count == expected["sms"]["count"]

    assert msg_counts[expected["sms"]["msg"]] == expected["sms"]["count"]
    assert msg_counts[expected["email"]["msg"]] == expected["email"]["count"]
