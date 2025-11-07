from pathlib import Path
path = Path(r'c:\Users\86199\Desktop\基于python二手车管理系统\users\models.py')
text = path.read_text('utf-8')
corrupted = sorted(set([w for w in text.split() if '\ufffd' in w]))
print('\n'.join(corrupted))
