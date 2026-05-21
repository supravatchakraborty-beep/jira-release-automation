import logging
import schedule
import time
from typing import Callable
from datetime import datetime
from config.settings import SCHEDULE_INTERVAL_HOURS, LOG_DIR
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Scheduler for periodic Jira task monitoring"""
    
    def __init__(self):
        self.schedule_interval = SCHEDULE_INTERVAL_HOURS
        self.is_running = False
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    def schedule_task(self, job_func: Callable, interval: int = None) -> None:
        """
        Schedule a task to run at regular intervals
        
        Args:
            job_func: Function to execute
            interval: Interval in hours (uses default if not specified)
        """
        interval = interval or self.schedule_interval
        
        schedule.every(interval).hours.do(self._run_job, job_func)
        logger.info(f"Task scheduled to run every {interval} hours")
    
    def _run_job(self, job_func: Callable) -> None:
        """
        Wrapper for job execution with error handling
        
        Args:
            job_func: Function to execute
        """
        try:
            logger.info(f"Starting scheduled job: {job_func.__name__}")
            job_func()
            logger.info(f"Completed scheduled job: {job_func.__name__}")
        except Exception as e:
            logger.error(f"Error in scheduled job {job_func.__name__}: {str(e)}", exc_info=True)
    
    def start(self, blocking: bool = True) -> None:
        """
        Start the scheduler
        
        Args:
            blocking: Whether to block execution (True for continuous running)
        """
        self.is_running = True
        logger.info("Scheduler started")
        
        if blocking:
            try:
                while self.is_running:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                self.stop()
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}", exc_info=True)
                self.stop()
        else:
            logger.info("Scheduler started in non-blocking mode")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def get_next_run(self) -> datetime:
        """
        Get the time of the next scheduled run
        
        Returns:
            Datetime of next run
        """
        if schedule.jobs:
            return schedule.jobs[0].next_run
        return None
    
    def run_once(self, job_func: Callable) -> None:
        """
        Run a job immediately without scheduling
        
        Args:
            job_func: Function to execute
        """
        self._run_job(job_func)

