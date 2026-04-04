"""
Генерація місячного звіту у форматі .xlsx
Три аркуші:
  1. «Операційний журнал» — деталізація по зміні/добі
  2. «Зведення місяця»    — ключові показники + денна таблиця
  3. «Технічне обслуговування» — журнал ТО та залишок ресурсу
"""
from __future__ import annotations

import calendar
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from sqlalchemy.ext.asyncio import AsyncSession

# ─── палітра ────────────────────────────────────────────────
C_HEADER_DARK  = "1F3864"
C_HEADER_MID   = "2E75B6"
C_HEADER_LIGHT = "BDD7EE"
C_TOTAL_ROW    = "D9E1F2"
C_ALT_ROW      = "EBF3FB"
C_WEEKEND      = "FFF2CC"
C_WHITE        = "FFFFFF"

FONT_WHITE = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
FONT_BOLD  = Font(name="Calibri", bold=True, size=10)
FONT_REG   = Font(name="Calibri", size=10)
FONT_SMALL = Font(name="Calibri", size=9)

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
RIGHT  = Alignment(horizontal="right",  vertical="center")

THIN   = Side(style="thin")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

UA_DAYS   = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
UA_MONTHS = [
    "", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень",
]


def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def _border_cell(ws, row: int, col: int,
                value: Any = None,
                font=None, align=None, fill=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.border = BORDER
    if font:  cell.font      = font
    if align: cell.alignment = align
    if fill:  cell.fill      = fill
    return cell


# ═══════════════════════════════════════════════════════════
#  АРКУШ 1 — Операційний журнал
# ═══════════════════════════════════════════════════════════
def _build_journal(ws, generator, year: int, month: int, days_data: list[dict]) -> None:
    month_name    = UA_MONTHS[month]
    days_in_month = calendar.monthrange(year, month)[1]
    generated_at  = datetime.now().strftime("%d.%m.%Y %H:%M")
    ws.title = "Операційний журнал"

    ws.merge_cells("A1:R1")
    c = ws["A1"]
    c.value = (f"Операційний журнал роботи генератора "
               f"«{generator.name}» — {month_name} {year}")
    c.font  = Font(name="Calibri", bold=True, color="FFFFFF", size=13)
    c.fill  = _fill(C_HEADER_DARK)
    c.alignment = CENTER
    ws.row_dimensions[1].height = 28

    meta = [
        (f"Генератор: «{generator.name}»", 4),
        (f"Місяць: {month_name} {year}",   4),
        (f"Сформовано: {generated_at}",    5),
        (f"Рядків: {days_in_month}",       5),
    ]
    col = 1
    for text, span in meta:
        ws.merge_cells(start_row=2, start_column=col,
                       end_row=2, end_column=col + span - 1)
        c = ws.cell(row=2, column=col, value=text)
        c.font  = Font(name="Calibri", bold=True, color="FFFFFF", size=9)
        c.fill  = _fill(C_HEADER_MID)
        c.alignment = CENTER
        c.border = BORDER
        col += span
    ws.row_dimensions[2].height = 20

    groups = [
        (1,  2,  ""),
        (3,  3,  ""),
        (4,  5,  "РАНОК"),
        (6,  7,  "ДЕНЬ"),
        (8,  9,  "ВЕЧІР"),
        (10, 11, "ВИРОБІТОК"),
        (12, 16, "ПАЛИВО"),
        (17, 18, "ДОКУМЕНТИ"),
    ]
    for sc, ec, label in groups:
        ws.merge_cells(start_row=3, start_column=sc, end_row=3, end_column=ec)
        c = ws.cell(row=3, column=sc, value=label)
        c.font = FONT_WHITE; c.fill = _fill(C_HEADER_MID)
        c.alignment = CENTER; c.border = BORDER
    ws.row_dimensions[3].height = 18

    headers = [
        "#", "Дата", "День",
        "Р↑ Поч.", "Р↓ Кін.",
        "Д↑ Поч.", "Д↓ Кін.",
        "В↑ Поч.", "В↓ Кін.",
        "Год.", "Оператор",
        "Пал.⬆, л", "Пал.⬇, л", "Витрата, л", "Заправка, л", "л/год",
        "Чек #", "Примітки",
    ]
    for col_idx, h in enumerate(headers, 1):
        c = _border_cell(ws, 4, col_idx, h, align=CENTER, fill=_fill(C_HEADER_LIGHT))
        c.font = Font(name="Calibri", bold=True, color="1F3864", size=9)
    ws.row_dimensions[4].height = 30

    widths = [4, 12, 5, 8, 8, 8, 8, 8, 8, 7, 16, 9, 9, 10, 10, 7, 8, 20]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    totals = {"hours": timedelta(), "fuel_consumed": 0.0, "fuel_refill": 0.0}

    for row_idx, day in enumerate(days_data, 5):
        d = day["date"]
        is_weekend = d.weekday() >= 5
        row_fill = _fill(C_WEEKEND if is_weekend else
                         (C_ALT_ROW if row_idx % 2 == 0 else C_WHITE))

        shifts: list[dict] = day.get("shifts", [])

        def _moto(period: str, side: str) -> str:
            s = next((s for s in shifts if s.get("period") == period), None)
            if not s:
                return "—"
            val = s.get(f"moto_{side}")
            return f"{val:.1f}" if val is not None else "—"

        total_hours = day.get("total_hours")
        hours_str = (str(timedelta(seconds=int(total_hours * 3600)))
                     if total_hours else "")

        operator   = day.get("operators", "—")
        fuel_start = day.get("fuel_start")
        fuel_end   = day.get("fuel_end")
        consumed   = day.get("fuel_consumed")
        refill     = day.get("fuel_refill", 0.0)
        lph = (consumed / total_hours
               if consumed and total_hours and total_hours > 0 else None)

        row_values = [
            row_idx - 4,
            d.strftime("%d.%m.%Y"),
            UA_DAYS[d.weekday()],
            _moto("morning", "start"), _moto("morning", "end"),
            _moto("day",     "start"), _moto("day",     "end"),
            _moto("evening", "start"), _moto("evening", "end"),
            hours_str,
            operator,
            f"{fuel_start:.1f}" if fuel_start is not None else "129.0",
            f"{fuel_end:.1f}"   if fuel_end   is not None else "129.0",
            f"{consumed:.1f}"   if consumed   is not None else "",
            f"{refill:.1f}"     if refill               else "",
            f"{lph:.2f}"        if lph                  else "",
            "",
            "—",
        ]

        for col_idx, val in enumerate(row_values, 1):
            _border_cell(ws, row_idx, col_idx, val,
                         font=FONT_SMALL, align=CENTER, fill=row_fill)

        if total_hours:
            totals["hours"] += timedelta(seconds=int(total_hours * 3600))
        totals["fuel_consumed"] += consumed or 0
        totals["fuel_refill"]   += refill   or 0

    total_row = 5 + days_in_month
    ws.merge_cells(start_row=total_row, start_column=1,
                   end_row=total_row, end_column=9)
    c = ws.cell(row=total_row, column=1, value="ПІДСУМОК МІСЯЦЯ")
    c.font = FONT_BOLD; c.fill = _fill(C_TOTAL_ROW)
    c.alignment = CENTER; c.border = BORDER

    hours_total = str(totals["hours"]) if totals["hours"] else "0:00"
    _border_cell(ws, total_row, 10, hours_total,
                 font=FONT_BOLD, align=CENTER, fill=_fill(C_TOTAL_ROW))
    for col in range(11, 14):
        _border_cell(ws, total_row, col, "",
                     font=FONT_BOLD, align=CENTER, fill=_fill(C_TOTAL_ROW))
    _border_cell(ws, total_row, 14, f"{totals['fuel_consumed']:.1f}",
                 font=FONT_BOLD, align=CENTER, fill=_fill(C_TOTAL_ROW))
    _border_cell(ws, total_row, 15, f"{totals['fuel_refill']:.1f}",
                 font=FONT_BOLD, align=CENTER, fill=_fill(C_TOTAL_ROW))
    for col in range(16, 19):
        _border_cell(ws, total_row, col, "",
                     font=FONT_BOLD, align=CENTER, fill=_fill(C_TOTAL_ROW))

    ws.freeze_panes = "A5"


# ═══════════════════════════════════════════════════════════
#  АРКУШ 2 — Зведення місяця
# ═══════════════════════════════════════════════════════════
def _build_summary(ws, generator, year: int, month: int,
                   days_data: list[dict], fuel_price: float) -> None:
    ws.title      = "Зведення місяця"
    month_name    = UA_MONTHS[month]
    days_in_month = calendar.monthrange(year, month)[1]
    generated_at  = datetime.now().strftime("%d.%m.%Y %H:%M")

    ws.merge_cells("A1:H1")
    c = ws["A1"]
    c.value = f"Зведення місяця — «{generator.name}» — {month_name} {year}"
    c.font  = Font(name="Calibri", bold=True, color="FFFFFF", size=13)
    c.fill  = _fill(C_HEADER_DARK); c.alignment = CENTER
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:H2")
    c = ws["A2"]
    c.value = f"Сформовано: {generated_at}"
    c.font  = Font(name="Calibri", bold=True, color="FFFFFF", size=9)
    c.fill  = _fill(C_HEADER_MID); c.alignment = CENTER; c.border = BORDER

    ws.merge_cells("A3:H3")
    c = ws["A3"]
    c.value = "Ключові показники"
    c.font  = FONT_WHITE; c.fill = _fill(C_HEADER_MID)
    c.alignment = CENTER; c.border = BORDER

    total_hours    = sum(d.get("total_hours") or 0 for d in days_data)
    working_days   = sum(1 for d in days_data if d.get("total_hours"))
    weekend_count  = sum(1 for d in days_data if d["date"].weekday() >= 5)
    total_consumed = sum(d.get("fuel_consumed") or 0 for d in days_data)
    total_refill   = sum(d.get("fuel_refill")   or 0 for d in days_data)
    avg_lph   = total_consumed / total_hours if total_hours > 0 else 0
    fuel_cost = total_consumed * fuel_price

    kpis = [
        ("Мотогодини за місяць",    f"{total_hours:.2f} год"),
        ("Робочих днів",            f"{working_days} / {days_in_month}"),
        ("Вихідних у місяці",       str(weekend_count)),
        ("Загальна витрата палива", f"{total_consumed:.1f} л"),
        ("Загальне поповнення",     f"{total_refill:.1f} л"),
        ("Середня витрата",         f"{avg_lph:.2f} л/год"),
        ("Ціна палива",             f"{fuel_price:.2f} грн/л"),
        ("Вартість палива",         f"{fuel_cost:.0f} грн"),
    ]

    for i, (label, value) in enumerate(kpis, 4):
        row_f = _fill(C_ALT_ROW if i % 2 == 0 else C_WHITE)
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=5)
        _border_cell(ws, i, 1, label, font=FONT_BOLD, align=LEFT,   fill=row_f)
        ws.merge_cells(start_row=i, start_column=6, end_row=i, end_column=8)
        _border_cell(ws, i, 6, value, font=FONT_BOLD, align=CENTER, fill=row_f)

    header_row = len(kpis) + 5
    ws.merge_cells(start_row=header_row - 1,
                   start_column=1, end_row=header_row - 1, end_column=8)
    c = ws.cell(row=header_row - 1, column=1, value="Щоденна зведена таблиця")
    c.font = FONT_WHITE; c.fill = _fill(C_HEADER_MID)
    c.alignment = CENTER; c.border = BORDER

    day_headers = ["Дата", "День", "Год.", "Пал.⬆, л", "Пал.⬇, л",
                   "Витрата, л", "Заправка, л", "Примітки"]
    for col_idx, h in enumerate(day_headers, 1):
        c = _border_cell(ws, header_row, col_idx, h, align=CENTER,
                         fill=_fill(C_HEADER_LIGHT))
        c.font = Font(name="Calibri", bold=True, color="1F3864", size=9)

    for row_idx, day in enumerate(days_data, header_row + 1):
        d = day["date"]
        is_weekend = d.weekday() >= 5
        row_fill = _fill(C_WEEKEND if is_weekend else
                         (C_ALT_ROW if row_idx % 2 == 0 else C_WHITE))
        total_h  = day.get("total_hours")
        hours_str = (str(timedelta(seconds=int(total_h * 3600)))
                     if total_h else "")
        fs  = day.get("fuel_start")
        fe  = day.get("fuel_end")
        con = day.get("fuel_consumed")
        ref = day.get("fuel_refill", 0.0)
        row_vals = [
            d.strftime("%d.%m.%Y"),
            UA_DAYS[d.weekday()],
            hours_str,
            f"{fs:.1f}"  if fs  is not None else "129.0",
            f"{fe:.1f}"  if fe  is not None else "129.0",
            f"{con:.1f}" if con is not None else "",
            f"{ref:.1f}" if ref             else "",
            "—",
        ]
        for col_idx, val in enumerate(row_vals, 1):
            _border_cell(ws, row_idx, col_idx, val,
                         font=FONT_SMALL, align=CENTER, fill=row_fill)

    for i, w in enumerate([12, 5, 8, 10, 10, 11, 12, 20], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = f"A{header_row + 1}"


# ═══════════════════════════════════════════════════════════
#  АРКУШ 3 — Технічне обслуговування
# ═══════════════════════════════════════════════════════════
def _build_maintenance(ws, generator,
                       moto_total: float,
                       oil_remaining: float,
                       spark_remaining: float,
                       maintenance_logs: list) -> None:
    ws.title = "Технічне обслуговування"

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = f"Технічне обслуговування — «{generator.name}»"
    c.font  = Font(name="Calibri", bold=True, color="FFFFFF", size=13)
    c.fill  = _fill(C_HEADER_DARK); c.alignment = CENTER
    ws.row_dimensions[1].height = 28

    meta = [
        ("Мотогодини (загалом):",  f"{moto_total:.1f} год"),
        ("До заміни мастила:",     f"{max(oil_remaining,   0):.0f} год"),
        ("До заміни свічок:",      f"{max(spark_remaining, 0):.0f} год"),
    ]
    for i, (label, val) in enumerate(meta, 2):
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3)
        _border_cell(ws, i, 1, label, font=FONT_BOLD, align=LEFT,   fill=_fill(C_ALT_ROW))
        ws.merge_cells(start_row=i, start_column=4, end_row=i, end_column=6)
        _border_cell(ws, i, 4, val,   font=FONT_BOLD, align=CENTER, fill=_fill(C_ALT_ROW))

    header_row = len(meta) + 3
    heads  = ["Дата", "Тип ТО", "Мотогодини", "Виконав", "Примітки"]
    widths = [18, 18, 14, 22, 30]
    for col_idx, (h, w) in enumerate(zip(heads, widths), 1):
        c = _border_cell(ws, header_row, col_idx, h,
                         align=CENTER, fill=_fill(C_HEADER_LIGHT))
        c.font = Font(name="Calibri", bold=True, color="1F3864", size=9)
        ws.column_dimensions[get_column_letter(col_idx)].width = w

    for row_idx, log in enumerate(maintenance_logs, header_row + 1):
        row_fill = _fill(C_ALT_ROW if row_idx % 2 == 0 else C_WHITE)
        vals = [
            log.performed_at.strftime("%Y-%m-%d %H:%M:%S") if log.performed_at else "",
            log.maintenance_type or "",
            f"{log.motohours_at:.1f} год" if log.motohours_at else "",
            log.performed_by or "",
            log.notes or "",
        ]
        for col_idx, val in enumerate(vals, 1):
            _border_cell(ws, row_idx, col_idx, val,
                         font=FONT_SMALL, align=LEFT, fill=row_fill)

    ws.freeze_panes = f"A{header_row + 1}"


# ═══════════════════════════════════════════════════════════
#  ГОЛОВНА ФУНКЦІЯ
# ═══════════════════════════════════════════════════════════
async def generate_monthly_report(
    db: AsyncSession,
    generator_id: uuid.UUID,
    year: int,
    month: int,
    fuel_price: float = 50.0,
) -> bytes:
    from sqlalchemy import select, and_, func
    from app.modules.motohours.models import MotohoursLog, MaintenanceLog
    from app.modules.fuel.models import FuelRefill
    from app.modules.generators.models import Generator, GeneratorSettings
    from app.modules.shifts.models import Shift
    from app.modules.users.models import User

    # 1. генератор
    gen = await db.get(Generator, generator_id)
    if not gen:
        raise ValueError(f"Generator {generator_id} not found")

    # 2. зміни за місяць
    month_start   = date(year, month, 1)
    days_in_month = calendar.monthrange(year, month)[1]
    month_end     = date(year, month, days_in_month)

    shifts_result = await db.execute(
        select(Shift, User.full_name.label("operator_name"))
        .join(User, Shift.user_id == User.id, isouter=True)
        .where(
            and_(
                Shift.generator_id == generator_id,
                func.date(Shift.started_at) >= month_start,
                func.date(Shift.started_at) <= month_end,
            )
        )
        .order_by(Shift.started_at)
    )
    shifts_rows = shifts_result.all()

    # 3. заправки за місяць
    refills_result = await db.execute(
        select(FuelRefill)
        .where(
            and_(
                FuelRefill.generator_id == generator_id,
                func.date(FuelRefill.created_at) >= month_start,
                func.date(FuelRefill.created_at) <= month_end,
            )
        )
    )
    refills = refills_result.scalars().all()

    # 4. останнє значення мотогодин
    moto_result = await db.execute(
        select(MotohoursLog)
        .where(MotohoursLog.generator_id == generator_id)
        .order_by(MotohoursLog.created_at.desc())
        .limit(1)
    )
    last_moto  = moto_result.scalar_one_or_none()
    moto_total = float(last_moto.total_hours) if last_moto else 0.0

    # 5. налаштування ТО
    settings_result = await db.execute(
        select(GeneratorSettings)
        .where(GeneratorSettings.generator_id == generator_id)
    )
    gen_settings   = settings_result.scalar_one_or_none()
    # використовуємо to_interval_hours або значення за замовчуванням
    oil_interval   = float(gen_settings.to_interval_hours)   if gen_settings and gen_settings.to_interval_hours   else 50.0
    spark_interval = float(gen_settings.to_interval_hours)   if gen_settings and gen_settings.to_interval_hours   else 100.0

    # 6. журнал ТО
    maintenance_result = await db.execute(
        select(MaintenanceLog)
        .where(MaintenanceLog.generator_id == generator_id)
        .order_by(MaintenanceLog.performed_at.desc())
    )
    maintenance_logs = maintenance_result.scalars().all()

    # 7. залишок до ТО
    last_oil   = next((m for m in maintenance_logs
                       if m.maintenance_type in ("oil_change", "Заміна мастила")), None)
    last_spark = next((m for m in maintenance_logs
                       if m.maintenance_type in ("spark_change", "Заміна свічок")), None)
    oil_remaining   = oil_interval   - (moto_total - (float(last_oil.motohours_at)   if last_oil   else 0))
    spark_remaining = spark_interval - (moto_total - (float(last_spark.motohours_at) if last_spark else 0))

    # 8. щоденні дані
    def _period(shift: Shift) -> str:
        h = shift.started_at.hour
        if 5 <= h < 12:  return "morning"
        if 12 <= h < 18: return "day"
        return "evening"

    shifts_by_date: dict[date, list] = defaultdict(list)
    for shift, op_name in shifts_rows:
        shifts_by_date[shift.started_at.date()].append((shift, op_name))

    refills_by_date: dict[date, float] = defaultdict(float)
    for r in refills:
        refills_by_date[r.created_at.date()] += float(r.amount_liters)

    days_data: list[dict] = []
    for day_num in range(1, days_in_month + 1):
        d = date(year, month, day_num)
        day_shifts_raw = shifts_by_date.get(d, [])

        shifts_list: list[dict] = []
        total_hours    = 0.0
        operators_set: list[str] = []
        fuel_start_val = None
        fuel_end_val   = None
        fuel_consumed  = 0.0

        for shift, op_name in day_shifts_raw:
            dur = 0.0
            if shift.stopped_at:
                dur = (shift.stopped_at - shift.started_at).total_seconds() / 3600
            total_hours += dur

            moto_start = float(shift.motohours_start) if shift.motohours_start else None
            moto_end   = float(shift.motohours_end)   if shift.motohours_end   else None
            fs = float(shift.fuel_level_start) if shift.fuel_level_start else None
            fe = float(shift.fuel_level_end)   if shift.fuel_level_end   else None
            cons = (fs - fe) if fs is not None and fe is not None else None

            shifts_list.append({
                "period":     _period(shift),
                "moto_start": moto_start,
                "moto_end":   moto_end,
            })
            if op_name and op_name not in operators_set:
                operators_set.append(op_name)
            if fuel_start_val is None and fs is not None:
                fuel_start_val = fs
            if fe is not None:
                fuel_end_val = fe
            if cons:
                fuel_consumed += cons

        refill_val = refills_by_date.get(d, 0.0)

        days_data.append({
            "date":          d,
            "shifts":        shifts_list,
            "total_hours":   total_hours if total_hours > 0 else None,
            "operators":     ", ".join(operators_set) if operators_set else "—",
            "fuel_start":    fuel_start_val,
            "fuel_end":      fuel_end_val,
            "fuel_consumed": fuel_consumed if fuel_consumed > 0 else None,
            "fuel_refill":   refill_val    if refill_val   > 0 else None,
        })

    # 9. збираємо книгу
    wb  = Workbook()
    ws1 = wb.active
    _build_journal(ws1, gen, year, month, days_data)
    ws2 = wb.create_sheet()
    _build_summary(ws2, gen, year, month, days_data, fuel_price)
    ws3 = wb.create_sheet()
    _build_maintenance(ws3, gen, moto_total,
                       oil_remaining, spark_remaining, maintenance_logs)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
