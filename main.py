from selenium import webdriver as web
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager

from art import tprint

import time
from pathlib import Path
from random import randint


user_data = {
    'username': '',
    'password': '',
}

statistics = {
    'subscribed': 0,
    'failures': 0
}

driver = web.Chrome(ChromeDriverManager().install())

finish = 0


# Login Instagram
def log_in():
    driver.get('https://www.instagram.com/accounts/login/')

    time.sleep(3)

    first_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/button[2]'))
    )
    first_button.click()

    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input'))
    )
    username_field.send_keys(user_data['username'])

    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input'))
    )
    password_field.send_keys(user_data['password'])

    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[3]/button'))
    )
    login_button.click()

    time.sleep(10)


# Subscribe on user
def subscribe(user):
    url = f'https://www.instagram.com/{user}/'
    driver.get(url)
    time.sleep(3)

    try:
        follow_button = driver.find_element(By.XPATH, "//*[text()='Following' or \
                                  text()='Requested' or \
                                  text()='Follow' or \
                                  text()='Follow Back' or \
                                  text()='Unblock']")
        follow_button.click()
        time.sleep(3)
        statistics['subscribed'] += 1
        return f'[+] Follow {user}'
    except NoSuchElementException:
        if "Sorry, this page isn't available." in driver.page_source:
            return f'[!] The {user} does not exist'

        statistics['failures'] += 1
        return f"[!] Can't subscribe to the {user}. You are already subscribed to {user}"


# Protection from being blocked by instagram.
# Since we subscribe to people, you have to secure the account.
# This function delays the time of each n subscriptions
def guard_from_inst(amount):
    if amount % 100 == 0:
        seconds = randint(28800, 43200)
        # 8 - 12 hours
        time.sleep(seconds)
        return f'[!GUARD!] We wait for {seconds} seconds.'
    if amount % 50 == 0:
        seconds = randint(1800, 3600)
        # 30 - 60 minutes
        time.sleep(seconds)
        return f'[!GUARD!] We wait for {seconds} seconds.'
    if amount % 10 == 0:
        seconds = randint(300, 480)
        # 5 - 8 minutes
        time.sleep(seconds)
        return f'[!GUARD!] We wait for {seconds} seconds.'
    seconds = randint(60, 180)
    # 1 - 3 minutes
    # seconds
    time.sleep(seconds)
    return f'[!GUARD!] We wait for {seconds} seconds.'


# Going by nicknames in the file
def iteration(path='base/file_nik.txt'):
    new_data = ''
    with open(path, 'r') as file:
        subscribe_users = 0

        for user in file:
            user = user.strip()
            if user == '':
                continue
            if user.endswith(' COMPLETE'):
                new_data = new_data + user + '\n'
            else:
                ret = subscribe(user)
                if ret.endswith('exist'):
                    print(ret)
                    continue
                elif ret.startswith('[+]'):
                    subscribe_users += 1
                    print(guard_from_inst(subscribe_users))
                print(ret)
                changes = user + ' COMPLETE'
                new_data = new_data + changes + '\n'

    with open(path, 'w') as file:
        file.write(new_data)


# check exist file or not and suffix
def check_file(file_path='base/file_nik.txt'):
    if Path(file_path).is_file() and Path(file_path).suffix == '.txt':
        return True
    return False


def static():
    return f"The program is over\n" \
           f"You are subscribed to {statistics['subscribed']} users\n" \
           f"Unable to subscribe to {statistics['failures']} users"


try:
    tprint('INSTpy')
    print('INSTpy version 1.0.0')
    response = input("\n[!] Before you start using the program, \
    file must have the ending txt and be sure that file contain urls. \
    All set? ('y' or 'n'): ")
    path_to_file = input("Enter a file's path: ")
    if response == 'y' and check_file(path_to_file):
        user_data['username'] = input('Enter a username: ')
        user_data['password'] = input('Enter a password: ')
        log_in()
        print('[+]  You are successfully logged in')

        try:
            iteration(path_to_file)
        except Exception:
            print('[!] THE PROGRAM WAS STOPPED DUE TO AN UNKNOWN ERROR. \
            PLEASE WRITE US ABOUT THIS (INSTAGRAM - nikita_konakh).')
            driver.quit()
            finish = 1
            print(static())

    elif response == 'y' and not check_file():
        print('[!] Incorrect path to the file or format.')
    elif response == 'n':
        print("Goodbye! \
        Come back when it's ready!")
except Exception:
    print('[!]  Incorrect username or password')
    driver.quit()
    finish = 1


if finish == 0:
    driver.quit()
    print(static())
