import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.common.exceptions import UnauthorizedException
from app.config import settings
from app.modules.auth.schemas import LoginRequest
from app.modules.auth.service import AuthService


@pytest.fixture
def auth_service():
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    service = AuthService(mock_db, mock_redis)
    service.repo = AsyncMock()
    return service

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.username = "test_user"
    user.password_hash = "hashed_pw"
    user.is_active = True
    user.role.name = "OPERATOR"
    return user


@pytest.mark.asyncio
@patch("app.modules.auth.service.verify_password")
async def test_login_success(mock_verify_password, auth_service: AuthService, mock_user):
    auth_service.repo.get_by_username.return_value = mock_user
    mock_verify_password.return_value = True
    
    request = LoginRequest(username="test_user", password="password")
    
    response = await auth_service.login(request)
    
    # Assert
    assert response.access_token is not None
    auth_service.redis.setex.assert_called_once()
    
    # Check JWT content
    payload = jwt.decode(response.access_token, settings.JWT_SECRET, algorithms=["HS256"])
    assert payload["sub"] == str(mock_user.id)
    assert payload["username"] == "test_user"
    assert payload["role"] == "OPERATOR"


@pytest.mark.asyncio
async def test_login_invalid_credentials(auth_service: AuthService):
    auth_service.repo.get_by_username.return_value = None
    
    request = LoginRequest(username="unknown", password="password")
    
    with pytest.raises(UnauthorizedException) as excinfo:
        await auth_service.login(request)
        
    assert "Invalid username or password" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_login_disabled_user(auth_service: AuthService, mock_user):
    mock_user.is_active = False
    auth_service.repo.get_by_username.return_value = mock_user
    
    with patch("app.modules.auth.service.verify_password", return_value=True):
        request = LoginRequest(username="test_user", password="password")
        
        with pytest.raises(UnauthorizedException) as excinfo:
            await auth_service.login(request)
            
        assert "User account is disabled" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(auth_service: AuthService):
    # Redis says token doesn't exist
    auth_service.redis.get.return_value = None
    
    with pytest.raises(UnauthorizedException) as excinfo:
        await auth_service.get_current_user("invalid_token")
        
    assert "Token is invalid or expired" in excinfo.value.detail
