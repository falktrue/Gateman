from requests import Session
from bs4 import BeautifulSoup as bs
import os, ssl
import re
import csv

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

with Session() as s:
    login_data = {"__LASTFOCUS":"","__EVENTTARGET":"","__EVENTARGUMENT":"","__VIEWSTATE":"/wEPDwUKLTU5MjQ5OTk4NGRklgfWV8P76+KyxeCbi6We6zq2M3o=","__VIEWSTATEGENERATOR":"393CE8FD","LoginControl1$UserName":"93222702","LoginControl1$Password":"Falk@033","LoginControl1$LoginButton":"Entrar"}
    s.post("https://10.129.198.33/nsed/login.aspx", login_data, verify=False)
    ssd_page = s.get("https://10.129.198.33/nsed/redes/ssd/ssdview.aspx?id=412284")
    soup = bs(ssd_page.text, "html.parser")
    table = soup.find("table", id="gv1")
    row_data = []
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        cols = [ele.get_text(strip=True, separator=" ") for ele in cols]
        row_data.append(' '.join(cols))
    print("\nFetching completed.\n")

# Regex madness
RE_subnet = r"(?<=Sub-rede )[^ ]*"
RE_description = r"(?<=Descrição: ).+?(?= D)"
RE_vlan = r"(?<=Vlan: )[^ ]*"
RE_gateway = r"(?<=Gateway: )[^ ]*"
relevant_vrf = re.compile(r"(\bLi\b|S1-U|SIG|SGI_VoLTE|AAA|S11|S5|SGI|APN-UNICA|ORION|External|Public|CIMC|Management|Mgmt|O&M|Local|SRP|LTE$)", re.IGNORECASE)

# Dropping some goodies
Parse_ip = []
Parse_desc = []
Parse_vlan = []
Interim_gw = []
Lo_check = []
Parse_gateway = []

# Derives from the 3 above
# Don't really exist, per se
Parse_netmask = []
Parse_vrf = []

with open(r'D:\samba\test.txt', "w", encoding="utf_8_sig") as o:
    for a in row_data:
        print (a, file=o)

with open(r'D:\samba\test.txt', encoding="utf_8_sig") as myfile:
    for line in myfile.readlines():
        match_ip = re.findall(RE_subnet, line, re.MULTILINE)
        match_desc = re.findall(RE_description, line, re.MULTILINE)
        match_vlan = re.findall(RE_vlan, line, re.MULTILINE)
        match_gateway = re.findall(RE_gateway,line,re.MULTILINE)
        Parse_ip.append(''.join(match_ip))
        Parse_desc.append(''.join(match_desc))
        Parse_vlan.append(''.join(match_vlan))
        Interim_gw.append(''.join(match_gateway))

# Clean up bullshit empty values
Parse_ip = list(filter(None,Parse_ip))
Parse_vlan = list(filter(None,Parse_vlan))
Parse_desc = list(filter(None,Parse_desc))
Interim_gw = list(filter(None,Interim_gw))

# Populates artificial lists
# Netmask and VRF
for mask in Parse_ip:
    le_mask = mask.rfind("/")
    net_mask = mask[le_mask:]
    Parse_netmask.append(''.join(net_mask))

for vrf in Parse_desc:
    match_vrf = re.findall(relevant_vrf, vrf)
    Parse_vrf.append(''.join(match_vrf))

with open("D:\samba\parsed.csv", "w") as o:
    print(r'Description,Network,Netmask,Gateway,VLAN,VRF', file=o)
    for a,b,c,d,e,f in zip(Parse_desc,Parse_ip,Parse_netmask,Interim_gw,Parse_vlan,Parse_vrf):
        print (a + ',' + b + ',' + c + ',' + d + ',' + e + ',' + f, file=o)

# Second pass, joins mask and gateway
# if it is of /32 length
# it's a bit shit but I didn't know any better

with open("D:\samba\parsed.csv", "r") as i:
    reader = csv.reader(i, delimiter=',')
    lenCol = len(next(reader))
    included_cols = [2,3]
    for row in reader:
        content = list(row[i] for i in [2,3])
        if content[0] != '/32': content[0] = ''
        Lo_check.append(''.join(content))

for x in range(len(Lo_check)):
    Parse_gateway.append(re.sub('(/32).*','N/A',Lo_check[x]))

# Show time
with open(r'D:\samba\parsed.csv', "w") as o:
    print(r'Description;Network;Netmask;Gateway;VLAN;VRF', file=o)
    for a,b,c,d,e,f in zip(Parse_desc,Parse_ip,Parse_netmask,Parse_gateway,Parse_vlan,Parse_vrf):
        print (a + ';' + b + ';' + c + ';' + d + ';' + e + ';' + f, file=o)

print("Parsing completed.")
