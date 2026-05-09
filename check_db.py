import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['edu_platform']
    count = await db['users'].count_documents({})
    print(f"User Count: {count}")
    
    users = await db['users'].find().to_list(10)
    for u in users:
        print(f"- {u['email']} ({u['role']})")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(check())
