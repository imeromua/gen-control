import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.generators.models import EventLog, Generator, GeneratorSettings


class GeneratorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Generator]:
        result = await self.db.execute(
            select(Generator).options(selectinload(Generator.settings)).order_by(Generator.created_at)
        )
        return list(result.scalars().all())

    async def get_by_id(self, generator_id: uuid.UUID) -> Generator | None:
        result = await self.db.execute(
            select(Generator)
            .options(selectinload(Generator.settings))
            .where(Generator.id == generator_id)
        )
        return result.scalar_one_or_none()

    async def create(self, generator: Generator) -> Generator:
        self.db.add(generator)
        await self.db.commit()
        await self.db.refresh(generator)
        return await self.get_by_id(generator.id)

    async def update(self, generator: Generator) -> Generator:
        await self.db.commit()
        await self.db.refresh(generator)
        return await self.get_by_id(generator.id)

    async def get_settings(self, generator_id: uuid.UUID) -> GeneratorSettings | None:
        result = await self.db.execute(
            select(GeneratorSettings).where(GeneratorSettings.generator_id == generator_id)
        )
        return result.scalar_one_or_none()

    async def update_settings(self, settings: GeneratorSettings) -> GeneratorSettings:
        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def add_event(self, event: EventLog) -> None:
        self.db.add(event)
        await self.db.commit()
