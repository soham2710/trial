# Vehicle Sales Dashboard

A modern, responsive web dashboard for managing vehicle inventory with AI-powered analytics using FastAPI, Mistral LLM, and HTML/CSS frontend.

## Features

- **Dashboard Overview**: Real-time statistics on vehicle inventory
- **Vehicle Inventory**: Browse all vehicles with detailed information
- **AI-Powered Analytics**: Ask questions about your inventory using Mistral AI
- **Advanced Analytics**: Visual charts and analytics
- **Vehicle Management**: Add, edit, and delete vehicles
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Project Structure

```
project2/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── templates/
│   └── index.html         # Main dashboard HTML
└── static/
    ├── styles.css         # Styling
    └── script.js          # Frontend JavaScript
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Mistral API Key

1. Get your Mistral API key from [Mistral AI Console](https://console.mistral.ai/)
2. Open `.env` file and replace `your_mistral_api_key_here` with your actual API key:

```env
MISTRAL_API_KEY=your_actual_api_key
```

### 3. Run the Application

```bash
python main.py
```

Or use Uvicorn directly:

```bash
uvicorn main:app --reload
```

### 4. Access the Dashboard

Open your browser and navigate to:

```
http://localhost:8000
```

## API Endpoints

### Dashboard & Analytics
- `GET /` - Main dashboard page
- `GET /api/sales-summary` - Get sales statistics
- `POST /api/analyze` - Analyze inventory with Mistral AI

### Vehicle Management
- `GET /api/vehicles` - Get all vehicles
- `GET /api/vehicles/{vehicle_id}` - Get specific vehicle
- `POST /api/vehicles` - Add new vehicle
- `PUT /api/vehicles/{vehicle_id}` - Update vehicle
- `DELETE /api/vehicles/{vehicle_id}` - Delete vehicle

### Health Check
- `GET /health` - API health check

## Example API Usage

### Get All Vehicles
```bash
curl http://localhost:8000/api/vehicles
```

### Add New Vehicle
```bash
curl -X POST http://localhost:8000/api/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "id": 0,
    "name": "Mercedes-Benz C-Class 2023",
    "price": 42000,
    "year": 2023,
    "mileage": 8000,
    "color": "Black",
    "description": "Luxury sedan with premium features"
  }'
```

### Ask AI About Inventory
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "Which vehicle offers the best value for money?"}'
```

## Frontend Features

### Dashboard Section
- View key metrics (total vehicles, average price, inventory value)
- AI-powered query interface for instant insights
- Get recommendations based on the current inventory

### Inventory Section
- Browse all vehicles in a grid layout
- View detailed information for each vehicle
- Edit or delete vehicles
- Quick actions for each vehicle

### Analytics Section
- Visual distribution of vehicle prices
- Year-wise inventory breakdown
- Extensible for additional metrics

### Add Vehicle Section
- Easy-to-use form to add new vehicles
- Validation for all fields
- Immediate inventory update

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/ML**: Mistral LLM (Claude alternative)
- **Server**: Uvicorn (ASGI server)
- **Environment**: Python 3.8+

## Configuration

Edit the `.env` file to customize settings:

```env
MISTRAL_API_KEY=your_key              # Your Mistral API key
DEBUG=True                             # Enable debug mode
HOST=0.0.0.0                          # Server host
PORT=8000                             # Server port
```

## Troubleshooting

### Mistral API Not Working
- Verify your API key is correct in `.env`
- Check your Mistral account has available credits
- Review the error message in the browser console

### Port Already in Use
```bash
# Use a different port
uvicorn main:app --port 8001
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Development Notes

- The frontend uses vanilla JavaScript (no frameworks) for simplicity
- Vehicles data is stored in memory (use a database for production)
- CORS is enabled for localhost development
- All API responses use JSON format

## Future Enhancements

- Database integration (PostgreSQL/MongoDB)
- User authentication and authorization
- Advanced filtering and search
- Export inventory to CSV/Excel
- Real-time notifications
- Multiple user dashboard views
- Payment integration for sales

## License

MIT License - Feel free to use and modify

## Support

For issues or questions, please check:
1. That all dependencies are installed
2. Your Mistral API key is valid
3. The server is running on the correct port

---

**Happy selling! 🚗**
