Kubernetes MCP Server (Claude Desktop)
Expose safe, focused Kubernetes operations to Claude via a custom MCP server.
This server authenticates with your local ~/.kube/config and provides tools to:
Pods: create, delete, describe (incl. events), get logs
Services: create, delete, describe (incl. events)
⚠️ These tools can mutate your cluster. Use least-privileged credentials and test on non-prod.


1) Prerequisites
macOS / Windows / Linux
Python 3.10+
kubectl configured for your cluster (valid ~/.kube/config)
Claude Desktop installed
macOS: download & install the latest Claude Desktop app
Optional (for EKS): AWS CLI configured (aws sts get-caller-identity works)

2) Quick Start

# 1) Clone your repo (or create a folder)
mkdir k8s-mcp && cd k8s-mcp

# 2) Create & activate a virtual environment
python3 -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .\.venv\Scripts\Activate.ps1

# 3) Install deps
pip install --upgrade pip
pip install mcp kubernetes

# 4) Create the server file
nano server.py  # (paste the code from the next section)

3) Server code (server.py)

This server uses the mcp Python library (FastMCP) and the official Kubernetes Python client.
It authenticates using your local ~/.kube/config .PLease refer the server.py file.

4) Run a quick sanity check

From your project folder:

python3 server.py 

If imports fail, your venv isn’t active or the interpreter path is wrong.

5) Install & configure Claude Desktop
5.1 Install
Download & install Claude Desktop for your OS.
Launch it once, then quit (so the config/log folders are created).
5.2 Add the MCP server entry
Create/update the Claude Desktop config file for your OS:
macOS
~/Library/Application Support/Claude/claude_desktop_config.json
Windows
%AppData%\Claude\claude_desktop_config.json
Linux
~/.config/Claude/claude_desktop_config.json
Add your server under the mcpServers key. Use absolute paths:

sample server.json content

{
  "mcpServers": {
    "k8s-mcp": {
      "command": "/ABSOLUTE/PATH/TO/your/project/.venv/bin/python3",
      "args": ["/ABSOLUTE/PATH/TO/your/project/server.py"]
    }
  }
}


Restart Claude Desktop.
Open Settings → Tools → Developer and ensure k8s-mcp appears and can be enabled.









