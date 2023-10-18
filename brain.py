from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (ElementClickInterceptedException,ElementNotInteractableException,
                                        StaleElementReferenceException,TimeoutException)
from dotenv import load_dotenv
from tools import cancel_popup,browser,wait,save_page,confirm_outcome,send_email
import os
load_dotenv()




class PlayGame:
    def __init__(self,market) -> None:
        self.market=market.lower()

    def choose_market(self):
        more_markets_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".area-dropdown")))
        more_markets_button.click()

        if self.market=="ht/ft":
            market_selector="[data-testid='ht/ft-area']"
        elif self.market=="3-3":
            market_selector=""
        print(market_selector)
        market_to_select=browser.find_element(By.CSS_SELECTOR, market_selector )
        market_to_select.click()

        
    def select_stake_options(self):
        available_games=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-content"]')
        attempt1=11
        attempt2=17
        for n in range(len(available_games[:9])):
            time.sleep(2)
            try:
                available_games[:9][n].click()
            except StaleElementReferenceException or ElementClickInterceptedException:
                browser.execute_script(f"window.scrollTo(0, {n*attempt1});")
                try:
                    available_games[:9][n].click()
                except StaleElementReferenceException or ElementClickInterceptedException:
                    browser.execute_script(f"window.scrollTo(0, {n*13});")
                    available_games[:9][n].click()

            stake_options=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:9*9]

            try:
                stake_options[2].click()
                time.sleep(0.5)   
            except ElementClickInterceptedException or StaleElementReferenceException:
                browser.execute_script(f"window.scrollTo(0, {n*attempt1});")
                try:
                    stake_options[2].click()
                    time.sleep(0.5)
                except ElementClickInterceptedException or StaleElementReferenceException:
                    browser.execute_script(f"window.scrollTo(0, {n*attempt2});")
                    stake_options[2].click()

                

            try:
                stake_options[6].click()
            except ElementClickInterceptedException or StaleElementReferenceException:
                browser.execute_script(f"window.scrollTo(0, {n*attempt1});")
                try:
                    stake_options[6].click()
                    time.sleep(0.5)
                except ElementClickInterceptedException or StaleElementReferenceException:
                    browser.execute_script(f"window.scrollTo(0, {n*attempt2});")
                    stake_options[6].click()

        

    def place_the_bet(self,amount):
        # identify and click the betslip botton
        time.sleep(1)
        betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')))
        betslip_button.click()
        time.sleep(1)
        # identify and click the singles tab option
        singles_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="groupings-tab-singles"]')))
        singles_button.click()
        # identify, clear existing amount and input new amount
        stake_input_box=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-groupings-group-stake"]')
        stake_input_box.clear()
        time.sleep(1)
        stake_input_box.send_keys(amount)
        # scroll to the bottom of the page
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # identify and click the place bet button

        # place_bet_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[text="Place Bet"]')))
        # place_bet_button.click()
        # time.sleep(2)
        # identify and click the continue betting button

        # continue_betting_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'button.btn.upper.btn-transparent')))
        # continue_betting_button.click        



class CheckPattern:
    def __init__(self,market) -> None:
        self.market=market
        self._VIRTUAL_BUTTON_LINK_TEXT="VIRTUAL"


    def checkout_virtual(self):       
        try:
            virtual_button=wait.until(EC.element_to_be_clickable((By.LINK_TEXT,self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()
        except ElementClickInterceptedException:
            cancel_popup()
            virtual_button=wait.until(EC.element_to_be_clickable((By.LINK_TEXT,self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()

        virtual_bundesliga_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".game-kings-bundliga.type-scheduled-league")))
        virtual_bundesliga_button.click()

    def check_result(self,length):
        
        standings_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
        standings_button.click()
        result_button=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")))
        result_button.click()
        # check halftime fulltime result
        time.sleep(5)
        # 1 - 10 weeks matches
        ht_scores=browser.find_elements(By.CSS_SELECTOR,".score.ht")
        ft_scores=browser.find_elements(By.CSS_SELECTOR,".score.ft")
        game_weeks=browser.find_elements(By.CSS_SELECTOR,".week-number")
        # save the games(1-10) page
        save_page(page_name="saved_pages/one_to_ten_page.html")

        # if length.lower()=="all result":
        #     time.sleep(1800)
        #     # 11-20 weeks matches
        #     ht_scores.extend(browser.find_elements(By.CSS_SELECTOR,".score.ht"))
        #     ft_scores.extend(browser.find_elements(By.CSS_SELECTOR,".score.ft"))
        #     game_weeks.extend(browser.find_elements(By.CSS_SELECTOR,".week-number"))
        #     # save the games(11-20) page
        #     save_page(page_name="saved_pages/eleven_to_twenty_page.html")

        if length.lower()=="last result":
            ht_scores=ht_scores[:9]
            ft_scores=ft_scores[:9]
            game_weeks=game_weeks[:1]
            
        result=confirm_outcome(ht_scores=ht_scores,ft_scores=ft_scores,game_weeks=game_weeks)
        if result["outcome"]!=True:
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                       Password=os.environ.get("EMAIL_PASSWORD"),
                       Subject="No halftime/fulltime yet",
                       Message=result["message"],
                       File_path=["saved_pages/one_to_ten_page.html","saved_pages/eleven_to_twenty_page.html"]
                       )        
            cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
            cancel_result_page_button.click()
            return False
        
        elif result["outcome"]==True and length.lower()=="last result":
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                       Password=os.environ.get("EMAIL_PASSWORD"),
                       Subject="No halftime/fulltime yet",
                       Message=result["message"],
                       File_path=["saved_pages/one_to_ten_page.html"]
                       )    
        
        cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
        cancel_result_page_button.click()
        return True
        
            
            


class LoginUser:
    def __init__(self,username,password) -> None:
        self.username=username
        self.password=password
        
    def login(self):
        login=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button.text")))
        try:
            login.click()
        except ElementClickInterceptedException:
            cancel_popup()
            login=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button.text")))
            login.click()

        username=browser.find_element(By.CSS_SELECTOR,'[placeholder="Username or Verified Mobile"]')
        password=browser.find_element(By.CSS_SELECTOR,'[placeholder="Password"]')
        for char in self.username:
            time.sleep(0.5)
            username.send_keys(char)
        for char in self.password:
            time.sleep(0.5)
            password.send_keys(char)
        time.sleep(1)
        login_button=browser.find_element(By.CSS_SELECTOR,'[text="Login"]')
        login_button.click()
        time.sleep(2)
        try:
            cancel_notification_option_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button.kumulos-action-button-cancel")))
            cancel_notification_option_button.click()
        except TimeoutException:
            pass



