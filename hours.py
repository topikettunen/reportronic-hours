#!/usr/bin/env python3

# Copyright (c) 2018 Topi Kettunen <topi@topikettunen.com>

import json
import logging
import time

from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys

class Reportronic:
    def __init__(self,
                 driver=webdriver.Firefox()):
        self.url = url
        self.driver = driver
        with open('config.json') as config:
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

class ReportonicCLI:
    def __init__(self):
        self.repo = Reportronic()
        self.logger = logging.getLogger()
        self.handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def login_to_reportronic(self):
        self.logger.info('Trying to log in to Reportronic.')
        self.repo.auth()
        self.logger.info('Login successful.')

    def locate_and_navigate_to_element_with_id(self, element_id):
        self.logger.info(
            'Trying to find element with id of {}'.format(element_id))
        self.repo.navigate_to_id(element_id)
        self.logger.info('Element found.')

    def take_screenshot(self):
        self.logger.info('Taking a screenshot.')
        screenshot_filename = datetime.now().strftime("%Y%m%d-%H%M%S-hours.png")
        self.repo.driver.save_screenshot(screenshot_filename)
        self.logger.info('Screenshot saved as {}'.format(screenshot_filename))
        
    def main(self):
        try:
            self.login_to_reportronic()
            time.sleep(5)
            browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
            self.locate_and_navigate_to_element_with_id(browse_worktime_id)
            time.sleep(5)
            show_worktime_announcement_id = 'prlWTEP_uwtWorkTimetd2'
            self.locate_and_navigate_to_element_with_id(show_worktime_announcement_id)
            time.sleep(5)
            send_for_approval_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_lnkTeeIlmoitus'
            self.locate_and_navigate_to_element_with_id(send_for_approval_id)
            time.sleep(5)
            worktime_announcement_next_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_rlbNext'
            self.locate_and_navigate_to_element_with_id(worktime_announcement_next_id)
            time.sleep(5)
            worktime_announcement_save_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_rlbSave'
            self.locate_and_navigate_to_element_with_id(worktime_announcement_save_id)
            time.sleep(5)
        except NoSuchElementException:
            self.logger.info('Element not found')
        finally:
            self.take_screenshot()
            self.repo.driver.quit()
            
if __name__ == '__main__':
    repo = ReportonicCLI()
    repo.main()
