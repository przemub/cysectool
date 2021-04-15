import os
import signal
import time
import unittest
from multiprocessing import Process

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from main import run_server


class GUITest(unittest.TestCase):
    url = "http://localhost:5006"
    driver: WebDriver = None
    server: Process = None

    headless = True

    @classmethod
    def _get(cls, link):
        cls.driver.get(cls.url + link)

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.headless = cls.headless

        try:
            cls.driver = webdriver.Firefox(options=options)
        except WebDriverException as wde:
            # Skip when Selenium not available
            raise unittest.SkipTest(str(wde))

        cls.server = Process(target=run_server)
        cls.server.start()
        time.sleep(0.5)  # Wait for the server start
        cls._get("")
        time.sleep(0.5)  # Wait for the page to load

    @classmethod
    def tearDownClass(cls):
        os.kill(cls.server.pid, signal.SIGTERM)
        cls.server.join()
        cls.driver.close()

    def test_title(self):
        self.assertEqual(self.driver.title, "Graph Security Optimiser")

    def test_change_control(self):
        """Verifies that a control change updates the graph."""
        option = self.driver.find_element_by_xpath(
            '//option[@value="3) whitelisting"]'
        )
        self.driver.find_element_by_xpath('//div[.="Total costs: 0"]')
        self.driver.find_element_by_xpath('//div[.="Total indirect costs: 0"]')
        self.driver.find_element_by_xpath(
            '//div[.="Max flow to the target(s): 1"]'
        )
        option.click()
        WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element_by_xpath('//div[.="Total costs: 4"]')
        )
        self.driver.find_element_by_xpath('//div[.="Total indirect costs: 6"]')
        self.driver.find_element_by_xpath(
            '//div[.="Max flow to the target(s): 0.1"]'
        )

    def test_optimise(self):
        """Try clicking the optimise button"""
        button = self.driver.find_element_by_xpath('//button[.="Optimise"]')
        button.click()

        WebDriverWait(self.driver, 5).until(
            lambda d: d.find_elements_by_xpath('//button[.="Optimise"]'),
            "Failed to optimise in 5 secs"
        )

        WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element_by_xpath('//div[.="Total indirect costs: 34"]')
        )
        self.driver.find_element_by_xpath('//div[.="Total costs: 26"]')
        self.driver.find_element_by_xpath(
            '//div[.="Max flow to the target(s): 8.3333e-05"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="3) whitelisting" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="3) in-depth packet inspection" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="3) strongly monitored policies" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="2) prompt disabling when users leave" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="2) regularly change password" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="1) access control" and @selected="true"]'
        )

        not_selected = self.driver.find_elements_by_xpath(
            '//option[@value="None" and @selected="true"]'
        )

        self.assertEqual(len(not_selected), 4)

    @unittest.expectedFailure  # it has not yet been figured out how to set sliders' value in Selenium
    def test_half_optimise(self):
        """Try setting both targets to their half-value and clicking the optimise button."""
        button = self.driver.find_element_by_xpath('//button[.="Optimise"]')
        button.click()

        WebDriverWait(self.driver, 5).until(
            lambda d: d.find_elements_by_xpath('//button[.="Optimise"]'),
            "Failed to optimise in 5 secs"
        )

        WebDriverWait(self.driver, 5).until(
            lambda d: d.find_element_by_xpath('//div[.="Total indirect costs: 26"]')
        )
        self.driver.find_element_by_xpath(
            '//div[.="Max flow to the target(s): 0.00012"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="2) patching" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="3) in-depth packet inspection" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="3) strongly monitored policies" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="2) prompt disabling when users leave" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="1) strong password policy" and @selected="true"]'
        )
        self.driver.find_element_by_xpath(
            '//option[@value="1) access control" and @selected="true"]'
        )

        not_selected = self.driver.find_elements_by_xpath(
            '//option[@value="None" and @selected="true"]'
        )

        self.assertEqual(len(not_selected), 4)

    def test_upload_model(self):
        path = os.path.abspath("doc/templates/1_NIST.json")
        upload = self.driver.find_element_by_id("load")

        try:
            upload.send_keys(path)

            # Check that control from the other model is present
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_elements_by_xpath('//label[.="ScW"]')
            )
        finally:
            # Go back to the main page
            self._get("")
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_elements_by_xpath('//label[.="Encryption"]')
            )

    def test_load_template(self):
        templates = self.driver.find_element_by_xpath('//button[.="Load Template"]')
        templates.click()
        load_template = self.driver.find_element_by_xpath('//div[.="NIST"]')

        try:
            load_template.click()

            # Check that control from the other model is present
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_elements_by_xpath('//label[.="ScW"]')
            )
        finally:
            # Go back to the main page
            self._get("")
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_elements_by_xpath('//label[.="Encryption"]')
            )


class GUITestChrome(GUITest):
    @classmethod
    def setUpClass(cls):
        options = ChromeOptions()
        if cls.headless:
            options.add_argument("--headless")

        try:
            cls.driver = webdriver.Chrome(options=options)
        except WebDriverException as wde:
            # Skip when Selenium not available
            raise unittest.SkipTest(str(wde))

        cls.server = Process(target=run_server)
        cls.server.start()
        time.sleep(0.5)  # Wait for the server start
        cls._get("")
        time.sleep(0.5)  # Wait for the page to load


if __name__ == "__main__":
    unittest.main()
