'''
This script selects train tasks at random according to your instructions
and creates a csv file with the list of tasks.
This is useful when creating a batch of tasks for parsing.
'''
from constants.constants import ROOT_DIR
import csv
from numpy.random import choice
import os.path
from reading_tasks import read_tasks, retrieve_task

train_tasks = read_tasks(which_tasks=['train'])

tasks_per_category = {}
tasks_per_image = {}
images_per_category = {}

def add_to_dict_set(d, key, item):
  if key not in d.keys():
    d[key] = set()
  d[key].add(item)

for task in train_tasks:
  category = task['category']
  task_id = task['index']
  image_id = task['image_id']
  add_to_dict_set(tasks_per_category, category,  task_id)
  add_to_dict_set(tasks_per_image, image_id,  task_id)
  add_to_dict_set(images_per_category, category,  image_id)

categories = list(images_per_category.keys())
print('Number of categories:', len(categories))
for c in categories:
  print(f'* {c}: {len(images_per_category[c])} images, {len(tasks_per_category[c])} tasks')

num_images_per_category = int(input('\nHow many images do you want to choose per category?\n'))
print('\nHow many tasks do you want to choose per image?')
print('Note that not all images have the same number of tasks. Most images have at least 3 different tasks.')
print("If you choose 'a', all tasks that belong to the image will be chosen.")
temp = input()
num_tasks_per_image = 0 if temp == 'a' else int(temp)

selected_images_per_category = {}
selected_tasks_per_image = {}
selected_tasks_per_category = {}
for c in categories:
  selected_tasks_per_category[c] = []
  choose_from_images = [image_id for image_id in images_per_category[c] if \
                        len(tasks_per_image[image_id]) >= num_tasks_per_image]
  selected_images_per_category[c] = list(choice(choose_from_images, num_images_per_category, replace = False))
  for image_id in selected_images_per_category[c]:
    if num_tasks_per_image == 0:
      selected_tasks_per_image[image_id] = list(tasks_per_image[image_id])
    else:
      choose_from_tasks = list(tasks_per_image[image_id])
      selected_tasks_per_image[image_id] = list(choice(choose_from_tasks, num_tasks_per_image, replace = False))
    selected_tasks_per_category[c] += selected_tasks_per_image[image_id]

print('\nNumber of selected images and tasks per category:')
for c in categories:
  print(f'* {c}: {len(selected_images_per_category[c])} images, {len(selected_tasks_per_category[c])} tasks')

save = input('\nDo you want to save the results to a csv file? [y/n]')

if save == 'y':
  columns = ['image', 'index', 'category', 'collection round', 'drawing steps', 'created file', 'done parsing', 'match', 'discuss', 'parsed by']
  file_name = input('Please enter a name for the batch\n') + '.csv'
  gold_dir = ROOT_DIR / 'gold'
  if os.path.exists(os.path.join(gold_dir, file_name)):
    print(f'\nFile {file_name} already exists! not creating a new file\n')
  else:
    print(f"Creating file {file_name} under 'gold' folder")
    with open(os.path.join(gold_dir, file_name), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        for c in categories:
          for image_id in selected_images_per_category[c]:
            for task_id in selected_tasks_per_image[image_id]:
              task = retrieve_task((task_id))
              writer.writerow([image_id, task_id, c, task['collection_round'], task['number_of_drawing_steps']])

