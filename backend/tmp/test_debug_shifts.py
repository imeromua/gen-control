import uuid
import enum
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
import asyncio

class RoleName(str, enum.Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"

class ShiftStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

class ForbiddenException(Exception): pass
class ConflictException(Exception): pass

class ShiftService:
    def __init__(self, db):
        self.db = db
        self.repo = AsyncMock()
        self.gen_repo = AsyncMock()
        self.moto_repo = AsyncMock()
        self.fuel_repo = AsyncMock()
        self.rules = AsyncMock()

    async def get_by_id(self, id):
        return await self.repo.get_by_id(id)

    async def stop(self, shift_id, current_user):
        await self.rules.check_working_hours()
        shift = await self.get_by_id(shift_id)
        
        print(f"DEBUG: shift.status={shift.status}")
        print(f"DEBUG: ShiftStatus.ACTIVE.value={ShiftStatus.ACTIVE.value}")
        if shift.status != ShiftStatus.ACTIVE.value:
            raise ConflictException("Shift not active")

        print(f"DEBUG: shift.started_by={shift.started_by}")
        print(f"DEBUG: current_user.id={current_user.id}")
        print(f"DEBUG: current_user.role.name={current_user.role.name}")
        print(f"DEBUG: RoleName.ADMIN={RoleName.ADMIN}")
        
        if shift.started_by != current_user.id and current_user.role.name != RoleName.ADMIN:
            raise ForbiddenException("Forbidden")

        print("DEBUG: Reached begin()")
        async with self.db.begin():
            print("DEBUG: Inside begin()")
            await self.moto_repo.get_total_hours_added(shift.generator_id)

async def test():
    mock_db = AsyncMock()
    mock_db.begin = MagicMock(return_value=AsyncMock())
    service = ShiftService(mock_db)

    mock_user_admin = MagicMock()
    mock_user_admin.id = uuid.uuid4()
    mock_user_admin.role.name = RoleName.ADMIN.value
    
    shift_id = uuid.uuid4()
    mock_shift = MagicMock()
    mock_shift.status = ShiftStatus.ACTIVE.value
    mock_shift.started_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    mock_shift.shift_number = 1
    mock_shift.generator_id = uuid.uuid4()
    
    service.repo.get_by_id.return_value = mock_shift
    service.moto_repo.get_total_hours_added.side_effect = Exception("DB Fail")

    print("\n--- Running debug test ---")
    try:
        await service.stop(shift_id, mock_user_admin)
    except Exception as e:
        print(f"Caught expected/unexpected exception: {e}")
    
    print(f"begin call count: {mock_db.begin.call_count}")

if __name__ == "__main__":
    asyncio.run(test())
