import pytest

from system_status.determine_db_status import (
    determine_high_status,
    determine_low_status,
    determine_medium_status,
    determine_status,
)

x = {
    "email": {
        "high": {"delivered"},
        "medium1": {"delivered"},
        "medium2": {"delivered"},
        "low1": {"delivered"},
        "low2": {"delivered"},
    },
    "sms": {
        "high": {"delivered"},
        "medium1": {"delivered"},
        "medium2": {"delivered"},
        "low1": {"delivered"},
        "low2": {"delivered"},
    },
}


class TestHighStatus:

    @pytest.mark.parametrize(
        "status, expected_result",
        [
            (set(["delivered"]), "up"),
            (set(["delivered", "sent"]), "up"),
            (set(["delivered", "created"]), "degraded"),
            (set(["temporary-failure", "created"]), "down"),
            (set(["delivered", "sent", "created"]), "degraded"),
            (set(["permanent-failure", "created"]), "down"),
            (
                set(["permanent-failure", "technical-failure", "temporary-failure"]),
                "down",
            ),
            (set(["created"]), "down"),
            (set([]), "down"),
        ],
    )
    def test_high_status(self, status, expected_result):
        assert determine_high_status(status) == expected_result


class TestMediumStatus:

    #  x =    "medium": {
    #         "group1": {
    #             "up": set(["sent", "delivered"]),
    #             "down": set(["created", "permanent-failure", "technical-failure", "temporary-failure"]),
    #         },
    #         "group2": {
    #             "up": set(["sending", "sent", "delivered"]),
    #             "down": set(["created", "permanent-failure", "technical-failure", "temporary-failure"]),
    #         },
    #     },

    @pytest.mark.parametrize(
        "mediumstat1, mediumstat2, expected_result",
        [
            # UP
            (
                set(["sent", "delivered"]),
                set(["sending", "created", "delivered"]),
                "up",
            ),
            (set(["created"]), set(["delivered"]), "up"),
            (set(["sent", "delivered"]), set(["temporary-failure"]), "up"),
            # DEGRADED
            (
                set(["sent", "delivered", "created"]),
                set(["created", "delivered"]),
                "degraded",
            ),
            # DOWN
            (set([]), set([]), "down"),
            (set(["delivered"]), set([]), "down"),
            (set([]), set(["delivered"]), "down"),
            (set(["created"]), set(["created"]), "down"),
            (set(["created"]), set(["permanent-failure"]), "down"),
            (set(["created"]), set(["technical-failure"]), "down"),
            (set(["created"]), set(["temporary-failure"]), "down"),
            (set(["permanent-failure"]), set(["permanent-failure"]), "down"),
            (set(["permanent-failure"]), set(["technical-failure"]), "down"),
        ],
    )
    def test_medium_status(self, mediumstat1, mediumstat2, expected_result):
        assert determine_medium_status(mediumstat1, mediumstat2) == expected_result


class TestLowStatus:

    @pytest.mark.parametrize(
        "lowstat1, lowstat2, expected_result",
        [
            # UP
            (
                set(["sent", "delivered"]),
                set(["sending", "created", "delivered"]),
                "up",
            ),
            (set(["created"]), set(["delivered"]), "up"),
            (set(["sent", "delivered"]), set(["temporary-failure"]), "up"),
            # DEGRADED
            (
                set(["sent", "delivered", "created"]),
                set(["created", "delivered"]),
                "degraded",
            ),
            # DOWN
            (set([]), set([]), "down"),
            (set(["delivered"]), set([]), "down"),
            (set([]), set(["delivered"]), "down"),
            (set(["created"]), set(["created"]), "down"),
            (set(["created"]), set(["permanent-failure"]), "down"),
            (set(["created"]), set(["technical-failure"]), "down"),
            (set(["created"]), set(["temporary-failure"]), "down"),
            (set(["permanent-failure"]), set(["permanent-failure"]), "down"),
            (set(["permanent-failure"]), set(["technical-failure"]), "down"),
        ],
    )
    def test_low_status(self, lowstat1, lowstat2, expected_result):
        assert determine_low_status(lowstat1, lowstat2) == expected_result
