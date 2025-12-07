from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from models.schemas import (
    CreateFulfillmentRequest,
    CreateFulfillmentResponse,
    CheckLocationRequest,
    CheckLocationResponse,
    CreatePackageRequest,
    CreatePackageResponse,
    CreateDeliveryRequestDTO,
    CreateDeliveryResponse,
    ErrorResponse
)
from services.fulfillment_service import FulfillmentService
from clients.ims_client import IMSClient
from clients.dms_client import DMSClient
from config import settings


router = APIRouter(
    prefix="/api/fulfillment",
    tags=["Fulfillment"],
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


def get_fulfillment_service(session: Session = Depends(get_session)) -> FulfillmentService:
    """Dependency to create FulfillmentService with clients."""
    ims_client = IMSClient(
        esb1_base_url=settings.esb1_base_url,
        timeout=settings.ims_timeout
    )
    dms_client = DMSClient(
        esb3_base_url=settings.esb3_base_url,
        timeout=settings.dms_timeout,
        max_retries=settings.dms_max_retries
    )
    return FulfillmentService(session, ims_client, dms_client)


@router.post(
    "",
    response_model=CreateFulfillmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Fulfillment Order"
)
async def create_fulfillment(
    request: CreateFulfillmentRequest,
    service: FulfillmentService = Depends(get_fulfillment_service)
) -> CreateFulfillmentResponse:
    """
    Create new fulfillment order.
    This endpoint is typically called by OMS when an order is ready for fulfillment.
    """
    try:
        fulfillment = service.create_fulfillment(
            order_id=request.order_id,
            items=request.items,
            destination=request.destination
        )
        # TODO  : ESB3/Camunda integration point

        return CreateFulfillmentResponse(
            fulfillment=fulfillment,
            message="Fulfillment order created successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create fulfillment: {str(e)}"
        )


@router.post(
    "/check-location",
    response_model=CheckLocationResponse,
    summary="Check Product Location"
)
async def check_location(
    request: CheckLocationRequest,
    service: FulfillmentService = Depends(get_fulfillment_service)
) -> CheckLocationResponse:
    """
    Check product location via IMS.
    Routes: WMS -> ESB1 -> IMS
    """
    try:
        if request.fulfillment_id:
            fulfillment_id = request.fulfillment_id
        elif request.order_id:

            fulfillment = service.fulfillment_repo.get_by_order_id(request.order_id)
            if not fulfillment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Fulfillment not found for order_id: {request.order_id}"
                )
            fulfillment_id = fulfillment.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either fulfillment_id or order_id must be provided"
            )
        
        fulfillment, ims_response = await service.check_and_update_location(fulfillment_id)
        
        # TODO optional  : ESB1/Camunda integration point: Publish location checked event
        # await event_bus.publish("fulfillment.location_checked", fulfillment.id)
        
        return CheckLocationResponse(
            fulfillment=fulfillment,
            ims_response=ims_response,
            message="Location checked successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check location: {str(e)}"
        )


@router.post(
    "/package-request",
    response_model=CreatePackageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Package Request"
)
async def create_package(
    request: CreatePackageRequest,
    service: FulfillmentService = Depends(get_fulfillment_service)
) -> CreatePackageResponse:
    """
    Create package request with packaging algorithm.
    """
    try:
        package, fulfillment = await service.create_package(request.fulfillment_id)
        
        # TODO  : ESB1/Camunda integration point: Publish package created event
        # await event_bus.publish("fulfillment.packaged", fulfillment.id)
        
        return CreatePackageResponse(
            package_request=package,
            fulfillment=fulfillment,
            message="Package created successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create package: {str(e)}"
        )


@router.post(
    "/delivery-request",
    response_model=CreateDeliveryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Delivery Request"
)
async def create_delivery_request(
    request: CreateDeliveryRequestDTO,
    service: FulfillmentService = Depends(get_fulfillment_service)
) -> CreateDeliveryResponse:
    """
    Create and send delivery request to DMS (Step 8)
    """
    try:
        delivery, fulfillment = await service.request_delivery(request.fulfillment_id)
        
        # TODO : ESB3/Camunda integration point: Publish delivery requested event
        # await event_bus.publish("fulfillment.delivery_requested", fulfillment.id)
        
        return CreateDeliveryResponse(
            delivery_request=delivery,
            fulfillment=fulfillment,
            message="Delivery request created successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create delivery request: {str(e)}"
        )
