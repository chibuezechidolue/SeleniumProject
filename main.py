import time
from brain import LoginUser,CheckPattern,PlayGame
import os
from dotenv import load_dotenv

load_dotenv()

SELECTED_MARKET="ht/ft"


pattern=CheckPattern(market=SELECTED_MARKET)
pattern.checkout_virtual()
pattern.check_result()

game_play=PlayGame(market=SELECTED_MARKET)
time.sleep(4)
game_play.choose_market()
time.sleep(10)
log=LoginUser(username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
log.login()


