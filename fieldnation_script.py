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
import urllib

def stonum(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return None
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
def Counteroffer(link,driverr,payrate):
    driver=driverr
    driver.get(link)
    try:
        locator = (By.XPATH,f"//span[text()='Counter-offer']")
        Request=wait_for_element_to_be_visible_special(driver, locator)
        Request.click()
        """
        time.sleep(10)
        locator = (By.XPATH,f"//span[text()='Counter-offer']")
        Request=wait_for_element_to_be_visible_special(driver, locator)
        Request.click()
        
        """
        
        Acknowlege_locator = (By.XPATH,f"//input[@data-nw-file='PaySection']")
        
        Acknowledge=wait_for_element_to_be_visible_special(driver,Acknowlege_locator) 
        Acknowledge.click()

        paytype_locator = (By.XPATH,f"//span[@data-nw-file='SelectedValueDefault']")
        
        paytype=wait_for_element_to_be_visible_special(driver,paytype_locator) 
        print(paytype.text)

        if paytype.text=="Hourly":
             
             Acknowlege_locator = driver.find_element(By.ID,"pay-base-amount").clear()
             time.sleep(1)
             Acknowlege_locator = driver.find_element(By.ID,"pay-base-amount").send_keys(payrate)
            
        elif paytype.text=="Blended":
            time.sleep(1)
            payunits= driver.find_element(By.ID,"pay-base-units").get_attribute("value")
           
            time.sleep(1)
            Acknowlege_locator = driver.find_element(By.ID,"pay-base-amount").clear()
            new_payrate=payrate*stonum(payunits)
            
            time.sleep(1)
            Acknowlege_locator = driver.find_element(By.ID,"pay-base-amount").send_keys(new_payrate)
            time.sleep(1)

            Acknowlege_locator = driver.find_element(By.ID,"pay-additional-amount").clear()
            Acknowlege_locator = driver.find_element(By.ID,"pay-additional-amount").send_keys(payrate)

            

        
    
        """hourss= driver.find_element(By.XPATH,f"//span[@data-nw-file='Pay']").text
        print(hourss)
        hourss=hourss.split("hrs")[0]
        """
        
        #Acknowlege_locator = driver.find_element(By.ID,"pay-base-units").send_keys(hourss)
        Acknowlege_locator = driver.find_element(By.ID,"counter-offer-reason").send_keys("Due to the complexity of the job I will need more compensation to complete job")
        locator = driver.find_element(By.XPATH,f"//span[text()='Submit']").click()

        
        
    


    except Exception as e:
        print(f"No Request:{e} ")
def applytojobs(link,distance,payrate,paytotal,driverr,in_rate,in_ratio):
    c_totalpay=200
    c_payrate=stonum(in_rate)
    c_distance=28
    c_pay_dist_ratio=stonum(in_ratio)
    pay_dist_ratio=paytotal/distance
    driver=driverr
    duration=paytotal/payrate
    
    ideal_pay_distance_ratio=(c_payrate*duration)/distance
    if((payrate>=c_payrate) and (distance<=c_distance) and (pay_dist_ratio>=c_pay_dist_ratio)):
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

    elif((distance<c_distance) and ideal_pay_distance_ratio>c_pay_dist_ratio):
        #counter offer if distance is less than  max distance and fixing the pay would make it doable
        
        Counteroffer(link,driver,c_payrate)

    else:
        print("didnt make the cut")

  

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
        # Use custom data in the automation process
        email = self.custom_data.get('email')
        rate = self.custom_data.get('data')
        ratio = self.custom_data.get('automation')

        
        
        mongo_uri =  "mongodb+srv://fieldnationbot:" + urllib.parse.quote("REACH4gold@mongodb") + "@cluster0.v6yd5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        db_name = "gmail"  # Replace with your database name
        collection_name = email
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        self.driver.get(self.website_url)
        while True:
            
            
            
            


            unprocessed_links = collection.find({'used': False})

            for document in unprocessed_links:
                link = document['link']
                distance=document['distance']
                payrate=document['payrate']
                paytotal=document['paytotal']
                
                print(f"Processing link: {link}")
                applytojobs(link,distance,payrate,paytotal,self.driver,rate,ratio)

            # Mark the link as used
                collection.update_one(
                    {'_id': document['_id']},
                    {'$set': {'used': True}}
                )
                print(f"Marked link as used: {link}")
        



            
            logger.info(f"Running automation for user {self.user_id}")
            logger.info(f"Using email: {email}")
            
            logger.info(f"Using rate: {rate}")
            logger.info(f"Using ratio: {ratio}")
            # Add your automation logic here, using the custom data as needed
            
            # For example:
            # if email:
            #     email_field = self.driver.find_element(By.ID, 'email-input')
            #     email_field.send_keys(email)
            
            # if data:
            #     # Use the 'data' in your automation process
            #     pass

