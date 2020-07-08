#!/usr/bin/python
import csv
import re
import os

# Declaration of independence
Gateway = []
Compute = []
Port = []
Interface = []
VRF = []
Unit = []
VLAN = []
Loopv4 = []
Loop_desc = []
Loop_ID = []
Lo_VRF = []

# User interaction. Ask questions, get answers. Mostly.
print('Suas Compute Units "High Performance" refletem o número de "slots" deste SAE-GW.')
while True:
    try:
        HP_qty = int(input("Entre com o número de HPs: "))
    except ValueError:
        print("Sorry. Remove boxing gloves")
        continue
    if HP_qty < 0:
        print("Sorry, don't be negative.")
        continue
    if HP_qty == 0:
        print("99 problemas, mas a compute não é 1.")
        continue
    else:
        break

print('Seu SAE-GW típico utiliza 9 VRFs (Li, SIG, AAA, LTE(S11), LTE(S5), SGI, S1-U, APN-UNICA, SGI_VoLTE).')
VRF_qty = None
VRF_qty = 9 if VRF_qty is None else VRF_qty
while True:
    try:
        VRF_qty = int(input("Entre com o número de VRFs: "))
    except ValueError:
        print("Assumindo 9 VRFs. \n")
        break
    else:
        break

relevant_vrf = re.compile(r"(Li|S1-U|SIG|SGI_VoLTE|AAA|S11|S5|SGI|APN-UNICA)")

# PROGRAM START
# Reads sauce file and populates Gateway list (column 3)
while True:
    try:
        with open('/home/falk/parsed.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader:
                description_col = row[0]
                gateway_col = row[3]
                network_col = row[1]
                mask_col = row[2]
                vrf_col = row[5]
                if mask_col == '/32':
                    match_vrf = re.findall(relevant_vrf, vrf_col)
                    Lo_VRF.append(''.join(match_vrf))
                    Loopv4.append(''.join(network_col))
                    Loop_desc.append(''.join(description_col))
                if mask_col == '/27':
                    Gateway.append(''.join(gateway_col))
    except FileNotFoundError:
        print("MAJOR: arquivo 'parsed.csv' non ecziste.")
        print("Ou talvez não tenha sido encontrado. Enfim, gere-o primeiro.")
        exit()
    except IndexError:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Parsed file has been pwned, try again')
        exit()
    else:
        break

if VRF_qty * 2 != len(Gateway):
    print('MINOR: número de VRFs (',VRF_qty,') leva conta a não bater com a quantidade de /27 encontrados.')
    print('Esperado: ',VRF_qty, 'x 2 (A-side, B-side). Valor encontrado:', len(Gateway))
    print('Gateman irá tentar remover da lista os candidatos menos prováveis,')
    print('mas recomenda-se (fortemente) realizar um double check nos endereços distribuídos.')
    input('\nPress ''F14'' to continue...')
    Gateway.clear()

    with open('/home/falk/parsed.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            gateway_col = row[3]
            mask_col = row[2]
            vrf_col = row[5]
            vlan_col = row[4]
            if relevant_vrf.search(vrf_col) and mask_col == '/27':
                match_vrf = re.findall(relevant_vrf, vrf_col)
                VRF.append(''.join(match_vrf))
                Gateway.append(''.join(gateway_col))
                VLAN.append(''.join(vlan_col))

# Calculates IPv4 Address from Default GW.
# c as a counter for the first "." reversely
# found in string.
while True:
    try:
        for b in Gateway:
            c = b.rfind(".")
            Lastoct = int(b[c + 1:])
            First3 = str(b[:c + 1])
            for x in range(1, (HP_qty + 1)):
                Lastcpt = str(Lastoct + int(x))
                Compute_cont = First3 + Lastcpt
                Compute.append(Compute_cont)

    except ValueError:
        print('yob tvuyo mat')
        break
    else:
        break

# Port count. Starting on Port-3, A-side(10), then B-side(11)
for y in range(VRF_qty):
    u = 3
    for x in range(3, (HP_qty + 3)):
        A_side = (str(u) + '/10')
        u = u + 1
        Port.append(A_side)
        Unit.append('card-'+str(u-1))
    u = 3
    for y in range(3, (HP_qty + 3)):
        B_side = (str(u) + '/11')
        u = u + 1
        Port.append(B_side)
        Unit.append('card-'+str(u-1))

# Creates dictionaries, which, by definition,
# cannot have duplicates.
# Multiplies so that it populates a list proper
VRF = list(filter(None,VRF))
VRF = list(dict.fromkeys(VRF))
VRF = [y for x in VRF for y in (x,)* (HP_qty * 2)]
VLAN = [y for x in VLAN for y in (x,)* (HP_qty)]
Gateway = [y for x in Gateway for y in (x,)* (HP_qty)]
Interface = list(map('-'.join, zip(Port,VRF)))

# Removes /32 from loopback address string
Loopv4 = ' '.join(Loopv4).replace('/32','').split()

# Generates Loopback ID based on 'until | sign' after description
for l in Loop_desc:
    r = l.rfind('|')
    Lo_name = str(l[r + 2:])
    Loop_ID.append(Lo_name)

# Show time
# Compute Units
with open("/home/falk/CIQ.csv", "w") as o:
    print('VRF;Interface;Unit;Port;Type;VLAN;IPv4 Address;Netmask;Gateway', file=o)
    for a,b,c,d,e,f,g in zip(VRF,Interface,Unit,Port,VLAN,Compute,Gateway):
        print (a + ';' + b + ';' + c + ';' + d + ';logical;' + e + ';' + f + ';/27;' + g, file=o)

# Append Loopbacks, same file
with open("/home/falk/CIQ.csv", "a") as o:
    for a,b,c in zip(Lo_VRF,Loop_ID,Loopv4):
        print (a + ';' + b + ';' + 'N/A' + ';' + 'N/A' + ';loopback;' + 'N/A' + ';' + c + ';/32;' + 'N/A', file=o)

print('CIQ generation completed.')
