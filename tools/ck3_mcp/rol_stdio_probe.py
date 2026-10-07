"""Exercise the real MCP stdio process using read-only/static tools only."""
import json
from pathlib import Path
import subprocess
import sys


def main() -> int:
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "rol-static-probe", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "ck3_environment", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "ck3_validate_mod", "arguments": {}}},
    ]
    server = Path(__file__).with_name("server.py")
    completed = subprocess.run([sys.executable, str(server)], input="".join(json.dumps(item) + "\n" for item in requests).encode(), capture_output=True, timeout=60, cwd=server.parents[2])
    if completed.returncode or completed.stderr:
        raise RuntimeError(f"MCP process failure: {completed.stderr.decode(errors='replace')}")
    replies = [json.loads(line) for line in completed.stdout.decode("utf-8").splitlines() if line.strip()]
    assert len(replies) == 4 and {item["id"] for item in replies} == {1, 2, 3, 4}, "unexpected response/notification behavior"
    response = {item["id"]: item["result"] for item in replies}
    assert response[1]["protocolVersion"] == "2024-11-05"
    names = [tool["name"] for tool in response[2]["tools"]]
    assert len(names) == len(set(names)) and {"ck3_environment", "ck3_validate_mod"} <= set(names)
    assert response[3]["structuredContent"]["descriptor_exists"]
    validation = response[4]["structuredContent"]
    for item in validation["results"]:
        print(item["stdout"].strip())
        if item["stderr"]: print(item["stderr"].strip())
    assert validation["passed"], "combined validation failed"
    print(f"[OK] Real MCP stdio: initialize/notification, {len(names)} unique tools, environment and combined validation. No CK3 launch/input.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
