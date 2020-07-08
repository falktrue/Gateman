#!/usr/bin/python
import subprocess

print("""
 ██████╗  █████╗ ████████╗███████╗███╗   ███╗ █████╗ ███╗   ██╗
██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝████╗ ████║██╔══██╗████╗  ██║
██║  ███╗███████║   ██║   █████╗  ██╔████╔██║███████║██╔██╗ ██║
██║   ██║██╔══██║   ██║   ██╔══╝  ██║╚██╔╝██║██╔══██║██║╚██╗██║
╚██████╔╝██║  ██║   ██║   ███████╗██║ ╚═╝ ██║██║  ██║██║ ╚████║
 ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
- "It manages Gateways."

    1. Executar o parser
    2. Gerar planilha CIQ da Cisco
    3. Sair""")
ans=True
while ans:
    ans=input("\nEntre sua opção: ")
    if ans=="1":
        print("\nChamando parser.")
        subprocess.check_call(["python", "/home/falk/PycharmProjects/cheems/parser.py"])
    elif ans=="2":
        print("\nChamando CIQ.")
        subprocess.check_call(["python", "/home/falk/PycharmProjects/cheems/ciq.py"])
    elif ans=="3":
        print('\nAgradecemos por utilizar o Gateman. Remember, kids -')
        print('\n\t\t\t\t\t"Automation is not AI"')
        print('\t\t\t\t\t-Falk')
        ans = None
    else:
        print("\n Comando ou nome de arquivo inválido")
