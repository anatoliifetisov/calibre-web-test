#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from testconfig import PY_BIN
import time
import lxml.etree
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# Dict for pages and the way to reach them
page = dict()
page['nav_serie']={'check':(By.TAG_NAME, "h1"),'click':[(By.ID, "nav_serie")]}
page['nav_publisher']={'check':(By.TAG_NAME, "h1"),'click':[(By.ID, "nav_publisher")]}
page['nav_new']={'check':None,'click':[(By.ID, "nav_new")]}
page['nav_cat']={'check':(By.TAG_NAME, "h1"),'click':[(By.ID, "nav_cat")]}
page['nav_author']={'check':(By.TAG_NAME, "h1"),'click':[(By.ID, "nav_author")]}
page['nav_lang']={'check':(By.TAG_NAME, "h1"),'click':[(By.ID, "nav_lang")]}
page['nav_hot']={'check':None,'click':[(By.ID, "nav_hot")]}
page['nav_about']={'check':(By.ID, "stats"),'click':[(By.ID, "nav_about")]}
page['nav_rated']={'check':None,'click':[(By.ID, "nav_rated")]}
page['nav_read']={'check':None,'click':[(By.ID, "nav_read")]}
page['nav_unread']={'check':None,'click':[(By.ID, "nav_unread")]}
page['nav_sort_old']={'check':None,'click':[(By.ID, "nav_sort"),(By.ID, "nav_sort_old")]}
page['nav_sort_new']={'check':None,'click':[(By.ID, "nav_sort"),(By.ID, "nav_sort_new")]}
page['nav_sort_asc']={'check':None,'click':[(By.ID, "nav_sort"),(By.ID, "nav_sort_asc")]}
page['nav_sort_desc']={'check':None,'click':[(By.ID, "nav_sort"),(By.ID, "nav_sort_desc")]}
page['basic_config']={'check':(By.ID, "config_calibre_dir"),'click':[(By.ID, "top_admin"),(By.ID, "basic_config")]}
page['view_config']={'check':None,'click':[(By.ID, "top_admin"),(By.ID, "view_config")]}
page['mail_server']={'check':(By.ID, "mail_server"),'click':[(By.ID, "top_admin"),(By.ID, "admin_edit_email")]}
page['admin_setup']={'check':(By.ID, "admin_edit_email"),'click':[(By.ID, "top_admin")]}
page['user_setup']={'check':(By.ID, "kindle_mail"),'click':[(By.ID, "top_user")]}
page['create_shelf']={'check':(By.ID, "title"),'click':[(By.ID, "nav_createshelf")]}
page['create_user']={'check':(By.ID, "nickname"),'click':[(By.ID, "top_admin"),(By.ID, "admin_new_user")]}
page['register']={'check':(By.ID, "nickname"),'click':[(By.ID, "register")]}
page['tasks']={'check':(By.TAG_NAME, "h2"),'click':[(By.ID, "top_tasks")]}
page['register']={'check':(By.ID, "nickname"),'click':[(By.ID, "register")]}
page['login']={'check':(By.NAME, "username"),'click':[(By.ID, "logout")]}
page['unlogged_login']={'check':(By.NAME, "username"),'click':[(By.CLASS_NAME, "glyphicon-log-in")]}
page['logviewer']={'check':(By.ID, "log_group"),'click':[(By.ID, "top_admin"),(By.ID, "logfile")]}


class ui_class():
    py_version = PY_BIN

    @classmethod
    def login(cls,user, passwd):
        WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))
        username = cls.driver.find_element_by_name("username")
        password = cls.driver.find_element_by_name("password")
        submit = cls.driver.find_element_by_name("submit")
        username.send_keys(user)
        password.send_keys(passwd)
        submit.click()
        try:
            WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located((By.NAME, "query")))
            return True
        except:
            return False

    '''
    return values: 
    - alert-info, alert-danger, alert-success, alert-warning if flash message occours
    - '-1' if resend button is not presend
    - '0' if no flash message occurs after submit button is pushed    
    '''
    @classmethod
    def forgot_password(cls,user):
        cls.logout()
        cls.check_element_on_page((By.NAME, "username"))
        username = cls.driver.find_element_by_name("username")
        resend = cls.driver.find_element_by_name("forgot")
        if resend:
            username.send_keys(user)
            resend.click()
            flash = cls.check_element_on_page((By.CLASS_NAME, "alert"))
            if flash:
                id = flash.get_attribute('id')
                return id
            else:
                return 0
        return -1

    @classmethod
    def logout(cls):
        logout = cls.check_element_on_page((By.ID, "logout"))
        if logout:
            logout.click()
            return cls.check_element_on_page((By.ID, "username"))
        return False

    @classmethod
    def check_user_logged_in(cls,user, noCompare=False):
        user_element = cls.check_element_on_page((By.ID, "top_user"))
        if user_element:
            if noCompare:
                return True
            if user_element.text.lower() == user.lower():
                return True
        return False

    @classmethod
    def register(cls,user, email):
        cls.goto_page('register')
        username = cls.driver.find_element_by_name("nickname")
        emailfield = cls.driver.find_element_by_name("email")
        submit = cls.driver.find_element_by_id("submit")
        username.send_keys(user)
        emailfield.send_keys(email)
        submit.click()
        flash = cls.check_element_on_page((By.CLASS_NAME, "alert"))
        if flash:
            id = flash.get_attribute('id')
            # text = flash.get_attribute('text')
            return id
        else:
            return False

    @classmethod
    def forgot_password(cls, user):
        cls.goto_page('login')
        username = cls.driver.find_element_by_name("username")
        submit = cls.driver.find_element_by_name("forgot")
        username.send_keys(user)
        submit.click()
        return bool(cls.check_element_on_page((By.ID, "flash_info")))


    @classmethod
    def list_shelfs(cls, search_name=None):
        public_shelfs = cls.driver.find_elements_by_xpath( "//a/span[@class='glyphicon glyphicon-list public_shelf']//ancestor::a")
        private_shelfs = cls.driver.find_elements_by_xpath("//a/span[@class='glyphicon glyphicon-list private_shelf']//ancestor::a")
        ret_shelfs = list()
        ret_ele = None
        for shelf in private_shelfs:
            sh = dict()
            sh['id'] = shelf.get_attribute('href')[shelf.get_attribute('href').rfind('/')+1:]
            sh['name'] = shelf.text
            sh['ele'] = shelf
            sh['public'] = False
            if search_name == shelf.text:
                ret_ele = sh
            else:
                ret_shelfs.append(sh)
        for shelf in public_shelfs:
            no = next((index for (index, d) in enumerate(ret_shelfs) if d["name"] == shelf.text), None)
            if no:
                ret_shelfs[no]['public'] = True
                ret_shelfs[no]['ele'] = shelf
            else:
                sh = dict()
                sh['id'] = shelf.get_attribute('href')[shelf.get_attribute('href').rfind('/')+1:]
                sh['name'] = shelf.text
                sh['public'] = True
                sh['ele'] = shelf
                if search_name == shelf.text:
                    if ret_ele:
                        ret_ele = [sh, ret_ele]
                    else:
                        ret_ele = sh
                else:
                    ret_shelfs.append(sh)
        if search_name:
            return ret_ele
        else:
            return ret_shelfs

    @classmethod
    def page_has_loaded(cls):
        # self.log.info("Checking if {} page is loaded.".format(self.driver.current_url))
        page_state = cls.driver.execute_script('return document.readyState;')
        return page_state == 'complete'

    @classmethod
    def goto_page(cls, page_target):
        if page_target in page:
            try:
                for element in page[page_target]['click']:
                    WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located(element))
                    # goto Page
                    if element[0] == By.ID:
                        cls.driver.find_element_by_id(element[1]).click()
                    if element[0] == By.NAME:
                        cls.driver.find_element_by_name(element[1]).click()
                    if element[0] == By.CLASS_NAME:
                        cls.driver.find_element_by_class_name(element[1]).click()

                # check if got to page
                if page[page_target]['check'][0] == By.TAG_NAME:
                    WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located(page[page_target]['check']))
                    if page[page_target]['check'][1] == 'h1':
                        list_type=cls.driver.find_element_by_tag_name(page[page_target]['check'][1])
                    else:
                        return True
                if page[page_target]['check'][0] == By.ID:
                    WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located(page[page_target]['check']))
                    return True
                if page[page_target]['check'][0] == None:
                    return True

                if list_type:
                    return cls.driver.find_elements_by_xpath("//*[contains(@id, 'list_')]")
                else:
                    return False
            except:
                # page not found on current webpage
                return False
        else:
            # Page_target element not found
            return False

    @classmethod
    def change_current_user_password(cls, new_passwd):
        cls.driver.find_element_by_id("top_user").click()
        WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located((By.ID, "password")))
        cls.driver.find_element_by_id("password").send_keys(new_passwd)
        cls.driver.find_element_by_id("submit").click()
        return cls.check_element_on_page((By.ID, "flash_success"))

    @classmethod
    def fill_initial_config(cls,elements=None):
        WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located((By.ID, "config_calibre_dir")))
        accordions=cls.driver.find_elements_by_class_name("accordion-toggle")
        opener = list()
        process_checkboxes = dict()
        process_elements = dict()
        process_options =dict()
        process_select = dict()
        # special handling for checkboxes
        checkboxes = ['config_uploading', 'config_anonbrowse', 'config_public_reg', 'config_remote_login',
                      'config_access_log']
        options = ['config_log_level', 'config_google_drive_folder']
        selects = ['config_ebookconverter']
        # depending on elements open accordions or not
        if any(key in elements for key in ['config_port', 'config_certfile','config_keyfile']):
            opener.append(1)
        if any(key in elements for key in ['config_log_level','config_logfile', 'config_access_logfile',
                                           'config_access_log']):
            opener.append(2)
        if any(key in elements for key in ['config_uploading', 'config_anonbrowse', 'config_public_reg',
                                           'config_remote_login', 'config_use_goodreads', 'config_goodreads_api_key',
                                           'config_goodreads_api_secret']):
            opener.append(3)
        if any(key in elements for key in ['config_ebookconverter', 'config_calibre',
                                           'config_converterpath','config_rarfile_location']):
            opener.append(4)

        # open all necessary accordions
        for o in opener:
            accordions[o].click()
        # check if checkboxes are in list and seperate lists
        for element,key in enumerate(elements):
            if key in checkboxes:
                process_checkboxes[key] = elements[key]
            elif key in options:
                process_options[key] = elements[key]
            elif key in selects:
                process_select[key] = elements[key]
            else:
                process_elements[key] = elements[key]
        # process all checkboxes Todo: If status was wrong before is not included in response
        for checkbox in process_checkboxes:
            ele = cls.driver.find_element_by_id(checkbox)
            if (elements[checkbox] == 1 and not ele.is_selected() )or elements[checkbox] == 0 and ele.is_selected():
                ele.click()

        for select in process_select:
            ele = cls.driver.find_elements_by_name(select)
            time.sleep(1)
            for el in ele:
                if el.get_attribute('id') == elements[select]:
                    el.click()
                    break

        # process all selects
        for option, key in enumerate(process_options):
            select = Select(cls.driver.find_element_by_id(key))
            select.select_by_visible_text(process_options[key])

        # process all text fields
        for element, key in enumerate(process_elements):
            ele = cls.driver.find_element_by_id(key)
            ele.clear()
            ele.send_keys(process_elements[key])

        # finally submit settings
        cls.driver.find_element_by_name("submit").click()

    @classmethod
    def fill_basic_config(cls,elements=None):
        cls.goto_page('basic_config')
        cls.fill_initial_config(elements)

    @classmethod
    def fill_view_config(cls,elements=None):
        cls.goto_page('view_config')
        WebDriverWait(cls.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "discover")))
        accordions=cls.driver.find_elements_by_class_name("accordion-toggle")
        opener = list()
        process_checkboxes = dict()
        process_elements = dict()
        process_options = dict()
        process_selects = dict()
        # special handling for checkboxes
        checkboxes = ['admin_role', 'download_role', 'upload_role', 'edit_role', 'delete_role', 'passwd_role',
                        'edit_shelf_role', 'show_32', 'show_512', 'show_16', 'show_128',
                        'show_2', 'show_4', 'show_8', 'show_64', 'show_256',
                        'Show_detail_random', 'Show_mature_content', 'show_4096']
        options = ['config_read_column']
        selects = ['config_theme']
        # depending on elements open accordions or not
        if any(key in elements for key in ['config_calibre_web_title', 'config_books_per_page', 'config_theme',
                                           'config_random_books', 'config_columns_to_ignore',
                                           'config_read_column', 'config_title_regex', 'config_mature_content_tags']):
            opener.append(0)
        if any(key in elements for key in ['admin_role', 'download_role', 'upload_role', 'edit_role',
                                           'delete_role', 'passwd_role', 'edit_shelf_role']):
            opener.append(1)
        if any(key in elements for key in ['show_32', 'show_512', 'show_16', 'show_128',
                                           'show_2', 'show_4', 'show_8', 'show_64',
                                           'show_256', 'Show_detail_random', 'Show_mature_content',
                                           'show_4096']):
            opener.append(2)

        # open all necessary accordions
        for o in opener:
            accordions[o].click()
        # check if checkboxes are in list and seperate lists
        for element,key in enumerate(elements):
            if key in checkboxes:
                process_checkboxes[key] = elements[key]
            elif key in options:
                process_options[key] = elements[key]
            elif key in selects:
                process_selects[key] = elements[key]
            else:
                process_elements[key] = elements[key]

        # process all checkboxes Todo: If status was wrong before is not included in response
        for checkbox in process_checkboxes:
            ele = cls.driver.find_element_by_id(checkbox)
            if (elements[checkbox] == 1 and not ele.is_selected() )or elements[checkbox] == 0 and ele.is_selected():
                ele.click()

        # process all text fields
        for element, key in enumerate(process_elements):
            ele = cls.driver.find_element_by_id(key)
            ele.clear()
            ele.send_keys(process_elements[key])

        for option, key in enumerate(process_selects):
            select = Select(cls.driver.find_element_by_id(key))
            select.select_by_visible_text(process_selects[key])

        # finally submit settings
        cls.driver.find_element_by_name("submit").click()


    def restart_calibre_web(self):
        self.goto_page('admin_setup')
        self.driver.find_element_by_id('admin_restart').click()
        element = self.check_element_on_page((By.ID, "restart"))
        element.click()
        time.sleep (10)

    def stop_calibre_web(self):
        self.goto_page('admin_setup')
        self.driver.find_element_by_id('admin_stop').click()
        element = self.check_element_on_page((By.ID, "shutdown"))
        element.click()

    def list_domains(self, allow=True):
        if not self.check_element_on_page((By.ID, "mail_server")):
            if not self.goto_page('mail_server'):
                print('got page failed')
                return False
        if allow:
            table_id = 'domain-allow-table'
        else:
            table_id = 'domain-deny-table'
        if not self.check_element_on_page((By.ID, table_id)):
            print('table not found')
            return False
        time.sleep(1)
        parser = lxml.etree.HTMLParser()
        html = self.driver.page_source

        tree = lxml.etree.parse(StringIO(html), parser)
        vals = tree.xpath("//table[@id='" + table_id + "']/tbody/tr")
        val = list()
        for va in vals:
            try:
                go = va.getchildren()[0].getchildren()[0]
                id = go.attrib['data-pk']
                delButton = self.driver.find_element_by_css_selector("a[data-pk='"+id+"']")
                editButton = self.driver.find_element_by_css_selector("a[data-domain-id='"+id+"']")
                val.append({'domain':go.text, 'delete': delButton, 'edit':editButton, 'id':id})
            except IndexError:
                pass
        return val

    def edit_domains(self, id,  new_value, accept, allow=True):
        if allow:
            table_id = 'domain-allow-table'
        else:
            table_id = 'domain-deny-table'
        if not self.check_element_on_page((By.ID, table_id)):
            return False
        editButton = self.check_element_on_page((By.CSS_SELECTOR, "a[data-pk='" + id + "']"))
        if not editButton:
            return False
        editButton.click()
        editor=self.check_element_on_page((By.CLASS_NAME, "input-sm"))
        if not editor:
            return False
        editor.clear()
        editor.send_keys(new_value)
        if accept:
            submit = self.check_element_on_page((By.CLASS_NAME, "editable-submit"))
        else:
            submit = self.check_element_on_page((By.CLASS_NAME, "editable-cancel"))
        submit.click()

    def delete_domains(self, id, accept, allow=True):
        if allow:
            table_id = 'domain-allow-table'
        else:
            table_id = 'domain-deny-table'
        if not self.check_element_on_page((By.ID, table_id)):
            return False
        deleteButton = self.check_element_on_page((By.CSS_SELECTOR, "a[data-domain-id='" + id + "']"))
        if not deleteButton:
            return False
        deleteButton.click()
        if accept:
            submit = self.check_element_on_page((By.ID, "btndeletedomain"))
        else:
            submit = self.check_element_on_page((By.ID, "btncancel"))
        submit.click()

    def add_domains(self, new_value, allow=True):
        if allow:
            edit = self.check_element_on_page((By.ID, "domainname_allow"))
            add = self.check_element_on_page((By.ID, "domain_allow_submit"))
        else:
            edit = self.check_element_on_page((By.ID, "domainname_deny"))
            add = self.check_element_on_page((By.ID, "domain_deny_submit"))
        if not edit:
            return False
        edit.clear()
        edit.send_keys(new_value)
        if not add:
            return False
        add.click()

    def list_restrictions(self, type):
        if type == 0:
            if not self.goto_page('mail_server'):  # ToDo check
                return False
        elif type == 1:
            if not self.goto_page('mail_server'):  # ToDo check
                return False
        elif type == 2:
            if not self.goto_page('mail_server'):  # ToDo check
                return False
        elif type == 3:
            if not self.goto_page('mail_server'):  # ToDo check
                return False
        table_id='restrict-elements-table'
        if not self.check_element_on_page((By.ID, table_id)):
            return False
        parser = lxml.etree.HTMLParser()
        html = self.driver.page_source

        tree = lxml.etree.parse(StringIO(html), parser)
        vals = tree.xpath("//table[@id='"+table_id+"']/tbody/tr")
        val = list()
        for va in vals:
            try:
                go = va.getchildren()[0].getchildren()
                id = go[0].attrib['data-pk']
                delButton = self.driver.find_element_by_css_selector("a[data-pk='"+id+"']")
                editButton = self.driver.find_element_by_css_selector("a[data-restriction-id='"+id+"']")
                val.append({'restriction':go[0].text,
                            'delete': delButton,
                            'edit':editButton,
                            'id':id,
                            'type': go[1].text})
            except IndexError:
                pass
        return val

    def edit_restrictions(self, id,  new_value, accept):
        table_id = 'restrict-elements-table'
        if not self.check_element_on_page((By.ID, table_id)):
            return False
        editButton = self.check_element_on_page((By.CSS_SELECTOR, "a[data-pk='" + id + "']"))
        if not editButton:
            return False
        editButton.click()
        editor=self.check_element_on_page((By.CLASS_NAME, "input-sm"))
        if not editor:
            return False
        editor.clear()
        editor.send_keys(new_value)
        if accept:
            submit = self.check_element_on_page((By.CLASS_NAME, "editable-submit"))
        else:
            submit = self.check_element_on_page((By.CLASS_NAME, "editable-cancel"))
        submit.click()

    def delete_restrictions(self, id):
        table_id = 'restrict-elements-table'
        if not self.check_element_on_page((By.ID, table_id)):
            return False
        deleteButton = self.check_element_on_page((By.CSS_SELECTOR, "a[data-restriction-id='" + id + "']"))
        if not deleteButton:
            return False
        deleteButton.click()

    def add_restrictions(self, new_value, allow=True):
        edit = self.check_element_on_page((By.ID, "add_element"))
        if allow:
            add = self.check_element_on_page((By.ID, "submit_allow"))
        else:
            add = self.check_element_on_page((By.ID, "submit_restrict"))
        if not edit:
            return False
        edit.clear()
        edit.send_keys(new_value)
        if not add:
            return False
        add.click()

    @classmethod
    def setup_server(cls, test_on_return, elements):
        cls.goto_page('mail_server')
        process_options = dict()
        process_elements = dict()
        options = ['mail_use_ssl']
        for element,key in enumerate(elements):
            if key in options:
                process_options[key] = elements[key]
            else:
                process_elements[key] = elements[key]

        # process all selects
        for option, key in enumerate(process_options):
            select = Select(cls.driver.find_element_by_id(key))
            select.select_by_visible_text(process_options[key])

        # process all text fields
        for element, key in enumerate(process_elements):
            ele = cls.driver.find_element_by_id(key)
            ele.clear()
            ele.send_keys(process_elements[key])
        if test_on_return:
            clicker = 'test'
        else:
            clicker = 'submit'
        cls.driver.find_element_by_name(clicker).click()



    @classmethod
    def check_element_on_page(cls, element, timeout=5):
        try:
            el = WebDriverWait(cls.driver, timeout).until(EC.presence_of_element_located(element))
            return el
        except TimeoutException:
            return False

    @classmethod
    def edit_user(cls, name, element):
        cls.goto_page('admin_setup')
        user = cls.driver.find_elements_by_xpath("//table[@id='table_user']/tbody/tr/td/a")
        for ele in user:
            if name == ele.text:
                ele.click()
                if not cls.check_element_on_page((By.ID, "email")):
                    print('Could not edit user: %s' % name)
                    return False
                return cls.change_user(element)
        print('User: %s not found' % name)
        return False


    @classmethod
    def change_visibility_me(cls, nav_element):
        ''' All Checkboses are:
            'show_32','show_512', 'show_16', 'show_128', 'show_2', 'show_4',
            'show_8', 'show_64', 'show_256', 'Show_detail_random' '''
        selects = ['locale', 'default_language']
        cls.goto_page('user_setup')
        process_selects = dict()
        process_checkboxes = dict()
        if 'kindle_mail' in nav_element:
            ele = cls.driver.find_element_by_id('kindle_mail')
            ele.clear()
            ele.send_keys(nav_element['kindle_mail'])
            nav_element.pop('kindle_mail')
        if 'password' in nav_element:
            ele = cls.driver.find_element_by_id('password')
            ele.clear()
            ele.send_keys(nav_element['password'])
            nav_element.pop('password')
        if 'email' in nav_element:
            ele = cls.driver.find_element_by_id('email')
            ele.clear()
            ele.send_keys(nav_element['email'])
            nav_element.pop('email')


        # check if checkboxes are in list and seperate lists
        for element,key in enumerate(nav_element):
            if key in selects:
                process_selects[key] = nav_element[key]
            else:
                process_checkboxes[key] = nav_element[key]

        # process all checkboxes Todo: If status was wrong before is not included in response
        for checkbox in process_checkboxes:
            ele = cls.driver.find_element_by_id(checkbox)
            if (nav_element[checkbox] == 1 and not ele.is_selected()) or nav_element[checkbox] == 0 and ele.is_selected():
                ele.click()

        # process all selects
        for option, key in enumerate(process_selects):
            select = Select(cls.driver.find_element_by_id(key))
            select.select_by_visible_text(process_selects[key])

        # finally submit settings
        cls.driver.find_element_by_id("submit").click()


    def create_shelf(self, name, public=False):
        self.goto_page('create_shelf')
        ele = self.check_element_on_page((By.ID,'title'))
        if ele:
            ele.clear()
            ele.send_keys(name)
            if public:
                public_shelf = self.check_element_on_page((By.NAME,'is_public'))
                if public_shelf:
                    public_shelf.click()
                else:
                    return False
            submit = self.check_element_on_page((By.ID, 'submit'))
            if submit:
                submit.click()
                return True
        return False

    @classmethod
    def create_user(cls, name, config):
        if name:
            config['nickname'] = name
        cls.goto_page('create_user')
        return cls.change_user(config)

    @classmethod
    def change_user(cls, config):
        ''' All Checkboses are:
            'show_32','show_512', 'show_16', 'show_128', 'show_2', 'show_4',
            'show_8', 'show_64', 'show_256', 'Show_detail_random' '''
        selects = ['locale', 'default_language']
        text_inputs = ['kindle_mail','email', 'password', 'nickname']
        process_selects = dict()
        process_checkboxes = dict()
        process_text = dict()
        # check if checkboxes are in list and seperate lists
        if 'resend_password' in config:
            ele = cls.driver.find_element_by_id('resend_password')
            if ele:
                ele.click()
                return cls.driver.find_element_by_id('flash_success')
            return ele

        for element,key in enumerate(config):
            if key in selects:
                process_selects[key] = config[key]
            elif key in text_inputs:
                process_text[key] = config[key]
            else:
                process_checkboxes[key] = config[key]

        # process all checkboxes Todo: If status was wrong before is not included in response
        for checkbox in process_checkboxes:
            ele = cls.driver.find_element_by_id(checkbox)
            if (config[checkbox] == 1 and not ele.is_selected()) or config[checkbox] == 0 and ele.is_selected():
                ele.click()
                eleclick = cls.driver.find_element_by_id(checkbox)
                if (config[checkbox] == 1 and not eleclick.is_selected()) or config[checkbox] == 0 and eleclick.is_selected():
                    print('click did not work')
                    time.sleep(2)
                    ele.click()

        # process all selects
        for option, key in enumerate(process_selects):
            select = Select(cls.driver.find_element_by_id(key))
            select.select_by_visible_text(process_selects[key])

        # process all text fields
        for element, key in enumerate(process_text):
            ele = cls.driver.find_element_by_id(key)
            ele.clear()
            ele.send_keys(config[key])

        # finally submit settings
        cls.driver.find_element_by_id("submit").click()


    @classmethod
    def get_opds_index(cls,text):
        ret = dict()
        parser = lxml.etree.HTMLParser()
        try:
            tree = lxml.etree.fromstring(text.encode('utf-8'), parser)
            # tree = lxml.etree.parse(StringIO(text), parser)
            ret['title'] = tree.xpath("/html/body/feed/title")[0].text
            ret['id'] = tree.xpath("/html/body/feed/id")[0].text
            ret['links'] = tree.xpath("/html/body/feed/link")
            ret['update'] = tree.xpath("/html/body/feed/updated")[0].text
            ret['author'] = tree.xpath("/html/body/feed/author/name")[0].text
            ret['uri'] = tree.xpath("/html/body/feed/author/uri")[0].text
            for element in tree.xpath("/html/body/feed/entry"):
                el = dict()
                el['link'] = element.find('link').attrib['href']
                el['id'] = element.find('id').text
                el['updated'] = element.find('updated').text
                el['content'] = element.find('content').text
                ret[element.find('title').text] = el
        except:
            pass
        return ret


    @classmethod
    def get_opds_feed(cls, text):
        ret = dict()
        parser = lxml.etree.HTMLParser()
        try:
            tree = lxml.etree.fromstring(text.encode('utf-8'), parser)
            # tree = lxml.etree.parse(StringIO(text.encode('utf-8')), parser)
            ret['title'] = tree.xpath("/html/body/feed/title")[0].text
            ret['id'] = tree.xpath("/html/body/feed/id")[0].text
            ret['links'] = tree.xpath("/html/body/feed/link")
            ret['update'] = tree.xpath("/html/body/feed/updated")[0].text
            ret['author'] = tree.xpath("/html/body/feed/author/name")[0].text
            ret['uri'] = tree.xpath("/html/body/feed/author/uri")[0].text
            key = 0
            for element in tree.xpath("/html/body/feed/entry"):
                el = dict()
                el['link'] = element.find('link').attrib['href']
                el['id'] = element.find('id').text
                el['title'] = element.find('title').text
                ele =  element.find('language')
                if ele is not None and ele.text:
                    el['language'] = ele
                ele = element.findall('link')
                if ele is not None:
                    el['cover'] = ele[0].attrib['href']
                    if len(ele) >=2:
                        el['download'] = ele[2].attrib['href']
                        el['filesize'] = ele[2].attrib['length']
                        el['filetype'] = ele[2].attrib['type']
                        el['time'] = ele[2].attrib['mtime']
                ele = element.find('author')
                if ele is not None:
                    author_list = list()
                    for aut in ele.getchildren():
                        author_list.append(aut.text)
                    el['author']=author_list
                    el['author_len'] = len(el['author'])

                ret[key] = el
                key += 1
        except:
            pass
        ret['len'] = key
        return ret


    @classmethod
    def get_opds_search(cls, text):
        parser = lxml.etree.HTMLParser()
        tree = lxml.etree.fromstring(text.encode('utf-8'), parser)

        pass

    @classmethod
    def get_user_list(cls):
        cls.goto_page('admin_setup')
        return cls.driver.find_elements_by_xpath("//table[@id='table_user']/tbody/tr")

    @classmethod
    def get_books_displayed(cls):
        parser = lxml.etree.HTMLParser()
        html = cls.driver.page_source

        tree = lxml.etree.parse(StringIO(html), parser)
        books_rand = list()
        br = tree.xpath("//*[@class='discover random-books']/div/div")
        for book_rand in br:
            ele = book_rand.getchildren()
            meta=ele[1].getchildren()
            book_r = dict()
            book_r['link'] = ele[0].getchildren()[0].attrib['href']
            book_r['ele'] = cls.check_element_on_page((By.XPATH,"//a[@href='"+book_r['link']+"']/img"))
            book_r['id'] = book_r['link'][6:]
            book_r['title']= meta[0].getchildren()[0].text
            authors = meta[1].getchildren()
            book_r['author'] = [a.text for a in authors]
            if len(meta) == 3:
                ratings = meta[2].getchildren()
                counter = 0
                for rating in ratings:
                    if rating.attrib['class'] == 'glyphicon glyphicon-star good':
                        counter += 1
                book_r['rating'] = counter
            books_rand.append(book_r)
        books = list()
        b = tree.xpath("//*[@class='discover load-more']/div/div")
        for book in b:
            ele = book.getchildren()
            # ele[0] -> cover
            meta=ele[1].getchildren()
            bk = dict()
            bk['link'] = ele[0].getchildren()[0].attrib['href']
            bk['id'] = bk['link'][6:]
            bk['ele'] = cls.check_element_on_page((By.XPATH,"//a[@href='"+bk['link']+"']/img"))
            bk['title']= meta[0].getchildren()[0].text
            authors = meta[1].getchildren()
            bk['author'] = [a.text for a in authors]
            if len(meta) == 3:
                ratings = meta[2].getchildren()
                counter = 0
                for rating in ratings:
                    if rating.attrib['class'] == 'glyphicon glyphicon-star good':
                        counter += 1
                bk['rating'] = counter
            books.append(bk)

        pages = tree.xpath("//*[@class='pagination']/a")
        pagination = None
        if len(pages):
            pagination = [p.text for p in pages]
        return [books_rand, books, pagination]


    @classmethod
    def get_book_details(cls,id=-1,root_url="http://127.0.0.1:8083"):
        if id>0:
            cls.driver.get(root_url + "/book/"+str(id))
        cls.check_element_on_page((By.TAG_NAME,"h2"))
        ret = dict()
        try:
            parser = lxml.etree.HTMLParser()
            html = cls.driver.page_source

            tree = lxml.etree.parse(StringIO(html), parser)
            reader = tree.findall("//*[@aria-labelledby='read-in-browser']/li/a")
            ret['reader'] = [r.text for r in reader]

            title = tree.find("//h2")
            if title is not None:
                ret['title'] = title.text
            author = tree.findall("//*[@class='author']/a")
            ret['author'] = [aut.text for aut in author]

            ret['rating']= len(tree.findall("//*[@class='glyphicon glyphicon-star good']"))

            languages = tree.findall("//*[@class='languages']//span")
            if languages:
                only_lang = languages[0].text.split(': ')[1].lstrip()
                ret['languages'] = only_lang.split(', ')

            ids = tree.findall("//*[@class='identifiers']//a")
            ret['Identifier'] = [id.text for id in ids]

            tags = tree.findall("//*[@class='tags']//a")
            ret['tag'] = [tag.text for tag in tags]

            publishers = tree.findall("//*[@class='publishers']//a")
            ret['publisher'] = [pub.text for pub in publishers]

            # Pubdate
            pubdate = tree.xpath("//p[starts-with(text(),'Publishing date:')]")
            if len(pubdate):
                ret['pubdate']= pubdate[0].text

            comment = tree.find("//*[@class='comments']")
            ret['comment'] = ''
            if comment is not None:
                try:
                    for ele in comment.getchildren()[1:]:
                        ret['comment'] += ele.text
                except:
                    for ele in comment.getchildren()[1].getchildren():
                        ret['comment'] += ele.text

            add_shelf = tree.findall("//*[@id='add-to-shelves']//a")
            ret['add_shelf'] = [sh.text.strip().lstrip() for sh in add_shelf]

            del_shelf = tree.findall("//*[@id='remove-from-shelves']//a")
            ret['del_shelf'] = [sh.text.strip().lstrip() for sh in del_shelf]

            ret['edit_enable'] = tree.find("//*[@class='glyphicon glyphicon-edit']") is not None

            ele = tree.xpath("//*[starts-with(@id,'sendbtn')]")
            # bk['ele'] = cls.check_element_on_page((By.XPATH, "//a[@href='" + bk['link'] + "']/img"))
            if len(ele):
                all = tree.findall("//*[@aria-labelledby='send-to-kindle']/li/a")
                if all:
                    ret['kindlebtn'] = cls.driver.find_element_by_id("sendbtn2")
                    ret['kindle'] = all
                else:
                    ret['kindlebtn'] = cls.driver.find_element_by_id("sendbtn")
                    # ele = dict()
                    #ele['ele'] = ele
                    #ele['link'] = ele[0].attrib['href']
                    ret['kindle'] = list(ele)
            else:
                ret['kindle'] = None
                ret['kindlebtn'] = None

            download1 = tree.findall("//*[@aria-labelledby='btnGroupDrop1']//a")
            if not download1:
                download1 = tree.xpath("//*[starts-with(@id,'btnGroupDrop')]")
                if download1:
                    ret['download'] = list()
                    for ele in download1:
                        ret['download'].append(ele.getchildren()[0].tail.strip())
            else:
                ret['download'] = [d.text for d in download1]

            ret['read']= tree.find("//*[@id='have_read_cb']") is not None

            series = tree.xpath("//*[contains(@href,'series')]/ancestor::p")
            if series:
                ret['series_all'] = ""
                ret['series_index'] = series[0].text[5:-3]
                for ele in series[0].iter():
                    ret['series_all'] += ele.text
                    ret['series'] = ele.text

            cust_columns = tree.xpath("//div[@class='real_custom_columns']")
            if len(cust_columns) :      # we have custom columns
                ret['cust_columns']=list()
                for col in cust_columns: # .getchildren()[0].getchildren()[1:]:
                    element = dict()
                    if len(col.text.strip()):
                        if len(col.getchildren()):
                            element['Text'] = col.text.lstrip().split(':')[0]
                            element['value'] = col.getchildren()[0].attrib['class'][20:]
                            ret['cust_columns'].append(element)
                        elif ':' in col.text:
                            element['Text'] = col.text.lstrip().split(':')[0]
                            element['value'] = col.text.split(':')[1].strip()
                            ret['cust_columns'].append(element)
                        else:
                            pass
        except Exception as e:
            print(e)
            pass
        return ret

    def get_books_list(self):
        pass

    @classmethod
    def check_tasks(cls):
        if cls.goto_page('tasks'):
            parser = lxml.etree.HTMLParser()
            html = cls.driver.page_source

            tree = lxml.etree.parse(StringIO(html), parser)
            vals = tree.xpath("//table[@id='table']/tbody/tr")
            val = list()
            for va in vals:
                try:
                    go = va.getchildren()
                    if len(go) == 6:
                        val.append({'user':go[0].text,'task':go[1].text,'result':go[2].text,
                                    'progress':go[3].text,'duration':go[4].text,'start':go[5].text})
                    else:
                        val.append({'user':None,'task':go[0].text,'result':go[1].text,
                                    'progress':go[2].text,'duration':go[3].text,'start':go[4].text})

                except IndexError:
                    pass
            # val = cls.driver.find_elements_by_xpath("//table[@id='table']/tbody/tr/td")
            return val
        else:
            return False

    @classmethod
    def edit_book(cls, id=-1, content=dict(), custom_content=dict(), detail_v=False, root_url='http://127.0.0.1:8083'):
        if id>0:
            cls.driver.get(root_url + "/admin/book/"+str(id))
        cls.check_element_on_page((By.ID,"book_edit_frm"))

        if custom_content:
            # Handle custom columns:
            parser = lxml.etree.HTMLParser()
            html = cls.driver.page_source

            tree = lxml.etree.parse(StringIO(html), parser)

            cust_columns = tree.xpath("//*[starts-with(@for,'custom_column')]")
            if cust_columns:
                for col in cust_columns:
                    element = dict()
                    element['label'] = col.text
                    element['index'] = col.attrib['for']
                    if element['label'] in custom_content:
                        # element['element'] = cls.check_element_on_page((By.ID, element['index']))
                        if col.getnext().tag == 'select':
                            select = Select(cls.driver.find_element_by_id(element['index']))
                            select.select_by_visible_text(custom_content[element['label']])
                            # element['options'] = [x.text for x in tree.findall("//select[@id='"+
                            #                                                  col.attrib['for'] + "']/option")]
                            # element['type'] = 'select'
                        elif col.getnext().tag == 'input':
                            edit = cls.check_element_on_page((By.ID, element['index']))
                            edit.send_keys(Keys.CONTROL, "a")
                            edit.send_keys(Keys.DELETE)
                            edit.send_keys(custom_content[element['label']])
                            '''if 'min' in col.getnext().attrib:
                                element['type'] = 'rating'
                            elif 'text' in col.getnext().attrib:
                                element['type'] = 'text'
                            else:
                                element['type'] = 'number'''
                        # elif col.getnext().tag == 'input':
                        # ret.append(element)

        if 'rating' in content:
            cls.driver.execute_script("arguments[0].setAttribute('value', arguments[1])",
                                  cls.driver.find_element_by_xpath("//input[@id='rating']"), content['rating'])
            content.pop('rating')

        if 'description' in content:
            cls.driver.switch_to_frame("description_ifr")
            ele = cls.check_element_on_page((By.ID, 'tinymce'))
            ele.clear()
            ele.send_keys(content['description'])
            cls.driver.switch_to_default_content()
            content.pop('description')


        for element, key in enumerate(content):
            ele = cls.check_element_on_page((By.ID, key))
            ele.send_keys(Keys.CONTROL, "a")
            ele.send_keys(Keys.DELETE)
            if ele.get_attribute('value') != '':
                print("clear didn't work")
            ele.send_keys(content[key])

        # not working
        if 'pubdate' in content:
            ele = cls.check_element_on_page((By.ID, 'pubdate'))
            cls.driver.execute_script("$('#fake_pubdate').val('2019-10-11');")


        # don't stay on page after edit
        if detail_v:
            cls.check_element_on_page((By.NAME, "detail_view")).click()

        submit = cls.check_element_on_page((By.ID, "submit"))
        submit.click()
        return


        '''number
        'upload-cover'
        'pubdate'
        'upload-format'
        custom coloums
        'detail_view'
        'get_meta' '''

    @classmethod
    def get_convert_book(cls, id=-1, root_url='http://127.0.0.1:8083'):
        if id>0:
            cls.driver.get(root_url + "/admin/book/"+str(id))
        cls.check_element_on_page((By.ID,"book_edit_frm"))
        parser = lxml.etree.HTMLParser()
        html = cls.driver.page_source

        tree = lxml.etree.parse(StringIO(html), parser)
        ret = dict()
        ret['from_book'] = tree.findall("//select[@id='book_format_from']/option")
        ret['to_book'] = tree.findall("//select[@id='book_format_to']/option")
        if not ret['from_book'] and not ret['to_book']:
            ret['btn_from'] = False
            ret['btn_to'] = False
        else:
            ret['btn_from'] = cls.check_element_on_page((By.XPATH, "//select[@id='book_format_from']"))
            ret['btn_to'] = cls.check_element_on_page((By.XPATH, "//select[@id='book_format_to']"))
        return ret
