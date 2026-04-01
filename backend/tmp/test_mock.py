import asyncio
from unittest.mock import AsyncMock, MagicMock

async def main():
    # Case 1: mock_db is AsyncMock
    mock_db = AsyncMock()
    # mock_db.begin is now an AsyncMock
    # If we do nothing, mock_db.begin() returns a Coroutine
    try:
        async with mock_db.begin():
            print("Case 1 success")
    except Exception as e:
        print(f"Case 1 fail: {type(e).__name__}: {e}")

    # Case 2: mock_db.begin is MagicMock returning AsyncMock
    mock_db_2 = AsyncMock()
    mock_db_2.begin = MagicMock(return_value=AsyncMock())
    try:
        async with mock_db_2.begin():
            print("Case 2 success")
    except Exception as e:
        print(f"Case 2 fail: {type(e).__name__}: {e}")

    # Case 3: mock_db.begin is MagicMock with manual __aenter__
    mock_db_3 = AsyncMock()
    mock_db_3.begin = MagicMock()
    mock_db_3.begin.return_value.__aenter__ = AsyncMock()
    mock_db_3.begin.return_value.__aexit__ = AsyncMock()
    try:
        async with mock_db_3.begin():
            print("Case 3 success")
    except Exception as e:
        print(f"Case 3 fail: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
