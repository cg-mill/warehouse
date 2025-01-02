from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime
import os
import sys

from Inventory import Crop


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('--window-size=1000,750')

URL = os.environ.get('GOHACCP_URL')
USERNAME = os.environ.get('GOHACCP_EMAIL')
PASSWORD = os.environ.get('GOHACCP_PASS')
INITIALS = 'CG'


class GoHAACP: #TODO loop try to click elements, then wait if not found
    def __init__(self, username: str, password: str, initials: str) -> None:
        self.weekday = datetime.now().weekday()
        self.username = username
        self.password = password
        self.initials = initials

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url=URL)
        time.sleep(4)
        self.login()


    def login(self):
        inputs = self.driver.find_elements(By.TAG_NAME, value='input')
        inputs[0].send_keys(self.username)
        inputs[1].send_keys(self.password)
        login_button = self.driver.find_element(By.XPATH, value='//*[@id="root"]/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div/div/div[1]/div[1]/div[3]/div')
        login_button.click()
        time.sleep(5) 
        # TODO implement nosuchelement exeption in loops to speed up sleep times


    def new_report(self):

        self.new_report_button = self.driver.find_element(By.XPATH, value='//div[contains(text(), "New Reports")]')
        
        self.new_report_button.click()
        time.sleep(8)


    def submit_report(self):
        send_button = self.driver.find_element(By.XPATH, value='//div[contains(text(), "Send Report")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", send_button)
        time.sleep(2)
        send_button.click()
        time.sleep(20)


class EODChecklist(GoHAACP):
    def __init__(self, username: str, password: str, initials: str) -> None:
        super().__init__(username, password, initials)
        self.new_report()
        self.warehouse_checklist()
        if self.weekday == 3:
            print('No Front Checklist on Thursdays')
            self.driver.quit()
        else:
            self.new_report()
            self.front_checklist()
            self.driver.quit()


    def front_checklist(self):
        start = self.driver.find_element(By.XPATH, value='//div[contains(text(), "SSOP-R-CF Daily Closing Log - General Facility - Front")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", start)
        time.sleep(1)
        start.click()
        time.sleep(3)
        initial_inputs = self.driver.find_elements(By.TAG_NAME, value='textarea')
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, value='[style="margin-left: 10px; margin-right: 5px; width: 22px; height: 22px; border-style: solid; border-color: rgb(244, 152, 30); border-width: 1px; border-radius: 4px;"]')
        # checkbox_iterations = [(0,3),(3,8),(8,12),(12,16),(16,16)]
        checkbox_iterations = [(1,4),(4,9),(9,13),(13,17),(17,18)]

        for i in range(5):
            initial_inputs[i].send_keys(self.initials)
            time.sleep(0.5)
            # for iteration in range(*checkbox_iterations[i]): # * is unpacker
            for iteration in range(checkbox_iterations[i][0], checkbox_iterations[i][1]):
                checkboxes[iteration].click()    

        self.submit_report()
        print('Front Checklist Complete')


    def warehouse_checklist(self):
        start = self.driver.find_element(By.XPATH, value='//div[contains(text(), "SSOP-R-CF Daily Closing Log - Warehouse")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", start)
        time.sleep(1)
        start.click()
        time.sleep(3)
        initail_inputs = self.driver.find_element(By.TAG_NAME, value='textarea')
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, value='[style="margin-left: 10px; margin-right: 5px; width: 22px; height: 22px; border-style: solid; border-color: rgb(244, 152, 30); border-width: 1px; border-radius: 4px;"]')
        for i in range(1,21):
            if i > 5:
                self.driver.execute_script("arguments[0].scrollIntoView();", checkboxes[i])
            time.sleep(0.25)
            checkboxes[i].click()
        initail_inputs.send_keys(self.initials)

        self.submit_report()
        print('Warehouse Checklist Complete')


class ReceivingForm(GoHAACP):
    def __init__(self, username: str, password: str, initials: str, crop: Crop) -> None:
        super().__init__(username, password, initials)
        self.crop = crop
        self.new_report()
        self.raw_materials_form()


    def raw_materials_form(self):
        start = self.driver.find_element(By.XPATH, value='//div[contains(text(), "Receiving Form - Raw Materials")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", start)

        pass#TODO


if __name__ == "__main__":
    
    eod = EODChecklist(username=USERNAME, password=PASSWORD, initials=INITIALS)
#     # rec_form = ReceivingForm(username=USERNAME, password=PASSWORD, initials=INITIALS, crop=Crop())


