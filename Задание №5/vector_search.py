from IPython.display import Markdown
warnings.filterwarnings("ignore")

def show_result_files(document_ids):
  if len(document_ids) == 0:
    print('Ничего не найдено!')
    return
  display(Markdown('##Результаты поиска'))
  for document_id in document_ids:
    document_link = all_files_id_and_link_dictionary[str(document_id)]
    display(Markdown(f'* [%s](%s)' % (document_link, document_link)))

#@title ##Поисковая система 'Minecraft Wiki' {run:"auto"}
query = "\u043C\u0430\u0440\u043A\u0443\u0441 \u0438 \u043A\u0438\u0440\u043A\u0430" #@param {type:"string"}
query = re.sub(r'[^а-я]', " ", query.lower())
if len(query) != 0:
  try:
    tokens = word_tokenization([query])

    pymorphy2_analyzer = MorphAnalyzer()
    normal_form = []
    for j in tokens:
      ana = pymorphy2_analyzer.parse(j)
      normal_form.append(ana[0].normal_form)
    indexing = []
    for i in all_lemmas:
      if i in normal_form:
        indexing.append(1)
      else:
        indexing.append(0)
    if 1 in indexing:
      for k, v in vectors.items():
        cos_distance[k] = spatial.distance.cosine(v, indexing)

      sorted_keys = sorted(cos_distance, key=cos_distance.get)
      filtered_sorted_keys = list(filter(lambda key: cos_distance[key] != 1.0, sorted_keys))
      for key in filtered_sorted_keys:
        cos = cos_distance[key]
        print(str(key) + ' - ' + str(cos))
      show_result_files(filtered_sorted_keys)
        
    else:
        print('Введённые слова не были найдены в словаре')
  except:
    print('Ничего не найдено по вашему запросу!')
else:
  print('Ничего не найдено по вашему запросу!')