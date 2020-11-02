from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cv2, easyocr, os, time
import concurrent.futures

# TJ RS Collector
# OCR plus clicky clicker
start = time.time()

comarcaList = []
procList = []
trollList = []
trollMark = []

x = 0
with open(str(r'D:/samba/TJ/proclist.txt'), "r") as o:
    while x < 50:
        procList.append(''.join(o.readline().split()))
        x += 1

initUrl = ("https://www.tjrs.jus.br/site_php/consulta/consulta_processo.php?versao=&versao_fonetica=2&tipo=1&id_comarca=uruguaiana&intervalo_movimentacao=0&N1_var2=1&id_comarca1=uruguaiana&num_processo_mask=00022351320138210037&num_processo=00022351320138210037&numCNJ=S")
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
    troller = int(len(driver.title))
    while troller == 0:
        codeLyoko = driver.find_element_by_xpath("//img[@name='img_check']")
        codeLyoko.screenshot('test.png')
        img = cv2.imread("./test.png")
        img_not = apply_brightness_contrast(img, -97, 120)
        # img_not = cv2.bitwise_not(img_not)
        # Do OCR and give me string
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img_not, detail = 0, allowlist = '1234567890', mag_ratio = 0.7)
        try:
            resultatum = result[0]
            if len(resultatum) != 4:
                print("Invalid input length. Retrying.")
                resultatum = '9999'
            else:
                pass
        except IndexError:
            print("No characters detected. Retrying.")
            resultatum = '9999'
        driver.find_element_by_xpath("//input[@type='text']").send_keys(resultatum)
        driver.find_element_by_name("verifica").submit()
        troller = int(len(driver.title))
        if troller > 0:
            print("Human verification PASSED.")
        elif troller == 0:
            print("Incorrect code sent.")
ocr_remix()

driver.execute_script("window.open('https://www.tjrs.jus.br/site_php/consulta/index.php', '_blank')")

# THIS HERE BE CATCHA LIST
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
    driver.get('https://www.tjrs.jus.br/site_php/consulta/consulta_processo.php?&versao=&versao_fonetica=2&tipo=1&id_comarca='+ comarca + '&intervalo_movimentacao=0&N1_var2=1&id_comarca1='+ comarca + '&num_processo_mask='+ numProc + '&num_processo=' + numProc + '&numCNJ=S')
    if len(driver.title) > 0:
        if len(driver.page_source) > 1500: # Processo válido. Tentar pegar movimentacao
            driver.find_element_by_partial_link_text("Ver todas as mov").click()
            # element_present = EC.presence_of_element_located((By.XPATH, "//div[@id='conteudo']"))
            # WebDriverWait(driver, 10).until(element_present)
            # time.sleep(1)
            if len(driver.title) > 0: # Processo não é troll, dei o click e passou
                text = driver.find_element_by_xpath("//div[@id='conteudo']").text
                # print('DEBUG:', numProc)
                # print('DEBUG:', comarca)
                with open(str(r'D:/samba/TJ/Movimentacoes/' + proc + '.txt'), "w") as o:
                    print(text, file=o)
                    print('Information saved as' , proc + '.txt')
                try:
                    trollMark.remove(comarca)
                    trollList.remove(proc)
                except ValueError:
                    pass
            else: # Processo troll
                if proc not in trollList:
                    trollList.append(proc)
        else: # Processo inválido, não vai ter movimentação
            with open(str(r'D:/samba/TJ/Movimentacoes/' + proc + '.txt'), "w") as o:
                for row in driver.find_elements_by_css_selector("tr"):
                    cell = row.find_elements_by_tag_name("td")[0]
                    print(cell.text, file=o)
            print('Information saved as' , proc + '.txt')
            try:
                trollMark.remove(comarca)
                trollList.remove(proc)
            except ValueError:
                pass
    else: # Novo CAPTCHA necessário
        ocr_remix()
        if len(driver.page_source) > 1500:
            driver.find_element_by_partial_link_text("Ver todas as mov").click()
            # element_present = EC.presence_of_element_located((By.XPATH, "//div[@id='conteudo']"))
            # WebDriverWait(driver, 10).until(element_present)
            # time.sleep(1)
            text = driver.find_element_by_xpath("//div[@id='conteudo']").text
            # print('DEBUG:', numProc)
            # print('DEBUG:', comarca)
            with open(str(r'D:/samba/TJ/Movimentacoes/' + proc + '.txt'), "w") as o:
                print(text, file=o)
                print('Information saved as' , proc + '.txt')
        else: # Pepega OK, mas processo invalido
            with open(str(r'D:/samba/TJ/Movimentacoes/' + proc + '.txt'), "w") as o:
                for row in driver.find_elements_by_css_selector("tr"):
                    cell = row.find_elements_by_tag_name("td")[0]
                    print(cell.text, file=o)
            print('Information saved as' , proc + '.txt')
    return trollList

for i in procList:
    getComarca(i)

if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor() as executor:
        trolada = executor.map(getProcesso, procList, comarcaList)
        
        for result in trolada:
            trollList.append(''.join(result))
    
    trollList = list(filter(None,trollList))
    trollList = list(dict.fromkeys(trollList))
    print('List troler:', trollList)

    comarcaList = []
    for i in trollList:
        getComarca(i)

    trollMark = comarcaList
    while len(trollList) > 0:
        for x in range(len(trollList)):
            try:
                getProcesso(trollList[x], trollMark[x])
            except IndexError as e:
                pass

    end = time.time()
    chrono = round(end - start, 2)
    print("Tasks finished,", chrono, "seconds taken.")
