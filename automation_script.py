
from abc import ABC, abstractmethod
import logging
from selenium import webdriver
from threading import Thread
from selenium.webdriver.chrome.options import Options


logger = logging.getLogger(__name__)
class AutomationScript(ABC):
    def __init__(self, website_url, user_id):
        self.website_url = website_url
        self.driver = None
        self.user_id = user_id
        


    @abstractmethod
    def require_authentication(self):
        pass

    @abstractmethod
    def is_logged_on(self):
        pass
    
    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def automation_process(self):
        pass

    def setup_driver_with_profile(self):
        chrome_options = Options()
        selenium_url = f"http://chrome-{self.user_id}:4444/wd/hub"
        chrome_options.add_argument("user-data-dir=/home/seluser/chrome-profile")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        try:
            self.driver = webdriver.Remote(command_executor=selenium_url, options=chrome_options)
        except Exception as e:
            logger.info(f"Error setting up driver: {str(e)}")
       
    def run(self, stop_event):
        if not self.driver:
            self.setup_driver_with_profile()
        logger.info(self.driver)
        try:
            self.driver.get(self.website_url)
            
            if self.require_authentication():
                if not self.is_logged_on():
                    logger.info("User is not logged in. Logging in...")
                    self.login()
            logger.info("user is logged in, starting automation...")

            automation_thread = Thread(target=self.automation_process)
            automation_thread.start()
            stop_event.wait()

            logger.info(f"Stop event received for user {self.user_id}")

            # Give the automation thread a chance to finish gracefully
            automation_thread.join(timeout=4)  

            if automation_thread.is_alive():
                logger.warning(f"Automation thread for user {self.user_id} did not finish in time, forcing stop")
        except Exception as e:
            logger.error(f"Error in automation for user {self.user_id}: {str(e)}")
        finally:
            self.driver.quit()