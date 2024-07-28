import time
import os
from brain import LoginUser,CheckPattern,PlayGame
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
from tools import reduce_week_selected, send_email, set_up_driver_instance,MyCustomThread,delete_cache,terminate_driver_process


load_dotenv()


# TODO: Create a requirements.txt file
# NOTE: start the program at 1.5-2.5mins to the next week play 
# TODO: check for left over find elements using path and try to convert to css selector
# TODO: Test the check_if_current_week_has_played(previous_week_selected) function to see if it works as intended
# TODO: test for time complexity
# TODO: Reformat all modules and code 





def stake_next_game(game_play,pattern,pattern_stake_options,key,stake_amount,LEAGUE):
    try:
        result=game_play.select_stake_options(week="current_week",previous_week_selected="Week 50",pattern_stake=pattern_stake_options[key],stake_amount=stake_amount)
        week_selected=result[0]
        try:
            acc_bal=result[1]
        except:
            pass
    except Exception as e:
        print(f'an error ocured i didnt stake option.   {e}')
    
    reduced_week_selected=reduce_week_selected(week_selected,by=0,league=LEAGUE["name"])
    last_result_outcome=pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal,market=key)['outcome']
    return [last_result_outcome,reduced_week_selected]


def start_bot():
    global current_pattern_count
    global count
    LEAGUE={"name":"bundliga","num_of_weeks":34}
    MAX_SEASON=6
    SELECTED_MARKET="correct_score"
    # amount_listX1=[10, 10, 10, 10, 10, 10, 20, 20, 20, 30, 30, 35, 45, 50, 55, 65, 80, 95, 110,
    #             130, 155, 185, 220, 250, 300, 350, 410, 490, 580, 680, 805, 935, 1100, 1300, 1530,
    #             1800, 2115, 2490, 2930, 3500]
    # TOTAL_AMOUNTx40=206730  #TOTAL_AMOUNTx30=40185
    amount_listX6=[60, 60, 60, 60, 60, 60, 120, 120, 120, 180, 180, 210, 270, 300, 330, 390, 
                   480, 570, 660, 780, 930, 1110, 1320, 1500, 1800, 2100, 2460, 2940, 3480, 
                   4080, 4830, 5610, 6600, 7800, 9180, 10800, 12690, 14940, 17580, 21000]
    AMOUNT_LIST=tuple(amount_listX6)
    TOTAL_AMOUNT=241110   # sum of amount_listX6[:30]

    # browser=webdriver.Chrome()           # driver instance with User Interface (not headless)
    browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
    pattern=CheckPattern(browser)
    try:
        
        browser.get("https://m.betking.com/")
        print("i have lunched")
        try:
            pattern.checkout_virtual(league=LEAGUE["name"])
        except:
            browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
    except Exception as error:
        print(f"THIS is the Error: {error}")
        
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
                        log=LoginUser(browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
                        try:
                            login=browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
                            acc_bal=log.login()
                        except NoSuchElementException:
                            acc_balance=browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
                        acc_bal=float(acc_bal.replace(",","_"))
                        # game level to be created only at the first iteration
                        if n<MAX_SEASON-1:
                            GAME_LEVEL=round((acc_bal-9000)/TOTAL_AMOUNT,2)
                        time.sleep(1)

                        game_play=PlayGame(browser,market=SELECTED_MARKET)
                        game_play.choose_market()
                        time.sleep(1)


                        acc_bal=str(acc_bal)
                        pattern_stake_options={'4 - 0':6,'4 - 1':7,} 
                        for i in range(10):
                            i+=current_stake_num
                            # provision to stake 10 games afterwhich funds are exhausted and place bet begins to skip
                            stake_amount=AMOUNT_LIST[i]*GAME_LEVEL
                            stake_the_next_game=MyCustomThread(target=stake_next_game,args=(game_play,pattern,pattern_stake_options,key,stake_amount,LEAGUE),daemon=True)
                            stake_the_next_game.start()
                            output=stake_the_next_game.join()
                            last_result_outcome=output[0]
                            reduced_week_selected=output[1]
                            print(last_result_outcome,reduced_week_selected)
                            if last_result_outcome:
                                won=True
                                # delete_cache(browser)
                                # time.sleep(5)
                                # terminate_driver_process(browser)
                                # browser.quit()
                                break

                        # check for patterns after each staked SEASON 
                        try:
                            check_result=pattern.check_result(length="all result", latest_week="all")
                            browser=check_result['driver']
                        except Exception as error:
                            print(f"An error occured, I skipped check_result(all result). This is the error {error}")
                            check_result={'outcome':{'4 - 0':1, '4 - 1':1}}
                        for k,v in check_result['outcome'].items():
                            if v==0:
                                current_pattern_count[k]+=1
                            else:
                                current_pattern_count[k]=0
                        print(f'first this is the current_pattern_count: {current_pattern_count}')
                        time.sleep(180)    # To delay till week 11
            
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
    for k,v in check_result['outcome'].items():
        if v==0:
            current_pattern_count[k]+=1
        else:
            current_pattern_count[k]=0
    print(f'last this is the current_pattern_count: {current_pattern_count}')
    time.sleep(180)    # To delay till week 11
    

    delete_cache(browser)
    time.sleep(5)
    terminate_driver_process(browser)
    browser.quit()


    # for testing full application
    if count<3:                                 #
        current_pattern_count["4 - 1"]=3        #
    elif count==4:
        count=0                                 #
    count+=1                                    #
        

        
    

if __name__ == "__main__":
    current_pattern_count={'4 - 0':0, '4 - 1':0}
    count=0               #
    while True:
        # bot=mp.Process(target=start_bot,args=(count,),daemon=True)
        bot=MyCustomThread(target=start_bot,daemon=True)
        bot.start()
        bot.join()
        # bot.terminate()
        print('bot terminated')