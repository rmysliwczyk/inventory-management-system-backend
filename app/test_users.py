import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from .main import app
from .dependencies import get_session, hash_password

from .models.user import User, UserRole

admin_id = ""
user_id = ""

@pytest.fixture(name="session", scope="module")
def session_fixture():
    engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

@pytest.fixture(name="admin_token")
def admin_fixture(client: TestClient):
    response = client.post("/auth/token", data={'username': 'admin', 'password': 'admin'})
    yield response.json()["access_token"]

@pytest.fixture(name="user_token")
def user_fixture(client: TestClient):
    response = client.post("/auth/token", data={'username': 'user', 'password': 'user'})
    yield response.json()["access_token"]


# Testing database only (and preparing data for next test cases)
def test_db_admin_can_be_created(session: Session):
    new_admin = User(username="admin", hashed_password=hash_password("admin"), role=UserRole.ADMIN)
    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)

def test_db_admin_exists(session: Session):
    admin = session.exec(select(User).where(User.username == "admin")).first()
    assert admin is not None

def test_db_user_can_be_created(session: Session):
    new_user = User(username="user", hashed_password=hash_password("user"), role=UserRole.USER)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

def test_db_user_exists(session: Session):
    user = session.exec(select(User).where(User.username == "user")).first()
    assert user is not None

# Testing endpoints

# /users/me
def test_users_me_returns_200_response_with_correct_token(admin_token: str, client: TestClient):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

def test_users_me_returns_401_response_with_incorrect_token(client: TestClient):
    response = client.get("/users/me", headers={"Authorization": f"Bearer BAD_TOKEN"})
    assert response.status_code == 401

def test_users_me_returns_correct_user_for_the_given_token_when_user_is_admin(admin_token: str, client: TestClient):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {admin_token}"})
    global admin_id
    admin_id = response.json()["id"]
    assert response.json()["username"] == "admin"

def test_users_me_returns_correct_user_for_the_given_token_when_user_is_regular_user(user_token: str, client: TestClient):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {user_token}"})
    global user_id
    user_id = response.json()["id"]
    assert response.json()["username"] == "user"

# /users/
def test_users_returns_200_response_with_correct_token(admin_token: str, client: TestClient):
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

def test_users_returns_401_response_with_incorrect_token(client: TestClient):
    response = client.get("/users", headers={"Authorization": f"Bearer BAD_TOKEN"})
    assert response.status_code == 401

def test_users_returns_correct_list_of_users(admin_token: str, client: TestClient):
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.json()[0]["username"] == "admin"
    assert response.json()[1]["username"] == "user"

# /users/{id}
def test_users_id_returns_200_response_with_correct_token(admin_token: str, client: TestClient):
    global admin_id
    response = client.get(f"/users/{admin_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

def test_users_id_returns_401_response_with_incorrect_token(client: TestClient):
    global admin_id
    response = client.get(f"/users/{admin_id}", headers={"Authorization": f"Bearer BAD_TOKEN"})
    assert response.status_code == 401

def test_users_id_returns_admin(admin_token: str, client: TestClient):
    global admin_id
    response = client.get(f"/users/{admin_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.json()["username"] == "admin"

def test_users_id_returns_user(admin_token: str, client: TestClient):
    global user_id
    response = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.json()["username"] == "user"

# POST /users/

def test_post_users_creates_a_new_user_when_using_admin_token(admin_token: str, client: TestClient):
    response = client.post(f"/users", headers={"Authorization": f"Bearer {admin_token}"}, json={"username": "new_user", "password": "new_password"})
    assert response.status_code == 200
    assert response.json()["username"] == "new_user"

def test_post_users_does_not_create_a_new_user_when_using_user_token(user_token: str, client: TestClient):
    response = client.post(f"/users", headers={"Authorization": f"Bearer {user_token}"}, json={"username": "new_user_2", "password": "new_password_2"})
    assert response.status_code == 401


