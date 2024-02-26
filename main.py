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
SELECTED_MARKET="ht/ft"
PLAY_OPTION="2/1"

if SELECTED_MARKET=="ht/ft":
    AMOUNT_LIST=(10,10,10,20,30,40,55,80,110,160,230,330,470,675,970,
                1390,1980,2840,4050,5800,8300,11850,16950,24250)
    MAX_AMOUNT_LENGTH=14
elif SELECTED_MARKET=="3-3":
    AMOUNT_LIST=(10,10,10,10,10,10,20,20,30,30,40,40,55,55,80,80,110,
                 110,160,160,230,230,330,330,470,470,675,675,970,970,
                 1390,1390,1980,1980)
    MAX_AMOUNT_LENGTH=20
    TOTAL_AMOUNT=9450
LEAGUE={"name":"bundliga","num_of_weeks":34}
    
MAX_SEASON=5

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
    won=False
    for n in range(1,MAX_SEASON+1):
        pattern=CheckPattern(browser,market=SELECTED_MARKET)
        try:
            check_result=pattern.check_result(length="all result", latest_week="all")
            browser=check_result['driver']
        except:
            print("An error occured, I skipped check_result(all result)")
            check_result={'outcome':True}
        time.sleep(180)    # To delay till week 11
        if check_result['outcome']:
            won=True
            break
        if n<MAX_SEASON:
            print(f"SEASON {n} result has been CHECKED, waiting for next SEASON ")
            send_email(Email=os.environ.get("EMAIL_USERNAME"),
                    Password=os.environ.get("EMAIL_PASSWORD"),
                    Subject=f"21st - 30th Week Results",
                    Message=f"3-3= 0 | 1/2= 0 | 2/1= 0 times(s) ",
                    File_path=[check_result["page_path"]]
                    )
        
        
    if not won:        
        print(f"{SELECTED_MARKET} did not come till week {LEAGUE['num_of_weeks']}")
        send_email(Email=os.environ.get("EMAIL_USERNAME"),
                    Password=os.environ.get("EMAIL_PASSWORD"),
                    Subject="YOU'VE LOST IT ALL",
                    Message=f"{SELECTED_MARKET} did not come till SEASON {MAX_SEASON}"
                    )
    browser.quit()
        
    

