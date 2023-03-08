'''Get Task
Methods that read drawing tasks info from the 'jsonl' files,
and return them in useful formats.
'''

# set params
H = 10 # number of lines
W = 18 # number of rows
num_colors = 8

import json
import textwrap
import sys

sys.path.append('../data')
data_dir_name = '../data/'

# jsonl files that contain all the tasks
f_train = '2022_01_19_hexagon_dataset_extended_public_hard1_train.jsonl'
f_dev = '2022_01_19_hexagon_dataset_extended_public_hard1_dev_abstraction.jsonl'
f_test = '2022_01_19_hexagon_dataset_extended_public_hard1_test.jsonl'

def retrieve_task(task_index):
  '''Retrieve a single task data from the jsonl files'''
  with open(data_dir_name + f_train) as jsonl_file:
      train_tasks = [json.loads(command) for command in jsonl_file]
      for procedure in train_tasks:
        procedure['group'] = 'train'
  with open(data_dir_name + f_dev) as jsonl_file:
      dev_tasks = [json.loads(command) for command in jsonl_file]
      for procedure in dev_tasks:
        procedure['group'] = 'dev'
  with open(data_dir_name + f_test) as jsonl_file:
      test_tasks = [json.loads(command) for command in jsonl_file]
      for procedure in test_tasks:
        procedure['group'] = 'test'
  tasks = train_tasks + dev_tasks + test_tasks
  task_inds = [task['index'] for task in tasks]
  task = tasks[task_inds.index(task_index)]
  return task

def extract_description(task):
  '''Extract the task description from the task info'''
  print(task.keys())
  return f"# task index: {task['index']}, " \
         f"image: {task['image_index']}, " \
         f"collection round: {task['collection_round']}, " \
         f"category: {task['category']}, " \
         f"group: {task['group']}\n" \
         f"# agreement scores: {task['agreement_scores']}"

def extract_boards(task):
  '''Extract the boards from the task info'''
  drawing_procedure = task['drawing_procedure'][1:]
  Bs = [_[2] for _ in drawing_procedure]
  return Bs

def extract_instructions(task):
  '''Extract the instructions from the task info'''
  instructions = ''
  for i, txt in enumerate([_[1] for _ in task['drawing_procedure'][1:]]):
    wrap_txt = '\n'.join(textwrap.wrap(txt, width=80))
    instructions += f"'''\n{i + 1}. {wrap_txt}\n'''\n\n"
  return instructions

def read_task(task_ind, print_description = False):
  '''Read a task and return the processed information'''
  task = retrieve_task(task_ind)
  task_dict = {'instructions': extract_instructions(task), 'gold_boards': extract_boards(task),
          'description': extract_description(task)}
  if print_description:
    print(task_dict['description'])
  return task_dict

if __name__ == '__main__':
  task_ind = 1
  read_task(task_ind, True)
