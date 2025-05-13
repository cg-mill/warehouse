from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.remote.webelement import WebElement
import time
from datetime import datetime
import json

from Inventory import Crop


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('--window-size=1000,750')

with open('Production/gohaccp.json') as f:
    login_data = json.load(f)

URL = login_data['url']
USERNAME = login_data['username']
PASSWORD = login_data['password']
INITIALS = 'CG'


class GoHAACP: #TODO loop try to click elements, then wait if not found
    def __init__(self, username: str, password: str, initials: str) -> None:
        self.weekday = datetime.now().weekday()
        self.username = username
        self.password = password
        self.initials = initials

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url=URL)
        self.login()


    def login(self):
        inputs = []
        while inputs == []:
            inputs = self.driver.find_elements(By.TAG_NAME, value='input')
            time.sleep(0.5)
        inputs[0].send_keys(self.username)
        inputs[1].send_keys(self.password)
        login_button = self.driver.find_element(By.XPATH, value='//*[@id="root"]/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div/div/div[1]/div[1]/div[3]/div')
        self.check_click(login_button)
        # login_button.click()
        # time.sleep(5) #FIXME delete sleeps if 
        # TODO implement nosuchelement exeption in loops to speed up sleep times


    def check_click(self, button:WebElement) -> None:
        max_iterations = 100
        for _ in range(max_iterations):
            try:
                button.click()
                time.sleep(1)
                return
            except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                time.sleep(0.5)
        print(f'<Click> {button.accessible_name} timed out...')


    def check_for_item(self, item:str) -> None:
        max_iterations = 100
        for _ in range(max_iterations):
            try:
                self.new_report_button = self.driver.find_element(By.XPATH, value=f'//div[contains(text(), "{item}")]')
                time.sleep(1)
                return
            except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                time.sleep(0.5)
        print(f'check for: "{item}" timed out...')


    def check_for_items(self):
        pass #TODO check for list of items like in self.login


    def new_report(self):
        self.check_for_item('New Reports')
        self.check_click(self.new_report_button)


    def submit_report(self):
        send_button = self.driver.find_element(By.XPATH, value='//div[contains(text(), "Send Report")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", send_button)
        time.sleep(1)
        self.check_click(send_button)
        # send_button.click()
        self.check_for_item('New Reports')
        # time.sleep(20)


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
        log_name = 'SSOP-R-CF Daily Closing Log - General Facility - Front'
        self.check_for_item(log_name)
        start = self.driver.find_element(By.XPATH, value=f'//div[contains(text(), "{log_name}")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", start)
        time.sleep(1)
        # start.click()
        self.check_click(start)
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
        log_name = 'SSOP-R-CF Daily Closing Log - Warehouse'
        self.check_for_item(log_name)
        start = self.driver.find_element(By.XPATH, value=f'//div[contains(text(), "{log_name}")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", start)
        time.sleep(1)
        self.check_click(start)
        # start.click()
        time.sleep(3)
        initail_input = self.driver.find_element(By.TAG_NAME, value='textarea')
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, value='[style="margin-left: 10px; margin-right: 5px; width: 22px; height: 22px; border-style: solid; border-color: rgb(244, 152, 30); border-width: 1px; border-radius: 4px;"]')
        for i in range(1,21):
            if i > 5:
                self.driver.execute_script("arguments[0].scrollIntoView();", checkboxes[i])
            time.sleep(0.25)
            checkboxes[i].click()
        initail_input.send_keys(self.initials)

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


