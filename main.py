from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (TimeoutException, StaleElementReferenceException,
                                        NoSuchElementException, ElementClickInterceptedException)
from selenium import webdriver

from pathlib import Path
from typing import Union
import time
import csv

# FIREFOX_DRIVER = "/home/andrei.nicola/apps/geckodriver"
FIREFOX_DRIVER = "/home/nick/apps/geckodriver"
PROBLEMS_FILE = "links/linkuri_probleme.txt"
FREE_PROBLEMS_FILE = "links/linkuri_free_probleme.txt"

website_url = "https://leetcode.com/problemset/"
service = FirefoxService(FIREFOX_DRIVER)  # Exemplu: /usr/local/bin/geckodriver
fremium_problems = []
user_timeout = 3
consent = False
driver = None

path_disc = "datasets/discussion-test.csv"
path_prob = "datasets/problemset-test.csv"

def dump_fremium_problems():
    global fremium_problems
    with open(FREE_PROBLEMS_FILE, "r") as g:
        fremium_problems = g.readlines()

def open_discussion():
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Discussion')]"))
        )
        discussion_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Discussion')]")
        discussion_element.click()  # Dă click pe element
    except Exception as e:
        return

def get_topics() -> Union[str, None]:
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

def get_difficulty() -> Union[str, None]:
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'text-difficulty')]"))
        )
        tag = driver.find_element(By.XPATH, "//div[contains(@class, 'text-difficulty')]")
        return tag.text
    except Exception as e_:
        return None

def acc_sub_accrate() -> Union[tuple[str, str, str], tuple[None, None, None]]:
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'text-label-1 dark:text-dark-label-1 text-sm font-medium')]"))
        )
        values = driver.find_elements(By.XPATH, "//div[contains(@class, 'text-label-1 dark:text-dark-label-1 text-sm font-medium')]")
        tup = (value.text for value in values)
        return tup
    except Exception as e_:
        return None, None, None

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

# TODO: trebuie ca dupa ce verific asta sa si apas pe 'Show more replies' pana cand dispare
def has_responses(div) -> bool:
    global consent
    while True:
        show_more_replies_button = div.find_elements(By.XPATH, ".//*[contains(text(), 'Show more replies')]")
        if not show_more_replies_button:
            break
        for button in show_more_replies_button:
            button.click()
    while True:
        try:
            reply = WebDriverWait(div, 2).until(
                EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class, 'flex items-center gap-1 group shrink-0 cursor-pointer transition-colors')]"))
            )
            reply.click()
            time.sleep(0.4)
            return True
        except (NoSuchElementException, TimeoutException):
            return False
        except ElementClickInterceptedException:

            if not consent: # Consent - big white box
                try:
                    consent_button = WebDriverWait(div, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Consent']"))
                    )
                    # print("Am gasit butonul de use data Consent!")
                    consent_button.click()
                    consent = True
                except TimeoutException:
                    # print("Butonul de consimțământ nu este disponibil.")
                    # consent = True
                    return False
            else: # Google cookie - small left-bottom corner pop-up
                try:
                    cookie_button = WebDriverWait(div, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss privacy and legal settings display']"))
                    )
                    # print("Am gasit butonul de google cookie!")
                    cookie_button.click()
                except TimeoutException:
                    # print("Butonul de cookie nu este disponibil.")
                    return False

def get_date(div) -> Union[str, None]:
    try:
        date_tag = WebDriverWait(div, 2).until(
            EC.element_to_be_clickable((By.XPATH, ".//span[contains(@class, 'closed')]"))
        )
        return date_tag.text
    except (NoSuchElementException, TimeoutException):
        return None

def do_consent():
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

    # TODO: resolve stale
    # class = mt-2 flex w-full flex-col text-label-2 dark:text-dark-label-2
    second_child_div = sixth_parent_div.find_element(By.XPATH, "div[2]")

    # class = FN9Jv
    fourth_descendant_div = second_child_div.find_element(By.XPATH, "./descendant::div[4]")

    # TODO:
    # COMMENT TEXT
    # read_more_button = WebDriverWait(fourth_descendant_div, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(), 'read more')]"))
    # )
    # read_more_button = fourth_descendant_div.find_element(By.XPATH, ".//*[contains(text(), 'read more')]")
    # all_comment_text = "blablabla"
    # if read_more_button is None:
    #     print("Butonul de read more NU A FOST GASIT")
    #     # Apasă pe butonul "read more"
    # else:
    #     read_more_button.click()
    #     all_comment_text = read_more_button.get_attribute('innerHTML')

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
    except NoSuchElementExceptiondiscussion:
        return ""

def get_description():
    try:
        descrb_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'elfjS')]"))
        )
        descrb = descrb_tag.get_attribute("innerHTML")
        return descrb
    except (NoSuchElementException, TimeoutException):
        return None

def seek_for_responses(problem):
    time.sleep(3)
    pag = 1
    comment_id = 0
    while True:
        # Reîncercări pe fiecare pagină
        retries = 0
        max_retries_per_page = 3
        page_processed = False
        
        while retries < max_retries_per_page:
            try:
                # Aici gasesc lista de comentarii
                root_users_on_page = WebDriverWait(driver, user_timeout).until(
                    EC.presence_of_all_elements_located((By.XPATH, "/*//a[starts-with(@href, '/u/') and normalize-space(text()) != '']"))
                )

                # Procesează comentariile de pe această pagină
                for root_user in root_users_on_page:
                    try:
                        sixth_parent_div, second_child_div, fourth_descendant_div, comment_text = comment_wrapper_aux(root_user)

                        # DATE & UPVOTES
                        date, upvotes = get_date_(sixth_parent_div), get_upvotes(second_child_div)
                        # PROBLEM NAME
                        problem_name_ = problem[problem.rfind('/') + 1:-1]

                        comment_id += 1
                        writer_2.writerow([problem_name_, comment_id, 0, comment_text, date, upvotes, root_user.text])

                        # Verifică dacă există buton "READ MORE"
                        if expand_read_more(sixth_parent_div):
                            print(f"\\tHAS 'READ MORE' BUTTON")
                            if has_responses(sixth_parent_div):
                                parent_id = comment_id

                                # Navighează către răspunsuri
                                parent_div = sixth_parent_div.find_element(By.XPATH, "..") 
                                responses_block = parent_div.find_element(By.XPATH, ".//div[2]") 

                                try:
                                    div_elements = WebDriverWait(parent_div, 10).until(
                                        EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@class, 'flex w-full px-3 pb-2 pt-4 transition-[background] duration-500')]"))
                                    )
                                except TimeoutException:
                                    continue

                                for el in div_elements:
                                    comment_id += 1 
                                    username = get_response_username(el) 
                                    date = get_response_date_(el) 
                                    upvotes = get_response_upvotes(el) 
                                    text = get_response_text(el) 

                                    writer_2.writerow([problem_name_, comment_id, parent_id, text, date, upvotes, username])
                    except StaleElementReferenceException:
                        print(f"Sarim peste comentariul {comment_id}")
                        continue
                page_processed = True
                break

            except StaleElementReferenceException:
                retries += 1
                print(f"Pagina {pag} a eșuat. Reîncercăm... ({retries}/{max_retries_per_page})")
                
            
            if not page_processed and retries >= max_retries_per_page:
                print(f"Nu am putut procesa pagina {pag} după {max_retries_per_page} încercări.")
                break

        if not go_to_next_comment_page(driver):
            break
        
        pag += 1

def seek_for_responses2(problem):
    pag = 1
    comment_id = 0
    while True:
        tries = 0
        try:
            # Aici gasesc lista de comentarii
            com_ancs = WebDriverWait(driver, user_timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, "/*//a[starts-with(@href, '/u/') and normalize-space(text()) != '']"))
            )

            # afiseaza userii de pe acelasi nivel
            for com_anc in com_ancs:
                try:
                    sixth_parent_div, second_child_div, fourth_descendant_div, split_comment_texts = comment_wrapper_aux(com_anc)

                    comment_text = ""
                    for c_text in split_comment_texts:
                        comment_text += c_text.text

                    # DATE & UPVOTES
                    date, upvotes = get_date_(sixth_parent_div), get_upvotes(second_child_div)
                    # PROBLEM NAME
                    problem_name_ = problem[problem.rfind('/') + 1:]

                    comment_id += 1
                    # pretty_print(pag, com_anc.text, comment_id, 0, date, upvotes)
                    writer_2.writerow([problem_name_, comment_id, 0, comment_text, date, upvotes, com_anc.text])

                    # if expand_read_more(sixth_parent_div):
                    # print(f"\tHAS 'READ MORE' BUTTON")
                    expand_read_more(sixth_parent_div)
                    if has_responses(sixth_parent_div):
                        parent_id = comment_id
                        # print("\tHAS RESPONSES!")

                        # px-1 transition-[background] duration-500
                        parent_div = sixth_parent_div.find_element(By.XPATH, "..") # E BINE

                        # flex flex-col
                        responses_block = parent_div.find_element(By.XPATH, ".//div[2]") # E BINE

                        responses = responses_block.find_elements(By.XPATH, ".//a[contains(@href, '/u/')]")
                        try:
                            div_elements = WebDriverWait(parent_div, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@class, 'flex w-full px-3 pb-2 pt-4 transition-[background] duration-500')]"))
                            )
                        except TimeoutException:
                            continue
                        for el in div_elements:
                            comment_id += 1 # COMMENT_ID
                            username = get_response_username(el) # USERNAME
                            date = get_response_date_(el) # DATE
                            upvotes = get_response_upvotes(el) # UP-VOTES
                            text = get_response_text(el) # TEXT


                            writer_2.writerow([problem_name_, comment_id, parent_id, text, date, upvotes, username])
                except StaleElementReferenceException:
                    break

            else:
                if go_to_next_comment_page(driver):
                    pag += 1
                else:
                    break

        except (StaleElementReferenceException, TimeoutException):
            if tries <= 5:
                print(f"Page {pag} elements went stale, retrying on this page...")
                tries += 1
                continue
            else:
                return
            
def check_clean():
    file_path1 = Path("dataset/discussion-test.csv")
    file_path2 = Path("dataset/problemset-test.csv")
    if file_path1.is_file():
        file_path1.unlink()
    if file_path2.is_file():
        file_path2.unlink()


if __name__=="__main__":
    dump_fremium_problems()
    firefox_options = Options()
    # firefox_options.add_argument("--headless")
    
    driver = webdriver.Firefox(service=service, options=firefox_options)

    check_clean()
    csv_1 = open(path_prob, mode="a", newline="")
    csv_2 = open(path_disc, mode="a", newline="")

    writer_1 = csv.writer(csv_1)
    writer_2 = csv.writer(csv_2)

    writer_1.writerow(["Id", "Problem Name", "Description", "Difficulty", "Accepted", "Submissions", "Acceptance Rate"])
    writer_2.writerow(["Problem Name", "Id", "Parent_Id", "Text", "Date", "Up Votes", "Username"])

    testers = ["https://leetcode.com/problems/zigzag-conversion"]
    n = len(testers)

    for i in range(n):
        print(f"Problema cu idx {i}")
        problem = testers[i]
        do_consent()
        pb = testers[i]
        driver.get(pb)

        # PROBLEM_NAME
        problem_name = problem[problem.rfind('/')+1:]
        # DIFFICULTY, TOPICS
        dif, topics = get_difficulty(), get_topics()
        # ACCURACY, SUBMISSIONS, ACCEPTANCE_RATE
        acc, sub, acc_rate = acc_sub_accrate()
        # DESCRIPTION
        description = get_description()

        # Extra check for some eroneous premium problems that passed the driver-waiting time filter
        if description == None:
            continue
        writer_1.writerow([i, problem_name, description, dif, acc, sub, acc_rate])


        open_discussion()
        seek_for_responses(problem_name) # writer2 is called in-here
    driver.quit()