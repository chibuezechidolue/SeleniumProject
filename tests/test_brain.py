import sys
sys.path.append('c:\\Users\\Stanley Chidolue\\PersonalProject\\SeleniumProject')
import unittest
import time
import os
from selenium import webdriver
from brain import (PlayGame,CheckPattern,LoginUser)
from tools import reduce_week_selected,clear_bet_slip, set_up_driver_instance
from dotenv import load_dotenv

load_dotenv()


class BrainTest(unittest.TestCase):

    def setUp(self):
        # test_market="correct_score"
        test_market="ht/ft"
        self.browser=webdriver.Chrome()    # driver instance with User Interface (not headless)
        # self.browser=set_up_driver_instance() # driver instance without User Interface (--headless)
        self.pattern=CheckPattern(self.browser,market=test_market)
        self.game_play=PlayGame(self.browser,market=test_market)
        self.log=LoginUser(self.browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
        self.browser.get("https://m.betking.com/virtual/league/kings-bundliga")
        self.pattern_stake_options={"3 - 2":[5], "2 - 3":[21],'4 - 0':[6,22], "0 - 4":[6,22],'4 - 1':[7,23], "1 - 4":[7,23], "4 - 2":[8,24], "2 - 4":[8,24], "2/1":[2,6], "1/2":[2,6]}
        self.AMOUNT_LIST=[50, 50, 50, 100, 150, 200, 275, 400, 550, 800, 1150, 1650, 2350, 3375, 4850, 6950, 9900,
                        14200, 20250, 29000, 41500, 59250, 84750, 121250]

    
    def test_choose_market(self):
        time.sleep(2)
        for _ in range(2):
            self.game_play.choose_market()
            time.sleep(10)


    def test_select_stake_options_and_place_the_bet(self):
        # check_result={'outcome':'4 - 1'}
        check_result={'outcome':'2/1'}
        stake_option_length=18
        
        time.sleep(2)
        self.game_play.choose_market()
        # self.test_login()
        acc_bal=2000.2
        # acc_bal=str(acc_bal)
        self.pattern.check_result(length="last result",latest_week="Week 8",acc_balance=acc_bal,market=check_result['outcome'])

        for n in range(3):
            # clear_bet_slip(self.browser)
            if n==10:
                os.environ["TEST"]="True"
            # for _ in range(stake_option_length):
            week_selected=self.game_play.select_stake_options(week="current_week",previous_week_selected="Week 1000",
                                                                pattern_stake=self.pattern_stake_options[check_result['outcome']],stake_amount=self.AMOUNT_LIST[n])
            # try:
            #     acc_bal=self.game_play.place_the_bet(amount=self.AMOUNT_LIST[n],test=os.environ.get("TEST"))
            # except:
            #     pass
            # print(acc_bal)
            # if n==1:                 # To test the try & except block if results are not available
            #     acc_bal="2,266"
            reduced_week_selected=reduce_week_selected(week_selected,by=0,league="bundliga")
            # self.pattern.check_result(length="last result",latest_week=reduced_week_selected)
            # self.pattern=CheckPattern(self.browser,market="ht/ft")
            self.pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal,market=check_result['outcome'])

    def test_checkout_virtual(self):
        for _ in range(3):
            self.browser.get("https://m.betking.com")
            self.pattern.checkout_virtual(league="bundliga")
            time.sleep(5)


    def test_login(self):
        acc_bal=self.log.login()
        # acc_bal=float(acc_bal.replace(",","_"))
        # GAME_LEVEL=round((acc_bal-1000)/500,2)
        print(acc_bal)
        # print(GAME_LEVEL)
        time.sleep(3)
        return acc_bal
        
    
    def test_check_last_result(self):
        check_result={'outcome':'4 - 0'}
        self.game_play.choose_market()
        # acc_bal=self.test_login()
        acc_bal="40000"
        while True:
            week_selected=self.game_play.select_stake_options(week="current_week",previous_week_selected="Week 1000",
                                                              pattern_stake=self.pattern_stake_options[check_result['outcome']],stake_amount=self.AMOUNT_LIST[0])
            reduced_week_selected=reduce_week_selected(week_selected,by=0,league="bundliga")
            time.sleep(3)
            clear_bet_slip(self.browser)
            if self.pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal,market=check_result['outcome'])['outcome']:
                print(f"it came in {reduced_week_selected}")
                break
            # break



    # TODO: check if theres is need to create another CheckPattern instance inorder for check_last_result to run sucessfully after the check_all_result has been run which will destroy and create a new driver instance
    def test_check_all_result(self):
        self.browser=self.pattern.check_result(length="all result", latest_week="all",to_play=14)['driver']

        # self.pattern=CheckPattern(self.browser,market="ht/ft")
        # print(self.pattern.check_result(length="last result",latest_week="Week 21")['outcome']) 



    

        
if __name__=="__main__":
    unittest.main()
