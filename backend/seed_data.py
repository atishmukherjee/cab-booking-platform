import asyncio
from app.core.db import async_engine
from app.models.ride import User, Driver
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

async def seed():
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 1. Dummy Rider
        rider = User(name="Rahul Sharma", email="rahul@example.com", phone="9876543210", role="rider")
        session.add(rider)
        await session.flush()

        # 2. Dummy Driver 1 (~1.2 km door)
        driver_user1 = User(name="Amit Verma", email="amit@example.com", phone="9876543211", role="driver")
        session.add(driver_user1)
        await session.flush()
        driver1 = Driver(
            user_id=driver_user1.id,
            vehicle_info="Maruti Swift - CG 04 AB 1234",
            is_active=True,
            current_location="SRID=4326;POINT(81.6350 21.2550)"
        )
        session.add(driver1)

        # 3. Dummy Driver 2 (~3.5 km door)
        driver_user2 = User(name="Suresh Kumar", email="suresh@example.com", phone="9876543212", role="driver")
        session.add(driver_user2)
        await session.flush()
        driver2 = Driver(
            user_id=driver_user2.id,
            vehicle_info="Hyundai i20 - CG 04 XY 9876",
            is_active=True,
            current_location="SRID=4326;POINT(81.6500 21.2400)"
        )
        session.add(driver2)

        # 4. Dummy Driver 3 (Bahut door - 25 km door, filter test ke liye)
        driver_user3 = User(name="Vikas Singh", email="vikas@example.com", phone="9876543213", role="driver")
        session.add(driver_user3)
        await session.flush()
        driver3 = Driver(
            user_id=driver_user3.id,
            vehicle_info="Tata Nexon - CG 04 CD 5555",
            is_active=True,
            current_location="SRID=4326;POINT(81.8500 21.4000)"
        )
        session.add(driver3)

        await session.commit()
        print("Test data seeded successfully!")
        print(f"Rider ID for testing: {rider.id}")

if __name__ == "__main__":
    asyncio.run(seed())
