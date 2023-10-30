
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (ElementClickInterceptedException,ElementNotInteractableException,
                                        StaleElementReferenceException,TimeoutException,NoSuchElementException)
from dotenv import load_dotenv
from tools import (cancel_popup,browser, check_if_current_week_has_played, check_if_current_week_islive, 
                   check_if_last_result_equal_input, clear_bet_slip, reload_result_page,wait,save_page,confirm_outcome,send_email)
import os
from selenium.webdriver.common.action_chains import ActionChains 

load_dotenv()


class PlayGame:
    def __init__(self,market:str) -> None:
        """" To handle the Game Play like: choose_market, select_stake_option, place_the_bet"""
        self.market=market.lower()

    def choose_market(self):
        """ To select the market which was passed as a variable during initializing """
        try:
            if check_if_current_week_islive():
                time.sleep(40)
            more_markets_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="market-dropdown-more-markets"]')))
            more_markets_button.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
                browser.execute_script(f"window.scrollTo(0, 20);")
                if check_if_current_week_islive():
                    time.sleep(40)
                more_markets_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="market-dropdown-more-markets"]')))
                more_markets_button.click()    

        if self.market.lower()=="ht/ft":
            market_selector="[data-testid='ht/ft-area']"
        elif self.market=="3-3":
            market_selector='[data-testid="correct-score-area"]'
        time.sleep(1)
        try:
            if check_if_current_week_islive():
                time.sleep(40)
            market_to_select=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, market_selector )))
            market_to_select.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
            # more_markets_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="market-dropdown-more-markets"]')))
            # more_markets_button.click()
            if check_if_current_week_islive():
                time.sleep(40)
            market_to_select=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, market_selector )))
            market_to_select.click()

        time.sleep(1)
        try:
            close_more_markets_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid=market-dropdown-close-markets]')))
            close_more_markets_button.click()
        except:
            pass
        
    def select_stake_options(self,week:str,previous_week_selected:str)->str:
        """ To select the stake option from the selected market, you wish to stake funds on """
        available_games=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-content"]')
        week_to_select=browser.find_elements(By.CSS_SELECTOR,'.week')

        if (check_if_current_week_has_played(previous_week_selected=previous_week_selected) 
            and week=="after_current_week"):
            week="current_week"

        attempt1=11
        # attempt2=attempt1*2
        if week=="current_week":
            start=0                 # Where to start selecting the option from (current week to start play)
            end=9                   # Where to end selecting the option from (current week to start play)
            week_to_select_num=0    # The week where the options is to be selected (current week to start play)
            
        elif week=="after_current_week":
            start=9                 # Where to start selecting the option from (week after current week to start play)
            end=18                  # Where to end selecting the option from (week after current week to start play)
            week_to_select_num=1    # The week where the options is to be selected (week after current week to start play)

        # select the week you wish to pick options from, for easy scrolling
        week_to_select=week_to_select[week_to_select_num]
        week_to_select.click()
        week_to_select_text=week_to_select.text
        const=0
        for n in range(start,len(available_games[:end])):
            window_height=n-start                         # The current iteration level minus the starting week to be selected
            n-=const
            
            try:
                if check_if_current_week_islive():
                    time.sleep(40)
                    print("i went live at available_games_1")
                    if week=="after_current_week":
                        n-=9
                        const=9

                available_games=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-content"]')
                available_games_1=wait.until(EC.element_to_be_clickable(available_games[:end][n]))
                available_games_1.click()
                time.sleep(0.5)
            except (ElementClickInterceptedException, StaleElementReferenceException,TimeoutException):
                print("exception was thrown at available_games_1")
                browser.execute_script(f"window.scrollTo(0, {window_height*attempt1});") # To Scroll to where the element can be clicked()
                    
                time.sleep(0.5)
                available_games=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-content"]')
                available_games_1=wait.until(EC.element_to_be_clickable(available_games[:end][n]))
                available_games_1.click()

            if week=="after_current_week" and const!=9:
                n-=8

            # stake_options=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]
            try:
                if check_if_current_week_islive():
                    time.sleep(40)
                    print("i went live at stake_option_1")
                    if week=="after_current_week" and const!=9:
                        n-=1
                        const=9
                        # stake_options=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]
                stake_options=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]        #Temp
                one_slash_two_option=wait.until(EC.element_to_be_clickable(stake_options[2]))
                one_slash_two_option.click()
                time.sleep(0.5)

            except (ElementClickInterceptedException, StaleElementReferenceException,TimeoutException):
                print("exception was thrown at stake_option_1")
                
                browser.execute_script(f"window.scrollTo(0, {window_height*attempt1});") # To Scroll to where the element can be clicked()
    
                time.sleep(0.5)
                stake_options=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]
                one_slash_two_option=wait.until(EC.element_to_be_clickable(stake_options[2]))
                one_slash_two_option.click()
                time.sleep(0.5)

                
            try:
                if check_if_current_week_islive():
                    time.sleep(40)
                    print("i went live at stake_option_2")
                    if week=="after_current_week" and const!=9:
                        n-=1
                        const=9
                stake_options=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]
                two_slash_one_option=wait.until(EC.element_to_be_clickable(stake_options[6]))
                two_slash_one_option.click()
                time.sleep(0.5)
            except (ElementClickInterceptedException, StaleElementReferenceException,TimeoutException):
                print("exception was thrown at stake_option_2")
               
                browser.execute_script(f"window.scrollTo(0, {window_height*attempt1});") # To Scroll to where the element can be clicked()
                
                time.sleep(0.5)
                stake_options=browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]
                two_slash_one_option=wait.until(EC.element_to_be_clickable(stake_options[6]))
                two_slash_one_option.click()
                time.sleep(0.5)
                
        return week_to_select_text
            
        

    def place_the_bet(self,amount:int,test:bool):
        """ To bet the selected stake options each with the inputed amount"""
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

        if test:
            clear_bet_slip()
        else:
            # identify and click the place bet button
            place_bet_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[text="Place Bet"]')))
            place_bet_button.click()
            time.sleep(2)
            # identify and click the continue betting button
            continue_betting_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'button.btn.upper.btn-transparent')))
            continue_betting_button.click        




class CheckPattern:
    def __init__(self,market:str) -> None:
        """ To check if the the desired pattern of the desired market has occured """
        self.market=market
        self._VIRTUAL_BUTTON_LINK_TEXT="VIRTUAL"


    def checkout_virtual(self, league:str):
        """ To enter the desired Virtual Game option(e.g. Bundesliga)"""       
        try:
            virtual_button=wait.until(EC.element_to_be_clickable((By.LINK_TEXT,self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()
        except ElementClickInterceptedException:
            cancel_popup()
            virtual_button=wait.until(EC.element_to_be_clickable((By.LINK_TEXT,self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()
        if league.lower()=="bundliga":
            css_selector=".game-kings-bundliga.type-scheduled-league"
        virtual_choice_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,css_selector)))    
        virtual_choice_button.click()

    
    def check_result(self,length:str,latest_week:str)->bool:
        """ To check the result outcomes of an inputed length or number of weeks"""
        standings_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
        standings_button.click()
        result_button=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")))
        result_button.click()
        time.sleep(5)
        # check halftime fulltime result
        # 1 - 10 weeks matches
        if length.lower()=="all result":
            game_weeks=[week.text for week in browser.find_elements(By.CSS_SELECTOR,".week-number")]

            # checking if the last week played is Week 10 before going ahead to save the page
            game_weeks=check_if_last_result_equal_input(game_weeks=game_weeks,week_to_check="Week 10",
                                                        time_delay=30)
            
            print("Woow its Week 10, lets wait for Week 20")
            ht_scores=[ht_score.text for ht_score in browser.find_elements(By.CSS_SELECTOR,".score.ht")]
            ft_scores=[ft_score.text for ft_score in browser.find_elements(By.CSS_SELECTOR,".score.ft")]
                    
            save_page(page_name="saved_pages/one_to_ten_page.html")         # save the games(1-10) page

            # browser.quit()
            time.sleep(1620)                                                # To wait untill Week 19
            # time.sleep(270)
            
            # browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")

            reload_result_page()
            second_game_weeks=[week.text for week in browser.find_elements(By.CSS_SELECTOR,".week-number")] 
            # checking if the last week played is Week 20 before going ahead to save the page
            second_game_weeks=check_if_last_result_equal_input(game_weeks=second_game_weeks,
                                                               week_to_check="Week 20",time_delay=30)
            
            # Add the 11-20 weeks matches to the 1-10 weeks matches
            ht_scores.extend([ht_score.text for ht_score in browser.find_elements(By.CSS_SELECTOR,".score.ht")])
            ft_scores.extend([ft_score.text for ft_score in browser.find_elements(By.CSS_SELECTOR,".score.ft")])
            game_weeks.extend(second_game_weeks)

            save_page(page_name="saved_pages/eleven_to_twenty_page.html")    # save the games(11-20) page

        elif length.lower()=="last result":
            game_weeks=[week.text for week in browser.find_elements(By.CSS_SELECTOR,".week-number")]
            
            # checking if the last week played is latest_week before going ahead to save the page
            game_weeks=check_if_last_result_equal_input(game_weeks=game_weeks,week_to_check=latest_week,
                                                        time_delay=30)
            game_weeks=game_weeks[:1]

            # Re-fill the ht and ft_scores list by the reloaded/current score result of the last week played   
            ht_scores=[ht_score.text for ht_score in browser.find_elements(By.CSS_SELECTOR,".score.ht")]
            ft_scores=[ft_score.text for ft_score in browser.find_elements(By.CSS_SELECTOR,".score.ft")]
            ht_scores=ht_scores[:9]
            ft_scores=ft_scores[:9]

        result=confirm_outcome(ht_scores=ht_scores,ft_scores=ft_scores,game_weeks=game_weeks)
                                            
        if result["outcome"]!=True and length.lower()=="all result":
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
            save_page(page_name="saved_pages/one_to_ten_page.html")     # save the games(1-10) page

            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                       Password=os.environ.get("EMAIL_PASSWORD"),
                       Subject="halftime/fulltime",
                       Message=result["message"],
                       File_path=["saved_pages/one_to_ten_page.html"]
                       )    
        
            cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
            cancel_result_page_button.click()
            return True 
        
        elif result["outcome"]==True and length.lower()=="all result":
            cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
            cancel_result_page_button.click()
            return True

         


class LoginUser:
    def __init__(self,username:str,password:str) -> None:
        """ To login a user with the relevant credentials """
        self.username=username
        self.password=password
        
    def login(self):
        """ Login the user with the credentials from initialization"""
        login=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button.text")))
        try:
            login.click()
        except ElementClickInterceptedException:
            cancel_popup()
            login=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button.text")))
            login.click()

        username=browser.find_element(By.CSS_SELECTOR,'[placeholder="Username or Verified Mobile"]')
        password=browser.find_element(By.CSS_SELECTOR,'[placeholder="Password"]')
        # fill the username and password form with the inputed variable
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



