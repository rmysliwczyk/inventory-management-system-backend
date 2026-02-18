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

def test_db_asset_type_can_be_created(session: Session):
    new_asset_type = AssetType(name="TestAssetType")
    session.add(new_asset_type)
    session.commit()
    session.refresh(new_asset_type)

def test_db_asset_type_exists(session: Session):
    global asset_type_id
    asset_type = session.exec(select(AssetType).where(AssetType.name=="TestAssetType")).first()
    assert asset_type is not None
    asset_type_id = str(asset_type.id)

# Testing endpoints

# POST /assets

def test_post_asset_is_created_when_using_admin_token(admin_token: str, client: TestClient):
    global asset_type_id
    global asset_id
    response = client.post("/assets", headers={"Authorization": f"Bearer {admin_token}"}, json={"asset_type_id": asset_type_id, "description": "TEST"})
    assert response.status_code == 200
    assert response.json()["description"] == "TEST"
    asset_id = response.json()["id"]

def test_post_asset_is_created_with_custom_acquisition_date_when_using_admin_token(admin_token: str, client: TestClient):
    global asset_type_id
    global asset_id
    response = client.post("/assets", headers={"Authorization": f"Bearer {admin_token}"}, json={"asset_type_id": asset_type_id, "acquisition_date": "2000-01-01"})
    assert response.status_code == 200
    assert response.json()["acquisition_date"] == "2000-01-01"

def test_post_asset_is_not_created_when_using_user_token(user_token: str, client: TestClient):
    global asset_type_id
    response = client.post("/assets", headers={"Authorization": f"Bearer {user_token}"}, json={"asset_type_id": asset_type_id, "description": "TEST2"})
    assert response.status_code == 401

# /assets

def test_assets_returns_all_assets_when_using_admin_token(admin_token: str, client: TestClient):
    response = client.get("/assets", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["description"] == "TEST"
    assert response.json()[1]["acquisition_date"] == "2000-01-01"

def test_assets_returns_all_assets_when_using_user_token(user_token: str, client: TestClient):
    response = client.get("/assets", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["description"] == "TEST"
    assert response.json()[1]["acquisition_date"] == "2000-01-01"

def test_assets_returns_401_with_bad_token(client: TestClient):
    response = client.get("/assets", headers={"Authorization": f"Bearer BAD_TOKEN"})
    assert response.status_code == 401

# /assets/{asset_id}

def test_assets_asset_id_returns_the_correct_asset_when_using_admin_token(admin_token: str, client: TestClient):
    global asset_id
    response = client.get(f"/assets/{asset_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["description"] == "TEST"

def test_assets_asset_id_returns_the_correct_asset_when_using_user_token(user_token: str, client: TestClient):
    global asset_id
    response = client.get(f"/assets/{asset_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert response.json()["description"] == "TEST"

def test_assets_asset_id_returns_401_with_bad_token(client: TestClient):
    global asset_id
    response = client.get(f"/assets/{asset_id}", headers={"Authorization": "Bearer BAD_TOKEN"})
    assert response.status_code == 401

# DELETE /assets/{asset_id}

def test_delete_assets_asset_id_returns_401_with_bad_token(client: TestClient):
    global asset_id
    response = client.delete(f"/assets/{asset_id}", headers={"Authorization": "Bearer BAD_TOKEN"})
    assert response.status_code == 401

def test_delete_assets_asset_id_asset_is_not_deleted_when_using_user_token(user_token: str, client: TestClient):
    global asset_id
    response = client.delete(f"/assets/{asset_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authorized"

def test_delete_assets_asset_id_asset_is_deleted_when_using_admin_token(admin_token: str, client: TestClient, session: Session):
    global asset_id
    response = client.delete(f"/assets/{asset_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
    asset_in_db = session.exec(select(Asset).where(Asset.id == uuid.UUID(asset_id))).first()
    assert asset_in_db == None




