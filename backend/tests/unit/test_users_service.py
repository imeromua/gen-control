import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.common.exceptions import ConflictException, NotFoundException
from app.modules.users.schemas import UserCreate, UserUpdate
from app.modules.users.service import UserService


@pytest.fixture
def user_service():
    mock_db = AsyncMock()
    service = UserService(mock_db)
    service.repo = AsyncMock()
    return service

@pytest.fixture
def mock_role():
    role = MagicMock()
    role.id = uuid.uuid4()
    role.name = "OPERATOR"
    return role


@pytest.mark.asyncio
@patch("app.modules.users.service.hash_password")
async def test_create_user_success(mock_hash_password, user_service: UserService, mock_role):
    # Username is available
    user_service.repo.get_by_username.return_value = None
    user_service.repo.get_role_by_id.return_value = mock_role
    
    mock_hash_password.return_value = "hashed_secret"
    
    mock_created = MagicMock()
    user_service.repo.create.return_value = mock_created
    
    user_data = UserCreate(
        username="new_operator",
        password="secret_password",
        full_name="Ivan Franko",
        role_id=mock_role.id
    )
    
    result = await user_service.create(user_data)
    
    assert result == mock_created
    user_service.repo.create.assert_called_once()
    
    # Check that it hashed the password correctly
    mock_hash_password.assert_called_once_with("secret_password")


@pytest.mark.asyncio
async def test_create_user_username_taken(user_service: UserService):
    # Username already exists
    user_service.repo.get_by_username.return_value = MagicMock()
    
    user_data = UserCreate(
        username="existing_user",
        password="password",
        full_name="Test",
        role_id=uuid.uuid4()
    )
    
    with pytest.raises(ConflictException) as excinfo:
        await user_service.create(user_data)
        
    assert "already taken" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_update_user_not_found(user_service: UserService):
    user_service.repo.get_by_id.return_value = None
    
    update_data = UserUpdate(full_name="New Name")
    
    with pytest.raises(NotFoundException):
        await user_service.update(uuid.uuid4(), update_data)


@pytest.mark.asyncio
async def test_deactivate_user_success(user_service: UserService):
    mock_user = MagicMock()
    mock_user.is_active = True
    
    user_service.repo.get_by_id.return_value = mock_user
    user_service.repo.update.return_value = mock_user
    
    result = await user_service.deactivate(uuid.uuid4())
    
    assert mock_user.is_active is False
    user_service.repo.update.assert_called_once_with(mock_user)

