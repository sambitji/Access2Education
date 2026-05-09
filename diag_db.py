import asyncio
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

from Backend.database.db import connect_db, db_instance

async def check():
    print("Testing MongoDB Connectivity from Backend...")
    await connect_db()
    if db_instance.database is not None:
        try:
            await db_instance.client.admin.command("ping")
            print("MongoDB Connectivity: OK (Ping success)")
        except Exception as e:
            print(f"MongoDB Connectivity: FAIL (Ping error: {e})")
    else:
        print("MongoDB Connectivity: FAIL (Database object is None)")

if __name__ == '__main__':
    asyncio.run(check())
