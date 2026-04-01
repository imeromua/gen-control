from datetime import datetime, timezone, timedelta
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import NotFoundException
from app.modules.motohours.schemas import MaintenanceCreate
from app.modules.motohours.service import MotohoursService


@pytest.fixture
def motohours_service():
    mock_db = AsyncMock()
    mock_db.begin = MagicMock(return_value=AsyncMock())
    mock_db.add = MagicMock()
    
    service = MotohoursService(mock_db)
    service.repo = AsyncMock()
    service.gen_repo = AsyncMock()
    return service

@pytest.fixture
def current_user_id():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_get_total_success(motohours_service: MotohoursService):
    gen_id = uuid.uuid4()
    mock_gen = MagicMock()
    mock_settings = MagicMock()
    mock_settings.initial_motohours = Decimal("100.5")
    mock_gen.settings = mock_settings
    
    motohours_service.gen_repo.get_by_id.return_value = mock_gen
    motohours_service.repo.get_total_hours_added.return_value = Decimal("20.5")
    
    result = await motohours_service.get_total(gen_id)
    
    assert result.motohours_total == Decimal("121.0")


@pytest.mark.asyncio
async def test_create_maintenance_calculates_next_service(motohours_service: MotohoursService, current_user_id):
    gen_id = uuid.uuid4()
    mock_gen = MagicMock()
    mock_settings = MagicMock()
    mock_settings.initial_motohours = Decimal("50.0")
    mock_settings.to_interval_hours = Decimal("200.0")
    mock_gen.settings = mock_settings
    
    motohours_service.gen_repo.get_by_id.return_value = mock_gen
    motohours_service.repo.get_total_hours_added.return_value = Decimal("40.0") # Total will be 90
    
    # Mocking repo create
    mock_created = MagicMock()
    # Pydantic validation handles MagicMock differently in model_validate,
    # so we construct a mock dictionary-like or class object that model_validate likes.
    class MockLog:
        id = uuid.uuid4()
        generator_id = gen_id
        performed_by = current_user_id
        motohours_at_service = Decimal("90.0")
        next_service_at_hours = Decimal("290.0")
        notes = "Oil change"
        performed_at = datetime.now(tz=timezone.utc)
        # Mock shift to be 1 hour old
        started_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        # Dummy attributes for response model
        
    mock_created_instance = MockLog()
    motohours_service.repo.create_maintenance.return_value = mock_created_instance
    
    data = MaintenanceCreate(notes="Oil change")
    
    result = await motohours_service.create_maintenance(gen_id, data, current_user_id)
    
    # Assert calculations
    args, _ = motohours_service.repo.create_maintenance.call_args
    assert args[0].motohours_at_service == Decimal("90.0")
    assert args[0].next_service_at_hours == Decimal("290.0")
    
    motohours_service.gen_repo.add_event.assert_called_once()
    event_args, _ = motohours_service.gen_repo.add_event.call_args
    assert event_args[0].event_type == "MAINTENANCE_PERFORMED"
    
    # Assert transaction
    motohours_service.db.begin.assert_called_once()

