import requests
from bs4 import BeautifulSoup
import time
import os
import shutil
from google.colab import files
import uuid

directory_name = '/content/urls'
if os.path.exists(directory_name):
    shutil.rmtree(directory_name, ignore_errors=True)
if os.path.exists('/content/urls.zip'):
    os.remove('/content/urls.zip')
os.mkdir(directory_name)

crawled_pages_set = set()
crawled_pages_list = []
crawled_pages_index_txt = ""

def crawl_page(url, max_pages):
  global crawled_pages_index_txt
  print("Crawling " + url)
  source_code = requests.get(url)
  plain_text = source_code.text
  soup = BeautifulSoup(plain_text)
  for link in soup.findAll('a', {'class': 'mw-redirect'}):
    if len(crawled_pages_set) < max_pages and link.string != None:
      href = "https://minecraft.fandom.com/" + link.get('href')
      check_page_source_code = requests.get(href)
      check_page_plain_text = check_page_source_code.text
      if check_page_plain_text.find("There is currently no text in this page.") == -1:
        if href not in crawled_pages_set:
          crawled_pages_set.add(href)
          crawled_pages_list.append(href)

          save_path = directory_name
          file_name = str(len(crawled_pages_list)) + '.html'
          completeName = os.path.join(save_path, file_name)
          web_page = open(completeName, "w")
          web_page.write(check_page_plain_text)
          web_page.close()
          crawled_pages_index_txt += file_name + " - " + href + "\n"
      time.sleep(0.1)

def trade_spider(max_pages):
  base_url = "https://minecraft.fandom.com/ru/wiki/%D0%98%D0%B3%D1%80%D0%BE%D0%B2%D0%BE%D0%B9_%D0%BF%D0%B5%D1%80%D1%81%D0%BE%D0%BD%D0%B0%D0%B6"
  crawl_page(base_url, max_pages)
  current_url_number = 1
  isOk = True
  while isOk and len(crawled_pages_set) < max_pages:
    try:
      crawl_page(crawled_pages_list[current_url_number], max_pages)
    except:
      isOk = False
      print("Not ok!")
    current_url_number += 1
trade_spider(100)
file_name = 'index.txt'
completeName = os.path.join('/content', file_name)
index_txt = open(completeName, "w")
index_txt.write(crawled_pages_index_txt)
index_txt.close()
!zip -r /content/urls.zip urls
files.download("/content/urls.zip")
files.download("/content/index.txt")
