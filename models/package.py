from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class PackageStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PACKAGED = "PACKAGED"


class PackageRequest(SQLModel, table=True):

    __tablename__ = "package_requests"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique package request identifier"
    )
    
    order_id: str = Field(
        index=True,
        nullable=False,
        description="Reference to OMS order ID"
    )
    
    fulfillment_id: UUID = Field(
        foreign_key="fulfillment_orders.id",
        index=True,
        nullable=False,
        description="Reference to fulfillment order"
    )
    
    status: PackageStatus = Field(
        default=PackageStatus.PENDING,
        nullable=False,
        description="Current package status"
    )
    
    package_type: Optional[str] = Field(
        default="STANDARD",
        nullable=True,
        description="Type of package (STANDARD, FRAGILE, etc.)"
    )
    
    weight: Optional[float] = Field(
        default=None,
        nullable=True,
        description="Calculated package weight in kg"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD-12345",
                "fulfillment_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "PACKAGED",
                "package_type": "STANDARD",
                "weight": 1.5
            }
        }
