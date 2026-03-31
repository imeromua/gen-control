import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import ConflictException, NotFoundException
from app.modules.fuel.schemas import FuelDeliveryCreate, FuelRefillCreate
from app.modules.fuel.service import FuelService


@pytest.fixture
def fuel_service():
    mock_db = AsyncMock()
    service = FuelService(mock_db)
    
    # Mocking repositories and rules service
    service.repo = AsyncMock()
    service.gen_repo = AsyncMock()
    service.shift_repo = AsyncMock()
    service.rules = AsyncMock()
    
    return service

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    return user


@pytest.mark.asyncio
async def test_create_delivery_success(fuel_service: FuelService, mock_user):
    # Setup mock stock
    mock_stock = MagicMock()
    mock_stock.current_liters = Decimal("100.0")
    mock_stock.max_limit_liters = Decimal("200.0")
    mock_stock.fuel_type = "A95"
    fuel_service.repo.get_stock.return_value = mock_stock
    
    delivery_data = FuelDeliveryCreate(
        liters=Decimal("50.0"),
        check_number="12345",
        delivered_by_name="Ivan"
    )
    
    # Call
    result = await fuel_service.create_delivery(delivery_data, mock_user)
    
    # Assert checks
    fuel_service.rules.check_working_hours.assert_called_once()
    assert result.liters == Decimal("50.0")
    assert result.stock_before == Decimal("100.0")
    assert result.stock_after == Decimal("150.0")
    
    # Assert DB operations
    assert fuel_service.db.add.call_count == 2  # Delivery and EventLog
    fuel_service.db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_delivery_exceeds_limit(fuel_service: FuelService, mock_user):
    mock_stock = MagicMock()
    mock_stock.current_liters = Decimal("180.0")
    mock_stock.max_limit_liters = Decimal("200.0")
    fuel_service.repo.get_stock.return_value = mock_stock
    
    # Trying to add 50 to 180 (Limit is 200)
    delivery_data = FuelDeliveryCreate(
        liters=Decimal("50.0"),
        check_number="12345",
        delivered_by_name="Ivan"
    )
    
    with pytest.raises(ConflictException) as excinfo:
        await fuel_service.create_delivery(delivery_data, mock_user)
        
    assert "Перевищення ліміту складу" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_create_refill_during_active_shift(fuel_service: FuelService, mock_user):
    # Setup active shift existing
    fuel_service.shift_repo.get_active_for_generator.return_value = MagicMock()
    
    refill_data = FuelRefillCreate(
        generator_id=uuid.uuid4(),
        liters=Decimal("20.0"),
        tank_level_before=Decimal("10.0")
    )
    
    with pytest.raises(ConflictException) as excinfo:
        await fuel_service.create_refill(refill_data, mock_user)
        
    assert "Заправка під час роботи заборонена" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_create_refill_insufficient_stock(fuel_service: FuelService, mock_user):
    fuel_service.shift_repo.get_active_for_generator.return_value = None
    
    mock_stock = MagicMock()
    mock_stock.current_liters = Decimal("10.0") # We have 10, want 20
    fuel_service.repo.get_stock.return_value = mock_stock
    
    refill_data = FuelRefillCreate(
        generator_id=uuid.uuid4(),
        liters=Decimal("20.0"),
        tank_level_before=Decimal("10.0")
    )
    
    with pytest.raises(ConflictException) as excinfo:
        await fuel_service.create_refill(refill_data, mock_user)
        
    assert "Недостатньо палива на складі" in str(excinfo.value.detail)

