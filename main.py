import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_message import ChatMessage
import logging

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Vehicle Sales Dashboard", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Mistral client
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    logger.warning("MISTRAL_API_KEY not set. Some features may not work.")
    client = None
else:
    client = MistralClient(api_key=MISTRAL_API_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models
class Vehicle(BaseModel):
    id: int
    name: str
    price: float
    year: int
    mileage: float
    color: str
    description: str = ""

class SalesQuery(BaseModel):
    question: str

class SalesAnalysis(BaseModel):
    analysis: str

# Sample vehicle data
vehicles_db = [
    Vehicle(id=1, name="Toyota Camry 2022", price=28000, year=2022, mileage=15000, color="Silver", description="Reliable sedan with excellent fuel efficiency"),
    Vehicle(id=2, name="Honda Civic 2021", price=24000, year=2021, mileage=22000, color="Blue", description="Compact car perfect for city driving"),
    Vehicle(id=3, name="Ford F-150 2020", price=35000, year=2020, mileage=45000, color="Black", description="Powerful pickup truck for work and family"),
    Vehicle(id=4, name="Tesla Model 3 2023", price=45000, year=2023, mileage=5000, color="White", description="Electric vehicle with advanced technology"),
    Vehicle(id=5, name="Chevrolet Malibu 2021", price=22000, year=2021, mileage=30000, color="Red", description="Spacious midsize sedan"),
]

# Routes
@app.get("/")
async def get_dashboard():
    """Serve the main dashboard page"""
    return FileResponse("templates/index.html")

@app.get("/api/vehicles")
async def get_vehicles():
    """Get all vehicles in inventory"""
    return {"vehicles": vehicles_db}

@app.get("/api/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: int):
    """Get a specific vehicle by ID"""
    for vehicle in vehicles_db:
        if vehicle.id == vehicle_id:
            return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")

@app.get("/api/sales-summary")
async def get_sales_summary():
    """Get sales summary statistics"""
    total_vehicles = len(vehicles_db)
    avg_price = sum(v.price for v in vehicles_db) / total_vehicles if total_vehicles > 0 else 0
    total_value = sum(v.price for v in vehicles_db)
    
    return {
        "total_vehicles": total_vehicles,
        "avg_price": round(avg_price, 2),
        "total_inventory_value": round(total_value, 2),
        "price_range": {
            "min": min(v.price for v in vehicles_db),
            "max": max(v.price for v in vehicles_db)
        }
    }

@app.post("/api/analyze")
async def analyze_sales(query: SalesQuery) -> SalesAnalysis:
    """Use Mistral LLM to analyze vehicle sales data"""
    
    if not client:
        raise HTTPException(status_code=500, detail="Mistral API not configured")
    
    # Prepare context with vehicle data
    vehicles_context = "\n".join([
        f"- {v.name}: ${v.price:,}, Year: {v.year}, Mileage: {v.mileage} miles, Color: {v.color}"
        for v in vehicles_db
    ])
    
    prompt = f"""You are a vehicle sales expert. Here is our current inventory:

{vehicles_context}

User question: {query.question}

Provide a helpful analysis or recommendation based on the inventory and the user's question."""
    
    try:
        messages = [ChatMessage(role="user", content=prompt)]
        response = client.chat(model="mistral-small", messages=messages)
        analysis = response.choices[0].message.content
        
        return SalesAnalysis(analysis=analysis)
    except Exception as e:
        logger.error(f"Error calling Mistral API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing sales data: {str(e)}")

@app.post("/api/vehicles")
async def add_vehicle(vehicle: Vehicle):
    """Add a new vehicle to inventory"""
    # Generate new ID
    new_id = max([v.id for v in vehicles_db]) + 1 if vehicles_db else 1
    vehicle.id = new_id
    vehicles_db.append(vehicle)
    return vehicle

@app.put("/api/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: int, vehicle: Vehicle):
    """Update an existing vehicle"""
    for i, v in enumerate(vehicles_db):
        if v.id == vehicle_id:
            vehicle.id = vehicle_id
            vehicles_db[i] = vehicle
            return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")

@app.delete("/api/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: int):
    """Delete a vehicle from inventory"""
    for i, v in enumerate(vehicles_db):
        if v.id == vehicle_id:
            deleted = vehicles_db.pop(i)
            return {"message": "Vehicle deleted", "vehicle": deleted}
    raise HTTPException(status_code=404, detail="Vehicle not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
