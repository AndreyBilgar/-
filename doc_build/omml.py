# Minimal LaTeX-subset -> OMML converter for article equations
import re
from xml.sax.saxutils import escape
MNS='http://schemas.openxmlformats.org/officeDocument/2006/math'
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
SYM={'cdot':'·','times':'×','approx':'≈','le':'≤','ge':'≥','leq':'≤','geq':'≥','pm':'±','infty':'∞','to':'→','Rightarrow':'⇒',
 'in':'∈','ll':'≪','gg':'≫','sim':'∼','ne':'≠','partial':'∂','Delta':'Δ','Sigma':'Σ','alpha':'α','beta':'β','gamma':'γ','delta':'δ',
 'zeta':'ζ','eta':'η','kappa':'κ','mu':'μ','nu':'ν','rho':'ρ','sigma':'σ','tau':'τ','phi':'ϕ','varphi':'φ','omega':'ω','Omega':'Ω',
 'theta':'θ','lambda':'λ','pi':'π','xi':'ξ','epsilon':'ε','varepsilon':'ε','langle':'⟨','rangle':'⟩','quad':' ','qquad':'  ',
 ',':' ',';':' ',' ':' ','!':'','{':'{','}':'}','|':'‖','ldots':'…','dots':'…','prime':'′','star':'*','minus':'−','deg':'°','lvert':'|','rvert':'|',"'":'′','ell':'ℓ','Theta':'Θ','Phi':'Φ','Psi':'Ψ','psi':'ψ','chi':'χ','cdots':'⋯','sum_':'∑','neq':'≠','propto':'∝','equiv':'≡','circ':'∘','oplus':'⊕'}
FUNCS={'max','min','ln','exp','sin','cos','arcsin','arccos','tanh','sign','arg','det','lim','argmin','tg','sh','ch','th'}
ACC={'dot':'̇','ddot':'̈','bar':'̅','hat':'̂','tilde':'̃','vec':'⃗'}
def isCyr(c): return 'Ѐ'<=c<='ӿ'
def run(text, plain=False, bold=False):
    rpr=''
    if plain or bold:
        rpr='<m:rPr>'+('<m:sty m:val="%s"/>'%('b' if bold and not plain else ('p' if not bold else 'b')))+'</m:rPr>'
    wr='<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>'
    return '<m:r>%s%s<m:t xml:space="preserve">%s</m:t></m:r>'%(rpr,wr,escape(text))
class P:
    def __init__(s,src): s.s=src; s.i=0
    def peek(s): return s.s[s.i] if s.i<len(s.s) else None
    def group(s):
        # expects '{'
        assert s.s[s.i]=='{', (s.s, s.i)
        s.i+=1; out=s.seq(stop='}'); s.i+=1; return out
    def arg(s):
        while s.peek()==' ': s.i+=1
        if s.peek()=='{': return s.group()
        return s.atom()
    def cmd(s):
        s.i+=1
        m=re.match(r'[A-Za-z]+',s.s[s.i:])
        if m: name=m.group(0); s.i+=len(name)
        else: name=s.s[s.i]; s.i+=1
        return name
    def atom(s):
        c=s.peek()
        if c=='{': return ''.join(s.group())
        if c=='\\':
            name=s.cmd()
            if name=='frac':
                a=''.join(s.arg()); b=''.join(s.arg()); return '<m:f><m:num>%s</m:num><m:den>%s</m:den></m:f>'%(a,b)
            if name=='sqrt':
                a=''.join(s.arg()); return '<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>%s</m:e></m:rad>'%a
            if name in ('text','mathrm','textrm'):
                assert s.peek()=='{'; j=s.s.index('}',s.i); t=s.s[s.i+1:j]; s.i=j+1; return run(t,plain=True)
            if name=='mathbf':
                assert s.peek()=='{'; j=s.s.index('}',s.i); t=s.s[s.i+1:j]; s.i=j+1; return run(t,bold=True)
            if name in ACC:
                a=''.join(s.arg()); return '<m:acc><m:accPr><m:chr m:val="%s"/></m:accPr><m:e>%s</m:e></m:acc>'%(ACC[name],a)
            if name in ('sum','int','prod'):
                ch={'sum':'∑','int':'∫','prod':'∏'}[name]; sub=sup=None
                for _ in range(2):
                    while s.peek()==' ': s.i+=1
                    if s.peek()=='_': s.i+=1; sub=''.join(s.arg())
                    elif s.peek()=='^': s.i+=1; sup=''.join(s.arg())
                body=''.join(s.arg())
                pr='<m:naryPr><m:chr m:val="%s"/><m:limLoc m:val="%s"/>%s%s</m:naryPr>'%(ch,'undOvr' if name!='int' else 'subSup','' if sub is not None else '<m:subHide m:val="1"/>','' if sup is not None else '<m:supHide m:val="1"/>')
                return '<m:nary>%s<m:sub>%s</m:sub><m:sup>%s</m:sup><m:e>%s</m:e></m:nary>'%(pr,sub or '',sup or '',body)
            if name=='left':
                o=s.s[s.i]
                if o=='\\': o=s.cmd(); o={'{':'{','langle':'⟨','|':'‖','lvert':'|'}.get(o,o)
                else: s.i+=1
                inner=s.seq(stop='\\right')
                s.i+=len('\\right'); cl=s.s[s.i]
                if cl=='\\': cl=s.cmd(); cl={'}':'}','rangle':'⟩','|':'‖','rvert':'|'}.get(cl,cl)
                else: s.i+=1
                if cl=='.': cl=''
                if o=='.': o=''
                return '<m:d><m:dPr><m:begChr m:val="%s"/><m:endChr m:val="%s"/></m:dPr><m:e>%s</m:e></m:d>'%(escape(o),escape(cl),''.join(inner))
            if name=='cases':
                rows=s.rows(); inner=''.join('<m:e>%s</m:e>'%(run('\u2003',plain=True).join(''.join(c) for c in r)) for r in rows)
                return '<m:d><m:dPr><m:begChr m:val="{"/><m:endChr m:val=""/></m:dPr><m:e><m:eqArr>%s</m:eqArr></m:e></m:d>'%inner
            if name=='mat':
                rows=s.rows(); ncol=max(len(r) for r in rows)
                mr=''.join('<m:mr>%s</m:mr>'%''.join('<m:e>%s</m:e>'%''.join(c) for c in r) for r in rows)
                return '<m:d><m:dPr><m:begChr m:val="["/><m:endChr m:val="]"/></m:dPr><m:e><m:m><m:mPr><m:mcs><m:mc><m:mcPr><m:count m:val="%d"/><m:mcJc m:val="center"/></m:mcPr></m:mc></m:mcs></m:mPr>%s</m:m></m:e></m:d>'%(ncol,mr)
            if name in FUNCS: return run(name,plain=True)
            if name=='op':
                j=s.s.index('}',s.i); t=s.s[s.i+1:j]; s.i=j+1; return run(t,plain=True)
            if name in SYM: return run(SYM[name], plain=not name.isalpha() or name in ('quad','qquad'))
            raise ValueError('unknown cmd '+name)
        s.i+=1
        if c.isdigit():
            j=s.i
            while j<len(s.s) and (s.s[j].isdigit() or (s.s[j]==',' and j+1<len(s.s) and s.s[j+1].isdigit())): j+=1
            t=c+s.s[s.i:j]; s.i=j; return run(t)
        if isCyr(c):
            j=s.i
            while j<len(s.s) and isCyr(s.s[j]): j+=1
            t=c+s.s[s.i:j]; s.i=j; return run(t,plain=True)
        if c=='-': return run('−')
        if c=="'": return run('′')
        if c=='*': return run('\u2217')
        if c=='|': return run('\u2223')
        return run(c)
    def rows(s):
        assert s.peek()=='{'; s.i+=1
        rows=[[[]]]
        while True:
            while s.peek()==' ': s.i+=1
            c=s.peek()
            if c=='}': s.i+=1; break
            if s.s.startswith('\\\\',s.i): s.i+=2; rows.append([[]]); continue
            if c=='&': s.i+=1; rows[-1].append([]); continue
            rows[-1][-1].extend(s.scripted())
        return rows
    def scripted(s):
        while s.peek()==' ': s.i+=1
        if s.peek() is None: return []
        base=s.atom()
        sub=sup=None
        while s.peek() in ('_','^'):
            k=s.peek(); s.i+=1; a=''.join(s.arg())
            if k=='_': sub=a
            else: sup=a
        if sub is not None and sup is not None: return ['<m:sSubSup><m:e>%s</m:e><m:sub>%s</m:sub><m:sup>%s</m:sup></m:sSubSup>'%(base,sub,sup)]
        if sub is not None: return ['<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>'%(base,sub)]
        if sup is not None: return ['<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>'%(base,sup)]
        return [base]
    def seq(s,stop=None):
        out=[]
        while s.i<len(s.s):
            if stop and s.s.startswith(stop,s.i): break
            if s.peek()==' ': s.i+=1; continue
            if s.peek() in ('&',) : break
            if s.s.startswith('\\\\',s.i): break
            out.extend(s.scripted())
        return out
def omath(src):
    src=src.translate({7:'\\a',8:'\\b',12:'\\f',10:'\\n',13:'\\r',9:'\\t',11:'\\v'})
    p=P(src); body=''.join(p.seq())
    return '<m:oMath xmlns:m="%s" xmlns:w="%s">%s</m:oMath>'%(MNS,WNS,body)
