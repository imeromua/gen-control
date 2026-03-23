from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin_or_operator
from app.modules.dashboard.schemas import DashboardResponse, DashboardSummaryResponse
from app.modules.dashboard.service import DashboardService
from app.modules.users.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    return await service.get_dashboard()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    return await service.get_summary()
