from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select

from models.package import PackageRequest, PackageStatus


class PackageRepository:
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, package: PackageRequest) -> PackageRequest:
        self.session.add(package)
        self.session.commit()
        self.session.refresh(package)
        return package
    
    def get_by_id(self, package_id: UUID) -> Optional[PackageRequest]:
        statement = select(PackageRequest).where(PackageRequest.id == package_id)
        return self.session.exec(statement).first()
    
    def get_by_fulfillment_id(self, fulfillment_id: UUID) -> Optional[PackageRequest]:
        statement = select(PackageRequest).where(
            PackageRequest.fulfillment_id == fulfillment_id
        )
        return self.session.exec(statement).first()
    
    def update(self, package: PackageRequest) -> PackageRequest:
        package.updated_at = datetime.utcnow()
        self.session.add(package)
        self.session.commit()
        self.session.refresh(package)
        return package
