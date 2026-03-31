import uuid
from datetime import datetime, time, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import ConflictException, ForbiddenException
from app.modules.rules.service import RulesService


@pytest.fixture
def rules_service():
    mock_db = AsyncMock()
    service = RulesService(mock_db)
    # Зробимо моки для репозиторіїв безпосередньо в сервісі
    service.settings_repo = AsyncMock()
    service.shift_repo = AsyncMock()
    service.gen_repo = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_check_only_one_generator_active_success(rules_service: RulesService):
    # Коли немає жодної активної зміни
    rules_service.shift_repo.get_any_active.return_value = None
    
    # Має пройти без помилок
    await rules_service.check_only_one_generator_active()


@pytest.mark.asyncio
async def test_check_only_one_generator_active_fails(rules_service: RulesService):
    # Вже є активна зміна
    rules_service.shift_repo.get_any_active.return_value = MagicMock()
    
    # Має видати ConflictException
    with pytest.raises(ConflictException) as excinfo:
        await rules_service.check_only_one_generator_active()
    
    assert "Інший генератор вже працює" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_check_no_active_shift_success(rules_service: RulesService):
    # Немає змін для конкретного генератора
    rules_service.shift_repo.get_active_for_generator.return_value = None
    
    # МАє пройти
    await rules_service.check_no_active_shift(uuid.uuid4())


@pytest.mark.asyncio
async def test_check_no_active_shift_fails(rules_service: RulesService):
    # Є активна зміна для конкретного генератора
    mock_shift = MagicMock()
    mock_shift.shift_number = 42
    rules_service.shift_repo.get_active_for_generator.return_value = mock_shift
    
    with pytest.raises(ConflictException) as excinfo:
        await rules_service.check_no_active_shift(uuid.uuid4())
        
    assert "Вже є активна зміна #42" in str(excinfo.value.detail)
