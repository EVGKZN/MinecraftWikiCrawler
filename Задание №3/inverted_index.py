!pip install pymorphy2
from bs4 import BeautifulSoup
import os
import nltk
nltk.download("stopwords")
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords
import pymorphy2
import re

is_need_to_reindexize = True

morph = pymorphy2.MorphAnalyzer()
directory_name = '/content/urls'
inverted_index_file_name = '/content/inverted_index.txt'
inverted_index_dictionary = {}
russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['что', 'ко' 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на', '“'])

cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
for symbol in cyrillic:
  russian_stopwords.extend([symbol])

def check_is_word_cyrillic(word):
  return all(char in cyrillic for char in word)

def indexize(text, file_number):
  file_number = int(file_number)
  global inverted_index_dictionary
  tokens = nltk.word_tokenize(text, language="russian")
  for token in tokens:
    token = token.lower()
    if token not in russian_stopwords and check_is_word_cyrillic(token):
      result = morph.parse(token)[0]
      lemma = result.normal_form
      lemma_in_inverted_index_dict = inverted_index_dictionary.get(lemma)
      if lemma_in_inverted_index_dict is None:
        inverted_index_dictionary[lemma] = [file_number]
      else:
        if file_number not in lemma_in_inverted_index_dict:
          inverted_index_dictionary[lemma] = lemma_in_inverted_index_dict + [file_number]

if is_need_to_reindexize:
  if os.path.exists(inverted_index_file_name):
    os.remove(inverted_index_file_name)

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
      base = os.path.basename(full_file_path)
      base_file_number = os.path.splitext(base)[0]
      indexize(file_content_text, base_file_number)

  inverted_indexes_file = open(inverted_index_file_name, "w")
  sorted_inverted_index_dictionary = sorted(inverted_index_dictionary)
  for key in sorted_inverted_index_dictionary:
    result_string = key
    sorted_values_array = sorted(inverted_index_dictionary[key])
    for value in sorted_values_array:
      result_string = result_string + " " + str(value)
    inverted_indexes_file.write(result_string + '\n')
  inverted_indexes_file.close()