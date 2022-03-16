REGEX = r'([\w]+|[,?;.:\/!()\[\]\'"’\\><+-=])'
OPERATORS = ['И', 'ИЛИ']
BASE_NAME = "/content/urls/"
BASE_EXTENSION = ".html"

def get_priority_of_operator(operator):
  if operator == 'И':
    return 2
  if operator == 'ИЛИ':
    return 1

def get_file_ids(token):
  result = morph.parse(token)[0]
  lemma = result.normal_form
  if lemma not in inverted_index_dictionary:
    return []
  ids = []
  for item in inverted_index_dictionary[lemma]:
    ids.append(item)
  return ids

def calculate(sbOut):
  dA = 0
  dB = 0
  stack = []
  used_symbols = 0
  while used_symbols < len(sbOut):
    symbol = sbOut[used_symbols]
    if symbol in OPERATORS:
      dB = stack.pop()
      dA = stack.pop()
      if symbol == 'И':
        dA = list(set(dA) & set(dB))
      if symbol == 'ИЛИ':
        dA = list(set(dA + dB))
    else:
      dA = get_file_ids(symbol)
    stack.append(dA)
    used_symbols = used_symbols + 1
  return stack

def boolean_search(elements):
  sbStack = []
  sbOut = []
  for element in elements:
    if element in OPERATORS:
      while len(sbStack) > 0:
        cTmp = sbStack[len(sbStack) - 1]
        if cTmp in OPERATORS and (get_priority_of_operator(element) <= get_priority_of_operator(cTmp)):
          sbOut.append(cTmp)
          sbStack.pop()
        else:
          break
      sbStack.append(element)
    elif element == '(':
      sbStack.append(element)
    elif element == ')':
      cTmp = sbStack.pop()
      while '(' != cTmp:
        if len(sbStack) < 1:
            print('Произошла непредвиденная ошибка!')
        sbOut.append(cTmp)
        cTmp = sbStack.pop()
    else:
      sbOut.append(element)
  while len(sbStack) > 0:
    sbOut.append(sbStack.pop())
  return calculate(sbOut)[0]

def show_result_files(document_ids):
  if len(document_ids) == 0:
    print('Ничего не найдено!')
    return
  document_names = []
  for document_id in document_ids:
    document_names.append(BASE_NAME + str(document_id) + BASE_EXTENSION)
  document_names.sort()
  print('Результаты поиска:')
  for document in document_names:
    print(document)

query_string = "маркус И (игра ИЛИ ночь)"
elements = re.findall(REGEX, query_string)
results = boolean_search(elements)
show_result_files(results)