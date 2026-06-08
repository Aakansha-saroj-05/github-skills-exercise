from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_participant():
    email = "teststudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup?email=teststudent%40mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    email = activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Participant is already signed up"


def test_remove_participant_unregisters_user():
    email = activities["Chess Club"]["participants"][0]
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants?email=missing%40mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
