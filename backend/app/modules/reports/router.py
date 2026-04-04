from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly")
async def download_monthly_report(
    generator_id: int = Query(...),
    year:         int = Query(..., ge=2020, le=2100),
    month:        int = Query(..., ge=1,    le=12),
    fuel_price:   float = Query(50.0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user = Depends(get_current_user),
):
    """Генерує та повертає .xlsx звіт за місяць."""
    from app.modules.reports.service import generate_monthly_report

    xlsx_bytes = await generate_monthly_report(
        db=db,
        generator_id=generator_id,
        year=year,
        month=month,
        fuel_price=fuel_price,
    )

    filename = f"report_{generator_id}_{year}_{month:02d}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
