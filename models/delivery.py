"""
Delivery request models for WMS.

Handles delivery request creation and tracking for communication with DMS.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON


class DeliveryStatus(str, Enum):
    CREATED = "CREATED"
    SENT_TO_DMS = "SENT_TO_DMS"
    FAILED = "FAILED"


class DeliveryRequest(SQLModel, table=True):

    __tablename__ = "delivery_requests"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique delivery request identifier"
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
    
    warehouse_id: str = Field(
        nullable=False,
        description="Source warehouse for delivery"
    )
    
    status: DeliveryStatus = Field(
        default=DeliveryStatus.CREATED,
        nullable=False,
        description="Current delivery request status"
    )
    
    destination: dict = Field(
        sa_column=Column(JSON),
        description="Delivery destination information"
    )
    
    items_summary: list = Field(
        sa_column=Column(JSON),
        description="Summary of items for delivery"
    )
    
    dms_response: Optional[dict] = Field(
        sa_column=Column(JSON),
        default=None,
        description="Response from DMS (if any)"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Error message if delivery request failed"
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
                "warehouse_id": "WH-TUN-01",
                "status": "SENT_TO_DMS",
                "destination": {
                    "address": "Rue de Tunis 10",
                    "city": "Tunis",
                    "phone": "+216 20 000 000"
                },
                "items_summary": [
                    {"sku": "SKU-ABC", "quantity": 2}
                ]
            }
        }
