import os
import tempfile
file_path = 'tests/test_08-edit-expense.py'
with open(file_path, 'r') as f:
    content = f.read()
content = content.replace('\"DATABASE\": \":memory:\",', '\"DATABASE\": tempfile.mkstemp()[1],')
with open(file_path, 'w') as f:
    f.write(content)
