import asyncio
import asyncpg
import os
import sys

async def wait_for_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set")
        sys.exit(1)
    
    print("Waiting for database...")
    for _ in range(30):
        try:
            conn = await asyncpg.connect(database_url)
            await conn.close()
            print("Database ready")
            return
        except Exception as e:
            print(f"Retry in 1 second... ({e})")
            await asyncio.sleep(1)
    print("Database not ready after 30 seconds")
    sys.exit(1)

if __name__ == "__main__":
    asyncio.run(wait_for_db())