from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cv2
import easyocr
import os

# TJ RS Collector
# OCR plus clicky clicker

initUrl = ("https://www.tjrs.jus.br/site_php/consulta/verifica_codigo_novo.php?nome_comarca=Porto+Alegre&versao=&versao_fonetica=2&tipo=1&id_comarca=porto_alegre&intervalo_movimentacao=0&N1_var2=1&id_comarca1=porto_alegre&num_processo_mask=90009625520198212001&num_processo=90009625520198212001&numCNJ=S")
urlComarca = ("https://www.tjrs.jus.br/site_php/consulta/index.php")

# Chrome tings
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1280x720")
chrome_options.add_argument('log-level=3')
chrome_driver = os.getcwd() +"\\chromedriver.exe"

# Rolling START
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
driver.get(initUrl)

driver.switch_to.window(driver.window_handles[0])


if len(driver.page_source) > 0:
    print('Site reached. Attempting to solve CAPTCHA.\n')

# Image processing fuckery
def apply_brightness_contrast(input_img, brightness = 0, contrast = 0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()
    if contrast != 0:
        f = 131*(contrast + 127)/(127*(131-contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
    return buf

def ocr_remix():
    codeLyoko = driver.find_element_by_xpath("//img[@name='img_check']")
    codeLyoko.screenshot('test.png')
    img = cv2.imread("./test.png")
    img_not = apply_brightness_contrast(img, -97, 120)
    img_not = cv2.bitwise_not(img_not)
    # Do OCR and give me string
    reader = easyocr.Reader(['en'])
    result = reader.readtext(img_not, detail = 0, allowlist = '1234567890', mag_ratio = 0.6)
    while True:
        try:
            resultatum = result[0]
            if len(resultatum) != 4:
                print("Invalid input length. Retrying.")
                resultatum = '9999'
            else:
                break
        except IndexError:
            print("No characters detected. Retrying.")
            resultatum = '9999'
            break
        else:
            break
    driver.find_element_by_xpath("//input[@type='text']").send_keys(resultatum)
    driver.find_element_by_name("verifica").submit()
    global troller
    troller = int(len(driver.title))
    if troller != 0:
        print("Human verification PASSED.")
    elif troller == 0 and resultatum == '9999':
        print("Here we go again.")
    elif troller == 0 and resultatum != '9999':
        print("Incorrect code passed.")
    return troller

ocr_remix()

while troller == 0:
    ocr_remix()
    if troller != 0:
        break

driver.execute_script("window.open('https://www.tjrs.jus.br/site_php/consulta/index.php', '_blank')")

# THIS HERE BE CATCHA LIST

comarcaList = []
# procList = ['0084300-88.2008.5.04.0029', '5000023-24.2014.8.21.0028', '0033257-24.2014.8.21.0015', '0434201-37.2013.8.21.0001', '0453171-06.2014.8.21.7000']
procList = ['5002452-50.2019.8.21.0072', '5000023-24.2014.8.21.0028', '0033257-24.2014.8.21.0015', '0434201-37.2013.8.21.0001', '9000148-27.2016.8.21.0165']


def getComarca(proc):
    driver.switch_to.window(driver.window_handles[1])
    driver.find_element_by_xpath("//input[@type='text'][@name='num_processo_mask']").send_keys(proc)
    driver.find_element_by_xpath("//input[@type='radio'][@name='numCNJ'][@value='S']").click()
    checka = driver.find_element_by_name("id_comarca1").get_attribute("value")
    comarcaList.append(''.join(checka))
    driver.find_element_by_xpath("//input[@type='text'][@name='num_processo_mask']").clear()
    return comarcaList

def getProcesso(proc, comarca):
    driver.switch_to.window(driver.window_handles[0])
    numProc = proc.replace('.', '').replace('-', '')
    print('DEBUG:', str('https://www.tjrs.jus.br/site_php/consulta/consulta_processo.php?nome_comarca=Porto+Alegre&versao=&versao_fonetica=2&tipo=1&id_comarca='+ comarca + '&intervalo_movimentacao=0&N1_var2=1&id_comarca1='+ comarca + '&num_processo_mask='+ numProc + '&num_processo=' + numProc + '&numCNJ=S&id_comarca2=700&uf_oab=RS&num_oab=&foro=0&N1_var2_1=1&intervalo_movimentacao_1=15&ordem_consulta=1&N1_var=&id_comarca3=todas&nome_parte=&N1_var2_2=1&intervalo_movimentacao_2=0'))
    driver.get('https://www.tjrs.jus.br/site_php/consulta/consulta_processo.php?nome_comarca=Porto+Alegre&versao=&versao_fonetica=2&tipo=1&id_comarca='+ comarca + '&intervalo_movimentacao=0&N1_var2=1&id_comarca1='+ comarca + '&num_processo_mask='+ numProc + '&num_processo=' + numProc + '&numCNJ=S&id_comarca2=700&uf_oab=RS&num_oab=&foro=0&N1_var2_1=1&intervalo_movimentacao_1=15&ordem_consulta=1&N1_var=&id_comarca3=todas&nome_parte=&N1_var2_2=1&intervalo_movimentacao_2=0')
    driver.find_element_by_partial_link_text("Ver todas as mov").click()
    text = driver.find_element_by_xpath("//div[@id='conteudo']").text
    print('DEBUG:', numProc)
    print('DEBUG:', comarca)
    with open(str(r'D:/samba/TJ/Movimentacoes/' + proc + '.txt'), "w") as o:
        print(text, file=o)
        print('Information saved as' , proc + '.txt')

for i in procList:
    getComarca(i)

for x in range(len(procList)):
    getProcesso(procList[x], comarcaList[x])


# nombresFile = []
# numProcess = []
# listafile = []
# with open(r'D:\samba\TJ\proclist.txt', "r") as listinha:
#     for i in range(0, 15):
#         line = listinha.readline().strip()
#         nombresFile.append(''.join(line))

# for i in nombresFile:
#     numProcess.append(i.replace('.', '').replace('-', ''))

# for x in range(len(numProcess)):
#     listafile.append(r'D:/samba/TJ/Movimentacoes/' + str(nombresFile[x]) + '.txt')
#     x = x + 1

# for i in numProcess:
#     x = numProcess.index(i)
#     print(i)
#     driver.get('https://www.tjrs.jus.br/site_php/consulta/consulta_processo.php?nome_comarca=Tribunal+de+Justi%E7a&versao=&versao_fonetica=1&tipo=1&id_comarca=700&intervalo_movimentacao=0&N1_var2=1&id_comarca1=700&num_processo_mask=' + i + '&num_processo=' + i + '&numCNJ=S&id_comarca2=700&uf_oab=RS&num_oab=&foro=0&N1_var2_1=1&intervalo_movimentacao_1=15&ordem_consulta=1&N1_var=&id_comarca3=todas&nome_parte=&N1_var2_2=1&intervalo_movimentacao_2=0')
#     driver.find_element_by_link_text("Ver todas as movimentações").click()

#     text = driver.find_element_by_xpath("//div[@id='conteudo']").text
#     with open(listafile[x], "w") as o:
#         print(text, file=o)
#         print('Information saved as ', o)
