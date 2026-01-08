import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of initial participants and restore after each test
    backup = {k: v.get("participants", []).copy() for k, v in activities.items()}
    yield
    for k, parts in backup.items():
        activities[k]["participants"] = parts.copy()


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "test.student@mergington.edu"

    # Ensure not already present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"]
    assert email in activities[activity]["participants"]

    # Unregister
    resp2 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_conflict():
    activity = "Basketball"
    existing = activities[activity]["participants"][0]
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_missing():
    activity = "Tennis Club"
    email = "nonexistent@mergington.edu"
    resp = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 404
