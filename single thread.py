import requests,time,random
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.options import Options


data = pd.read_excel('abc.xlsx')

data_new= pd.DataFrame(columns= ['Postal_code'])

#to click the popup once
try:
    wait = 3
    chrome_options = Options()
    #hrome_options.add_argument('--headless')

    browser = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    browser.get('https://pta.waynecounty.com/')
    time.sleep(wait)
    browser.find_element_by_css_selector('[class="ui large blue right labeled icon button"]').click()
except Exception as e:
    print( e, "occurred.")
    
def data_scrap(Postal_code):
    dic_new={}
    #browser.find_element_by_css_selector('a.item').click()
    browser.find_element_by_id('ParcelTab').click()
    elementID = browser.find_element_by_id("PARCEL_ID")
    elementID.send_keys(Postal_code)
    elementID.submit()
    src = browser.page_source
    soup = BeautifulSoup(src,'lxml')
    first_data = soup.find('div',{'class':'ui stackable three column grid'})
    second_data = soup.find('table',{'class':'ui striped celled table'})
    #for top data
    a = first_data.find_all('div',{'class':"column"})
    top_labels = ['lblMunicipality','PARCEL_ID','lblPropertyType','PROP_STREET_NBR', 'lblTaxPayer1']
    for i in range(5):
        top_labels.append(a[i].find('h4',{'class':'ui dividing header'}).get_text().strip())
    dic_new['Postal_code'] = Postal_code
    for j in range(5):
        dic_new[str(top_labels[j+5])] = a[j].find('label',{'id':top_labels[j]}).get_text().strip()
    #for bottom list
    b =  second_data.find_all('td')
    tax = []
    st = ['_Tax','_Interest_&_Fees','_Amount_Due','_Status']

    for k in b:
        tax.append(k.get_text().strip())

    for l in range(len(tax)):
        
        if 'Tax Year' in str(tax[l]):
            pre_st = str(tax[l][-4:])
            for m in range(4):
                dic_new[pre_st+st[m]] = tax[l+m+1].split(':')[1]

        if 'Totals ' in str(tax[l]):
            pre_st = str(tax[l][:-2])
            for m in range(3):
                dic_new[pre_st+st[m]] = tax[l+m+1].split(':')[1]
     
    time.sleep(random.randint(1,5))
    browser.get('https://pta.waynecounty.com/')
    
    
    return dic_new
   
    

for post in data['Postal_code']:
    try:
        data_new = data_new.append(data_scrap(post), ignore_index=True)
    
    except Exception as e:
        print( e, "occurred.")
data_new.to_csv(r'postalIDs.csv')



