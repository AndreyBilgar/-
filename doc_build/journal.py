# Journal manuscript for «Известия высших учебных заведений. Машиностроение» (BMSTU Journal of Mechanical Engineering).
# Master text: the author's version article/source/LGP-50_article_author_v4.docx. The script keeps its paragraphs, OMML
# formulas and tables and only (1) adds the journal front/back matter, (2) merges 11 figures into 7 (journal limit 5–7),
# (3) renumbers figure references, (4) applies the page format. Every edit is anchored to the expected source text.
import re, copy, os, sys
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from omml import omath
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(HERE,'../article/source/LGP-50_article_author_v4.docx')
OUT=os.path.join(HERE,'../article/journal/LGP-50_Izv_VUZ_Mashinostroenie.docx')
FIG=os.path.join(HERE,'../figures/journal/')
BODY_PT=14; LINE=1.5; SMALL=12; CAP=12
d=Document(SRC)
body=d.element.body
els=list(body.iterchildren())
def text(el): return ''.join(t.text or '' for t in el.iter(qn('w:t')))
def expect(i,start): assert text(els[i]).startswith(start), (i,text(els[i])[:70])
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
    pf.alignment=ALIGN[align]; pf.first_line_indent=Cm(1.0) if indent else Cm(0)
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
    p=d.add_paragraph(); p.add_run().add_picture(path,width=Cm(width_cm))
    ppr=els[i].find(qn('w:pPr'))
    if ppr is not None: p._p.insert(0,copy.deepcopy(ppr))
    replace_el(els[i],p)
def caption(i,n,txt):
    expect(i,'Рисунок ')
    p=par('Рисунок %d – %s'%(n,txt),align='center',indent=False,size=CAP,after=6,line=1.0); replace_el(els[i],p)
def rep(i,old,new,count=1):
    n=0
    for t in els[i].iter(qn('w:t')):
        if t.text and old in t.text: n+=t.text.count(old); t.text=t.text.replace(old,new)
    assert n==count, (i,old,n)
def restyle(i,size=None,line=None,align=None,indent=None,bold=None):
    el=els[i]
    for r in el.iter(qn('w:r'),'{http://schemas.openxmlformats.org/officeDocument/2006/math}r'):
        rpr=r.find(qn('w:rPr'))
        if rpr is None: rpr=OxmlElement('w:rPr'); r.insert(0,rpr)
        if size:
            for tag in ('w:sz','w:szCs'):
                for e in rpr.findall(qn(tag)): rpr.remove(e)
            sz=OxmlElement('w:sz'); sz.set(qn('w:val'),str(int(size*2))); rpr.append(sz)
    from docx.text.paragraph import Paragraph
    pf=Paragraph(el,None).paragraph_format
    if line: pf.line_spacing=line
    if align: pf.alignment=ALIGN[align]
    if indent is not None: pf.first_line_indent=Cm(indent)
# ---------------------------------------------------------------- anchors in the author's version
for i,s in [(0,'ВЛИЯНИЕ РЕГУЛИРУЕМЫХ'),(1,'Балябин'),(2,'СарФТИ'),(3,'МИФИ'),(4,'ИПФ РАН'),(5,'Аннотация.'),(6,'Ключевые слова'),
            (7,'Введение'),(14,'Рисунок 1 '),(16,'Рисунок 2 '),(17,'Установка оснащена'),(22,'Временная зависимость'),(24,'2.1.'),
            (26,'Рисунок 3 '),(31,'где '),(40,'При средних'),(42,'Рисунок 4 '),(43,'2.4.'),(50,'3.2.'),(55,'Рисунок 5 '),(58,'что дает'),
            (67,'Результаты приведены'),(69,'Рисунок 6 '),(80,'где '),(82,'поскольку нормальная'),(88,'Рисунок 7 '),(98,'(ср. [6, 8])'),
            (100,'где '),(102,'Рисунок 8 '),(109,'7.2.'),(111,'Рисунок 9 '),(122,'Рисунок 10 '),(125,'т.е. минимизировался'),
            (131,'Рисунок 11 '),(144,'Заключение'),(152,'Работа выполнена'),(153,'Список литературы'),(154,'1. Серебряков'),(169,'16. Вибрации')]:
    expect(i,s)
# ---------------------------------------------------------------- page format
st=d.styles['Normal']; st.font.size=Pt(BODY_PT); st.paragraph_format.line_spacing=LINE
SIZE_MAP={26:BODY_PT,22:SMALL,21:SMALL,20:SMALL-1}
for el in list(body.iterchildren(qn('w:p'))):          # body-level paragraphs only; tables keep their sizes
    for sz in el.iter(qn('w:sz')):
        v=int(sz.get(qn('w:val')))//2 if sz.get(qn('w:val')) else None
        if v in SIZE_MAP: sz.set(qn('w:val'),str(SIZE_MAP[v]*2))
# display equations: single line spacing inside the 1.5-spaced text (tall fractions would otherwise get 1.5x leading)
for el in list(body.iterchildren(qn('w:p'))):
    if el.find('{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath') is not None and re.fullmatch(r'\s*\(\d+\)\s*',text(el)):
        from docx.text.paragraph import Paragraph
        pf=Paragraph(el,None).paragraph_format; pf.line_spacing=1.0; pf.space_before=Pt(4); pf.space_after=Pt(4)
for i in range(154,170):
    if 'расчётов' in text(els[i]): rep(i,'расчётов','расчетов')
# ---------------------------------------------------------------- front matter
u=par('УДК [[534.1:62-592]]',align='left',indent=False,after=6); els[0].addprevious(u._p)
replace_el(els[1],par('А.И. Балябин^{1}, С.А. Воронов^{2}, С.И. Герасимов^{1, 3}, М.В. Заузолков^{1}, Е.Е. Ломтева^{1}',align='center',indent=False,bold=True,before=6,after=4,line=1.0))
AFF_RU=['^{1} Саровский физико-технический институт — филиал федерального государственного автономного образовательного учреждения высшего образования «Национальный исследовательский ядерный университет «МИФИ», 607186, Саров, Российская Федерация, ул. Духова, д. 6',
        '^{2} Национальный исследовательский ядерный университет «МИФИ», 115409, Москва, Российская Федерация, Каширское ш., д. 31',
        '^{3} Федеральный исследовательский центр Институт прикладной физики им. А.В. Гапонова-Грехова Российской академии наук, 603950, Нижний Новгород, Российская Федерация, ул. Ульянова, д. 46']
for i,t in zip((2,3,4),AFF_RU): replace_el(els[i],par(t,align='center',indent=False,italic=True,size=SMALL,line=1.0,after=2))
ABS_RU=('**Аннотация.** Многосекционные легкогазовые пушки при выстреле совершают откат, на который накладываются продольные упругие колебания, '
 'поэтому действие регулируемых фрикционных тормозов определяется не только суммарным тормозным усилием, но и местами его приложения. '
 'Цель работы — по экспериментальным данным и проверяемой численной модели обосновать размещение и относительные уровни затяжки тормозов такой установки. '
 'По данным скоростной видеорегистрации трех выстрелов исследовано влияние регулируемых фрикционных тормозов на откат и продольные колебания легкогазовой пушки 50-мм калибра. '
 'По распределениям массы и осевой жесткости построена одномерная конечно-элементная модель установки, которая при жестких стыках независимо от эксперимента дает первую продольную частоту 69,0 Гц, '
 'а измеренная частота 64,18 ± 0,04 Гц воспроизводится при жесткости фланцевых стыков 12–28 ГН/м. '
 'Показано, что асимметрия полупериодов колебаний вызвана наложением колебаний на незавершенный откат и что 23 мм в опыте без распределенного торможения представляют собой перемещение к концу записи, '
 'тогда как расчетный полный откат составляет 35–50 мм. Восстановлены эквивалентные газодинамические импульсы 12,5 и 10,5 кН·с. '
 'Тормозная способность тормоза с пакетами тарельчатых пружин определена по формулам Альмена – Ласло. '
 'Эффективное усилие торможения в опытах с тормозами (при одинаковом нагружении) составило 30–37 кН, что на два порядка меньше усилия в стыке поршневой трубы и форкамеры (≈ 3,1 МН), '
 'поэтому рост раскрытия стыка тормозами вызван быть не может. '
 'Получены коэффициенты эффективности сухого трения при наложении колебаний на откат, согласно которым станции вблизи узла первой формы эффективны для остановки отката, а станции в пучностях для гашения колебаний. '
 'Прямым моделированием с контролем энергобаланса обоснована затяжка S1 : S2 : S3 ≈ 0,48 : 0,18 : 0,32, которая уменьшает откат на 6–12 % при том же гашении колебаний. '
 'Полученные коэффициенты эффективности могут служить критерием выбора мест установки тормозов на протяженных многосекционных установках.')
replace_el(els[5],par(ABS_RU,size=SMALL,line=1.15,before=10,after=4))
restyle(6,size=SMALL,line=1.15)
# ---------------------------------------------------------------- figures 11 -> 7 and references in the text
picture(13,FIG+'fig1_object.png',14.0)
caption(14,1,'Экспериментальная установка: а — общий вид легкогазовой пушки 50-мм калибра; б — кадр скоростной съемки с марками на фланце ПС3, форкамере и рельсовой направляющей (37 458 кадр/с, экспозиция 10 мкс); в — тормозная станция на муфте поршневой трубы: муфта с хомутами, тяга и тормоз на рельсе; г — схема поперечного сечения тормоза по пакету пружин')
remove(15,16)
rep(17,'(рисунок 2, а)','(рисунок 1, в)'); rep(17,'(рисунок 2, б)','(рисунок 1, г)')
rep(22,'(рисунок 3)','(рисунок 2, а)'); rep(24,'(рисунок 3)','(рисунок 2, а)')
picture(25,FIG+'fig2_test1.png',15.0)
caption(26,2,'Опыт 1: а — перемещение форкамеры $X_{ФК}^*(t)$ и десятикратно увеличенное изменение базы $dL$ между марками ПС3–ФК (отмечены времена экстремумов $t_1$–$t_{19}$, отметка D1 и момент вылета); б — эксперимент, модель (1)–(2) и дрейф; в — длительности полупериодов и прогноз по формуле (5)')
remove(41,42)
rep(31,'методом наименьших квадратов на интервале','методом наименьших квадратов [14] на интервале'); rep(31,'рисунок 4, а','рисунок 2, б')
rep(40,'(рисунок 4, б)','(рисунок 2, в)'); rep(43,'(рисунок 4, а)','(рисунок 2, б)')
picture(54,FIG+'fig3_modes.png',14.5); rep(55,'Рисунок 5 ','Рисунок 3 ')
rep(50,'(рисунок 5)','(рисунок 3)'); rep(58,'на рисунке 5','на рисунке 3')
picture(68,FIG+'fig4_ident.png',13.5); rep(69,'Рисунок 6 ','Рисунок 4 ')
rep(67,'на рисунке 6','на рисунке 4')
picture(87,FIG+'fig5_brake_eff.png',17.0)
caption(88,5,'Характеристики тормоза и эффективность сухого трения: а — тарельчатая пружина; б — нормальная сила и сила трения одного тормоза в зависимости от сжатия пакета; в — доли силы трения, идущие на торможение отката $\\eta(r)$ и на гашение колебаний $\\kappa(r)$ (раздел 6)')
remove(101,102)
rep(80,'(рисунок 7, а)','(рисунок 5, а)'); rep(82,' кН/мм на тормоз, и при',' кН/мм на тормоз (рисунок 5, б), и при')
rep(98,'(ср. [6, 8])','(ср. [6, 8, 16])'); rep(100,'(рисунок 8)','(рисунок 5, в)')
picture(110,FIG+'fig6_layouts.png',15.5)
caption(111,6,'Сравнение схем размещения тормозов: а–в — влияние суммарного тормозного усилия для четырех схем (а — перемещение форкамеры за 0–200 мс, пунктир — опыты 1–3; б — полный откат; в — амплитуда колебаний при 170–200 мс); г, д — компромисс «полный откат — остаточные колебания» при $F_\\Sigma$ = 30 и 100 кН (номера — по таблице 6; ★ — рекомендуемая схема, ◆ — оптимум задачи (24) при 30 кН)')
remove(121,122)
rep(109,'на рисунке 9','на рисунке 6, а–в'); rep(109,'на рисунке 10','на рисунке 6, г, д'); rep(109,'на рисунке 11','на рисунке 7')
rep(125,'(рисунок 9)','(рисунок 6, а–в)')
# Table 9 (summary of results and how each was checked) repeats the Conclusions item by item; it is dropped to keep
# the manuscript within the journal limit of 20 pages. Its two lines of context go with it.
expect(138,'Основные количественные результаты'); expect(139,'Таблица 9 '); assert els[140].tag==qn('w:tbl'); expect(141,'')
remove(138,139,140,141)
picture(130,FIG+'fig7_time.png',14.0); rep(131,'Рисунок 11 ','Рисунок 7 ')
# ---------------------------------------------------------------- funding, references
replace_el(els[152],par('Исследование выполнено за счет гранта Российского научного фонда № 26‑19‑00532, https://rscf.ru/project/26-19-00532/',before=8,after=4))
rep(153,'Список литературы','Литература')
for i in range(154,170): restyle(i,size=SMALL,line=1.15,indent=0)
while text(els[-2])=='' and els[-2].tag==qn('w:p'): els[-2].getparent().remove(els[-2]); els.pop(-2)
last=els[169]
# ---------------------------------------------------------------- authors (RU)
a=After(last)
a('Сведения об авторах',align='left',indent=False,bold=True,before=10,after=4,keep_next=True)
AUTH_RU=[('Балябин','А.И.','1'),('Воронов','С.А.','2'),('Герасимов','С.И.','1, 3'),('Заузолков','М.В.','1'),('Ломтева','Е.Е.','1')]
for fam,ini,aff in AUTH_RU:
    a('**%s %s** [[(имя и отчество полностью)]] — [[ученая степень, должность, подразделение]], организация %s; e-mail: [[…]]; SPIN-код РИНЦ: [[…]]; ORCID: [[…]]; Scopus Author ID: [[…]]; Web of Science ResearcherID: [[…]].'%(fam,ini,aff),align='left',size=SMALL,line=1.15,after=2)
# ---------------------------------------------------------------- English part
a.brk()
a('INFLUENCE OF ADJUSTABLE FRICTION BRAKES ON THE KINEMATICS OF A LIGHT-GAS GUN',align='center',indent=False,bold=True,after=4,line=1.0)
a('A.I. Balyabin^{1}, S.A. Voronov^{2}, S.I. Gerasimov^{1, 3}, M.V. Zauzolkov^{1}, E.E. Lomteva^{1}',align='center',indent=False,bold=True,after=4,line=1.0)
AFF_EN=['^{1} Sarov Physics and Technology Institute — Branch of the National Research Nuclear University MEPhI, 607186, Sarov, Russian Federation, Dukhova St., Bldg. 6',
        '^{2} National Research Nuclear University MEPhI (Moscow Engineering Physics Institute), 115409, Moscow, Russian Federation, Kashirskoe Shosse, Bldg. 31',
        '^{3} A.V. Gaponov-Grekhov Institute of Applied Physics of the Russian Academy of Sciences, 603950, Nizhny Novgorod, Russian Federation, Ulyanov St., Bldg. 46']
for t in AFF_EN: a(t,align='center',indent=False,italic=True,size=SMALL,line=1.0,after=2)
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
a(ABS_EN,size=SMALL,line=1.15,before=10,after=4)
a('**Keywords:** light-gas gun, friction brake, disc spring, high-speed video recording, longitudinal vibrations, finite element model, load identification, dry friction, brake placement',size=SMALL,line=1.15,after=4)
a('The study was supported by the Russian Science Foundation grant No. 26‑19‑00532, https://rscf.ru/en/project/26-19-00532/',size=SMALL,line=1.15,before=4,after=4)
a('References',align='left',indent=False,bold=True,before=10,after=4,keep_next=True)
REFS_EN=[
 'Serebryakov M.E. Vnutrennyaya ballistika stvolnykh sistem i porokhovykh raket [Internal ballistics of barrel systems and solid-propellant rockets]. 3rd ed. Moscow, Oborongiz Publ., 1962. 703 p. (In Russ.)',
 'Seigel A.E. The theory of high speed guns. AGARDograph 91. Paris, NATO AGARD, 1965.',
 'Crozier W.D., Hume W. High-velocity, light-gas gun. Journal of Applied Physics, 1957, vol. 28, no. 8, pp. 892–894.',
 'Biderman V.L. Teoriya mekhanicheskikh kolebaniy [Theory of mechanical vibrations]. Moscow, Vysshaya shkola Publ., 1980. 408 p. (In Russ.)',
 'Panovko Ya.G., Gubanova I.I. Ustoychivost i kolebaniya uprugikh sistem [Stability and vibrations of elastic systems]. Moscow, Nauka Publ., 1979. 384 p. (In Russ.)',
 'Den Hartog J.P. Forced vibrations with combined Coulomb and viscous friction. Transactions of the ASME, 1931, vol. 53, pp. 107–115.',
 'Kragelskiy I.V., Dobychin M.N., Kombalov V.S. Osnovy raschetov na trenie i iznos [Fundamentals of friction and wear calculations]. Moscow, Mashinostroenie Publ., 1977. (In Russ.)',
 'Olsson H., Åström K.J., Canudas de Wit C., Gäfvert M., Lischinsky P. Friction models and friction compensation. European Journal of Control, 1998, vol. 4, no. 3, pp. 176–195.',
 'Almen J.O., László A. The uniform-section disk spring. Transactions of the ASME, 1936, vol. 58, pp. 305–314.',
 'GOST 3057-90. Pruzhiny tarelchatye. Obshchie tekhnicheskie usloviya [State Standard 3057-90. Disc springs. General specifications]. (In Russ.)',
 'EN 16984:2017. Disc springs — Calculation.',
 'Bathe K.-J. Finite element procedures. Englewood Cliffs, Prentice Hall, 1996.',
 'Clough R.W., Penzien J. Dynamics of structures. 2nd ed. New York, McGraw-Hill, 1993.',
 'Ewins D.J. Modal testing: theory, practice and application. 2nd ed. Baldock, Research Studies Press, 2000.',
 'Sutton M.A., Orteu J.-J., Schreier H.W. Image correlation for shape, motion and deformation measurements. New York, Springer, 2009.',
 'Vibratsii v tekhnike. Spravochnik. V 6 t. [Vibrations in engineering. Handbook. In 6 vols.]. Chelomey V.N., ed. Moscow, Mashinostroenie Publ., 1978–1981. (In Russ.)']
for k,t in enumerate(REFS_EN,1): a('%d. %s'%(k,t),size=SMALL,line=1.15,indent=False,after=1)
a('Information about the authors',align='left',indent=False,bold=True,before=10,after=4,keep_next=True)
AUTH_EN=[('Balyabin A.I.','1'),('Voronov S.A.','2'),('Gerasimov S.I.','1, 3'),('Zauzolkov M.V.','1'),('Lomteva E.E.','1')]
for nm,aff in AUTH_EN:
    a('**%s** [[(full first name and patronymic)]] — [[academic degree, position, department]], affiliation %s; e-mail: [[…]]; ORCID: [[…]]; Scopus Author ID: [[…]]; Web of Science ResearcherID: [[…]].'%(nm,aff),align='left',size=SMALL,line=1.15,after=2)
os.makedirs(os.path.dirname(OUT),exist_ok=True)
d.save(OUT); print('saved',OUT)
