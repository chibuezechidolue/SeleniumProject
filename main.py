import time
from brain import LoginUser,CheckPattern


pattern=CheckPattern(market="3-3")
pattern.checkout_virtual()
pattern.check_result()
time.sleep(10)
# log=LoginUser(username=os.environ.get("BETKING_USERNAME"),password=os.environ.get("BETKING_PASSWORD"))
# log.login()


