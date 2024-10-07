import time
import os
from brain import CheckPattern
from dotenv import load_dotenv
from tools import set_up_driver_instance,delete_cache
import pygsheets 
import threading
import psutil


load_dotenv()


# TODO: Create a requirements.txt file
# NOTE: start the program at 1.5-2.5mins to the next week play 
# TODO: check for left over find elements using path and try to convert to css selector
# TODO: Test the check_if_current_week_has_played(previous_week_selected) function to see if it works as intended
# TODO: test for time complexity
# TODO: Reformat all modules and code 


SELECTED_MARKET="ht/ft"



# browser=webdriver.Chrome()           # driver instance with User Interface (not headless)
# browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
def start_bot():
    global browser
    LEAGUE={"name":"bundliga","num_of_weeks":34}
    # client = pygsheets.authorize(service_account_file=os.environ.get("GDRIVE_API_CREDENTIALS"))
    client = None
    try:
        browser.get("https://m.betking.com/")
        print("i have lunched")
    except:
        pass
    try:
        pattern=CheckPattern(browser,market=SELECTED_MARKET)
        pattern.checkout_virtual(league=LEAGUE["name"])
    except:
        try:
            browser.get("https://m.betking.com/virtual/league/kings-bundliga")  
        except:
            browser.quit()
            browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
            browser.get("https://m.betking.com/virtual/league/kings-bundliga")

    
    print("i am about to check result")
   
    try:
        check_result=pattern.check_result(length="all result", latest_week="all",client=client)
        browser=check_result['driver']
    except:
        print("An error occured i skipped check_result(all result)")
        check_result={'outcome':True}

    delete_cache(browser)
    time.sleep(2)
    # browser.quit()

def get_mem_usage():
    return psutil.Process().memory_info().rss // 1024

if __name__=='__main__':

    count=0               #
    browser=set_up_driver_instance()       # driver instance without User Interface (--headless)
    print(f"start: {get_mem_usage()}")
    while True:
        # bot=mp.Process(target=start_bot,args=(count,),daemon=True)
        bot=threading.Thread(target=start_bot,daemon=True)
        bot.start()
        print(f"after thread creation: {get_mem_usage()}")
        bot.join()
        # bot.terminate()
        print('bot terminated')
        print(f"end of thread: {get_mem_usage()}")