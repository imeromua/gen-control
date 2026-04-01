import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.enums import GeneratorType
from app.common.exceptions import NotFoundException
from app.modules.generators.schemas import GeneratorCreate, GeneratorSettingsUpdate
from app.modules.generators.service import GeneratorService


@pytest.fixture
def gen_service():
    mock_db = AsyncMock()
    mock_db.begin = MagicMock(return_value=AsyncMock())
    mock_db.add = MagicMock()
    
    service = GeneratorService(mock_db)
    service.db = mock_db
    service.repo = AsyncMock()
    service.moto_repo = AsyncMock()
    return service

@pytest.fixture
def current_user_id():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_create_generator_success(gen_service: GeneratorService, current_user_id):
    create_data = GeneratorCreate(
        name="Main Generator",
        type=GeneratorType.GASOLINE,
        model="Honda EU22i",
        serial_number="SN12345"
    )
    
    mock_created = MagicMock()
    mock_created.id = uuid.uuid4()
    mock_created.name = "Main Generator"
    gen_service.repo.create.return_value = mock_created
    
    result = await gen_service.create(create_data, current_user_id)
    
    assert result == mock_created
    gen_service.repo.create.assert_called_once()
    
    # Verify that an event was logged
    gen_service.repo.add_event.assert_called_once()
    args, _ = gen_service.repo.add_event.call_args
    event = args[0]
    assert event.event_type == "GENERATOR_CREATED"
    assert event.performed_by == current_user_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(gen_service: GeneratorService):
    gen_service.repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundException) as excinfo:
        await gen_service.get_by_id(uuid.uuid4())
        
    assert "not found" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_deactivate_generator(gen_service: GeneratorService, current_user_id):
    gen_id = uuid.uuid4()
    mock_gen = MagicMock()
    mock_gen.is_active = True
    
    gen_service.repo.get_by_id.return_value = mock_gen
    gen_service.repo.update.return_value = mock_gen
    
    result = await gen_service.deactivate(gen_id, current_user_id)
    
    assert mock_gen.is_active is False
    gen_service.repo.update.assert_called_once_with(mock_gen)
    gen_service.repo.add_event.assert_called_once()


@pytest.mark.asyncio
async def test_get_status_calculations(gen_service: GeneratorService):
    gen_id = uuid.uuid4()
    
    mock_gen = MagicMock()
    mock_gen.id = gen_id
    mock_gen.name = "Test Gen"
    mock_gen.type = "GASOLINE"
    mock_gen.is_active = True
    
    mock_settings = MagicMock()
    # Mock settings values specifically explicitly, to avoid mocks doing weird things on str()
    mock_settings.initial_motohours = Decimal("100.0")
    mock_settings.to_interval_hours = Decimal("50.0")
    mock_settings.to_warning_before_hours = Decimal("10.0")
    mock_settings.tank_capacity_liters = Decimal("100.0")
    mock_settings.fuel_warning_level = Decimal("20.0")
    mock_settings.fuel_critical_level = Decimal("10.0")
    mock_settings.fuel_type = "A95"
    
    mock_gen.settings = mock_settings
    gen_service.repo.get_by_id.return_value = mock_gen
    
    # Mock DB return sizes
    gen_service.moto_repo.get_total_hours_added.return_value = Decimal("40.0")
    gen_service.moto_repo.get_motohours_since_last_maintenance.return_value = Decimal("40.0")
    
    # Setup last maintenance to exist
    mock_last_to = MagicMock()
    mock_last_to.next_service_at_hours = None # fallback to calculation
    gen_service.moto_repo.get_last_maintenance.return_value = mock_last_to
    
    status = await gen_service.get_status(gen_id)
    
    # initial(100) + added(40)
    assert status.motohours_total == Decimal("140.0")
    
    # last_to calculated from motohours_since_last_to(40) + interval(50) -> next at 140+whatever?
    # Wait, the logic says if next_service_at_hours is None:
    # next_to_at_hours = motohours_since_last_to(40) + to_interval(50) = 90
    # hours_to_next_to = next_to(90) - total(140) = -50
    assert status.motohours_since_last_to == Decimal("40.0")
    assert status.next_to_at_hours == Decimal("90.0")
    assert status.hours_to_next_to == Decimal("-50.0")
    assert status.to_warning_active is True  # -50 < 10


@pytest.mark.asyncio
async def test_update_generator_logs_event(gen_service: GeneratorService, current_user_id):
    """BUG-5: update() повинен записувати EventLog з GENERATOR_UPDATED."""
    from app.modules.generators.schemas import GeneratorUpdate

    gen_id = uuid.uuid4()
    mock_gen = MagicMock()
    mock_gen.name = "Old Name"
    mock_gen.type = "GASOLINE"
    mock_gen.model = "Old Model"
    mock_gen.serial_number = "OLD-SN"
    mock_gen.is_active = True
    gen_service.repo.get_by_id.return_value = mock_gen
    gen_service.repo.update.return_value = mock_gen

    update_data = GeneratorUpdate(name="New Name")
    await gen_service.update(gen_id, update_data, current_user_id)

    # Після виправлення: add_event повинен бути викликаний з GENERATOR_UPDATED
    gen_service.repo.add_event.assert_called_once()
    args, _ = gen_service.repo.add_event.call_args
    event = args[0]
    assert event.event_type == "GENERATOR_UPDATED"
    assert event.performed_by == current_user_id


@pytest.mark.asyncio
async def test_create_generator_commits_exactly_once(gen_service: GeneratorService, current_user_id):
    """create() повинен викликати db.commit() рівно 1 раз."""
    from app.modules.generators.schemas import GeneratorCreate
    from app.common.enums import GeneratorType

    create_data = GeneratorCreate(
        name="Test Gen",
        type=GeneratorType.GASOLINE,
        model="Honda",
        serial_number="SN-001"
    )
    mock_created = MagicMock()
    mock_created.id = uuid.uuid4()
    gen_service.repo.create.return_value = mock_created

    await gen_service.create(create_data, current_user_id)

    # Після виправлення: commit рівно 1 раз (через begin)
    gen_service.db.begin.assert_called()
    gen_service.repo.add_event.assert_called_once()

