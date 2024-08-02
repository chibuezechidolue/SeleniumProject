import sys
import os
from dotenv import load_dotenv


load_dotenv()
sys.path.append(os.environ.get('PROJECT_PATH'))
import unittest
import time
from selenium import webdriver
from brain import (PlayGame,CheckPattern,LoginUser)
from tools import (reduce_week_selected,clear_bet_slip, set_up_driver_instance,delete_cache,terminate_driver_process,
                   save_page,send_email,MyCustomThread)
from selenium.webdriver.common.by import By

from main import stake_next_game,play_process
import multiprocessing as mp

import psutil
def get_mem_usage():
    return psutil.Process().memory_info().rss // 1024

def play_process(que,SELECTED_MARKET,check_result,MAX_AMOUNT_LENGTH,week_to_save1,LEAGUE,position):
    browser=set_up_driver_instance()
    browser.get("https://m.betking.com/virtual/league/kings-bundliga")
    time.sleep(2)
    
    log=LoginUser(browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
    try:
        login=browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
        acc_bal=log.login()
    except:
        browser.refresh()
        time.sleep(1)
        try:
            login=browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
            acc_bal=log.login()
        except:
            acc_bal=browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
    acc_bal=float(acc_bal.replace(",","_"))
    # time.sleep(0.5)
    
    game_play=PlayGame(browser,market=SELECTED_MARKET)
    game_play.choose_market()
    won=False
    sleep_time_before_next_check=1
    if check_result['outcome']=="3 - 2" or check_result['outcome']=="2 - 3":
        # amount_listX1=[11.3, 11.3, 16.95, 28.25, 45.2, 67.8, 107.35, 169.5, 265.55, 418.1, 649.75, 1033.95, 1638.5]
        amount_listX6=[68, 68, 102, 170, 272, 407, 645, 1017, 1594, 2509, 3899, 6204, 9831]
        AMOUNT_LIST=tuple(amount_listX6)
        stake_options_length=9
        TOTAL_AMOUNT=241074
    else:
        # amount_listX1=[10, 10, 10, 20, 30, 40, 55, 80, 110, 160, 230, 330, 470,675] 
        amount_listX6=[60, 60, 60, 120, 180, 240, 330, 480, 660, 960, 1380, 1980, 2820, 4050]
        AMOUNT_LIST=tuple(amount_listX6)
        stake_options_length=18
        TOTAL_AMOUNT=240840
    if os.environ.get('TEST'):
        GAME_LEVEL=1
    else:
        GAME_LEVEL=round((acc_bal-4000)/TOTAL_AMOUNT,2)
    acc_bal=str(acc_bal)
    pattern_stake_options={"3 - 2":[5], "2 - 3":[21],'4 - 0':[6,22], "0 - 4":[6,22],'4 - 1':[7,23], "1 - 4":[7,23], "2/1":[2,6], "1/2":[2,6]} 
    last_result=None
    reduced_week_selected=None
    print('ready to start staking')
    for n in range(len(AMOUNT_LIST[:MAX_AMOUNT_LENGTH])):
        # provision to stake 10 games afterwhich funds are exhausted and place bet begins to skip
        # if n==10:
        #     os.environ["TEST"]="True"
        #     send_email(Email=os.environ.get("EMAIL_USERNAME"),
        #            Password=os.environ.get("EMAIL_PASSWORD"),
        #            Subject="YOU'VE LOST IT ALL",
        #            Message=f"{SELECTED_MARKET} did not come till week {n}. I have changed to TEST MODE"
        #            )

        stake_the_next_game=MyCustomThread(target=stake_next_game,args=(position,game_play,pattern_stake_options,check_result,GAME_LEVEL,browser,AMOUNT_LIST,LEAGUE,n),daemon=True)
        stake_the_next_game.start()
        output=stake_the_next_game.join()
        last_result=output[0]
        reduced_week_selected=output[1]

        print(last_result,reduced_week_selected)
        if last_result['outcome']:
            # Calculate the number of weeks left before week 10 of the next season
            won=True
            weeks_left_to_finish_season = LEAGUE["num_of_weeks"] - int(reduced_week_selected.split()[1])
            sleep_time_before_next_check=(weeks_left_to_finish_season + week_to_save1-1)*3
            delete_cache(browser)
            time.sleep(5)
            terminate_driver_process(browser)
            # browser.quit()
            break
    que.put([won,sleep_time_before_next_check])


class BrainTest(unittest.TestCase):

    def setUp(self):
        self.test_market="correct_score"
        # test_market="ht/ft"
        # self.browser=webdriver.Chrome()    # driver instance with User Interface (not headless)
        self.browser=set_up_driver_instance() # driver instance without User Interface (--headless)
        self.pattern=CheckPattern(self.browser)
        self.game_play=PlayGame(self.browser,market=self.test_market)
        self.log=LoginUser(self.browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
        self.browser.get("https://m.betking.com/virtual/league/kings-bundliga")
        time.sleep(2)
        self.pattern_stake_options={"3 - 2":[5], "2 - 3":[21],'4 - 0':[6,22], "0 - 4":[6,22],'4 - 1':[7,23], "1 - 4":[7,23], "4 - 2":[8,24], "2 - 4":[8,24], "2/1":[2,6], "1/2":[2,6]}
        self.AMOUNT_LIST=[50, 50, 50, 100, 150, 200, 275, 400, 550, 800, 1150, 1650, 2350, 3375, 4850, 6950, 9900,
                        14200, 20250, 29000, 41500, 59250, 84750, 121250]
        self.LEAGUE={"name":"bundliga","num_of_weeks":34}

    
    # def test_choose_market(self):
    #     time.sleep(2)
    #     for _ in range(2):
    #         self.game_play.choose_market()
    #         time.sleep(10)

    #     # time.sleep(10)
    #     # delete_cache(self.browser)
    #     # print('i have cleared the cache')
    #     # time.sleep(100)


    def test_select_stake_options_and_place_the_bet(self):
        check_result={'outcome':'4 - 1'}
        # check_result={'outcome':'2/1'}
        # time.sleep(2)
        # self.game_play.choose_market()
        # time.sleep(2)
        # acc_bal=self.log.login()
        acc_bal=2000.2
        # acc_bal=str(acc_bal)
        week_to_play = self.browser.find_elements(By.CSS_SELECTOR, '.week')[0].text
        print(week_to_play)
        if week_to_play[5]=="0":
            week_no=week_to_play[6]
        else:
            week_no=week_to_play[5:7]
        check_week=f"{week_to_play[:4]} {week_no}"
        print(check_week)
        self.pattern.check_result(length="last result",latest_week=check_week,acc_balance=acc_bal,market=check_result['outcome'])
        
        terminate_driver_process(self.browser)
        s=time.perf_counter()
        # self.browser.quit()
        e=time.perf_counter()
        print(f"browser.quit took {e - s}secs")
        
        que = mp.Queue()  # to store data and move data between process
        left=mp.Process(target=play_process,args=(que,self.test_market,check_result,14,10,self.LEAGUE,0),daemon=True)
        left.start()
        if check_result['outcome']!='3 - 2' and check_result['outcome']!='2 - 3':
            right=mp.Process(target=play_process,args=(que,self.test_market,check_result,14,10,self.LEAGUE,1),daemon=True)
            right.start()

        left.join()
        try:
            right.join()
        except:
            pass
                                # OR
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     won=executor.submit(play_process,SELECTED_MARKET,check_result,MAX_AMOUNT_LENGTH,week_to_save1,LEAGUE,0)
        #     won1=executor.submit(play_process,SELECTED_MARKET,check_result,MAX_AMOUNT_LENGTH,week_to_save1,LEAGUE,1)
        # print(won)

        result=que.get()
        won,sleep_time_before_next_check = result[0],result[1]
        print(sleep_time_before_next_check*60)
        print(f"this is thr result: {won}")



    # def test_checkout_virtual(self):
    #     for _ in range(3):
    #         self.browser.get("https://m.betking.com")
    #         self.pattern.checkout_virtual(league="bundliga")
    #         time.sleep(5)


    # def test_login(self):
    #     acc_bal=self.log.login()
    #     # acc_bal=float(acc_bal.replace(",","_"))
    #     # GAME_LEVEL=round((acc_bal-1000)/500,2)
    #     print(acc_bal)
    #     # print(GAME_LEVEL)
    #     time.sleep(3)
    #     return acc_bal
        
    
    # def test_check_last_result(self):
    #     check_result={'outcome':'4 - 0'}
    #     self.game_play.choose_market()
    #     # acc_bal=self.test_login()
    #     acc_bal="40000"
    #     while True:
    #         week_selected=self.game_play.select_stake_options(week="current_week",previous_week_selected="Week 1000",
    #                                                           pattern_stake=self.pattern_stake_options[check_result['outcome']],stake_amount=self.AMOUNT_LIST[0])
    #         reduced_week_selected=reduce_week_selected(week_selected,by=0,league="bundliga")
    #         time.sleep(3)
    #         clear_bet_slip(self.browser)
    #         if self.pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal,market=check_result['outcome'])['outcome']:
    #             print(f"it came in {reduced_week_selected}")
    #             break
    #         # break



    # TODO: check if theres is need to create another CheckPattern instance inorder for check_last_result to run sucessfully after the check_all_result has been run which will destroy and create a new driver instance
    # def test_check_all_result(self):
    #     self.browser=self.pattern.check_result(length="all result", latest_week="all",to_play=14)['driver']

    #     # self.pattern=CheckPattern(self.browser,market="ht/ft")
    #     # print(self.pattern.check_result(length="last result",latest_week="Week 21")['outcome']) 



    

        
if __name__=="__main__":
    unittest.main()
    # test=BrainTest()
    # test.test_select_stake_options_and_place_the_bet()
