import concurrent.futures
from queue import Queue
from brain import LoginUser,CheckPattern,PlayGame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
from tools import MyCustomThread, reduce_week_selected, send_email, set_up_driver_instance,delete_cache, terminate_driver_process
import time
import os
import psutil
import multiprocessing as mp
import concurrent



load_dotenv()


# TODO: Create a requirements.txt file
# NOTE: start the program at 1.5-2.5mins to the next week play 
# TODO: check for left over find elements using path and try to convert to css selector
# TODO: Test the check_if_current_week_has_played(previous_week_selected) function to see if it works as intended
# TODO: test for time complexity
# TODO: Reformat all modules and code 



def stake_next_game(position,game_play,pattern_stake_options,check_result,GAME_LEVEL,browser,AMOUNT_LIST,LEAGUE,n):
    try:
        result=game_play.select_stake_options(position,week="current_week",previous_week_selected="Week 50",pattern_stake=pattern_stake_options[check_result['outcome']],stake_amount=AMOUNT_LIST[n]*GAME_LEVEL)
        week_selected=result[0]
        try:
            acc_bal=result[1]
        except:
            pass
    except Exception as e:
        print(f'an error ocured i didnt stake option.   {e}')
    reduced_week_selected=reduce_week_selected(week_selected,by=0,league=LEAGUE["name"])        
    pattern=CheckPattern(browser)
    last_result=pattern.check_result(length="last result",latest_week=reduced_week_selected,acc_balance=acc_bal,market=check_result['outcome'])
    return [last_result,reduced_week_selected]


def start_bot(que,position,count):
    MAX_AMOUNT_LENGTH=14
    LEAGUE={"name":"bundliga","num_of_weeks":34}
    browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
    try:
        browser.get("https://m.betking.com/")
    except:
        pass
        # browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
        # browser.get("https://m.betking.com/")

    print("i have lunched")
    try:
        pattern=CheckPattern(browser)
        pattern.checkout_virtual(league=LEAGUE["name"])
    except:
        try:
            browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
        except:
            delete_cache(browser)
            time.sleep(5)
            terminate_driver_process(browser)
            # browser.quit()
            browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
            browser.get("http://m.betking.com/virtual/league/kings-bundliga")
    
    print("i am about to check result")
    games_to_check=LEAGUE["num_of_weeks"] - MAX_AMOUNT_LENGTH
    if games_to_check<11:
        week_to_save1=games_to_check
    else:
        week_to_save1=10
    try:
        check_result=pattern.check_result(length="all result", latest_week="all",to_play=MAX_AMOUNT_LENGTH)
        browser=check_result['driver']
    except:
        print("An error occured i skipped check_result(all result)")
        check_result={'outcome':""}
        
    if count<3:                          #
        check_result['outcome']="4 - 0"               #
    elif count==3:
        count=0                                 #
    count+=1                                   #

    que.put(count)                             #
    

    if check_result['outcome'] != "":
        if check_result['outcome']=='2/1' or check_result['outcome']=='1/2':
            SELECTED_MARKET="ht/ft"
        else:
            SELECTED_MARKET="correct_score"
    
        if check_result['outcome']=='3 - 2' and position==1 or check_result['outcome']=='2 - 3' and position==1:
            terminate_driver_process(browser)
            weeks_left_to_finish_season = LEAGUE["num_of_weeks"] - 20 #(last week played)
            sleep_time_before_next_check=(weeks_left_to_finish_season + week_to_save1-1)*3
            print(f'away_bot is waiting for {sleep_time_before_next_check*60} secs')
            time.sleep(sleep_time_before_next_check*60)
        else:
            game_play=PlayGame(browser,market=SELECTED_MARKET)
            game_play.choose_market()
            time.sleep(1)
            log=LoginUser(browser,username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
            try:
                login=browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
                acc_bal=log.login()
            except NoSuchElementException:
                browser.refresh()
                time.sleep(1)
                try:
                    login=browser.find_element(By.CSS_SELECTOR, '.guest-header-content .text')
                    acc_bal=log.login()
                except:
                    acc_bal=browser.find_element(By.CSS_SELECTOR, '.user-balance-container .amount').text
            acc_bal=float(acc_bal.replace(",","_"))
            # time.sleep(0.5)
            
            won=False
            if check_result['outcome']=="3 - 2" or check_result['outcome']=="2 - 3":
                # amount_listX1=[11.3, 11.3, 16.95, 28.25, 45.2, 67.8, 107.35, 169.5, 265.55, 418.1, 649.75, 1033.95, 1638.5]
                amount_listX6=[68, 68, 102, 170, 272, 407, 645, 1017, 1594, 2509, 3899, 6204, 9831]
                AMOUNT_LIST=tuple(amount_listX6)
                stake_options_length=9
                TOTAL_AMOUNT=241074
            else:
                # amount_listX1=[10, 10, 10, 20, 30, 40, 55, 80, 110, 160, 230, 330, 470,675] 
                amount_listX6=[60, 60, 60, 120, 180, 240, 330, 480, 660, 960, 1380, 1980, 2820, 4050]
                AMOUNT_LIST=tuple(amount_listX6)
                stake_options_length=18
                TOTAL_AMOUNT=240840
            if os.environ.get('TEST'):
                GAME_LEVEL=1
            else:
                GAME_LEVEL=round((acc_bal-4000)/TOTAL_AMOUNT,2)
            acc_bal=str(acc_bal)
            pattern_stake_options={"3 - 2":[5], "2 - 3":[21],'4 - 0':[6,22], "0 - 4":[6,22],'4 - 1':[7,23], "1 - 4":[7,23], "2/1":[2,6], "1/2":[2,6]} 
            last_result=None
            reduced_week_selected=None
            print('ready to start staking')
            for n in range(len(AMOUNT_LIST[:MAX_AMOUNT_LENGTH])):
                # provision to stake 10 games afterwhich funds are exhausted and place bet begins to skip
                # if n==10:
                #     os.environ["TEST"]="True"
                #     send_email(Email=os.environ.get("EMAIL_USERNAME"),
                #            Password=os.environ.get("EMAIL_PASSWORD"),
                #            Subject="YOU'VE LOST IT ALL",
                #            Message=f"{SELECTED_MARKET} did not come till week {n}. I have changed to TEST MODE"
                #            )

                stake_the_next_game=MyCustomThread(target=stake_next_game,args=(position,game_play,pattern_stake_options,check_result,GAME_LEVEL,browser,AMOUNT_LIST,LEAGUE,n),daemon=True)
                stake_the_next_game.start()
                output=stake_the_next_game.join()
                last_result=output[0]
                reduced_week_selected=output[1]

                print(last_result,reduced_week_selected)
                if last_result['outcome']:
                    # Calculate the number of weeks left before week 10 of the next season
                    won=True
                    weeks_left_to_finish_season = LEAGUE["num_of_weeks"] - int(reduced_week_selected.split()[1])
                    sleep_time_before_next_check=(weeks_left_to_finish_season + week_to_save1-1)*3
                    delete_cache(browser)
                    time.sleep(5)
                    terminate_driver_process(browser)
                    # browser.quit()
                    print(f'waiting for {sleep_time_before_next_check*60} secs')
                    time.sleep(sleep_time_before_next_check*60)
                    break

            if not won:
                send_email(Email=os.environ.get("EMAIL_USERNAME"),
                        Password=os.environ.get("EMAIL_PASSWORD"),
                        Subject="YOU'VE LOST IT ALL",
                        Message=f"{check_result['outcome']} {SELECTED_MARKET} did not come till week {LEAGUE['num_of_weeks']}"
                        )
    else:
        # Calculate the number of weeks left before week 10 of the next season
        time_to_sleep = (LEAGUE["num_of_weeks"]-games_to_check+(week_to_save1-1))*3
        delete_cache(browser)
        time.sleep(5)
        terminate_driver_process(browser)
        # browser.quit()
        print(f'waiting for {time_to_sleep*60} secs')
        time.sleep(time_to_sleep*60)



def get_mem_usage():
    return psutil.Process().memory_info().rss // 1024



if __name__=='__main__':

    count=0               #
    que=mp.Queue()         #
    # print(f"start: {get_mem_usage()}")
    while True:
        home_bot=mp.Process(target=start_bot,args=(que,0,count),daemon=True)
        away_bot=mp.Process(target=start_bot,args=(que,1,count),daemon=True)
        home_bot.start()
        away_bot.start()
        # print(f"after thread creation: {get_mem_usage()}")
        home_bot.join()
        away_bot.join()
        count=que.get()
        print(f"this is the current count: {count}")
        # print(f"end of thread: {get_mem_usage()}")
        print('bot terminated')
        # print(threading.active_count())
        # print(f"THREADS: {len(threading.enumerate())}")


