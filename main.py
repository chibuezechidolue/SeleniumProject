import time
import os
from brain import LoginUser,CheckPattern,PlayGame
from dotenv import load_dotenv
from tools import reduce_week_selected, send_email, set_up_driver_instance


load_dotenv()


# TODO: Create a requirements.txt file
# NOTE: start the program at 1.5-2.5mins to the next week play 
# TODO: check for left over find elements using path and try to convert to css selector
# TODO: Test the check_if_current_week_has_played(previous_week_selected) function to see if it works as intended
# TODO: test for time complexity
# TODO: Reformat all modules and code 


SELECTED_MARKET="correct_score"

AMOUNT_LIST=(50, 50, 50, 50, 50, 50, 100, 100, 100, 150, 150, 175, 225, 250, 275, 325, 400, 
             475, 550, 650, 775, 925, 1100, 1250, 1500, 1750, 2050, 2450, 2900, 3400, 4025, 
             4675, 5500, 6500, 7650, 9000, 10575, 12450, 14650, 17500)

TOTAL_AMOUNT=201000

LEAGUE={"name":"bundliga","num_of_weeks":34}
    
MAX_SEASON=6

# browser=webdriver.Chrome()           # driver instance with User Interface (not headless)
browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
pattern=CheckPattern(browser,market=SELECTED_MARKET)
log=LoginUser(browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
game_play=PlayGame(browser,market=SELECTED_MARKET)

current_pattern_count={'4 - 0':3, '4 - 1':0}

while True:
    try:
        
        browser.get("https://m.betking.com/")
        print("i have lunched")
        try:
            pattern.checkout_virtual(league=LEAGUE["name"])
        except:
            browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
    except Exception as error:
        print(f"THIS is the Error: {error}")
        pass
    print("i am about to check result")
    

    won=False
    for key,value in current_pattern_count.items():
        if value>=3:
            print(f"{key} PATTERN found waiting for NEW SEASON to start STAKING ")
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                    Password=os.environ.get("EMAIL_PASSWORD"),
                    Subject=f"(1st-10th) {key} PATTERN found",
                    Message=f"waiting for NEW SEASON to start STAKING ",
                    )
            for n in range(4,MAX_SEASON+1):
                if won:
                    break
                if n>=MAX_SEASON-2:
                    # Note: the number if statements depends on the number of seasons to be played (i.e current_stake_num=20)
                    if n==MAX_SEASON-1:
                        current_stake_num=10
                    elif n==MAX_SEASON:
                        current_stake_num=20
                    else:
                        current_stake_num=0
                    print(current_stake_num)
                    try:
                        check_result_new_season=pattern.check_result(length="new season", latest_week="all")
                    except Exception as error:
                        print(f"An error occured, I skipped check_result(new season). This is the error {error}")
                        check_result_new_season={'outcome':False}

                    if check_result_new_season["outcome"]:
                        browser=check_result_new_season['driver']
                        time.sleep(2)
                        acc_bal=log.login()
                        acc_bal=float(acc_bal.replace(",","_"))
                        if n<MAX_SEASON-1:
                            GAME_LEVEL=round((acc_bal-9000)/TOTAL_AMOUNT,2)
                        time.sleep(1)

                        
                        game_play.choose_market()
                        time.sleep(1)


                        acc_bal=str(acc_bal)
                        pattern_stake_options={'4 - 0':6,'4 - 1':7,} 
                        for i in range(10):
                            i+=current_stake_num
                            # provision to stake 10 games afterwhich funds are exhausted and place bet begins to skip
                            try:
                                result=game_play.select_stake_options(week="current_week",previous_week_selected="Week 50",pattern_stake=pattern_stake_options[key],stake_amount=AMOUNT_LIST[i]*GAME_LEVEL)
                                week_selected=result[0]
                                acc_bal=result[1]
                            except:
                                pass
                            # try:
                            #     acc_bal=game_play.place_the_bet(amount=str(AMOUNT_LIST[i]*GAME_LEVEL),test=eval(os.environ.get("TEST")))
                            #     print(str(AMOUNT_LIST[i]*GAME_LEVEL))
                            # except:
                            #     pass
                            
                            reduced_week_selected=reduce_week_selected(week_selected,by=0,league=LEAGUE["name"])

                            if pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal,market=key)['outcome']:
                                won=True
                                # browser.quit()
                                break

                        # check for patterns after each staked SEASON 
                        try:
                            check_result=pattern.check_result(length="all result", latest_week="all")
                            browser=check_result['driver']
                        except Exception as error:
                            print(f"An error occured, I skipped check_result(all result). This is the error {error}")
                            check_result={'outcome':{'4 - 0':1, '4 - 1':1}}
                        time.sleep(180)    # To delay till week 11
                        for k,v in check_result['outcome'].items():
                            if v==0:
                                current_pattern_count[k]+=1
                            else:
                                current_pattern_count[k]=0
                        print(f'this is the current_pattern_count: {current_pattern_count}')
            
            current_pattern_count[key]=0
            if not won:        
                print(f"{key} did not come till SEASON {MAX_SEASON}")
                send_email(Email=os.environ.get("EMAIL_USERNAME"),
                            Password=os.environ.get("EMAIL_PASSWORD"),
                            Subject="(1st-10th) YOU'VE LOST IT ALL",
                            Message=f"{key} did not come till SEASON {MAX_SEASON}"
                            )
            break

    try:
        check_result=pattern.check_result(length="all result", latest_week="all")
        browser=check_result['driver']
    except Exception as error:
        print(f"An error occured, I skipped check_result(all result). This is the error {error}")
        check_result={'outcome':{'4 - 0':1, '4 - 1':1}}
    time.sleep(180)    # To delay till week 11
    for k,v in check_result['outcome'].items():
        if v==0:
            current_pattern_count[k]+=1
        else:
            current_pattern_count[k]=0
    print(f'this is the current_pattern_count: {current_pattern_count}')
    
        
    
    # browser.quit()
        
    

