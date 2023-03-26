'''Get Task
Methods that read drawing tasks info from the 'jsonl' files,
and return them in useful formats.

read_task
search_tasks_by_keyword
'''

from constants.constants import ROOT_DIR
import json
from os.path import join
import re
import textwrap

# jsonl files that contain all the tasks
data_dir = ROOT_DIR / 'data'
f_train = '2022_01_19_hexagon_dataset_extended_public_hard1_train.jsonl'
f_dev = '2022_01_19_hexagon_dataset_extended_public_hard1_dev_abstraction.jsonl'
f_test = '2022_01_19_hexagon_dataset_extended_public_hard1_test.jsonl'

def read_tasks(which_tasks=['train','dev','test']):
  ''' Read the entire dataset of tasks
  The dataset is divided into train, dev and test.
  By default all tasks will be read,
  but you can specify which of the three parts to read
  '''
  train_tasks, dev_tasks, test_tasks = [], [], []
  if 'train' in which_tasks:
    with open(join(data_dir, f_train)) as jsonl_file:
        train_tasks = [json.loads(command) for command in jsonl_file]
        for task in train_tasks:
          task['group'] = 'train'
  if 'dev' in which_tasks:
    with open(join(data_dir, f_dev)) as jsonl_file:
        dev_tasks = [json.loads(command) for command in jsonl_file]
        for task in dev_tasks:
          task['group'] = 'dev'
  if 'test' in which_tasks:
    with open(join(data_dir, f_test)) as jsonl_file:
        test_tasks = [json.loads(command) for command in jsonl_file]
        for task in test_tasks:
          task['group'] = 'test'
  return train_tasks + dev_tasks + test_tasks

def retrieve_task(task_index):
  '''Retrieve a single task data from the jsonl files'''
  tasks = read_tasks()
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

def read_task(task_ind, print_description=False):
  '''Read a task and return the processed information'''
  task = retrieve_task(task_ind)
  task_dict = {'instructions': extract_instructions(task), 'gold_boards': extract_boards(task),
          'description': extract_description(task)}
  if print_description:
    print(task_dict['description'])
  return task_dict

def search_tasks_by_keyword(reg_exp, at_least=1, avoid_reg_exp=None, which_tasks=['train','dev','test']):
  '''search for tasks by a keyword in the drawing instructions

  Parameters:
  -----------
  reg_exp: string
    A regular expression to search in the text.
    For example, to search the word 'repeat' or 'Repeat', set reg_exp to '[Rr]epeat'.
  at_least: int
    The minimal number of times rex_exp should appear in the text. Default: 1
  avoid_reg_exp:
    Another regular expression you wish to be absent from the text. Default: None
  which_tasks:
    The list of task groups you wish to search in. Default: ['train', 'dev', 'test']

  Returns:
  ------------
  List[int]
    a list of task indices
  '''

  if avoid_reg_exp is None:
    print(f"Searching for drawing instructions in {which_tasks} that contain the regular expression '{reg_exp}'"
          f' at least {at_least} times')
  else:
    print(f"Searching for drawing instructions in {which_tasks} that contain the regular expression '{reg_exp}'"
          f" at least {at_least} times and do not contain the regular expression ''{avoid_reg_exp}'")
  tasks_inds_that_contain_keyword = []
  tasks = read_tasks(which_tasks=which_tasks)
  for task in tasks:
    instructions =  ' '.join([_[1] for _ in task['drawing_procedure'][1:]])
    if (len(re.findall(reg_exp, instructions)) >= at_least) \
        and (avoid_reg_exp is None or len(re.findall(avoid_reg_exp, instructions)) == 0):
        tasks_inds_that_contain_keyword.append(task['index'])
  print(f'Found {reg_exp} in {len(tasks_inds_that_contain_keyword)} tasks')
  return tasks_inds_that_contain_keyword

if __name__ == '__main__':
  # tasks_containing_repeat = search_tasks_by_keyword('[Ss]tep')
  # ind = 0
  # while input("press enter to show the next task, press 's' and then enter to stop") == '':
  #   task_dict = read_task(tasks_containing_repeat[ind], True)
  #   print(task_dict['instructions'])
  #   ind += 1

  print(read_task(1, True)['instructions'])
