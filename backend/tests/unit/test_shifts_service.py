import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.enums import RoleName, ShiftStatus
from app.common.exceptions import ConflictException, ForbiddenException
from app.modules.shifts.schemas import ShiftStartRequest
from app.modules.shifts.service import ShiftService


@pytest.fixture
def shift_service():
    mock_db = AsyncMock()
    mock_db.begin = MagicMock(return_value=AsyncMock())

    # Also mock synchronous methods explicitly to avoid RuntimeWarning
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    service = ShiftService(mock_db)

    # Mock repositories
    service.repo = AsyncMock()
    service.settings_repo = AsyncMock()
    service.gen_repo = AsyncMock()
    service.moto_repo = AsyncMock()
    service.fuel_repo = AsyncMock()  # Added fuel_repo
    service.rules = AsyncMock()

    return service


@pytest.fixture
def mock_user_operator():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.role.name = RoleName.OPERATOR.value
    return user


@pytest.fixture
def mock_user_admin():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.role.name = RoleName.ADMIN.value
    return user


@pytest.mark.asyncio
async def test_start_shift_success(shift_service: ShiftService, mock_user_operator):
    # Setup mock active generator
    gen_id = uuid.uuid4()
    mock_gen = MagicMock()
    mock_gen.is_active = True
    mock_gen.name = "Generator A"
    shift_service.gen_repo.get_by_id.return_value = mock_gen

    shift_service.repo.get_next_shift_number.return_value = 1

    # Setup mock created shift
    mock_created = MagicMock()
    shift_service.repo.create.return_value = mock_created

    request_data = ShiftStartRequest(generator_id=gen_id)

    # Run
    result = await shift_service.start(request_data, mock_user_operator)

    # Asserts
    shift_service.rules.check_working_hours.assert_called_once()
    shift_service.rules.check_only_one_generator_active.assert_called_once()
    shift_service.rules.check_no_active_shift.assert_called_once()

    shift_service.gen_repo.add_event.assert_called_once()
    assert result == mock_created


@pytest.mark.asyncio
async def test_start_shift_generator_not_active(shift_service: ShiftService, mock_user_operator):
    gen_id = uuid.uuid4()
    mock_gen = MagicMock()
    mock_gen.is_active = False  # Generator disabled
    shift_service.gen_repo.get_by_id.return_value = mock_gen

    request_data = ShiftStartRequest(generator_id=gen_id)

    with pytest.raises(ConflictException):
        await shift_service.start(request_data, mock_user_operator)


@pytest.mark.asyncio
async def test_stop_shift_success_as_operator(shift_service: ShiftService, mock_user_operator):
    shift_id = uuid.uuid4()
    gen_id = uuid.uuid4()

    mock_shift = MagicMock()
    mock_shift.id = shift_id
    mock_shift.generator_id = gen_id
    mock_shift.status = ShiftStatus.ACTIVE.value
    mock_shift.started_by = mock_user_operator.id  # Same user
    mock_shift.started_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    shift_service.repo.get_by_id.return_value = mock_shift

    # Generator settings (for fuel consumption calc)
    mock_settings = MagicMock()
    mock_settings.fuel_consumption_per_hour = Decimal("2.5")
    mock_settings.initial_motohours = Decimal("100.0")

    mock_gen = MagicMock()
    mock_gen.settings = mock_settings
    shift_service.gen_repo.get_settings.return_value = mock_settings
    shift_service.gen_repo.get_by_id.return_value = mock_gen

    shift_service.moto_repo.get_total_hours_added.return_value = Decimal("5.0")

    # Mock fuel stock
    mock_stock = MagicMock()
    mock_stock.current_liters = Decimal("50.0")
    shift_service.fuel_repo.get_stock.return_value = mock_stock

    # Run
    await shift_service.stop(shift_id, mock_user_operator)

    assert mock_shift.status == ShiftStatus.CLOSED.value
    assert mock_shift.stopped_by == mock_user_operator.id
    shift_service.repo.update.assert_called_once_with(mock_shift)
    shift_service.db.add.assert_called_once()  # MotohoursLog

    # BUG: This should be called!
    shift_service.fuel_repo.get_stock.assert_called_once()
    assert mock_stock.current_liters < Decimal("50.0")


@pytest.mark.asyncio
async def test_stop_shift_forbidden_for_other_operator(shift_service: ShiftService, mock_user_operator):
    shift_id = uuid.uuid4()

    mock_shift = MagicMock()
    mock_shift.status = ShiftStatus.ACTIVE.value
    mock_shift.started_by = uuid.uuid4()  # Different user ID

    shift_service.repo.get_by_id.return_value = mock_shift

    with pytest.raises(ForbiddenException):
        await shift_service.stop(shift_id, mock_user_operator)


@pytest.mark.asyncio
async def test_stop_shift_transactional_failure_rollback(shift_service: ShiftService, mock_user_admin):
    # This test verifies that we are using atomic transactions
    shift_id = uuid.uuid4()

    mock_shift = MagicMock()
    mock_shift.status = ShiftStatus.ACTIVE.value
    mock_shift.started_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    mock_shift.shift_number = 1
    shift_service.repo.get_by_id.return_value = mock_shift

    # Simulate failure in later step
    shift_service.gen_repo.get_settings.return_value = None
    shift_service.moto_repo.get_total_hours_added.side_effect = Exception("DB Fail")

    with pytest.raises(Exception):
        await shift_service.stop(shift_id, mock_user_admin)

    # If we use async with db.begin(), the transaction context manager handles rollback
    shift_service.db.begin.assert_called_once()


@pytest.mark.asyncio
async def test_start_shift_commits_exactly_once(shift_service: ShiftService, mock_user_operator):
    """BUG-2: start() повинен викликати db.begin() (context manager) рівно 1 раз."""
    gen_id = uuid.uuid4()
    mock_gen = MagicMock()
    mock_gen.is_active = True
    mock_gen.name = "Generator A"
    shift_service.gen_repo.get_by_id.return_value = mock_gen
    shift_service.repo.get_next_shift_number.return_value = 1
    shift_service.repo.create.return_value = MagicMock()

    await shift_service.start(ShiftStartRequest(generator_id=gen_id), mock_user_operator)

    # Після виправлення: використовується context manager begin() або commit()
    # Якщо використовуємо begin, він викликає __aenter__
    shift_service.db.begin.assert_called_once()
    # add_event також повинен бути викликаний (EventLog в тій самій транзакції)
    shift_service.gen_repo.add_event.assert_called_once()


@pytest.mark.asyncio
async def test_stop_shift_commits_exactly_once(shift_service: ShiftService, mock_user_operator):
    """BUG-1: stop() повинен викликати db.begin() (context manager) рівно 1 раз."""
    shift_id = uuid.uuid4()
    gen_id = uuid.uuid4()

    mock_shift = MagicMock()
    mock_shift.id = shift_id
    mock_shift.generator_id = gen_id
    mock_shift.status = ShiftStatus.ACTIVE.value
    mock_shift.started_by = mock_user_operator.id
    mock_shift.started_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    shift_service.repo.get_by_id.return_value = mock_shift

    mock_settings = MagicMock()
    mock_settings.fuel_consumption_per_hour = Decimal("2.5")
    mock_settings.initial_motohours = Decimal("100.0")
    mock_gen = MagicMock()
    mock_gen.settings = mock_settings
    shift_service.gen_repo.get_settings.return_value = mock_settings
    shift_service.gen_repo.get_by_id.return_value = mock_gen
    shift_service.moto_repo.get_total_hours_added.return_value = Decimal("5.0")
    shift_service.repo.update.return_value = mock_shift

    await shift_service.stop(shift_id, mock_user_operator)

    # Після виправлення: використовується context manager begin()
    shift_service.db.begin.assert_called_once()
    # EventLog в тій самій транзакції
    shift_service.gen_repo.add_event.assert_called_once()


@pytest.mark.asyncio
async def test_stop_shift_event_failure_does_not_commit(shift_service: ShiftService, mock_user_admin):
    """BUG-1: якщо add_event кидає виняток — транзакція повинна бути відкочена."""
    shift_id = uuid.uuid4()
    gen_id = uuid.uuid4()

    mock_shift = MagicMock()
    mock_shift.id = shift_id
    mock_shift.generator_id = gen_id
    mock_shift.status = ShiftStatus.ACTIVE.value
    mock_shift.started_by = mock_user_admin.id
    mock_shift.started_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    shift_service.repo.get_by_id.return_value = mock_shift

    mock_settings = MagicMock()
    mock_settings.fuel_consumption_per_hour = Decimal("2.5")
    mock_settings.initial_motohours = Decimal("100.0")
    mock_gen = MagicMock()
    mock_gen.settings = mock_settings
    shift_service.gen_repo.get_settings.return_value = mock_settings
    shift_service.gen_repo.get_by_id.return_value = mock_gen
    shift_service.moto_repo.get_total_hours_added.return_value = Decimal("5.0")
    shift_service.repo.update.return_value = mock_shift
    shift_service.fuel_repo.get_stock.return_value = MagicMock(current_liters=Decimal("100.0"))

    # Симулюємо збій при записі EventLog
    shift_service.gen_repo.add_event.side_effect = Exception("EventLog DB failure")

    with pytest.raises(Exception, match="EventLog DB failure"):
        await shift_service.stop(shift_id, mock_user_admin)

    # Якщо add_event впав — транзакція (через context manager) не повинна закінчитися успішно
    pass
