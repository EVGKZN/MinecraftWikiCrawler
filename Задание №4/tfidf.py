from bs4 import BeautifulSoup
import nltk
import pymorphy2
nltk.download("stopwords")
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords
import os
import collections
russian_stopwords = stopwords.words("russian")
russian_stopwords.extend(['что', 'ко' 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на', '“'])
cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
for symbol in cyrillic:
  russian_stopwords.extend([symbol])
morph = pymorphy2.MorphAnalyzer()
import math
import shutil
from pathlib import Path

directory_name = '/content/urls'
all_files_texts = []
all_files_ids = []

tf_idf_tokens_dir = '/content/tf_idf_tokens/'
tf_idf_lemmas_dir = '/content/tf_idf_lemmas/'

if os.path.exists(tf_idf_tokens_dir):
  shutil.rmtree(tf_idf_tokens_dir, ignore_errors=True)
if os.path.exists(tf_idf_lemmas_dir):
  shutil.rmtree(tf_idf_lemmas_dir, ignore_errors=True)
os.mkdir(tf_idf_tokens_dir)
os.mkdir(tf_idf_lemmas_dir)

def get_all_files_texts():
  global all_files_texts
  global all_files_ids
  texts = []
  for file_name in os.listdir(directory_name):
    full_file_path = os.path.join(directory_name, file_name)
    file_id = int(Path(full_file_path).stem)
    all_files_ids.append(file_id)
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
      file_text_words = set()
      tokens = nltk.word_tokenize(file_content_text, language="russian")
      for token in tokens:
        token = token.lower()
        if token not in russian_stopwords and check_is_word_cyrillic(token):
          file_text_words.add(token)
      texts.append(list(file_text_words))
  all_files_texts = texts

def get_lemmas_from_tokens_in_text(text):
  lemmas_dictionary = {}
  for token in text:
    result = morph.parse(token)[0]
    token_text = token
    token_lemma = result.normal_form
    lemma_tokens_in_dict = lemmas_dictionary.get(token_lemma)
    if lemma_tokens_in_dict is None:
      lemmas_dictionary[token_lemma] = [token_text]
    else:
      if token_text not in lemma_tokens_in_dict:
        lemmas_dictionary[token_lemma] = lemma_tokens_in_dict + [token_text]
  return lemmas_dictionary

def calculate_df_for_tokens_in_text(text):
    tf_text = collections.Counter(text)
    for i in tf_text:
        tf_text[i] = tf_text[i]/float(len(text))
    return tf_text

def calculate_df_for_lemmas_in_text(lemmas, text):
  lemmas_df_dictionary = {}
  for key in lemmas:
    lemma_counter = 0
    for value in lemmas[key]:
      lemma_counter += text.count(value)
    lemmas_df_dictionary[key] = lemma_counter/float(len(text))
  return lemmas_df_dictionary

def calculate_idf_for_tokens_in_text(text):
  global all_files_texts
  tokens_idf_dictionary = {}
  for token in text:
    tokens_idf_dictionary[token] = math.log10(len(all_files_texts)/sum([1.0 for i in all_files_texts if token in i]))
  return tokens_idf_dictionary

def calculate_idf_for_lemmas_in_text(lemmas):
  global all_files_ids
  global all_files_texts
  lemmas_df_dictionary = {}
  for key in lemmas:
    files_ids_set = set()
    for value in lemmas[key]:
      for count, text in enumerate(all_files_texts):
        if value in text:
          files_ids_set.add(all_files_ids[count])
    lemmas_df_dictionary[key] = math.log10(len(all_files_texts)/len(files_ids_set))
  return lemmas_df_dictionary



get_all_files_texts()
for count, text in enumerate(all_files_texts):
  lemmas_in_current_text = get_lemmas_from_tokens_in_text(text)
  tokens_and_df = calculate_df_for_tokens_in_text(text)
  lemmas_and_df = calculate_df_for_lemmas_in_text(lemmas_in_current_text, text)
  tokens_and_idf = calculate_idf_for_tokens_in_text(text)
  lemmas_and_idf = calculate_idf_for_lemmas_in_text(lemmas_in_current_text)
  tokens_tf_idf_file_name = tf_idf_tokens_dir + str(all_files_ids[count]) + '.txt'
  lemmas_tf_idf_file_name = tf_idf_lemmas_dir + str(all_files_ids[count]) + '.txt'

  f_tokens = open(tokens_tf_idf_file_name, 'w')
  for token in text:
    f_tokens.write(token + ' ' + str(tokens_and_idf[token]) + ' ' + str(tokens_and_idf[token]*tokens_and_df[token]) + '\n')
  f_tokens.close()

  f_lemmas = open(lemmas_tf_idf_file_name, 'w')
  for lemma in lemmas_in_current_text:
    f_lemmas.write(lemma + ' ' + str(lemmas_and_idf[lemma]) + ' ' + str(lemmas_and_idf[lemma]*lemmas_and_df[lemma]) + '\n')
  f_lemmas.close()