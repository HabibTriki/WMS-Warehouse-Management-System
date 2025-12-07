from typing import Dict, Any
import httpx
from pydantic import BaseModel


class DMSDeliveryRequest(BaseModel):
    order_id: str
    fulfillment_id: str
    warehouse_id: str
    destination: Dict[str, Any]
    items: list


class DMSClient:
    
    def __init__(self, esb3_base_url: str, timeout: float = 30.0, max_retries: int = 3):

        self.esb3_base_url = esb3_base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def create_delivery_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create delivery request in DMS (Step 8).
        
        Routes through: WMS → ESB3 → DMS
        
        Args:
            payload: Delivery request data including:
                - order_id: OMS order identifier
                - fulfillment_id: WMS fulfillment identifier
                - warehouse_id: Source warehouse
                - destination: Delivery address info
                - items: Items to deliver
                
        Returns:
            DMS response with delivery request confirmation
            
        Raises:
            Exception: If request fails after retries
            
        Example payload:
            {
                "order_id": "ORD-12345",
                "fulfillment_id": "550e8400-e29b-41d4-a716-446655440000",
                "warehouse_id": "WH-TUN-01",
                "destination": {
                    "address": "Rue de Tunis 10",
                    "city": "Tunis",
                    "phone": "+216 20 000 000"
                },
                "items": [
                    {"sku": "SKU-ABC", "quantity": 2}
                ]
            }
            
        Example response:
            {
                "delivery_id": "DEL-12345",
                "status": "PENDING_ASSIGNMENT",
                "estimated_pickup": "2025-12-07T10:00:00Z"
            }
        """
        url = f"{self.esb3_base_url}/dms/delivery-request/create"
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as e:
                last_error = f"DMS delivery request failed: {e.response.status_code} - {e.response.text}"
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    continue
                break
            except httpx.RequestError as e:
                last_error = f"DMS delivery request connection failed: {str(e)}"
                if attempt < self.max_retries - 1:
                    continue
                break
        
        raise Exception(last_error or "DMS delivery request failed")
