import sys,os,collections,re
from bs4 import BeautifulSoup, Comment
d=sys.argv[1]; seen=collections.OrderedDict()
for f in sys.argv[2:]:
    s=BeautifulSoup(open(os.path.join(d,f)).read(),'html.parser')
    for t in s.find_all(['script','style','noscript','template','svg']): t.decompose()
    for n in s.find_all(string=True):
        if isinstance(n,Comment): continue
        x=' '.join(n.split())
        if len(x)<2: continue
        seen.setdefault(x,[]).append(f[:3])
for k,v in seen.items(): print(f"{','.join(sorted(set(v)))}\t{k}")
