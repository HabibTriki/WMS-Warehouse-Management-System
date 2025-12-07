from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from models.fulfillment import FulfillmentItem, DestinationInfo, FulfillmentOrder
from models.package import PackageRequest
from models.delivery import DeliveryRequest


# Fulfillment Schemas

class CreateFulfillmentRequest(BaseModel):
    """Request to create a new fulfillment order (Step 5)."""
    order_id: str = Field(..., description="OMS order identifier")
    items: List[FulfillmentItem] = Field(..., description="Items to fulfill")
    destination: DestinationInfo = Field(..., description="Delivery destination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD-12345",
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


class CreateFulfillmentResponse(BaseModel):
    """Response after creating fulfillment order."""
    fulfillment: FulfillmentOrder
    message: str = "Fulfillment order created successfully"


# Location Check Schemas

class CheckLocationRequest(BaseModel):
    """Request to check product location via IMS."""
    order_id: Optional[str] = Field(None, description="OMS order identifier")
    fulfillment_id: Optional[UUID] = Field(None, description="Fulfillment order ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fulfillment_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class CheckLocationResponse(BaseModel):
    """Response after checking location with IMS."""
    fulfillment: FulfillmentOrder
    ims_response: dict = Field(..., description="Response from IMS")
    message: str = "Location checked successfully"


# Package Request Schemas

class CreatePackageRequest(BaseModel):
    """Request to create package (Step 7 + 9)."""
    fulfillment_id: UUID = Field(..., description="Fulfillment order ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fulfillment_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class CreatePackageResponse(BaseModel):
    """Response after creating package."""
    package_request: PackageRequest
    fulfillment: FulfillmentOrder
    message: str = "Package created successfully"


# Delivery Request Schemas

class CreateDeliveryRequestDTO(BaseModel):
    """Request to create delivery request (Step 8)."""
    fulfillment_id: UUID = Field(..., description="Fulfillment order ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fulfillment_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class CreateDeliveryResponse(BaseModel):
    """Response after creating delivery request."""
    delivery_request: DeliveryRequest
    fulfillment: FulfillmentOrder
    message: str = "Delivery request created successfully"


# Error Response

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
