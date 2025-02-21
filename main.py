from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (TimeoutException, StaleElementReferenceException,
                                        NoSuchElementException, ElementClickInterceptedException,
                                        ElementNotInteractableException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from scrapper import *
import time
import csv
import cv2


# TODO: trebuie ca dupa ce verific asta sa si apas pe 'Show more replies' pana cand dispare
def has_responses(div) -> bool:
    global consent
    
    tries_responses = 0
    max_tries_responses = 3
    while tries_responses < max_tries_responses:
        try:
            tries_responses += 1
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
            return False
        except ElementClickInterceptedException:
            if not consent: # Consent - big white box
                try:
                    time.sleep(5)
                    # THE FIRST BUTTON
                    consent_button = WebDriverWait(div, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Consent']"))
                    )
                    print("Am gasit butonul de use data Consent!")
                    consent_button.click()
                    consent = True

                    span_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'close') and @aria-label='true']"))
                    )
                    print("A mers span-ul")
                    inp = input("STOP")
                    html_content = driver.page_source

                    # Open a .txt file in write mode and save the HTML content
                    with open("page_source.txt", "w", encoding="utf-8") as file:
                        file.write(html_content)
                except TimeoutException:
                    driver.save_screenshot("debug.png")
                    print("Butonul de consimțământ nu este disponibil.")
                    # consent = True
                    return False
            else: # Google cookie - small left-bottom corner pop-up
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # TODO: Aici as putea gestiona fereastra aia mica de cookies
                # print("Am intrat pe else")
                # screenshot = cv2.imread("screenshot.png")
                # button_template = cv2.imread("button.png", cv2.IMREAD_UNCHANGED)

                # # Convertește în alb-negru pentru o mai bună potrivire
                # button_gray = cv2.cvtColor(button_template, cv2.COLOR_BGR2GRAY)
                # screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

                # # Folosește template matching pentru a găsi poziția butonului
                # result = cv2.matchTemplate(screenshot_gray, button_gray, cv2.TM_CCOEFF_NORMED)
                # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                # button_x, button_y = max_loc
                # button_w, button_h = button_template.shape[1], button_template.shape[0]

                # button_center_x = button_x + button_w // 2
                # button_center_y = button_y + button_h // 2

                # window_position = driver.get_window_rect()
                # real_x = window_position["x"] + button_center_x
                # real_y = window_position["y"] + button_center_y

                # # Simulează un click pe coordonatele găsite
                # actions = ActionChains(driver)
                # actions.move_by_offset(real_x, real_y).click().perform()

                # # Revino cu mouse-ul la poziția inițială pentru a evita probleme
                # actions.move_by_offset(-real_x, -real_y).perform()
                
                # driver.save_screenshot("after-debug.png")

                # iframes = WebDriverWait(driver, 4).until(
                #     EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
                # )
                # print(f"Număr de iframe-uri găsite: {len(iframes)}")

                # for index, iframe in enumerate(iframes):
                #     print(f"Iframe {index + 1}: {iframe.get_attribute('name') or iframe.get_attribute('id')}")
                #     try:
                #         cookie_button = WebDriverWait(div, 2).until(
                #             EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Dismiss privacy and legal settings display']"))
                #         )
                #         print("Am găsit butonul de cookie!")
                #     except Exception as e:
                #         print(f"Nu am găsit butonul de cookie")
                #         # print(f"{e}")
                #         continue
                # inp = input("blabla")

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

                            try:
                                # print(parent_div.get_attribute('class'))
                                while True:
                                    try:
                                        show_more_button = parent_div.find_element(By.XPATH, ".//div[contains(text(), 'Show more replies')]")
                                        print("Dau click pe 'Show more replies'")
                                        
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
                                    except ElementNotInteractableException:
                                        print("Am terminat de dat click pe 'Show more replies'!")
                                        break

                            except TimeoutException:
                                continue

                            div_elements = WebDriverWait(parent_div, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@class, 'flex w-full px-3 pb-2 pt-4 transition-[background] duration-500')]"))
                            )
                            print(f"div_elements size -> {len(div_elements)}")
                            for el in div_elements:
                                comment_id += 1 
                                username = get_response_username(el) 
                                date = get_response_date_(el) 
                                upvotes = get_response_upvotes(el) 
                                text = get_response_text(el) 
                                print(f"{username} a raspuns")

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
        time.sleep(2)
        # inp = input("BLABLA=")


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

    testers = ["https://leetcode.com/problems/zigzag-conversion", "https://leetcode.com/problems/reverse-integer"]
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