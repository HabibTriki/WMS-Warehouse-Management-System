# ShipOra WMS - Warehouse Management System

FastAPI-based Warehouse Management System handling fulfillment workflow for the ShipOra platform.

## Purpose

Manages order fulfillment from warehouse assignment through packaging to delivery handoff.

## Architecture

![WMS Architecture](images/architecture%20globale.png)

The WMS integrates with:
- **IMS** (Inventory Management) via ESB1 - for warehouse location and inventory
- **DMS** (Delivery Management) via ESB3 - for delivery dispatch

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/fulfillment` | POST | Create fulfillment order |
| `/api/fulfillment/check-location` | POST | Check warehouse location (via IMS) |
| `/api/fulfillment/package-request` | POST | Create package with weight calculation |
| `/api/fulfillment/delivery-request` | POST | Send delivery request (via DMS) |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your ESB endpoints

# Run server
python main.py
```

Server runs on http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Database

SQLite database (`wms.db`) with 3 tables:
- `fulfillment_orders` - Main fulfillment tracking
- `package_requests` - Packaging operations
- `delivery_requests` - DMS handoff tracking

## Fulfillment Workflow

```
1. Create Fulfillment (PENDING)
   ↓
2. Check Location via IMS (WAITING_RESERVATION)
   ↓
3. Create Package (READY_FOR_DELIVERY)
   ↓
4. Request Delivery via DMS (DELIVERY_REQUESTED)
```

## Example Usage

```bash
# 1. Create fulfillment
curl -X POST http://localhost:8000/api/fulfillment \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-001",
    "items": [{"sku": "SKU-ABC", "quantity": 2}],
    "destination": {
      "address": "Rue de Tunis 10",
      "city": "Tunis",
      "phone": "+216 20 000 000"
    }
  }'

# 2. Check location (requires ESB1/IMS)
curl -X POST http://localhost:8000/api/fulfillment/check-location \
  -H "Content-Type: application/json" \
  -d '{"fulfillment_id": "your-id-here"}'

# 3. Create package
curl -X POST http://localhost:8000/api/fulfillment/package-request \
  -H "Content-Type: application/json" \
  -d '{"fulfillment_id": "your-id-here"}'

# 4. Request delivery (requires ESB3/DMS)
curl -X POST http://localhost:8000/api/fulfillment/delivery-request \
  -H "Content-Type: application/json" \
  -d '{"fulfillment_id": "your-id-here"}'
```

## Configuration

Key environment variables in `.env`:
```
ESB1_BASE_URL=http://localhost:8001  # IMS routing
ESB3_BASE_URL=http://localhost:8003  # DMS routing
```

## Tech Stack

- **FastAPI** - Web framework
- **SQLModel** - ORM with Pydantic validation
- **SQLite** - Database
- **httpx** - Async HTTP client for ESB calls

## Integration Points

### ESB1 → IMS
- `POST /ims/inventory/locate` - Get warehouse location
- `POST /ims/inventory/reserve` - Reserve inventory

### ESB3 → DMS
- `POST /dms/delivery-request/create` - Create delivery

## License

Part of ShipOra platform - PoC implementation.

