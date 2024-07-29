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
from tools import (MyCustomThread, calc_stake_amount, cancel_popup, check_if_current_week_has_played,
                   check_if_current_week_islive, check_if_last_result_equal_input,terminate_driver_process,
                   clear_bet_slip, delete_cache, save_page, confirm_outcome, send_email, set_up_driver_instance,check_if_last_stake_has_played)
import datetime

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
        self.browser.execute_script(f"window.scrollTo(0, 0);")
        try:
            # if check_if_current_week_islive(self.browser):
            #     time.sleep(40)
            more_markets_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="market-dropdown-more-markets"]')))
            more_markets_button.click()
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
            print('an exception occured')
            try:
                close_more_markets_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid=market-dropdown-close-markets]')))
                close_more_markets_button.click()
            except:
                more_markets_button=self.browser.find_element(By.CSS_SELECTOR,'[data-testid="market-dropdown-more-markets"]')
                self.browser.execute_script(f"window.scrollTo(0, {more_markets_button.location['y']-200});")
                time.sleep(0.5)
                if check_if_current_week_islive(self.browser):
                    time.sleep(40)
                # more_markets_button = self.wait.until(
                #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="market-dropdown-more-markets"]')))
                more_markets_button.click()

        if self.market.lower() == "ht/ft":
            market_selector = "[data-testid='ht/ft-area']"
        elif self.market == "correct_score":
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
            market_to_select=self.browser.find_element(By.CSS_SELECTOR, market_selector)
            self.browser.execute_script(f"window.scrollTo(0, {market_to_select.location['y']-200});")
            time.sleep(0.5)
            # market_to_select = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, market_selector)))
            market_to_select.click()

        time.sleep(0.5)
        try:
            close_more_markets_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid=market-dropdown-close-markets]')))
            close_more_markets_button.click()
        except ElementClickInterceptedException:
            try:
                self.browser.execute_script(f"window.scrollTo(0, 0);")
                time.sleep(1)
                # self.browser.execute_script(f"window.scrollTo(0, {close_more_markets_button.location['y']-200});")
                close_more_markets_button.click()
            except:
                pass

    
    def stake_games(self,position,available_games,pattern_stake,stake_amount,n):
        end=9
        try:
            # available_games_1=available_games[n]
            available_games[n].click()
        except (ElementClickInterceptedException, StaleElementReferenceException, TimeoutException):
            # print("exception was thrown at available_games_1")
            self.browser.execute_script(
                f"window.scrollTo(0, {available_games[n].location['y']-200});")  # To Scroll to where the element can be clicked()
            time.sleep(0.5)
            # available_games_1=available_games[n]
            available_games[n].click()

        if n==0:
            current_open_stake_options=0
        else:
            current_open_stake_options=1
        
        if pattern_stake==[2,6]:
            stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[current_open_stake_options * 9:end * 9]  # Temp
        else:
            stake_options = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-odd-value"]')[current_open_stake_options * 28:end * 28]  # Temp
            # one_slash_two_option = self.wait.until(EC.element_to_be_clickable(stake_options[2]))
        
        
        try:
            # option_btn=option_btns[i]
            stake_options[pattern_stake[position]].click()
            # time.sleep(0.5)
        except (ElementClickInterceptedException, TimeoutException):
            # print("exception was thrown at stake_option_1")
            self.browser.execute_script(
                f"window.scrollTo(0, {stake_options[pattern_stake[position]].location['y']-200});")  # To Scroll to where the element can be clicked()
            time.sleep(0.5)
            stake_options[pattern_stake[position]].click()
        if len(pattern_stake)==1:
            amount=calc_stake_amount(amount=stake_amount,odd=float(stake_options[pattern_stake[position]].text.replace(" ",'')),base=25)
        else:
            amount=calc_stake_amount(amount=stake_amount,odd=float(stake_options[pattern_stake[position]].text.replace(" ",'')))
        acc_bal=self.place_the_bet(amount=amount,test=eval(os.environ.get("TEST")))
        # renew Stale Elements
        if not check_if_current_week_islive(self.browser):
            available_games[:] = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-content"]')[:end]
        
        return [available_games,acc_bal]




    def select_stake_options(self,position, week: str, previous_week_selected: str,pattern_stake:list,stake_amount:float) -> str:
        """ To select the stake option from the selected market, you wish to stake funds on """
        print(f"select_stake_option Start: {datetime.datetime.now().time()}")
        week_to_select = self.browser.find_elements(By.CSS_SELECTOR, '.week')
        if week == "current_week":
            start = 0  # Where to start selecting the option from (current week to start play)
            end = 9  # Where to end selecting the option from (current week to start play)
            week_to_select_num = 0  # The week where the options is to be selected (current week to start play)

        elif week == "after_current_week":
            start = 9  # Where to start selecting the option from (week after current week to start play)
            end = 18  # Where to end selecting the option from (week after current week to start play)
            week_to_select_num = 1  # The week where the options is to be selected (week after current week to start play)

        # select the week you wish to pick options from, for easy scrolling
        # week_to_select = week_to_select[week_to_select_num]
        week_to_select[week_to_select_num].click()
        week_to_select_text = week_to_select[week_to_select_num].text
        try:
            available_games = self.browser.find_elements(By.CSS_SELECTOR, '[data-testid="match-content"]')[:end]
            for n in range(start, len(available_games)):
                stake_game=MyCustomThread(target=self.stake_games,args=(position,available_games,pattern_stake,stake_amount,n),daemon=True)
                stake_game.start()
                output=stake_game.join()
                if stake_game.error:
                    raise stake_game.error
                available_games[:]=output[0]
                acc_bal=output[1] 
            # print(f"select_stake_option End: {datetime.datetime.now().time()}")
            return [week_to_select_text,acc_bal]
        except Exception as error:
                # To clear all stake options selected if an error occurs while selecting stake options
                print(f"An error occured during select_stake_options. This is the error: {error}")
                betslip_button=self.browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
                betslip_button.click()
                time.sleep(1)
                refresh_bal_button=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .refresh-icon')
                try:
                    refresh_bal_button.click()
                except ElementClickInterceptedException:
                    self.browser.execute_script(
                    f"window.scrollTo(0, {refresh_bal_button.location['y']-200});")  # To Scroll to where the element can be clicked()
                    time.sleep(0.5)
                    refresh_bal_button.click()
                time.sleep(2)
                acc_bal=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
                clear_bet_slip(self.browser)
                send_email(Email=os.environ.get("EMAIL_USERNAME"),
                        Password=os.environ.get("EMAIL_PASSWORD"),
                        Subject="(FullSeason) ERROR during select_stake_options",
                        Message=f"An error occured during select_stake_options. This is the error: {error}"
                        )
                return [week_to_select_text,acc_bal]

    def place_the_bet(self, amount: int, test: bool)->str:
        """ To bet the selected stake options each with the inputed amount"""
        # identify and click the betslip botton
        time.sleep(1)
        # betslip_button = self.wait.until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="nav-bar-betslip"]')))
        betslip_button=self.browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
        betslip_button.click()
        # time.sleep(3)
        # identify and click the singles tab option
        try:

            # singles_button=self.browser.find_element(By.CSS_SELECTOR,'[data-testid="groupings-tab-singles"]')
            # singles_button.click()
            # identify, clear existing amount and input new amount
            # stake_input_box = self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-groupings-group-stake"]')
            stake_input_box = self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-totals-stake-amount-value"]')
            stake_input_box.clear()
            # time.sleep(1)
            stake_input_box.send_keys(amount)
            # scroll to the bottom of the page
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)

            if test:
                clear_bet_slip(self.browser)
            else:
                # identify and click the place bet button
                # place_bet_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[text="Place Bet"]')))
                place_bet_button=self.browser.find_element(By.CSS_SELECTOR, '[text="Place Bet"]')
                place_bet_button.click()
                # time.sleep(2)
                # identify and click the continue betting button
                try:
                    # continue_betting_button = self.wait.until(
                    #     EC.element_to_be_clickable((By.CSS_SELECTOR, '.bet-success-dialog-buttons .btn-text')))
                    continue_betting_button=self.browser.find_element(By.CSS_SELECTOR, '.bet-success-dialog-buttons .btn-text')
                    continue_betting_button.click()
                except (TimeoutException, NoSuchElementException):
                    # close_betslip_button = self.wait.until(
                    #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')))
                    close_betslip_button=self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')
                    close_betslip_button.click()
            try:
                acc_balance=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
                return acc_balance
            except (NoSuchElementException, TimeoutException):
                pass
        except:
            # close_betslip_button = self.wait.until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')))
            close_betslip_button=self.browser.find_element(By.CSS_SELECTOR, '[data-testid="coupon-close-icon"]')
            close_betslip_button.click()
            close_betslip_button.click()

class CheckPattern:
    """ To check if the the desired pattern of the desired market has occured. 
    It takes a driver instance as first argument """

    def __init__(self, driver: object,) -> None:
        self._VIRTUAL_BUTTON_LINK_TEXT = "VIRTUALS"
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

    def check_result(self, length: str, latest_week: str,acc_balance:str=None,to_play:int=None,market:str=None) -> dict:
        """ To check the result outcomes of an inputed length or number of weeks"""
        # check halftime fulltime result
        # 1 - 20 weeks matches
        if length.lower() == "all result":
            try:
                try:
                    try:
                        standings_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="results-and-standings-button"]')))
                        # standings_button=self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
                        standings_button.click()
                    except (TimeoutException,ElementClickInterceptedException):
                        standings_button=self.browser.find_element(By.CSS_SELECTOR, '[data-testid="results-and-standings-button"]')
                        standings_button.click()                
                    try:
                        result_button = self.browser.find_elements(By.CSS_SELECTOR,'[data-testid="results-page-tab-standings"]')
                        result_button[1].click()
                    except (TimeoutException,ElementClickInterceptedException):
                        result_button=self.browser.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/div/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")
                        result_button.click()
                except:
                    self.browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")
                time.sleep(7)


                # To determine the week num to save pages 
                games_to_check=34-to_play
                if games_to_check<11:
                    week_to_save1=games_to_check
                    week_to_save2=0
                elif games_to_check>10:
                    week_to_save1=10
                    week_to_save2=games_to_check
                    # week_to_save1=21
                    # week_to_save2=23

            
                game_weeks = self.browser.find_elements(By.CSS_SELECTOR, ".week-number")[:week_to_save1]
                current_game_week=int(game_weeks[0].text.split(" ")[-1])  # To get the integer num of weeks
                # To check if last result is 9th - 10th week or sleep till it is

                if current_game_week<week_to_save1-1:
                    time_to_sleep=(week_to_save1-1-current_game_week)*3
                    delete_cache(self.browser)
                    time.sleep(5)
                    terminate_driver_process(self.browser)
                    # self.browser.quit()
                    time.sleep(time_to_sleep*60)
                    # self.browser=webdriver.Chrome()        # driver instance with User Interface (not headless)
                    self.browser = set_up_driver_instance()  # driver instance without User Interface (--headless)
                    time.sleep(1)
                    self.browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")
                    time.sleep(5)
                elif current_game_week>week_to_save1:
                    time_to_sleep=(34-current_game_week)*3
                    delete_cache(self.browser)
                    time.sleep(5)
                    terminate_driver_process(self.browser)
                    # self.browser.quit()
                    time.sleep(((week_to_save1-1)*3+time_to_sleep)*60)
                    # self.browser=webdriver.Chrome()         # driver instance with User Interface (not headless)
                    self.browser = set_up_driver_instance()   # driver instance without User Interface (--headless)
                    time.sleep(1)
                    self.browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")
                    time.sleep(5)

                # checking if the last week played is Week 10 before going ahead to save the page
                game_weeks[:] = self.browser.find_elements(By.CSS_SELECTOR, ".week-number")[:week_to_save1]
                # game_weeks = check_if_last_result_equal_input(self.browser, game_weeks=game_weeks, week_to_check=f"Week {week_to_save1}",time_delay=30)
                
                last_week_equal_input=MyCustomThread(target=check_if_last_result_equal_input,kwargs={"browser":self.browser,
                "game_weeks":game_weeks, "week_to_check":f"Week {week_to_save1}", "time_delay":30},daemon=True)
                last_week_equal_input.start()
                game_weeks[:]=last_week_equal_input.join()
                if last_week_equal_input.error:
                    raise last_week_equal_input.error

                game_weeks[:]=game_weeks[:week_to_save1]
                print(f"Woow its week {week_to_save1}, lets wait for week {week_to_save2}")
                ht_scores = self.browser.find_elements(By.CSS_SELECTOR, ".score.ht")[:week_to_save1*9]
                ft_scores = self.browser.find_elements(By.CSS_SELECTOR, ".score.ft")[:week_to_save1*9]
                for i in range(len(ft_scores)):
                    ht_scores[i]=ht_scores[i].text
                    ft_scores[i]=ft_scores[i].text
                    if i<len(game_weeks):
                        game_weeks[i]=game_weeks[i].text

                try:
                    page_path1 = "saved_pages/one_to_ten_page.html"
                    save_page(self.browser, page_name=page_path1)  # save the games(1-10) page
                except FileNotFoundError:
                    page_path1 = "SeleniumProject/saved_pages/one_to_ten_page.html"
                    save_page(self.browser, page_name=page_path1)
                delete_cache(self.browser)
                time.sleep(5)
                terminate_driver_process(self.browser)
                # self.browser.quit()
                weeks_left=week_to_save2-week_to_save1
                if weeks_left<0:
                    weeks_left=0
                    time.sleep(weeks_left*3*60)  # To wait untill start_week2
                else:
                    time.sleep((weeks_left-1)*3*60)  # To wait untill start_week2
                
                # self.browser=webdriver.Chrome()          # driver instance with User Interface (not headless)
                self.browser = set_up_driver_instance()    # driver instance without User Interface (--headless)
                self.browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")
                time.sleep(5)
                second_game_weeks = self.browser.find_elements(By.CSS_SELECTOR, ".week-number")[:weeks_left]
                # checking if the last week played is Week 20 before going ahead to save the page
                # second_game_weeks = check_if_last_result_equal_input(self.browser, game_weeks=second_game_weeks,
                #                                                     week_to_check=f"Week {week_to_save2}", time_delay=5)
                
                last_week_equal_input=MyCustomThread(target=check_if_last_result_equal_input,kwargs={"browser":self.browser,
                "game_weeks":second_game_weeks, "week_to_check":f"Week {week_to_save2}", "time_delay":10},daemon=True)
                last_week_equal_input.start()
                second_game_weeks[:]=last_week_equal_input.join()
                if last_week_equal_input.error:
                    raise last_week_equal_input.error
                second_game_weeks[:]=second_game_weeks[:weeks_left]
                
                # Add the 11-20 weeks matches to the 1-10 weeks matchesx
                ht_scores.extend(self.browser.find_elements(By.CSS_SELECTOR, ".score.ht")[:weeks_left*9])
                ft_scores.extend(self.browser.find_elements(By.CSS_SELECTOR, ".score.ft")[:weeks_left*9])
                game_weeks.extend(second_game_weeks)

                try:
                    page_path2 = "saved_pages/eleven_to_twenty_page.html"
                    save_page(self.browser, page_name=page_path2)  # save the games(11-20) page
                except FileNotFoundError:
                    page_path2 = "SeleniumProject/saved_pages/eleven_to_twenty_page.html"
                    save_page(self.browser, page_name=page_path2)
                # result = confirm_outcome(ht_scores=ht_scores, ft_scores=ft_scores, game_weeks=game_weeks,market=market,length=length)
                outcome_confirmation=MyCustomThread(target=confirm_outcome,kwargs={'ht_scores':ht_scores, 'ft_scores':ft_scores, "game_weeks":game_weeks,"market":market,"length":length},daemon=True)
                outcome_confirmation.start()
                result=outcome_confirmation.join()
                if outcome_confirmation.error:
                    raise outcome_confirmation.error
            except Exception as error:
                print("an error occured i skipped this session")
                print(f"this is the error: {error}")
                result={"outcome":"","message":f"an error occured i skipped this session. This is the error: {error}"}

        elif length.lower() == "last result":
            try:
                try:
                    try:
                        standings_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="results-and-standings-button"]')))
                        # standings_button=self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
                        standings_button.click()
                    except (TimeoutException,ElementClickInterceptedException):
                        standings_button=self.browser.find_element(By.CSS_SELECTOR, '[data-testid="results-and-standings-button"]')
                        standings_button.click()                
                    try:
                        result_button = self.browser.find_elements(By.CSS_SELECTOR,'[data-testid="results-page-tab-standings"]')
                        result_button[1].click()

                    except (TimeoutException,ElementClickInterceptedException):
                        result_button=self.browser.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/div/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")
                        result_button.click()
                except:
                    self.browser.get("https://m.betking.com/virtual/league/kings-bundliga/results")
                time.sleep(5)
            
                game_weeks = self.browser.find_elements(By.CSS_SELECTOR, ".week-number")
                # checking if the last week played is latest_week before going ahead to save the page
                # game_weeks = check_if_last_result_equal_input(self.browser, game_weeks=game_weeks,
                #                                             week_to_check=latest_week,time_delay=5)
                
                last_week_equal_input=MyCustomThread(target=check_if_last_result_equal_input,kwargs={"browser":self.browser,
                "game_weeks":game_weeks, "week_to_check":latest_week, "time_delay":10},daemon=True)
                last_week_equal_input.start()
                game_weeks[:]=last_week_equal_input.join()
                if last_week_equal_input.error:
                    raise last_week_equal_input.error
                game_weeks[:] = game_weeks[:1]

                # Re-fill the ht and ft_scores list by the reloaded/current score result of the last week played   
                ht_scores = self.browser.find_elements(By.CSS_SELECTOR, ".score.ht")[:9]
                ft_scores = self.browser.find_elements(By.CSS_SELECTOR, ".score.ft")[:9]

                # result = confirm_outcome(ht_scores=ht_scores, ft_scores=ft_scores, game_weeks=game_weeks,market=market,length=length)
                outcome_confirmation=MyCustomThread(target=confirm_outcome,kwargs={'ht_scores':ht_scores, 'ft_scores':ft_scores, "game_weeks":game_weeks,"market":market,"length":length},daemon=True)
                outcome_confirmation.start()
                result=outcome_confirmation.join()
                if outcome_confirmation.error:
                    raise outcome_confirmation.error
            
            except Exception as error:
                print(f"an error occured when checking last result i want to use acc balance to check.This is the error: {error}")
                # if the result page fails, compare balances to tell the outcome
                if check_if_last_stake_has_played(browser=self.browser,week_to_check=latest_week,time_delay=30):
                    time.sleep(10)  # TODO: Confirm the time to sleep before the balance reflects
                    print("last staked has finnished playing")
                    refresh_bal_button=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .refresh-icon')
                    refresh_bal_button.click()
                    time.sleep(2)
                    acc_balance_2=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
                    print(f"Old acc bal {acc_balance}, New acc bal {acc_balance_2}")
                    if float(acc_balance_2.replace(",","_"))>float(acc_balance.replace(',','_')):
                        result={"outcome":True,"message":f"I used the acc bal to confirm ticket won. this is the error: {error}"}
                    else:
                        result={"outcome":False,"message":f"I used the acc bal to confirm ticket won. this is the error: {error}"}

        if result["outcome"] == "" and length.lower() == "all result":
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                       Password=os.environ.get("EMAIL_PASSWORD"),
                       Subject=f"No PATTERN found yet",
                       Message=result["message"],
                       File_path=[page_path1, page_path2]
                       )
            cancel_result_page_button = self.browser.find_element(By.CSS_SELECTOR, "svg path")
            cancel_result_page_button.click()
            return {"outcome": result["outcome"], "driver": self.browser}

        elif result["outcome"] == True and length.lower() == "last result":
            try:
                page_path = "saved_pages/one_to_ten_page.html"
                save_page(self.browser, page_name=page_path)
            except FileNotFoundError:
                page_path = f"{os.environ.get('PROJECT_PATH')}/saved_pages/one_to_ten_page.html"
                save_page(self.browser, page_name=page_path)  # save the games(1-10) page
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                       Password=os.environ.get("EMAIL_PASSWORD"),
                       Subject=f"{market} came in the last result" ,
                       Message=result["message"],
                       File_path=[page_path]
                       )

            cancel_result_page_button = self.browser.find_element(By.CSS_SELECTOR, "svg path")
            cancel_result_page_button.click()
            return {"outcome": True, "driver": self.browser}

        elif result["outcome"] != "" and length.lower() == "all result":
            print(f'PATTERN found: {result["message"]}')
            print('Did not send mail')
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                       Password=os.environ.get("EMAIL_PASSWORD"),
                       Subject=f"PATTERN found",
                       Message=result["message"],
                       File_path=[page_path1, page_path2]
                       )
            cancel_result_page_button = self.browser.find_element(By.CSS_SELECTOR, "svg path")
            cancel_result_page_button.click()
            return {"outcome": result["outcome"], "driver": self.browser}

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
        """ Login the user with the credentials from initialization and return the account balance of the user"""
        # login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text")))
        # login= self.browser.find_element(By.CSS_SELECTOR, "button.text")
        login= self.browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
        try:
            login.click()
        except:
            try:
                cancel_popup(self.browser)
                login = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text")))
                login.click()
            except:
                login= self.browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
                login.click()
                
        username = self.browser.find_element(By.CSS_SELECTOR, '[placeholder="Username or Verified Mobile"]')
        password = self.browser.find_element(By.CSS_SELECTOR, '[placeholder="Password"]')
        # fill the username and password form with the inputed variable
        for char in self.username:
            # time.sleep(0.5)
            username.send_keys(char)
        for char in self.password:
            # time.sleep(0.5)
            password.send_keys(char)
        # time.sleep(1)
        login_button = self.browser.find_element(By.CSS_SELECTOR, '[text="Login"]')
        login_button.click()
        time.sleep(2)
        try:
            cancel_notification_option_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.kumulos-action-button-cancel")))
            # cancel_notification_option_button=self.browser.find_element(
            #     By.CSS_SELECTOR, "button.kumulos-action-button-cancel")
            cancel_notification_option_button.click()
        except (TimeoutException, NoSuchElementException):
            pass

        try:
            acc_balance=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
        except NoSuchElementException:
            acc_balance="210,000"
            pass
            # self.browser.refresh()
            # time.sleep(2)
            # acc_balance=self.browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
            
        return acc_balance