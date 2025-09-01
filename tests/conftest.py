"""
PyTest configuration file
"""
import os
import pytest
import vcr

# Configure VCR
@pytest.fixture(scope='module')
def vcr_config():
    return {
        'filter_headers': ['authorization', 'api-key'],  # Don't record API keys
        'record_mode': 'once',
        'cassette_library_dir': 'tests/cassettes'
    }

# Create cassettes directory if it doesn't exist
if not os.path.exists('tests/cassettes'):
    os.makedirs('tests/cassettes')
