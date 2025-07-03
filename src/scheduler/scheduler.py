import schedule
import time
import logging
from typing import Callable
from threading import Thread

logger = logging.getLogger(__name__)

class TranscriptScheduler:
    def __init__(self, check_function: Callable, interval_hours: int = 24):
        """
        Initialize the scheduler.
        
        Args:
            check_function: The function to run periodically
            interval_hours: Hours between checks (default 24)
        """
        self.check_function = check_function
        self.interval_hours = interval_hours
        self.running = False
    
    def start(self, run_immediately: bool = True):
        """
        Start the scheduler.
        
        Args:
            run_immediately: Whether to run the check function immediately (default True)
        """
        try:
            # Run immediately if requested
            if run_immediately:
                logger.info("Running initial check...")
                self.check_function()
            
            # Schedule periodic checks
            schedule.every(self.interval_hours).hours.do(self.check_function)
            
            logger.info(f"Scheduler started. Will check every {self.interval_hours} hours.")
            
            self.running = True
            # Keep the scheduler running
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user.")
            self.stop()
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        schedule.clear()
        logger.info("Scheduler stopped.")
    
    def run_once(self):
        """Run the check function once without scheduling."""
        try:
            logger.info("Running one-time check...")
            self.check_function()
            logger.info("One-time check completed.")
        except Exception as e:
            logger.error(f"Error during one-time check: {str(e)}")
            raise