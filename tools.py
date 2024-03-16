import codecs
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException,NoSuchElementException,TimeoutException
from selenium import webdriver
import pygsheets 
import datetime
from dotenv import load_dotenv
import os

load_dotenv()





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
   
    if week_to_check=="Week 0":
        return game_weeks
    last_result_week=game_weeks[0].text
    while last_result_week!=week_to_check:
        print(last_result_week,week_to_check)
        time.sleep(time_delay)
        reload_result_page(browser)
        time.sleep(2)
        for _ in range(3):
            game_weeks=browser.find_elements(By.CSS_SELECTOR,".week-number")
            if game_weeks!=[]:
                break
            reload_result_page(browser)
            time.sleep(2)
        last_result_week=game_weeks[0].text
    return game_weeks

def check_if_last_stake_has_played(browser:object,week_to_check:str,time_delay:float):
    week_to_select = browser.find_elements(By.CSS_SELECTOR, '.week')
    print(week_to_select[0].text,week_to_check)
    while week_to_select[0].text==week_to_check:
        print(week_to_select[0].text,week_to_check)
        time.sleep(time_delay)
        week_to_select = browser.find_elements(By.CSS_SELECTOR, '.week')
    return True


def reload_result_page(browser):
    """ To cancel and reload result page inorder to reflect new changes to the result"""
    wait=WebDriverWait(driver=browser,timeout=10)

    try:
        betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
        betslip_button.click()
        time.sleep(2)
        close_betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')
        close_betslip_button.click()
        time.sleep(3)

    except:

        # cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
        cancel_result_page_button=browser.find_element(By.CSS_SELECTOR,"svg path")
        cancel_result_page_button.click()
        time.sleep(2)
        # standings_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"span.view-switch-icon")))
        standings_button=browser.find_element(By.CSS_SELECTOR,"span.view-switch-icon")
        standings_button.click()
        time.sleep(1)
        # result_button=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")))
        result_button=browser.find_element(By.XPATH,"/html/body/app-root/app-wrapper/div/virtuals-league-wrapper/mobile-virtuals-soccer/mvs-virtual-league-page/div[2]/mvs-results-page/div[2]/div[2]")
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

def tabulate_result(score_dictionary,sheet_name,cell_list,type):
    """To transfer and tabulate the score_dictory to an online google sheet"""
    
    client = pygsheets.authorize(service_account_file=os.environ.get("GDRIVE_API_CREDENTIALS"))
    
    # print(client.spreadsheet_titles()) 
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
    for k,v in score_dictionary.items():
        if type=="pair":
            if k=="3 - 3":
                pass
            elif v==0 and score_dictionary[k[::-1]]==0:
                current_value=worksht.get_value(addr=f"{cell_list[n]}{col_num}")
                if current_value== "":
                    val_to_update=1
                else:
                    val_to_update=str(int(current_value)+1)
                worksht.update_value(addr=f"{cell_list[n]}{col_num}", val=val_to_update, parse=None)
        elif type=="single": 
            if v==0:
                current_value=worksht.get_value(addr=f"{cell_list[n]}{col_num}")
                if current_value== "":
                    val_to_update=1
                else:
                    val_to_update=str(int(current_value)+1)
                worksht.update_value(addr=f"{cell_list[n]}{col_num}", val=val_to_update, parse=None)   
        
        n+=1

def confirm_outcome(ht_scores:list,ft_scores:list,game_weeks:list,market:str)->list:
    """To check the result for the presence or possible presence of an intended or staked outcome"""
    message=""
    outcome=None
    score_dict={'4 - 1':0, "1 - 4":0, "4 - 2":0, "2 - 4":0, "5 - 0":0, "0 - 5":0, "5 - 1":0, "1 - 5":0, 
                "6 - 0":0, "0 - 6":0, "3 - 3":0, "2/1":0, "1/2":0}
    
    hf_ft_score_dict={'4 - 1':0, "1 - 4":0, "4 - 2":0, "2 - 4":0, "5 - 0":0, "0 - 5":0, "5 - 1":0, "1 - 5":0, 
                "6 - 0":0, "0 - 6":0, "3 - 3":0, "2/1":0, "1/2":0}
    hf_ft_range=20

    cs_1_10_dict={'4 - 1':0, "1 - 4":0, "4 - 2":0, "2 - 4":0, "5 - 0":0, "0 - 5":0, "5 - 1":0, "1 - 5":0, 
                "6 - 0":0, "0 - 6":0, "3 - 3":0, "2/1":0, "1/2":0}
    cs_1_10_range=10

    cs_11_20_dict={'4 - 1':0, "1 - 4":0, "4 - 2":0, "2 - 4":0, "5 - 0":0, "0 - 5":0, "5 - 1":0, "1 - 5":0, 
                "6 - 0":0, "0 - 6":0, "3 - 3":0, "2/1":0, "1/2":0}
    cs_11_20_range=20

    cs_21_30_dict={'4 - 1':0, "1 - 4":0, "4 - 2":0, "2 - 4":0, "5 - 0":0, "0 - 5":0, "5 - 1":0, "1 - 5":0, 
                "6 - 0":0, "0 - 6":0, "3 - 3":0, "2/1":0, "1/2":0}
    cs_21_30_range=30

    for n in range(1,len(ft_scores)+1):
        
        ht_home_score=int(ht_scores[n][0])
        ht_away_score=int(ht_scores[n][4])
        ft_home_score=int(ft_scores[n][0])
        ft_away_score=int(ft_scores[n][4])
        # current_week=n//9                                                      # the number of the game by 9(total games/week), i.e 54//9 will be week 6
        # week_number=game_weeks[current_week]

        current_ft_score=ft_scores[n]

        if current_ft_score in score_dict:
            score_dict[current_ft_score]+=1
            if n<=9*hf_ft_range:
                hf_ft_score_dict[current_ft_score]+=1

            if n<=9*cs_1_10_range:
                cs_1_10_dict[current_ft_score]+=1

            if n>9*cs_1_10_range and n<=9*cs_11_20_range:
                cs_11_20_dict[current_ft_score]+=1

            if n>9*cs_11_20_range and n<=9*cs_21_30_range:
                cs_21_30_dict[current_ft_score]+=1
            # message+=f"{current_ft_score}: {week_number}, "
        if (ht_home_score>ht_away_score and ft_home_score<ft_away_score):     # 1/2
            score_dict["1/2"]+=1
            if n<9*hf_ft_range:
                hf_ft_score_dict["1/2"]+=1
            # message+=f"1/2: {week_number}, "
        elif (ht_home_score<ht_away_score and ft_home_score>ft_away_score):     # 2/1
            score_dict["2/1"]+=1
            if n<9*hf_ft_range:
                hf_ft_score_dict["2/1"]+=1
        
    message+=f"FullSeason = {score_dict} | Halftime/Fulltime = {hf_ft_score_dict} | 
    CS_1-10 = {cs_1_10_dict} | CS_11-20 = {cs_11_20_dict} | CS_21-30 = {cs_21_30_dict} "
    sheet_name=['FullSeason_SeleniumProject_Spreadsheet','FullSeason_SeleniumProject_Spreadsheet',
                'FullSeason_SeleniumProject_Spreadsheet','SeleniumProject spreadsheet',
                'SeleniumProject spreadsheet','SeleniumProject spreadsheet']
    
    dictionaries=[score_dict,score_dict,hf_ft_score_dict,cs_1_10_dict,cs_11_20_dict,cs_21_30_dict]

    CELLS=[['B','C','D','E','F','G','H','I','J','K','L','M','N'],
           ['P','Q','R','S','T','U','V','W','X','Y','Z','AA',"AB"],
           ['AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP'],
           ['B','C','D','E','F','G','H','I','J','K','L','M','N'],
           ['P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB'],
           ['AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP']]
    
    TYPES=["single","pair","pair","single","single","single"]

    for n in range(6):
        try:
            tabulate_result(score_dictionary=dictionaries[n],sheet_name=sheet_name[n],cell_list=CELLS[n],type=TYPES[n])
        except:
            pass
    print(message)
    return {"outcome":outcome,"message":message}
            



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
        # betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')))
        betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="nav-bar-betslip"]')
        betslip_button.click()
        time.sleep(1)
    try:
        # clear_all_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.clear-all')))
        clear_all_button=browser.find_element(By.CSS_SELECTOR,'.clear-all')
        clear_all_button.click()
    except (TimeoutException,NoSuchElementException):
        pass
    time.sleep(1)
    # close_betslip_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')))
    close_betslip_button=browser.find_element(By.CSS_SELECTOR,'[data-testid="coupon-close-icon"]')
    close_betslip_button.click()
    time.sleep(2)

