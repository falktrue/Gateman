#!/usr/bin/python
import re
import csv

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

# Regex madness
RE_subnet = r"(?<=Sub-rede\t).+$"
RE_description = r"(?<=Descrição: ).*"
RE_vlan = r"(?<=Vlan: ).+?(?=	)"
RE_gateway = r"(?<=Gateway: ).*"

# Reads your file. Call Mauricio, get your IPs,
# copy and paste into source.txt. Use join or else
# it creates a list of lists for some stupid fucking reason

with open('/home/falk/source.txt') as myfile:
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
    le_vrf = vrf.rfind("|")
    clean_vrf = vrf[le_vrf+2:]
    Parse_vrf.append(''.join(clean_vrf))

# First pass; pure parsing without
# loopback cleanup

with open("/home/falk/parsed.csv", "w") as o:
    print('Description,Network,Gateway,Netmask,VLAN,VRF', file=o)
    for a,b,c,d,e,f in zip(Parse_desc,Parse_ip,Parse_netmask,Interim_gw,Parse_vlan,Parse_vrf):
        print (a + ',' + b + ',' + c + ',' + d + ',' + e + ',' + f, file=o)

# Second pass, joins mask and gateway
# if it is of /32 length
# it's a bit shit but I didn't know any better

with open("/home/falk/parsed.csv", "r") as i:
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
with open("/home/falk/parsed.csv", "w") as o:
    print('Description,Network,Gateway,Netmask,VLAN,VRF', file=o)
    for a,b,c,d,e,f in zip(Parse_desc,Parse_ip,Parse_netmask,Parse_gateway,Parse_vlan,Parse_vrf):
        print (a + ',' + b + ',' + c + ',' + d + ',' + e + ',' + f, file=o)

print("Parsing completed.")
