#!/usr/bin/env python3

import logging
import sys
from pathlib import Path
from datetime import datetime
from src.jira_client import JiraClient
from src.report_generator import ReportGenerator
from src.scheduler import TaskScheduler
from config.settings import LOG_DIR

# Setup logging
log_dir = Path(LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"main_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def fetch_and_report():
    """
    Main function to fetch release tasks and generate reports
    """
    try:
        logger.info("Starting Jira release task automation...")
        
        # Initialize clients
        jira_client = JiraClient()
        report_gen = ReportGenerator()
        
        # Fetch tasks and statistics
        logger.info("Fetching release tasks...")
        tasks = jira_client.get_release_tasks()
        statistics = jira_client.get_statistics()
        
        logger.info(f"Retrieved {statistics['total_tasks']} tasks")
        
        # Generate reports
        logger.info("Generating reports...")
        html_report = report_gen.generate_html_dashboard(tasks, statistics)
        json_report = report_gen.generate_json_report(tasks, statistics)
        md_report = report_gen.generate_markdown_report(tasks, statistics)
        
        logger.info(f"Reports generated:")
        logger.info(f"  - HTML: {html_report}")
        logger.info(f"  - JSON: {json_report}")
        logger.info(f"  - Markdown: {md_report}")
        
        # Log statistics
        logger.info(f"Task Statistics:")
        logger.info(f"  - Total: {statistics['total_tasks']}")
        logger.info(f"  - Overdue: {statistics['overdue_tasks']}")
        logger.info(f"  - By Status: {statistics['by_status']}")
        logger.info(f"  - By Priority: {statistics['by_priority']}")
        
        logger.info("Automation completed successfully")
        
    except Exception as e:
        logger.error(f"Error during automation: {str(e)}", exc_info=True)
        sys.exit(1)

def main():
    """
    Main entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Jira Release Task Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run once and generate reports
  python main.py --once
  
  # Start continuous scheduler
  python main.py --schedule
  
  # Fetch specific status tasks
  python main.py --status 'In Progress'
  
  # Fetch overdue tasks
  python main.py --overdue
        """
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and generate reports'
    )
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Start continuous scheduler'
    )
    parser.add_argument(
        '--status',
        type=str,
        help='Fetch tasks with specific status'
    )
    parser.add_argument(
        '--overdue',
        action='store_true',
        help='Fetch overdue tasks'
    )
    
    args = parser.parse_args()
    
    try:
        if args.once or (not args.schedule and not args.status and not args.overdue):
            # Default: run once
            fetch_and_report()
        
        elif args.schedule:
            # Start scheduler
            logger.info("Starting scheduled automation...")
            scheduler = TaskScheduler()
            scheduler.schedule_task(fetch_and_report)
            scheduler.start(blocking=True)
        
        elif args.status:
            # Fetch specific status
            logger.info(f"Fetching tasks with status: {args.status}")
            jira_client = JiraClient()
            tasks = jira_client.get_tasks_by_status(args.status)
            logger.info(f"Found {len(tasks)} tasks with status '{args.status}'")
            for task in tasks:
                logger.info(f"  - {task['key']}: {task['summary']}")
        
        elif args.overdue:
            # Fetch overdue tasks
            logger.info("Fetching overdue tasks...")
            jira_client = JiraClient()
            tasks = jira_client.get_overdue_tasks()
            logger.info(f"Found {len(tasks)} overdue tasks")
            for task in tasks:
                logger.info(f"  - {task['key']}: {task['summary']} (Due: {task.get('due_date', 'N/A')})")
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

