import time
import os
from brain import LoginUser,CheckPattern,PlayGame
from dotenv import load_dotenv
from tools import reduce_week_selected, send_email, set_up_driver_instance
from selenium import webdriver

load_dotenv()


# TODO: Create a requirements.txt file
# NOTE: start the program at 1.5-2.5mins to the next week play 
# TODO: check for left over find elements using path and try to convert to css selector
# TODO: Test the check_if_current_week_has_played(previous_week_selected) function to see if it works as intended
# TODO: test for time complexity
# TODO: Reformat all modules and code 


SELECTED_MARKET="ht/ft"

LEAGUE={"name":"bundliga","num_of_weeks":34}

while True:
    # browser=webdriver.Chrome()           # driver instance with User Interface (not headless)
    browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
    browser.get("https://m.betking.com/")
    print("i have lunched")
    pattern=CheckPattern(browser,market=SELECTED_MARKET)
    try:
        pattern.checkout_virtual(league=LEAGUE["name"])
    except:
        browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
    
    print("i am about to check result")
   
    # try:
    check_result=pattern.check_result(length="all result", latest_week="all")
    browser=check_result['driver']
    # except:
    #     print("An error occured i skipped check_result(all result)")
    #     check_result={'outcome':True}

    browser.quit()

