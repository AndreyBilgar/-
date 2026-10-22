# 20-page version of the journal manuscript («Известия вузов. Машиностроение», rule 2: 4–20 pages A4).
# Master: the authors' version article/source/LGP-50_article_author_v5.docx (their abstract, author data and ORCID).
# What is shortened, and why it loses no result:
#   * figure 7 (time histories) and table 8 (energy balance): their numbers are kept in the text;
#   * figure 6, г–д (recoil vs. residual vibration for ten layouts): the same values are in table 6;
#   * figure 5, а–б (disc spring characteristic): the same values are in table 5; its panel в (dry friction
#     efficiency) joins figure 3 next to the mode shapes, so the paper has 5 figures; all figures printed smaller;
#   * three one-line unnumbered formulas set inline; the abstract (RU and EN) shortened;
#   * three textbooks removed from the reference list (rule 11 discourages textbooks): Biderman, Clough & Penzien,
#     Bathe; 17 sources remain (rule 1: at least 15);
#   * paragraphs of the introduction and of sections 2–8 and the conclusions rewritten more compactly; every number,
#     formula reference and citation is kept. Formula numbers do not change: (9) and (11) stay referenced in the text.
# Every edit is anchored to the expected source text and fails loudly if the source changes.
import re, copy, os, shutil
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import parse_xml
from omml import omath
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(HERE,'../article/source/LGP-50_article_author_v5.docx')
OUT=os.path.join(HERE,'../article/journal/LGP-50_Izv_VUZ_Mashinostroenie.docx')
SUB=os.path.join(HERE,'../article/journal/submission/')
FIG=os.path.join(HERE,'../figures/journal/')
CAP=12
MNS='http://schemas.openxmlformats.org/officeDocument/2006/math'; M=lambda t:'{%s}%s'%(MNS,t)
d=Document(SRC)
body=d.element.body
els=list(body.iterchildren())
def tm(el): return ''.join((n.text or '') for n in el.iter(qn('w:t'),M('t')))
def expect(i,start): assert tm(els[i]).startswith(start), (i,tm(els[i])[:70])
def is_eq(el): return el.tag==qn('w:p') and el.find(M('oMath')) is not None and re.fullmatch(r'\s*\(\d+\)\s*',''.join(t.text or '' for t in el.iter(qn('w:t'))))
TOK=re.compile(r'(\$[^$]+\$|\*\*[^*]+\*\*)')
def runs(txt,size=None):
    """Runs and OMML for `txt` ($latex$ -> formula, **bold**) built in a scratch paragraph."""
    p=d.add_paragraph()
    for tok in TOK.split(txt):
        if not tok: continue
        if tok.startswith('$') and tok.endswith('$') and len(tok)>1:
            m=parse_xml(omath(tok[1:-1]))
            if size:
                for rpr in m.iter(qn('w:rPr')): rpr.append(parse_xml('<w:sz xmlns:w="%s" w:val="%d"/>'%('http://schemas.openxmlformats.org/wordprocessingml/2006/main',size*2)))
            p._p.append(m); continue
        b=tok.startswith('**'); r=p.add_run(tok[2:-2] if b else tok); r.bold=b
        if size: r.font.size=Pt(size)
    kids=[c for c in p._p if c.tag!=qn('w:pPr')]
    p._p.getparent().remove(p._p)
    return kids
def set_text(i,start,txt,size=None):
    """Replace the content of paragraph i (its paragraph format is kept)."""
    expect(i,start); el=els[i]
    for c in [c for c in el if c.tag!=qn('w:pPr')]: el.remove(c)
    for k in runs(txt,size): el.append(k)
def append_text(i,start,txt):
    expect(i,start)
    for k in runs(txt): els[i].append(k)
def insert_after(i,anchor,txt):
    for r in els[i].iter(qn('w:r')):
        t=r.find(qn('w:t'))
        if t is None or not t.text or anchor not in t.text: continue
        head,tail=t.text.split(anchor,1); t.text=head+anchor; t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        last=r
        for k in runs(txt): last.addnext(k); last=k
        if tail:
            r2=copy.deepcopy(r); r2.find(qn('w:t')).text=tail; last.addnext(r2)
        return
    raise AssertionError((i,anchor))
def remove(i,start=None):
    if start is not None: expect(i,start)
    els[i].getparent().remove(els[i])
def picture(i,path,width_cm):
    assert els[i].find('.//'+qn('w:drawing')) is not None, i
    p=d.add_paragraph(); p.add_run().add_picture(path,width=Cm(width_cm))
    ppr=els[i].find(qn('w:pPr'))
    if ppr is not None: p._p.insert(0,copy.deepcopy(ppr))
    els[i].addprevious(p._p); els[i].getparent().remove(els[i])
def rep(i,old,new):
    n=0
    for t in els[i].iter(qn('w:t')):
        if t.text and old in t.text: n+=t.text.count(old); t.text=t.text.replace(old,new)
    assert n==1, (i,old,n)
# ---------------------------------------------------------------- figures: smaller; 7 -> 6
picture(15,FIG+'fig1_object_doc.jpg',10.0)
set_text(16,'Рисунок 1 — ','Рисунок 1 — Установка: а — общий вид легкогазовой пушки 50-мм калибра; б — кадр скоростной съемки с марками на фланце ПС3, форкамере и рельсе (37 458 кадр/с, экспозиция 10 мкс); в — тормозная станция на муфте поршневой трубы; г — сечение тормоза по пакету пружин',size=CAP)
picture(25,FIG+'fig2_test1_doc.png',11.5)
picture(52,FIG+'fig3_modes_eff_doc.png',14.0)
set_text(53,'Рисунок 3 — ','Рисунок 3 — Формы колебаний и эффективность сухого трения: а — первые две продольные формы ($\\xi=z/L$; вверху — схема секций, штриховые линии — стыки, точки — тормозные станции); б — доли силы трения, идущие на торможение отката $\\eta(r)$ и на гашение колебаний $\\kappa(r)$',size=CAP)
picture(66,FIG+'fig4_ident_doc.png',11.0)
assert els[85].find('.//'+qn('w:drawing')) is not None; remove(85); remove(86,'Рисунок 5 — ')
picture(106,FIG+'fig6_scan_doc.png',14.0)
set_text(107,'Рисунок 6 — ','Рисунок 5 — Влияние суммарного тормозного усилия для четырех схем: а — перемещение форкамеры за 0–200 мс (пунктир — опыты 1–3); б — полный откат; в — амплитуда колебаний при 170–200 мс',size=CAP)
assert els[124].find('.//'+qn('w:drawing')) is not None; remove(124); remove(125,'Рисунок 7 — ')
# ---------------------------------------------------------------- introduction
set_text(10,'При выстреле двухступенчатой','При выстреле двухступенчатой легкогазовой пушки газодинамическая нагрузка прикладывается к секциям установки последовательно: давление пороховых газов действует на казенную часть и разгоняет поршень, торможение поршня в сжатом легком газе нагружает конический переход форкамеры, а истекающий из ствола газ создает реактивную силу [1–5]. Поэтому протяженную многосекционную установку нельзя считать жестким телом: на ее откат накладываются продольные колебания секций и относительные перемещения во фланцевых соединениях [6–8].')
set_text(11,'Регулируемые фрикционные','Регулируемые фрикционные тормоза ограничивают откат за счет сухого трения о рельсовую направляющую [9–11]. Для многосекционной установки важна не только суммарная тормозная сила, но и места ее приложения: тормоза скользят по неподвижному рельсу и реагируют на абсолютную скорость точки крепления, а не на относительную скорость соседних секций. Кроме того, жесткость редуцированной модели, подобранная по измеренному периоду, не может служить независимой проверкой, а при конечной длительности записи максимальное зарегистрированное перемещение может не совпадать с полным откатом.')
set_text(12,'Цель работы','Цель работы — обосновать схему размещения и относительные уровни затяжки тормозов, последовательно построив конечно-элементную модель установки по распределениям массы и жесткости, проверив ее по эксперименту, идентифицировав нагрузку и рассчитав механику тормоза.')
# ---------------------------------------------------------------- sections 1–2
set_text(14,'1.1. Установка.','**1.1. Установка.** Установка (рисунок 1, а) включает затвор, зарядную камеру (ЗК), поршневую трубу из трех секций (ПС1–ПС3) с межсекционными муфтами, форкамеру (ФК) и баллистический ствол из двух секций (БТ1, БТ2); ствольная линия установлена на тележках, перемещающихся по рельсовой направляющей. Масса подвижной части $M$ ≈ 17,9 т; при разделении по стыку ПС3–ФК масса задней группы $m_1$ ≈ 10,9 т, передней $m_2$ ≈ 7,0 т ($m_2/M$ = 0,394).')
set_text(18,'1.2. Эксперимент.','**1.2. Эксперимент.** Рассмотрены три выстрела (таблица 1): в опыте 1 распределенные тормозные пары не применялись и откат компенсировался со стороны зарядной камеры, в опытах 2 и 3 штатные тормозные пары работали на узлах установки. Скоростная съемка (37 458 кадр/с, экспозиция 10 мкс) велась 0–200 мс после импульса поджига. Регистрировались перемещение марки форкамеры $X_{ФК}$ относительно неподвижной марки на рельсе и изменение базы между марками на фланце ПС3 и форкамере ($d_X$ вдоль оси, $d_Y$ поперек оси; исходная база 109,44 мм) [12, 13]. Временная зависимость получена только для опыта 1, для опытов 2 и 3 известны лишь максимальные значения.')
remove(22,'Временная зависимость приведена')
set_text(24,'2.1. Исходные данные.','**2.1. Исходные данные.** Для анализа полупериодов использованы времена 18 последовательных экстремумов $X_{ФК}$ (67,13–196,71 мс), для идентификации моделей — вся запись $X_{ФК}(t)$ опыта 1 на интервале 45–198 мс (рисунок 2, а).')
assert tm(els[30]).startswith('ζ') and els[30].find(M('oMath')) is not None; remove(30)        # ζ = α/ω, f = ω/2π -> inline
insert_after(31,'круговая частота и фаза','; $\\zeta=\\alpha/\\omega$ — коэффициент демпфирования, $f=\\omega/2\\pi$ — частота')
rep(27,', т.е. продолжающегося отката, и затухающей',' (продолжающегося отката) и затухающей')
rep(116,', и вероятными его причинами являются разброс газодинамического нагружения и нерегулярные контактные явления в соединении (раздел 2.5).','; его вероятные причины — разброс нагружения и нерегулярные контактные явления в соединении (раздел 2.5).')
set_text(36,'2.3. Природа','**2.3. Природа асимметрии полупериодов.** Средние длительности полупериодов спада и роста различаются и составляют 8,57 и 6,92 мс. Такое различие можно было бы принять за признак несимметричности восстанавливающей силы, однако оно следует из самой кинематики. Для $X=-V_dt+A\\cos\\omega t$ условие экстремума $\\dot X=0$ дает $\\sin\\omega t=-V_d/(A\\omega)$, т.е. минимумы смещаются на $\\beta/\\omega$ позже, а максимумы на $\\beta/\\omega$ раньше положений $\\omega t=\\pi$ и $2\\pi$. Отсюда')
assert els[37].find(M('oMath')) is not None and '⇒' in tm(els[37]); remove(37); remove(38,'т.е. минимумы')      # X' = 0 => sin ωt = ... -> inline
remove(35,'Средний период')
insert_after(31,'Физическую природу этой составляющей по одной марке установить нельзя.',' Средний период по экстремумам (15,48 мс) согласуется с модельным, а оценка затухания по полуразмахам ($\\alpha$ ≈ 6,9 с⁻¹) завышена на 10–15 % из-за смещения полуразмахов дрейфом, поэтому далее используется оценка по модели (1)–(2).')
set_text(41,'2.4. Незавершенность','**2.4. Незавершенность отката.** К концу записи скорость дрейфа еще составляет 0,085 м/с (рисунок 2, б), поэтому 23 мм — перемещение к моменту 200 мс, а не полный откат. По модели раздела 4 полный откат составляет 40 мм (35–50 мм в пределах погрешности сопротивления опор), остановка — через 0,50–0,68 с. Опыты корректнее сравнивать по перемещению в фиксированный момент и по скорости дрейфа.')
set_text(42,'2.5. Сигнал стыка.','**2.5. Сигнал стыка.** Размах $d_X$ = 0,81 мм (таблица 1) складывается из колебательной составляющей, синфазной с $X_{ФК}$ (коэффициент корреляции 0,83, коэффициент передачи $dL/X_{осц}$ = 0,056, около 0,25 мм размаха), остаточного смещения около +0,1 мм и одиночного события сжатия около −0,4 мм при 105–118 мс. Следовательно, $d_{X,\\max}$ объединяет упругий отклик и нерегулярные (вероятно, контактные) явления, и сравнивать его между опытами без разложения на составляющие нельзя.')
# ---------------------------------------------------------------- section 3
rep(78,'(рисунок 5, а)','(таблица 5)')
expect(47,''); assert 'ω' in tm(els[47]) and tm(els[47]).replace(' ','').startswith('K'); remove(47)   # (K − ω²M)φ = 0 -> inline
set_text(46,'где E','где $E$ = 206 ГПа, $k_J$ — жесткость стыка. Собственные частоты и формы свободного стержня находятся из задачи $(\\mathbf{K}-\\omega^2\\mathbf{M})\\mathbf{φ}=0$.')
set_text(48,'3.2. Независимая проверка','**3.2. Независимая проверка частоты.** При жестких стыках модель дает $f_1$ = 68,99 Гц, $f_2$ = 142,65 Гц и $f_3$ = 171,57 Гц; узел первой формы расположен вблизи центра масс, у муфты ПС2–ПС3 (рисунок 3, а). Превышение измеренной частоты на 7,5 % ожидаемо, так как жесткие стыки дают верхнюю оценку. Следовательно, колебания с частотой 64,2 Гц — первая продольная форма всей установки, а не локальная форма одного соединения. Жесткость стыков калибровалась по двум независимым условиям: по частоте 64,18 Гц и по коэффициенту передачи на базе марок $dL/X_{ФК}$ = 0,056–0,070 (таблица 3). При жестких стыках этот коэффициент равен 0,0088, т.е. измеренная деформация на базе марок в 6–8 раз больше, чем у сплошной конструкции, и сосредоточена в соединении ПС3–ФК.')
expect(55,''); assert els[55].find(M('oMath')) is not None and 'mпр' in tm(els[55]).replace(' ','')
remove(55)                                              # display formula of the two-mass model -> inline
set_text(54,'Эквивалентная жесткость','Эквивалентная жесткость двухмассовой модели $k_s=m_{пр}\\omega^2$, где $m_{пр}=m_1m_2/(m_1+m_2)$ ≈ 4,27 т, составляет ≈ 694 МН/м. Однако, как видно из рисунка 3, а, относительное движение распределено по длине поршневой трубы, и марки на стыке фиксируют лишь 5,6–7 % перемещения форкамеры, поэтому модель «две массы и пружина в стыке» пригодна только для оценки частоты, но не для анализа раскрытия стыка.')
remove(56,'что дает')
# ---------------------------------------------------------------- section 4
set_text(71,'Результат согласуется','Результат согласуется с независимыми признаками: начало импульса $P$ (47,9 ± 0,6 мс) близко к отметке D1 (48,9 мс), не использованной при подгонке; максимум $Q$ (69,5 мс) практически совпадает с моментом вылета (70,07 мс); эквивалентные давления, отнесенные к площадям канала, составляют сотни мегапаскалей, что правдоподобно для двухступенчатых установок [2, 3]. При пиковой скорости центра масс −0,69 м/с (58,6 мс) количество движения установки равно 12,4 кН·с, т.е. близко к $I_P$: при торможении поршня в форкамере его количество движения возвращается установке, и после выстрела остается лишь разность $I_Q-I_P$ ≈ −2 кН·с. Надежно определяются импульсы и моменты времени, а пиковые значения зависят от принятой формы (5), коэффициент корреляции $P_0$ и $\\tau_P$ равен −0,97.')
set_text(72,'Энергетический баланс','Энергетический баланс резко несимметричен: из работы нагрузок 11,4 кДж после выстрела 9,2 кДж запасено в первой форме, тогда как кинетическая энергия остаточного отката $Mv^2/2$ ≈ 87 Дж. Следовательно, остановка отката и гашение колебаний — две задачи, энергии которых различаются на два порядка.')
set_text(73,'Анализ чувствительности','Анализ чувствительности выявляет принципиальное ограничение серии опытов: изменение $P_0$ на ±10 % меняет перемещение к 200 мс на ±40 %, поскольку остаточный импульс — малая разность двух больших величин, а уменьшение $I_P$ всего на 6,0 и 7,1 % без тормозов дает 18 и 17 мм, т.е. значения опытов 2 и 3. Раскрытие стыка менее чувствительно: ±6–8 % при вариации $P_0$ на ±10 % и $Q_0$ на ±20 %.')
# ---------------------------------------------------------------- sections 5–6
set_text(80,'поскольку нормальная сила','поскольку нормальная сила действует на двух поверхностях трения: между пластиной и головкой рельса и между захватами и нижними гранями головки. Коэффициенты трения этих пар не определялись, поэтому принят диапазон $\\mu_\\Sigma$ = 0,3–0,8. Чувствительность регулировки $dN/d\\Delta=n_пc/n_т$ = 17,0 кН/мм на тормоз; при шаге резьбы гайки $p$ один оборот меняет $N$ на 17$p$ кН ($p$ в мм), поэтому необходима прямая калибровка «деление шкалы — сила».')
set_text(98,'где m','где $m^*$ = 8479 кг — модальная масса, $E_1=m^*\\omega^2q^2/2$. Сразу после выстрела ($q$ = 3,66 мм, $V_d$ ≈ 0,1 м/с) параметр $r_j$ для станций S1–S5 равен 0,07; 0,14; 1,31; 0,11; 0,08. Поэтому у станций S1, S4, S5 $\\eta$ = 0,04–0,07: их сила трения почти целиком идет на гашение колебаний и мало тормозит откат, а станция S3 в узле полностью работает на остановку отката ($\\eta$ = 1), но колебаний не гасит (рисунок 3, б). Для равномерной схемы с $F_\\Sigma$ = 30 кН среднее тормозящее усилие в начале процесса составляет лишь 7,5 кН (25 %), а $\\zeta_T$ = 0,0022 (15 % собственного демпфирования). По мере затухания колебаний $\\eta$ растет, поэтому эффект нелинейный и оценивается прямым моделированием.')
# ---------------------------------------------------------------- section 7
set_text(104,'где E','где $E_k$, $E_s$ — кинетическая и упругая энергии; $D_C$, $D_T$, $D_r$ — диссипация в конструкции, тормозах и опорах. Погрешность баланса во всех расчетах не превышает 5·10⁻⁴; при уменьшении шага сетки и шага по времени вдвое $f_1$, перемещения форкамеры, полный откат и $N_{J,\\max}$ меняются не более чем на 0,3 %. Без тормозов модель воспроизводит опыт 1 (раздел 4). При равных усилиях на всех пяти станциях перемещения 18 и 17 мм к 200 мс получаются при $F_\\Sigma$ = 30,3 и 37,0 кН, т.е. 3,0–3,7 кН на тормоз, что соответствует сжатию пакетов всего 0,22–0,73 мм, или прогибу пружин 5–17 % $h_0\'$ (таблица 5). Идентифицированное усилие зависит от схемы (45 кН без S3, 53,5 кН при тормозах только на S1 и S5) и мало зависит от $k_b$ (менее 3 % при уменьшении в 10 раз). С учетом раздела 4 эта оценка условна: тот же эффект дает уменьшение импульса $P$ на 6–7 %.')
set_text(105,'7.2. Результаты.','**7.2. Результаты.** Зависимости от суммарного усилия показаны на рисунке 5, сравнение десяти схем приведено в таблице 6. Из этих данных вытекают следующие закономерности.')
set_text(112,'1. Быструю фазу','1. Быструю фазу (до ≈ 75 мс) тормоза практически не меняют: газодинамические силы порядка 2 МН на два порядка превышают тормозные, и перемещение форкамеры даже при 200 кН не опускается ниже ≈ 11 мм. Регулируется только остаточный откат: для равномерной схемы полный откат уменьшается с 40,3 мм без тормозов до 18,3; 11,2 и 8,0 мм при 30, 100 и 200 кН.')
set_text(119,'т.е. минимизировался','т.е. в задаче (11) минимизировался откат при гашении колебаний не хуже, чем у равномерной схемы (метод Нелдера — Мида, 70 прямых расчетов). При $F_\\Sigma$ = 30 кН получено $w$ = (0,56; 0,01; 0,43; 0; 0) и $X_{полн}$ = 16,2 мм вместо 18,3 мм (−11,5 %), при 60 кН — $w$ = (0,48; 0,18; 0,32; 0,01; 0,01) и 13,2 мм вместо 14,1 мм (−6,3 %). Оптимум сочетает пучность S1 (гашение) и узел S3 (остановка отката), что согласуется с (6)–(8). Распределение, найденное для 60 кН, сохраняет преимущество во всем диапазоне 10–200 кН (рисунок 5). При 60 кН усилия пар составляют 28,9; 10,9 и 19,0 кН, что при $\\mu_\\Sigma$ = 0,8…0,3 соответствует сжатию пакетов на S1 1,06–2,83 мм, на S2 0,40–1,07 мм и на S3 0,70–1,86 мм, т.е. не более 0,67$h_0\'$. Точные уставки требуют калибровки.')
set_text(120,'Устойчивость рекомендации','Устойчивость рекомендации проверена изменением $P_0$ на ±6 % и $Q_0$ на ±10 % при $F_\\Sigma$ = 60 кН (таблица 7): во всех вариантах рекомендуемая схема дает полный откат на 1–10 % меньше, чем равномерная, при практически одинаковых амплитудах колебаний (различие менее 0,5 %). Выигрыш растет с остаточным импульсом, т.е. проявляется именно в выстрелах с большим откатом.')
# energy balance: table 8 -> two sentences (its numbers are kept)
set_text(126,'Распределение энергии','Энергобаланс (9) за 0–600 мс показывает, что без тормозов почти вся работа нагрузок (11,4 кДж) рассеивается за счет собственного демпфирования первой формы (90 %, остальное — в опорах), а доля тормозов растет с усилием: 19 % при 30 кН, 31 % при рекомендуемой схеме и 60 кН, 43 % при 100 кН (погрешность баланса 4·10⁻⁴). При усилиях выше ≈ 50 кН тормоза работают главным образом на гашение колебаний, поскольку энергия остаточного отката (≈ 87 Дж) на два порядка меньше энергии колебаний.')
remove(127,'Таблица 8 — '); assert els[128].tag==qn('w:tbl'); remove(128); expect(129,''); remove(129); remove(130,'Примечание: к моменту 600 мс')
# ---------------------------------------------------------------- section 8, conclusions
set_text(132,'К ограничениям','К ограничениям работы относятся одномерность продольной модели, не описывающей поперечно-поворотную составляющую ($d_Y$) и изгиб, использование эквивалентных нагрузок вместо измеренных давлений, закон Кулона с постоянным $\\mu$ (коэффициенты трения не определялись), а также то, что для опытов 2–3 известны только максимальные значения и каждая конфигурация испытана одним выстрелом.')
set_text(133,'Для проверки выводов','Для проверки выводов нужны тарировка тормозов с определением $\\mu_\\Sigma$, записи длительностью не менее 0,8 с с дополнительными марками у S1, S3, S5 и не менее трех выстрелов на конфигурацию: равномерную и рекомендуемую при $F_\\Sigma$ ≈ 60 кН.')
set_text(135,'1. По распределениям','1. Одномерная конечно-элементная модель, построенная по распределениям массы и осевой жесткости, независимо от эксперимента дает при жестких стыках первую продольную частоту 69,0 Гц; измеренные частота 64,18 ± 0,04 Гц и коэффициент передачи на базе марок воспроизводятся при жесткости стыков 12–28 ГН/м. Наблюдаемые колебания — первая продольная форма всей установки с узлом у муфты ПС2–ПС3.')
set_text(136,'2. По результатам','2. По опыту 1 $\\alpha$ = 5,98 ± 0,24 с⁻¹ и $\\zeta$ = 0,0148 ± 0,0006; асимметрия полупериодов объясняется наложением колебаний на дрейф. К 200 мс откат не завершен: 23 мм — перемещение к концу записи, расчетный полный откат составляет 35–50 мм.')
set_text(137,'3. Восстановлены','3. Эквивалентные газодинамические импульсы — 12,5 кН·с (казенная часть, начало при 47,9 мс в согласии с отметкой D1) и 10,5 кН·с (форкамера, максимум вблизи момента вылета). Остаточный импульс около 2 кН·с — малая разность больших величин, поэтому по одиночным выстрелам эффект тормозов не отделить от разброса нагружения на уровне 6–7 %.')
set_text(138,'4. Штатный тормоз','4. Штатный тормоз развивает нормальную силу 17,0 кН на 1 мм сжатия пакетов, его тормозная способность при $s$ = 0,5$h_0\'$ составляет 103–276 кН на установку ($\\mu_\\Sigma$ = 0,3–0,8). Эффективное усилие в опытах 2–3 (при одинаковом нагружении) — 30–37 кН, т.е. пакеты были сжаты всего на 0,2–0,7 мм.')
set_text(139,'5. Получены','5. Коэффициенты (6)–(8) эффективности сухого трения при наложении колебаний на откат показывают, что станция в узле первой формы (S3) эффективна для остановки отката, а станции в пучностях (S1, S5) — для гашения колебаний; они могут служить физически обоснованным критерием выбора мест установки тормозов.')
set_text(140,'6. Тормоза не увеличивают','6. Тормоза не увеличивают усилие в стыке ПС3–ФК: квазистатическая добавка (10) не превышает 0,7 % динамического усилия 3,1 МН, а гашение колебаний снижает его на величину до 12 %. Рост $d_X$ в опытах 2–3 следует связывать с разбросом нагружения и контактными явлениями в соединении.')
set_text(141,'7. Прямым моделированием','7. Прямым моделированием с контролем энергобаланса обоснована затяжка S1 : S2 : S3 ≈ 0,48 : 0,18 : 0,32 при суммарном усилии не менее 60 кН: она уменьшает полный откат на 6–12 % относительно равномерной схемы при том же гашении колебаний и при 60–100 кН ограничивает откат величиной 11–13 мм. Это расчетная рекомендация, которую следует проверить в испытаниях (раздел 8).')
# ---------------------------------------------------------------- abstract (RU, EN): shortened, structure of rule 5 kept
set_text(7,'Аннотация.','**Аннотация.** При выстреле многосекционной легкогазовой пушки на откат накладываются продольные упругие колебания, поэтому действие регулируемых фрикционных тормозов зависит и от суммарного тормозного усилия, и от мест его приложения. Для 50-мм пушки такого типа требовалось по экспериментальным данным и проверяемой численной модели обосновать, где размещать тормоза и как распределять между ними затяжку. По данным скоростной видеорегистрации трех выстрелов и одномерной конечно-элементной модели, которая независимо от эксперимента дает при жестких стыках первую продольную частоту 69,0 Гц, а измеренную частоту 64,18 ± 0,04 Гц воспроизводит при жесткости стыков 12–28 ГН/м, показано, что асимметрия полупериодов вызвана наложением колебаний на незавершенный откат: к концу записи зарегистрировано 23 мм, тогда как полный откат составляет 35–50 мм. Восстановлены эквивалентные газодинамические импульсы 12,5 и 10,5 кН·с. Эффективное усилие торможения в опытах составило 30–37 кН, что на два порядка меньше усилия в стыке поршневой трубы и форкамеры (≈ 3,1 МН), поэтому рост раскрытия стыка тормозами не вызван. Получены коэффициенты эффективности сухого трения, согласно которым станции вблизи узла первой формы эффективны для остановки отката, а станции в пучностях — для гашения колебаний. Прямым моделированием с контролем энергобаланса обоснована затяжка S1 : S2 : S3 ≈ 0,48 : 0,18 : 0,32, которая уменьшает откат на 6–12 % при том же гашении колебаний. Предложенные коэффициенты эффективности можно использовать при выборе мест установки тормозов и на других протяженных многосекционных пушках.')
set_text(177,'Abstract.','**Abstract.** When a multi-section light-gas gun is fired, longitudinal elastic vibrations are superimposed on its recoil, so the effect of adjustable friction brakes depends on the total braking force and on where this force is applied. For a 50 mm gun of this type, the task was to determine from experimental data and a verifiable numerical model where the brakes should be placed and how the preload should be distributed among them. Using high-speed video recordings of three shots and a one-dimensional finite element model that, independently of the experiment, gives a first longitudinal frequency of 69.0 Hz with rigid joints and reproduces the measured 64.18 ± 0.04 Hz with a joint stiffness of 12–28 GN/m, it is shown that the asymmetry of the half-periods results from vibrations superimposed on the unfinished recoil: 23 mm were recorded by the end of the record, whereas the full recoil is 35–50 mm. Equivalent gas-dynamic impulses of 12.5 and 10.5 kN·s were reconstructed. The effective braking force in the shots with brakes was 30–37 kN, two orders of magnitude lower than the force in the joint between the pump tube and the high-pressure section (≈ 3.1 MN); therefore, the brakes did not cause the increase in the joint opening. Efficiency coefficients of dry friction were obtained, according to which stations near the node of the first mode are effective in stopping the recoil, and stations at the antinodes in damping the vibrations. Direct simulation with energy balance control substantiates the preload ratio S1 : S2 : S3 ≈ 0.48 : 0.18 : 0.32, which reduces the recoil by 6–12% with the same vibration damping. The proposed efficiency coefficients can also be used to select brake locations on other long multi-section guns.')
# English author information: deleting the department placeholder left «Head of RFNC-VNIIEF» (RU: начальник отдела)
rep(204,'Head of Russian Federal','Head of Department, Russian Federal'); rep(204,'Chief Researcher, , A.V.','Chief Researcher, A.V.')
# ---------------------------------------------------------------- references: textbooks out (rule 11), renumber in citation order
DROP={6,8,15}; KEEP=[k for k in range(1,21) if k not in DROP]; NEWNUM={old:new for new,old in enumerate(KEEP,1)}
for base,first in ((144,'1. Серебряков'),(181,'1. Serebryakov')):
    expect(base,first)
    for old in range(1,21):
        el=els[base+old-1]; t0=el.find('.//'+qn('w:t'))
        assert t0.text.startswith('%d. '%old), (base,old,t0.text[:20])
        if old in DROP: el.getparent().remove(el)
        else: t0.text='%d. '%NEWNUM[old]+t0.text[len('%d. '%old):]
def _cite(m_):
    nums=set()
    for part in m_.group(1).split(','):
        part=part.strip()
        if '–' in part: a_,b_=map(int,part.split('–')); nums|=set(range(a_,b_+1))
        else: nums.add(int(part))
    new=sorted(NEWNUM[n] for n in nums if n in NEWNUM)
    if not new: return ''
    out=[]; i_=0
    while i_<len(new):
        j_=i_
        while j_+1<len(new) and new[j_+1]==new[j_]+1: j_+=1
        out.append('%d–%d'%(new[i_],new[j_]) if j_-i_>=2 else ', '.join(str(x) for x in new[i_:j_+1])); i_=j_+1
    return '['+', '.join(out)+']'
for el in els[:144]:
    if el.getparent() is None: continue
    for t in el.iter(qn('w:t')):
        if t.text and re.search(r'\[[\d,\s–]+\]',t.text):
            t.text=re.sub(r'\s?\[([\d,\s–]+)\]',lambda m_:(' '+_cite(m_)) if _cite(m_) else '',t.text)
# ---------------------------------------------------------------- spacing: headings and display formulas a bit tighter
from docx.text.paragraph import Paragraph
HEAD=re.compile(r'^(\d\. [А-Я]|Введение$|Заключение$|Литература$|Сведения об авторах$)')
for el in list(body.iterchildren(qn('w:p'))):
    pf=Paragraph(el,None).paragraph_format
    def _bold(r):
        b=r.find(qn('w:rPr')+'/'+qn('w:b')); return b is not None and b.get(qn('w:val')) not in ('0','false')
    if HEAD.match(tm(el)) and all(_bold(r) for r in el.findall(qn('w:r')) if (r.findtext(qn('w:t')) or '').strip()):
        pf.space_before=Pt(6); pf.space_after=Pt(2)
    elif el.find(M('oMath')) is not None and not ''.join(t.text or '' for t in el.iter(qn('w:t'))).strip(' \t()0123456789'):
        pf.space_before=Pt(2); pf.space_after=Pt(2)
# table 2: the period row repeats the frequency (T = 1/f)
tb2=els[33]; assert tb2.tag==qn('w:tbl')
rows=[tr for tr in tb2.findall(qn('w:tr')) if tm(tr).startswith('Период')]; assert len(rows)==1; tb2.remove(rows[0])
# ---------------------------------------------------------------- formulas: Greek and Cyrillic upright (rule 9); glyphs as in the authors' file
GREEK=re.compile(r'([Ͱ-Ͽἀ-῿Ѐ-ӿ]+)')
for t in body.iter(M('t')):
    if t.text: t.text=t.text.replace('−','-').replace('∗','*').replace('′',"'")
for r in list(body.iter(M('r'))):
    rpr=r.find(M('rPr'))
    if rpr is not None and (rpr.find(M('sty')) is not None or rpr.find(M('nor')) is not None): continue
    t=r.find(M('t'))
    if t is None or not t.text or not GREEK.search(t.text): continue
    tmpl=copy.deepcopy(r); prev=None
    for k,s in enumerate([s for s in GREEK.split(t.text) if s]):
        nr=copy.deepcopy(tmpl) if k else r
        nr.find(M('t')).text=s
        if GREEK.fullmatch(s):
            pr=nr.find(M('rPr'))
            if pr is None: pr=parse_xml('<m:rPr xmlns:m="%s"/>'%MNS); nr.insert(0,pr)
            sty=parse_xml('<m:sty xmlns:m="%s" m:val="p"/>'%MNS); nxt=[c for c in pr if c.tag in (M('brk'),M('aln'))]
            (nxt[0].addprevious(sty) if nxt else pr.append(sty))
        if k: prev.addnext(nr)
        prev=nr
# ---------------------------------------------------------------- checks: figures, tables, formula numbers and their references
alltxt='\n'.join(tm(p) for p in body.iter(qn('w:p')) if not is_eq(p))
ru=alltxt.split('\nЛитература\n')[0]
caps=[int(x) for x in re.findall(r'^Рисунок (\d+) —',ru,re.M)]; tcaps=[int(x) for x in re.findall(r'^Таблица (\d+) —',ru,re.M)]
assert caps==[1,2,3,4,5] and tcaps==[1,2,3,4,5,6,7], (caps,tcaps)
frefs={int(x) for x in re.findall(r'рисун\w*\s+(\d+)',ru.replace('Рисунок','#'))}; assert frefs=={1,2,3,4,5}, frefs
cits=[]
for g in re.findall(r'\[([\d,\s–]+)\]',ru):
    for part in g.split(','):
        part=part.strip(); a_,_,b_=part.partition('–'); cits+=list(range(int(a_),int(b_ or a_)+1))
first=[]
for c_ in cits:
    if c_ not in first: first.append(c_)
assert first==list(range(1,18)), first
nums=[int(re.search(r'\d+',''.join(t.text or '' for t in e.iter(qn('w:t')))).group()) for e in body.iter(qn('w:p')) if is_eq(e)]
cited=set()
for a_,b_ in re.findall(r'\((\d{1,2})\)(?:\s*–\s*\((\d{1,2})\))?',ru): cited|=set(range(int(a_),int(b_ or a_)+1))
assert nums==list(range(1,12)) and cited==set(nums), (nums,sorted(cited))
# drop images no longer referenced (rule 1: archive <= 5 MB)
used={e.get(qn('r:embed')) for e in body.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')}
for rId,rel in list(d.part.rels.items()):
    if rel.reltype.endswith('/image') and rId not in used: d.part.drop_rel(rId)
d.save(OUT); shutil.copy(OUT,SUB+'LGP-50_Izv_VUZ_Mashinostroenie.docx')
print('saved',OUT)
