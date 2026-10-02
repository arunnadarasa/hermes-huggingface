#!/usr/bin/env python3
"""Live smoke test for the Hugging Face hf CLI + MCP wiring.

Checks (no secrets printed):
  1. hf CLI is on PATH and reports a version
  2. hf auth whoami resolves an identity (auth works)
  3. A real Hub API call returns live data (hf papers ls)
  4. hermes mcp test huggingface connects and lists tools (if hermes CLI present)
"""
import shutil
import subprocess
import sys


def run(cmd, timeout=60):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def check(name, condition, detail=""):
    condition = bool(condition)
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return condition


def main():
    results = []

    hf_bin = shutil.which("hf")
    results.append(check("hf CLI on PATH", hf_bin, hf_bin or "not found"))
    if not hf_bin:
        print("Cannot continue without hf CLI.")
        sys.exit(1)

    ver = run([hf_bin, "version"])
    results.append(check("hf version reports cleanly", ver.returncode == 0,
                          ver.stdout.strip().splitlines()[-1] if ver.stdout else ""))

    whoami = run([hf_bin, "auth", "whoami"])
    results.append(check("hf auth whoami resolves an identity",
                          whoami.returncode == 0 and "user=" in whoami.stdout,
                          whoami.stdout.strip()))

    papers = run([hf_bin, "papers", "ls", "--limit", "1"])
    got_real_row = papers.returncode == 0 and len(papers.stdout.strip().splitlines()) >= 2
    results.append(check("hf papers ls returns live data (not empty)", got_real_row))

    hermes_bin = shutil.which("hermes")
    if hermes_bin:
        mcp_test = run([hermes_bin, "mcp", "test", "huggingface"], timeout=30)
        results.append(check(
            "hermes mcp test huggingface connects",
            mcp_test.returncode == 0 and "Connected" in mcp_test.stdout,
            "see hermes mcp test huggingface for tool list",
        ))
    else:
        print("[SKIP] hermes CLI not on PATH — skipping MCP connectivity check")

    print()
    passed = sum(results)
    print(f"{passed}/{len(results)} checks passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
