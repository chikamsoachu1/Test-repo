import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from automation_script import AutomationScript
import threading
import pymongo
from selenium.webdriver.common.action_chains import ActionChains
import re

def wait_for_element_to_be_visible(driver, locator, timeout=60):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        print("Element is visible, proceeding with the next step.")
        return element
    except TimeoutException:
        print("Element was not visible within the timeout period.")
        return None
    
def wait_for_element_to_be_visible_special(driver, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        print("Element is visible, proceeding with the next step.")
        return element
    except TimeoutException:
        print("Element was not visible within the timeout period.")
        return None
def hourlypay(pay):
    if "hourly" in pay:
        pay = pay.split("$")[2].split("/")[0]
        pay = pay.replace(",", "")  # Remove commas
        return float(pay)
    return None

def fixedpay(pay):
    if "fixed" in pay:
        pay = pay.split("$")[2]
        pay = pay.replace(",", "")  # Remove commas
        return float(pay)
    return None
def applytojobs(link,distance,payrate,paytotal,driverr):
    c_totalpay=200
    c_payrate=45
    c_distance=25
    c_pay_dist_ratio=8.5
    pay_dist_ratio=paytotal/distance
    driver=driverr

    if((payrate<c_payrate) or (distance>c_distance) or (pay_dist_ratio<c_pay_dist_ratio)):
        
        print(link)
        print("print didnt make the cut")
    else:
        driver.get(link)
       
        if "Routed" in link:
            try:
                accept_locator = (By.XPATH,f"//span[text()='Accept']")
                accept=wait_for_element_to_be_visible_special(driver,accept_locator)
                accept.click()
                try:
                    Acknowlege_locator = (By.XPATH,f"//span[text()='Acknowledge And Accept']")
                    Acknowledge=wait_for_element_to_be_visible_special(driver,Acknowlege_locator) 
                    Acknowledge.click()
                except:


                    try:
                        Acknowlege_locator = (By.XPATH,f"//span[text()='Set And Accept']")
                        Acknowledge=wait_for_element_to_be_visible_special(driver,Acknowlege_locator) 
                        Acknowledge.click()
                    except:
                        try:
                            Acknowlege_locator = (By.XPATH,f"//span[text()='Set Start Time Later']")
                            Acknowledge=wait_for_element_to_be_visible_special(driver,Acknowlege_locator) 
                            Acknowledge.click()
                        except:
                            print("no  tools ")


            except Exception as e:
                print(f"No Request:{e} ")

       
        else:


         
            try:
                locator = (By.XPATH,f"//span[text()='Request']")
                Request=wait_for_element_to_be_visible_special(driver, locator)
                Request.click()
                try:
                    Acknowlege_locator = (By.XPATH,f"//span[text()='Acknowledge and Request']")
                    Acknowledge=wait_for_element_to_be_visible_special(driver,Acknowlege_locator) 
                    Acknowledge.click()
                except:
                    try:
                        Acknowlege_locator = (By.XPATH,f"//span[text()='Request Without Start Time']")
                        Acknowledge=wait_for_element_to_be_visible_special(driver,Acknowlege_locator) 
                        Acknowledge.click()
                    except:
                        print("no  tools ")


            except Exception as e:
                print(f"No Request:{e} ")

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
        mongo_uri = "mongodb+srv://fiverrtest1012:A5zOSyMdUT1Ay5bs@cluster0.aeo5n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        db_name = "gmail"  # Replace with your database name
        collection_name = "links"
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        self.driver.get(self.website_url)
        while True:
            
            
            
            # Use custom data in the automation process
            email = self.custom_data.get('email')
            data = self.custom_data.get('data')



            unprocessed_links = collection.find({'used': False})

            for document in unprocessed_links:
                link = document['link']
                distance=document['distance']
                payrate=document['payrate']
                paytotal=document['paytotal']
                
                print(f"Processing link: {link}")
                applytojobs(link,distance,payrate,paytotal,self.driver)

            # Mark the link as used
            self.collection.update_one(
                {'_id': document['_id']},
                {'$set': {'used': True}}
            )
            print(f"Marked link as used: {link}")
        



            
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

