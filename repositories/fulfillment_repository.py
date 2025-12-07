from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select

from models.fulfillment import FulfillmentOrder, FulfillmentStatus


class FulfillmentRepository:
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, fulfillment: FulfillmentOrder) -> FulfillmentOrder:

        self.session.add(fulfillment)
        self.session.commit()
        self.session.refresh(fulfillment)
        return fulfillment
    
    def get_by_id(self, fulfillment_id: UUID) -> Optional[FulfillmentOrder]:

        statement = select(FulfillmentOrder).where(FulfillmentOrder.id == fulfillment_id)
        return self.session.exec(statement).first()
    
    def get_by_order_id(self, order_id: str) -> Optional[FulfillmentOrder]:

        statement = select(FulfillmentOrder).where(FulfillmentOrder.order_id == order_id)
        return self.session.exec(statement).first()
    
    def update(self, fulfillment: FulfillmentOrder) -> FulfillmentOrder:

        fulfillment.updated_at = datetime.utcnow()
        self.session.add(fulfillment)
        self.session.commit()
        self.session.refresh(fulfillment)
        return fulfillment
    
    def update_status(
        self,
        fulfillment_id: UUID,
        status: FulfillmentStatus,
        warehouse_id: Optional[str] = None
    ) -> Optional[FulfillmentOrder]:

        fulfillment = self.get_by_id(fulfillment_id)
        if not fulfillment:
            return None
        
        fulfillment.status = status
        if warehouse_id:
            fulfillment.warehouse_id = warehouse_id
        
        return self.update(fulfillment)
