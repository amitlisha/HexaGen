import os.path
import sys
sys.path.append('../src')
sys.path.append('../utils')

from get_procedure import get_instructions

drpr = 432
inst, desc = get_instructions(drpr)

with open('../gold/template.txt', 'r') as file:
  template = file.read()

template = template.split('\n')

file_name = f'gold_{drpr:0>3}'
file_path = '../gold/' + file_name + '.py'
if os.path.exists(file_path):
  print(f'file {file_name} already exists')
else:
  print(f'creating file {file_name}')
  with open(file_path, 'w+') as file_id:
    file_id.write('\n'.join(template[:8]))
    file_id.write(f'\ndrpr = {drpr}\n')
    file_id.write('\n'.join(template[9:14]))
    file_id.write(f'\n# {desc}\n\n')
    file_id.write(inst)
    file_id.write('\n'.join(template[18:]))


