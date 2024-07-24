import codecs
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (StaleElementReferenceException,NoSuchElementException,
                                        TimeoutException,ElementClickInterceptedException)
from selenium import webdriver
import pygsheets 
import datetime
from dotenv import load_dotenv
import threading
import os,psutil

load_dotenv()



def set_up_driver_instance():
    """ To create and return a webdriver object with disabled gpu and headless"""

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'

    chrome_options = webdriver.ChromeOptions()  # Google Chrome 
    # chrome_options = webdriver.EdgeOptions()      # Microsoft Edge 
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--log-level=3') # to stop printing error messages to the console 
    chrome_options.add_argument("start-maximized") # chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--disable-extensions')
    
    # prefs={'profile.default_content_setting_values': {'images': 2, 'javascript': 2}}
    # prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.javascript": 2}
    prefs = {'profile.default_content_setting_values': {'images': 2, "stylesheet":2,
                            'plugins': 2, 'popups': 2, 'geolocation': 2, 
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}}
    # chrome_options.add_experimental_option('prefs', prefs)

    # chrome_options.add_argument("--disable-blink-features")
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument('disable-infobars')


    #emulate a mobile device
    # mobile_emulation = { "deviceName": "Nexus 5" }
#     mobile_emulation = {
#    "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
#    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
#    "clientHints": {"platform": "Android", "mobile": True} }
#     chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

                    # To rotate the user agent in order to avoid detection
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    # print(driver.execute_script("return navigator.userAgent;"))
    
    return webdriver.Chrome(options=chrome_options)   # Google Chrome
    # return webdriver.Edge(options=chrome_options)       # Microsoft Edge

def check_if_last_result_equal_input(browser:object,game_weeks:list,week_to_check:str,time_delay:float)->list:   #updated game weeks
    """ To check if the current last result is the same with the week_to_check 
    input variable, then return an updated game_weeks """
   
    if week_to_check=="Week 0":
        return game_weeks
    last_result_week=game_weeks[0].text
    print(last_result_week,week_to_check)
    while last_result_week!=week_to_check:
        #print(last_result_week,week_to_check)
        time.sleep(time_delay)
        reload_result_page(browser)
        time.sleep(2)
        for _ in range(3):
            game_weeks[:]=browser.find_elements(By.CSS_SELECTOR,".week-number")
            if game_weeks!=[]:
                break
            reload_result_page(browser)
            time.sleep(2)
        last_result_week=game_weeks[0].text
    print(last_result_week,week_to_check)
    return game_weeks

def check_if_last_stake_has_played(browser:object,week_to_check:str,time_delay:float):
    week_to_select = browser.find_elements(By.CSS_SELECTOR, '.week')
    print(week_to_select[0].text,week_to_check)
    while week_to_select[0].text==week_to_check:
        time.sleep(time_delay)
        week_to_select[:] = browser.find_elements(By.CSS_SELECTOR, '.week')
    print(week_to_select[0].text,week_to_check)    
    return True


def reload_result_page(browser):
    """ To cancel and reload result page inorder to reflect new changes to the result"""
    wait=WebDriverWait(driver=browser,timeout=10)

    try:
        betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
        betslip_button.click()
        time.sleep(0.5)
        close_betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')
        close_betslip_button.click()
        time.sleep(0.5)

    except:

        # cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
        cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
        cancel_result_page_button.click()
        time.sleep(0.5)
        # standings_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
        standings_button=browser.find_element(By.CSS_SELECTOR,"span.view-switch-icon")
        standings_button.click()
        time.sleep(0.5)
        result_button = browser.find_elements(By.CSS_SELECTOR,'[data-testid="results-page-tab-standings"]')
        # result_button=browser.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")
        result_button[1].click()
        time.sleep(1)


def cancel_popup(browser):
    """To cancel popup at the landing page"""
    wait=WebDriverWait(driver=browser,timeout=10)
    body=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body")))
    body.click()
    cancel_body=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="btn-close-header"]')))
    cancel_body.click()


def save_page(browser,page_name:str):
    """To save the content of a page by writing the content of the page to a given file path"""
    with codecs.open(page_name, 'w', "utf−8") as file:
            file.truncate(0)                        # clear the existing content of the file
            page_content=browser.page_source        # get the content of the current page
            file.write(page_content)                # write the content of the current page to the file 

def tabulate_result(score_dictionary,sheet_name,cell_list):
    """To transfer and tabulate the score_dictory to an online google sheet"""
    
    client = pygsheets.authorize(service_account_file=os.environ.get("GDRIVE_API_CREDENTIALS"))
    
    spreadsht = client.open(sheet_name) 

    worksht = spreadsht.worksheet("title", "Sheet1") 

    today=datetime.datetime.now().date().strftime("%d/%m")
    print(today)
    col=worksht.get_col(col=1)[3:]
    pattern=worksht.find(today)
    if pattern==[]:
        col_num=col.index("")+4
        worksht.cell(f"A{col_num}").value=today 

    else:
        col_num=pattern[0].row
    print(f"This is the column num: {col_num}")
    n=0
    failed_scores=["3 - 3", "5 - 0", "0 - 5", "6 - 0", "0 - 6" ]
    for k,v in score_dictionary.items():
        if k in failed_scores:
            pass
        elif v==0 and score_dictionary[k[::-1]]==0:    
            current_value=worksht.get_value(addr=f"{cell_list[n]}{col_num}")
            if current_value== "":
                val_to_update=1
            else:
                val_to_update=str(int(current_value)+1)
            worksht.update_value(addr=f"{cell_list[n]}{col_num}", val=val_to_update, parse=None)
        n+=1


def confirm_outcome(ht_scores:list,ft_scores:list,game_weeks:list,market:str,length:str)->list:
    """To check the result for the presence or possible presence of an intended or staked outcome"""
    count=0
    message=""
    score_dict={"3 - 2":0, "2 - 3":0,'4 - 0':0, "0 - 4":0,'4 - 1':0, "1 - 4":0, "2/1":0, "1/2":0}
    for n in range(len(ht_scores)):
        try:
            ht_home_score=int(ht_scores[n].text[0])
            ht_away_score=int(ht_scores[n].text[4])

            ft_home_score=int(ft_scores[n].text[0])
            ft_away_score=int(ft_scores[n].text[4])
            current_ft_score=ft_scores[n].text

            current_week=n//9                                                      # the number of the game by 9(total games/week), i.e 54//9 will be week 6
            week_number=game_weeks[current_week].text
        except AttributeError:
            ht_home_score=int(ht_scores[n][0])
            ht_away_score=int(ht_scores[n][4])

            ft_home_score=int(ft_scores[n][0])
            ft_away_score=int(ft_scores[n][4])
            current_ft_score=ft_scores[n]

            current_week=n//9                                                      # the number of the game by 9(total games/week), i.e 54//9 will be week 6
            week_number=game_weeks[current_week]

        # use a try and except block to check the passed in bal and the current on screen bal
        if current_ft_score in score_dict:
            score_dict[current_ft_score]+=1

        if (ht_home_score>ht_away_score and ft_home_score<ft_away_score):     # 1/2
            score_dict["1/2"]+=1
            count+=1

        elif (ht_home_score<ht_away_score and ft_home_score>ft_away_score):     # 2/1
            score_dict["2/1"]+=1
            count+=1
    if length.lower()=="all result":
        for k,v in score_dict.items():
            if k=="3 - 2" or k=="2 - 3":
                if v==0:
                    message+=f"({k} appeeared {v} time(s)) "
                    return {"outcome":k,"message":message}
            if v==0 and score_dict[k[::-1]]==0:
                message+=f"({k} & {k[::-1]} appeeared {v+score_dict[k[::-1]]} time(s)) "
                message+=str(score_dict)
                return {"outcome":k,"message":message}
        
        message+=f"(no pattern appeeared this season) "
        message+=str(score_dict)
        print(message)
        return {"outcome":"","message":message}
    elif length.lower()=="last result":
        if market=="3 - 2" or market=="2 - 3":
            if score_dict[market]>0:
                message+=f"({market} appeeared {score_dict[market]} time(s)) "
                message+=str(score_dict)
                print(message)
                return {"outcome":True,"message":message}
            else: 
                return {"outcome":False,"message":f"{market} did not appear"} 
            
        else:
            if score_dict[market]>0 or score_dict[market[::-1]]>0:
                message+=f"({market} or {market[::-1]} appeeared {score_dict[market]+score_dict[market[::-1]]} time(s)) "
                message+=str(score_dict)
                print(message)
                return {"outcome":True,"message":message}
            else: 
                return {"outcome":False,"message":f"{market} did not appear"} 


            



import smtplib
from email.mime.multipart import MIMEMultipart               #
from email.mime.text import MIMEText                         # Necessary imports inorder to attach a file(page)
from email.mime.base import MIMEBase                         #
from email import encoders                                   #

def send_email(Email:str,Password:str,Message:str,Subject:str,File_path:list=[]):
    """To send an email attached with the screenshoot(s) of a page(specifically the result page)"""
    msg=MIMEMultipart()
    msg['From'] = Email
    msg['To'] = Email
    msg['Subject'] = Subject
    body = Message
    msg.attach(MIMEText(body, 'plain'))

    for n in range(len(File_path)):
        with open(File_path[n], "rb") as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read()) 
            encoders.encode_base64(p) 
            p.add_header('Content-Disposition', f"attachment; filename= {File_path[n].split('/')[-1]}")
            msg.attach(p)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com') as connection:
            connection.login(user=Email, password=Password)
            connection.sendmail(from_addr=Email,
                                to_addrs = Email,
                                msg = msg.as_string()
                                )
    except:
        pass

def reduce_week_selected(week_selected:str,by:int,league:str)->str:
    """To reduce the week which the staking options has been selected while waiting for last staked result"""
    if league=="bundliga":
        last_week="34"
    else:
        last_week="38"
    var_list=week_selected.split(" ") # To split the string(Week_selected)
    num=str(int(var_list[1])-by)      # Convert number part to int, then reduce by(-by), then covert back to str()
    if len(num)==1 and num=='0':
        output=var_list[0]+" "+last_week    # To change the output back to 34(which is the last week for bundesliga) Since week 1 - by = 0  
    else:
        output=var_list[0]+" "+num
    return output

def check_if_current_week_islive(browser)->bool:
    """ To check if next week to play has started play"""
    try:
        # live_match=browser.find_element(By.CSS_SELECTOR,'[data-testid="in-play-match"]')
        live_match=browser.find_element(By.CSS_SELECTOR,'[data-testid="in-play-results"]')
        live_match=True
    except (StaleElementReferenceException, NoSuchElementException):
        live_match=False
    
    return live_match
    

def check_if_current_week_has_played(browser,previous_week_selected:str)->bool:
    """ To check if next week to play has started play """
    var_list=previous_week_selected.split(" ")
    output=f"{var_list[0].lower()}-{var_list[1]}"
    try:
        played=browser.find_element(By.CSS_SELECTOR,f'[data-testid={output}]')
        played=False
    except (StaleElementReferenceException, NoSuchElementException):
        played=True

    return played


def clear_bet_slip(browser):
    wait=WebDriverWait(driver=browser,timeout=10)
    try:
        try:
            clear_all_button= browser.find_element(By.CSS_SELECTOR,'.clear-all')
            clear_all_button.click()
        except (TimeoutException,NoSuchElementException):
            # betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')))
            # betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
            # betslip_button.click()
            # time.sleep(1)
            pass
        try:
            # clear_all_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.clear-all')))
            clear_all_button=browser.find_element(By.CSS_SELECTOR,'.clear-all')
            clear_all_button.click()
        except (TimeoutException,NoSuchElementException):
            pass
        except ElementClickInterceptedException:
            browser.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            clear_all_button=browser.find_element(By.CSS_SELECTOR,'.clear-all')
            clear_all_button.click()
        # time.sleep(2)
        # close_betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')))
        try:
            close_betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')
            close_betslip_button.click()
        except:
            continue_betting_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-continue-betting"]')
            continue_betting_button.click  
        time.sleep(1)
    except:
        pass
import math
def calc_stake_amount(amount:float,odd:float,base:int=60)->float:
    if odd<10:
        return 50
    expected_sum=amount*base
    possible_stake=math.ceil(expected_sum/odd)
    if possible_stake<50:
        possible_stake=50
    return possible_stake

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def delete_cache(driver):
    driver.execute_cdp_cmd('Storage.clearDataForOrigin', {
    "origin": '*',
    "storageTypes": 'all',
    })
    time.sleep(2)
    driver.delete_all_cookies()
    time.sleep(2)
    driver.get('chrome://settings/clearBrowserData')  # Open your chrome settings.
    time.sleep(2)
    actions = ActionChains(driver) 
    actions.send_keys(Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 7 + Keys.ENTER) # Google Chrome 
    # actions.send_keys(Keys.TAB * 2 + Keys.DOWN * 4 + Keys.TAB * 9 + Keys.ENTER) # Microsoft Edge  
    actions.perform()


class MyCustomThread(threading.Thread):
    # def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: codecs.Iterable[codecs.Any] = ..., kwargs: threading.Mapping[str, codecs.Any] | None = None, *, daemon: bool | None = None) -> None:
    #     super().__init__(group, target, name, args, kwargs, daemon=daemon)
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None,daemon=bool):
        threading.Thread.__init__(self, group, target, name, args, kwargs,daemon=daemon)
        self._return = None

    def run(self):
        self.error = None
        if self._target is not None:
            try:
                self._return = self._target(*self._args, **self._kwargs)
            except BaseException as e:
                self.error=e

    # def check_error(self):
    #     if self.exc:
    #         raise self.exc
        
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return
    

def terminate_driver_process():
    process_name="chrome.exe"
    # process_name="msedge.exe"
    try:
        os.system(f"taskkill /f /t /im {process_name}")   # Windows OS
        # os.system(f"kilall {process_name}")   # Linux OS

                            # OR

        # for process in psutil.process_iter():
        #     if process.name().lower() == process_name.lower():
        #         print(process.name())
        #         process.kill()

    except:
        pass