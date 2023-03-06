import importlib
import sys
from openaitools import call_gpt3
sys.path.append('../utils')
sys.path.append('../data')
sys.path.append('../results')

# set parameters for the experiment
model = 'code-davinci-002' #'text-davinci-003'
max_total_tokens = {'code-davinci-002':8000, 'text-davinci-003':4000}[model]

with open('../data/api_documentation_01.txt', 'r') as file:
  api_doc = file.read()
with open('../data/task_instructions_01.txt', 'r') as file:
  instructions = file.read()

# conclusion: api_doc + instructions = 3513 tokens with 'code-davinci-002'

prompt = api_doc + instructions
conjectured_prompt_num_tokens = 3500
conjecture_too_low = True
result_max_tokens = 100

try:
  response = call_gpt3(prompt, temp=0.8, max_tokens=result_max_tokens)
  print(f"simple request succeeded, test continues\n")
  while conjecture_too_low:
    add_to_prompt = max_total_tokens - conjectured_prompt_num_tokens - result_max_tokens
    N = add_to_prompt // 2 + 1
    extra = ''
    for i in range(N):
      extra += 'x\n'

    try:
      response = call_gpt3(prompt + extra, temp = 0.8, max_tokens = result_max_tokens)
      print(f"request succeeded with conjecture_prompt_num_tokens = {conjectured_prompt_num_tokens}")
      conjecture_too_low = False
    except:
      print(f"request failed with conjecture_prompt_num_tokens = {conjectured_prompt_num_tokens}")
      conjectured_prompt_num_tokens += 1

except:
  print(f"simple request failed, stopping test")




