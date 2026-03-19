import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_dict(client):
    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_expected_fields(client):
    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert email in activities[activity_name]["participants"]


def test_signup_nonexistent_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404


def test_signup_duplicate_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity_name = "Chess Club"

    # Act
    client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_student_not_signed_up_returns_404(client):
    # Arrange
    email = "notregistered@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
