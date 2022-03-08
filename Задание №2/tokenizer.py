!pip install pymorphy2
from bs4 import BeautifulSoup
import os
import nltk
nltk.download("stopwords")
nltk.download('wordnet')
from nltk.corpus import stopwords
import pymorphy2

directory_name = '/content/urls'
tokens_file_name = '/content/tokens.txt'
lemmas_file_name = '/content/lemmas.txt'
tokens_set = set()
lemmas_dictionary = {}
russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['что', 'ко' 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на', '“'])
morph = pymorphy2.MorphAnalyzer()
cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
for symbol in cyrillic:
  russian_stopwords.extend([symbol])

if os.path.exists(tokens_file_name):
    os.remove(tokens_file_name)
if os.path.exists(lemmas_file_name):
    os.remove(lemmas_file_name)

def check_is_word_cyrillic(word):
  return all(char in cyrillic for char in word)

def lemmatize(text):
  global tokens_set
  global lemmas_dictionary
  tokens = nltk.word_tokenize(text, language="russian")
  for token in tokens:
    token = token.lower()
    if token not in russian_stopwords and check_is_word_cyrillic(token):
      result = morph.parse(token)[0]
      token_text = token
      token_lemma = result.normal_form
      tokens_set.add(token_text)
      lemma_tokens_in_dict = lemmas_dictionary.get(token_lemma)
      if lemma_tokens_in_dict is None:
        lemmas_dictionary[token_lemma] = [token_text]
      else:
        if token_text not in lemma_tokens_in_dict:
          lemmas_dictionary[token_lemma] = lemma_tokens_in_dict + [token_text]

for file_name in os.listdir(directory_name):
  full_file_path = os.path.join(directory_name, file_name)
  file_text = open(full_file_path).read()
  soup = BeautifulSoup(file_text)
  for infobox in soup.find_all('div', {'class': 'notaninfobox'}):
    infobox.decompose()
  for toc in soup.find_all('div', {'class': 'toc'}):
    toc.decompose()
  for hatnote in soup.find_all('div', {'class': 'hatnote'}):
    hatnote.decompose()
  for references_small in soup.find_all('div', {'class': 'references-small'}):
    references_small.decompose()
  for loadbox_navbox in soup.find_all('div', {'class': 'load-page loadbox-navbox'}):
    loadbox_navbox.decompose()
  for table_wide in soup.find_all('div', {'class': 'table-wide'}):
    table_wide.decompose()
  for text in soup.find_all('div', {'class': 'page-content'}):
    file_content_text = text.get_text()
    lemmatize(file_content_text)

web_page = open(tokens_file_name, "w")
for token in tokens_set:
  web_page.write(token + '\n')
web_page.close()

web_page = open(lemmas_file_name, "w")
for key in lemmas_dictionary:
  result_string = key
  for value in lemmas_dictionary[key]:
    result_string = result_string + " " + value
  web_page.write(result_string + '\n')
web_page.close()