import time
from brain import LoginUser,CheckPattern,PlayGame,browser,wait,By,EC,TimeoutException,NoSuchElementException
import os
from dotenv import load_dotenv
from tools import reduce_week_selected,clear_bet_slip

load_dotenv()



# NOTE: start the program at 1.5-2.5mins to the next week play 
# TODO: check for left over find elements using path and try to convert to css selector
# TODO: Test the check_if_current_week_has_played(previous_week_selected) function to see if it works as intended
# TODO: test for time complexity
# TODO: Reformat all modules and code 


def play_bundesliga(as_test:bool,game_level:int,selected_market:str):
    """ To play the """
    # Bundesliga game variables
    GAME_LEVEL=game_level
    SELECTED_MARKET=selected_market
    AMOUNT_LIST=(10,10,10,20,30,40,55,80,110,160,230,330,470,675,970)
    bundesliga={"name":"bundliga","num_of_weeks":34}

    pattern=CheckPattern(market=SELECTED_MARKET)
    try:
        pattern.checkout_virtual(league=bundesliga["name"])
    except:
        browser.get("https://m.betking.com/virtual/league/kings-bundliga")  

    if not pattern.check_result(length="all result", latest_week="all"):

        log=LoginUser(username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
        log.login()
        time.sleep(1)

        game_play=PlayGame(market=SELECTED_MARKET)
        time.sleep(2)
        game_play.choose_market()
        time.sleep(1)
        week_selected=game_play.select_stake_options(week="current_week",previous_week_selected="Week 50")

        for n in range(len(AMOUNT_LIST[:1])):
            game_play.place_the_bet(amount=str(AMOUNT_LIST[n]*GAME_LEVEL),test=as_test)
            week_selected=game_play.select_stake_options(week="after_current_week",
                                                        previous_week_selected=week_selected)
            reduced_week_selected=reduce_week_selected(week_selected,by=1,league=bundesliga["name"])

            #   TODO: write a script to stop/cancel the amount list in order to stop betting only if ht/ft does not come before the AMOUNT_LIST is exhauseted to avoid staking with the profit already made
            if pattern.check_result(length="last result",latest_week=reduced_week_selected):
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
            
    
while True:
    play_bundesliga(as_test=True,game_level=1,selected_market="ht/ft")


# TEST for check_result
# browser.get("https://m.betking.com/virtual/league/kings-bundliga")
# pattern=CheckPattern(market=SELECTED_MARKET)
# game_play=PlayGame(market=SELECTED_MARKET)
# time.sleep(3)
# game_play.choose_market()
# time.sleep(2)
# week_selected=game_play.select_stake_options(week="after_current_week")
# week_selected=reduce_week_selected(week_selected,by=1,league=bundesliga)


# pattern.check_result(length="last result",latest_week=week_selected) 






# Test for choose market


browser.get("https://m.betking.com/virtual/league/kings-bundliga")
game_play=PlayGame(market=SELECTED_MARKET)
time.sleep(3)

game_play.choose_market()
time.sleep(2)
week_selected=game_play.select_stake_options(week="current_week",previous_week_selected="Week 50")
for n in range(30):
    clear_bet_slip()
    time.sleep(3)
    game_play.choose_market()
    time.sleep(2)
    week_selected=game_play.select_stake_options(week="after_current_week",previous_week_selected=week_selected)
    time.sleep(1)
#     browser.refresh()
#     time.sleep(4)
    print(f"{n+1}  round")

    # NOTE: the problem is during the after_current_week selection when the current week starts, the total elements should reduces by 90 rather than remain 180. thus, the reason for the error
    
    # time.sleep(50)
    
    
    
print("Test complete. SUCCESS!!!")



