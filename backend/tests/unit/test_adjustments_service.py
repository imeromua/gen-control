import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.enums import AdjustmentType
from app.modules.adjustments.schemas import AdjustmentCreate
from app.modules.adjustments.service import AdjustmentService


@pytest.fixture
def adj_service():
    mock_db = AsyncMock()
    mock_db.begin = MagicMock(return_value=AsyncMock())
    mock_db.add = MagicMock()
    
    service = AdjustmentService(mock_db)
    service.repo = AsyncMock()
    service.gen_repo = AsyncMock()
    service.fuel_repo = AsyncMock()
    service.oil_repo = AsyncMock()
    service.motohours_repo = AsyncMock()
    return service


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    return user


@pytest.mark.asyncio
async def test_create_adjustment_motohours_commits_exactly_once(adj_service: AdjustmentService, mock_user):
    """BUG-3: MOTOHOURS_ADJUST повинен викликати db.commit() рівно 1 раз в кінці."""
    gen_id = uuid.uuid4()

    mock_created = MagicMock()
    mock_created.id = uuid.uuid4()
    adj_service.repo.create.return_value = mock_created
    adj_service.motohours_repo.get_total_hours_added.return_value = Decimal("100.0")

    data = AdjustmentCreate(
        adjustment_type=AdjustmentType.MOTOHOURS_ADJUST,
        entity_type="generator",
        entity_id=gen_id,
        value_before=Decimal("100.0"),
        value_after=Decimal("105.0"),
        reason="Manual correction",
    )

    await adj_service.create(data, mock_user)
    
    # Після виправлення: commit рівно 1 раз в кінці (через begin)
    adj_service.db.begin.assert_called_once()
    # EventLog записаний
    adj_service.gen_repo.add_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_adjustment_fuel_commits_exactly_once(adj_service: AdjustmentService, mock_user):
    """BUG-3: FUEL_STOCK_ADJUST повинен викликати db.commit() рівно 1 раз."""
    gen_id = uuid.uuid4()

    mock_created = MagicMock()
    mock_created.id = uuid.uuid4()
    adj_service.repo.create.return_value = mock_created

    mock_stock = MagicMock()
    mock_stock.current_liters = Decimal("50.0")
    adj_service.fuel_repo.get_stock.return_value = mock_stock
    adj_service.fuel_repo.update_stock.return_value = mock_stock

    data = AdjustmentCreate(
        adjustment_type=AdjustmentType.FUEL_STOCK_ADJUST,
        entity_type="fuel_stock",
        entity_id=gen_id,
        value_before=Decimal("50.0"),
        value_after=Decimal("60.0"),
        reason="Corrected stock",
    )

    await adj_service.create(data, mock_user)

    # Після виправлення: commit рівно 1 раз (через begin)
    adj_service.db.begin.assert_called_once()
    adj_service.gen_repo.add_event.assert_called_once()


@pytest.mark.asyncio
async def test_create_adjustment_oil_commits_exactly_once(adj_service: AdjustmentService, mock_user):
    """BUG-3: OIL_STOCK_ADJUST повинен викликати db.commit() рівно 1 раз."""
    oil_id = uuid.uuid4()

    mock_created = MagicMock()
    mock_created.id = uuid.uuid4()
    adj_service.repo.create.return_value = mock_created

    mock_oil = MagicMock()
    mock_oil.current_quantity = Decimal("5.0")
    adj_service.oil_repo.get_by_id.return_value = mock_oil
    adj_service.oil_repo.update.return_value = mock_oil

    data = AdjustmentCreate(
        adjustment_type=AdjustmentType.OIL_STOCK_ADJUST,
        entity_type="oil_stock",
        entity_id=oil_id,
        value_before=Decimal("5.0"),
        value_after=Decimal("7.0"),
        reason="Corrected oil level",
    )

    await adj_service.create(data, mock_user)

    # Після виправлення: commit рівно 1 раз (через begin)
    adj_service.db.begin.assert_called_once()
    adj_service.gen_repo.add_event.assert_called_once()
