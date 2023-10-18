from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
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

    def check_result(self):
        standings_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
        standings_button.click()
        result_button=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")))
        # [data-testid="results-page-tab-standings"]
        result_button.click()
        # check halftime fulltime result
        time.sleep(5)
        # 1 - 10 weeks matches
        ht_scores=browser.find_elements(By.CSS_SELECTOR,".score.ht")
        ft_scores=browser.find_elements(By.CSS_SELECTOR,".score.ft")
        game_weeks=browser.find_elements(By.CSS_SELECTOR,".week-number")
        # save the games(1-10) page
        save_page(page_name="saved_pages/one_to_ten_page.html")

        # time.sleep(1800)

        # # 11-20 weeks matches
        # ht_scores.extend(browser.find_elements(By.CSS_SELECTOR,".score.ht"))
        # ft_scores.extend(browser.find_elements(By.CSS_SELECTOR,".score.ft"))
        # game_weeks.extend(browser.find_elements(By.CSS_SELECTOR,".week-number"))
        # # save the games(11-20) page
        # save_page(page_name="saved_pages/eleven_to_twenty_page.html")

            
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
        login_button=browser.find_element(By.CSS_SELECTOR,'[type="button"]')
        login_button.click()
        time.sleep(100)



