import os
file_path = 'tests/test_08-edit-expense.py'
with open(file_path, 'r') as f:
    content = f.read()
if 'import tempfile' not in content:
    content = 'import tempfile\n' + content
with open(file_path, 'w') as f:
    f.write(content)
