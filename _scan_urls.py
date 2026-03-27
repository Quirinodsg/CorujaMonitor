import os, re

checks = [
    ('HARDCODED_PORT', r'window\.location\.hostname.*:\d{4}'),
    ('HARDCODED_PORT', r'`\$\{.*hostname.*\}:\d{4}'),
    ('HARDCODED_PORT', r':\d{4}/api'),
    ('LOCALHOST', r'localhost:\d{3,4}'),
    ('HTTP_ABSOLUTE', r"fetch\(['\"]http://"),
    ('HTTP_ABSOLUTE', r'axios\.[a-z]+\([\'"]http://'),
    ('WEBSOCKET', r'new WebSocket\('),
    ('REACT_APP_URL', r'REACT_APP_API_URL'),
    ('PROCESS_ENV', r'process\.env\.REACT_APP'),
]

src = 'frontend/src'
found = {}

for root, dirs, files in os.walk(src):
    dirs[:] = [d for d in dirs if d not in ['node_modules']]
    for f in files:
        if not f.endswith('.js'):
            continue
        path = os.path.join(root, f).replace('\\', '/')
        try:
            content = open(path, encoding='utf-8', errors='ignore').read()
        except:
            continue
        lines = content.split('\n')
        hits = []
        for i, line in enumerate(lines, 1):
            for label, pat in checks:
                if re.search(pat, line):
                    stripped = line.strip()
                    if stripped.startswith('//') or stripped.startswith('*'):
                        continue
                    hits.append((i, label, stripped[:100]))
        if hits:
            found[path] = hits

if not found:
    print("CLEAN — no issues found")
else:
    for path in sorted(found):
        print(f"\n{'='*60}")
        print(f"FILE: {path}")
        for ln, label, text in found[path]:
            print(f"  L{ln:4d} [{label}] {text}")

print(f"\nTotal files with issues: {len(found)}")
