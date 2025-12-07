from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField, Column, JSON


class FulfillmentStatus(str, Enum):
    PENDING = "PENDING"
    WAITING_LOCATION = "WAITING_LOCATION"
    WAITING_RESERVATION = "WAITING_RESERVATION"
    PACKAGING = "PACKAGING"
    READY_FOR_DELIVERY = "READY_FOR_DELIVERY"
    DELIVERY_REQUESTED = "DELIVERY_REQUESTED"
    COMPLETED = "COMPLETED"


class DestinationInfo(BaseModel):
    """Delivery destination information."""
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    phone: str = Field(..., description="Contact phone number")


class FulfillmentItem(BaseModel):
    """Individual item in a fulfillment order."""
    sku: str = Field(..., description="Product SKU identifier")
    quantity: int = Field(..., gt=0, description="Quantity to fulfill")


class FulfillmentOrder(SQLModel, table=True):

    __tablename__ = "fulfillment_orders"
    
    id: UUID = SQLField(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique fulfillment identifier"
    )
    
    order_id: str = SQLField(
        index=True,
        nullable=False,
        description="Reference to OMS order ID"
    )
    
    status: FulfillmentStatus = SQLField(
        default=FulfillmentStatus.PENDING,
        nullable=False,
        description="Current fulfillment status"
    )
    
    warehouse_id: Optional[str] = SQLField(
        default=None,
        nullable=True,
        description="Assigned warehouse (set after location check)"
    )
    
    items: List[FulfillmentItem] = SQLField(
        sa_column=Column(JSON),
        description="List of items to fulfill"
    )
    
    destination: DestinationInfo = SQLField(
        sa_column=Column(JSON),
        description="Delivery destination information"
    )
    
    created_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )
    
    updated_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD-12345",
                "status": "PENDING",
                "warehouse_id": "WH-TUN-01",
                "items": [
                    {"sku": "SKU-ABC", "quantity": 2},
                    {"sku": "SKU-XYZ", "quantity": 1}
                ],
                "destination": {
                    "address": "Rue de Tunis 10",
                    "city": "Tunis",
                    "phone": "+216 20 000 000"
                }
            }
        }
