import json
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from os import path

info = {}
with open('user_info.json') as f:
    info = json.load(f)  


def getChromeDriver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    # options.add_argument('--no-sandbox')
    # options.add_argument('--headless')
    return webdriver.Chrome(options=options)

def loginProcess(driver):
    driver.get("https://www.evernote.com/Login.action")
    driver.implicitly_wait(2)
    email = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))    
    email.send_keys(info["username"])
    submit_button = driver.find_element_by_id('loginButton')
    submit_button.click()
    driver.implicitly_wait(1)
    password = driver.find_element_by_id('password')
    password.send_keys(info["password"])
    submit_button.click()    
    return driver

def read_note(driver):
    title = driver.find_element_by_id('qa-HEADER_NOTE_TITLE').text
    print(title)
    driver.switch_to.frame(0)
    note = driver.find_element_by_id('en-note')
    soup_tbody=BeautifulSoup(note.get_attribute('innerHTML'), 'lxml')
    note_date= soup_tbody.find('h2')    
    tables=soup_tbody.find_all('table')
    content=str(note_date)
    for table in tables:
        content+="<ul>"
        trs=table.find('tbody').find_all('tr')
        for tr in trs:
            tds=tr.find_all('td')
            lis=tds[3].find_all('li')
            for li in lis:
                li_string = str(li)
                if ((li_string.find('[FL]')!=-1) or (li_string.find('[WK]')!=-1)):
                    if(tds[4].text!=""):
                        li_string = li_string.replace("</div></li>", " " + tds[4].text+"</div></li>") 
                    content+=li_string
        content+="</ul><div><br></div>"

    driver.close()
    driver.switch_to.window(driver.window_handles[0]) 
    note_li=driver.find_element_by_id('qa-NAV_ALL_NOTES')
    note_li.click()
    note_li.find_element_by_id('qa-NAVBAR_NOTE_ADD_BUTTON').click()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "iframe"))) 
    driver.switch_to.frame("qa-COMMON_EDITOR_IFRAME")
    time.sleep(1)
    element=WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
    element.send_keys(title)
    element=driver.find_element_by_id('en-note')
    new_html="arguments[0].innerHTML = '" + content + "';"
    driver.execute_script(new_html, element)
    driver.switch_to.default_content()
    # driver.find_element_by_id("qa-SHARE_BUTTON").click()    
    # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "publicLinkSwitch"))) 
    # driver.find_element_by_id("publicLinkSwitch").click()

if  __name__ == "__main__":
    with open('old_note_share_urls.txt') as f:
        URLs = f.readlines()    
    driver=getChromeDriver()
    loginProcess(driver)    
    for url in URLs:
        try:
            new_node = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "qa-NAVBAR_NOTE_ADD_BUTTON"))) 
            driver.execute_script("window.open();")
            driver.implicitly_wait(1)
            driver.switch_to.window(driver.window_handles[1]) 
            driver.get(url)
            driver.implicitly_wait(3)    
            read_note(driver)
        except:
            pass