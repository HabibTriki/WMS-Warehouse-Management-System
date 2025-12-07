from typing import List, Dict, Any
import httpx
from pydantic import BaseModel


class IMSLocationRequest(BaseModel):
    """Request payload for IMS location check."""
    items: List[Dict[str, Any]]


class IMSReservationRequest(BaseModel):
    """Request payload for IMS product reservation."""
    warehouse_id: str
    items: List[Dict[str, Any]]


class IMSClient:
    
    def __init__(self, esb1_base_url: str, timeout: float = 30.0):
        """
        Initialize IMS client.
        
        Args:
            esb1_base_url: Base URL for ESB1 (e.g., "http://localhost:8001")
            timeout: Request timeout in seconds
        """
        self.esb1_base_url = esb1_base_url.rstrip("/")
        self.timeout = timeout
    
    async def check_location(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check product location via IMS.
        
        Routes through: WMS → ESB1 → IMS
        
        Args:
            items: List of items with Stock Keeping Unit and quantity
            
        Returns:
            IMS response with warehouse_id and availability info
            
        Raises:
            httpx.HTTPError: If request fails
            
        Example response:
            {
                "warehouse_id": "WH-TUN-01",
                "items": [
                    {
                        "sku": "SKU-ABC",
                        "available": true,
                        "location": "A-12-3"
                    }
                ]
            }
        """
        url = f"{self.esb1_base_url}/ims/inventory/locate"
        payload = {"items": items}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # TODO : ESB1/Camunda integration point: Could trigger compensation workflow
                raise Exception(f"IMS location check failed: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                raise Exception(f"IMS location check request failed: {str(e)}")
    
    async def reserve_product(
        self,
        warehouse_id: str,
        items: List[Dict[str, Any]]
     ) -> Dict[str, Any]:
        """
        Reserve products in IMS (Step 7).
        
        Routes through: WMS → ESB1 → IMS
        
        Args:
            warehouse_id: Target warehouse ID
            items: List of items to reserve
            
        Returns:
            IMS response with reservation confirmation
            
        Raises:
            httpx.HTTPError: If request fails
            
        Example response:
            {
                "reservation_id": "RES-12345",
                "warehouse_id": "WH-TUN-01",
                "status": "RESERVED",
                "items": [...]
            }
        """
        url = f"{self.esb1_base_url}/ims/inventory/reserve"
        payload = {
            "warehouse_id": warehouse_id,
            "items": items
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # ESB1/Camunda integration point: Could trigger inventory allocation retry
                raise Exception(f"IMS reservation failed: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                raise Exception(f"IMS reservation request failed: {str(e)}")
