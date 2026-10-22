# Journal manuscript for «Известия высших учебных заведений. Машиностроение» (BMSTU Journal of Mechanical Engineering),
# formatted to the journal's «Требования к оформлению рукописей статей» (items 1–14 of the rules page).
# Master text: the author's version article/source/LGP-50_article_author_v4.docx. The script keeps its paragraphs, OMML
# formulas and tables and (1) adds the front/back matter of rule 5, (2) merges 11 figures into 7 (rule 1: up to 5–7),
# (3) applies the page format of rule 6, (4) numbers only the formulas referred to in the text and sets Greek and
# Cyrillic letters upright (rule 9), (5) rebuilds the reference list in citation order with standards as endnotes
# (rule 11). Every edit is anchored to the expected source text and fails loudly if the source changes.
import re, copy, os
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.text.paragraph import Paragraph
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from omml import omath
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(HERE,'../article/source/LGP-50_article_author_v4.docx')
OUT=os.path.join(HERE,'../article/journal/LGP-50_Izv_VUZ_Mashinostroenie.docx')
FIG=os.path.join(HERE,'../figures/journal/')
BODY_PT=14; LINE=1.5; SMALL=12; CAP=12; META=14; MLINE=1.5; INDENT=1.25; MARGIN=2.5; TEXTW=21.0-2*MARGIN   # rule 6
MNS='http://schemas.openxmlformats.org/officeDocument/2006/math'; M=lambda t:'{%s}%s'%(MNS,t)
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
d=Document(SRC)
body=d.element.body
els=list(body.iterchildren())
def text(el): return ''.join(t.text or '' for t in el.iter(qn('w:t')))
def expect(i,start): assert text(els[i]).startswith(start), (i,text(els[i])[:70])
def is_eq(el): return el.tag==qn('w:p') and el.find(M('oMath')) is not None and re.fullmatch(r'\s*\(\d+\)\s*',text(el))
# ---------------------------------------------------------------- helpers
ALIGN={'justify':WD_ALIGN_PARAGRAPH.JUSTIFY,'center':WD_ALIGN_PARAGRAPH.CENTER,'left':WD_ALIGN_PARAGRAPH.LEFT}
TOK=re.compile(r'(\$[^$]+\$|\*\*[^*]+\*\*|\^\{[^}]*\}|\[\[[^\]]*\]\])')
def _hl(r):
    h=OxmlElement('w:highlight'); h.set(qn('w:val'),'yellow'); r._r.get_or_add_rPr().append(h)
def fill(p,txt,size=None,bold=False,italic=False):
    """$latex$ -> OMML, **bold**, ^{superscript}, [[placeholder]] -> yellow highlight (to be filled by the authors)."""
    for tok in TOK.split(txt):
        if not tok: continue
        if tok.startswith('$') and tok.endswith('$') and len(tok)>1:
            m=parse_xml(omath(tok[1:-1]))
            if size:
                for rpr in m.iter(qn('w:rPr')):
                    sz=OxmlElement('w:sz'); sz.set(qn('w:val'),str(int(size*2))); rpr.append(sz)
            p._p.append(m); continue
        b=bold; sup=False; hl=False
        if tok.startswith('**'): tok=tok[2:-2]; b=True
        elif tok.startswith('^{'): tok=tok[2:-1]; sup=True
        elif tok.startswith('[['): tok=tok[2:-2]; hl=True
        r=p.add_run(tok); r.bold=b; r.italic=italic
        if size: r.font.size=Pt(size)
        if sup: r.font.superscript=True
        if hl: _hl(r)
    return p
def par(txt='',align='justify',indent=True,size=None,bold=False,italic=False,before=0,after=0,keep_next=False,line=None):
    p=d.add_paragraph(); pf=p.paragraph_format
    pf.alignment=ALIGN[align]; pf.first_line_indent=Cm(INDENT) if indent else Cm(0)
    pf.space_before=Pt(before); pf.space_after=Pt(after)
    if line: pf.line_spacing=line
    if keep_next: pf.keep_with_next=True
    return fill(p,txt,size,bold,italic)
class After:
    """Insert new paragraphs one after another, starting after an anchor element."""
    def __init__(s,el): s.el=el
    def __call__(s,*a,**k):
        p=par(*a,**k); s.el.addnext(p._p); s.el=p._p; return p
    def brk(s):
        p=d.add_paragraph(); p.add_run().add_break(WD_BREAK.PAGE); s.el.addnext(p._p); s.el=p._p
def replace_el(old,new_p): old.addprevious(new_p._p); old.getparent().remove(old)
def remove(*idx):
    for i in idx: els[i].getparent().remove(els[i])
def picture(i,path,width_cm):
    assert els[i].find('.//'+qn('w:drawing')) is not None, i
    assert width_cm<=TEXTW, (path,width_cm)
    p=d.add_paragraph(); p.add_run().add_picture(path,width=Cm(width_cm))
    ppr=els[i].find(qn('w:pPr'))
    if ppr is not None: p._p.insert(0,copy.deepcopy(ppr))
    replace_el(els[i],p)
def caption(i,n,txt):
    expect(i,'Рисунок ')
    p=par('Рисунок %d — %s'%(n,txt),align='center',indent=False,size=CAP,after=6,line=1.0); replace_el(els[i],p)
def rep(i,old,new,count=1):
    n=0
    for t in els[i].iter(qn('w:t')):
        if t.text and old in t.text: n+=t.text.count(old); t.text=t.text.replace(old,new)
    assert n==count, (i,old,n)
def pfmt(el): return Paragraph(el,None).paragraph_format
def restyle(i,size=None,line=None,align=None,indent=None):
    el=els[i]
    for r in el.iter(qn('w:r'),M('r')):
        rpr=r.find(qn('w:rPr'))
        if rpr is None: rpr=OxmlElement('w:rPr'); r.insert(0,rpr)
        if size:
            for tag in ('w:sz','w:szCs'):
                for e in rpr.findall(qn(tag)): rpr.remove(e)
            sz=OxmlElement('w:sz'); sz.set(qn('w:val'),str(int(size*2))); rpr.append(sz)
    pf=pfmt(el)
    if line: pf.line_spacing=line
    if align: pf.alignment=ALIGN[align]
    if indent is not None: pf.first_line_indent=Cm(indent)
# ---------------------------------------------------------------- endnotes (rule 6: only endnotes; rule 11: standards go to notes)
ENDNOTES=[]
def endnote(i,anchor,note):
    """Put an endnote reference right after the text `anchor` in paragraph i."""
    for r in els[i].iter(qn('w:r')):
        t=r.find(qn('w:t'))
        if t is None or t.text is None or anchor not in t.text: continue
        head,tail=t.text.split(anchor,1); head+=anchor
        t.text=head; t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        ENDNOTES.append(note); nid=len(ENDNOTES)
        ref=parse_xml('<w:r xmlns:w="%s"><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:endnoteReference w:id="%d"/></w:r>'%(WNS,nid))
        r.addnext(ref)
        if tail:
            r2=copy.deepcopy(r); r2.find(qn('w:t')).text=tail; ref.addnext(r2)
        return
    raise AssertionError((i,anchor))
def write_endnotes():
    sep='<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:%s/></w:r></w:p>'
    notes=''.join('<w:endnote w:id="%d"><w:p><w:pPr><w:spacing w:line="360" w:lineRule="auto"/><w:ind w:firstLine="%d"/><w:jc w:val="both"/></w:pPr>'
                  '<w:r><w:rPr><w:vertAlign w:val="superscript"/><w:sz w:val="28"/></w:rPr><w:endnoteRef/></w:r>'
                  '<w:r><w:rPr><w:sz w:val="28"/></w:rPr><w:t xml:space="preserve"> %s</w:t></w:r></w:p></w:endnote>'%(k,int(INDENT*567),n)
                  for k,n in enumerate(ENDNOTES,1))
    xml=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:endnotes xmlns:w="%s">'
         '<w:endnote w:type="separator" w:id="-1">%s</w:endnote><w:endnote w:type="continuationSeparator" w:id="0">%s</w:endnote>%s</w:endnotes>'
         %(WNS,sep%'separator',sep%'continuationSeparator',notes))
    part=Part(PackURI('/word/endnotes.xml'),'application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml',xml.encode('utf-8'),d.part.package)
    d.part.relate_to(part,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/endnotes')
    st=d.settings.element
    pr=parse_xml('<w:endnotePr xmlns:w="%s"><w:numFmt w:val="decimal"/><w:endnote w:id="-1"/><w:endnote w:id="0"/></w:endnotePr>'%WNS)
    st.find(qn('w:compat')).addprevious(pr)
    sp=d.sections[0]._sectPr                            # arabic endnote numbers (Word and LibreOffice default to i, ii, ...)
    before=[c for c in sp if c.tag in (qn('w:type'),qn('w:pgSz'))]
    before[0].addprevious(parse_xml('<w:endnotePr xmlns:w="%s"><w:numFmt w:val="decimal"/></w:endnotePr>'%WNS))
# ---------------------------------------------------------------- anchors in the author's version
for i,s in [(0,'ВЛИЯНИЕ РЕГУЛИРУЕМЫХ'),(1,'Балябин'),(2,'СарФТИ'),(3,'МИФИ'),(4,'ИПФ РАН'),(5,'Аннотация.'),(6,'Ключевые слова'),
            (7,'Введение'),(8,'При выстреле'),(9,'Регулируемые'),(11,'1. Объект'),(14,'Рисунок 1 '),(16,'Рисунок 2 '),(17,'Установка оснащена'),
            (18,'1.2.'),(22,'Временная зависимость'),(23,'2. Обработка'),(24,'2.1.'),(26,'Рисунок 3 '),(31,'где '),(40,'При средних'),
            (42,'Рисунок 4 '),(43,'2.4.'),(45,'3. Динамическая'),(46,'3.1.'),(50,'3.2.'),(55,'Рисунок 5 '),(58,'что дает'),(60,'4. Идентификация'),
            (65,'Вектор параметров'),(67,'Результаты приведены'),(69,'Рисунок 6 '),(73,'Результат согласуется'),(76,'5. Механика'),
            (77,'Характеристика тарельчатой'),(80,'где '),(82,'поскольку нормальная'),(86,'Примечание:'),(88,'Рисунок 7 '),(89,'6. Сухое'),
            (98,'(ср. [6, 8])'),(100,'где '),(102,'Рисунок 8 '),(103,'7. Численное'),(109,'7.2.'),(111,'Рисунок 9 '),(122,'Рисунок 10 '),
            (125,'т.е. минимизировался'),(131,'Рисунок 11 '),(137,'8. Обсуждение'),(144,'Заключение'),(152,'Работа выполнена'),
            (153,'Список литературы'),(154,'1. Серебряков'),(169,'16. Вибрации')]:
    expect(i,s)
HEADINGS=[7,11,23,45,60,76,89,103,137,144,153]
# ---------------------------------------------------------------- rule 6: page, font, spacing, indent, hyphenation
sec=d.sections[0]
for k in ('left_margin','right_margin','top_margin','bottom_margin'): setattr(sec,k,Cm(MARGIN))
st=d.styles['Normal']; st.font.size=Pt(BODY_PT); st.paragraph_format.line_spacing=LINE
SIZE_MAP={26:BODY_PT,22:SMALL,21:SMALL,20:SMALL-1}
for el in list(body.iterchildren(qn('w:p'))):          # body-level paragraphs only; tables keep their sizes
    for sz in el.iter(qn('w:sz')):
        v=int(sz.get(qn('w:val')))//2 if sz.get(qn('w:val')) else None
        if v in SIZE_MAP: sz.set(qn('w:val'),str(SIZE_MAP[v]*2))
    ind=el.find(qn('w:pPr')+'/'+qn('w:ind'))
    if ind is not None and ind.get(qn('w:firstLine'))=='567': ind.set(qn('w:firstLine'),str(int(round(INDENT*567))))
for i in HEADINGS: restyle(i,indent=INDENT)
for el in list(body.iterchildren(qn('w:p'))):
    if is_eq(el):                                      # display formulas: single spacing, tab stops on the 16 cm text width
        pf=pfmt(el); pf.line_spacing=1.0; pf.space_before=Pt(4); pf.space_after=Pt(4)
        for tab in el.iter(qn('w:tab')):
            if tab.get(qn('w:val'))=='center': tab.set(qn('w:pos'),str(int(round(TEXTW/2*567))))
            elif tab.get(qn('w:val'))=='right': tab.set(qn('w:pos'),str(int(round(TEXTW*567))))
for tb in d.tables:                                    # tables: scale to the text width
    grid=tb._tbl.tblGrid.findall(qn('w:gridCol')); tot=sum(int(g.get(qn('w:w'))) for g in grid); f=min(1.0,TEXTW*567/tot)
    for g in grid: g.set(qn('w:w'),str(int(int(g.get(qn('w:w')))*f)))
    for w in tb._tbl.iter(qn('w:tcW')):
        if w.get(qn('w:type'))=='dxa': w.set(qn('w:w'),str(int(int(w.get(qn('w:w')))*f)))
s_el=d.settings.element
if s_el.find(qn('w:autoHyphenation')) is None: s_el.find(qn('w:defaultTabStop')).addnext(OxmlElement('w:autoHyphenation'))
for i in range(154,170):
    if 'расчётов' in text(els[i]): rep(i,'расчётов','расчетов')
# ---------------------------------------------------------------- rule 5: front matter
u=par('УДК [[534.1:62-592]]',align='left',indent=False,after=6); els[0].addprevious(u._p)
replace_el(els[1],par('А.И. Балябин^{1}, С.А. Воронов^{2}, С.И. Герасимов^{1, 3}, М.В. Заузолков^{1}, Е.Е. Ломтева^{1}',align='center',indent=False,bold=True,before=6,after=4,line=1.0))
for i,t in zip((2,3,4),['^{1} СарФТИ НИЯУ МИФИ','^{2} НИЯУ МИФИ','^{3} ИПФ РАН']):   # official abbreviations
    p_=par(t,align='center',indent=False,italic=True,size=SMALL,line=1.0); replace_el(els[i],p_)
a=After(p_._p)
a('e-mail: [[…]] (А.И. Балябин), [[…]] (С.А. Воронов), [[…]] (С.И. Герасимов), [[…]] (М.В. Заузолков), [[…]] (Е.Е. Ломтева)',align='center',indent=False,size=SMALL,line=1.0,before=4)
ABS_RU=('**Аннотация.** Многосекционные легкогазовые пушки при выстреле совершают откат, на который накладываются продольные упругие колебания, '
 'поэтому действие регулируемых фрикционных тормозов определяется не только суммарным тормозным усилием, но и местами его приложения. '
 'Цель работы — по экспериментальным данным и проверяемой численной модели обосновать размещение и относительные уровни затяжки тормозов такой установки. '
 'По данным скоростной видеорегистрации трех выстрелов исследовано влияние регулируемых фрикционных тормозов на откат и продольные колебания легкогазовой пушки 50-мм калибра. '
 'По распределениям массы и осевой жесткости построена одномерная конечно-элементная модель установки, которая при жестких стыках независимо от эксперимента дает первую продольную частоту 69,0 Гц, '
 'а измеренная частота 64,18 ± 0,04 Гц воспроизводится при жесткости фланцевых стыков 12–28 ГН/м. '
 'Показано, что асимметрия полупериодов колебаний вызвана наложением колебаний на незавершенный откат и что 23 мм в опыте без распределенного торможения представляют собой перемещение к концу записи, '
 'тогда как расчетный полный откат составляет 35–50 мм. Восстановлены эквивалентные газодинамические импульсы 12,5 и 10,5 кН·с. '
 'Тормозная способность тормоза с пакетами тарельчатых пружин определена по формулам Альмена — Ласло. '
 'Эффективное усилие торможения в опытах с тормозами (при одинаковом нагружении) составило 30–37 кН, что на два порядка меньше усилия в стыке поршневой трубы и форкамеры (≈ 3,1 МН), '
 'поэтому рост раскрытия стыка тормозами вызван быть не может. '
 'Получены коэффициенты эффективности сухого трения при наложении колебаний на откат, согласно которым станции вблизи узла первой формы эффективны для остановки отката, а станции в пучностях для гашения колебаний. '
 'Прямым моделированием с контролем энергобаланса обоснована затяжка S1 : S2 : S3 ≈ 0,48 : 0,18 : 0,32, которая уменьшает откат на 6–12 % при том же гашении колебаний. '
 'Полученные коэффициенты эффективности могут служить критерием выбора мест установки тормозов на протяженных многосекционных установках.')
replace_el(els[5],par(ABS_RU,size=META,line=MLINE,before=10,after=4))
KW_RU='легкогазовая пушка, фрикционный тормоз, продольные колебания, сухое трение, конечно-элементная модель, идентификация нагрузки, размещение тормозов'
replace_el(els[6],par('**Ключевые слова:** '+KW_RU,size=META,line=MLINE,after=4))           # rule 5: 5–7 keywords
# ---------------------------------------------------------------- figures 11 -> 7 and references in the text
picture(13,FIG+'fig1_object_doc.jpg',12.0)        # 1473 px wide photo/frame panels -> 300 dpi at 12.5 cm (rule 8)
caption(14,1,'Экспериментальная установка: а — общий вид легкогазовой пушки 50-мм калибра; б — кадр скоростной съемки с марками на фланце ПС3, форкамере и рельсовой направляющей (37 458 кадр/с, экспозиция 10 мкс); в — тормозная станция на муфте поршневой трубы: муфта с хомутами, тяга и тормоз на рельсе; г — схема поперечного сечения тормоза по пакету пружин')
remove(15,16)
rep(17,'(рисунок 2, а)','(рисунок 1, в)'); rep(17,'(рисунок 2, б)','(рисунок 1, г)')
rep(22,'(рисунок 3)','(рисунок 2, а)'); rep(24,'(рисунок 3)','(рисунок 2, а)')
picture(25,FIG+'fig2_test1_doc.png',13.5)
# formula numbers in captions are the source numbers; the renumbering pass below maps them
caption(26,2,'Опыт 1: а — перемещение форкамеры $X_{ФК}^*(t)$ и десятикратно увеличенное изменение базы $dL$ между марками ПС3–ФК (отмечены времена экстремумов $t_1$–$t_{19}$, отметка D1 и момент вылета); б — эксперимент, модель (1)–(2) и дрейф; в — длительности полупериодов и прогноз по формуле (5)')
remove(41,42)
rep(31,'рисунок 4, а','рисунок 2, б')
rep(40,'(рисунок 4, б)','(рисунок 2, в)'); rep(43,'(рисунок 4, а)','(рисунок 2, б)')
picture(54,FIG+'fig3_modes_doc.png',13.0); rep(55,'Рисунок 5 ','Рисунок 3 ')
rep(50,'(рисунок 5)','(рисунок 3)'); rep(58,'на рисунке 5','на рисунке 3')
picture(68,FIG+'fig4_ident_doc.png',12.5); rep(69,'Рисунок 6 ','Рисунок 4 ')
rep(67,'на рисунке 6','на рисунке 4')
picture(87,FIG+'fig5_brake_eff_doc.png',15.0)
caption(88,5,'Характеристики тормоза и эффективность сухого трения: а — тарельчатая пружина; б — нормальная сила и сила трения одного тормоза в зависимости от сжатия пакета; в — доли силы трения, идущие на торможение отката $\\eta(r)$ и на гашение колебаний $\\kappa(r)$ (раздел 6)')
remove(101,102)
rep(80,'(рисунок 7, а)','(рисунок 5, а)'); rep(82,' кН/мм на тормоз, и при',' кН/мм на тормоз (рисунок 5, б), и при')
rep(100,'(рисунок 8)','(рисунок 5, в)')
picture(110,FIG+'fig6_layouts_doc.png',14.0)
caption(111,6,'Сравнение схем размещения тормозов: а–в — влияние суммарного тормозного усилия для четырех схем (а — перемещение форкамеры за 0–200 мс, пунктир — опыты 1–3; б — полный откат; в — амплитуда колебаний при 170–200 мс); г, д — компромисс «полный откат — остаточные колебания» при $F_\\Sigma$ = 30 и 100 кН (номера — по таблице 6; ★ — рекомендуемая схема, ◆ — оптимум задачи (24) при 30 кН)')
remove(121,122)
rep(109,'на рисунке 9','на рисунке 6, а–в'); rep(109,'на рисунке 10','на рисунке 6, г, д'); rep(109,'на рисунке 11','на рисунке 7')
rep(125,'(рисунок 9)','(рисунок 6, а–в)')
picture(130,FIG+'fig7_time_doc.png',12.5); rep(131,'Рисунок 11 ','Рисунок 7 ')
# Table 9 (summary of results and how each was checked) repeats the Conclusions item by item; it is dropped to keep
# the manuscript within the journal limit of 20 pages. Its line of context goes with it.
expect(138,'Основные количественные результаты'); expect(139,'Таблица 9 '); assert els[140].tag==qn('w:tbl'); expect(141,'')
remove(138,139,140,141)
# ---------------------------------------------------------------- rule 10: abbreviations at first use
rep(31,'снижает СКО невязки','снижает среднеквадратическое отклонение (СКО) невязки')
# ---------------------------------------------------------------- rule 11: references in citation order; standards -> endnotes
# source numbers -> new numbers (order of first citation); new journal articles: 4, 5, 13, 16, 17, 19, 20
rep(8,'[1–3]','[1–5]'); rep(8,'[4, 5, 13]','[6–8]')
rep(9,'[6–8]','[9–11]')
rep(17,'ГОСТ 3057-90 [10]','ГОСТ 3057-90'); endnote(17,'ГОСТ 3057-90','ГОСТ 3057-90. Пружины тарельчатые. Общие технические условия.')
rep(18,'109,44 мм [15]','109,44 мм [12, 13]')
rep(31,'методом наименьших квадратов на интервале','методом наименьших квадратов [14] на интервале')
rep(46,' [12], погонная масса',' [15], погонная масса')
rep(46,'податливость фланцевого стыка, если он','податливость фланцевого стыка [16], если он')
rep(65,' находится из условия',' находится, как и в задачах идентификации параметров процесса выстрела [17], из условия')
rep(73,'установок [2, 3]','установок [2, 3]')
rep(77,'Альмена – Ласло с поправками EN 16984 [9, 11]','Альмена — Ласло [18, 19] с поправками EN 16984')
endnote(77,'EN 16984','EN 16984:2017. Disc springs — Calculation.')
rep(86,'по марке стали пружин [10, 11].','по марке стали пружин (ГОСТ 3057-90, EN 16984:2017).')
rep(98,'(ср. [6, 8])','(ср. [9, 11, 20])')
# ---------------------------------------------------------------- rule 6: long dash in text, short dash only in number ranges
for t in body.iter(qn('w:t')):
    if t.text and ' – ' in t.text: t.text=t.text.replace(' – ',' — ')
# ---------------------------------------------------------------- rule 9: number only the formulas referred to in the text
eqs=[el for el in body.iter(qn('w:p')) if is_eq(el)]
assert [int(re.search(r'\d+',text(e)).group()) for e in eqs]==list(range(1,25))
alltext='\n'.join(text(p) for p in body.iter(qn('w:p')) if not is_eq(p))
cited=set()
for m_ in re.finditer(r'\((\d{1,2})\)(?:\s*–\s*\((\d{1,2})\))?',alltext):
    a_=int(m_.group(1)); b_=int(m_.group(2) or a_); cited|=set(range(a_,b_+1))
EQMAP={old:new for new,old in enumerate(sorted(cited),1)}
assert sorted(cited)==[1,2,5,9,10,18,19,20,22,23,24], sorted(cited)
for p in body.iter(qn('w:p')):
    if is_eq(p): continue
    for t in p.iter(qn('w:t')):
        if t.text and re.search(r'\(\d{1,2}\)',t.text):
            t.text=re.sub(r'\((\d{1,2})\)',lambda m_:'(%d)'%EQMAP[int(m_.group(1))],t.text)
for e in eqs:
    old=int(re.search(r'\d+',text(e)).group())
    numrun=[r for r in e.findall(qn('w:r')) if re.fullmatch(r'\(\d+\)',''.join(x.text or '' for x in r.iter(qn('w:t'))))]
    assert len(numrun)==1, old
    if old in EQMAP:
        numrun[0].find(qn('w:t')).text='(%d)'%EQMAP[old]   # the run keeps its own <w:tab/> before the number
    else: e.remove(numrun[0])
# ---------------------------------------------------------------- rule 9: Greek and Cyrillic upright, Latin italic
for t in body.iter(M('t')):                            # proper minus, asterisk and prime glyphs in formulas
    if t.text: t.text=t.text.replace('-','−').replace('*','∗').replace("'",'′')
GREEK=re.compile(r'([Ͱ-Ͽἀ-῿Ѐ-ӿ]+)')
for r in list(body.iter(M('r'))):
    rpr=r.find(M('rPr')); sty=rpr.find(M('sty')) if rpr is not None else None
    if sty is not None or (rpr is not None and rpr.find(M('nor')) is not None): continue   # already upright/bold/plain text
    t=r.find(M('t'))
    if t is None or not t.text or not GREEK.search(t.text): continue
    parts=[s for s in GREEK.split(t.text) if s]
    tmpl=copy.deepcopy(r)                              # unmodified copy for the 2nd, 3rd ... pieces
    for k,s in enumerate(parts):
        nr=copy.deepcopy(tmpl) if k else r
        nr.find(M('t')).text=s
        if GREEK.fullmatch(s):
            pr=nr.find(M('rPr'))
            if pr is None: pr=parse_xml('<m:rPr xmlns:m="%s"/>'%MNS); nr.insert(0,pr)
            sty_=parse_xml('<m:sty xmlns:m="%s" m:val="p"/>'%MNS); nxt=[c for c in pr if c.tag in (M('brk'),M('aln'))]
            if nxt: nxt[0].addprevious(sty_)
            else: pr.append(sty_)
        if k: prev.addnext(nr)
        prev=nr
# ---------------------------------------------------------------- funding, references
replace_el(els[152],par('Исследование выполнено за счет гранта Российского научного фонда № 26‑19‑00532, https://rscf.ru/project/26-19-00532/',before=8,after=4))
rep(153,'Список литературы','Литература')
OLD={k:text(els[153+k]).split('. ',1)[1] for k in range(1,17)}       # the author's entries, without their numbers
NEW={'rogers':'Rogers J. A., Bass N. T., Wiest M. L., Wantz Z., Wilkerson J. W., Lacy T. E., Jr. The pursuit of hypervelocities: a review of two-stage light gas gun aeroballistic ranges // International Journal of Impact Engineering. — 2024. — Vol. 185. — Art. 104861. — DOI: 10.1016/j.ijimpeng.2023.104861.',
     'surma':'Surma Z. Ballistic model of two-stage light gas gun // Problems of Mechatronics. Armament, Aviation, Safety Engineering. — 2023. — Vol. 14, No. 1. — P. 73–88. — DOI: 10.5604/01.3001.0016.2960.',
     'dong':'Dong C.-Z., Catbas F. N. A review of computer vision-based structural health monitoring at local and global levels // Structural Health Monitoring. — 2021. — Vol. 20, No. 2. — P. 692–743. — DOI: 10.1177/1475921720935585.',
     'jamia':'Jamia N., Jalali H., Taghipour J., Friswell M. I., Haddad Khodaparast H. An equivalent model of a nonlinear bolted flange joint // Mechanical Systems and Signal Processing. — 2021. — Vol. 153. — Art. 107507. — DOI: 10.1016/j.ymssp.2020.107507.',
     'zhao':'Zhao W., Hou B., Bao D. Multi-parameter identification of soft recoil artillery launch process using IICCA // Journal of Vibration and Shock. — 2023. — Vol. 42, No. 21. — P. 43–51. — (На кит. яз.)',
     'koral':'Koralewski J., Wodtke M. Determining the range of applicability of analytical methods for Belleville springs and novel approach of calculating quasi-progressive spring stacks // Machines. — 2025. — Vol. 13, No. 5. — Art. 349. — DOI: 10.3390/machines13050349.',
     'marino':'Marino L., Cicirello A. Experimental investigation of a single-degree-of-freedom system with Coulomb friction // Nonlinear Dynamics. — 2020. — Vol. 99, No. 3. — P. 1781–1799. — DOI: 10.1007/s11071-019-05443-2.'}
ORDER=[1,2,3,'rogers','surma',4,5,13,6,7,8,15,'dong',14,12,'jamia','zhao',9,'koral','marino']   # GOST 3057 (10), EN 16984 (11) -> endnotes; handbook (16) dropped
REFS_RU=[OLD[k] if isinstance(k,int) else NEW[k] for k in ORDER]
assert len(REFS_RU)==20 and REFS_RU[0].startswith('Серебряков') and REFS_RU[8].startswith('Den Hartog') and REFS_RU[17].startswith('Almen')
for i in range(155,170): els[i].getparent().remove(els[i])
a=After(els[154]); first=True
for k,t in enumerate(REFS_RU,1):
    p=a('%d. %s'%(k,t),size=META,line=MLINE)
els[154].getparent().remove(els[154])
while text(els[-2])=='' and els[-2].tag==qn('w:p'): els[-2].getparent().remove(els[-2]); els.pop(-2)
# ---------------------------------------------------------------- rule 5: author information (RU)
ADR={'sar':'607186, Нижегородская обл., г. Саров, ул. Духова, д. 6','vniief':'607188, Нижегородская обл., г. Саров, пр. Мира, д. 37',
     'mephi':'115409, г. Москва, Каширское ш., д. 31','ipf':'603950, г. Нижний Новгород, ул. Ульянова, д. 46'}
SAR_RU='СарФТИ НИЯУ МИФИ ('+ADR['sar']+')'; VN_RU='ФГУП «РФЯЦ-ВНИИЭФ» ('+ADR['vniief']+')'
IDS_RU='SPIN-код РИНЦ: [[…]]; ORCID: [[…]]; Scopus Author ID: [[…]]; Web of Science ResearcherID: [[…]].'
AUTH_RU=['**Балябин А.И.** [[(имя и отчество полностью)]] — инженер-исследователь [[отдела …]] '+VN_RU+'; преподаватель [[кафедры …]] '+SAR_RU,
         '**Воронов Сергей Алексеевич** — д-р техн. наук, доцент, профессор [[кафедры …]] НИЯУ МИФИ ('+ADR['mephi']+')',
         '**Герасимов Сергей Иванович** — д-р физ.-мат. наук, профессор, начальник [[отдела …]] '+VN_RU+'; профессор [[кафедры …]] '+SAR_RU+'; главный научный сотрудник [[отдела …]] ИПФ РАН ('+ADR['ipf']+')',
         '**Заузолков Михаил Валерьевич** — старший научный сотрудник, преподаватель [[кафедры …]] '+SAR_RU,
         '**Ломтева Екатерина Евгеньевна** — старший преподаватель [[кафедры …]] '+SAR_RU]
a=After(a.el)
a('Сведения об авторах',bold=True,before=10,after=4,keep_next=True)
for t in AUTH_RU: a(t+'; '+IDS_RU,size=META,line=MLINE)
# ---------------------------------------------------------------- English part
a.brk()
a('INFLUENCE OF ADJUSTABLE FRICTION BRAKES ON THE KINEMATICS OF A LIGHT-GAS GUN',align='center',indent=False,bold=True,after=4,line=1.0)
a('A.I. Balyabin^{1}, S.A. Voronov^{2}, S.I. Gerasimov^{1, 3}, M.V. Zauzolkov^{1}, E.E. Lomteva^{1}',align='center',indent=False,bold=True,after=4,line=1.0)
ORG_EN=['Sarov Physics and Technology Institute — Branch of the National Research Nuclear University MEPhI',
        'National Research Nuclear University MEPhI (Moscow Engineering Physics Institute)',
        'A.V. Gaponov-Grekhov Institute of Applied Physics of the Russian Academy of Sciences']
for k,t in enumerate(ORG_EN,1): a('^{%d} %s'%(k,t),align='center',indent=False,italic=True,size=SMALL,line=1.0)
a('e-mail: [[…]] (A.I. Balyabin), [[…]] (S.A. Voronov), [[…]] (S.I. Gerasimov), [[…]] (M.V. Zauzolkov), [[…]] (E.E. Lomteva)',align='center',indent=False,size=SMALL,line=1.0,before=4)
ABS_EN=('**Abstract.** On firing, multi-section light-gas guns recoil, and longitudinal elastic vibrations are superimposed on the recoil; '
 'therefore, the action of adjustable friction brakes is determined not only by the total braking force but also by the points where it is applied. '
 'The purpose of the work is to substantiate the placement and relative preload levels of the brakes of such a facility using experimental data and a verifiable numerical model. '
 'The influence of adjustable friction brakes on the recoil and longitudinal vibrations of a 50 mm light-gas gun was studied using high-speed video recordings of three shots. '
 'A one-dimensional finite element model of the facility was built from the distributions of mass and axial stiffness; with rigid joints and independently of the experiment, '
 'it gives a first longitudinal frequency of 69.0 Hz, while the measured frequency of 64.18 ± 0.04 Hz is reproduced with a flange joint stiffness of 12–28 GN/m. '
 'It is shown that the asymmetry of the vibration half-periods results from the superposition of the vibrations on the unfinished recoil, and that the 23 mm recorded in the shot without distributed braking '
 'is the displacement at the end of the record, whereas the calculated full recoil is 35–50 mm. Equivalent gas-dynamic impulses of 12.5 and 10.5 kN·s were reconstructed. '
 'The braking capacity of the brake with disc spring stacks was determined using the Almen–László formulas. '
 'The effective braking force in the shots with brakes (assuming identical loading) was 30–37 kN, two orders of magnitude lower than the force in the joint between the pump tube and the high-pressure section (≈ 3.1 MN); '
 'therefore, the brakes cannot cause the observed increase in the joint opening. '
 'Efficiency coefficients of dry friction under vibrations superimposed on recoil were obtained, according to which brake stations near the node of the first mode are effective in stopping the recoil, '
 'and stations at the antinodes are effective in damping the vibrations. '
 'Direct simulation with energy balance control substantiates the preload ratio S1 : S2 : S3 ≈ 0.48 : 0.18 : 0.32, which reduces the recoil by 6–12% with the same vibration damping. '
 'The obtained efficiency coefficients can serve as a criterion for selecting brake locations on long multi-section facilities.')
a(ABS_EN,size=META,line=MLINE,before=10,after=4)
a('**Keywords:** light-gas gun, friction brake, longitudinal vibrations, dry friction, finite element model, load identification, brake placement',size=META,line=MLINE,after=4)
a('The study was supported by the Russian Science Foundation grant No. 26‑19‑00532, https://rscf.ru/en/project/26-19-00532/',size=META,line=MLINE,before=4,after=4)
a('References',bold=True,before=10,after=4,keep_next=True)
REFS_EN=[
 'Serebryakov M.E. Vnutrennyaya ballistika stvolnykh sistem i porokhovykh raket [Internal ballistics of barrel systems and solid-propellant rockets]. 3rd ed. Moscow, Oborongiz Publ., 1962. 703 p. (In Russ.)',
 'Seigel A.E. The theory of high speed guns. AGARDograph 91. Paris, NATO AGARD, 1965.',
 'Crozier W.D., Hume W. High-velocity, light-gas gun. Journal of Applied Physics, 1957, vol. 28, no. 8, pp. 892–894.',
 'Rogers J.A., Bass N.T., Wiest M.L., Wantz Z., Wilkerson J.W., Lacy T.E., Jr. The pursuit of hypervelocities: a review of two-stage light gas gun aeroballistic ranges. International Journal of Impact Engineering, 2024, vol. 185, art. 104861. DOI: 10.1016/j.ijimpeng.2023.104861',
 'Surma Z. Ballistic model of two-stage light gas gun. Problems of Mechatronics. Armament, Aviation, Safety Engineering, 2023, vol. 14, no. 1, pp. 73–88. DOI: 10.5604/01.3001.0016.2960',
 'Biderman V.L. Teoriya mekhanicheskikh kolebaniy [Theory of mechanical vibrations]. Moscow, Vysshaya shkola Publ., 1980. 408 p. (In Russ.)',
 'Panovko Ya.G., Gubanova I.I. Ustoychivost i kolebaniya uprugikh sistem [Stability and vibrations of elastic systems]. Moscow, Nauka Publ., 1979. 384 p. (In Russ.)',
 'Clough R.W., Penzien J. Dynamics of structures. 2nd ed. New York, McGraw-Hill, 1993.',
 'Den Hartog J.P. Forced vibrations with combined Coulomb and viscous friction. Transactions of the ASME, 1931, vol. 53, pp. 107–115.',
 'Kragelskiy I.V., Dobychin M.N., Kombalov V.S. Osnovy raschetov na trenie i iznos [Fundamentals of friction and wear calculations]. Moscow, Mashinostroenie Publ., 1977. (In Russ.)',
 'Olsson H., Åström K.J., Canudas de Wit C., Gäfvert M., Lischinsky P. Friction models and friction compensation. European Journal of Control, 1998, vol. 4, no. 3, pp. 176–195.',
 'Sutton M.A., Orteu J.-J., Schreier H.W. Image correlation for shape, motion and deformation measurements. New York, Springer, 2009.',
 'Dong C.-Z., Catbas F.N. A review of computer vision-based structural health monitoring at local and global levels. Structural Health Monitoring, 2021, vol. 20, no. 2, pp. 692–743. DOI: 10.1177/1475921720935585',
 'Ewins D.J. Modal testing: theory, practice and application. 2nd ed. Baldock, Research Studies Press, 2000.',
 'Bathe K.-J. Finite element procedures. Englewood Cliffs, Prentice Hall, 1996.',
 'Jamia N., Jalali H., Taghipour J., Friswell M.I., Haddad Khodaparast H. An equivalent model of a nonlinear bolted flange joint. Mechanical Systems and Signal Processing, 2021, vol. 153, art. 107507. DOI: 10.1016/j.ymssp.2020.107507',
 'Zhao W., Hou B., Bao D. Multi-parameter identification of soft recoil artillery launch process using IICCA. Journal of Vibration and Shock, 2023, vol. 42, no. 21, pp. 43–51. (In Chinese)',
 'Almen J.O., László A. The uniform-section disk spring. Transactions of the ASME, 1936, vol. 58, pp. 305–314.',
 'Koralewski J., Wodtke M. Determining the range of applicability of analytical methods for Belleville springs and novel approach of calculating quasi-progressive spring stacks. Machines, 2025, vol. 13, no. 5, art. 349. DOI: 10.3390/machines13050349',
 'Marino L., Cicirello A. Experimental investigation of a single-degree-of-freedom system with Coulomb friction. Nonlinear Dynamics, 2020, vol. 99, no. 3, pp. 1781–1799. DOI: 10.1007/s11071-019-05443-2']
assert len(REFS_EN)==len(REFS_RU)
for k,t in enumerate(REFS_EN,1): a('%d. %s'%(k,t),size=META,line=MLINE)
ADR_EN={'sar':'607186, Russian Federation, Nizhny Novgorod Region, Sarov, Dukhova St., Bldg. 6','vniief':'607188, Russian Federation, Nizhny Novgorod Region, Sarov, Mira Ave., Bldg. 37',
        'mephi':'115409, Russian Federation, Moscow, Kashirskoe Shosse, Bldg. 31','ipf':'603950, Russian Federation, Nizhny Novgorod, Ulyanov St., Bldg. 46'}
SAR_EN=ORG_EN[0]+' ('+ADR_EN['sar']+')'; VN_EN='Russian Federal Nuclear Center — All-Russian Research Institute of Experimental Physics (RFNC-VNIIEF) ('+ADR_EN['vniief']+')'
IDS_EN='SPIN-code (RSCI): [[…]]; ORCID: [[…]]; Scopus Author ID: [[…]]; Web of Science ResearcherID: [[…]].'
AUTH_EN=['**Balyabin A.I.** [[(full first name and patronymic)]] — Research Engineer, [[Department …]], '+VN_EN+'; Lecturer, [[Department …]], '+SAR_EN,
         '**Voronov Sergey Alekseevich** — Dr. Sc. (Eng.), Associate Professor, Professor, [[Department …]], '+ORG_EN[1]+' ('+ADR_EN['mephi']+')',
         '**Gerasimov Sergey Ivanovich** — Dr. Sc. (Phys.-Math.), Professor, Head of [[Department …]], '+VN_EN+'; Professor, [[Department …]], '+SAR_EN+'; Chief Researcher, [[Department …]], '+ORG_EN[2]+' ('+ADR_EN['ipf']+')',
         '**Zauzolkov Mikhail Valerievich** — Senior Researcher, Lecturer, [[Department …]], '+SAR_EN,
         '**Lomteva Ekaterina Evgenievna** — Senior Lecturer, [[Department …]], '+SAR_EN]
a('Information about the authors',bold=True,before=10,after=4,keep_next=True)
for t in AUTH_EN: a(t+'; '+IDS_EN,size=META,line=MLINE)
write_endnotes()
# drop the images of the replaced figures (otherwise they stay in the package and inflate the file, rule 1: archive <= 5 MB)
used={e.get(qn('r:embed')) for e in body.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')}
for rId,rel in list(d.part.rels.items()):
    if rel.reltype.endswith('/image') and rId not in used: d.part.drop_rel(rId)
os.makedirs(os.path.dirname(OUT),exist_ok=True)
d.save(OUT)
import shutil; shutil.copy(OUT,os.path.join(HERE,'../article/journal/submission/LGP-50_Izv_VUZ_Mashinostroenie.docx'))
print('saved',OUT,'| formulas numbered:',len(EQMAP),'of 24 | endnotes:',len(ENDNOTES))
