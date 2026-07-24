"""Minimal stand-in for the `higgsfield-client` SDK (PyPI is unreachable in this
environment). Implements the two functions generate_static.py needs, against the
Higgsfield platform API directly:

  upload_file(path) -> public URL
      The platform API has no upload endpoint reachable here; input images must be
      public HTTPS URLs. This repo is public on GitHub, so files already committed
      and pushed resolve to their raw.githubusercontent.com URL; anything else is
      copied into assets/uploads/, committed, pushed, and served the same way.

  subscribe(model_path, arguments={...}) -> {"images": [{"url": ...}]}
      Creates a nano-banana job (POST /v1/text2image/nano-banana — verified live:
      params require prompt, input_images[{type:"image_url",image_url}], and
      aspect_ratio), then polls the job set until it completes.

Credentials come from HF_API_KEY + HF_API_SECRET (or HF_KEY="key:secret") in the
environment only.
"""

import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request

API_BASE = "https://platform.higgsfield.ai"
GENERATE_ENDPOINT = os.environ.get(
    "WINNING_STATICS_HF_ENDPOINT", API_BASE + "/v1/text2image/nano-banana")
POLL_INTERVAL = 5
POLL_TIMEOUT = 900


def _credentials():
    key = os.environ.get("HF_API_KEY")
    secret = os.environ.get("HF_API_SECRET")
    if not (key and secret) and os.environ.get("HF_KEY"):
        key, _, secret = os.environ["HF_KEY"].partition(":")
    if not (key and secret):
        raise RuntimeError("no Higgsfield credentials: set HF_API_KEY + HF_API_SECRET "
                           "(or HF_KEY='key:secret')")
    return key, secret


def _request(method, url, payload=None, timeout=60):
    key, secret = _credentials()
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "hf-api-key": key, "hf-secret": secret, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {url} -> HTTP {e.code}: {body[:500]}") from None


def _git(repo_root, *argv):
    proc = subprocess.run(["git", "-C", repo_root] + list(argv),
                          capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(argv)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _repo_info(path):
    repo_root = _git(os.path.dirname(os.path.abspath(path)) or ".",
                     "rev-parse", "--show-toplevel")
    remote = _git(repo_root, "remote", "get-url", "origin")
    # Remotes may be rewritten through a local git proxy — keep only the trailing
    # owner/repo pair, which survives any prefix.
    parts = remote.replace(":", "/").rstrip("/").split("/")
    if len(parts) < 2:
        raise RuntimeError(f"cannot parse owner/repo from remote: {remote}")
    slug = f"{parts[-2]}/{parts[-1]}"
    if slug.endswith(".git"):
        slug = slug[:-4]
    branch = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    return repo_root, slug, branch


def _raw_url(slug, branch, rel_path):
    return f"https://raw.githubusercontent.com/{slug}/{branch}/{rel_path}"


def _push(repo_root, branch):
    delay = 2
    for attempt in range(4):
        try:
            _git(repo_root, "push", "-u", "origin", branch)
            return
        except RuntimeError:
            if attempt == 3:
                raise
            time.sleep(delay)
            delay *= 2


def upload_file(path):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise RuntimeError(f"file not found: {path}")
    repo_root, slug, branch = _repo_info(path)
    rel = os.path.relpath(path, repo_root)

    if not rel.startswith(".."):
        committed = subprocess.run(
            ["git", "-C", repo_root, "ls-files", "--error-unmatch", rel],
            capture_output=True).returncode == 0
        clean = subprocess.run(
            ["git", "-C", repo_root, "diff", "--quiet", "HEAD", "--", rel],
            capture_output=True).returncode == 0
        if committed and clean:
            local = _git(repo_root, "rev-parse", f"{branch}:{rel}")
            remote = subprocess.run(
                ["git", "-C", repo_root, "rev-parse", f"origin/{branch}:{rel}"],
                capture_output=True, text=True)
            if remote.returncode == 0 and remote.stdout.strip() == local:
                return _raw_url(slug, branch, rel)
            _push(repo_root, branch)
            return _raw_url(slug, branch, rel)

    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]
    dest_rel = f"assets/uploads/{digest}-{os.path.basename(path)}"
    dest = os.path.join(repo_root, dest_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest):
        shutil.copyfile(path, dest)
    _git(repo_root, "add", dest_rel)
    if subprocess.run(["git", "-C", repo_root, "diff", "--cached", "--quiet"],
                      capture_output=True).returncode != 0:
        _git(repo_root, "commit", "-m", f"Add generation input {dest_rel}")
    _push(repo_root, branch)
    return _raw_url(slug, branch, dest_rel)


def _find_image_urls(node, out):
    if isinstance(node, dict):
        # Prefer the full-resolution variant when a results object offers both.
        if "raw" in node and isinstance(node["raw"], dict) and node["raw"].get("url"):
            out.append(node["raw"]["url"])
        elif node.get("url") and isinstance(node["url"], str):
            out.append(node["url"])
        for v in node.values():
            _find_image_urls(v, out)
    elif isinstance(node, list):
        for v in node:
            _find_image_urls(v, out)


def subscribe(model_path, arguments=None):
    arguments = arguments or {}
    urls = (arguments.get("image_urls") or arguments.get("input_images")
            or arguments.get("images") or [])
    params = {
        "prompt": arguments.get("prompt", ""),
        "aspect_ratio": arguments.get("aspect_ratio", "1:1"),
        "input_images": [{"type": "image_url", "image_url": u} for u in urls],
    }
    created = _request("POST", GENERATE_ENDPOINT, {"params": params}, timeout=120)

    job_set_id = created.get("id") or created.get("job_set_id")
    if not job_set_id:
        found = []
        _find_image_urls(created, found)
        if found:
            return {"images": [{"url": found[0]}]}
        raise RuntimeError(f"unexpected create response: {json.dumps(created)[:500]}")

    deadline = time.time() + POLL_TIMEOUT
    status = "queued"
    while time.time() < deadline:
        state = _request("GET", f"{API_BASE}/v1/job-sets/{job_set_id}")
        jobs = state.get("jobs") or [state]
        statuses = [j.get("status") for j in jobs]
        if any(s in ("failed", "nsfw", "canceled", "cancelled") for s in statuses):
            raise RuntimeError(f"job failed: {json.dumps(state)[:500]}")
        if statuses and all(s in ("completed", "succeeded", "success") for s in statuses):
            found = []
            _find_image_urls(state, found)
            if not found:
                raise RuntimeError(f"completed but no image URL: {json.dumps(state)[:500]}")
            return {"images": [{"url": u} for u in found]}
        status = statuses[0] if statuses else status
        time.sleep(POLL_INTERVAL)
    raise RuntimeError(f"timed out after {POLL_TIMEOUT}s (last status: {status}, "
                       f"job set {job_set_id})")
