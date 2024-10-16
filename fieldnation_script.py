import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from automation_script import AutomationScript
import threading

logger = logging.getLogger(__name__)


class FieldNationAutomation(AutomationScript):
    def __init__(self, user_id, custom_data):
        super().__init__("https://app.fieldnation.com", user_id)
        self.custom_data = custom_data

    def require_authentication(self):
        return True

    def is_logged_on(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@title='Received Payments']"))  
            )
            return True
        except TimeoutException:
            return False

    def login(self):
        logger.info("User is not logged in. Please log in manually.")
        try:
            WebDriverWait(self.driver, 500).until(
                EC.presence_of_element_located((By.XPATH, "//div[@title='Received Payments']"))  
            )
            return True
        except TimeoutException:
            return False

    def automation_process(self):
        while True:
            self.driver.get(self.website_url)
            time.sleep(10)
            
            # Use custom data in the automation process
            email = self.custom_data.get('email')
            data = self.custom_data.get('data')
            
            logger.info(f"Running automation for user {self.user_id}")
            logger.info(f"Using email: {email}")
            logger.info(f"Using data: {data}")
            
            # Add your automation logic here, using the custom data as needed
            
            # For example:
            # if email:
            #     email_field = self.driver.find_element(By.ID, 'email-input')
            #     email_field.send_keys(email)
            
            # if data:
            #     # Use the 'data' in your automation process
            #     pass

