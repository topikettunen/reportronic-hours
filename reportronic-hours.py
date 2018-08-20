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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui

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

    def is_element_visible(self, element_id, timeout=300):
        """Wait for element with given id to be visible. Brings up
        TimeoutException if element is not visible within 5 minutes or
        NoSuchelementException if element with given id doesn't exist.
        """
        self.logger.info(
            'Waiting for element with id of {}'.format(element_id))
        try:
            ui.WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.ID, element_id)))
            return True
        except TimeoutException:
            self.logger.error('Timeout error')
            return False
        except NoSuchElementException:
            self.logger.error('Element not found')
            return False

    def are_todays_hours_saved(self):
        self.logger.info(
            "Check if today's working hours have already been saved.")
        today = datetime.now().strftime('%d.%m.%Y')
        try:
            self.driver.find_element_by_xpath("//*[text()='{}']".format(today))
            self.logger.error('Working hours for today have already been saved')
            return True
        except NoSuchElementException:
            return False
    
    def login_to_reportronic(self):
        """Authenticate user with given username and password from
        config.json.
        """
        self.logger.info('Trying to log in to Reportronic.')        
        self.driver.get(self.url)
        prompt = Alert(self.driver)
        prompt.send_keys(self.user + Keys.TAB + self.password)
        prompt.accept()

    def navigate_to_id(self, element_id):
        """Navigate to element with given id and click on it to proceed to next
        site.
        """
        if self.is_element_visible(element_id):
            self.logger.info(
                'Trying to find element with id of {}'.format(element_id))
            element = self.driver.find_element_by_id(element_id)
            element.click()

    def click_option_value_from_dropdown_menu(self, option_value):
        """Finds element with given value from dropdown menu and clicks it to
        choose it.
        """
        self.logger.info(
            'Trying to find option 9996  OPETUS JA OHJAUS 408 HETI PVÄ 100 Tutkintokoulutus from dropdown')
        xpath = "//option[@value=" + option_value + "]"
        self.driver.find_element_by_xpath(xpath).click()

    def save_working_hours(self):
        """Saves given working hours to Reportronic."""
        self.logger.info('Saving working hours')
        element = self.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_rlbSave')
        element.click()

    def take_screenshot(self):
        """Takes final screenshot of the site after either failure or successful
        addition of working hours.
        """
        self.logger.info('Taking a screenshot.')
        screenshot_filename = datetime.now().strftime("%Y%m%d-%H%M%S-hours.png")
        self.driver.save_screenshot(screenshot_filename)
        self.logger.info('Screenshot saved as {}'.format(screenshot_filename))

    def take_screenshot_of_saved_working_hours(self):
        pass

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
        """Writes log output to email's message body."""
        msg = MIMEText('Hello, World')
        msg['Subject'] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S Reportronic Hours Output")
        msg['From'] = self.mail_user
        msg['To'] = self.mail_to
        return msg

    def send_mail(self):
        """Sends mail from one mail account to another. Fetches these addresses
        from config.json
        """        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.mail_user, self.password)
        msg = self.mail_body()
        server.sendmail(self.mail_user, self.mail_to, msg.as_string())

class ScriptRuns:
    def monthly(self):
        """Does monthly working hour saving, which saves all the working hours
        given from the past month.
        """
        repo = Reportronic()
        repo.login_to_reportronic()
        browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
        repo.navigate_to_id(browse_worktime_id)
        show_worktime_announcement_id = 'prlWTEP_uwtWorkTimetd2'
        repo.navigate_to_id(show_worktime_announcement_id)
        send_for_approval_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_lnkTeeIlmoitus'
        repo.navigate_to_id(send_for_approval_id)
        worktime_announcement_next_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_rlbNext'
        repo.navigate_to_id(worktime_announcement_next_id)
        worktime_announcement_save_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_rlbSave'
        repo.navigate_to_id(worktime_announcement_save_id)
        repo.take_screenshot()
        repo.driver.quit()
            
    def daily(self, start='08:00', end='18:00'):
        """Does daily working hour saving. Saves 08-18 hours by default."""
        repo = Reportronic()
        repo.login_to_reportronic()
        browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
        repo.navigate_to_id(browse_worktime_id)
        add_worktime_id = 'prlWTEP_uwtWorkTimetd1'
        repo.navigate_to_id(add_worktime_id)
        start_worktime_input_element = repo.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_txtStart')
        start_worktime_input_element.send_keys(start)
        end_worktime_input_element = repo.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_txtEnd')
        end_worktime_input_element.send_keys(end)
        check_remove_break_time_id = 'prlWTEP_uwtWorkTime__ctl1_chkRemoveBreakTime'
        repo.navigate_to_id(check_remove_break_time_id)
        # If its friday use option value 599 else 498.
        if datetime.now().isoweekday() == 5:
            # Option value 599 equalst to
            # 4058  Osaamisen pelimerkit
            repo.click_option_value_from_dropdown_menu('599')
        else:
            # Option value 498 equals to
            # 9996  OPETUS JA OHJAUS 408 HETI PVÄ 100 Tutkintokoulutus
            repo.click_option_value_from_dropdown_menu('498')
        working_hours_amount_id = repo.driver.find_element_by_id(
            'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask1_txtDuration')
        working_hours_amount_id.send_keys('10:00')
        repo.take_screenshot()
        repo.driver.quit()
