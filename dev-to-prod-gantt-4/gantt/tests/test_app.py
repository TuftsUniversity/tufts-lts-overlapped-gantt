LASK_SECRET_KEY=your_secret_key
EARER_ACCESS_TOKEN=your_bearer_access_token
ANTT_CREDENTIALS={"username": "your_username", "password": "your_password"}
``

## Step 4: Add Basic Tests

reate a `tests` directory and add a basic test for the application.

``diff
import pytest
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Gantt Chart Generator' in response.data

def test_login(client):
    """Test the login page."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_generate(client):
    """Test the generate endpoint."""
    response = client.post('/generate', json={'projects_df': {}})
    assert response.status_code == 400
    assert b'No data provided' in response.data

def test_fetch_api(client):
    """Test the fetchAPI endpoint."""
    response = client.get('/fetchAPI')
    assert response.status_code == 400