import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from automation_script import AutomationScript

logger = logging.getLogger(__name__)


class FieldNationAutomation(AutomationScript):
    def __init__(self, user_id):
        super().__init__("https://app.fieldnation.com", user_id)

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
            



        
