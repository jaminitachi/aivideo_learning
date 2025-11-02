from prisma import Prisma
from typing import Optional

# Prisma client instance
db: Optional[Prisma] = None


async def connect_db():
    """Connect to the database"""
    global db
    db = Prisma()
    await db.connect()
    print("Database connected successfully")


async def disconnect_db():
    """Disconnect from the database"""
    global db
    if db:
        await db.disconnect()
        print("Database disconnected")


def get_db() -> Prisma:
    """Get database instance"""
    if db is None:
        raise Exception("Database not connected")
    return db
