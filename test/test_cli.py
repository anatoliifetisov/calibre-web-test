#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from selenium import webdriver
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
import shutil
from ui_helper import ui_class
from subproc_wrapper import process_open
from testconfig import CALIBRE_WEB_PATH, TEST_DB, BOOT_TIME
import re
import sys

from parameterized import parameterized_class

@parameterized_class([
   { "py_version": u'/usr/bin/python'},
   { "py_version": u'/usr/bin/python3'},
],names=('Python27','Python36'))
class test_cli(unittest.TestCase, ui_class):

    @classmethod
    def setUpClass(cls):
        print('test_cli')
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()
        shutil.rmtree(TEST_DB,ignore_errors=True)
        shutil.copytree('./Calibre_db', TEST_DB)

    def setUp(self):
        os.chdir(os.path.dirname(__file__))
        try:
            os.remove(os.path.join(CALIBRE_WEB_PATH,'app.db'))
        except:
            pass

    @classmethod
    def tearDownClass(cls):
        # close the browser window
        cls.driver.quit()
        try:
            os.remove(os.path.join(CALIBRE_WEB_PATH, 'app.db'))
        except:
            pass

    def test_cli_different_folder(self):
        os.chdir(CALIBRE_WEB_PATH)
        self.p = process_open([self.py_version, u'cps.py'],(1))
        os.chdir(os.path.dirname(__file__))
        try:
            # create a new Firefox session
            time.sleep(15)
            # navigate to the application home page
            self.driver.get("http://127.0.0.1:8083")

            # Wait for config screen to show up
            self.fill_initial_config({'config_calibre_dir':TEST_DB})

            # wait for cw to reboot
            time.sleep(BOOT_TIME)

            # Wait for config screen with login button to show up
            login_button = self.check_element_on_page((By.NAME, "login"))
            self.assertTrue(login_button)
            login_button.click()

            # login
            self.login("admin", "admin123")
            time.sleep(3)
            self.assertTrue(self.check_element_on_page((By.NAME, "query")))
        except:
            pass
        self.p.kill()


    def test_cli_different_settings_database(self):
        new_db = os.path.join(CALIBRE_WEB_PATH, 'hü go.app')  # .decode('UTF-8')
        # if sys.version_info < (3, 0):
        new_db = new_db.decode('UTF-8')
        self.p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-p', new_db], (1,3))

        time.sleep(15)
        # navigate to the application home page
        self.driver.get("http://127.0.0.1:8083")

        # Wait for config screen to show up
        self.fill_initial_config({'config_calibre_dir':TEST_DB})

        # wait for cw to reboot
        time.sleep(BOOT_TIME)

        # Wait for config screen with login button to show up
        login_button = self.check_element_on_page((By.NAME, "login"))
        self.assertTrue(login_button)
        self.p.kill()
        self.assertTrue(os.path.isfile(new_db), "New settingsfile location not accepted")
        os.remove(new_db)


    def test_cli_SSL_files(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(os.path.join(CALIBRE_WEB_PATH, 'hü lo'), ignore_errors=True)
        path_like_file = CALIBRE_WEB_PATH
        only_path = CALIBRE_WEB_PATH + os.sep
        real_key_file = os.path.join(CALIBRE_WEB_PATH, 'hü lo', 'lö g.key') # .decode('UTF-8')
        real_crt_file = os.path.join(CALIBRE_WEB_PATH, 'hü lo', 'lö g.crt') # .decode('UTF-8')
        if sys.version_info < (3, 0):
            real_key_file = real_key_file.decode('UTF-8')
            real_crt_file = real_crt_file.decode('UTF-8')

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-c', path_like_file],(1,3))
        time.sleep(2)
        nextline = p.communicate()[0]
        if p.poll() is None:
            p.kill()
        self.assertIsNotNone(re.findall('Certfilepath is invalid. Exiting', nextline))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-k', path_like_file],(1,3))
        time.sleep(2)
        nextline = p.communicate()[0]
        if p.poll() is None:
            p.kill()
        self.assertIsNotNone(re.findall('Keyfilepath is invalid. Exiting', nextline))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-c', only_path],(1,3))
        time.sleep(2)
        nextline = p.communicate()[0]
        if p.poll() is None:
            p.kill()
        self.assertIsNotNone(re.findall('Certfilepath is invalid. Exiting', nextline))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-k', only_path],(1,3))
        time.sleep(2)
        nextline = p.communicate()[0]
        if p.poll() is None:
            p.kill()
        self.assertIsNotNone(re.findall('Keyfilepath is invalid. Exiting', nextline))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-c', real_crt_file],(1,3))
        time.sleep(2)
        if p.poll() is None:
            p.kill()
        nextline = p.communicate()[0]
        self.assertIsNotNone(re.findall('Certfilepath is invalid. Exiting', nextline))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-k', real_key_file],(1,3))
        time.sleep(2)
        if p.poll() is None:
            p.kill()
        nextline = p.communicate()[0]
        self.assertIsNotNone(re.findall('Keyfilepath is invalid. Exiting', nextline))

        os.makedirs(os.path.join(CALIBRE_WEB_PATH, 'hü lo'))
        with open(real_key_file, 'wb') as fout:
            fout.write(os.urandom(124))
        with open(real_crt_file, 'wb') as fout:
            fout.write(os.urandom(124))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-c', real_crt_file],(1,3))
        time.sleep(2)
        if p.poll() is None:
            p.kill()
        nextline = p.communicate()[0]
        self.assertIsNotNone(re.findall('Certfile and Keyfile have to be used together. Exiting', nextline))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-k', real_key_file],(1,3))
        time.sleep(2)
        if p.poll() is None:
            p.kill()
        nextline = p.communicate()[0]
        self.assertIsNotNone(re.findall('Certfile and Keyfile have to be used together. Exiting', nextline))

        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-c', real_crt_file, '-k', real_key_file],(1,3,5))
        if p.poll() is not None:
            self.assertIsNone('Fail','Unexpected error')
        time.sleep(10)

        # navigate to the application home page
        try:
            self.driver.get("https://127.0.0.1:8083")
            self.assertIsNone("Error", "HTTPS Connection could established with wrong key/cert file")
        except WebDriverException as e:
            self.assertIsNotNone(re.findall('Reached error page: about:neterror?nssFailure', e.msg))
        p.kill()
        shutil.rmtree(os.path.join(CALIBRE_WEB_PATH, 'hü lo'), ignore_errors=True)
        shutil.copytree('./SSL', os.path.join(CALIBRE_WEB_PATH, 'hü lo'))
        real_crt_file = os.path.join(CALIBRE_WEB_PATH, 'hü lo', 'ssl.crt') # .decode('UTF-8')
        real_key_file = os.path.join(CALIBRE_WEB_PATH, 'hü lo', 'ssl.key') # .decode('UTF-8')
        if sys.version_info < (3, 0):
            real_crt_file = real_crt_file.decode('UTF-8')
            real_key_file = real_key_file.decode('UTF-8')
        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py'),
                        '-c', real_crt_file, '-k', real_key_file],(1,3,5))
        if p.poll() is not None:
            self.assertIsNone('Fail','Unexpected error')
        time.sleep(10)

        # navigate to the application home page
        try:
            self.driver.get("https://127.0.0.1:8083")
        except WebDriverException:
            self.assertIsNone("Error", "HTTPS Connection could not established with key/cert file")

        shutil.rmtree(os.path.join(CALIBRE_WEB_PATH, 'hü lo'), ignore_errors=True)
        self.assertTrue(self.check_element_on_page((By.ID, "config_calibre_dir")))
        p.kill()

    # @unittest.expectedFailure
    @unittest.skip("Not Implemented")
    def test_cli_gdrive_location(self):
        # ToDo: implement
        self.assertIsNone('not Implemented', 'Check if moving gdrive db on commandline works')

    def test_environ_port_setting(self):
        p = process_open([self.py_version, os.path.join(CALIBRE_WEB_PATH,u'cps.py')],(1), env={'CALIBRE_PORT':'8082'})

        time.sleep(15)
        # navigate to the application home page
        try:
            self.driver.get("http://127.0.0.1:8082")
        except WebDriverException as e:
            self.assertIsNotNone(re.findall('Reached error page: about:neterror?e=connectionFailure', e.msg))
        self.assertTrue(self.check_element_on_page((By.ID, "config_calibre_dir")))
        p.kill()

    # @unittest.expectedFailure
    # @unittest.skip("Not Implemented")
    # start calibre-web in process A.
    # Start calibre-web in process B.
    # Check process B terminates with exit code 1
    # stop process A
    def test_already_started(self):
        os.chdir(CALIBRE_WEB_PATH)
        p1 = process_open([self.py_version, u'cps.py'], (1))
        time.sleep(BOOT_TIME)
        p2 = process_open([self.py_version, u'cps.py'], (1))
        time.sleep(BOOT_TIME)
        result = p2.poll()
        if result is None:
            p2.kill()
            self.assert_('2nd process not terminated, port is already in use')
        self.assertEqual(result, 1)
        p1.kill()


