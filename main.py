import time
from brain import LoginUser,CheckPattern,PlayGame
import os
from dotenv import load_dotenv

load_dotenv()

GAME_LEVEL=1
SELECTED_MARKET="ht/ft"
AMOUNT_LIST=[10,10,10,20,30,40,55,80,110,160,230,330,470,675,970]


pattern=CheckPattern(market=SELECTED_MARKET)
pattern.checkout_virtual()
if not pattern.check_result(length="all result"):
    log=LoginUser(username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
    log.login()

    game_play=PlayGame(market=SELECTED_MARKET)
    time.sleep(6)
    game_play.choose_market()
    time.sleep(1)
    for n in range(len(AMOUNT_LIST[:1])):
        game_play.select_stake_options()
        game_play.place_the_bet(amount=str(AMOUNT_LIST[n]*GAME_LEVEL))
    
        if pattern.check_result(length="last result"):
            break
        # NOTE: continue from check_result tomorrow




