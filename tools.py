from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import codecs


browser=webdriver.Chrome()
browser.get("https://m.betking.com/")

wait=WebDriverWait(driver=browser,timeout=15)
def cancel_popup():
    CANCEL_SIGNUP_BUTTON="/html/body/app-root/app-wrapper/div/app-registration/registration-split/div/app-breadcrumb/div/div/span"
    body=wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body")))
    body.click()
    cancel_body=wait.until(EC.element_to_be_clickable((By.XPATH,CANCEL_SIGNUP_BUTTON)))
    cancel_body.click()


def save_page(page_name):
    with codecs.open(page_name, 'w', "utf−8") as file:
            file.truncate(0)
            page_content=browser.page_source
            file.write(page_content)

def confirm_outcome(ht_scores,ft_scores,game_weeks):
    count=0
    message=""
    outcome=None
    for n in range(len(ht_scores)):
        ht_home_score=int(ht_scores[n].text[0])
        ht_away_score=int(ht_scores[n].text[4])

        ft_home_score=int(ft_scores[n].text[0])
        ft_away_score=int(ft_scores[n].text[4])
        current_week=n//9
        week_number=game_weeks[current_week].text

        if ht_home_score>ht_away_score and ft_home_score<ft_away_score or ht_home_score<ht_away_score and ft_home_score>ft_away_score:
            count+=1
            outcome=True
            message+=f"{week_number}, "
    return {"outcome":outcome,"count":count,"message":message}
            



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(Email,Password,Message,Subject,File_path):
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

    with smtplib.SMTP_SSL('smtp.gmail.com') as connection:
        connection.login(user=Email, password=Password)
        connection.sendmail(from_addr=Email,
                            to_addrs = Email,
                            msg = msg.as_string()
                            )
     
