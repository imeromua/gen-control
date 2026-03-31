import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.dashboard.service import DashboardService


@pytest.fixture
def dashboard_service():
    mock_db = AsyncMock()
    service = DashboardService(mock_db)
    
    # Mocking all 8 repositories
    service.shift_repo = AsyncMock()
    service.gen_repo = AsyncMock()
    service.moto_repo = AsyncMock()
    service.fuel_repo = AsyncMock()
    service.oil_repo = AsyncMock()
    service.outage_repo = AsyncMock()
    service.user_repo = AsyncMock()
    service.dash_repo = AsyncMock()
    
    return service


@pytest.mark.asyncio
async def test_get_summary_no_active_operations(dashboard_service: DashboardService):
    dashboard_service.shift_repo.get_any_active.return_value = None
    dashboard_service.fuel_repo.get_stock.return_value = None
    dashboard_service.outage_repo.get_next.return_value = None
    
    summary = await dashboard_service.get_summary()
    
    assert summary.generator_is_running is False
    assert summary.active_shift_number is None
    assert summary.fuel_stock_liters is None
    assert summary.fuel_warning_active is False
    assert summary.next_outage_date is None


@pytest.mark.asyncio
async def test_get_summary_with_active_shift(dashboard_service: DashboardService):
    from datetime import datetime, timedelta, timezone
    
    now = datetime.now(tz=timezone.utc)
    mock_shift = MagicMock()
    mock_shift.shift_number = 101
    mock_shift.started_at = now - timedelta(minutes=45)
    
    dashboard_service.shift_repo.get_any_active.return_value = mock_shift
    dashboard_service.fuel_repo.get_stock.return_value = None
    dashboard_service.outage_repo.get_next.return_value = None
    
    summary = await dashboard_service.get_summary()
    
    assert summary.generator_is_running is True
    assert summary.active_shift_number == 101
    assert 44.0 <= summary.active_shift_duration_minutes <= 46.0


@pytest.mark.asyncio
async def test_get_summary_fuel_warning(dashboard_service: DashboardService):
    dashboard_service.shift_repo.get_any_active.return_value = None
    dashboard_service.outage_repo.get_next.return_value = None
    
    mock_stock = MagicMock()
    mock_stock.current_liters = Decimal("15.0")
    mock_stock.warning_level_liters = Decimal("20.0")
    dashboard_service.fuel_repo.get_stock.return_value = mock_stock
    
    summary = await dashboard_service.get_summary()
    
    assert summary.fuel_stock_liters == Decimal("15.0")
    assert summary.fuel_warning_active is True

