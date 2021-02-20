import requests,time,random
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import threading,queue,time

data = pd.read_excel('abc.xlsx')

class Scrap:
############################################################
    def open_webdriver(self):
        chrome_options = Options()
        #hrome_options.add_argument('--headless')

        self.browser = webdriver.Chrome('chromedriver.exe', options=chrome_options)
        return self.browser
############################################################
    def popup(self):
        
        self.browser.get('https://pta.waynecounty.com/')
        time.sleep(3)
        try:
            self.browser.find_element_by_css_selector('[class="ui large blue right labeled icon button"]').click()
        except Exception as e:
            print( e, "occurred.")
    
############################################################

    def data_scrap(self,Postal_code='bilal'):
        browser = self.browser
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
        self.browser.get('https://pta.waynecounty.com/')


        return dic_new
############################################################
#function outside class
data_new= pd.DataFrame(columns= ['Postal_code','Municipality','Parcel ID','Property Address','Property Type','Taxpayer(s)'])

############################################################

def divide_data_for_each_thread(max_length_of_data, max_thread,initial_index):
    divide_data = max_length_of_data // max_thread
    my_list=[]
    for i in range(max_thread):

        a = initial_index

        initial_index = initial_index+divide_data
        my_list.append(a)
    return my_list
################################################################################
################################################################################
################################################################################
max_length_of_data = 50
max_thread = 5
delta = max_length_of_data//max_thread
initial_index = 0
csv_data = data
dataframe = data_new
################################################################################
################################################################################
################################################################################

q = queue.Queue()
def run_for_multithreading(initial,csv_data=csv_data,delta=delta,dataframe= dataframe,q=q):
    s = Scrap() 
    s.open_webdriver()
    s.popup()
    
    for post in data.iloc[initial:initial+delta,0]:
        try:
            dictionary = s.data_scrap(post)
            q.put(dictionary)
   
             #print("put --> ",dictionary)


        except Exception as e:
            print( e, "occurred.")


start = time.perf_counter()
output_data=[]
try:
    
    
    ids = divide_data_for_each_thread(max_length_of_data, max_thread,initial_index)
    start = time.perf_counter()
    
    threads = []
    for t in range(max_thread):
        t = threading.Thread(target = run_for_multithreading, args=[ids[t]] )
        t.start()
        threads.append(t)
    
    for thread in threads:
        
        thread.join()

except Exception as e:
    print( e, "occurred.")
    

# dataframe.to_csv(r'dummy_data_from_multi.csv')
end = time.perf_counter()
print('finished in ',round(end-start,2),' seconds')
count = 0
while(not(q.empty())):
    count = count + 1
    result = q.get()
    print(count," --> " , result)
    data_new = data_new.append(result, ignore_index=True)
data_new.to_csv(r'final_data_multithreading.csv')

print('Data scraped from index ',initial_index,' to index ',initial_index+(max_length_of_data-(max_length_of_data%max_thread)))