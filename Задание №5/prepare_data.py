import os
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
import string
import warnings
from scipy import spatial
from sklearn.metrics.pairwise import cosine_similarity

vectors = {}
all_lemmas = []
index_file_directory = '/content/index.txt'
files = os.listdir('/content/tf_idf_lemmas/')
cos_distance = {}
all_files_id_and_link_dictionary = {}

total = set(str(i) for i in range(len(files)))
noise = stopwords.words('russian') + list(string.punctuation)

with open(index_file_directory) as file:
  for line in file:
      line_content_string = line.rstrip()
      line_content_array = line_content_string.split(' - ')
      file_id = line_content_array[0].split('.')[0]
      file_link = line_content_array[1]
      all_files_id_and_link_dictionary[file_id] = file_link

def get_all_lemmas():
  global all_lemmas
  for i in range(len(files)):
    i += 1
    with open(f'/content/tf_idf_lemmas/{i}.txt', 'r', encoding='utf-8') as file:
      while True:
        line = file.readline()[:-1].split(' ')[0]
        if not line:
          break
        elif line not in all_lemmas:
          all_lemmas.append(line)


def word_tokenization(t):
  vectorized = CountVectorizer(ngram_range=(1, 1),
                                tokenizer=word_tokenize,
                                stop_words=noise)
  vectorized.fit_transform(t)
  return list(vectorized.vocabulary_)


get_all_lemmas()
for i in range(len(files)):
  i += 1
  file_words = []
  with open(f'/content/tf_idf_lemmas/{i}.txt', 'r', encoding='utf-8') as file:
      lines = file.readlines()[:-1]
  vectors[i] = []
  lines = [i[:-1].split(' ')[0] for i in lines]
  for j in all_lemmas:
    if j in lines:
      vectors[i].append(1)
    else:
      vectors[i].append(0)