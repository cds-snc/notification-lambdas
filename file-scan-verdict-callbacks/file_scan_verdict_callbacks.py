import json
import os
import re
import time

import boto3
import requests

SCAN_CALLBACK_SECRET = os.environ["SCAN_CALLBACK_SECRET"]
NOTIFY_API_BASE_URL = os.environ["NOTIFY_API_URL"]

# Object key pattern: template/<service_id>/<document_id>
KEY_RE = re.compile(
    r"^template/(?P<service_id>[0-9a-f-]{36})/(?P<document_id>[0-9a-f-]{36})$"
)

STATUS_MAP = {
    "NO_THREATS_FOUND": "uploaded",
    "THREATS_FOUND": "virus_scan_failed",
    # Leave scan errors terminal so UI can show failure rather than spin forever
    "UNSUPPORTED": "virus_scan_failed",
    "ACCESS_DENIED": "virus_scan_failed",
    "FAILED": "virus_scan_failed",
}


def lambda_handler(event, context):
    detail = event["detail"]
    scan_status = detail.get("scanStatus")
    scan_result = detail.get("scanResultDetails", {}).get("scanResultStatus")
    object_key = detail["s3ObjectDetails"]["objectKey"]
    bucket_name = detail["s3ObjectDetails"]["bucketName"]

    print(
        f"Scan result: bucket={bucket_name} key={object_key} "
        f"scanStatus={scan_status} scanResult={scan_result}"
    )

    if scan_status != "COMPLETED":
        print(f"Scan not completed (status={scan_status}), skipping.")
        return {"status": "skipped", "reason": "scan_not_completed"}

    m = KEY_RE.match(object_key)
    if not m:
        print(f"Cannot parse service_id/document_id from key: {object_key}")
        return {"status": "skipped", "reason": "unparseable_key"}

    service_id = m.group("service_id")
    file_id = m.group("document_id")
    new_status = STATUS_MAP.get(scan_result, "virus_scan_failed")

    url = f"{NOTIFY_API_BASE_URL}/service/{service_id}/files/{file_id}/status"
    headers = {
        "Authorization": f"Bearer {SCAN_CALLBACK_SECRET}",
        "Content-Type": "application/json",
    }
    payload = {"status": new_status}

    resp = requests.post(url, json=payload, headers=headers, timeout=10)

    if resp.status_code == 200:
        print(f"Updated file {file_id} to status={new_status}")
        return {"status": "ok", "file_id": file_id, "new_status": new_status}

    print(f"API returned {resp.status_code}: {resp.text}")
    resp.raise_for_status()  # triggers Lambda retry / DLQ
