import pytest
from datetime import datetime
from weisaw.worker.tasks import parse_leave, extract_leave_features
from unittest.mock import patch, Mock

# @pytest.mark.parametrize("u_access,requested,result", [
#     (["RW_Data", "RW_Models", "RW_Reports", "RW_Evaluations", "RW_Results", "R_Logs"], "RW_Data", True),
#     (["RW_Data", "RW_Models", "RW_Reports", "RW_Evaluations", "RW_Results", "R_Logs"], "R_Data", True),
#     (["RW_Data", "RW_Models", "RW_Reports", "RW_Evaluations", "RW_Results", "R_Logs"], "RW_Logs", False),
#     (["RW_Data", "RW_Models", "RW_Reports", "RW_Evaluations", "RW_Results", "R_Logs"], "RW_Project", False)
# ])
# def test_parse_leave(celery_app, raw_text, leave_type, user_name, user_id, channel_id, team_id, response_url):
#     pass


# @pytest.mark.parametrize("raw_text,leave_expected_list", [
#     ("OOO on 5th and 6th, not feeling well", [{"from": datetime(2018, 1, 5), "to": datetime(2018, 1, 6)}]),
#     ("WFH tomorrow and day after tomorrow", [{"from": datetime(2018, 1, 2), "to": datetime(2018, 1, 3)}]),
#     ("OOO for the rest of the week", [{"from": datetime(2018, 1, 2), "to": datetime(2018, 1, 6)}]),
#     ("WFH on the wednesday and friday", [{"from": datetime(2018, 1, 2), "to": datetime(2018, 1, 2)},
#                                          {"from": datetime(2018, 1, 4), "to": datetime(2018, 1, 4)}]),
#     ("OOO for the last monday of the month", [{"from": datetime(2018, 1, 28), "to": datetime(2018, 1, 28)}]),
#     ("WFH 5th Nov and 3rd Jun", [{"from": datetime(2018, 11, 5), "to": datetime(2018, 11, 5)},
#                                  {"from": datetime(2018, 6, 3), "to": datetime(2018, 6, 3)}]),
#     ("WFH next thursday", [{"from": datetime(2018, 1, 10), "to": datetime(2018, 1, 10)}]),
#     ("WFH for the next 3 days", [{"from": datetime(2018, 1, 2), "to": datetime(2018, 1, 4)}])
# ])
@pytest.mark.parametrize("raw_text,leave_expected_list", [
    ("WFH tomorrow and day after tomorrow", [{"from": datetime(2018, 1, 2), "to": datetime(2018, 1, 3)}])
])
def test_extract_leave_features(raw_text, leave_expected_list):
    leave_date_list = extract_leave_features(raw_text)

    for leaves, expected_leaves in zip(leave_date_list, leave_expected_list):
        assert leaves.get("from").day == expected_leaves.get("from").day
        assert leaves.get("from").month == expected_leaves.get("from").month

        assert leaves.get("to").day == expected_leaves.get("to").day
        assert leaves.get("to").month == expected_leaves.get("to").month


@patch('weisaw.worker.tasks.get_slack_user_info', return_value=("test@alleviate.xyz", "Test User",
                                                                "http://avatar/alleviate.png"))
def test_get_slack_user_info():
    pass
