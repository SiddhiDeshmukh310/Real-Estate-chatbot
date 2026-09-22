import os
import sys
import django
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'realestate_chatbot.settings'
django.setup()

class MockLLMProvider:
    def __init__(self, mode='valid'):
        self.mode = mode

    def parse(self, query: str):
        q = query.lower()
        if self.mode == 'invalid_schema':
            return {'operation': 'invalid_operation_name', 'metric': 'flat_rate', 'localities': ['Wakad']}
        if self.mode == 'out_of_whitelist':
            return {'operation': 'locality_summary', 'metric': 'flat_rate', 'localities': ['Mumbai']}
        
        if 'compare' in q:
            return {
                'operation': 'compare',
                'metric': 'flat_rate',
                'localities': ['Wakad', 'Akurdi'],
                'start_year': 2020,
                'end_year': 2024,
                'group_by': 'location',
                'is_valid': True
            }
        elif 'best' in q:
            return {
                'operation': 'top_n',
                'metric': 'flat_rate',
                'localities': ['Wakad', 'Aundh', 'Akurdi', 'Ambegaon Budruk'],
                'start_year': 2020,
                'end_year': 2024,
                'group_by': 'location',
                'is_valid': True
            }
        else:
            return {
                'operation': 'locality_summary',
                'metric': 'flat_rate',
                'localities': ['Wakad'],
                'start_year': 2020,
                'end_year': 2024,
                'group_by': 'year',
                'is_valid': True
            }

@pytest.fixture
def mock_llm_valid():
    return MockLLMProvider('valid')

@pytest.fixture
def mock_llm_invalid():
    return MockLLMProvider('invalid_schema')

@pytest.fixture
def mock_llm_out_of_whitelist():
    return MockLLMProvider('out_of_whitelist')
