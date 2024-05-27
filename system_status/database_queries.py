import logging
import sqlalchemy

from datetime import datetime, timedelta

# Heartbeat Templates
TEMPLATES = {
    "email": {
        "low": "73079cb9-c169-44ea-8cf4-8d397711cc9d",
        "medium": "c75c4539-3014-4c4c-96b5-94d326758a74",
        "high": "276da251-3103-49f3-9054-cbf6b5d74411",
    },
    "sms": {
        "low": "ab3a603b-d602-46ea-8c83-e05cb280b950",
        "medium": "a48b54ce-40f6-4e4a-abe8-1e2fa389455b",
        "high": "4969a9e9-ddfd-476e-8b93-6231e6f1be4a",
    },
}

TIMING = {
    "high": {
        "all": {
            "timing": datetime.now() - timedelta(seconds=60),
        }
    },
    "medium": {
        "group1": {
            "timing": [
                datetime.now() - timedelta(minutes=52),
                datetime.now() - timedelta(minutes=47),
            ],
        },
        "group2": {
            "timing": [
                datetime.now() - timedelta(minutes=42),
                datetime.now() - timedelta(minutes=37),
            ],
        },
    },
    "low": {
        "group1": {
            "timing": [
                datetime.now() - timedelta(hours=3, minutes=7),
                datetime.now() - timedelta(hours=3, minutes=2),
            ],
        },
        "group2": {
            "timing": [
                datetime.now() - timedelta(minutes=20),
                datetime.now() - timedelta(minutes=15),
            ],
        },
    },
}


def build_sql_query(template_ids: list, created_at_min, created_at_max=None) -> str:
    template_ids_str = ", ".join(f"'{str(item)}'" for item in template_ids)
    sql = f"""
        SELECT
            n.template_id, array_agg(DISTINCT(n.notification_status))
        FROM
            notifications n
        WHERE
            n.template_id in ({template_ids_str})
            AND n.created_at >= '{created_at_min}'
    """

    if created_at_max:
        sql = f"{sql} AND n.created_at <= '{created_at_max}'"

    sql += """
        GROUP BY
            n.template_id
    """
    return sql


def formatted_result(result, email_template_id, sms_template_id):
    final = {}
    for template_id, status in result:
        if str(template_id) == email_template_id:
            final["email"] = {"template_id": str(template_id), "status": set(status)}
        if str(template_id) == sms_template_id:
            final["sms"] = {"template_id": str(template_id), "status": set(status)}
    return final


def high_template_result(connection):
    """
    Data from the database: is in the format: [(UUID('xx'), ['delivered']), (UUID('xx'), ['delivered'])]
    """
    sql = build_sql_query(
        (TEMPLATES["email"]["high"], TEMPLATES["sms"]["high"]),
        TIMING["high"]["all"]["timing"],
    )
    result = connection.execute(sqlalchemy.sql.text(sql)).fetchall()
    return formatted_result(
        result, TEMPLATES["email"]["high"], TEMPLATES["sms"]["high"]
    )


def medium_template_result_group1(connection):
    sql = build_sql_query(
        (TEMPLATES["email"]["medium"], TEMPLATES["sms"]["medium"]),
        TIMING["medium"]["group1"]["timing"][0],
        TIMING["medium"]["group1"]["timing"][1],
    )
    result = connection.execute(sqlalchemy.sql.text(sql)).fetchall()
    return formatted_result(
        result, TEMPLATES["email"]["medium"], TEMPLATES["sms"]["medium"]
    )


def medium_template_result_group2(connection):
    sql = build_sql_query(
        (TEMPLATES["email"]["medium"], TEMPLATES["sms"]["medium"]),
        TIMING["medium"]["group2"]["timing"][0],
        TIMING["medium"]["group2"]["timing"][1],
    )
    result = connection.execute(sqlalchemy.sql.text(sql)).fetchall()
    return formatted_result(
        result, TEMPLATES["email"]["medium"], TEMPLATES["sms"]["medium"]
    )


def low_template_result_group1(connection):
    sql = build_sql_query(
        (TEMPLATES["email"]["low"], TEMPLATES["sms"]["low"]),
        TIMING["low"]["group1"]["timing"][0],
        TIMING["low"]["group1"]["timing"][1],
    )
    result = connection.execute(sqlalchemy.sql.text(sql)).fetchall()
    return formatted_result(result, TEMPLATES["email"]["low"], TEMPLATES["sms"]["low"])


def low_template_result_group2(connection):
    sql = build_sql_query(
        (TEMPLATES["email"]["low"], TEMPLATES["sms"]["low"]),
        TIMING["low"]["group2"]["timing"][0],
        TIMING["low"]["group2"]["timing"][1],
    )
    result = connection.execute(sqlalchemy.sql.text(sql)).fetchall()
    return formatted_result(result, TEMPLATES["email"]["low"], TEMPLATES["sms"]["low"])
