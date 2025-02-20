from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (TimeoutException, StaleElementReferenceException,
                                        NoSuchElementException, ElementClickInterceptedException)
from selenium import webdriver
from scrapper import *
from pathlib import Path
from typing import Union
import time
import csv


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
        try:
            # Here we click the 'Show X Replies' button
            reply = WebDriverWait(div, 3).until(
                EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class, 'flex items-center gap-1 group shrink-0 cursor-pointer transition-colors')]"))
            )
            # reply = WebDriverWait(div, 5).until(
            #     EC.element_to_be_clickable((By.XPATH, ".//svg[@xmlns='http://www.w3.org/2000/svg']"))
            # )
            reply.click()
            time.sleep(0.4)
            return True
        except (NoSuchElementException, TimeoutException):
            print("NSEE / TLE")
            return False
        except ElementClickInterceptedException:

            if not consent: # Consent - big white box
                try:
                    consent_button = WebDriverWait(div, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Consent']"))
                    )
                    print("Am gasit butonul de use data Consent!")
                    consent_button.click()
                    consent = True
                except TimeoutException:
                    print("Butonul de consimțământ nu este disponibil.")
                    # consent = True
                    return False
            # else: # Google cookie - small left-bottom corner pop-up
            #     try:
            #         cookie_button = WebDriverWait(div, 2).until(
            #             EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss privacy and legal settings display']"))
            #         )
            #         # print("Am gasit butonul de google cookie!")
            #         cookie_button.click()
            #     except TimeoutException:
            #         print("Butonul de cookie nu este disponibil.")
            #         return True


def seek_for_root_comments(problem):
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

                        # Check for a root comment too long that needs to be expanded for displaying(for JS html loading)
                        expand_read_more(sixth_parent_div)
                        # print(f"    HAS 'READ MORE' BUTTON")

                        # DATE & UPVOTES
                        date, upvotes = get_date_(sixth_parent_div), get_upvotes(second_child_div)
                        # PROBLEM NAME
                        problem_name_ = problem[problem.rfind('/') + 1:]

                        comment_id += 1
                        writer_2.writerow([problem_name_, comment_id, 0, comment_text, date, upvotes, root_user.text])

                        # Check for responses
                        if has_responses(sixth_parent_div):
                            parent_id = comment_id
                            print(f"Comentariul {comment_id} are răspunsuri.")

                            parent_div = sixth_parent_div.find_element(By.XPATH, "..") 
                            responses_block = parent_div.find_element(By.XPATH, ".//div[2]") 

                            # TODO: sa apas pana cand nu mai exista butonul de show more
                            try:
                                div_elements = WebDriverWait(parent_div, 10).until(
                                    EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@class, 'flex w-full px-3 pb-2 pt-4 transition-[background] duration-500')]"))
                                )
                                print(f"div_elements size -> {len(div_elements)}")
                                print(parent_div.get_attribute('class'))
                                while True:
                                    try:
                                        show_more_button = parent_div.find_element(By.XPATH, ".//div[contains(text(), 'Show more replies')]")
                                        print(show_more_button.get_attribute('class'))
                                        
                                        driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                                        time.sleep(1)
                                        show_more_button.click()
                                    
                                    except NoSuchElementException:
                                        print("NU avem buton de 'Show more replies'")
                                        break
                                    except ElementClickInterceptedException:
                                        print("elemenul nu poate fi accesat, trebuie sa dam mai mult scroll")
                                        driver.execute_script("window.scrollBy(0, 500)")
                                        time.sleep(1)

                            except TimeoutException:
                                continue

                            for el in div_elements:
                                comment_id += 1 
                                username = get_response_username(el) 
                                date = get_response_date_(el) 
                                upvotes = get_response_upvotes(el) 
                                text = get_response_text(el) 
                                print(f"{username} a raspuns")

                                writer_2.writerow([problem_name_, comment_id, parent_id, text, date, upvotes, username])
                        else:
                            print(f"Comentariul {comment_id} nu are răspunsuri.")
                        inp = input("blabla=")
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
        time.sleep(2)
        # inp = input("BLABLA=")

def check_clean():
    file_path1 = Path("datasets/discussion-test.csv")
    file_path2 = Path("datasets/problemset-test.csv")
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
        do_consent(driver)
        pb = testers[i]
        driver.get(pb)

        # PROBLEM_NAME
        problem_name = problem[problem.rfind('/')+1:]
        # DIFFICULTY, TOPICS
        dif, topics = get_difficulty(driver), get_topics(driver)
        # ACCURACY, SUBMISSIONS, ACCEPTANCE_RATE
        acc, sub, acc_rate = acc_sub_accrate(driver)
        # DESCRIPTION
        description = get_description(driver)

        # Extra check for some eroneous premium problems that passed the driver-waiting time filter
        if description == None:
            continue
        writer_1.writerow([i, problem_name, description, dif, acc, sub, acc_rate])


        open_discussion(driver)
        seek_for_root_comments(problem_name) # writer2 is called in-here
    driver.quit()