import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_message import ChatMessage
import logging
from datetime import timedelta

from database import engine, Base, SessionLocal, get_db, User, Vehicle
from schemas import UserCreate, UserLogin, Token, UserResponse, VehicleCreate, VehicleResponse, VehicleWithOwner
from security import hash_password, verify_password, create_access_token, verify_token

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Vehicle Sales Dashboard",
    version="2.0.0",
    description="Vehicle Sales Management with Authentication"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Mistral client
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    logger.warning("MISTRAL_API_KEY not set. AI features may not work.")
    client = None
else:
    client = MistralClient(api_key=MISTRAL_API_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security
security = HTTPBearer()

# ==================== Helper Functions ====================
def get_current_user(credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from token"""
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# ==================== Authentication Routes ====================
@app.post("/api/auth/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    # Create new user
    hashed_pwd = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@app.post("/api/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should delete token)"""
    return {"message": "Logged out successfully"}


# ==================== Dashboard Routes ====================
@app.get("/")
async def get_dashboard():
    """Serve the main dashboard page"""
    return FileResponse("templates/index.html")


@app.get("/login")
async def get_login_page():
    """Serve the login page"""
    return FileResponse("templates/login.html")


@app.get("/signup")
async def get_signup_page():
    """Serve the signup page"""
    return FileResponse("templates/signup.html")


# ==================== Vehicle Routes ====================
@app.get("/api/vehicles")
async def get_vehicles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all vehicles for current user"""
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id).all()
    return {"vehicles": vehicles}


@app.get("/api/vehicles/{vehicle_id}", response_model=VehicleWithOwner)
async def get_vehicle(vehicle_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific vehicle by ID"""
    vehicle = db.query(Vehicle).filter(
        (Vehicle.id == vehicle_id) & (Vehicle.owner_id == current_user.id)
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return vehicle


@app.get("/api/sales-summary")
async def get_sales_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get sales summary statistics for current user"""
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id).all()
    
    total_vehicles = len(vehicles)
    if total_vehicles == 0:
        return {
            "total_vehicles": 0,
            "avg_price": 0,
            "total_inventory_value": 0,
            "price_range": {"min": 0, "max": 0}
        }
    
    avg_price = sum(v.price for v in vehicles) / total_vehicles
    total_value = sum(v.price for v in vehicles)
    
    return {
        "total_vehicles": total_vehicles,
        "avg_price": round(avg_price, 2),
        "total_inventory_value": round(total_value, 2),
        "price_range": {
            "min": min(v.price for v in vehicles),
            "max": max(v.price for v in vehicles)
        }
    }


@app.post("/api/vehicles", response_model=VehicleResponse)
async def add_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new vehicle"""
    db_vehicle = Vehicle(
        name=vehicle_data.name,
        price=vehicle_data.price,
        year=vehicle_data.year,
        mileage=vehicle_data.mileage,
        color=vehicle_data.color,
        description=vehicle_data.description,
        owner_id=current_user.id
    )
    
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    return db_vehicle


@app.put("/api/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing vehicle"""
    vehicle = db.query(Vehicle).filter(
        (Vehicle.id == vehicle_id) & (Vehicle.owner_id == current_user.id)
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle.name = vehicle_data.name
    vehicle.price = vehicle_data.price
    vehicle.year = vehicle_data.year
    vehicle.mileage = vehicle_data.mileage
    vehicle.color = vehicle_data.color
    vehicle.description = vehicle_data.description
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@app.delete("/api/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a vehicle"""
    vehicle = db.query(Vehicle).filter(
        (Vehicle.id == vehicle_id) & (Vehicle.owner_id == current_user.id)
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db.delete(vehicle)
    db.commit()
    
    return {"message": "Vehicle deleted successfully"}


# ==================== AI Analytics Route ====================
@app.post("/api/analyze")
async def analyze_sales(
    query: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use Mistral LLM to analyze vehicle sales data"""
    
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Mistral API not configured"
        )
    
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id).all()
    
    # Prepare context with vehicle data
    vehicles_context = "\n".join([
        f"- {v.name}: ${v.price:,}, Year: {v.year}, Mileage: {v.mileage} miles, Color: {v.color}"
        for v in vehicles
    ]) if vehicles else "No vehicles in inventory"
    
    prompt = f"""You are a vehicle sales expert. Here is the current inventory:

{vehicles_context}

User question: {query.get('question', '')}

Provide a helpful analysis or recommendation based on the inventory and the user's question."""
    
    try:
        messages = [ChatMessage(role="user", content=prompt)]
        response = client.chat(model="mistral-small", messages=messages)
        analysis = response.choices[0].message.content
        
        return {"analysis": analysis}
    except Exception as e:
        logger.error(f"Error calling Mistral API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing sales data: {str(e)}"
        )


# ==================== Health Check ====================
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
