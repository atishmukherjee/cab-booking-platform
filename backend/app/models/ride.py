import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from geoalchemy2 import Geometry

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    phone: str
    role: str = Field(default="rider")
    rating_avg: float = Field(default=5.0)

class Driver(SQLModel, table=True):
    __tablename__ = "drivers"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    vehicle_info: str
    is_active: bool = Field(default=False)
    # spatial_index=False set kiya taaki auto-create conflict na ho
    current_location: Optional[str] = Field(
        default=None,
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=False))
    )

class Ride(SQLModel, table=True):
    __tablename__ = "rides"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rider_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    driver_id: Optional[uuid.UUID] = Field(default=None, foreign_key="drivers.id", index=True)
    status: str = Field(default="REQUESTED")
    pickup_point: str = Field(sa_column=Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=False)))
    drop_point: str = Field(sa_column=Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=False)))
    fare_estimate: float
    fare_actual: Optional[float] = None
    distance_meters: int
    duration_secs: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
