#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import re
import mimetypes
from config_test import CALIBRE_WEB_PATH, TEST_DB, BOOT_TIME, VENV_PYTHON, base_path, TEST_OS
from selenium.webdriver.support.ui import WebDriverWait
from subproc_wrapper import process_open
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import errno
import psutil
from helper_environment import environment
from psutil import process_iter
import os
import sys
import socket
import importlib
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

try:
    import pdfkit
    convert_config = True
except ImportError:
    convert_config = False
try:
    from config_email import E_MAIL_ADDRESS, E_MAIL_SERVER_ADDRESS, STARTSSL, EMAIL_SERVER_PORT
    from config_email import E_MAIL_LOGIN, E_MAIL_PASSWORD
    if E_MAIL_ADDRESS != '' and E_MAIL_SERVER_ADDRESS !='' and E_MAIL_LOGIN !='' and E_MAIL_PASSWORD !='':
        email_config = True
    else:
        email_config = False
        print('config_email.py E-Mail not configured')
except ImportError:
    email_config = False

try:
    from config_email import SERVER_PASSWORD, SERVER_NAME, SERVER_FILE_DESTINATION, SERVER_USER, SERVER_PORT
    if SERVER_PASSWORD != '' and SERVER_NAME !='' and SERVER_FILE_DESTINATION !='' and SERVER_USER !='':
        server_config = True
    else:
        print('config_email.py Server not configured')
        server_config = False
except ImportError:
    server_config = False

try:
    import paramiko
except ImportError:
    print('Create config_email.py file to email finishing message')
    server_config = False

if os.name != 'nt':
    from signal import SIGKILL
else:
    from signal import SIGTERM as SIGKILL

try:
    import pycurl
    from io import BytesIO
    curl_available = True
except ImportError:
    pycurl = None
    BytesIO = None
    curl_available = False


def is_port_in_use(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            return True
        else:
            return False
    s.close()
    return False


# Function to return IP address
def get_Host_IP():
    if os.name!='nt':
        addrs = psutil.net_if_addrs()
        for ele, key in enumerate(addrs):
            if key != 'lo':
                if addrs[key][0][2]:
                    return addrs[key][0][1]
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP


def debug_startup(inst, __, ___, login=True, host="http://127.0.0.1:8083", env=None):

    # create a new Firefox session
    inst.driver = webdriver.Firefox()
    inst.driver.implicitly_wait(BOOT_TIME)
    inst.driver.maximize_window()

    # navigate to the application home page
    inst.driver.get(host)
    WebDriverWait(inst.driver, 5).until(EC.title_contains("Calibre-Web"))
    inst.login("admin", "admin123")
    # login
    if not login:
        inst.logout()


def startup(inst, pyVersion, config, login=True, host="http://127.0.0.1:8083",
            env=None, parameter=None, work_path=None, only_startup=False, only_metadata=False):
    print("\n%s - %s: " % (inst.py_version, inst.__name__))
    try:
        os.remove(os.path.join(CALIBRE_WEB_PATH, 'app.db'))
    except PermissionError:
        kill_dead_cps()
        time.sleep(5)
        try:
            os.remove(os.path.join(CALIBRE_WEB_PATH, 'app.db'))
        except Exception as e:
            print(e)
    except Exception as ex:
        print(ex)
    try:
        os.remove(os.path.join(CALIBRE_WEB_PATH, 'gdrive.db'))
    except PermissionError:
        time.sleep(5)
        try:
            os.remove(os.path.join(CALIBRE_WEB_PATH, 'gdrive.db'))
        except Exception as e:
            print(e)
    except Exception as ex:
        print(ex)
    try:
        os.chmod(TEST_DB, 0o764)
    except Exception:
        pass
    shutil.rmtree(TEST_DB, ignore_errors=True)
    if not only_metadata:
        try:
            shutil.copytree(os.path.join(base_path, 'Calibre_db'), TEST_DB)
        except FileExistsError:
            print('Test DB already present, might not be a clean version')
    else:
        try:
            os.makedirs(TEST_DB)
            shutil.copy(os.path.join(base_path, 'Calibre_db', 'metadata.db'), os.path.join(TEST_DB, 'metadata.db'))
        except FileExistsError:
            print('Metadata.db already present, might not be a clean version')
    command = [pyVersion, os.path.join(CALIBRE_WEB_PATH, u'cps.py')]
    if parameter:
        command.extend(parameter)
    inst.p = process_open(command, [1], sout=None, env=env, cwd=work_path)
    # create a new Firefox session
    inst.driver = webdriver.Firefox()
    # inst.driver = webdriver.Chrome()
    time.sleep(BOOT_TIME)
    if inst.p.poll():
        kill_old_cps()
        inst.p = process_open(command, [1], sout=None, env=env, cwd=work_path)
        print('Calibre-Web restarted...')
        time.sleep(BOOT_TIME)

    inst.driver.maximize_window()

    # navigate to the application home page
    inst.driver.get(host)
    WebDriverWait(inst.driver, 5).until(EC.title_contains("Calibre-Web"))
    if not only_startup:
        # Wait for config screen to show up
        inst.fill_db_config(dict(config_calibre_dir=config['config_calibre_dir']))
        del config['config_calibre_dir']

        # wait for cw to reboot
        time.sleep(5)
        try:
            WebDriverWait(inst.driver, 5).until(EC.presence_of_element_located((By.ID, "flash_success")))
        except Exception:
            pass

        if config:
            inst.fill_basic_config(config)
        time.sleep(BOOT_TIME)
        try:
            WebDriverWait(inst.driver, 5).until(EC.presence_of_element_located((By.ID, "flash_success")))
        except Exception:
            pass
        # login
        if not login:
            inst.logout()


def wait_Email_received(func):
    i = 0
    while i < 10:
        time.sleep(2)
        if func():
            return True
        i += 1
    return False


def check_response_language_header(url, header, expected_response, search_text):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.HTTPHEADER, header)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    if c.getinfo(c.RESPONSE_CODE) != expected_response:
        return False
    c.close()

    body = buffer.getvalue().decode('utf-8')
    return bool(re.search(search_text, body))


def digest_login(url, expected_response):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.HTTPHEADER,
             ["Authorization: Digest username=\"admin\", "
              "realm=\"calibre\", "
              "nonce=\"40f00b48437860f60066:9bcc076210c0bbc2ebc9278fbba05716bcc55e09daa59f53b9ebe864635cf254\", "
              "uri=\"/config\", algorithm=MD5, response=\"c3d1e34c67fd8b408a167ca61b108a30\", "
              "qop=auth, nc=000000c9, cnonce=\"2a216b9b9c1b1108\""])
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    if c.getinfo(c.RESPONSE_CODE) != expected_response:
        c.close()
        return False
    c.close()
    return True


def add_dependency(name, testclass_name):
    print("Adding dependencies")
    element_version = list()
    with open(os.path.join(CALIBRE_WEB_PATH, 'optional-requirements.txt'), 'r') as f:
        requirements = f.readlines()
    for element in name:
        if element.lower().startswith('local|'):
            # full_module_name = ".config_test." + element.split('|')[1]
            # The file gets executed upon import, as expected.
            # tmp = __import__('pkg', fromlist=['mod', 'mod2'])
            whl = importlib.__import__("config_test", fromlist=[element.split('|')[1]])
            element_version.append(whl.__dict__[element.split('|')[1]])
        for line in requirements:
            if element.lower().startswith('git|') \
                    and not line.startswith('#') \
                    and not line == '\n' \
                    and line.lower().startswith('git') \
                    and line.lower().endswith('#egg=' + element.lower().lstrip('git|')+'\n'):
                element_version.append(line.strip('\n'))
            elif not line.startswith('#') \
                    and not line == '\n' \
                    and not line.startswith('git') \
                    and not line.startswith('local') \
                    and line.upper().startswith(element.upper()):
                element_version.append(line.split('=', 1)[0].strip('>'))
                break

    for indx, element in enumerate(element_version):
        with process_open([VENV_PYTHON, "-m", "pip", "install", element], (0, 4)) as r:
            while r.poll() == None:
                r.stdout.readline().strip("\n")
            #if os.name == 'nt':
            #    while r.poll() == None:
            #        r.stdout.readline()
            #else:
            #    r.wait()
        if element.lower().startswith('git'):
            element_version[indx] = element[element.rfind('#egg=')+5:]

    environment.add_Environment(testclass_name, element_version)


def remove_dependency(names):
    for name in names:
        if name.startswith('git|'):
            name = name[4:]
        if name.startswith('local|'):
            name = name.split('|')[2]
        with process_open([VENV_PYTHON, "-m", "pip", "uninstall", "-y", name], (0, 5)) as q:
            if os.name == 'nt':
                while q.poll() == None:
                    q.stdout.readline()
            else:
                q.wait()


def kill_old_cps(port=8083):
    for proc in process_iter():
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == port:
                    proc.send_signal(SIGKILL)  # or SIGKILL
                    print('Killed old Calibre-Web instance')
                    break
        except (PermissionError, psutil.AccessDenied):
            pass
    # Give Calibre-Web time to die
    time.sleep(3)


def kill_dead_cps():
    for proc in process_iter():
        try:
            if 'python' in proc.name():
                res = [i for i in proc.cmdline() if 'cps.py' in i]
                if res:
                    proc.send_signal(SIGKILL)
                    print('Killed dead Calibre-Web instance')
                    time.sleep(2)
        except (PermissionError, psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    # Give Calibre-Web time to die
    time.sleep(3)


def unrar_path():
    if sys.platform == "win32":
        unrar_pth = ["C:\\program files\\WinRar\\unrar.exe", "C:\\program files(x86)\\WinRar\\unrar.exe"]
    else:
        unrar_pth = ["/usr/bin/unrar"]
    for element in unrar_pth:
        if os.path.isfile(element):
            return element
    return None


def is_unrar_not_present():
    return unrar_path() is None

def save_logfiles(inst, module_name):
    result = ""
    if not os.path.isdir(os.path.join(base_path, 'outcome')):
        os.makedirs(os.path.join(base_path, 'outcome'))
    datestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    outdir = os.path.join(base_path, 'outcome', module_name + '-' + datestamp)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    for file in ['calibre-web.log', 'calibre-web.log', 'calibre-web.log.1', 'calibre-web.log.2',
                 'access.log', 'access.log.1', 'access.log.2']:
        src = os.path.join(CALIBRE_WEB_PATH, file)
        dest = os.path.join(outdir, file)
        if os.path.exists(src):
            with open(src) as fc:
                if "Traceback" in fc.read():
                    result = file
            shutil.move(src,dest)
    inst.assertTrue(result == "", "Exception in File {}".format(result))

def get_attachment(filename):
    file_ = open(filename, 'rb')
    data = file_.read()
    file_.close()
    content_type, encoding = mimetypes.guess_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    attachment = MIMEBase(main_type, sub_type)
    attachment.set_payload(data)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    return attachment

def finishing_notifier(result_file):
    try:
        if server_config:
            result_upload(TEST_OS)
    except Exception as e:
        print(e)
    if convert_config:
        pdfkit.from_url(result_file, 'out.pdf')
    try:
        if email_config:
            msg = MIMEMultipart()
            message = MIMEText('Calibre-Web Tests finished')
            msg['Subject'] = 'Calibre-Web Tests on ' + TEST_OS + ' finished'
            msg['From'] = E_MAIL_ADDRESS
            msg['To'] = E_MAIL_ADDRESS
            msg.attach(message)
            if convert_config:
                msg.attach(get_attachment('out.pdf'))
            s = smtplib.SMTP(E_MAIL_SERVER_ADDRESS, EMAIL_SERVER_PORT)
            if STARTSSL:
                s.starttls()
            if E_MAIL_LOGIN and E_MAIL_PASSWORD:
                s.login(E_MAIL_LOGIN, E_MAIL_PASSWORD)
            s.send_message(msg)
            s.quit()
    except Exception as e:
        print(e)
    if convert_config:
        os.remove('out.pdf')

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def result_upload(TEST_OS):
    ssh = createSSHClient(SERVER_NAME, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
    ftp_client = ssh.open_sftp()
    file_destination = os.path.normpath(os.path.join(SERVER_FILE_DESTINATION, 'Calibre-Web TestSummary_' + TEST_OS + '.html')).replace('\\','/')
    ftp_client.put('./../../calibre-web/test/Calibre-Web TestSummary_' + TEST_OS + '.html', file_destination)
    ftp_client.close()

def poweroff(power):
    if power:
        if os.name == 'nt':
            os.system('shutdown /s')
        else:
            os.system('shutdown -P')
        time.sleep(12)


