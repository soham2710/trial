// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    loadDashboard();
    loadVehicles();
});

// ==================== Authentication ====================
function checkAuthentication() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');

    if (!token) {
        // Redirect to login if not authenticated
        window.location.href = '/login';
        return;
    }

    // Display username in header
    document.getElementById('username-display').textContent = `Logged in as: ${username}`;
}

function getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

function handleLogout() {
    // Clear stored data
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');

    // Redirect to login
    window.location.href = '/login';
}

// ==================== Section Navigation ====================
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionId).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');

    // Reload analytics if that section is shown
    if (sectionId === 'analytics') {
        loadAnalytics();
    }
}

// ==================== Load Dashboard Data ====================
async function loadDashboard() {
    try {
        const response = await fetch('/api/sales-summary', {
            headers: getAuthHeader()
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        const data = await response.json();

        document.getElementById('total-vehicles').textContent = data.total_vehicles;
        document.getElementById('avg-price').textContent = `$${data.avg_price.toLocaleString()}`;
        document.getElementById('total-value').textContent = `$${data.total_inventory_value.toLocaleString()}`;
        
        if (data.total_vehicles > 0) {
            document.getElementById('price-range').textContent = `$${data.price_range.min.toLocaleString()} - $${data.price_range.max.toLocaleString()}`;
        } else {
            document.getElementById('price-range').textContent = 'N/A';
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ==================== Load Vehicles ====================
async function loadVehicles() {
    try {
        const response = await fetch('/api/vehicles', {
            headers: getAuthHeader()
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        const data = await response.json();
        const vehiclesList = document.getElementById('vehicles-list');
        vehiclesList.innerHTML = '';

        if (data.vehicles.length === 0) {
            vehiclesList.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #6b7280;">No vehicles added yet. Create one in the "Add Vehicle" section.</p>';
            return;
        }

        data.vehicles.forEach(vehicle => {
            const card = document.createElement('div');
            card.className = 'vehicle-card';
            card.innerHTML = `
                <div class="vehicle-header">
                    <h3>${vehicle.name}</h3>
                    <p class="vehicle-price">$${vehicle.price.toLocaleString()}</p>
                </div>
                <div class="vehicle-body">
                    <div class="vehicle-details">
                        <div class="detail">
                            <div class="detail-label">Year</div>
                            <div class="detail-value">${vehicle.year}</div>
                        </div>
                        <div class="detail">
                            <div class="detail-label">Mileage</div>
                            <div class="detail-value">${vehicle.mileage.toLocaleString()} mi</div>
                        </div>
                        <div class="detail">
                            <div class="detail-label">Color</div>
                            <div class="detail-value">${vehicle.color}</div>
                        </div>
                        <div class="detail">
                            <div class="detail-label">ID</div>
                            <div class="detail-value">#${vehicle.id}</div>
                        </div>
                    </div>
                    <p class="vehicle-description">${vehicle.description || 'No description'}</p>
                    <div class="vehicle-actions">
                        <button class="btn btn-primary" onclick="editVehicle(${vehicle.id})">Edit</button>
                        <button class="btn btn-danger" onclick="deleteVehicle(${vehicle.id})">Delete</button>
                    </div>
                </div>
            `;
            vehiclesList.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading vehicles:', error);
    }
}

// ==================== Analyze Query with Mistral ====================
async function analyzeQuery() {
    const query = document.getElementById('analysis-query').value.trim();
    
    if (!query) {
        alert('Please enter a question');
        return;
    }

    const resultBox = document.getElementById('analysis-result');
    const loadingBox = document.getElementById('analysis-loading');
    
    resultBox.style.display = 'none';
    loadingBox.style.display = 'block';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: getAuthHeader(),
            body: JSON.stringify({ question: query })
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error analyzing query');
        }

        const data = await response.json();
        loadingBox.style.display = 'none';
        document.getElementById('analysis-text').textContent = data.analysis;
        resultBox.style.display = 'block';

    } catch (error) {
        console.error('Error analyzing query:', error);
        loadingBox.style.display = 'none';
        alert(`Error: ${error.message}. Make sure MISTRAL_API_KEY is set in .env file.`);
    }
}

// ==================== Add Vehicle ====================
async function handleAddVehicle(event) {
    event.preventDefault();

    const vehicle = {
        name: document.getElementById('vehicle-name').value,
        price: parseFloat(document.getElementById('vehicle-price').value),
        year: parseInt(document.getElementById('vehicle-year').value),
        mileage: parseFloat(document.getElementById('vehicle-mileage').value),
        color: document.getElementById('vehicle-color').value,
        description: document.getElementById('vehicle-description').value
    };

    try {
        const response = await fetch('/api/vehicles', {
            method: 'POST',
            headers: getAuthHeader(),
            body: JSON.stringify(vehicle)
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        if (response.ok) {
            alert('Vehicle added successfully!');
            event.target.reset();
            loadVehicles();
            loadDashboard();
        } else {
            alert('Error adding vehicle');
        }
    } catch (error) {
        console.error('Error adding vehicle:', error);
        alert('Error adding vehicle');
    }
}

// ==================== Edit Vehicle ====================
async function editVehicle(vehicleId) {
    alert(`Edit functionality for vehicle ${vehicleId} would be implemented here`);
    // In a full implementation, this would open a modal with the vehicle details
}

// ==================== Delete Vehicle ====================
async function deleteVehicle(vehicleId) {
    if (!confirm('Are you sure you want to delete this vehicle?')) {
        return;
    }

    try {
        const response = await fetch(`/api/vehicles/${vehicleId}`, {
            method: 'DELETE',
            headers: getAuthHeader()
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        if (response.ok) {
            alert('Vehicle deleted successfully!');
            loadVehicles();
            loadDashboard();
        } else {
            alert('Error deleting vehicle');
        }
    } catch (error) {
        console.error('Error deleting vehicle:', error);
        alert('Error deleting vehicle');
    }
}

// ==================== Load Analytics ====================
async function loadAnalytics() {
    try {
        const response = await fetch('/api/vehicles', {
            headers: getAuthHeader()
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        const data = await response.json();
        const vehicles = data.vehicles;

        if (vehicles.length === 0) {
            return;
        }

        drawPriceDistribution(vehicles);
        drawYearDistribution(vehicles);

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ==================== Draw Price Distribution ====================
function drawPriceDistribution(vehicles) {
    const priceRanges = [
        { min: 0, max: 25000, label: '<$25k' },
        { min: 25000, max: 35000, label: '$25-35k' },
        { min: 35000, max: 50000, label: '$35-50k' },
        { min: 50000, max: Infinity, label: '>$50k' }
    ];

    const counts = priceRanges.map(range => 
        vehicles.filter(v => v.price >= range.min && v.price < range.max).length
    );

    const maxCount = Math.max(...counts, 1);
    const container = document.getElementById('price-distribution');
    container.innerHTML = '';

    priceRanges.forEach((range, index) => {
        const bar = document.createElement('div');
        const height = (counts[index] / maxCount) * 100;
        bar.className = 'bar';
        bar.style.height = `${height}%`;
        bar.title = `${range.label}: ${counts[index]} vehicles`;
        bar.innerHTML = `<span style="font-size: 0.75rem; font-weight: bold;">${counts[index]}</span>`;
        container.appendChild(bar);
    });
}

// ==================== Draw Year Distribution ====================
function drawYearDistribution(vehicles) {
    const years = {};
    vehicles.forEach(v => {
        years[v.year] = (years[v.year] || 0) + 1;
    });

    const sortedYears = Object.entries(years).sort((a, b) => a[0] - b[0]);
    const maxCount = Math.max(...sortedYears.map(y => y[1]), 1);
    const container = document.getElementById('year-distribution');
    container.innerHTML = '';

    sortedYears.forEach(([year, count]) => {
        const bar = document.createElement('div');
        const height = (count / maxCount) * 100;
        bar.className = 'bar';
        bar.style.height = `${height}%`;
        bar.title = `${year}: ${count} vehicles`;
        bar.innerHTML = `<span style="font-size: 0.75rem; font-weight: bold;">${count}</span>`;
        container.appendChild(bar);
    });
}
