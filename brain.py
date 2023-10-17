from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from dotenv import load_dotenv
from tools import cancel_popup,browser,wait,save_page,confirm_outcome,send_email
import os
load_dotenv()




class CheckPattern:
    def __init__(self,market) -> None:
        self.market=market
        self._VIRTUAL_BUTTON_PATH="/html/body/app-root/app-wrapper/div/app-landing/landing-header/div/app-header/div/header/header-bk-product-switcher/div/div[2]/header-bk-product-switcher-item/button/a"

    def checkout_virtual(self):       
        try:
            virtual_button=wait.until(EC.element_to_be_clickable((By.XPATH,self._VIRTUAL_BUTTON_PATH)))
            virtual_button.click()
        except ElementClickInterceptedException:
            cancel_popup()
            virtual_button=wait.until(EC.element_to_be_clickable((By.XPATH,self._VIRTUAL_BUTTON_PATH)))
            virtual_button.click()

        virtual_bundesliga_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".game-kings-bundliga.type-scheduled-league")))
        virtual_bundesliga_button.click()

    def check_result(self):
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
    
            
            


class LoginUser:
    def __init__(self,username,password) -> None:
        self.username=username
        self.password=password
    ###### LoginUser Variables##########################
        self._USERNAME_PATH="/html/body/app-root/app-wrapper/app-login-dialog/div/div/div[2]/div/div[1]/input"
        self._PASSWORD_PATH="/html/body/app-root/app-wrapper/app-login-dialog/div/div/div[2]/div/div[2]/input"
        self._LOGIN_LINK_SELECTOR="div.header-bk-guest.div.button"
        # self._LOGIN_LINK_PATH='/html/body/app-root/app-wrapper/div/app-landing/landing-header/div/app-header/div/header/div/div/header-bk-guest/div/button'
        self._LOGIN_BUTTON_PATH="/html/body/app-root/app-wrapper/app-login-dialog/div/div/div[2]/div/div[3]/app-button[2]/button"
        self._CANCEL_SIGNUP_BUTTON="/html/body/app-root/app-wrapper/div/app-registration/registration-split/div/app-breadcrumb/div/div/span"

        
    def login(self):
        login=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button.text")))
        try:
            login.click()
        except ElementClickInterceptedException:
            cancel_popup()
            login=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button.text")))
            login.click()

        username=browser.find_element(By.XPATH,self._USERNAME_PATH)
        password=browser.find_element(By.XPATH,self._PASSWORD_PATH)
        for char in self.username:
            time.sleep(0.5)
            username.send_keys(char)
        for char in self.password:
            time.sleep(0.5)
            password.send_keys(char)
        time.sleep(1)
        login_button=browser.find_element(By.XPATH,self._LOGIN_BUTTON_PATH)
        login_button.click()
        time.sleep(100)



