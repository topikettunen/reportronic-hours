import json
import time

from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys

class Reportronic:
    def __init__(self,
                 driver=webdriver.Firefox()):
        self.driver = driver
        with open('./config/config-test.json') as config:
            data = json.load(config)
        self.url = data['reportronic']['url']
        self.user = data['reportronic']['user']
        self.password = data['reportronic']['password']
    
    def auth(self):
        self.driver.get(self.url)
        prompt = Alert(self.driver)
        prompt.send_keys(self.user + Keys.TAB + self.password)
        prompt.accept()

    def navigate_to_id(self, id):
        element_id = id
        element = self.driver.find_element_by_id(element_id)
        element.click()

    def wait_for_element_to_be_visible(self):
        pass
