import importlib
import sys
from openaitools import call_gpt3
sys.path.append('../utils')
from get_procedure import get_procedure_for_codex
sys.path.append('../data')
sys.path.append('../results')

# set parameters for the experiment
model = 'code-davinci-002' #'text-davinci-003'
max_tokens = 256

with open('../data/api_documentation_01.txt', 'r') as file:
  api_doc = file.read()
with open('../data/task_instructions_01.txt', 'r') as file:
  instructions = file.read()

task_id = 24
procedure, gold = get_procedure_for_codex(task_id, model = model, max_tokens = max_tokens)
prompt = api_doc + instructions + procedure

valid = []
success = []
total = 1

for i in range(total):
  print(f'test number {i}: ', end = '')
  prompt = api_doc + instructions + procedure
  response = call_gpt3(prompt, temp = .5, max_tokens = 480)
  file_name = f'_gpt_generated_code_task_id_{task_id}_test_{i:0>2}'

  with open('../results/' + file_name + '.py', 'w+') as file_id:
    file_id.write('from src.hexagen import HexagonsGame, Shape, Line, Circle, Triangle\n\n')
    file_id.write('def func(pr = False):\n')
    # file_id.write(f"  print(f'code number {i}')\n")
    file_id.write('  HexagonsGame.start()\n')
    file_id.write('  ' + '\n  '.join(response.split('\n')))
    file_id.write('\n\n')
    file_id.write('  if pr:\n')
    file_id.write('    HexagonsGame.plot()\n\n')
    file_id.write('  return HexagonsGame.board_state\n\n')
    file_id.write("if __name__ == '__main__':\n")
    file_id.write('  func(pr=True)\n')

  mod = importlib.import_module(file_name)
  # importlib.reload(mod)

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

print()
print(f'valid: {len(valid)}/{total}')
print(f'success: {len(success)}/{total}')
