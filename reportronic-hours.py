#!/usr/bin/env python3

# Copyright (c) 2018 Topi Kettunen <topi@topikettunen.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import logging
import os
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys

class Reportronic:
    def __init__(self,
                 driver=webdriver.Firefox()):
        self.driver = driver
        absolute_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(absolute_path, "./config-test.json")
        with open(config_path) as config:
            data = json.load(config)
        self.url = data['reportronic']['url']
        self.user = data['reportronic']['user']
        self.password = data['reportronic']['password']
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)
        self.logger.setLevel(logging.INFO)
    
    def login_to_reportronic(self):
        self.logger.info('Trying to log in to Reportronic.')        
        self.driver.get(self.url)
        prompt = Alert(self.driver)
        prompt.send_keys(self.user + Keys.TAB + self.password)
        prompt.accept()
        self.logger.info('Login successful.') 

    def navigate_to_id(self, element_id):
        self.logger.info(
            'Trying to find element with id of {}'.format(element_id))       
        element = self.driver.find_element_by_id(element_id)
        element.click()
        self.logger.info('Element found')

    def click_option_value_from_dropdown_menu(self, option_value):
        self.logger.info(
            'Trying to find option 9996  OPETUS JA OHJAUS 408 HETI PVÄ 100 Tutkintokoulutus from dropdown')
        xpath = "//option[@value=" + option_value + "]"
        self.driver.find_element_by_xpath(xpath).click()
        self.logger.info('Option found')

    def save_working_hours(self):
        self.logger.info('Saving working hours')
        element = self.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_rlbSave')
        element.click()
        self.logger.info('Working hours saved')

    def wait_for_element_to_be_visible(self):
        pass

    def take_screenshot(self):
        self.logger.info('Taking a screenshot.')
        screenshot_filename = datetime.now().strftime("%Y%m%d-%H%M%S-hours.png")
        self.repo.driver.save_screenshot(screenshot_filename)
        self.logger.info('Screenshot saved as {}'.format(screenshot_filename))

class Mail:
    def __init__(self):
        absolute_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(absolute_path, "./config-test.json")
        with open(config_path) as config:
            data = json.load(config)
        self.mail_user = data['mail']['mail_user']
        self.password = data['mail']['password']
        self.mail_to = data['mail']['mail_to']

    def mail_body(self):
        msg = MIMEText('Hello, World')
        msg['Subject'] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S Reportronic Hours Output")
        msg['From'] = self.mail_user
        msg['To'] = self.mail_to
        return msg

    def send_mail(self):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.mail_user, self.password)
        msg = self.mail_body()
        server.sendmail(self.mail_user, self.mail_to, msg.as_string())

class ScriptRuns:
    def monthly(self):
        repo = Reportronic()
        repo.login_to_reportronic()
        time.sleep(10)
        browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
        repo.navigate_to_id(browse_worktime_id)
        time.sleep(10)
        show_worktime_announcement_id = 'prlWTEP_uwtWorkTimetd2'
        repo.navigate_to_id(show_worktime_announcement_id)
        time.sleep(10)
        send_for_approval_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_lnkTeeIlmoitus'
        repo.navigate_to_id(send_for_approval_id)
        time.sleep(10)
        worktime_announcement_next_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_rlbNext'
        repo.navigate_to_id(worktime_announcement_next_id)
        time.sleep(10)
        worktime_announcement_save_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_rlbSave'
        repo.navigate_to_id(worktime_announcement_save_id)
        time.sleep(10)
        repo.logger.error('Element not found')
        repo.take_screenshot()
        repo.driver.quit()
            
    def daily(self):
        repo = Reportronic()
        repo.login_to_reportronic()
        time.sleep(10)
        browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
        repo.navigate_to_id(browse_worktime_id)
        time.sleep(10)
        add_worktime_id = 'prlWTEP_uwtWorkTimetd1'
        repo.navigate_to_id(add_worktime_id)
        time.sleep(10)
        start_worktime_input_element = repo.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_txtStart')
        start_worktime_input_element.send_keys('08:00')
        end_worktime_input_element = repo.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_txtEnd')
        end_worktime_input_element.send_keys('18:00')
        check_remove_break_time_id = 'prlWTEP_uwtWorkTime__ctl1_chkRemoveBreakTime'
        repo.navigate_to_id(check_remove_break_time_id)
        # Option value 498 equals to
        # 9996  OPETUS JA OHJAUS 408 HETI PVÄ 100 Tutkintokoulutus
        repo.click_option_value_from_dropdown_menu('498')
        time.sleep(10)
        working_hours_amount_id = repo.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask1_txtDuration')
        working_hours_amount_id.send_keys('10:00')
        repo.logger.error('Element not found')
        repo.take_screenshot()
        repo.driver.quit()

if __name__ == '__main__':
    script = ScriptRuns()
    script.daily()
