from dotenv import load_dotenv
import imaplib, email, os
import datetime

load_dotenv()
 
 
    

SINCE_DATE="12-Jul-2024"
# SINCE_DATE="14-Jun-2024
# EXCLUDE_DATE="13 Jun 2024"" 
EXCLUDE_DATE="11 Jul 2024"
imap_url = 'imap.gmail.com'
 
# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)
 
# Function to search for a key value pair 
def search(key, value, con):
    # using only SINCE or BEFORE to filter 
    result, data = con.search(None, key, '"{}"'.format(value))
    # using both SINCE and BEFORE to filter
    # result, data = con.search(None,'(SINCE "24-Jun-2024" BEFORE "26-Jun-2024")' )
    
    # result, data = con.search(None,'(SINCE "17-Apr-2024"  )' )
    # result, data = con.search(None,f'(SINCE {SINCE_DATE}  )' )
    # result, data = con.search(None,"ALL" )  #not sure about the all


    return data
 
# Function to get the list of emails under this label
def get_emails(result_bytes):
    msgs = [] # all the email data are pushed inside an array
    count=0
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')

        # create a dictionary so as to sort with date since gmail does not support con.sort()
        msg_object={}
        msg_object_copy={}
        msg=email.message_from_bytes(data[0][1])
        msg_date=""
        for val in msg['Date'].split(' '):
            if(len(val)==1):
                val="0"+val
            # to pad the single date with 0
            msg_date=msg_date+val+" "
        msg_date=msg_date[:-13]
        msg_object['date']= datetime.datetime.strptime(msg_date,"%a, %d %b %Y %H:%M:%S")
    # to convert string to date time object for sorting the list
        msg_object['msg']=msg
        msg_object_copy=msg_object.copy()
        msgs.append(msg_object_copy)
        # count+=1
        # if count==16:
        #     break
    # msgs.sort(reverse=True,key=lambda r:r['date'])
    msgs.sort(reverse=False,key=lambda r:r['date'])
    return msgs


# this is done to make SSL connection with GMAIL
con = imaplib.IMAP4_SSL(imap_url) 
 
# logging the user in
response=con.login(os.environ.get("EMAIL_USERNAME"), os.environ.get("EMAIL_PASSWORD")) 
print(response) 
# calling function to check for email under this label
result=con.select('FullSeason') 
print(result)
 
 # fetching emails from this user "tu**h*****1@gmail.com"
# msgs = get_emails(search('FROM', os.environ.get("EMAIL_USERNAME"), con))

msgs = get_emails(search('SINCE', SINCE_DATE, con))
print(len(msgs))

# for since and before option
# msgs=msgs[:19]  #
# print(len(msgs))  #

from tabulate_data import tabulate_result
# from dotenv import load_dotenv
import pygsheets 
# import os

sheet_name=['FullSeason_SeleniumProject_Spreadsheet','FullSeason_SeleniumProject_Spreadsheet',
            'FullSeason_SeleniumProject_Spreadsheet','SeleniumProject spreadsheet',
            'SeleniumProject spreadsheet','SeleniumProject spreadsheet']


# CELLS=[['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'],
#         ['R','S','T','U','V','W','X','Y','Z','AA',"AB",'AC','AD','AE','AF'],
#         ['AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV'],
#         ['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'],
#         ['R','S','T','U','V','W','X','Y','Z','AA',"AB",'AC','AD','AE','AF'],
#         ['AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV'],]

CELLS=[['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R'],
        ['T','U','V','W','X','Y','Z','AA',"AB",'AC','AD','AE','AF','AG','AH','AI','AJ'],
        ['AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ','BA','BB'],
        ['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R'],
        ['T','U','V','W','X','Y','Z','AA',"AB",'AC','AD','AE','AF','AG','AH','AI','AJ'],
        ['AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ','BA','BB'],]

TYPES=["single","pair","pair","single","single","single"]
client = pygsheets.authorize(service_account_file=os.environ.get("GDRIVE_API_CREDENTIALS"))
for msg in msgs:
    my_msg=msg['msg']
    print(my_msg['date'])
    for part in my_msg.walk():
        # print(part.get_content_type())
        if my_msg['date'][5:16]!=EXCLUDE_DATE:
            if part.get_content_type()=="text/plain":
                content=part.get_payload()

                # new_content=content
                # print(new_content)
                try:
                    new_content=content.replace(" ","")[17:]
                    exec(new_content)
                except SyntaxError:
                    try:
                        new_content=content.replace(" ","")[22:]
                        exec(new_content)
                    except Exception as e:
                        print(f"this is the exec() error: {e} ")

                try:
                    email_date=my_msg['date'][5:16]
                    dictionaries=[FullSeason,FullSeason,Halftime_Fulltime,CS_1_10,CS_11_20,CS_21_30]
                except Exception as e:
                    print(f"this is the dictionary error: {e} ")
                
                for n in range(6):
                    try:
                        tabulate_result(score_dictionary=dictionaries[n],sheet_name=sheet_name[n],cell_list=CELLS[n],type=TYPES[n],client=client,date=email_date)
                    except Exception as e:
                        print(f"this is the tabulate_result error: {e} ")


            



















# from dotenv import load_dotenv
# import imaplib, email, os

# load_dotenv()
 
 
    

 
# imap_url = 'imap.gmail.com'
 
# # Function to get email content part i.e its body part
# def get_body(msg):
#     if msg.is_multipart():
#         return get_body(msg.get_payload(0))
#     else:
#         return msg.get_payload(None, True)
 
# # Function to search for a key value pair 
# def search(key, value, con): 
#     # result, data = con.search(None, key, '"{}"'.format(value))
#     result, data = con.search(None,"ALL")

#     return data
 
# # Function to get the list of emails under this label
# def get_emails(result_bytes):
#     msgs = [] # all the email data are pushed inside an array
#     count=0
#     for num in result_bytes[0].split():
#         typ, data = con.fetch(num, '(RFC822)')
#         msgs.append(data)
#         # count+=1
#         # if count==16:
#         #     break
 
#     return msgs


# # this is done to make SSL connection with GMAIL
# con = imaplib.IMAP4_SSL(imap_url) 
 
# # logging the user in
# response=con.login(os.environ.get("EMAIL_USERNAME"), os.environ.get("EMAIL_PASSWORD")) 
# print(response) 
# # calling function to check for email under this label
# result=con.select('FullSeason') 
# print(result)
 
#  # fetching emails from this user "tu**h*****1@gmail.com"
# msgs = get_emails(search('FROM', os.environ.get("EMAIL_USERNAME"), con))




# for msg in msgs: 
#     for sent in msg[::-1]:
#     # for sent in msg:
#         if type(sent) is tuple: 
#             my_msg=email.message_from_bytes((sent[1]))
#             print(my_msg['subject'])
#             print(my_msg['from'])
#             print(my_msg['date'])
#             for part in my_msg.walk():
#                 # print(part.get_content_type())
#                 if part.get_content_type()=="text/plain":
#                     # print(part.get_payload())
#                     pass





            ## encoding set as utf-8
            # content = str(sent[1], 'utf-8') 
            # data = str(content)
            # print(data)
 
            # # Handling errors related to unicodenecode
            # try: 
            #     indexstart = data.find("ltr")
            #     data2 = data[indexstart + 5: len(data)]
            #     indexend = data2.find("</div>")
 
            #     # printing the required content which we need
            #     # to extract from our email i.e our body
            #     print(data2[0: indexend])
 
            # except UnicodeEncodeError as e:
            #     pass
 