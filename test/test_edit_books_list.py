#!/usr/bin/env python
# -*- coding: utf-8 -*-


from unittest import TestCase
import time

from helper_ui import ui_class
from config_test import TEST_DB
from helper_func import startup, debug_startup
from helper_func import save_logfiles
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class TestEditBooksList(TestCase, ui_class):
    p = None
    driver = None

    @classmethod
    def setUpClass(cls):
        try:
            startup(cls, cls.py_version, {'config_calibre_dir': TEST_DB})
            time.sleep(3)
        except Exception:
            cls.driver.quit()
            cls.p.kill()

    @classmethod
    def tearDownClass(cls):
        cls.driver.get("http://127.0.0.1:8083")
        cls.stop_calibre_web()
        # close the browser window and stop calibre-web
        cls.driver.quit()
        cls.p.terminate()
        save_logfiles(cls, cls.__name__)

    def check_search(self, bl, term, count, column, value):
        bl['search'].clear()
        bl['search'].send_keys(term)
        bl['search'].send_keys(Keys.RETURN)
        time.sleep(1)
        bl = self.get_books_list(-1)
        self.assertEqual(count, len(bl['table']))
        self.assertEqual(value, bl['table'][0][column]['text'])
        return bl

    def test_search_books_list(self):
        bl = self.get_books_list(1)
        self.assertEqual(10, len(bl['table']))
        self.assertEqual(4, len(bl['pagination']))
        bl = self.check_search(bl, "genot", 4, "Categories", "Gênot")
        bl = self.check_search(bl, "buch", 1, "Title", "Der Buchtitel")
        bl = self.check_search(bl, "HaLaG", 2, "Author Sort", "Halagal, Norbert")
        bl = self.check_search(bl, "", 10, "Languages", "Norwegian Bokmål")
        bl = self.check_search(bl, " Loko ", 1, "Series", "Loko")
        self.check_search(bl, "Random", 1, "Publishers", "Randomhäus")
        self.get_book_details(5)
        # tick archive book in book details
        self.check_element_on_page((By.XPATH, "//*[@id='archived_cb']")).click()
        self.get_book_details(10)
        self.check_element_on_page((By.XPATH, "//*[@id='archived_cb']")).click()
        bl = self.get_books_list(1)
        self.assertEqual(9, len(bl['table']))
        # remove books from archive
        self.get_book_details(5)
        self.check_element_on_page((By.XPATH, "//*[@id='archived_cb']")).click()
        self.get_book_details(10)
        self.check_element_on_page((By.XPATH, "//*[@id='archived_cb']")).click()

    def test_bookslist_edit_title(self):
        bl = self.get_books_list(1)
        self.edit_table_element(bl['table'][3]['Title']['element'], "Die Buc\"t'itel")
        bl = self.get_books_list(-1)
        self.assertEqual("Die Buc\"t'itel", bl['table'][3]['Title']['text'])
        self.assertEqual("Buc\"t'itel, Die", bl['table'][3]['Title Sort']['text'])
        self.edit_table_element(bl['table'][3]['Title']['element'], "Die Buctitel")
        bl = self.get_books_list(-1)
        self.assertEqual("Die Buctitel", bl['table'][3]['Title']['text'])
        self.assertEqual("Buctitel, Die", bl['table'][3]['Title Sort']['text'])
        self.assertTrue(bl['title_sort'].is_selected())
        bl['title_sort'].click()
        self.edit_table_element(bl['table'][3]['Title']['element'], "Das Buctitel")
        bl = self.get_books_list()
        self.assertEqual("Das Buctitel", bl['table'][3]['Title']['text'])
        self.assertEqual("Buctitel, Die", bl['table'][3]['Title Sort']['text'])
        self.goto_page('nav_new')
        bl = self.get_books_list()
        self.assertTrue(bl['title_sort'].is_selected()) # is not stored
        self.edit_table_element(bl['table'][3]['Title Sort']['element'], "Buchtitel, Der")
        bl = self.get_books_list()
        self.assertEqual("Das Buctitel", bl['table'][3]['Title']['text'])
        self.assertEqual("Buchtitel, Der", bl['table'][3]['Title Sort']['text'])
        # Restore default
        self.edit_table_element(bl['table'][3]['Title']['element'], "testbook")

    def test_bookslist_edit_author(self):
        bl = self.get_books_list(1)
        self.edit_table_element(bl['table'][3]['Authors']['element'], "Jane Dä")
        bl = self.get_books_list(-1)
        self.assertEqual("Jane Dä", bl['table'][3]['Authors']['text'])
        self.assertEqual("Dä, Jane", bl['table'][3]['Author Sort']['text'])
        self.assertTrue(bl['author_sort'].is_selected())
        bl['author_sort'].click()
        self.edit_table_element(bl['table'][3]['Authors']['element'], "Jane dÜ")
        bl = self.get_books_list()
        self.assertEqual("Jane dÜ", bl['table'][3]['Authors']['text'])
        self.assertEqual("Dä, Jane", bl['table'][3]['Author Sort']['text'])
        self.goto_page('nav_new')
        bl = self.get_books_list()
        self.assertTrue(bl['author_sort'].is_selected())
        self.edit_table_element(bl['table'][3]['Author Sort']['element'], "De, Janette")
        bl = self.get_books_list()
        self.assertEqual("De, Janette", bl['table'][3]['Author Sort']['text'])
        self.edit_table_element(bl['table'][3]['Authors']['element'], "John  D, James Költ")
        bl = self.get_books_list(-1)
        self.assertEqual("John D, James Költ", bl['table'][3]['Authors']['text'])
        self.assertEqual("John D, James Költ", bl['table'][3]['Author Sort']['text'])
        self.edit_table_element(bl['table'][3]['Authors']['element'], " John  D& James Költ ")
        bl = self.get_books_list(-1)
        self.assertEqual("D, John & Költ, James", bl['table'][3]['Author Sort']['text'])
        self.edit_table_element(bl['table'][3]['Authors']['element'], "James Költ & John Döe")
        bl = self.get_books_list(-1)
        self.assertEqual("James Költ & John Döe", bl['table'][3]['Authors']['text'])
        self.assertEqual("Költ, James & Döe, John", bl['table'][3]['Author Sort']['text'])
        self.edit_table_element(bl['table'][3]['Authors']['element'], "../admin")
        bl = self.get_books_list(-1)
        self.assertEqual("../admin", bl['table'][3]['Authors']['text'])
        self.assertEqual("../admin", bl['table'][3]['Author Sort']['text'])
        self.edit_table_element(bl['table'][3]['Authors']['element'], "admin | Name, Kurt")
        bl = self.get_books_list(-1)
        self.assertEqual("admin , Name, Kurt", bl['table'][3]['Authors']['text'])
        self.assertEqual("admin , Name, Kurt", bl['table'][3]['Author Sort']['text'])
        # Restore default
        self.edit_table_element(bl['table'][3]['Authors']['element'], "John Döe")

    def test_bookslist_edit_categories(self):
        bl = self.get_books_list(2)
        self.assertEqual("+", bl['table'][0]['Categories']['text'])
        self.edit_table_element(bl['table'][0]['Categories']['element'], "执 Huki")
        bl = self.get_books_list(-1)
        bl['table'][0]['Categories']['sort'].click()
        bl = self.get_books_list(-1)        # we are now back on page 1 again
        self.assertEqual("+", bl['table'][0]['Categories']['text'])
        bl['table'][0]['Categories']['sort'].click()
        bl = self.get_books_list(-1)
        self.assertEqual("执 Huki", bl['table'][0]['Categories']['text'])
        bl = self.get_books_list(2)
        self.edit_table_element(bl['table'][0]['Categories']['element'], "+")
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][0]['Categories']['text'])
        self.edit_table_element(bl['table'][0]['Categories']['element'], " Gênot,Test ")
        bl = self.get_books_list(-1)
        self.assertEqual("Gênot, Test", bl['table'][0]['Categories']['text'])
        elements = self.goto_page("nav_cat")
        self.assertEqual(2, len(elements))
        self.assertEqual("Test", elements[1].text)
        bl = self.get_books_list(2)
        self.edit_table_element(bl['table'][0]['Categories']['element'], "Gênot| Test")
        bl = self.get_books_list(-1)
        self.assertEqual("Gênot| Test", bl['table'][0]['Categories']['text'])
        elements = self.goto_page("nav_cat")
        self.assertEqual(2, len(elements))
        self.assertEqual("Gênot| Test", elements[1].text)
        # Restore default
        bl = self.get_books_list(2)
        self.edit_table_element(bl['table'][0]['Categories']['element'], "")
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][0]['Categories']['text'])

    def test_bookslist_edit_series(self):
        bl = self.get_books_list(1)
        self.assertEqual("+", bl['table'][3]['Series']['text'])
        self.edit_table_element(bl['table'][3]['Series']['element'], "执 Hukes")
        bl = self.get_books_list(-1)
        self.assertEqual("执 Hukes", bl['table'][3]['Series']['text'])
        self.edit_table_element(bl['table'][3]['Series']['element'], "+")
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][3]['Series']['text'])
        self.edit_table_element(bl['table'][3]['Series']['element'], " Djüngel,Te|s@t ")
        bl = self.get_books_list(-1)
        self.assertEqual("Djüngel,Te|s@t", bl['table'][3]['Series']['text'])
        self.goto_page("nav_serie")
        elements = self.get_series_books_displayed()
        self.assertEqual(3, len(elements))
        self.assertEqual("Djüngel,Te|s@t", elements[1]['title'])
        bl = self.get_books_list(1)
        # Restore default
        self.edit_table_element(bl['table'][3]['Series']['element'], "")
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][3]['Series']['text'])

    def test_bookslist_edit_publisher(self):
        bl = self.get_books_list(1)
        self.assertEqual("+", bl['table'][4]['Publishers']['text'])
        self.edit_table_element(bl['table'][4]['Publishers']['element'], "执 Huks")
        bl = self.get_books_list(-1)
        self.assertEqual("执 Huks", bl['table'][4]['Publishers']['text'])
        self.edit_table_element(bl['table'][4]['Publishers']['element'], "+")
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][4]['Publishers']['text'])
        self.edit_table_element(bl['table'][4]['Publishers']['element'], " Pandöm,Ti|s@d ")
        bl = self.get_books_list(-1)
        self.assertEqual("Pandöm,Ti|s@d", bl['table'][4]['Publishers']['text'])
        elements = self.goto_page("nav_publisher")
        self.assertEqual(2, len(elements))
        self.assertEqual("Pandöm,Ti|s@d", elements[0].text)
        bl = self.get_books_list(1)
        # Restore default
        self.edit_table_element(bl['table'][4]['Publishers']['element'], "")
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][4]['Publishers']['text'])

    def test_bookslist_edit_languages(self):
        bl = self.get_books_list(1)
        bl['table'][0]['Languages']['sort'].click()
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][3]['Languages']['text'])
        self.edit_table_element(bl['table'][3]['Languages']['element'], "German")
        bl = self.get_books_list(-1)
        self.assertEqual("German", bl['table'][3]['Languages']['text'])
        self.edit_table_element(bl['table'][3]['Languages']['element'], "+")
        self.assertTrue("+" in self.check_element_on_page((By.XPATH,
                                                          "//div[contains(@class,'editable-error-block')]")).text)
        self.check_element_on_page((By.XPATH,"//button[contains(@class,'editable-cancel')]")).click()
        bl = self.get_books_list(-1)
        self.assertEqual("German", bl['table'][3]['Languages']['text'])
        self.edit_table_element(bl['table'][3]['Languages']['element'], " English,  German   , fReNcH  ")
        bl = self.get_books_list(-1)
        self.assertEqual("German, English, French", bl['table'][3]['Languages']['text'])
        elements = self.goto_page("nav_lang")
        self.assertEqual(4, len(elements))
        self.assertEqual("French", elements[3].text)
        self.assertEqual("German", elements[2].text)
        bl = self.get_books_list(1)
        self.edit_table_element(bl['table'][2]['Languages']['element'], "German, ")
        bl = self.get_books_list(1)
        self.assertEqual("German", bl['table'][2]['Languages']['text'])
        # Restore default
        self.edit_table_element(bl['table'][2]['Languages']['element'], "")
        bl = self.get_books_list(-1)
        self.assertEqual("+", bl['table'][2]['Languages']['text'])

    def test_bookslist_edit_seriesindex(self):
        bl = self.get_books_list(1)
        self.assertEqual("+", bl['table'][4]['Series Index']['text'])
        self.edit_table_element(bl['table'][5]['Series Index']['element'], "2")
        bl = self.get_books_list(-1)
        self.assertEqual("2", bl['table'][5]['Series Index']['text'])
        self.edit_table_element(bl['table'][5]['Series Index']['element'], "+")
        time.sleep(1)
        self.assertTrue(self.check_element_on_page((By.XPATH,
                                                          "//button[contains(@class,'editable-submit')]")))
        self.check_element_on_page((By.XPATH,"//button[contains(@class,'editable-cancel')]")).click()
        bl = self.get_books_list(-1)
        self.assertEqual("2", bl['table'][5]['Series Index']['text'])
        self.edit_table_element(bl['table'][5]['Series Index']['element'], "-2")
        self.assertTrue(self.check_element_on_page((By.XPATH,
                                                          "//button[contains(@class,'editable-submit')]")))
        self.check_element_on_page((By.XPATH,"//button[contains(@class,'editable-cancel')]")).click()
        bl = self.get_books_list(-1)
        self.assertEqual("2", bl['table'][5]['Series Index']['text'])
        self.edit_table_element(bl['table'][5]['Series Index']['element'], "2.009")
        self.assertTrue(self.check_element_on_page((By.XPATH,
                                                          "//button[contains(@class,'editable-submit')]")))
        self.check_element_on_page((By.XPATH,"//button[contains(@class,'editable-cancel')]")).click()
        bl = self.get_books_list(-1)
        self.assertEqual("2", bl['table'][5]['Series Index']['text'])
        self.edit_table_element(bl['table'][5]['Series Index']['element'], "2,01")
        bl = self.get_books_list(-1)
        self.assertEqual("2.01", bl['table'][5]['Series Index']['text'])
        self.edit_table_element(bl['table'][5]['Series Index']['element'], "1.99")
        bl = self.get_books_list(-1)
        self.assertEqual("1.99", bl['table'][5]['Series Index']['text'])

        # Restore default
        bl = self.get_books_list(-1)
        self.edit_table_element(bl['table'][4]['Series Index']['element'], "1")
        bl = self.get_books_list(-1)
        self.assertEqual("1", bl['table'][4]['Series Index']['text'])

    # change visibility of some columns
    # goto other page, return to books list, check if visibility is same
    def test_list_visibility(self):
        bl = self.get_books_list(1)
        self.assertTrue(bl['column'])
        bl['column'].click()
        self.assertEqual(9, len(bl['column_elements']))
        self.assertEqual(11, len(bl['table'][0]))
        for indx, element in enumerate(bl['column_elements']):
            if element.is_selected():
                self.assertTrue(bl['column_texts'][indx].text in bl['table'][0])
        bl['column_elements'][0].click()
        bl['column_elements'][1].click()
        bl['column_elements'][2].click()
        bl['column_elements'][3].click()
        bl['column_elements'][4].click()
        bl['column_elements'][5].click()
        bl['column_elements'][6].click()
        bl = self.get_books_list(2)
        self.assertTrue(bl['column'])
        bl['column'].click()
        self.assertEqual(9, len(bl['column_elements']))
        self.assertEqual(4, len(bl['table'][0]))
        self.assertFalse(bl['column_elements'][0].is_selected())
        self.assertFalse(bl['column_elements'][1].is_selected())
        self.assertFalse(bl['column_elements'][2].is_selected())
        self.assertFalse(bl['column_elements'][3].is_selected())
        self.assertFalse(bl['column_elements'][4].is_selected())
        self.assertFalse(bl['column_elements'][5].is_selected())
        self.assertFalse(bl['column_elements'][6].is_selected())
        bl['column_elements'][0].click()
        bl['column_elements'][1].click()
        bl['column_elements'][2].click()
        bl['column_elements'][3].click()
        bl['column_elements'][4].click()
        bl['column_elements'][5].click()
        bl['column_elements'][6].click()
        bl = self.get_books_list(1)
        self.assertEqual(11, len(bl['table'][0]))

    def test_restricted_rights(self):
        bl = self.get_books_list(1)
        self.assertTrue('Delete' in bl['table'][0])
        self.edit_user('admin', {'delete_role': 0})
        bl = self.get_books_list(1)
        self.assertFalse('Delete' in bl['table'][0])
        self.edit_user('admin', {'edit_role': 0})
        bl = self.get_books_list(1)
        self.assertEqual(10, len(bl['table']))
        self.assertFalse('Delete' in bl['table'][0])
        for el in bl['table'][0]:
            self.assertTrue('td', bl['table'][0][el]['element'].tag_name)
        self.edit_user('admin', {'delete_role': 1, 'edit_role': 1})