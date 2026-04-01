import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.oil.schemas import OilStockCreate, OilStockUpdate
from app.modules.oil.service import OilService


@pytest.fixture
def oil_service():
    mock_db = AsyncMock()
    mock_db.begin = MagicMock(return_value=AsyncMock())
    mock_db.add = MagicMock()
    
    service = OilService(mock_db)
    service.repo = AsyncMock()
    service.gen_repo = AsyncMock()
    return service


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    return user


@pytest.mark.asyncio
async def test_create_oil_commits_exactly_once(oil_service: OilService, mock_user):
    """create() повинен викликати db.commit() рівно 1 раз (BUG-4)."""
    gen_id = uuid.uuid4()
    mock_created = MagicMock()
    oil_service.repo.create.return_value = mock_created

    data = OilStockCreate(
        generator_id=gen_id,
        oil_type="5W-40",
        current_quantity=Decimal("3.5"),
        unit="L",
    )

    await oil_service.create(data, mock_user)
    
    # Після виправлення: commit рівно 1 раз (через begin)
    oil_service.db.begin.assert_called_once()
    oil_service.gen_repo.add_event.assert_called_once()


@pytest.mark.asyncio
async def test_update_oil_commits_exactly_once(oil_service: OilService, mock_user):
    """update() повинен викликати db.commit() рівно 1 раз (BUG-4)."""
    oil_id = uuid.uuid4()
    mock_oil = MagicMock()
    mock_oil.generator_id = uuid.uuid4()
    mock_oil.current_quantity = Decimal("3.5")
    mock_oil.unit = "L"
    oil_service.repo.get_by_id.return_value = mock_oil
    oil_service.repo.update.return_value = mock_oil

    data = OilStockUpdate(current_quantity=Decimal("4.0"))

    await oil_service.update(oil_id, data, mock_user)
    
    # Після виправлення: commit рівно 1 раз (через begin)
    oil_service.db.begin.assert_called_once()
    oil_service.gen_repo.add_event.assert_called_once()
