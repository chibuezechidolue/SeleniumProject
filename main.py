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

GAME_LEVEL=1
SELECTED_MARKET="3-3"

if SELECTED_MARKET=="ht/ft":
    AMOUNT_LIST=(10,10,10,20,30,40,55,80,110,160,230,330,470,675,970,
                1390,1980,2840,4050,5800,8300,11850,16950,24250)
    MAX_AMOUNT_LENGTH=14
elif SELECTED_MARKET=="3-3":
    AMOUNT_LIST=(10,10,10,10,10,10,20,20,30,30,40,40,55,55,80,80,110,
                 110,160,160,230,230,330,330,470,470,675,675,970,970,
                 1390,1390,1980,1980)
    MAX_AMOUNT_LENGTH=30
LEAGUE={"name":"bundliga","num_of_weeks":34}
    

while True:
    browser=webdriver.Chrome()           # driver instance with User Interface (not headless)
    # browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
    browser.get("https://m.betking.com/")
    print("i have lunched")
    pattern=CheckPattern(browser,market=SELECTED_MARKET)
    try:
        pattern.checkout_virtual(league=LEAGUE["name"])
    except:
        browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
    
    check_result=pattern.check_result(length="all result", latest_week="all",to_play=35)
    browser=check_result['driver']
    if check_result['outcome']:
        log=LoginUser(browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
        log.login()
        time.sleep(1)

        game_play=PlayGame(browser,market=SELECTED_MARKET)
        game_play.choose_market()
        time.sleep(1)
        week_selected=game_play.select_stake_options(week="current_week",previous_week_selected="Week 50")

        won=False
        for n in range(len(AMOUNT_LIST[:MAX_AMOUNT_LENGTH])):
            acc_bal=game_play.place_the_bet(amount=str(AMOUNT_LIST[n]*GAME_LEVEL),test=True)
            week_selected=game_play.select_stake_options(week="after_current_week",
                                                        previous_week_selected=week_selected)
            reduced_week_selected=reduce_week_selected(week_selected,by=1,league=LEAGUE["name"])

            #   TODO: write a script to stop/cancel the amount list in order to stop betting only if ht/ft does not come before the AMOUNT_LIST is exhauseted to avoid staking with the profit already made
            pattern=CheckPattern(browser,market=SELECTED_MARKET)
            # pass in the account bal as a variable
            if pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal)['outcome']:
                # Calculate the number of weeks left before week 10 of the next season
                won=True
                weeks_left_to_finish_season = LEAGUE["num_of_weeks"] - int(reduced_week_selected.split()[1])
                sleep_time_before_next_check=weeks_left_to_finish_season*3
                browser.quit()
                time.sleep(sleep_time_before_next_check*60) 
                break
            if n==9 or n==19:
                # time.sleep(24*3*60)
                check_result=pattern.check_result(length="all result", latest_week="all",to_play=35)
                browser=check_result['driver']
        if not won:
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                       Password=os.environ.get("EMAIL_PASSWORD"),
                       Subject="YOU'VE LOST IT ALL",
                       Message=f"{SELECTED_MARKET} did not come till week {LEAGUE['num_of_weeks']}"
                       )

