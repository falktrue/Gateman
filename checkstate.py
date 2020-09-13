from requests import Session
from bs4 import BeautifulSoup as bs
import os, ssl
import re
import csv

# USER input
print("Lembrando: também aceitamos múltiplos inputs, separados por vírgula.")
ssd_Numba = str(input("Entre com o número(s) da SSD: "))
ssd_List = ssd_Numba.split(", ")
print(ssd_List)
print("\nTrying 'PORTAL SSD'...")
print("Sit down and have a seat, as the server is probably a Super Nintendo.\n")

# Disables the fucking warning for SSL certificate expiry
# Thanks Lugarinho
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Portal Session transaction
with Session() as s:
    i = 1
    w = 0
    status_List = []
    warning_List = []
    login_data = {"__LASTFOCUS":"","__EVENTTARGET":"","__EVENTARGUMENT":"","__VIEWSTATE":"/wEPDwUKLTU5MjQ5OTk4NGRklgfWV8P76+KyxeCbi6We6zq2M3o=","__VIEWSTATEGENERATOR":"393CE8FD","LoginControl1$UserName":"93222702","LoginControl1$Password":"Falk@033","LoginControl1$LoginButton":"Entrar"}
    s.post("https://10.129.198.33/nsed/login.aspx", login_data, verify=False)

    for x in range(len(ssd_List)):
        ssd_Url=("https://10.129.198.33/nsed/redes/ssd/ssdview.aspx?id=" + ssd_List[x])
        ssd_page = s.get(ssd_Url)
        soup = bs(ssd_page.text, "html.parser")
        table = soup.find("table", id="ctl00_ContentPlaceHolder1_gvSubs")

        # To be used when I wanna run offline tests
        # with open(r"D:\samba\page.txt", "w") as o:
        #     print(table, file=o)

        for row in table.find_all("tr"):
            # rows A and B count sub-SSDs
            row_A = table.findAll('tr', attrs={'class': 'gvRowStyle'})
            row_B = table.findAll('tr', attrs={'class': 'gvAlternatingRow'})
            cols = row.find_all("td")
            cols = [ele.get_text(strip=True, separator=" ") for ele in cols]
            status_List.append(' ;'.join(cols))  
            w = len(row_A) + len(row_B)
        warn = soup.find_all('div', class_="warningbar2")
        if len(warn) > 0:
            for x in range (len(warn)):
                warning_List.append(warn[x].get_text().strip())
        else:
            for x in range (w):
                warning_List.append("No Warnings.")
        
        print("Item # " + str(i) + " GET.")
        i = i + 1
        w = 0

    status_List = list(filter(None,status_List))

    # Show time
    with open(r'D:\samba\ssdstate.csv', "w") as o:
        print(r'Sub-SSD;Assunto;Status;CRQ;Prazo;Warnings', file=o)
        for a,b in zip(status_List,warning_List):
            print (a + ';' + b, file=o)
    
    print("\nFetching completed.\n")
