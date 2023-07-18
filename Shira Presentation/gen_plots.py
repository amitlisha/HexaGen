'''
This script was used to create plots for Shira's presentation in the lab meeting
'''

from utils.reading_tasks import read_task
from src.plot_board import plot_boards
import textwrap

task_id = 132

d = read_task(task_id, True)
steps = [1,2]
show_first_instruction = False

def edit_instruction(step):
  txt = f"{d['full']['drawing_procedure'][step][1]}"
  return f"INSTRUCTION {step}:\n" + '\n'.join(textwrap.wrap(txt, width=60))

boards = [d['gold_boards'][_-1] for _ in steps]
titles = [edit_instruction(_) for _ in steps]
print(titles)
if not show_first_instruction:
  titles[0] = 'INITIAL STATE'

# print(titles[0])

# fig = plot_boards(boards=boards, max_in_row=2)
fig = plot_boards(boards=boards, titles=titles, max_in_row=2)
# fig.suptitle('This is a somewhat long figure title', fontsize=16)
# fig.savefig(f'task_{str(task_id)}_steps_{steps}')

#
# file_name = input('please enter file name\n')
# if file_name == '':
#   HexagonsGame.plot()
# else:
#   HexagonsGame.plot(file_name = 'board_examples/' + file_name)
#

