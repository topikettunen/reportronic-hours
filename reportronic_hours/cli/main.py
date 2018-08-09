import logging
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

from reportronic_hours.reportonic import Reportronic

class ReportonicCLI:
    def __init__(self):
        self.repo = Reportronic()
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)
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
        self.logger.error('Element not found')
    finally:
        self.take_screenshot()
        self.repo.driver.quit()