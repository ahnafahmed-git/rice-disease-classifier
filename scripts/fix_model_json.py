# run from project root: python scripts/fix_model_json.py
import json, re

path = 'frontend/public/model/model.json'
with open(path) as f:
    content = f.read()

content = content.replace('"batch_shape":', '"batch_input_shape":')

with open(path, 'w') as f:
    f.write(content)

print("Done.")