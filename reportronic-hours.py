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

import calendar
import json
import logging
import os
import smtplib
import time
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui

class Reportronic:
    def __init__(self):
        self.driver = webdriver.Firefox()
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
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.formatter)
        stream_handler.setLevel(logging.INFO)
        self.log_filename = 'logs/reportronic-hours.log'
        os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
        file_handler = logging.FileHandler(self.log_filename)
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
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
            self.logger.info('Working hours for today have already been saved')
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

    def click_option_value_from_dropdown_menu(self, select_id, option_value):
        """Finds element with given value from dropdown menu and clicks it to
        choose it.
        """
        if option_value == 599:
            self.logger.info(
                'Trying to find option 4058  Osaamisen pelimerkit from dropdown')
        elif option_value == 498:
            self.logger.info(
                'Trying to find option 9996  OPETUS JA OHJAUS 408 HETI PVÄ 100 Tutkintokoulutus from dropdown')
        else:
            self.logger.info(
                'Trying to find select with id of {}'.format(select_id))
        xpath = "//select[@id='{}']/option[@value='{}']".format(select_id,
                                                               option_value)
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
        screenshot_filename = 'pics/reportronic-hours.png'
        os.makedirs(os.path.dirname(screenshot_filename), exist_ok=True)
        self.driver.save_screenshot(screenshot_filename)
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
        """Writes log output to email's message body."""
        msg = MIMEMultipart()
        msg['Subject'] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S Reportronic Hours Output")
        msg['From'] = self.mail_user
        msg['To'] = self.mail_to
        with open(Reportronic().log_filename) as log:
            body = log.readlines()
        msg_body = ''.join(body)
        msg.attach(MIMEText(msg_body))
        with open('pics/reportronic-hours.png', 'rb') as fp:
            img = MIMEImage(fp.read())
        msg.attach(img)
        return msg

    def send(self):
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
        try:
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

            repo.navigate_to_id(browse_worktime_id)
            repo.navigate_to_id(show_worktime_announcement_id)
            announcement_filter_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_cboFilter'
            repo.click_option_value_from_dropdown_menu(announcement_filter_id, '0')
            search_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_rlbSearch'
            repo.navigate_to_id(search_id)

            datagrid_id = 'prlWorkTimeAnnouncementPage_uwtWorkTime__ctl2_DataGrid'
            if repo.is_element_visible(datagrid_id):
                repo.take_screenshot()
        finally:
            repo.driver.quit()
            
    def daily(self, start='08:00', end='18:07'):
        """Does daily working hour saving. Saves 08-18 hours by default."""
        try:
            repo = Reportronic()
            repo.login_to_reportronic()
            browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
            repo.navigate_to_id(browse_worktime_id)
            
            if repo.are_todays_hours_saved():
                repo.take_screenshot()
                return

            add_worktime_id = 'prlWTEP_uwtWorkTimetd1'
            repo.navigate_to_id(add_worktime_id)
            start_worktime_input_element_id = 'prlWTEP_uwtWorkTime__ctl1_txtStart'

            if repo.is_element_visible(start_worktime_input_element_id):
                start_worktime_input_element = repo.driver.find_element_by_id(
                    start_worktime_input_element_id)
                start_worktime_input_element.send_keys(start)
                end_worktime_input_element = repo.driver.find_element_by_id(
                    'prlWTEP_uwtWorkTime__ctl1_txtEnd')
                end_worktime_input_element.send_keys(end)
                check_remove_break_time_id = 'prlWTEP_uwtWorkTime__ctl1_chkRemoveBreakTime'
                repo.driver.find_element_by_id(check_remove_break_time_id).click()

                # Option value 498 equals to
                # 9996  OPETUS JA OHJAUS 408 HETI PVÄ 100 Tutkintokoulutus
                worktime_task_id = 'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask1_cboProject'
                repo.click_option_value_from_dropdown_menu(worktime_task_id, '498')
                # Had to use sleep here since JS sucks.
                time.sleep(10)

                working_hours_amount_id = 'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask1_txtDuration'
                working_hours_amount = repo.driver.find_element_by_id(
                    working_hours_amount_id)
                working_hours_amount.send_keys('10:07')
                repo.save_working_hours()

                browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
                repo.navigate_to_id(browse_worktime_id)

                worktimes_id = 'prlWTEPuwtWorkTimectl0ctlWorkTimeViewSelector1UWTS1_1'
                if repo.is_element_visible(worktimes_id):
                    if repo.are_todays_hours_saved():
                        repo.take_screenshot()
        finally:
            repo.driver.quit()

    def friday(self, start='08:00', end='18:07'):
        """Option values for Friday are 498 and 599"""
        try:
            repo = Reportronic()
            repo.login_to_reportronic()
            browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
            repo.navigate_to_id(browse_worktime_id)

            if repo.are_todays_hours_saved():
                repo.take_screenshot()
                return

            add_worktime_id = 'prlWTEP_uwtWorkTimetd1'
            repo.navigate_to_id(add_worktime_id)
            start_worktime_input_element_id = 'prlWTEP_uwtWorkTime__ctl1_txtStart'

            if repo.is_element_visible(start_worktime_input_element_id):
                start_worktime_input_element = repo.driver.find_element_by_id(
                    start_worktime_input_element_id)
                start_worktime_input_element.send_keys(start)
                end_worktime_input_element = repo.driver.find_element_by_id(
                    'prlWTEP_uwtWorkTime__ctl1_txtEnd')
                end_worktime_input_element.send_keys(end)
                check_remove_break_time_id = 'prlWTEP_uwtWorkTime__ctl1_chkRemoveBreakTime'
                repo.driver.find_element_by_id(check_remove_break_time_id).click()

                worktime_task_id1 = 'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask1_cboProject'
                # Option value 498 equals to
                # 9996  OPETUS JA OHJAUS 408 HETI PVÄ 100 Tutkintokoulutus
                repo.click_option_value_from_dropdown_menu(worktime_task_id1, '498')
                time.sleep(10)
                working_hours_amount_id = 'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask1_txtDuration'
                working_hours_amount = repo.driver.find_element_by_id(
                    working_hours_amount_id)
                working_hours_amount.send_keys('05:00')

                worktime_task_id2 = 'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask2_cboProject'
                # Option value 599 equals to
                # 4058 Osaamisen pelimerkit
                repo.click_option_value_from_dropdown_menu(worktime_task_id2, '599')
                time.sleep(10)
                working_hours_amount_id = 'prlWTEP_uwtWorkTime__ctl1_ctlWorkTimeTask2_txtDuration'
                working_hours_amount = repo.driver.find_element_by_id(
                    working_hours_amount_id)
                working_hours_amount.send_keys('05:07')
                repo.save_working_hours()

                browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
                repo.navigate_to_id(browse_worktime_id)

                worktimes_id = 'prlWTEPuwtWorkTimectl0ctlWorkTimeViewSelector1UWTS1_1'
                if repo.is_element_visible(worktimes_id):
                    if repo.are_todays_hours_saved():
                        repo.take_screenshot()
        finally:
            repo.driver.quit()

    def delete_duplicate(self):
        try:
            repo = Reportronic()
            repo.login_to_reportronic()
            browse_worktime_id = 'CtlMenu1_CtlNavBarMain1_ctlNavBarWorkT1_lnkSelaaTyoaika'
            repo.navigate_to_id(browse_worktime_id)
            delete_button_id = 'prlWTEP_uwtWorkTime__ctl0_dgWorkTime_RLinkbutton2_0'
            if repo.is_element_visible(delete_button_id):
                repo.driver.find_element_by_id(
                    'prlWTEP_uwtWorkTime__ctl0_dgWorkTime_RLinkbutton2_0').click()
                time.sleep(2)
                alert = Alert(repo.driver)
                time.sleep(2)
                alert.accept()
                time.sleep(10)
                worktimes_id = 'prlWTEPuwtWorkTimectl0ctlWorkTimeViewSelector1UWTS1_1'
                if repo.is_element_visible(worktimes_id):
                    repo.take_screenshot()
        finally:
            repo.driver.quit()   

if __name__ == '__main__':
    import argparse
    import sys

    run = ScriptRuns()
    mail = Mail()

    parser = argparse.ArgumentParser()
    parser.add_argument('--daily',
                        help='Run daily run of saving working hours.',
                        action='store_true')
    parser.add_argument('--monthly',
                        help='Run monthly run of saving working hours.',
                        action='store_true')
    parser.add_argument('--delete-duplicate',
                        help='Delete possible duplicate working hours.',
                        action='store_true')
    parser.add_argument('--friday',
                        help='Run specific run for saving Friday\'s working hours.',
                        action='store_true')
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.daily and len(sys.argv) == 2:
        run.daily()
        mail.send()
        sys.exit(0)
    elif args.monthly and len(sys.argv) == 2:
        run.monthly()
        mail.send()
        sys.exit(0)
    elif args.delete_duplicate and len(sys.argv) == 2:
        run.delete_duplicate()
        mail.send()
        sys.exit(0)
    elif args.friday and len(sys.argv) == 2:
        run.friday()
        mail.send()
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)
