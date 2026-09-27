import re,sys
def dec(s):
    def rep(m):
        h=m.group(1); return ''.join(chr(int(h[i:i+4],16)) for i in range(0,len(h),4))
    return re.sub(r'\\X2\\([0-9A-Fa-f]+)\\X0\\', rep, s)
txt=open('model.stp',encoding='latin-1').read()
names=re.findall(r"#(\d+)=PRODUCT\('([^']*)'",txt)
for i,n in names: print(i, dec(n))
