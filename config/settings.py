import os
from dotenv import load_dotenv

load_dotenv()

# Jira Configuration
JIRA_SERVER = os.getenv('JIRA_SERVER', 'https://your-jira-instance.atlassian.net')
JIRA_USERNAME = os.getenv('JIRA_USERNAME', '')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', '')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY', 'RELEASE')

# Report Configuration
REPORT_OUTPUT_DIR = os.getenv('REPORT_OUTPUT_DIR', './reports')
LOG_DIR = os.getenv('LOG_DIR', './logs')

# Scheduler Configuration
SCHEDULE_INTERVAL_HOURS = int(os.getenv('SCHEDULE_INTERVAL_HOURS', '2'))

# Dashboard Configuration
DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '8000'))

# Ensure directories exist
os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

