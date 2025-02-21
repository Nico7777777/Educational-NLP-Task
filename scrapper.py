from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (TimeoutException, NoSuchElementException, ElementClickInterceptedException)
from typing import Union
from pathlib import Path

# FIREFOX_DRIVER = "/home/andrei.nicola/apps/geckodriver"
FIREFOX_DRIVER = "/home/nick/apps/geckodriver"
PROBLEMS_FILE = "links/linkuri_probleme.txt"
FREE_PROBLEMS_FILE = "links/linkuri_free_probleme.txt"

website_url = "https://leetcode.com/problemset/"
service = FirefoxService(FIREFOX_DRIVER)  # Exemplu: /usr/local/bin/geckodriver
fremium_problems = []
user_timeout = 5
consent = False

path_disc = "datasets/discussion-test.csv"
path_prob = "datasets/problemset-test.csv"


def check_clean():
    file_path1 = Path(path_disc)
    file_path2 = Path(path_prob)
    if file_path1.is_file():
        file_path1.unlink()
    if file_path2.is_file():
        file_path2.unlink()
def get_date(div) -> Union[str, None]:
    try:
        date_tag = WebDriverWait(div, 2).until(
            EC.element_to_be_clickable((By.XPATH, ".//span[contains(@class, 'closed')]"))
        )
        return date_tag.text
    except (NoSuchElementException, TimeoutException):
        return None

def do_consent(driver):
    global consent
    try:
        consent_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Consent']"))
        )
        # print("Am gasit butonul de use data Consent!")
        consent_button.click()
        consent = True
    except TimeoutException:
        return

def comment_wrapper_aux(com_anc):
    # class = flex w-full flex-col py-3
    sixth_parent_div = com_anc.find_element(By.XPATH, "ancestor::div[6]")

    # mt-2 flex w-full flex-col text-label-2 dark:text-dark-label-2
    second_child_div = sixth_parent_div.find_element(By.XPATH, "div[2]")

    # class = FN9Jv
    fourth_descendant_div = second_child_div.find_element(By.XPATH, "./descendant::div[4]")

    all_comment_text = fourth_descendant_div.get_attribute('innerHTML')
    return sixth_parent_div, second_child_div, fourth_descendant_div, all_comment_text

def get_date_(sixth_parent_div):
    date_tag = sixth_parent_div.find_element(By.XPATH, ".//span")
    date = date_tag.text
    return date
def get_upvotes(second_child_div):
    upvotes_div = second_child_div.find_element(By.XPATH, ".//div[@class='text-xs cursor-pointer text-label-3 dark:text-dark-label-3 hover:text-label-2 dark:hover:text-dark-label-2']")
    upvotes = upvotes_div.text
    return upvotes
def get_response_username(el):
    ret = WebDriverWait(el, 10).until(
        EC.presence_of_element_located((By.XPATH, ".//a[contains(@href, '/u/') and normalize-space(text()) != '']"))
    )
    return ret.text
def get_response_date_(el):
    span_tag = el.find_element(By.XPATH, ".//span")
    date = span_tag.text
    return date
def get_response_upvotes(el):
    try:
        up_votes_tag = WebDriverWait(el, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'dark:hover:text-dark-label-2')]"))
        )
        upvotes = up_votes_tag.text
    except NoSuchElementException:
        upvotes = "upvotes"
    return upvotes

def get_response_text(el):
    try:
        wrapper = WebDriverWait(el, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'mYe_l')]"))
        )
        return wrapper.get_attribute('innerHTML')
    except NoSuchElementException:
        return ""

def get_description(driver):
    try:
        descrb_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'elfjS')]"))
        )
        descrb = descrb_tag.get_attribute("innerHTML")
        return descrb
    except (NoSuchElementException, TimeoutException):
        return None

def get_topics(driver) -> Union[str, None]:
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/tag/')]"))
        )
        tags = driver.find_elements(By.XPATH, "//a[contains(@href, '/tag/')]")
        # print("Click pe elementul 'Topics' efectuat cu succes!\n")
        for tag_ in tags:
            l = tag_.get_attribute('outerHTML')
            start = l.find(">") + 1
            stop = l.find("<", start + 1)
            return l[start:stop]
    except Exception as e_:
        return None

def get_difficulty(driver) -> Union[str, None]:
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'text-difficulty')]"))
        )
        tag = driver.find_element(By.XPATH, "//div[contains(@class, 'text-difficulty')]")
        return tag.text
    except Exception as e_:
        return None

def acc_sub_accrate(driver) -> Union[tuple[str, str, str], tuple[None, None, None]]:
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'text-label-1 dark:text-dark-label-1 text-sm font-medium')]"))
        )
        values = driver.find_elements(By.XPATH, "//div[contains(@class, 'text-label-1 dark:text-dark-label-1 text-sm font-medium')]")
        tup = (value.text for value in values)
        return tup
    except Exception as e_:
        return None, None, None



def dump_fremium_problems():
    global fremium_problems
    with open(FREE_PROBLEMS_FILE, "r") as g:
        fremium_problems = g.readlines()

def open_discussion(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Discussion')]"))
        )
        discussion_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Discussion')]")
        discussion_element.click()  # Dă click pe element
    except Exception as e:
        return
    

def go_to_next_comment_page(drv, timeout=2) -> bool:
    try:
        # drv.find_element(By.XPATH, "//button[@aria-label='next']")
        next_button = WebDriverWait(drv, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='next']"))
        )
        if next_button:
            next_button.click()
        return True
    except (NoSuchElementException, TimeoutException):
        return False
    except ElementClickInterceptedException:
        return False


def expand_read_more(parent_div) -> bool:
    try:
        read_more_button = WebDriverWait(parent_div, 1).until(
            EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class, 'text-md flex w-full items-center justify-center text-label-1 dark:text-dark-label-1')]"))
        )
        read_more_button.click()
        expand_read_more(parent_div)
        return True
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
        return False