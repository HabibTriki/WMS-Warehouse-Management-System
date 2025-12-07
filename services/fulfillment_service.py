from typing import Dict, Any, Tuple
from uuid import UUID

from sqlmodel import Session

from models.fulfillment import FulfillmentOrder, FulfillmentStatus, FulfillmentItem, DestinationInfo
from models.package import PackageRequest, PackageStatus
from models.delivery import DeliveryRequest, DeliveryStatus
from repositories.fulfillment_repository import FulfillmentRepository
from repositories.package_repository import PackageRepository
from repositories.delivery_repository import DeliveryRepository
from clients.ims_client import IMSClient
from clients.dms_client import DMSClient
from config import settings


class FulfillmentService:
    
    def __init__(
        self,
        session: Session,
        ims_client: IMSClient,
        dms_client: DMSClient
    ):
        self.fulfillment_repo = FulfillmentRepository(session)
        self.package_repo = PackageRepository(session)
        self.delivery_repo = DeliveryRepository(session)
        self.ims_client = ims_client
        self.dms_client = dms_client
    
    def create_fulfillment(
        self,
        order_id: str,
        items: list[FulfillmentItem],
        destination: DestinationInfo
    ) -> FulfillmentOrder:
        # Convert Pydantic models to dicts for JSON storage
        items_dict = [item.model_dump() for item in items]
        destination_dict = destination.model_dump()
        
        fulfillment = FulfillmentOrder(
            order_id=order_id,
            status=FulfillmentStatus.PENDING,
            items=items_dict,
            destination=destination_dict
        )
        
        return self.fulfillment_repo.create(fulfillment)
    
    async def check_and_update_location(
        self,
        fulfillment_id: UUID
    ) -> Tuple[FulfillmentOrder, Dict[str, Any]]:
        # Get fulfillment order
        fulfillment = self.fulfillment_repo.get_by_id(fulfillment_id)
        if not fulfillment:
            raise ValueError(f"Fulfillment order {fulfillment_id} not found")
        
        # Prepare items for IMS (items are stored as dicts in JSON)
        items = [{"sku": item['sku'], "quantity": item['quantity']} for item in fulfillment.items]
        
        # Call IMS via ESB1
        ims_response = await self.ims_client.check_location(items)
        
        # Update fulfillment with warehouse info
        warehouse_id = ims_response.get("warehouse_id")
        if warehouse_id:
            fulfillment.warehouse_id = warehouse_id
            fulfillment.status = FulfillmentStatus.WAITING_RESERVATION
            fulfillment = self.fulfillment_repo.update(fulfillment)
        
        return fulfillment, ims_response
    
    async def create_package(
        self,
        fulfillment_id: UUID
    ) -> Tuple[PackageRequest, FulfillmentOrder]:
        # Get fulfillment order
        fulfillment = self.fulfillment_repo.get_by_id(fulfillment_id)
        if not fulfillment:
            raise ValueError(f"Fulfillment order {fulfillment_id} not found")
        
        if not fulfillment.warehouse_id:
            raise ValueError("Warehouse not assigned. Run location check first.")
        
        # Create package request
        package = PackageRequest(
            order_id=fulfillment.order_id,
            fulfillment_id=fulfillment.id,
            status=PackageStatus.IN_PROGRESS,
            package_type="STANDARD"
        )
        
        # Packaging algorithm
        # Calculate weight: sum of quantities × 0.5 kg (items are dicts from JSON)
        total_quantity = sum(item['quantity'] for item in fulfillment.items)
        package.weight = total_quantity * 0.5
        
        # Mark as packaged
        package.status = PackageStatus.PACKAGED
        package = self.package_repo.create(package)
        
        # Update fulfillment status
        fulfillment.status = FulfillmentStatus.READY_FOR_DELIVERY
        fulfillment = self.fulfillment_repo.update(fulfillment)
        
        return package, fulfillment
    
    async def request_delivery(
        self,
        fulfillment_id: UUID
    ) -> Tuple[DeliveryRequest, FulfillmentOrder]:
        # Get fulfillment order
        fulfillment = self.fulfillment_repo.get_by_id(fulfillment_id)
        if not fulfillment:
            raise ValueError(f"Fulfillment order {fulfillment_id} not found")
        
        # Validate packaging completed
        package = self.package_repo.get_by_fulfillment_id(fulfillment_id)
        if not package or package.status != PackageStatus.PACKAGED:
            raise ValueError("Packaging not completed. Run package request first.")
        
        if not fulfillment.warehouse_id:
            raise ValueError("Warehouse not assigned")
        
        # Create delivery request (items and destination are dicts from JSON)
        delivery = DeliveryRequest(
            order_id=fulfillment.order_id,
            fulfillment_id=fulfillment.id,
            warehouse_id=fulfillment.warehouse_id,
            status=DeliveryStatus.CREATED,
            destination=fulfillment.destination,
            items_summary=fulfillment.items
        )
        delivery = self.delivery_repo.create(delivery)
        
        # Prepare DMS payload
        dms_payload = {
            "order_id": fulfillment.order_id,
            "fulfillment_id": str(fulfillment.id),
            "warehouse_id": fulfillment.warehouse_id,
            "destination": fulfillment.destination,
            "items": fulfillment.items
        }
        
        # Call DMS via ESB3
        try:
            dms_response = await self.dms_client.create_delivery_request(dms_payload)
            
            # Update delivery request as sent
            delivery.status = DeliveryStatus.SENT_TO_DMS
            delivery.dms_response = dms_response
            delivery = self.delivery_repo.update(delivery)
            
            # Update fulfillment status
            fulfillment.status = FulfillmentStatus.DELIVERY_REQUESTED
            fulfillment = self.fulfillment_repo.update(fulfillment)
            
        except Exception as e:
            # Mark delivery as failed
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = str(e)
            delivery = self.delivery_repo.update(delivery)
            
            # ESB3/Camunda integration point: Could trigger compensation workflow
            raise
        
        return delivery, fulfillment
