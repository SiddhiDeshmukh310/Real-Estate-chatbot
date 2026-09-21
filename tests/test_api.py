import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

def test_health_check_endpoint(api_client):
    response = api_client.get('/api/health/')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['dataset_loaded'] is True
    assert data['row_count'] == 20

def test_analyze_endpoint_valid(api_client):
    response = api_client.post('/api/analyze/', {'query': 'Analyze Wakad'}, format='json')
    assert response.status_code == 200
    data = response.json()
    assert 'summary' in data
    assert 'chart' in data
    assert 'tables' in data
    assert 'Wakad' in data['areas']

def test_analyze_endpoint_empty(api_client):
    response = api_client.post('/api/analyze/', {'query': ''}, format='json')
    assert response.status_code == 400
