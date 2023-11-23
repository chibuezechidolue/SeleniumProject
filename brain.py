import time
import os
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException, TimeoutException,
                                        NoSuchElementException)
from dotenv import load_dotenv
from tools import (cancel_popup, check_if_current_week_has_played,
                   check_if_current_week_islive, check_if_last_result_equal_input,
                   clear_bet_slip, save_page, confirm_outcome, send_email, set_up_driver_instance)
from datetime import datetime
load_dotenv()


class PlayGame:
    """ To handle the Game Play like: choose_market, select_stake_option,
        place_the_bet. It takes a driver instance as first argument """

    def __init__(self, driver: object, market: str) -> None:
        self.market = market.lower()
        self.browser = driver
        self.wait = WebDriverWait(driver=self.browser, timeout=10)

    def choose_market(self):
        """ To select the market which was passed as a variable during initializing """
        try:
            if check_if_current_week_islive(self.browser):
                time.sleep(40)
            more_markets_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="market-dropdown-more-markets"]')))
            more_markets_button.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
            self.browser.execute_script("window.scrollTo(0, 20);")
            if check_if_current_week_islive(self.browser):
                time.sleep(40)
            more_markets_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="market-dropdown-more-markets"]')))
            more_markets_button.click()

        if self.market.lower() == "ht/ft":
            market_selector = "[data-testid='ht/ft-area']"
        elif self.market == "3-3":
            market_selector = '[data-testid="correct-score-area"]'
        time.sleep(0.5)
        try:
            if check_if_current_week_islive(self.browser):
                time.sleep(40)
            market_to_select = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, market_selector)))
            market_to_select.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
            if check_if_current_week_islive(self.browser):
                time.sleep(40)
            market_to_select = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, market_selector)))
            market_to_select.click()

        time.sleep(0.5)
        try:
            close_more_markets_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid=market-dropdown-close-markets]')))
            close_more_markets_button.click()
        except:
            pass
    
    def select_stake_options(self, week: str, previous_week_selected: str) -> str:
        """ To select the stake option from the selected market, you wish to stake funds on """
        available_games = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-content"]')
        week_to_select = self.browser.find_elements(By.CSS_SELECTOR, '.week')

        if (check_if_current_week_has_played(self.browser, previous_week_selected=previous_week_selected)
                and week == "after_current_week"):
            week = "current_week"

        attempt1 = 11
        # attempt2=attempt1*2
        if week == "current_week":
            start = 0  # Where to start selecting the option from (current week to start play)
            end = 9  # Where to end selecting the option from (current week to start play)
            week_to_select_num = 0  # The week where the options is to be selected (current week to start play)

        elif week == "after_current_week":
            start = 9  # Where to start selecting the option from (week after current week to start play)
            end = 18  # Where to end selecting the option from (week after current week to start play)
            week_to_select_num = 1  # The week where the options is to be selected (week after current week to start play)

        # select the week you wish to pick options from, for easy scrolling
        week_to_select = week_to_select[week_to_select_num]
        week_to_select.click()
        week_to_select_text = week_to_select.text
        const = 0
        for n in range(start, len(available_games[:end])):
            window_height = n - start  # The current iteration level minus the starting week to be selected
            n -= const

            try:
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at available_games_1")
                    if week == "after_current_week":
                        n -= 9
                        const = 9

                available_games = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-content"]')
                available_games_1 = self.wait.until(EC.element_to_be_clickable(available_games[:end][n]))
                available_games_1.click()
                print(f"no {n+1} of available games was clicked, time: {datetime.now().time()}")
                time.sleep(0.5)
            except (ElementClickInterceptedException, StaleElementReferenceException, TimeoutException):
                print("exception was thrown at available_games_1")
                self.browser.execute_script(
                    f"window.scrollTo(0, {window_height * attempt1});")  # To Scroll to where the element can be clicked()

                time.sleep(0.5)
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at available_games_1")
                    if week == "after_current_week":
                        n -= 9
                        const = 9
                        
                available_games = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-content"]')
                available_games_1 = self.wait.until(EC.element_to_be_clickable(available_games[:end][n]))
                available_games_1.click()
                print(f"at exception, no {n+1} of available games was clicked, time: {datetime.now().time()}")

            if week == "after_current_week" and const != 9:
                n -= 8

            # stake_options=self.browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]
            try:
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at stake_option_1")
                    if week == "after_current_week" and const != 9:
                        n -= 1
                        const = 9
                        # stake_options=self.browser.find_elements(By.CSS_SELECTOR,'[data-testid="match-odd-value"]')[n*9:end*9]
                if self.market=="ht/ft":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 9:end * 9]  # Temp
                    one_slash_two_option = self.wait.until(EC.element_to_be_clickable(stake_options[2]))
                    one_slash_two_option.click()
                elif self.market=="3-3":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 28:end * 28]  # Temp
                    print(f"This is len of stake_options: {len(stake_options)}, time: {datetime.now().time()}")
                    three_three_option = self.wait.until(EC.element_to_be_clickable(stake_options[15]))
                    three_three_option.click()
                time.sleep(0.5)

            # except (ElementClickInterceptedException, StaleElementReferenceException, TimeoutException, IndexError):
            except (ElementClickInterceptedException, TimeoutException):
                print(f"exception was thrown at stake_option_1, time: {datetime.now().time()}")
                self.browser.execute_script(
                    f"window.scrollTo(0, {window_height * attempt1});")  # To Scroll to where the element can be clicked()

                time.sleep(0.5)
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at stake_option_1")
                    if week == "after_current_week" and const != 9:
                        n -= 1
                        const = 9
                if self.market=="ht/ft":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 9:end * 9]  # Temp
                    one_slash_two_option = self.wait.until(EC.element_to_be_clickable(stake_options[2]))
                    one_slash_two_option.click()
                elif self.market=="3-3":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 28:end * 28]  # Temp
                    print(f"This is len of stake_options: {len(stake_options)}, time: {datetime.now().time()}")
                    three_three_option = self.wait.until(EC.element_to_be_clickable(stake_options[15]))
                    three_three_option.click()
                time.sleep(0.5)

            except (IndexError,StaleElementReferenceException):
                self.browser.refresh()
                self.choose_market()
                print(f"the page was reloaded, i had to reselect available_games, time: {datetime.now().time()}")
                for i in range(n+1):
                    available_games = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-content"]')
                    available_games_1 = self.wait.until(EC.element_to_be_clickable(available_games[:end][i]))
                    available_games_1.click()
                    time.sleep(0.5)
                print(f"an index error exception was thrown at stake_option_1, time: {datetime.now().time()}")

                self.browser.execute_script(
                    f"window.scrollTo(0, {window_height * attempt1});")  # To Scroll to where the element can be clicked()

                time.sleep(0.5)
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at stake_option_1")
                    if week == "after_current_week" and const != 9:
                        n -= 1
                        const = 9
                if self.market=="ht/ft":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 9:end * 9]  # Temp
                    one_slash_two_option = self.wait.until(EC.element_to_be_clickable(stake_options[2]))
                    one_slash_two_option.click()
                elif self.market=="3-3":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 28:end * 28]  # Temp
                    print(f"This is len of stake_options: {len(stake_options)}, time: {datetime.now().time()}")
                    three_three_option = self.wait.until(EC.element_to_be_clickable(stake_options[15]))
                    three_three_option.click()
                time.sleep(0.5)


            try:
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at stake_option_2")
                    if week == "after_current_week" and const != 9:
                        n -= 1
                        const = 9
                if self.market=="ht/ft":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 9:end * 9]
                    two_slash_one_option = self.wait.until(EC.element_to_be_clickable(stake_options[6]))
                    two_slash_one_option.click()
                elif self.market=="3-3":
                    pass
                time.sleep(0.5)
            except (ElementClickInterceptedException, TimeoutException):
                print("exception was thrown at stake_option_2")
                self.browser.execute_script(
                    f"window.scrollTo(0, {window_height * attempt1});")  # To Scroll to where the element can be clicked()

                time.sleep(0.5)
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at stake_option_2")
                    if week == "after_current_week" and const != 9:
                        n -= 1
                        const = 9
                if self.market=="ht/ft":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 9:end * 9]
                    two_slash_one_option = self.wait.until(EC.element_to_be_clickable(stake_options[6]))
                    two_slash_one_option.click()
                elif self.market=="3-3":
                    pass
                time.sleep(0.5)
            except (IndexError,StaleElementReferenceException):
                self.browser.refresh()
                self.choose_market()
                print(f"the page was reloaded, i had to reselect available_games, time: {datetime.now().time()}")
                for i in range(n+1):
                    available_games = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-content"]')
                    available_games_1 = self.wait.until(EC.element_to_be_clickable(available_games[:end][i]))
                    available_games_1.click()
                    time.sleep(0.5)
                
                print(f"exception was thrown at stake_option_2, time: {datetime.now().time()}")
                self.browser.execute_script(
                    f"window.scrollTo(0, {window_height * attempt1});")  # To Scroll to where the element can be clicked()

                time.sleep(0.5)
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                    print("i went live at stake_option_2")
                    if week == "after_current_week" and const != 9:
                        n -= 1
                        const = 9
                if self.market=="ht/ft":
                    stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[n * 9:end * 9]
                    two_slash_one_option = self.wait.until(EC.element_to_be_clickable(stake_options[6]))
                    two_slash_one_option.click()
                elif self.market=="3-3":
                    pass
                time.sleep(0.5)
        return week_to_select_text

    def place_the_bet(self, amount: int, test: bool)->str:
        """ To bet the selected stake options each with the inputed amount"""
        # identify and click the betslip botton
        time.sleep(1)
        betslip_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="nav-bar-betslip"]')))
        betslip_button.click()
        time.sleep(1)
        # identify and click the singles tab option
        singles_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="groupings-tab-singles"]')))
        singles_button.click()
        # identify, clear existing amount and input new amount
        stake_input_box = self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-groupings-group-stake"]')
        stake_input_box.clear()
        time.sleep(1)
        stake_input_box.send_keys(amount)
        # scroll to the bottom of the page
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        if test:
            clear_bet_slip(self.browser)
        else:
            # identify and click the place bet button
            place_bet_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[text="Place Bet"]')))
            place_bet_button.click()
            time.sleep(2)
            # identify and click the continue betting button
            try:
                continue_betting_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.bet-success-dialog-buttons .btn-text')))
                continue_betting_button.click()
            except (TimeoutException, NoSuchElementException):
                close_betslip_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')))
                close_betslip_button.click()
        try:
            acc_balance=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
            return acc_balance
        except (NoSuchElementException,TimeoutException):
            pass


class CheckPattern:
    """ To check if the the desired pattern of the desired market has occured. 
    It takes a driver instance as first argument """

    def __init__(self, driver: object, market: str) -> None:
        self.market = market
        self._VIRTUAL_BUTTON_LINK_TEXT = "VIRTUAL"
        self.browser = driver
        self.wait = WebDriverWait(driver=self.browser, timeout=10)

    def checkout_virtual(self, league: str):
        """ To enter the desired Virtual Game option(e.g. Bundesliga)"""
        try:
            virtual_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()
        except ElementClickInterceptedException:
            cancel_popup(self.browser)
            virtual_button = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, self._VIRTUAL_BUTTON_LINK_TEXT)))
            virtual_button.click()
        if league.lower() == "bundliga":
            css_selector = ".game-kings-bundliga.type-scheduled-league"
        virtual_choice_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        virtual_choice_button.click()

    def check_result(self, length: str, latest_week: str,acc_balance:str=None,to_play:int=None) -> dict:
        """ To check the result outcomes of an inputed length or number of weeks"""
        standings_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="results-and-standings-button"]')))
        # standings_button=self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
        standings_button.click()
        result_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                    "/html/body/app-root/app-wrapper/div/virtuals"
                                                                    "-league-wrapper/mobile-virtuals-soccer/mvs"
                                                                    "-virtual-league-page/div["
                                                                    "2]/mvs-results-page/div[2]/div[2]")))
        result_button.click()
        time.sleep(7)
        # check halftime fulltime result
        # 1 - 10 weeks matches
        if length.lower() == "all result":
            game_weeks = [week.text for week in self.browser.find_elements(By.CSS_SELECTOR, ".week-number")]
            current_game_week=int(game_weeks[0].split(" ")[-1])  # To get the integer num of weeks
            # To check if last result is 9th - 10th week or sleep till it is
            if current_game_week<to_play-2:
                time_to_sleep=(to_play-2-current_game_week)*3
                print(f"i will be sleeping for: {time_to_sleep*60}")
                self.browser.quit()
                time.sleep(time_to_sleep*60)
                # self.browser=webdriver.Chrome()        # driver instance with User Interface (not headless)
                self.browser = set_up_driver_instance()  # driver instance without User Interface (--headless)
                time.sleep(1)
                self.browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")
                time.sleep(2)

            game_weeks = [week.text for week in self.browser.find_elements(By.CSS_SELECTOR, ".week-number")]
            game_weeks = check_if_last_result_equal_input(self.browser, game_weeks=game_weeks, week_to_check=f"Week 34",
                                                        time_delay=30)
            result={"outcome":True,"driver":self.browser}
            cancel_result_page_button = self.browser.find_element(By.CSS_SELECTOR, "svg path")
            cancel_result_page_button.click()
            return result

        elif length.lower() == "last result":
            try:
                game_weeks = [week.text for week in self.browser.find_elements(By.CSS_SELECTOR, ".week-number")]
                # checking if the last week played is latest_week before going ahead to save the page
                game_weeks = check_if_last_result_equal_input(self.browser, game_weeks=game_weeks,
                                                            week_to_check=latest_week,time_delay=30)
                game_weeks = game_weeks[:1]

                # Re-fill the ht and ft_scores list by the reloaded/current score result of the last week played   
                ht_scores = [ht_score.text for ht_score in self.browser.find_elements(By.CSS_SELECTOR, ".score.ht")]
                ft_scores = [ft_score.text for ft_score in self.browser.find_elements(By.CSS_SELECTOR, ".score.ft")]
                ht_scores = ht_scores[:9]
                ft_scores = ft_scores[:9]

                result = confirm_outcome(ht_scores=ht_scores, ft_scores=ft_scores, game_weeks=game_weeks,market=self.market)
            except:
                print("an error occured when checking last result i used acc balance to check")
                # if the result page fails, compare balances to tell the outcome
                time.sleep(110)  # TODO: Confirm the time to sleep before the balance reflects

                refresh_bal_button=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .refresh-icon')
                refresh_bal_button.click()
                time.sleep(2)
                acc_balance_2=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
                if float(acc_balance_2.replace(",","_"))>float(acc_balance.replace(',','_')):
                    result={"outcome":True,"message":"I used the acc bal to confirm ticket won"}
                else:
                    result={"outcome":False}

            if result["outcome"] == True and length.lower() == "last result":
                try:
                    page_path = "saved_pages/one_to_ten_page.html"
                    save_page(self.browser, page_name=page_path)
                except FileNotFoundError:
                    page_path = "SeleniumProject/saved_pages/one_to_ten_page.html"
                    save_page(self.browser, page_name=page_path)  # save the games(1-10) page
                send_email(Email=os.environ.get("EMAIL_USERNAME"),
                        Password=os.environ.get("EMAIL_PASSWORD"),
                        Subject=f"{self.market} came in the last result" ,
                        Message=result["message"],
                        File_path=[page_path]
                        )

                cancel_result_page_button = self.browser.find_element(By.CSS_SELECTOR, "svg path")
                cancel_result_page_button.click()
                return {"outcome": True, "driver": self.browser}

            else:
                cancel_result_page_button = self.browser.find_element(By.CSS_SELECTOR, "svg path")
                cancel_result_page_button.click()
                return {"outcome": False, "driver": self.browser}


class LoginUser:
    """ To login a user with the relevant credentials.
      It takes a driver instance as first argument """

    def __init__(self, driver: object, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.browser = driver
        self.wait = WebDriverWait(driver=self.browser, timeout=10)

    def login(self):
        """ Login the user with the credentials from initialization"""
        login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text")))
        try:
            login.click()
        except ElementClickInterceptedException:
            cancel_popup(self.browser)
            login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text")))
            login.click()

        username = self.browser.find_element(By.CSS_SELECTOR, '[placeholder="Username or Verified Mobile"]')
        password = self.browser.find_element(By.CSS_SELECTOR, '[placeholder="Password"]')
        # fill the username and password form with the inputed variable
        for char in self.username:
            time.sleep(0.5)
            username.send_keys(char)
        for char in self.password:
            time.sleep(0.5)
            password.send_keys(char)
        time.sleep(1)
        login_button = self.browser.find_element(By.CSS_SELECTOR, '[text="Login"]')
        login_button.click()
        time.sleep(1)
        try:
            cancel_notification_option_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button-cancel")))
            cancel_notification_option_button.click()
        except (TimeoutException, NoSuchElementException):
            pass