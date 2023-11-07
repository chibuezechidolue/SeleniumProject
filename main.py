import time
import os
from brain import LoginUser,CheckPattern,PlayGame
from dotenv import load_dotenv
from tools import reduce_week_selected
from selenium import webdriver

load_dotenv()


# TODO: Create a requirements.txt file
# NOTE: start the program at 1.5-2.5mins to the next week play 
# TODO: check for left over find elements using path and try to convert to css selector
# TODO: Test the check_if_current_week_has_played(previous_week_selected) function to see if it works as intended
# TODO: test for time complexity
# TODO: Reformat all modules and code 




while True:
    # Bundesliga game variables
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # browser=webdriver.Chrome(options=chrome_options)
    browser=webdriver.Chrome()
    GAME_LEVEL=1
    SELECTED_MARKET="ht/ft"
    AMOUNT_LIST=(10,10,10,20,30,40,55,80,110,160,230,330,470,675,970,
                 1390,1980,2840,4050,5800,8300,11850,16950,24250)
    bundesliga={"name":"bundliga","num_of_weeks":34}
    
    
    browser.get("https://m.betking.com/")
    print("i have lunched")
    pattern=CheckPattern(browser,market=SELECTED_MARKET)
    try:
        pattern.checkout_virtual(league=bundesliga["name"])
    except:
        browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
    
    print("i am about to check result")
    check_result=pattern.check_result(length="all result", latest_week="all")
    browser=check_result['driver']
    if not check_result['outcome']:
        log=LoginUser(browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
        log.login()
        time.sleep(1)

        game_play=PlayGame(browser,market=SELECTED_MARKET)
        game_play.choose_market()
        time.sleep(1)
        week_selected=game_play.select_stake_options(week="current_week",previous_week_selected="Week 50")

        for n in range(len(AMOUNT_LIST[:14])):
            game_play.place_the_bet(amount=str(AMOUNT_LIST[n]*GAME_LEVEL),test=True)
            week_selected=game_play.select_stake_options(week="after_current_week",
                                                        previous_week_selected=week_selected)
            reduced_week_selected=reduce_week_selected(week_selected,by=1,league=bundesliga["name"])

            #   TODO: write a script to stop/cancel the amount list in order to stop betting only if ht/ft does not come before the AMOUNT_LIST is exhauseted to avoid staking with the profit already made
            pattern=CheckPattern(browser,market=SELECTED_MARKET)
            if pattern.check_result(length="last result",latest_week=reduced_week_selected)['outcome']:
                # Calculate the number of weeks left before week 10 of the next season
                weeks_left_to_finish_season = bundesliga["num_of_weeks"] - int(reduced_week_selected.split()[1])
                sleep_time_before_next_check=(weeks_left_to_finish_season + 9)*3
                browser.quit()
                time.sleep(sleep_time_before_next_check*60) 
                break
    else:
        # Calculate the number of weeks left before week 10 of the next season
        time_to_sleep = (bundesliga["num_of_weeks"]-20+9)*3
        browser.quit()
        time.sleep(time_to_sleep*60)

