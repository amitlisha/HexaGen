# set params
H = 10 # number of lines
W = 18 # number of rows
num_colors = 8

import json
import textwrap
import sys
import plot_board as pb

sys.path.append('../data')
data_dir_name = '../data/'

# reading procedures from json files
f_train = '2022_01_19_hexagon_dataset_extended_public_hard1_train.jsonl'
f_dev = '2022_01_19_hexagon_dataset_extended_public_hard1_dev_abstraction.jsonl'
f_test = '2022_01_19_hexagon_dataset_extended_public_hard1_test.jsonl'

def get_info(drpr):
  with open(data_dir_name + f_train) as jsonl_file:
      train_procedures = [json.loads(command) for command in jsonl_file]
      for procedure in train_procedures:
        procedure['group'] = 'train'
  with open(data_dir_name + f_dev) as jsonl_file:
      dev_procedures = [json.loads(command) for command in jsonl_file]
      for procedure in dev_procedures:
        procedure['group'] = 'dev'
  with open(data_dir_name + f_test) as jsonl_file:
      test_procedures = [json.loads(command) for command in jsonl_file]
      for procedure in test_procedures:
        procedure['group'] = 'test'
  procedures = train_procedures + dev_procedures + test_procedures
  drpr_inds = [d['index'] for d in procedures]
  id = drpr_inds.index(drpr)
  d = procedures[id]
  return d

def get_description(d):
  return f"procedure {d['index']}, image {d['image_index']}, collection round {d['collection_round']}, category {d['category']}, group {d['group']}"

def get_boards(d):
  dr_pr = d['drawing_procedure'][1:]
  Bs = [_[2] for _ in dr_pr]
  return Bs

def get_procedure(drpr, plot = False):
  d = get_info(drpr)
  description = get_description(d)
  Bs = get_boards(d)
  print(description, '\n')
  for i,txt in enumerate([_[1] for _ in d['drawing_procedure'][1:]]):
    wrap_txt = '\n'.join(textwrap.wrap(txt, width=120))
    print(f'{i + 1}. {wrap_txt}')
    # print(f'{i+1}. {txt}')
  print()
  if plot:
    pb.plot_boards(Bs, max_in_row = 3, fig_size = [4,4])
  return Bs, description

def get_procedure_for_codex(drpr, pr = False):
  d = get_info(drpr)
  s = ''
  for i,txt in enumerate([_[1] for _ in d['drawing_procedure'][1:]]):
    wrap_txt = '\n'.join(textwrap.wrap(txt, width=120))
    s += f"'''\n{i + 1}. {wrap_txt}\n'''\n\n"
    # s += '# complete code here\n\n'
  if pr:
    print(s)
  gold = get_boards(d)[-1]
  return s, gold

if __name__ == '__main__':
  drpr = 24
  get_procedure_for_codex(drpr, True)
