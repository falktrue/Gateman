from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
import cv2
import easyocr
import os

result = "1234"
url = ("https://www.tjrs.jus.br/site_php/consulta/verifica_codigo_novo.php?nome_comarca=Porto+Alegre&versao=&versao_fonetica=2&tipo=1&id_comarca=porto_alegre&intervalo_movimentacao=0&N1_var2=1&id_comarca1=porto_alegre&num_processo_mask=90009625520198212001&num_processo=90009625520198212001&numCNJ=S&id_comarca2=700&uf_oab=RS&num_oab=&foro=0&N1_var2_1=1&intervalo_movimentacao_1=15&ordem_consulta=1&N1_var=&id_comarca3=todas&nome_parte=&N1_var2_2=1&intervalo_movimentacao_2=0&code=" + result)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1280x720")
chrome_options.add_argument('log-level=3')
chrome_driver = os.getcwd() +"\\chromedriver.exe"
driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
driver.get(url)

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
    img_not = apply_brightness_contrast(img, -99, 120)
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
    txtField = driver.find_element_by_xpath("//input[@type='text']").send_keys(resultatum)
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

