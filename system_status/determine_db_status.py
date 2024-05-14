"""Helper functions to determine the status of the database based on the results of notification statuses"""

STATUS_DEFINITION = {
    "high": {
        "all": {
            "up": set(["delivered", "sent", "sending"]),
            "down": set(
                [
                    "created",
                    "permanent-failure",
                    "technical-failure",
                    "temporary-failure",
                ]
            ),
        }
    },
    "medium": {
        "group1": {
            "up": set(["sent", "delivered", "sending"]),
            "down": set(
                [
                    "created",
                    "permanent-failure",
                    "technical-failure",
                    "temporary-failure",
                ]
            ),
        },
        "group2": {
            "up": set(["sending", "sent", "delivered"]),
            "down": set(
                [
                    "created",
                    "permanent-failure",
                    "technical-failure",
                    "temporary-failure",
                ]
            ),
        },
    },
    "low": {
        "group1": {
            "up": set(["sent", "delivered", "sending"]),
            "down": set(
                [
                    "created",
                    "permanent-failure",
                    "technical-failure",
                    "temporary-failure",
                ]
            ),
        },
        "group2": {
            "up": set(["sending", "sent", "delivered"]),
            "down": set(
                [
                    "created",
                    "permanent-failure",
                    "technical-failure",
                    "temporary-failure",
                ]
            ),
        },
    },
}


def determine_high_status(priority_result):
    success = STATUS_DEFINITION["high"]["all"]["up"]
    failure = STATUS_DEFINITION["high"]["all"]["down"]

    if not priority_result:
        return "down"
    if priority_result.issubset(success):
        return "up"
    if priority_result.issubset(failure):
        return "down"
    return "degraded"


def determine_medium_status(medium_result1, medium_result2):
    success_group1 = STATUS_DEFINITION["medium"]["group1"]["up"]
    failure_group1 = STATUS_DEFINITION["medium"]["group1"]["down"]
    success_group2 = STATUS_DEFINITION["medium"]["group2"]["up"]
    failure_group2 = STATUS_DEFINITION["medium"]["group2"]["down"]

    if not medium_result1 or not medium_result2:
        return "down"

    if (medium_result1.issubset(success_group1)) or (
        medium_result2.issubset(success_group2)
    ):
        return "up"
    if (medium_result1.issubset(failure_group1)) and (
        medium_result2.issubset(failure_group2)
    ):
        return "down"
    return "degraded"


def determine_low_status(low_result1, low_result2):
    success_group1 = STATUS_DEFINITION["low"]["group1"]["up"]
    failure_group1 = STATUS_DEFINITION["low"]["group1"]["down"]
    success_group2 = STATUS_DEFINITION["low"]["group2"]["up"]
    failure_group2 = STATUS_DEFINITION["low"]["group2"]["down"]

    if not low_result1 or not low_result2:
        return "down"

    if (low_result1.issubset(success_group1)) or (low_result2.issubset(success_group2)):
        return "up"

    if (low_result1.issubset(failure_group1)) and (
        low_result2.issubset(failure_group2)
    ):
        return "down"
    return "degraded"


def determine_status(
    priroity_result, medium_result1, medium_result2, low_result1, low_result2
):
    high_status = determine_high_status(priroity_result)
    medium_status = determine_medium_status(medium_result1, medium_result2)
    low_status = determine_low_status(low_result1, low_result2)
    if high_status == "down" or medium_status == "down" or low_status == "down":
        return "down"
    if (
        high_status == "degraded"
        or medium_status == "degraded"
        or low_status == "degraded"
    ):
        return "degraded"
    return "up"
