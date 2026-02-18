import pytest
import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from .main import app
from .dependencies import get_session, hash_password

from .models.user import User, UserRole
from .models.asset_type import AssetType
from .models.asset import Asset

asset_type_id = ""
asset_id = ""

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

# POST /asset-types

def test_post_asset_type_is_created_when_using_admin_token(admin_token: str, client: TestClient):
    global asset_type_id
    response = client.post("/asset-types", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "TestAssetType"})
    assert response.status_code == 200
    assert response.json()["name"] == "TestAssetType"
    asset_type_id = response.json()["id"]

def test_post_asset_type_is_created_when_using_special_characters_in_name_and_when_using_admin_token(admin_token: str, client: TestClient):
    global asset_type_id
    response = client.post("/asset-types", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "@!#@"})
    assert response.status_code == 200
    assert response.json()["name"] == "@!#@"
    asset_type_id = response.json()["id"]

def test_post_asset_type_is_not_created_when_using_user_token(user_token: str, client: TestClient):
    response = client.post("/asset-types", headers={"Authorization": f"Bearer {user_token}"}, json={"name": "TestAssetType"})
    assert response.status_code == 401

# /asset-types

def test_asset_types_returns_all_asset_types_when_using_admin_token(admin_token: str, client: TestClient):
    response = client.get("/asset-types", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "TestAssetType"
    assert response.json()[1]["name"] == "@!#@"

def test_asset_types_returns_all_asset_types_when_using_user_token(user_token: str, client: TestClient):
    response = client.get("/asset-types", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "TestAssetType"
    assert response.json()[1]["name"] == "@!#@"

def test_asset_types_returns_401_with_bad_token(client: TestClient):
    response = client.get("/asset-types", headers={"Authorization": f"Bearer BAD_TOKEN"})
    assert response.status_code == 401

# /asset-types/{asset_type_id}

def test_asset_types_asset_type_id_returns_the_correct_asset_type_when_using_admin_token(admin_token: str, client: TestClient):
    global asset_type_id
    response = client.get(f"/asset-types/{asset_type_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == str(asset_type_id)

def test_asset_types_asset_type_id_returns_the_correct_asset_when_using_user_token(user_token: str, client: TestClient):
    global asset_type_id
    response = client.get(f"/asset-types/{asset_type_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == str(asset_type_id)

def test_asset_types_asset_type_id_returns_401_with_bad_token(client: TestClient):
    global asset_type_id
    response = client.get(f"/asset-types/{asset_type_id}", headers={"Authorization": "Bearer BAD_TOKEN"})
    assert response.status_code == 401

# DELETE /asset-types/{asset_type_id}

def test_delete_asset_types_asset_type_id_returns_401_with_bad_token(client: TestClient):
    global asset_type_id
    response = client.delete(f"/asset-types/{asset_type_id}", headers={"Authorization": "Bearer BAD_TOKEN"})
    assert response.status_code == 401

def test_delete_asset_types_asset_type_id_asset_type_is_not_deleted_when_using_user_token(user_token: str, client: TestClient):
    global asset_type_id
    response = client.delete(f"/asset-types/{asset_type_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authorized"

def test_delete_asset_types_asset_type_id_asset_type_is_deleted_when_using_admin_token(admin_token: str, client: TestClient, session: Session):
    global asset_type_id
    response = client.delete(f"/asset-types/{asset_type_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
    asset_type_in_db = session.exec(select(AssetType).where(AssetType.id == uuid.UUID(asset_type_id))).first()
    assert asset_type_in_db == None




