# Set environment variables
$env:PYTHONPATH = 'C:\Projects\ai-news-automation'
$env:NEWS_API_KEY = '556025e23b5e4d6b94b4780a4e89fdd8'

# Run tests and capture output
$output = python -m pytest tests/test_backend_integration.py -v --log-cli-level=INFO *>&1
$output | Out-File -FilePath "test_output.txt"
Get-Content "test_output.txt"
