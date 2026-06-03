import importlib
import sys


MODULE_NAME = "file_scan_verdict_callbacks"


def _load_module(monkeypatch):
    monkeypatch.setenv("SCAN_CALLBACK_SECRET", "test-secret")
    monkeypatch.setenv("NOTIFY_API_URL", "https://notify.example.com")

    if MODULE_NAME in sys.modules:
        return importlib.reload(sys.modules[MODULE_NAME])

    return importlib.import_module(MODULE_NAME)


# Based on the payload described in docs:
# https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings_eventbridge.html#guardduty_findings_eventbridge_format
def _guardduty_event(scan_status, scan_result_status, object_key):
    return {
        "detail": {
            "schemaVersion": "1.0",
            "scanStatus": scan_status,
            "resourceType": "S3_OBJECT",
            "s3ObjectDetails": {
                "bucketName": "amzn-s3-demo-bucket",
                "objectKey": object_key,
                "eTag": "etag-value",
                "versionId": "version-id",
                "s3Throttled": False,
            },
            "scanResultDetails": {
                "scanResultStatus": scan_result_status,
                "threats": None,
                "statusReasons": None,
            },
        }
    }


class _Response:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        return None


def test_lambda_handler_parses_no_threats_payload(monkeypatch):
    module = _load_module(monkeypatch)
    service_id = "11111111-1111-1111-1111-111111111111"
    file_id = "22222222-2222-2222-2222-222222222222"
    object_key = f"template/{service_id}/{file_id}"
    event = _guardduty_event("COMPLETED", "NO_THREATS_FOUND", object_key)

    captured = {}

    def _fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _Response(status_code=200)

    monkeypatch.setattr(module.requests, "post", _fake_post)

    result = module.lambda_handler(event, None)

    assert result == {"status": "ok", "file_id": file_id, "new_status": "uploaded"}
    assert (
        captured["url"]
        == f"https://notify.example.com/service/{service_id}/files/{file_id}/status"
    )
    assert captured["json"] == {"status": "uploaded"}
    assert captured["headers"]["Authorization"] == "Bearer test-secret"
    assert captured["timeout"] == 10


def test_lambda_handler_parses_threats_found_payload(monkeypatch):
    module = _load_module(monkeypatch)
    service_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    file_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    object_key = f"template/{service_id}/{file_id}"
    event = _guardduty_event("COMPLETED", "THREATS_FOUND", object_key)

    captured = {}

    def _fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _Response(status_code=200)

    monkeypatch.setattr(module.requests, "post", _fake_post)

    result = module.lambda_handler(event, None)

    assert result == {
        "status": "ok",
        "file_id": file_id,
        "new_status": "virus_scan_failed",
    }
    assert (
        captured["url"]
        == f"https://notify.example.com/service/{service_id}/files/{file_id}/status"
    )
    assert captured["json"] == {"status": "virus_scan_failed"}


def test_lambda_handler_skips_non_completed_scan(monkeypatch):
    module = _load_module(monkeypatch)
    event = _guardduty_event(
        "SKIPPED",
        "UNSUPPORTED",
        "template/11111111-1111-1111-1111-111111111111/22222222-2222-2222-2222-222222222222",
    )

    def _unexpected_post(*args, **kwargs):
        raise AssertionError(
            "requests.post should not be called when scanStatus != COMPLETED"
        )

    monkeypatch.setattr(module.requests, "post", _unexpected_post)

    result = module.lambda_handler(event, None)

    assert result == {"status": "skipped", "reason": "scan_not_completed"}


def test_lambda_handler_skips_unparseable_object_key(monkeypatch):
    module = _load_module(monkeypatch)
    event = _guardduty_event("COMPLETED", "NO_THREATS_FOUND", "not/a/valid/key")

    def _unexpected_post(*args, **kwargs):
        raise AssertionError("requests.post should not be called for unparseable key")

    monkeypatch.setattr(module.requests, "post", _unexpected_post)

    result = module.lambda_handler(event, None)

    assert result == {"status": "skipped", "reason": "unparseable_key"}
