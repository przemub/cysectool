import os
import signal
import time
import unittest
from multiprocessing import Process

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options

from main import run_server


class GUITest(unittest.TestCase):
    url = "http://localhost:5006"

    @classmethod
    def _get(cls, link):
        cls.driver.get(cls.url + link)

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.headless = True

        try:
            cls.driver = webdriver.Firefox(options=options)
        except WebDriverException as wde:
            # Skip when Selenium not available
            raise unittest.SkipTest(str(wde))

        cls.server = Process(target=run_server)
        cls.server.start()
        time.sleep(0.1)  # Wait for the server start
        cls._get("")
        time.sleep(0.1)  # Wait for the page to load

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
        self.driver.find_element_by_xpath('//div[.="Total costs: 4"]')
        self.driver.find_element_by_xpath('//div[.="Total indirect costs: 6"]')
        self.driver.find_element_by_xpath(
            '//div[.="Max flow to the target(s): 0.1"]'
        )

    def test_optimise(self):
        """Try clicking the optimise button"""
        button = self.driver.find_element_by_xpath('//button[.="Optimise"]')
        button.click()

        watchdog = 0
        while not self.driver.find_elements_by_xpath('//button[.="Optimise"]'):
            time.sleep(0.1)

            watchdog += 1
            if watchdog == 100:
                raise TimeoutError("Optimisation timed out")

        self.driver.find_element_by_xpath('//div[.="Total costs: 22"]')
        self.driver.find_element_by_xpath(
            '//div[.="Total indirect costs: 25"]'
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


if __name__ == "__main__":
    unittest.main()
