'''
This script takes a task_ind, creates a prompt, runs it through GPT using the API,
writes the response (which is Python code that creates a board) to a Python file,
tries to run the file, if the file can run it compares the board to the gold board.

Before running experiments for some task, for example 16, create a folder 'gpt/results/task_15'
'''

import importlib
import sys
from openai_tools import call_gpt
sys.path.append('../utils')
from reading_tasks import read_task
sys.path.append('../data')
sys.path.append('../results')

# set parameters for the experiment
task_ind = 24
total = 3 # total number of a experiments to run with gpt
model = 'text-davinci-003'
max_tokens = 256
temp = 0.5

# creating a prompt
# reading the api documentation
with open('../data/api_documentation_01.txt', 'r') as file:
  api_doc = file.read()
# reading the instructions for gpt describing the general setup
with open('../data/gpt_instructions_01.txt', 'r') as file:
  gpt_instructions = file.read()
task_dict = read_task(task_ind=task_ind)
task_instructions = task_dict['instructions_for_gpt']
gold = task_dict['gold_boards'][-1]
# procedure, gold = get_procedure_for_codex(task_ind, model = model, max_tokens = max_tokens)
prompt = api_doc + gpt_instructions + task_instructions

valid = [] # counts how many responses have valid Python code (the code runs without collapsing)
success = []  # counts how many of the responses produce the correct board

for i in range(total):
  print(f'\n*** test number {i}')

  # using the API to access GPT and get a response
  # the response is supposed to be in the form of Python code
  response = call_gpt(prompt, model=model, temp=temp, max_tokens=max_tokens)

  # use this to test the script
  # response = f"print('Im inside file of test number {i}')\n"

  # file_name to write the response to
  file_name = f'gpt_generated_code_task_ind_{task_ind}_test_{i:0>2}'

  # write the response to the file
  # wrap it with all the necessary imports and commands to run the code
  with open(f'results/task_{task_ind}/{file_name}.py', 'w+') as file_id:
    file_id.write('from src.hexagen import HexagonsGame, Shape, Line, Circle, Triangle\n\n')
    file_id.write('def func(pr=False):\n')
    # file_id.write(f"  print(f'code number {i}')\n")
    file_id.write('  HexagonsGame.start()\n\n')
    file_id.write('  ' + '\n  '.join(response.split('\n')))
    file_id.write('\n\n')
    file_id.write('  if pr:\n')
    file_id.write('    HexagonsGame.plot()\n\n')
    file_id.write('  return HexagonsGame.board_state\n\n')
    file_id.write("if __name__ == '__main__':\n")
    file_id.write('  func(pr=False)\n')

  # import the newly created Python file
  mod = importlib.import_module(f'results.task_{task_ind}.{file_name}')
  # importlib.reload(mod)

  # try to run the newly created Python file
  try:
    board_state = mod.func(pr = False)
    valid += [i]
    if gold == board_state:
      success += [i]
      print('valid, exact answer')
    else:
      print('valid, wrong answer')
  except:
    print('not valid')

print(f'\nFinished {total} experminets for task {task_ind}')
print(f'valid gpt responses:      {len(valid)}/{total}')
print(f'successful gpt responses: {len(success)}/{total}')
