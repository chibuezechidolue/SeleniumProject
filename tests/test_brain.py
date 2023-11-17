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
        self.browser=webdriver.Chrome()    # driver instance with User Interface (not headless)
        # self.browser=set_up_driver_instance() # driver instance without User Interface (--headless)
        self.pattern=CheckPattern(self.browser,market="ht/ft")
        self.game_play=PlayGame(self.browser,market="ht/ft")
        self.log=LoginUser(self.browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
        self.browser.get("https://m.betking.com/virtual/league/kings-bundliga")

    
    def test_choose_market(self):
        time.sleep(2)
        for _ in range(10):
            self.game_play.choose_market()
            time.sleep(10)


    def test_select_stake_options_and_place_the_bet(self):
        AMOUNT_LIST=(10,10,10,20,30,40,55,80,110,160,230,330,470,675,970)
        self.game_play.choose_market()
        week_selected=self.game_play.select_stake_options(week="current_week",previous_week_selected="Week 1000")
        # self.test_login()
        for n in range(5):
            # clear_bet_slip(self.browser)
            acc_bal=self.game_play.place_the_bet(amount=AMOUNT_LIST[n],test=True)
            print(acc_bal)
            # if n==1:                 # To test the try & except block if results are not available
            #     acc_bal="2,266"
            week_selected=self.game_play.select_stake_options(week="after_current_week",previous_week_selected=week_selected)
            reduced_week_selected=reduce_week_selected(week_selected,by=1,league="bundliga")
            # self.pattern.check_result(length="last result",latest_week=reduced_week_selected)
            self.pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal)

    def test_checkout_virtual(self):
        for _ in range(3):
            self.browser.get("https://m.betking.com")
            self.pattern.checkout_virtual(league="bundliga")
            time.sleep(5)


    def test_login(self):
        self.log.login()
        time.sleep(3)
        
    
    def test_check_last_result(self):
        self.game_play.choose_market()
        week_selected=self.game_play.select_stake_options(week="current_week",previous_week_selected="Week 1000")
        while True:
            clear_bet_slip(self.browser)
            week_selected=self.game_play.select_stake_options(week="after_current_week",previous_week_selected=week_selected)
            reduced_week_selected=reduce_week_selected(week_selected,by=1,league="bundliga")
            if self.pattern.check_result(length="last result",latest_week=reduced_week_selected)['outcome']:
                print(f"it came in {reduced_week_selected}")
                break


    # TODO: check if theres is need to create another CheckPattern instance inorder for check_last_result to run sucessfully after the check_all_result has been run which will destroy and create a new driver instance
    def test_check_all_result(self):
        self.browser=self.pattern.check_result(length="all result", latest_week="all",to_play=20)['driver']

        # self.pattern=CheckPattern(self.browser,market="ht/ft")
        # print(self.pattern.check_result(length="last result",latest_week="Week 21")['outcome']) 



    

        
if __name__=="__main__":
    unittest.main()
