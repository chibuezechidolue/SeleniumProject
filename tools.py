import codecs
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException,NoSuchElementException,TimeoutException
from selenium import webdriver





def set_up_driver_instance():
    """ To create and return a webdriver object with disabled gpu and headless"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)

def check_if_last_result_equal_input(browser:object,game_weeks:list,week_to_check:str,time_delay:float)->list:   #updated game weeks
    """ To check if the current last result is the same with the week_to_check 
    input variable, then return an updated game_weeks """
   
    last_result_week=game_weeks[0]
    while last_result_week!=week_to_check:
        print(last_result_week,week_to_check)
        time.sleep(time_delay)
        reload_result_page(browser)
        time.sleep(2)
        game_weeks=[week.text for week in browser.find_elements(By.CSS_SELECTOR,".week-number")]
        last_result_week=game_weeks[0]
    return game_weeks


def reload_result_page(browser):
    """ To cancel and reload result page inorder to reflect new changes to the result"""
    wait=WebDriverWait(driver=browser,timeout=10)

    cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
    cancel_result_page_button.click()
    time.sleep(2)
    standings_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
    standings_button.click()
    time.sleep(1)
    result_button=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")))
    result_button.click()
    time.sleep(3)


def cancel_popup(browser):
    """To cancel popup at the landing page"""
    wait=WebDriverWait(driver=browser,timeout=10)
    body=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body")))
    body.click()
    cancel_body=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[title="Close"]')))
    cancel_body.click()


def save_page(browser,page_name:str):
    """To save the content of a page by writing the content of the page to a given file path"""
    with codecs.open(page_name, 'w', "utf−8") as file:
            file.truncate(0)                        # clear the existing content of the file
            page_content=browser.page_source        # get the content of the current page
            file.write(page_content)                # write the content of the current page to the file 

def confirm_outcome(ht_scores:list,ft_scores:list,game_weeks:list,market:str)->list:
    """To check the result for the presence or possible presence of an intended or staked outcome"""
    count=0
    message=""
    outcome=None
    for n in range(len(ht_scores)):
        
        ht_home_score=int(ht_scores[n][0])
        ht_away_score=int(ht_scores[n][4])

        ft_home_score=int(ft_scores[n][0])
        ft_away_score=int(ft_scores[n][4])
        current_week=n//9                                                      # the number of the game by 9(total games/week), i.e 54//9 will be week 6
        week_number=game_weeks[current_week]

        # use a try and except block to check the passed in bal and the current on screen bal
        if market=="ht/ft":
            if (ht_home_score>ht_away_score and ft_home_score<ft_away_score or     # 2/1
                ht_home_score<ht_away_score and ft_home_score>ft_away_score):     # 1/2
                count+=1
                outcome=True
                message+=f"{week_number}, "
        elif market=="3-3":
            if ft_home_score==3 and ft_away_score==3:
                count+=1
                outcome=True
                message+=f"{week_number}, "

        
    message+=f"({market} appeeared {count} time(s)) "
    print(message)
    return {"outcome":outcome,"count":count,"message":message}
            



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
        live_match=browser.find_element(By.CSS_SELECTOR,'[data-testid="in-play-match-index"]')
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
       clear_all_button= browser.find_element(By.CSS_SELECTOR,'.clear-all')
    except (TimeoutException,NoSuchElementException):
        betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')))
        betslip_button.click()
        time.sleep(1)
    try:
        clear_all_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.clear-all')))
        # clear_all_button=browser.find_element(By.CSS_SELECTOR,'.clear-all')
        clear_all_button.click()
    except (TimeoutException,NoSuchElementException):
        pass
    time.sleep(1)
    close_betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')))
    close_betslip_button.click()
    time.sleep(2)