import calendar
from datetime import date, datetime, timezone
from io import BytesIO

import uuid
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin_or_operator
from app.modules.reports.service import ReportService
from app.modules.users.models import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly")
async def monthly_report(
    generator_id: uuid.UUID = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    fuel_price: float = Query(default=50.0),
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    """Generate monthly Excel report for a generator."""
    service = ReportService(db)
    buffer: BytesIO = await service.generate_monthly_excel(
        generator_id=generator_id,
        year=year,
        month=month,
        fuel_price=fuel_price,
    )

    ua_months = ["", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
                 "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"]
    month_name = ua_months[month]
    filename = f"Zvit-{month:02d}.{year}.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
