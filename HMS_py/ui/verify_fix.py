import subprocess
import os
result = subprocess.run(['git', 'show', 'HEAD:HMS_py/ui/sidebar_buttons.py'], capture_output=True, text=True)
content = result.stdout
if not content:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    path = os.path.join(base, "HMS_py", "ui", "sidebar_buttons.py")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            content = f.read()
issues = []
if content and 'from HMS_py.core import menu as _um' in content:
    issues.append('unused import still present')
if content and 'housekeping' in content:
    issues.append('typo still present')
if content and 'VB6_MODE' in content:
    issues.append('VB6_MODE still present')
if content and 'btn=b' in content:
    issues.append('btn=b still present')
if content and 'lambda _, ac=item.get' in content and ': ' in content.split('lambda _, ac=item.get')[1].split(chr(10))[0]:
    issues.append('trailing space still present')
if issues:
    print('ISSUES:', issues)
else:
    print('All fixes verified in sidebar_buttons.py')
print('Lines: %d' % len(content.split(chr(10))))