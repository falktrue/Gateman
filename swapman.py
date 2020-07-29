#!/usr/bin/python
import re

listafrom = ['upf1_lte-vlan1', 'upf1_lte-vlan2', 'upf1_s1-u-vlan1', 'upf1_s1-u-vlan2', 'upf1_li-vlan1', 'upf1_li-vlan2', 'upf1_sgi-vlan1', 'upf1_sgi-vlan2', 'upf1_sgi-v6_vlan1', 'upf1_sgi-v6_vlan2', 'upf1_sgi_volte-vlan1', 'upf1_sgi_volte-v6_vlan1', 'upf1_sgi_volte-vlan2', 'upf1_sgi_volte-v6_vlan2', 'upf1_orion_vlan1', 'upf1_orion_vlan2', 'upf1_lte-loop', 'upf1_pgw-s5-up-loop', 'upf1_sgw-s5-up-loop', 'upf1_sx-c-up-loop', 'upf1_sx-u-up-loop', 'upf1_s1u-loop', 'upf1_Li-loop', 'upf1_sgi-loop', 'upf1_sgi_volte-loop', 'upf1_orion-loop']
listato = ['10.191.67.66', '10.191.67.67', '10.191.67.68', '10.191.67.69', '10.191.67.70', '10.191.67.71', '10.191.67.72', '10.191.67.73', '10.191.67.98', '10.191.67.99', '10.191.67.100', '10.191.67.101', '10.191.67.102', '10.191.67.103', '10.191.67.104', '10.191.67.105', '10.191.67.130', '10.191.67.131', '10.191.67.132', '10.191.67.133', '10.191.67.134', '10.191.67.135', '10.191.67.136', '10.191.67.137', '10.191.67.162', '10.191.67.163']
listafound = []
listafile = []
new_file_content = ""
dictfromto = dict(zip(listafrom, listato))

cp_qty = int(input("Entre com o número de UPCIS: "))

for x in range(cp_qty):
    listafile.append('/home/falk/slide' + str(x+3)+'.xml')
    x = x + 1

for x in range(len(listafile)):
    reading_file = open(listafile[x], "r")
    for pingas in reading_file.readlines():
        for k, v in dictfromto.items():
            pingas = pingas.replace(k, v)
        new_file_content += pingas
    reading_file.close()
    writing_file = open(listafile[x], "w")
    writing_file.write(new_file_content)
    new_file_content = ""
    writing_file.close()
