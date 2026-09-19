"""Fetch the show's web fonts as woff2 (latin subset) into assets/fonts/.
   build.py embeds them into the STANDALONE and docs so the projection machine never
   depends on theatre Wi-Fi — the type is the show (David, Sept 19 night). Re-run only
   when a family or weight changes; the files are committed."""
import os, re, subprocess
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CA = "/root/.ccr/ca-bundle.crt"
FAMILIES = [
    ("Archivo",      "Archivo:wght@300..700"),
    ("Courier Prime","Courier+Prime:wght@400;700"),
    ("Fraunces",     "Fraunces:opsz,wght@9..144,300..700"),
    ("Inter",        "Inter:wght@300..800"),
    ("Poppins",      "Poppins:wght@500;600;700;800"),
]
OUT = "assets/fonts"; os.makedirs(OUT, exist_ok=True)

def curl(url, binary=False):
    r = subprocess.run(["curl","-sS","--cacert",CA,"-A",UA,url], capture_output=True)
    if r.returncode: raise SystemExit("curl failed: "+r.stderr.decode()[:200])
    return r.stdout if binary else r.stdout.decode()

manifest=[]
for fam, q in FAMILIES:
    css = curl(f"https://fonts.googleapis.com/css2?family={q}&display=swap")
    blocks = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)
    for b in blocks:
        ur = re.search(r"unicode-range:\s*([^;]+);", b)
        if not ur or "U+0000-00FF" not in ur.group(1): continue      # latin only
        url = re.search(r"url\((https://[^)]+\.woff2)\)", b).group(1)
        wt  = re.search(r"font-weight:\s*([^;]+);", b).group(1).strip()
        sty = re.search(r"font-style:\s*([^;]+);", b).group(1).strip()
        name = f"{fam.replace(' ','')}-{wt.replace(' ','_')}-{sty}.woff2"
        open(os.path.join(OUT,name),"wb").write(curl(url, True))
        manifest.append((name, fam, wt, sty, os.path.getsize(os.path.join(OUT,name))))
        print(f"  {name:44s} {os.path.getsize(os.path.join(OUT,name)):>7,} B")
print(f"{len(manifest)} faces, {sum(m[4] for m in manifest):,} B total")
