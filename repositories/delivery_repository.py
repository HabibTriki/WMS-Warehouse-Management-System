"""
Delivery repository for database operations.

Handles CRUD operations for DeliveryRequest entities.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select

from models.delivery import DeliveryRequest, DeliveryStatus


class DeliveryRepository:
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, delivery: DeliveryRequest) -> DeliveryRequest:

        self.session.add(delivery)
        self.session.commit()
        self.session.refresh(delivery)
        return delivery
    
    def get_by_id(self, delivery_id: UUID) -> Optional[DeliveryRequest]:
        statement = select(DeliveryRequest).where(DeliveryRequest.id == delivery_id)
        return self.session.exec(statement).first()
    
    def get_by_fulfillment_id(self, fulfillment_id: UUID) -> Optional[DeliveryRequest]:
        statement = select(DeliveryRequest).where(
            DeliveryRequest.fulfillment_id == fulfillment_id
        )
        return self.session.exec(statement).first()
    
    def update(self, delivery: DeliveryRequest) -> DeliveryRequest:
        delivery.updated_at = datetime.utcnow()
        self.session.add(delivery)
        self.session.commit()
        self.session.refresh(delivery)
        return delivery
