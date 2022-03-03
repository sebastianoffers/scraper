from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd 
import numpy as np 
import json
import time

DRIVER_PATH = 'C:\chromedriver'
options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")
driver.implicitly_wait(10)

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get("https://www.gelbeseiten.de/Suche/Fenster/Bundesweit")
time.sleep(5)
try:
    banner_accept = driver.find_element(By.CSS_SELECTOR, '#cmpwelcomebtnyes')
    banner_accept.click()
except:
    print('no cookie banner')

try:
    more = driver.find_element(By.CSS_SELECTOR, '#mod-LoadMore--button')
except:
    print("no button next")

HeaderCsv = ['Company Name', 'Street', 'Phone', 'Email', 'GS URL', 'Website', 'Branche']
results = []
phonenumber_exist = []

if len(driver.find_elements(By.CSS_SELECTOR, '#loadMoreGesamtzahl')) > 0:
    loadMoreGesamtzahl = int(driver.find_elements(By.CSS_SELECTOR, '#loadMoreGesamtzahl')[0].text)
else:
    loadMoreGesamtzahl = 0

        
def control():
    global resultsprogress
    global loadMoreGesamtzahl
    global results
    global HeaderCsv
    global phonenumber_exist
    if resultsprogress == 0:
       run = len(driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer'))
       i = 0
       while i < run:
           getResults(i)
           i += 1
           resultsprogress += 1
       if run > 0 and len(results) > 0:
           arr = np.asarray(results)
           pd.DataFrame(arr).to_csv('sample.csv', mode='a', index=True, header  = HeaderCsv)
           results = []
       else:
           return 1
    elif resultsprogress > 0 and len(driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer')) > 0:
        n = 1
        run = len(driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer')) - resultsprogress
        print(run)
        a = resultsprogress
        while n < run:
           print(n+a)
           try:
               getResults(n+a)
           except:
               print("error results")
           n += 1
           resultsprogress += 1
        if run > 0 and len(results) > 0:
           arr = np.asarray(results)
           pd.DataFrame(arr).to_csv('sample.csv', mode='a', index=True, header  = HeaderCsv)
           results = []
    
    if len(driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer')) > 0 and run > 0:
        try:
            if len(driver.find_elements(By.CSS_SELECTOR, '#mod-LoadMore--button')) == 1: 
                driver.execute_script("document.getElementById('mod-LoadMore--button').scrollIntoView({ block: 'end',  behavior: 'smooth' });")
                time.sleep(1)
                print("ckick 1")
                driver.find_elements(By.CSS_SELECTOR, 'a[id="mod-LoadMore--button"]')[0].click()
                time.sleep(3)
                
            else:
                return 1
        except:
            try:
                driver.execute_script("document.getElementById('mod-LoadMore--button').scrollIntoView({ block: 'end',  behavior: 'smooth' });")
                
                if len(driver.find_elements(By.CSS_SELECTOR, '#mod-LoadMore--button')) == 1: 
                    time.sleep(1)
                    print("ckick 2")
                    driver.find_elements(By.CSS_SELECTOR, '#mod-LoadMore--button')[0].click()
                else:
                    return 1
            except:
                print('click error')
                if len(results) > 0:
                    arr = np.asarray(results)
                    pd.DataFrame(arr).to_csv('sample.csv', mode='a', index=True, header=HeaderCsv)
                    results = []
                return 1;
        if len(results) > 100:
            arr = np.asarray(results)
            pd.DataFrame(arr).to_csv('sample.csv', mode='a', index=True, header=HeaderCsv)
            results = []
        control();
    elif len(driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer')) == 0:
        arr = np.asarray(results)
        pd.DataFrame(arr).to_csv('sample.csv', mode='a', index=True, header=HeaderCsv)
        results = []
        return 'finish'
        #driver.quit()


def getResults(i):
    arr = []
    try:
        artikelall = driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer')
    except:
        return 'error artikel'
    if artikelall[i]:
        try:
            driver.execute_script(f"document.querySelectorAll('.mod-Treffer')[{i}].scrollIntoView()")
        except:
            print("error script")
    time.sleep(1)
    try:
        CompanyName = artikelall[i].find_elements(By.CSS_SELECTOR, 'h2')[0].text
    except:
        CompanyName = ""
    arr.append(CompanyName)
    try:		
        Adresse = artikelall[i].find_elements(By.CSS_SELECTOR, 'p[data-wipe-name="Adresse"]')[0].text
    except:
        Adresse = ""
    arr.append(Adresse)
    try:		
        PhoneNumber = artikelall[i].find_elements(By.CSS_SELECTOR, '.mod-AdresseKompakt__phoneNumber')[0].text
    except:
        PhoneNumber = ""
    arr.append(PhoneNumber)
    try:
       Email = artikelall[i].find_elements(By.CSS_SELECTOR, '.contains-icon-email')[0].get_attribute('href').replace('mailto:', '').split('?')[0]
       if Email.find("@") == -1:
          Email = 'scanMail'
    except:
       Email = "scanMail"
    arr.append(Email)
    try:		
        url = 'https://www.gelbeseiten.de/gsbiz/' + json.loads(driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer')[i].find_elements(By.CSS_SELECTOR, '.contains-icon-details')[0].get_attribute('data-parameters'))['realId']
    except:
        try:
            url = artikelall[i].find_elements(By.CSS_SELECTOR, '.contains-icon-details')[0].get_attribute('href')   
        except:
            url = ""
    arr.append(url)
    try:
        Website = artikelall[i].find_elements(By.CSS_SELECTOR, '.contains-icon-homepage')[0].get_attribute('href')
    except:
        Website = ""
    arr.append(Website)
    try:
        Branche =  artikelall[i].find_elements(By.CSS_SELECTOR, '.mod-Treffer--besteBranche')[0].text
    except:
        Branche = 'unknown'
    arr.append(Branche)
    #print(arr)
    if PhoneNumber not in phonenumber_exist and PhoneNumber != "":
        phonenumber_exist.append(PhoneNumber)
        print(PhoneNumber)
        results.append(arr)


with open('stadt.txt') as file:
     for line in file:
        #print(line.rstrip())
        driver.find_elements(By.CSS_SELECTOR, '#where_search')[0].clear()
        driver.find_elements(By.CSS_SELECTOR, '#where_search')[0].send_keys(line.rstrip())
        driver.find_elements(By.CSS_SELECTOR, '.search_go')[0].click()
        resultsprogress = 0
        time.sleep(3)
        loadMoreGezeigteAnzahl = len(driver.find_elements(By.CSS_SELECTOR, '.mod-Treffer'))
        control() 