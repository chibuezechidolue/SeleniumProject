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

GAME_LEVEL=1
SELECTED_MARKET="3-3"

if SELECTED_MARKET=="ht/ft":
    AMOUNT_LIST=(10,10,10,20,30,40,55,80,110,160,230,330,470,675,970,
                1390,1980,2840,4050,5800,8300,11850,16950,24250)
    MAX_AMOUNT_LENGTH=14
    TOTAL_AMOUNT=9450
elif SELECTED_MARKET=="3-3":
    # AMOUNT_LIST=(10,10,10,10,10,10,20,20,30,30,40,40,55,55,80,80,110,
    #              110,160,160,230,230,330,330,470,470,675,675,970,970,
    #              1390,1390,1980,1980)
    AMOUNT_LIST=(10,10,10,10,10,10,20,20,20,30,30,35,45,50,55,65,80,95,110,
                 130,155,185,220,250,300,350,410,490,580,680,805,935,1100,
                 1300,1530,1800,2115,2490,2930,3500)
    MAX_AMOUNT_LENGTH=30
    # TOTAL_AMOUNT=9450
    TOTAL_AMOUNT=40183
LEAGUE={"name":"bundliga","num_of_weeks":34}
    
MAX_SEASON=6

while True:
    try:
        # browser=webdriver.Chrome()           # driver instance with User Interface (not headless)
        browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
        browser.get("https://m.betking.com/")
        print("i have lunched")
        pattern=CheckPattern(browser,market=SELECTED_MARKET)
        try:
            pattern.checkout_virtual(league=LEAGUE["name"])
        except:
            browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
    except Exception as error:
        print(f"THIS is the Error: {error}")
        pass
    print("i am about to check result")
    won=False
    
    for n in range(1,MAX_SEASON+1):
        if n>=MAX_SEASON-2:
            # Note: the number if statements depends on the number of seasons to be played (i.e current_stake_num=20)
            if n==MAX_SEASON-1:
                current_stake_num=10
            elif n==MAX_SEASON:
                current_stake_num=20
            else:
                current_stake_num=0
            pattern=CheckPattern(browser,market=SELECTED_MARKET)
            print(current_stake_num)
            try:
                check_result=pattern.check_result(length="new season", latest_week="all")
            except Exception as error:
                print(f"An error occured, I skipped check_result(new season). This is the error {error}")
                check_result={'outcome':False}
            if check_result["outcome"]:
                browser=check_result['driver']
                log=LoginUser(browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
                time.sleep(2)
                acc_bal=log.login()
                acc_bal=float(acc_bal.replace(",","_"))
                if n<MAX_SEASON-1:
                    GAME_LEVEL=round((acc_bal-1000)/TOTAL_AMOUNT,2)
                time.sleep(1)

                game_play=PlayGame(browser,market=SELECTED_MARKET)
                game_play.choose_market()
                time.sleep(1)


                won=False
                acc_bal=str(acc_bal)
                for i in range(10):
                    i+=current_stake_num
                    # provision to stake 10 games afterwhich funds are exhausted and place bet begins to skip
                    try:
                        week_selected=game_play.select_stake_options(week="current_week",previous_week_selected="Week 50")
                    except:
                        pass
                    try:
                        acc_bal=game_play.place_the_bet(amount=str(AMOUNT_LIST[i]*GAME_LEVEL),test=eval(os.environ.get("TEST")))
                        print(str(AMOUNT_LIST[i]*GAME_LEVEL))
                    except:
                        pass
                    # week_selected=game_play.select_stake_options(week="after_current_week",
                    #                                             previous_week_selected=week_selected)
                    reduced_week_selected=reduce_week_selected(week_selected,by=0,league=LEAGUE["name"])

                    pattern=CheckPattern(browser,market=SELECTED_MARKET)
                    if pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal)['outcome']:
                        won=True
                        # browser.quit()
                        break


        pattern=CheckPattern(browser,market=SELECTED_MARKET)
        try:
            check_result=pattern.check_result(length="all result", latest_week="all")
            browser=check_result['driver']
        except Exception as error:
            print(f"An error occured, I skipped check_result(all result). This is the error {error}")
            check_result={'outcome':True}
        time.sleep(180)    # To delay till week 11
        if check_result['outcome']:
            won=True
            break
        if n<MAX_SEASON:
            print(f"SEASON {n} result has been CHECKED, waiting for next SEASON ")
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                    Password=os.environ.get("EMAIL_PASSWORD"),
                    Subject=f"(11th-20th) On To The NEXT 10 Stakes",
                    Message=f"SEASON {n} result has been CHECKED, waiting for next SEASON ",
                    File_path=[check_result["page_path"]]
                    )
        
        
    if not won:        
        print(f"{SELECTED_MARKET} did not come till SEASON {MAX_SEASON}")
        send_email(Email=os.environ.get("EMAIL_USERNAME"),
                    Password=os.environ.get("EMAIL_PASSWORD"),
                    Subject="(11th-20th) YOU'VE LOST IT ALL",
                    Message=f"{SELECTED_MARKET} did not come till SEASON {MAX_SEASON}"
                    )
    browser.quit()
        
    

