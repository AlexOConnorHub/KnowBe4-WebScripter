#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from argparse import ArgumentParser
from pyotp import TOTP
from json import load as jload
from sys import stderr
from pickle import dump as pdump, load as pload
from pathlib import Path

parser = ArgumentParser()

parser.add_argument('--driver', type=str, help='Driver to use', choices=['chrome', 'firefox', 'edge'], default='chrome')

parser.add_argument('--config-file', type=str, help='Name of the file specifying what all needs to be done', default='config.json')

parser.add_argument('--wait-for-auth', action='store_true', help='Whether to wait for user to authenticate or not')

parser.add_argument('--no-totp', action='store_true', help='Whether to use TOTP or not')

args = parser.parse_args()

config = jload(open(args.config_file))
base_url = config.get('base_url') if config.get('base_url') else 'https://training.knowbe4.com'
delay = config.get('delay') if config.get('delay') else 10
cookies_path = config.get('cookies') if config.get('cookies') else 'cookies.pkl'

# Load driver
if (args.driver == 'chrome'):
    driver = webdriver.Chrome()
elif (args.driver == 'firefox'):
    driver = webdriver.Firefox()
elif (args.driver == 'edge'):
    driver = webdriver.Edge()
else:
    print('Invalid driver specified', file=stderr)
    exit(1)

# If cookies.pkl exists, pload it
driver.get(base_url) # Hack, as I couldn't get cookies to pload without visiting the page first
if (cookies_path is not None and Path(cookies_path).exists()):
    cookies = pload(open(cookies_path, 'rb'))
    for cookie in cookies:
        driver.add_cookie(cookie)

driver.get(base_url)
if (not args.wait_for_auth and config.get('username') is not None and config.get('password') is not None):
    elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, 'email')))
    elem.send_keys(config.get('username'))
    driver.find_element(By.TAG_NAME, 'button').click()
    
    elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, 'password')))
    elem.send_keys(config.get('password'))
    driver.find_element(By.TAG_NAME, 'button').click()
    
    if (config.get('totp') is not None or args.no_totp):
        try:
            elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, 'otp_secret_key')))
            totp = TOTP(config.get('totp')).now()
            elem.send_keys(totp)
            driver.find_element(By.TAG_NAME, 'button').click()
        except:
            pass
WebDriverWait(driver, 60 if args.wait_for_auth else delay).until( lambda x : driver.current_url == base_url + '/ui/dashboard' )

if (cookies_path is not None):
    pdump(driver.get_cookies(), open(cookies_path, 'wb'))

for item in config.get('todo'):
    for todo in item.get('data'):
        driver.get(f"{base_url}{item.get('uri')}")
        if (item.get('buttonText') is not None):
            elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.XPATH, f"//*[text()[contains(.,'{item.get('buttonText')}')]]")))
            elem.click()
        elem = None
        for data in todo.get('values'):
            if data.get('id'):
                elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, data.get('id'))))
            elif data.get('name'):
                elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.NAME, data.get('name'))))
            elif (data.get('xpath') is not None):
                elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.XPATH, data.get('xpath'))))
            elif data.get('class_name'):
                elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CLASS_NAME, data.get('class_name'))))
            elif data.get('css_selector'):
                elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, data.get('css_selector'))))
            elif data.get('link_text'):
                elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.LINK_TEXT, data.get('link_text'))))
            elif data.get('partial_link_text'):
                elem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, data.get('partial_link_text'))))
            elif data.get('action'):
                elem = ActionChains(driver)

            if data.get('value'):
                elem.send_keys(data.get('value'))
                if (data.get('action') is not None):
                    elem.perform()
            elif data.get('click'):
                try:
                    elem.click()
                except Exception as e:
                    print("Error while clicking")
                    print(data)
                    exit(1)
            elif data.get('select'):
                select = Select(elem)
                select.select_by_visible_text(data.get('select_text'))
            elif data.get('special_key') is not None:
                key = data.get('special_key').upper()
                if key == 'RETURN':
                    elem.send_keys(Keys.RETURN)
                elif key == 'ENTER':
                    elem.send_keys(Keys.ENTER)
        if (todo.get('submitButtonText') is not None):
            WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.XPATH, f"//*[text()[contains(.,'{todo.get('submitButtonText')}')]]"))).click()
        elif (todo.get('submitButtonXPath') is not None):
            WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.XPATH, todo.get('submitButtonXPath')))).click()
