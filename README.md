# Vehicle Sales Dashboard

A modern, responsive web dashboard for managing vehicle inventory with user authentication, SQLite database, and AI-powered analytics using FastAPI, Mistral LLM, and HTML/CSS frontend.

## Current Version: 2.0 (With Authentication & Database)

## Features

- **User Authentication**: Secure signup and login with JWT tokens
- **SQLite Database**: Persistent data storage with SQLAlchemy ORM
- **Dashboard Overview**: Real-time statistics on vehicle inventory
- **Vehicle Inventory**: Browse all vehicles with detailed information
- **AI-Powered Analytics**: Ask questions about your inventory using Mistral AI
- **Advanced Analytics**: Visual charts and analytics
- **Vehicle Management**: Add, edit, and delete vehicles (user-specific)
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Security**: Password hashing, JWT tokens, user isolation

## Project Structure

```
project2/
├── main.py                    # FastAPI application with routes
├── database.py               # SQLAlchemy models and configuration
├── schemas.py                # Pydantic models for request/response
├── security.py               # Authentication & password utilities
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── vehicle_sales.db         # SQLite database (auto-created)
├── templates/
│   ├── index.html           # Main dashboard
│   ├── login.html           # Login page
│   └── signup.html          # Sign up page
└── static/
    ├── styles.css           # Dashboard styling
    ├── auth.css             # Authentication pages styling
    └── script.js            # JavaScript functionality
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

1. Open `.env` file and replace with your actual values:

```env
# Mistral API Configuration
MISTRAL_API_KEY=your_mistral_api_key_here

# FastAPI Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# JWT Configuration (Change to a random string in production)
SECRET_KEY=your-secret-key-change-this-in-production-12345
```

### 3. Run the Application

```bash
python main.py
```

Or using Uvicorn directly:

```bash
uvicorn main:app --reload
```

### 4. Access the Dashboard

Open your browser and navigate to:

```
http://localhost:8000
```

**First Time:**
- You'll be redirected to the login page
- Click "Sign up here" to create a new account
- Create your account with username, email, and password
- Login with your credentials

## API Endpoints

### Authentication Routes
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout (client-side token deletion)

### Dashboard & Analytics
- `GET /` - Main dashboard page
- `GET /api/sales-summary` - Get sales statistics
- `POST /api/analyze` - Analyze inventory with Mistral AI

### Vehicle Management (All require authentication)
- `GET /api/vehicles` - Get all vehicles for current user
- `GET /api/vehicles/{vehicle_id}` - Get specific vehicle
- `POST /api/vehicles` - Add new vehicle
- `PUT /api/vehicles/{vehicle_id}` - Update vehicle
- `DELETE /api/vehicles/{vehicle_id}` - Delete vehicle

### Health Check
- `GET /health` - API health check

## Example API Usage

### Sign Up
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_dealer",
    "email": "john@example.com",
    "password": "secure_password_123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_dealer",
    "password": "secure_password_123"
  }'
```

Response will include:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "john_dealer"
}
```

### Add New Vehicle (with token)
```bash
curl -X POST http://localhost:8000/api/vehicles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Mercedes-Benz C-Class 2023",
    "price": 42000,
    "year": 2023,
    "mileage": 8000,
    "color": "Black",
    "description": "Luxury sedan with premium features"
  }'
```

### Ask AI About Your Inventory
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"question": "Which vehicle offers the best value for money?"}'
```

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `hashed_password` - BCrypt hashed password
- `is_active` - Account status
- `created_at` - Account creation timestamp

### Vehicles Table
- `id` - Primary key
- `name` - Vehicle name/model
- `price` - Sale price
- `year` - Year of manufacture
- `mileage` - Current mileage
- `color` - Vehicle color
- `description` - Vehicle details
- `owner_id` - Foreign key to User
- `created_at` - Record creation timestamp
- `updated_at` - Last update timestamp

## Frontend Features

### Login Page
- User authentication with credentials
- Auto-redirect if already logged in
- Sign up link for new users
- Error messaging

### Sign Up Page
- New user registration
- Email validation
- Password confirmation
- Password length requirements (min 6 characters)

### Dashboard Section
- View key metrics (total vehicles, average price, inventory value)
- AI-powered query interface for instant insights
- Get recommendations based on current inventory

### Inventory Section
- Browse all vehicles in grid layout
- View detailed information for each vehicle
- Edit or delete vehicles
- Quick actions for each vehicle

### Analytics Section
- Visual distribution of vehicle prices
- Year-wise inventory breakdown
- Real-time data visualization

### Add Vehicle Section
- Easy-to-use form to add new vehicles
- Validation for all fields
- Immediate inventory update
- Immediate dashboard refresh

## Security Features

✅ Password Hashing with Bcrypt
✅ JWT Token-based Authentication
✅ User Data Isolation (each user only sees their vehicles)
✅ HTTPBearer Token validation
✅ Email validation
✅ CSRF protection ready
✅ Secure password requirements
✅ Token expiration (24 hours)

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with python-jose
- **Password Security**: Bcrypt hashing with passlib
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/ML**: Mistral LLM
- **Server**: Uvicorn (ASGI server)
- **Language**: Python 3.8+

## Configuration

Edit the `.env` file to customize settings:

```env
MISTRAL_API_KEY=your_key              # Your Mistral API key
SECRET_KEY=your-secret-key            # JWT secret (change in production!)
DEBUG=True                             # Enable debug mode
HOST=0.0.0.0                          # Server host
PORT=8000                             # Server port
```

## Troubleshooting

### Authentication Not Working
- Verify credentials are correct
- Check that user account exists
- Ensure SECRET_KEY is set in `.env`

### Database Issues
- Delete `vehicle_sales.db` to reset (will lose all data)
- Tables auto-create on first run
- Check file permissions in project directory

### Mistral API Not Working
- Verify your API key is correct in `.env`
- Check your Mistral account has available credits
- Review error message in browser console

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

- Each user's vehicles are isolated (owner_id enforcement)
- Frontend uses localStorage for JWT token storage
- Tokens expire after 24 hours
- All times stored in UTC
- Vehicles data is persistent in SQLite database
- Frontend uses vanilla JavaScript (no frameworks)

## Future Enhancements

- PostgreSQL support for production
- Multi-user dashboard with sharing
- Advanced filtering and search
- Export inventory to CSV/Excel
- Real-time notifications
- Multiple user roles (admin, dealer, viewer)
- Payment integration for sales
- Vehicle images/gallery
- Test drive scheduling
- Inventory forecasting with AI
- Mobile app version

## Deployment Notes

For production:
1. Change `SECRET_KEY` to a long random string
2. Set `DEBUG=False`
3. Use PostgreSQL instead of SQLite
4. Set up proper CORS if needed
5. Use HTTPS/SSL certificates
6. Set strong `MISTRAL_API_KEY`
7. Use environment-based configuration
8. Set up database backups
9. Monitor API usage and rate limiting
10. Use a production ASGI server like Gunicorn

## License

MIT License - Feel free to use and modify

## Support

For issues or questions:
1. Check that all dependencies are installed
2. Verify Mistral API key is valid
3. Ensure server is running on correct port
4. Check .env configuration
5. Review browser console for errors

## Repository

GitHub: https://github.com/soham2710/trial.git

---

**Happy selling! 🚗**

