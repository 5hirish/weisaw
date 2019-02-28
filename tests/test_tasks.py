import pytest
from datetime import datetime
from weisaw.worker.tasks import parse_leave, extract_leave_features
from unittest.mock import patch, Mock

# @pytest.mark.parametrize("raw_text,leave_expected_list", [
#     ("OOO on 5th and 6th, not feeling well", [{"from": datetime(2019, 1, 5), "to": datetime(2019, 1, 6)}]),
#     ("WFH tomorrow and day after tomorrow", [{"from": datetime(2019, 1, 2), "to": datetime(2019, 1, 3)}]),
#     ("OOO for the rest of the week", [{"from": datetime(2019, 1, 2), "to": datetime(2019, 1, 6)}]),
#     ("WFH on the wednesday and friday", [{"from": datetime(2019, 1, 2), "to": datetime(2019, 1, 2)},
#                                          {"from": datetime(2019, 1, 4), "to": datetime(2019, 1, 4)}]),
#     ("OOO for the last monday of the month", [{"from": datetime(2019, 1, 28), "to": datetime(2019, 1, 28)}]),
#     ("WFH 5th Nov and 3rd Jun", [{"from": datetime(2019, 11, 5), "to": datetime(2019, 11, 5)},
#                                  {"from": datetime(2019, 6, 3), "to": datetime(2019, 6, 3)}]),
#     ("WFH next thursday", [{"from": datetime(2019, 1, 10), "to": datetime(2019, 1, 10)}]),
#     ("WFH for the next 3 days", [{"from": datetime(2019, 1, 2), "to": datetime(2019, 1, 4)}])
# ])
@pytest.mark.parametrize("raw_text,leave_expected_list", [
    ("OOO on 2nd and 3rd Jan", [{"from": datetime(2019, 1, 2), "to": datetime(2019, 1, 2)},
                                {"from": datetime(2019, 1, 3), "to": datetime(2019, 1, 3)}])
])
def test_extract_leave_features(raw_text, leave_expected_list):
    leave_date_list = extract_leave_features(raw_text)
    print(datetime.now())
    print(leave_date_list)

    for leaves, expected_leaves in zip(leave_date_list, leave_expected_list):
        assert leaves.get("from").day == expected_leaves.get("from").day
        assert leaves.get("from").month == expected_leaves.get("from").month
        assert leaves.get("from").year == expected_leaves.get("from").year

        assert leaves.get("to").day == expected_leaves.get("to").day
        assert leaves.get("to").month == expected_leaves.get("to").month
        assert leaves.get("to").year == expected_leaves.get("to").year


@patch('weisaw.worker.tasks.get_slack_user_info', return_value=("test@alleviate.xyz", "Test User",
                                                                "http://avatar/alleviate.png"))
def test_get_slack_user_info():
    pass
