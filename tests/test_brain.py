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

from main import stake_next_game

import psutil
def get_mem_usage():
    return psutil.Process().memory_info().rss // 1024




class BrainTest(unittest.TestCase):

    def setUp(self):
        test_market="correct_score"
        # test_market="ht/ft"
        # self.browser=webdriver.Chrome()    # driver instance with User Interface (not headless)
        self.browser=set_up_driver_instance() # driver instance without User Interface (--headless)
        self.pattern=CheckPattern(self.browser)
        self.game_play=PlayGame(self.browser,market=test_market)
        self.log=LoginUser(self.browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
        self.browser.get("https://m.betking.com/virtual/league/kings-bundliga")
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
        time.sleep(2)
        self.game_play.choose_market()
        time.sleep(2)
        acc_bal=self.log.login()
        # acc_bal=2000.2
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
        print(f"start: {get_mem_usage()}")
        for n in range(14):
            # clear_bet_slip(self.browser)
            if n==10:
                os.environ["TEST"]="True"

            # print(f"after thread creation: {get_mem_usage()}")
            # result=self.game_play.select_stake_options(week="current_week",previous_week_selected="Week 1000",
            #                                                     pattern_stake=self.pattern_stake_options[check_result['outcome']],stake_amount=self.AMOUNT_LIST[n])
            
            # week_selected=result[0]
            # acc_bal=result[1]
            # reduced_week_selected=reduce_week_selected(week_selected,by=0,league="bundliga")
            # output=self.pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal,market=check_result['outcome'])
            # last_result=output["outcome"]

            # stake_next=threading.Thread(target=stake_next_game,args=(self.game_play,self.pattern_stake_options,check_result,1,self.browser,self.AMOUNT_LIST,self.LEAGUE,n),daemon=True)
            stake_next=MyCustomThread(target=stake_next_game,args=(self.game_play,self.pattern_stake_options,check_result,1,self.browser,self.AMOUNT_LIST,self.LEAGUE,n),daemon=True)
            stake_next.start()
            print(f"after thread creation: {get_mem_usage()}")
            output=stake_next.join()
            last_result=output[0]
            reduced_week_selected=output[1]
            print(f"last: {last_result,reduced_week_selected}")
            print(f"end of thread: {get_mem_usage()}")
            
        delete_cache(self.browser)
        time.sleep(5)
        self.browser.quit()
        terminate_driver_process()

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
