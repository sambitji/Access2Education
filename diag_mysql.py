import asyncio
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

from Backend.database.db import connect_db, engine, Base

async def check():
    print("Testing MySQL Connectivity and Table Creation...")
    try:
        await connect_db()
        print("MySQL Connectivity: OK")
        
        # Check if tables exist
        from sqlalchemy import inspect
        def get_tables(conn):
            return inspect(conn).get_table_names()
        
        async with engine.connect() as conn:
            tables = await conn.run_sync(get_tables)
            print(f"Tables found: {tables}")
            
    except Exception as e:
        print(f"MySQL Diagnostic FAIL: {e}")
    finally:
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(check())
