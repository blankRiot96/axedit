import json
import subprocess
import sys

directory = "." if len(sys.argv) == 1 else sys.argv[1]


command_str = (
    f"pyright {directory} --outputjson --level=warning --pythonpath='{sys.executable}'"
)
command = command_str.split()

try:
    lsp_data = subprocess.check_output(command)
except subprocess.CalledProcessError as e:
    lsp_data = e.output
lsp_info = json.loads(lsp_data)
print(json.dumps(lsp_info, indent=2))
