import datetime

def tabulate_result(score_dictionary,sheet_name,cell_list,type,client,date):
    """To transfer and tabulate the score_dictory to an online google sheet"""
    
    
    # print(client.spreadsheet_titles()) 
    spreadsht = client.open(sheet_name) 

    worksht = spreadsht.worksheet("title", "Sheet1") 

    # today=datetime.datetime.now().date().strftime("%d/%m")
    today=date
    # print(today)
    col=worksht.get_col(col=1)[3:]
    pattern=worksht.find(today)
    if pattern==[]:
        col_num=col.index("")+4
        worksht.cell(f"A{col_num}").value=today 
        # print(pattern)


    else:
        col_num=pattern[0].row
    # print(f"This is the column num: {col_num}")
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





