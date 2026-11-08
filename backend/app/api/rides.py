import math
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.db import get_session
from app.models.ride import Ride, Driver, User

router = APIRouter(prefix="/rides", tags=["Rides"])

class EstimateRequest(BaseModel):
    pickup_lat: float
    pickup_lon: float
    drop_lat: float
    drop_lon: float

class CreateRideRequest(BaseModel):
    rider_id: uuid.UUID
    pickup_lat: float
    pickup_lon: float
    drop_lat: float
    drop_lon: float

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.post("/estimate")
async def estimate_fare(payload: EstimateRequest):
    distance_km = calculate_haversine_distance(
        payload.pickup_lat, payload.pickup_lon, payload.drop_lat, payload.drop_lon
    )
    if distance_km < 0.1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pickup aur drop location lagbhag same hain."
        )

    base_fare = 50.0
    rate_per_km = 14.0
    rate_per_min = 2.0
    duration_mins = (distance_km / 25.0) * 60.0
    total_fare = base_fare + (distance_km * rate_per_km) + (duration_mins * rate_per_min)

    return {
        "distance_km": round(distance_km, 2),
        "distance_meters": int(distance_km * 1000),
        "duration_minutes": round(duration_mins, 1),
        "duration_secs": int(duration_mins * 60),
        "fare_estimate": round(total_fare, 2)
    }

@router.post("/request", status_code=status.HTTP_201_CREATED)
async def request_ride(payload: CreateRideRequest, session: AsyncSession = Depends(get_session)):
    distance_km = calculate_haversine_distance(
        payload.pickup_lat, payload.pickup_lon, payload.drop_lat, payload.drop_lon
    )
    duration_mins = (distance_km / 25.0) * 60.0
    total_fare = 50.0 + (distance_km * 14.0) + (duration_mins * 2.0)

    pickup_wkt = f"SRID=4326;POINT({payload.pickup_lon} {payload.pickup_lat})"
    drop_wkt = f"SRID=4326;POINT({payload.drop_lon} {payload.drop_lat})"

    new_ride = Ride(
        rider_id=payload.rider_id,
        pickup_point=pickup_wkt,
        drop_point=drop_wkt,
        fare_estimate=round(total_fare, 2),
        distance_meters=int(distance_km * 1000),
        duration_secs=int(duration_mins * 60),
        status="REQUESTED"
    )

    session.add(new_ride)
    await session.commit()
    await session.refresh(new_ride)

    return {
        "message": "Ride request successfully created",
        "ride_id": new_ride.id,
        "status": new_ride.status,
        "fare_estimate": new_ride.fare_estimate
    }

@router.get("/nearby-drivers")
async def find_nearby_drivers(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    session: AsyncSession = Depends(get_session)
):
    """PostGIS ST_DWithin query ke through rider ke aas-paas active drivers dhoondhta hai."""
    radius_meters = radius_km * 1000.0

    # ST_DWithin geography casting ke saath true geodesic meter distance use karta hai
    spatial_query = text("""
        SELECT 
            d.id AS driver_id,
            u.name AS driver_name,
            d.vehicle_info,
            ST_Y(d.current_location::geometry) AS lat,
            ST_X(d.current_location::geometry) AS lon,
            ST_Distance(d.current_location::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography) AS distance_meters
        FROM drivers d
        JOIN users u ON d.user_id = u.id
        WHERE d.is_active = TRUE
          AND d.current_location IS NOT NULL
          AND ST_DWithin(
                d.current_location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius_meters
              )
        ORDER BY distance_meters ASC
        LIMIT 10;
    """)

    result = await session.execute(
        spatial_query,
        {"lat": lat, "lon": lon, "radius_meters": radius_meters}
    )
    rows = result.mappings().all()

    drivers = [
        {
            "driver_id": str(row["driver_id"]),
            "driver_name": row["driver_name"],
            "vehicle_info": row["vehicle_info"],
            "latitude": row["lat"],
            "longitude": row["lon"],
            "distance_km": round(row["distance_meters"] / 1000.0, 2)
        }
        for row in rows
    ]

    return {
        "search_center": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "total_found": len(drivers),
        "drivers": drivers
    }
