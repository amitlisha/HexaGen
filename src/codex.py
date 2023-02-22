import sys
from use_codex import call_codex
sys.path.append('../utils')
from get_procedure import get_procedure_for_codex
sys.path.append('../data')

with open('../data/api_documentation.txt', 'r') as file:
  api_doc = file.read()
with open('../data/instructions.txt', 'r') as file:
  instructions = file.read()
drpr = 24
procedure = get_procedure_for_codex(drpr)
prompt = api_doc + instructions + procedure

call_codex(prompt, temp = .1, max_tokens = 480)
