import pytest

def test_root(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/')
    json_data = response
    assert response.status_code == 200
    assert json_data.get("developer") == "Alleviate"
