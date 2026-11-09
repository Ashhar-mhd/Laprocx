"""Static site generator for laprocx.com (English + Arabic).

python3 gen.py prod  OUTDIR   -> clean URLs (/services/golden-visa/) for hosting
python3 gen.py preview OUTDIR -> relative links ending in index.html, for local/preview viewing
"""
import os, sys, json, re, shutil, html
from bs4 import BeautifulSoup
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content_services import S as SERVICES
from content_briefs import BRIEFS

MODE = sys.argv[1] if len(sys.argv) > 1 else 'preview'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '..', 'out-' + MODE)
BASE = 'https://laprocx.com'
WA_NUM = '971543368567'
PHONE = '+971 54 336 8567'
GTAG = '''
<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-MRF2XJKM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());</script>'''
EMAIL = 'laprocx@gmail.com'
IG_CREDIT = 'https://www.instagram.com/ashar_mhd__/'
BRAND = os.path.join(HERE, 'brand')        # copied brand assets
HOME_SRC = os.path.join(HERE, 'home.html')  # homepage body with data-ar

E = lambda s: html.escape(s, quote=True)

# ---------------------------------------------------------------- helpers
class Ctx:
    def __init__(s, path, lang):
        s.path, s.lang = path, lang  # path: clean english path like '/services/'
    @property
    def ar(s): return s.lang == 'ar'
    def t(s, pair): return pair[1] if s.ar else pair[0]
    def lpath(s, p, lang=None):
        lang = lang or s.lang
        return ('/ar' + p) if lang == 'ar' else p
    def here(s): return s.lpath(s.path)
    def url(s, p, lang=None, anchor=''):
        """link to a page given its english clean path"""
        target = s.lpath(p, lang)
        if MODE == 'prod':
            return target + anchor
        rel = os.path.relpath(target, s.here())
        return (rel.rstrip('/') + '/' if rel != '.' else '') + 'index.html' + anchor
    def asset(s, f):
        if MODE == 'prod':
            return '/assets/' + f
        return os.path.relpath('/assets/' + f, s.here())

def wa(text=''):
    from urllib.parse import quote
    return f'https://wa.me/{WA_NUM}' + (f'?text={quote(text)}' if text else '')

WAICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-wa"/></svg>'
ICONS = open(os.path.join(HERE, 'icons.svg')).read()
SVC_BY = {s['slug']: s for s in SERVICES}
NAV = [('/services/', ('Services', 'الخدمات')), ('/pro-plans/', ('PRO Plans', 'باقات المندوب')),
       ('/estimate/', ('Fee Estimate', 'تقدير الرسوم')), ('/brief/', ('Daily Brief', 'الموجز اليومي')),
       ('/about/', ('About', 'من نحن')), ('/contact/', ('Contact', 'تواصل معنا'))]

def header(c):
    nav = ''.join(f'<a href="{c.url(p)}"{" aria-current=page" if c.path==p else ""}>{c.t(n)}</a>' for p, n in NAV)
    other = 'en' if c.ar else 'ar'
    logo = 'laprocx-01-primary-horizontal-color.svg' if c.ar else 'laprocx-02-horizontal-english-color.svg'
    return f'''<header class="site"><div class="wrap">
<a class="logo" href="{c.url('/')}" aria-label="{c.t(('Laprocx Business Services home','الصفحة الرئيسية للابروكس'))}"><img src="{c.asset(logo)}" alt="{c.t(('Laprocx Business Services','لابروكس لخدمات الأعمال'))}" width="125" height="46"></a>
<nav class="main" aria-label="{c.t(('Main','القائمة الرئيسية'))}">{nav}</nav>
<a class="lang-link" href="{c.url('/' if c.path=='/404/' else c.path, other)}" hreflang="{other}" lang="{other}">{'English' if c.ar else 'العربية'}</a>
<a class="btn btn-wa" href="{wa()}">{WAICON}<span>{c.t(('WhatsApp','واتساب'))}</span></a>
</div><div class="wrap"><nav class="mnav" aria-label="{c.t(('Main','القائمة الرئيسية'))}">{nav}</nav></div></header>'''

def footer(c):
    def li(p, n, anchor=''): return f'<li><a href="{c.url(p, anchor=anchor)}">{c.t(n)}</a></li>'
    biz = ''.join(li(s['slug'], s['name']) for s in SERVICES if s['group']=='biz')
    ind = ''.join(li(s['slug'], s['name']) for s in SERVICES if s['group']=='ind')
    return f'''<footer><div class="wrap">
<div class="brand"><img src="{c.asset('laprocx-01-primary-horizontal-reverse.svg')}" alt="{c.t(('Laprocx Business Services','لابروكس لخدمات الأعمال'))}" width="174" height="64" loading="lazy"><p style="margin-top:1rem;max-width:22rem">{c.t(('Your partner for business and visa paperwork in the UAE.','شريكك في معاملات الأعمال والإقامات في الإمارات.'))}</p>
<p style="margin-top:1rem"><span dir="ltr">{PHONE}</span><br>{EMAIL}<br>{c.t(('Mon – Sat, 9 AM – 10 PM','الاثنين – السبت، ٩ ص – ١٠ م'))}</p></div>
<div><h4>{c.t(('For business','للشركات'))}</h4><ul>{biz}</ul></div>
<div><h4>{c.t(('For individuals','للأفراد'))}</h4><ul>{ind}</ul></div>
<div><h4>{c.t(('Laprocx','لابروكس'))}</h4><ul>{li('/pro-plans/',('PRO plans','باقات المندوب'))}{li('/brief/',('Daily Brief','الموجز اليومي'))}{li('/estimate/',('Fee estimate','تقدير الرسوم'))}{li('/about/',('About','من نحن'))}{li('/contact/',('Contact','تواصل معنا'))}</ul></div>
<div class="legal"><span>{c.t(('© 2026 Laprocx Business Services. A private business services company.','© ٢٠٢٦ لابروكس لخدمات الأعمال. شركة خدمات خاصة.'))}</span><span><a href="{c.url('/privacy/')}">{c.t(('Privacy','الخصوصية'))}</a> · <a href="{c.url('/terms/')}">{c.t(('Terms','الشروط'))}</a></span></div>
<p class="credit">{c.t(('Website designed by','تصميم الموقع:'))} <a href="{IG_CREDIT}" target="_blank" rel="noopener" dir="ltr">@Ashar_Mhd__</a></p>
</div></footer>
<a class="wa-float" href="{wa()}" aria-label="WhatsApp">{WAICON}</a>'''

def crumbs_schema(c, items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":c.t(n),"item":BASE+c.lpath(p)} for i,(p,n) in enumerate(items)]}

def crumbs_html(c, items):
    parts=[]
    for i,(p,n) in enumerate(items):
        parts.append(f'<span>{c.t(n)}</span>' if i==len(items)-1 else f'<a href="{c.url(p)}">{c.t(n)}</a><span aria-hidden="true">›</span>')
    return f'<nav class="crumbs" aria-label="{c.t(("Breadcrumb","مسار التصفح"))}">{"".join(parts)}</nav>'

HOME_CRUMB = ('/', ('Home','الرئيسية'))

def write_page(c, title, desc, body, schema=(), og_type='website', has_ar=True, noindex=False):
    alt = ''
    if has_ar:
        alt = (f'<link rel="alternate" hreflang="en" href="{BASE}{c.path}">'
               f'<link rel="alternate" hreflang="ar" href="{BASE}/ar{c.path}">'
               f'<link rel="alternate" hreflang="x-default" href="{BASE}{c.path}">')
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    canonical = BASE + c.here()
    full_title = title if 'Laprocx' in title or 'لابروكس' in title else f"{title} | {c.t(('Laprocx','لابروكس'))}"
    doc = f'''<!doctype html>
<html lang="{c.lang}" dir="{'rtl' if c.ar else 'ltr'}">
<head>{GTAG if MODE=='prod' else ''}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{canonical}">{alt}
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Laprocx Business Services">
<meta property="og:title" content="{E(full_title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}/assets/og-image.png">
<meta property="og:locale" content="{'ar_AE' if c.ar else 'en_AE'}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B4F45">
<link rel="icon" href="{c.asset('favicon.ico')}" sizes="any"><link rel="icon" type="image/png" sizes="192x192" href="{'/favicon-192.png' if MODE=='prod' else c.asset('app-icon-192.png')}"><link rel="icon" type="image/png" sizes="32x32" href="{c.asset('favicon-32.png')}">
<link rel="apple-touch-icon" href="{c.asset('apple-touch-icon-180.png')}"><link rel="manifest" href="{c.asset('site.webmanifest')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Baloo+Bhaijaan+2:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{c.asset('site.css')}">
{ld}
</head>
<body{' class="ar"' if c.ar else ''}>
{ICONS}
{header(c)}
<main id="top">
{body}
</main>
{footer(c)}
<script src="{c.asset('site.js')}" defer></script>
</body>
</html>'''
    out = os.path.join(OUT, c.here().lstrip('/'), 'index.html') if c.path != '/404/' else os.path.join(OUT, ('ar/' if c.ar else '') + '404.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(doc)
    PAGES.append((c.path, c.lang, noindex))

PAGES = []

def wa_btn(c, label, text=''):
    return f'<a class="btn btn-wa" href="{wa(text)}">{WAICON}<span>{c.t(label)}</span></a>'

def svc_card(c, s, feature=False):
    cls = 'svc feature corner' if feature else 'svc'
    return (f'<a class="{cls}" href="{c.url(s["slug"])}" data-k="{E(s["name"][0]+" "+s["name"][1])}"><span class="ic"><svg aria-hidden="true"><use href="#i-{s["icon"]}"/></svg></span>'
            f'<h3>{c.t(s["name"])}</h3><p>{c.t(s["card"])}</p><span class="go">{c.t(("Details →","التفاصيل ←"))}</span></a>')

import datetime as _dt
for _i,_b in enumerate(BRIEFS):
    _b['date']=_b['url'].split('/brief/')[1][:10]; _b['_i']=_i
BRIEFS = sorted(BRIEFS, key=lambda b:(b['date'], b['_i']), reverse=True)  # newest first
BRIEF_PATH = {b['file'].replace('.html',''): '/brief/' + b['url'].split('/brief/')[1] for b in BRIEFS}
def bpath(b): return BRIEF_PATH[b['file'].replace('.html','')]
_AR_DIG=str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩')
_MON_AR=['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
_DAY_AR=['الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت','الأحد']
def dshort(c, iso):
    d=_dt.date.fromisoformat(iso)
    return f"{d.day} {_MON_AR[d.month-1]} {d.year}".translate(_AR_DIG) if c.ar else d.strftime('%-d %b %Y')
def dlong(c, iso):
    d=_dt.date.fromisoformat(iso)
    return f"{_DAY_AR[d.weekday()]} {d.day} {_MON_AR[d.month-1]} {d.year}".translate(_AR_DIG) if c.ar else d.strftime('%A %-d %B %Y')
def dmeta(c, iso):
    d=_dt.date.fromisoformat(iso)
    return f"{_DAY_AR[d.weekday()]} {d.day} {_MON_AR[d.month-1]} {d.year}".translate(_AR_DIG) if c.ar else d.strftime('%a %-d %b %Y')

# ---------------------------------------------------------------- service pages
def service_page(c, s):
    grp = ('For business','للشركات') if s['group']=='biz' else ('For individuals','للأفراد')
    items = [HOME_CRUMB, ('/services/', ('Services','الخدمات')), (s['slug'], s['name'])]
    docs = ''.join(f'<li>{c.t(d)}</li>' for d in s['docs'])
    steps = ''.join(f'<li>{c.t(d)}</li>' for d in s['steps'])
    faq = ''.join(f'<details{" open" if i==0 else ""}><summary>{c.t(q)}</summary><p>{c.t(a)}</p></details>' for i,(q,a) in enumerate(s['faq']))
    msg = c.t((f"Hello Laprocx, I need help with: {s['name'][0]}.", f"مرحباً لابروكس، أحتاج مساعدة في: {s['name'][1]}."))
    related = [o for o in SERVICES if o['group']==s['group'] and o is not s][:4]
    rel = ''.join(f'<a href="{c.url(o["slug"])}">{c.t(o["name"])}<small>{c.t(o["card"])}</small></a>' for o in related)
    brief_box = ''
    rel_b=[b for b in BRIEFS if b['svc']==s['slug']][:3]
    if rel_b:
        items_b=''.join(f'<a href="{c.url(bpath(b))}">{c.t((b["title_en"],b["title_ar"]))}<small>{dshort(c,b["date"])}</small></a>' for b in rel_b)
        brief_box = f'<div class="box"><h3>{c.t(("From the Daily Brief","من الموجز اليومي"))}</h3><div class="mini">{items_b}</div></div>'
    more = ''
    if s.get('more'):
        more = f'<a class="btn btn-ghost" href="{c.url(s["more"][0])}">{c.t(s["more"][1])}</a>'
    body = f'''<section class="page-hero" style="padding:0"><div class="wrap">
{crumbs_html(c, items)}
<p class="eyebrow">{c.t(grp)}</p>
<h1>{c.t(s['name'])}</h1>
<p class="lede">{c.t(s['lede'])}</p>
<div class="btns">{wa_btn(c, ('Start on WhatsApp','ابدأ على واتساب'), msg)}<a class="btn btn-ghost" href="{c.url('/estimate/')}?s={s['slug'].strip('/').split('/')[-1]}">{c.t(('Get a fee estimate','احصل على تقدير الرسوم'))}</a>{more}</div>
<dl class="facts">
<div><dt>{c.t(('Typical time','المدة المعتادة'))}</dt><dd>{c.t(s['time'])}</dd></div>
<div><dt>{c.t(('Documents','المستندات'))}</dt><dd>{c.t((f"{len(s['docs'])} main documents", f"{len(s['docs'])} مستندات أساسية"))}</dd></div>
<div><dt>{c.t(('Fees','الرسوم'))}</dt><dd>{c.t(('Written quote before we start','عرض مكتوب قبل البدء'))}</dd></div>
</dl>
</div></section>
<div class="wrap content"><div class="art" style="padding:0">
<div>
<section class="part"><h2><i></i><span>{c.t(("Who it's for","لمن هذه الخدمة"))}</span></h2><p>{c.t(s['who'])}</p></section>
<section class="part"><h2><i></i><span>{c.t(('Documents you usually need','المستندات المطلوبة عادةً'))}</span></h2><ul class="checks">{docs}</ul>
<p class="note-sm">{c.t(('We confirm the exact list for your case on WhatsApp before you start.','نؤكد لك القائمة الدقيقة لحالتك على واتساب قبل البدء.'))}</p></section>
<section class="part"><h2><i></i><span>{c.t(('How it works','كيف تتم المعاملة'))}</span></h2><ol class="flow">{steps}</ol></section>
<section class="part"><h2><i></i><span>{c.t(('Fees','الرسوم'))}</span></h2><p>{c.t(('You pay two things: the government fees, charged at cost, and our service fee. We send both in a written quote before we start, so there are no surprises.','تدفع أمرين: الرسوم الحكومية بتكلفتها الفعلية، ورسوم خدمتنا. نرسلهما في عرض مكتوب قبل البدء حتى لا تكون هناك مفاجآت.'))}</p></section>
<section class="part do"><h2><i></i><span>{c.t(('Common questions','أسئلة شائعة'))}</span></h2><div class="faq">{faq}</div>
{wa_btn(c, ('Ask us on WhatsApp','اسألنا على واتساب'), msg)}</section>
<p class="disc">{c.t(('Laprocx is a private business services company. We prepare and submit applications through the official government channels. Rules and fees can change, and we check them before every application.','لابروكس شركة خدمات أعمال خاصة. نجهز الطلبات ونقدمها عبر القنوات الحكومية الرسمية. القواعد والرسوم قد تتغير، ونتحقق منها قبل كل معاملة.'))}</p>
</div>
<aside class="side">
<div class="box green"><h3>{c.t(('We handle it for you','نتولاها عنك'))}</h3><p>{c.t(('Send your documents on WhatsApp and get a written quote.','أرسل مستنداتك على واتساب واحصل على عرض مكتوب.'))}</p><a class="btn btn-gold" href="{wa(msg)}">{c.t(('Start now →','ابدأ الآن ←'))}</a></div>
{brief_box}
<div class="box"><h3>{c.t(('Related services','خدمات ذات صلة'))}</h3><div class="mini">{rel}</div></div>
</aside>
</div></div>'''
    schema = [crumbs_schema(c, items),
              {"@context":"https://schema.org","@type":"Service","name":c.t(s['name']),"description":c.t(s['desc']),
               "provider":{"@type":"ProfessionalService","name":"Laprocx Business Services","url":BASE+'/',"telephone":PHONE},
               "areaServed":{"@type":"Country","name":"United Arab Emirates"},"url":BASE+c.here()},
              {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":c.t(q),"acceptedAnswer":{"@type":"Answer","text":c.t(a)}} for q,a in s['faq']]}]
    write_page(c, c.t(s['title']), c.t(s['desc']), body, schema)

# ---------------------------------------------------------------- services index
def services_index(c):
    items=[HOME_CRUMB, ('/services/', ('Services','الخدمات'))]
    biz=''.join(svc_card(c,s,s.get('feature')) for s in SERVICES if s['group']=='biz')
    ind=''.join(svc_card(c,s,s.get('feature')) for s in SERVICES if s['group']=='ind')
    body=f'''<section class="page-hero" style="padding:0"><div class="wrap">{crumbs_html(c,items)}
<p class="eyebrow">{c.t(('Services','الخدمات'))}</p><h1>{c.t(('Every service, one team','كل الخدمات، فريق واحد'))}</h1>
<p class="lede">{c.t(('Company setup, PRO work, visas, attestation, typing and travel. Pick a service to see the documents, steps and typical time.','تأسيس الشركات، وخدمات المندوب، والإقامات، والتصديقات، والطباعة، والسفر. اختر الخدمة لترى المستندات والخطوات والمدة المعتادة.'))}</p></div></section>
<div class="wrap content"><h2 class="sub-h">{c.t(('For business','للشركات'))}</h2><div class="svc-grid all">{biz}</div>
<h2 class="sub-h">{c.t(('For individuals','للأفراد'))}</h2><div class="svc-grid all">{ind}</div>
<div class="cta-box corner"><div><h2>{c.t(("Can't find what you need?","لم تجد ما تبحث عنه؟"))}</h2><p>{c.t(('Send us the details on WhatsApp. If it is government paperwork in the UAE, we can usually help.','أرسل لنا التفاصيل على واتساب. إن كانت معاملة حكومية في الإمارات فغالباً نستطيع المساعدة.'))}</p></div><div>{wa_btn(c,('Ask on WhatsApp','اسأل على واتساب'))}</div></div></div>'''
    write_page(c, c.t(('UAE Business, Visa and PRO Services','خدمات الأعمال والإقامات والمندوب في الإمارات')),
      c.t(('All Laprocx services: company setup, PRO services, licence renewal, employee, golden, freelance and family visas, attestation, typing, insurance and travel.','كل خدمات لابروكس: تأسيس الشركات، خدمات المندوب، تجديد الرخص، إقامات الموظفين والذهبية والعمل الحر والعائلية، التصديقات، الطباعة، التأمين والسفر.')),
      body, [crumbs_schema(c,items)])

# ---------------------------------------------------------------- PRO plans
PLANS = [
 (('Starter','البداية'),('Sole owners and teams up to 5','للمستقلين والشركات حتى ٥ موظفين'),[('Licence and visa renewal reminders','تذكير بتجديد الرخصة والإقامات'),('Up to 4 transactions a month','حتى ٤ معاملات شهرياً'),('WhatsApp support','دعم عبر واتساب')],False),
 (('Growth','النمو'),('Companies with 6 to 25 staff','للشركات من ٦ إلى ٢٥ موظفاً'),[('Everything in Starter','كل ما في باقة البداية'),('A named PRO for your company','مندوب مخصص لشركتك'),('Up to 12 transactions a month','حتى ١٢ معاملة شهرياً'),('Monthly report of deadlines and renewals','تقرير شهري بالمواعيد والتجديدات')],True),
 (('Enterprise','المؤسسات'),('25+ staff or several licences','لأكثر من ٢٥ موظفاً أو عدة رخص'),[('Everything in Growth','كل ما في باقة النمو'),('Unlimited transactions within scope','معاملات غير محدودة ضمن الاتفاق'),('Office visits when needed','زيارات للمكتب عند الحاجة')],False)]
def plans_html(c):
    out=''
    for n,f,lis,pick in PLANS:
        li=''.join(f'<li>{c.t(x)}</li>' for x in lis)
        msg=c.t((f'Hello Laprocx, I would like a quote for the {n[0]} PRO plan.',f'مرحباً لابروكس، أريد عرض سعر لباقة {n[1]}.'))
        badge=f'<span class="badge">{c.t(("Most asked","الأكثر طلباً"))}</span>' if pick else ''
        btn='btn-gold' if pick else 'btn-ghost'
        out+=f'''<div class="plan{' pick corner' if pick else ''}">{badge}<h3>{c.t(n)}</h3><p class="for">{c.t(f)}</p><ul>{li}</ul>
<p class="price">{c.t(('Price on request','السعر عند الطلب'))}<small>{c.t(('Set after a short call','يُحدد بعد مكالمة قصيرة'))}</small></p><a class="btn {btn}" href="{wa(msg)}">{c.t(('Get a quote','اطلب عرض سعر'))}</a></div>'''
    return out
def pro_plans(c):
    items=[HOME_CRUMB, ('/pro-plans/', ('PRO Plans','باقات المندوب'))]
    tasks=[('New and renewed staff visas','إصدار وتجديد إقامات الموظفين'),('Labour contracts and cancellations','عقود العمل والإلغاء'),('Trade licence renewal','تجديد الرخصة التجارية'),('Establishment card and immigration file','بطاقة المنشأة وملف الإقامة'),('Ejari and tenancy registration','تسجيل إيجاري وعقود الإيجار'),('Document attestation and translation','تصديق وترجمة المستندات')]
    t=''.join(f'<li>{c.t(x)}</li>' for x in tasks)
    faq=[(('What counts as one transaction?','ما الذي يُحتسب معاملة واحدة؟'),('One application to one government office, for example one visa renewal or one licence renewal. We list them on your monthly report.','طلب واحد لدى جهة حكومية واحدة، مثل تجديد إقامة واحدة أو تجديد رخصة واحدة. نوضحها في تقريرك الشهري.')),
         (('Are government fees included?','هل الرسوم الحكومية مشمولة؟'),('No. Government fees are charged at cost and shown separately on every invoice.','لا. الرسوم الحكومية تُحتسب بتكلفتها الفعلية وتظهر منفصلة في كل فاتورة.')),
         (('Can I change or cancel my plan?','هل يمكنني تغيير الباقة أو إلغاؤها؟'),('Yes. You can move between plans or stop at the end of any month.','نعم. يمكنك الانتقال بين الباقات أو التوقف في نهاية أي شهر.'))]
    fq=''.join(f'<details{" open" if i==0 else ""}><summary>{c.t(q)}</summary><p>{c.t(a)}</p></details>' for i,(q,a) in enumerate(faq))
    body=f'''<section class="page-hero" style="padding:0"><div class="wrap">{crumbs_html(c,items)}
<p class="eyebrow">{c.t(('Monthly PRO plans','باقات المندوب الشهرية'))}</p><h1>{c.t(('A PRO for your company, without the hire','مندوب لشركتك، بدون توظيف'))}</h1>
<p class="lede">{c.t(('One fixed monthly fee for our work. We track every deadline, handle the applications and send you a monthly summary. Government fees are charged at cost.','رسوم شهرية ثابتة لعملنا. نتابع كل المواعيد ونتولى المعاملات ونرسل لك خلاصة شهرية. الرسوم الحكومية بتكلفتها الفعلية.'))}</p></div></section>
<div class="wrap content"><div class="plans">{plans_html(c)}</div>
<div class="split" style="margin-top:4rem"><div class="prose"><h2 style="margin-top:0">{c.t(('What your PRO handles','ما يتولاه المندوب'))}</h2><ul class="checks">{t}</ul></div>
<div class="faq"><h2 class="sub-h">{c.t(('Common questions','أسئلة شائعة'))}</h2>{fq}</div></div></div>'''
    write_page(c, c.t(('Monthly PRO Service Plans for UAE Companies','باقات خدمات المندوب الشهرية للشركات')),
      c.t(('Laprocx monthly PRO plans for UAE companies: Starter, Growth and Enterprise. Visas, labour contracts, licence renewals and reminders.','باقات المندوب الشهرية من لابروكس: البداية والنمو والمؤسسات. الإقامات وعقود العمل وتجديد الرخص والتذكير بالمواعيد.')),
      body, [crumbs_schema(c,items),{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":c.t(q),"acceptedAnswer":{"@type":"Answer","text":c.t(a)}} for q,a in faq]}])

# ---------------------------------------------------------------- estimate
EMIRATES=[('Dubai','دبي'),('Sharjah','الشارقة'),('Abu Dhabi','أبوظبي'),('Ajman','عجمان'),('Umm Al Quwain','أم القيوين'),('Ras Al Khaimah','رأس الخيمة'),('Fujairah','الفجيرة')]
def estimate(c):
    items=[HOME_CRUMB, ('/estimate/', ('Fee Estimate','تقدير الرسوم'))]
    data={s['slug'].strip('/').split('/')[-1]:{'name':c.t(s['name']),'time':c.t(s['time']),'docs':[c.t(d) for d in s['docs']],'url':c.url(s['slug'])} for s in SERVICES}
    opts=''.join(f'<option value="{k}">{E(v["name"])}</option>' for k,v in data.items())
    em=''.join(f'<option>{c.t(e)}</option>' for e in EMIRATES)
    body=f'''<section class="page-hero" style="padding:0"><div class="wrap">{crumbs_html(c,items)}
<p class="eyebrow">{c.t(('Fee estimate','تقدير الرسوم'))}</p><h1>{c.t(('Know what you need before you start','اعرف ما تحتاجه قبل أن تبدأ'))}</h1>
<p class="lede">{c.t(('Pick a service and your emirate. You see the documents and typical time right away, then send it to us on WhatsApp for a written fee quote.','اختر الخدمة والإمارة. ترى المستندات والمدة المعتادة فوراً، ثم أرسلها لنا على واتساب لتصلك الرسوم في عرض مكتوب.'))}</p></div></section>
<div class="wrap content"><div class="split">
<div class="est corner"><form class="form" id="est-form">
<label for="est-svc">{c.t(('1. Service','١. الخدمة'))}<select id="est-svc" name="svc">{opts}</select></label>
<label for="est-em">{c.t(('2. Emirate','٢. الإمارة'))}<select id="est-em" name="em">{em}</select></label>
<label for="est-n">{c.t(('3. How many people or documents?','٣. كم شخصاً أو مستنداً؟'))}<select id="est-n" name="n"><option>1</option><option>2</option><option>3</option><option>4</option><option>5+</option></select></label>
</form>
<div class="est-out on" id="est-out" aria-live="polite"><h3 id="est-name"></h3><p><b>{c.t(('Typical time:','المدة المعتادة:'))}</b> <span id="est-time"></span></p>
<p style="margin-top:.8rem"><b>{c.t(('Documents you usually need:','المستندات المطلوبة عادةً:'))}</b></p><ul class="checks" id="est-docs"></ul>
<div class="btns" style="display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.2rem"><a class="btn btn-wa" id="est-wa" href="{wa()}">{WAICON}<span>{c.t(('Send to WhatsApp for a quote','أرسلها على واتساب لعرض السعر'))}</span></a><a class="btn btn-ghost" id="est-more" href="#">{c.t(('Service details','تفاصيل الخدمة'))}</a></div></div></div>
<div class="prose"><h2 style="margin-top:0">{c.t(('How the quote works','كيف يتم عرض السعر'))}</h2>
<p>{c.t(('Every quote has two parts. Government fees are set by the authorities and charged at cost. Our service fee covers typing, submitting and following up.','كل عرض سعر من جزأين: الرسوم الحكومية تحددها الجهات الرسمية وتُحتسب بتكلفتها، ورسوم خدمتنا تغطي الطباعة والتقديم والمتابعة.'))}</p>
<p>{c.t(('Government fees change from time to time and depend on your case, so we confirm them in writing before you pay anything.','الرسوم الحكومية تتغير من وقت لآخر وتختلف حسب الحالة، لذلك نؤكدها كتابياً قبل أن تدفع أي شيء.'))}</p></div>
</div></div>
<script>window.LPX_EST={json.dumps({'data':data,'lang':c.lang,'wa':WA_NUM},ensure_ascii=False)};</script>'''
    write_page(c, c.t(('UAE Visa and Business Fee Estimate','تقدير رسوم الإقامات والأعمال في الإمارات')),
      c.t(('See the documents and typical time for any Laprocx service, then get a written fee quote on WhatsApp.','اطلع على المستندات والمدة المعتادة لأي خدمة من لابروكس، ثم احصل على عرض رسوم مكتوب عبر واتساب.')), body, [crumbs_schema(c,items)])

# ---------------------------------------------------------------- about
def about(c):
    items=[HOME_CRUMB, ('/about/', ('About','من نحن'))]
    body=f'''<section class="page-hero" style="padding:0"><div class="wrap">{crumbs_html(c,items)}
<p class="eyebrow">{c.t(('About Laprocx','عن لابروكس'))}</p><h1>{c.t(('Paperwork, handled.','معاملاتك… علينا.'))}</h1>
<p class="lede">{c.t(('Laprocx Business Services is a UAE business services company for founders, companies and professionals. We take care of government paperwork so you can get on with your work.','لابروكس لخدمات الأعمال شركة خدمات في الإمارات للمؤسسين والشركات والمهنيين. نتولى المعاملات الحكومية لتتفرغ أنت لعملك.'))}</p></div></section>
<div class="wrap content"><div class="split"><div class="prose">
<h2 style="margin-top:0">{c.t(('What we do','ماذا نقدم'))}</h2>
<p>{c.t(('We set up companies, act as a monthly PRO for businesses, and handle Golden, Freelance, Investor, employee and family visas. We also do the everyday work: typing, attestation, translation, insurance and travel.','نؤسس الشركات، ونعمل كمندوب شهري للشركات، ونتولى الإقامات الذهبية والعمل الحر والمستثمر والموظفين والعائلية. كما نقدم الخدمات اليومية: الطباعة والتصديق والترجمة والتأمين والسفر.'))}</p>
<h2>{c.t(('How we work','طريقتنا في العمل'))}</h2>
<ul class="checks"><li>{c.t(('Online first. Most applications start with photos of your documents on WhatsApp.','أونلاين أولاً. معظم المعاملات تبدأ بصور المستندات على واتساب.'))}</li>
<li>{c.t(('Clear quotes. Government fees and our fee are shown separately, in writing.','عروض واضحة. الرسوم الحكومية ورسومنا منفصلة ومكتوبة.'))}</li>
<li>{c.t(('Updates at every step, so you never have to chase us.','تحديثات في كل مرحلة، حتى لا تضطر للسؤال.'))}</li>
<li>{c.t(('Reminders before your licence, visas and IDs expire.','تذكير قبل انتهاء رخصتك وإقاماتك وهوياتك.'))}</li></ul>
<h2>{c.t(('Who we are','من نحن'))}</h2>
<p>{c.t(('Laprocx is a private business services company. We are not a government office. We prepare your applications and submit them through the official government channels, then follow them until they are approved.','لابروكس شركة خدمات أعمال خاصة، ولسنا جهة حكومية. نجهز طلباتك ونقدمها عبر القنوات الحكومية الرسمية، ونتابعها حتى الاعتماد.'))}</p>
</div>
<div class="cta-box corner" style="grid-template-columns:1fr"><div><h2>{c.t(('Talk to us','تواصل معنا'))}</h2><p>{c.t(('Tell us what you need and we will reply with a clear plan.','أخبرنا بما تحتاجه ونرد عليك بخطة واضحة.'))}</p></div>
<dl class="contact-list"><div><dt>{c.t(('WhatsApp / phone','واتساب / هاتف'))}</dt><dd dir="ltr">{PHONE}</dd></div><div><dt>{c.t(('Email','البريد'))}</dt><dd dir="ltr">{EMAIL}</dd></div><div><dt>{c.t(('Office','المكتب'))}</dt><dd>{c.t(('Announced soon','يُعلن عنه قريباً'))}</dd></div></dl>
<div>{wa_btn(c,('Start on WhatsApp','ابدأ على واتساب'))}</div></div></div></div>'''
    write_page(c, c.t(('About Laprocx Business Services','عن لابروكس لخدمات الأعمال')),
      c.t(('Laprocx Business Services helps UAE founders, companies and professionals with company setup, PRO services, visas and everyday paperwork.','تساعد لابروكس لخدمات الأعمال المؤسسين والشركات والمهنيين في الإمارات في تأسيس الشركات وخدمات المندوب والإقامات والمعاملات اليومية.')), body, [crumbs_schema(c,items)])

# ---------------------------------------------------------------- contact
def contact(c):
    items=[HOME_CRUMB, ('/contact/', ('Contact','تواصل معنا'))]
    opts=''.join(f'<option>{c.t(s["name"])}</option>' for s in SERVICES)+f'<option>{c.t(("Something else","أمر آخر"))}</option>'
    body=f'''<section class="page-hero" style="padding:0"><div class="wrap">{crumbs_html(c,items)}
<p class="eyebrow">{c.t(('Contact','تواصل معنا'))}</p><h1>{c.t(('Tell us what you need','أخبرنا بما تحتاجه'))}</h1>
<p class="lede">{c.t(('WhatsApp is the fastest way to reach us. Our new office opens soon, and until then we serve you on WhatsApp, phone and email.','واتساب هو أسرع طريقة للتواصل معنا. مكتبنا الجديد سيفتتح قريباً، وحتى ذلك الحين نخدمك عبر واتساب والهاتف والبريد.'))}</p></div></section>
<div class="wrap content"><div class="split">
<div class="est corner"><h3 style="margin-top:0">{c.t(('Send us a message','أرسل لنا رسالة'))}</h3>
<form class="form" id="contact-form" data-wa="{WA_NUM}" data-lang="{c.lang}">
<label for="cf-name">{c.t(('Your name','اسمك'))}<input id="cf-name" name="name" autocomplete="name" required></label>
<label for="cf-svc">{c.t(('Service','الخدمة'))}<select id="cf-svc" name="svc">{opts}</select></label>
<label for="cf-msg">{c.t(('Message','الرسالة'))}<textarea id="cf-msg" name="msg" placeholder="{c.t(('For example: my visa expires on 20 December','مثال: إقامتي تنتهي في ٢٠ ديسمبر'))}"></textarea></label>
<button class="btn btn-wa" type="submit">{WAICON}<span>{c.t(('Send on WhatsApp','أرسل على واتساب'))}</span></button>
<p class="note-sm">{c.t(('This opens WhatsApp with your message ready to send.','يفتح هذا واتساب ورسالتك جاهزة للإرسال.'))}</p></form></div>
<div><dl class="contact-list" style="font-size:1.05rem">
<div><dt>{c.t(('WhatsApp / phone','واتساب / هاتف'))}</dt><dd dir="ltr">{PHONE}</dd></div>
<div><dt>{c.t(('Email','البريد'))}</dt><dd dir="ltr">{EMAIL}</dd></div>
<div><dt>{c.t(('Hours','المواعيد'))}</dt><dd>{c.t(('Mon – Sat, 9 AM – 10 PM','الاثنين – السبت، ٩ ص – ١٠ م'))}</dd></div>
<div><dt>{c.t(('Office','المكتب'))}</dt><dd>{c.t(('Announced soon','يُعلن عنه قريباً'))}</dd></div></dl>
<div style="display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.6rem">{wa_btn(c,('Chat on WhatsApp','تحدث على واتساب'))}<a class="btn btn-ghost" href="mailto:{EMAIL}">{c.t(('Email us','راسلنا بالبريد'))}</a></div></div>
</div></div>'''
    write_page(c, c.t(('Contact Laprocx Business Services','تواصل مع لابروكس لخدمات الأعمال')),
      c.t((f'Contact Laprocx on WhatsApp {PHONE} or {EMAIL}. Open Monday to Saturday, 9 AM to 10 PM.',f'تواصل مع لابروكس على واتساب {PHONE} أو {EMAIL}. من الاثنين إلى السبت، ٩ صباحاً – ١٠ مساءً.')), body, [crumbs_schema(c,items)])

# ---------------------------------------------------------------- legal
def legal(c, path, title, sections):
    items=[HOME_CRUMB,(path,title)]
    secs=''.join(f'<h2>{c.t(h)}</h2><p>{c.t(p)}</p>' for h,p in sections)
    body=f'''<section class="page-hero" style="padding:0"><div class="wrap">{crumbs_html(c,items)}<h1>{c.t(title)}</h1><p class="lede">{c.t(('Last updated 9 November 2026','آخر تحديث ٩ نوفمبر ٢٠٢٦'))}</p></div></section>
<div class="wrap content"><div class="prose">{secs}</div></div>'''
    write_page(c, c.t(title), c.t(title)+' – Laprocx Business Services', body, [crumbs_schema(c,items)])

PRIVACY=[(('What we collect','ما نجمعه'),('We collect the details and documents you send us to process your application: for example your name, phone number, passport, visa and Emirates ID copies.','نجمع البيانات والمستندات التي ترسلها لنا لإنجاز معاملتك، مثل الاسم ورقم الهاتف ونسخ الجواز والإقامة والهوية.')),
 (('How we use it','كيف نستخدمها'),('We use your information only to prepare and submit your applications, contact you about them, and send renewal reminders you asked for.','نستخدم بياناتك فقط لتجهيز طلباتك وتقديمها، والتواصل معك بشأنها، وإرسال تذكيرات التجديد التي طلبتها.')),
 (('Who we share it with','مع من نشاركها'),('We share documents only with the government authorities and service providers (such as insurers or translators) needed for your application.','نشارك المستندات فقط مع الجهات الحكومية ومقدمي الخدمات (مثل شركات التأمين أو المترجمين) اللازمين لمعاملتك.')),
 (('How long we keep it','مدة الاحتفاظ بها'),('We keep documents as long as needed for your application and renewals, then delete them. You can ask us to delete your data at any time.','نحتفظ بالمستندات طوال المدة اللازمة للمعاملة والتجديد ثم نحذفها. يمكنك طلب حذف بياناتك في أي وقت.')),
 (('Website analytics','تحليلات الموقع'),('This website uses Google Analytics to count visits, the pages people read, and clicks on buttons such as WhatsApp or Call. Google may set cookies to do this. It does not collect your documents, and we never send your name or phone number to Google Analytics.','يستخدم هذا الموقع Google Analytics لعدّ الزيارات والصفحات التي تُقرأ والنقرات على أزرار مثل واتساب والاتصال، وقد تضع Google ملفات تعريف الارتباط لذلك. لا يجمع الموقع مستنداتك، ولا نرسل اسمك أو رقم هاتفك إلى Google Analytics.')),
 (('Contact','التواصل'),(f'For any privacy question, email {EMAIL}.',f'لأي استفسار عن الخصوصية، راسلنا على {EMAIL}.'))]
TERMS=[(('Our service','خدمتنا'),('Laprocx Business Services is a private company. We prepare and submit applications on your behalf through official government channels. Approval decisions are made by the government authorities, not by Laprocx.','لابروكس لخدمات الأعمال شركة خاصة. نجهز الطلبات ونقدمها نيابةً عنك عبر القنوات الحكومية الرسمية. قرارات الموافقة تتخذها الجهات الحكومية وليس لابروكس.')),
 (('Quotes and fees','العروض والرسوم'),('We send a written quote before we start. Government fees are charged at cost and can change if the authority changes them. Our service fee is agreed in the quote.','نرسل عرضاً مكتوباً قبل البدء. الرسوم الحكومية بتكلفتها الفعلية وقد تتغير إذا غيرتها الجهة المختصة. رسوم خدمتنا يُتفق عليها في العرض.')),
 (('Your documents','مستنداتك'),('You are responsible for the documents and information you give us being true and complete.','أنت مسؤول عن صحة واكتمال المستندات والمعلومات التي تقدمها لنا.')),
 (('Refunds','الاسترداد'),('Government fees already paid usually cannot be refunded. If we have not started work, we refund our service fee.','الرسوم الحكومية المدفوعة لا تُسترد غالباً. إذا لم نبدأ العمل نعيد لك رسوم خدمتنا.')),
 (('Website content','محتوى الموقع'),('Daily Briefs and service pages are general information, not legal advice. Always check your own case with us before you act.','الموجزات اليومية وصفحات الخدمات معلومات عامة وليست استشارة قانونية. تحقق دائماً من حالتك معنا قبل التصرف.'))]

# ---------------------------------------------------------------- briefs
def brief_dict(b, c):
    return {k: (b[k+'_ar'] if c.ar else b[k+'_en']) for k in ('topic','title','sum','what','who','do')}
def brief_page(c, b):
    bp=bpath(b); d=brief_dict(b,c)
    items=[HOME_CRUMB,('/brief/',('Daily Brief','الموجز اليومي')),(bp,(b['title_en'],b['title_ar']))]
    srcs=''.join(f'<li><a href="{u}" rel="noopener" target="_blank">{c.t((e,a))}</a></li>' for e,a,u in b['sources'])
    svc=SVC_BY[b['svc']]
    same=[o for o in BRIEFS if o is not b and o['date']==b['date']] or [o for o in BRIEFS if o is not b]
    others=''.join(f'<a href="{c.url(bpath(o))}">{c.t((o["title_en"],o["title_ar"]))}<small>{c.t((o["topic_en"],o["topic_ar"]))} · {dshort(c,o["date"])}</small></a>' for o in same[:4])
    body=f'''<div class="wrap">{crumbs_html(c,items)}
<div class="art"><article>
<div class="meta" style="margin-top:1.2rem"><span class="tag">{d['topic']}</span><time datetime="{b['date']}">{dmeta(c,b['date'])}</time><span class="src">{b['src']}</span><span>{c.t(('1 min read','قراءة دقيقة واحدة'))}</span></div>
<h1>{d['title']}</h1><p class="sum">{d['sum']}</p>
<section class="part"><h2><i></i><span>{c.t(('What it is','ما الموضوع'))}</span></h2>{d['what']}</section>
<section class="part"><h2><i></i><span>{c.t(('Who it affects','من يتأثر'))}</span></h2>{d['who']}</section>
<section class="part do"><h2><i></i><span>{c.t(('What to do','ماذا تفعل'))}</span></h2>{d['do']}{wa_btn(c,('Send your documents on WhatsApp','أرسل مستنداتك على واتساب'))}</section>
<section class="part source"><h2><i></i><span>{c.t(('Official source','المصدر الرسمي'))}</span></h2><ul>{srcs}</ul></section>
<p class="disc">{c.t(('Rules and fees can change. We check the official source before every application.','القواعد والرسوم قد تتغير. نتحقق من المصدر الرسمي قبل كل معاملة.'))}</p>
</article><aside class="side">
<div class="box green"><h3>{c.t(('We can handle this for you','نتولاها عنك'))}</h3><p>{c.t(svc['card'])}</p><a class="btn btn-gold" href="{c.url(svc['slug'])}">{c.t(svc['name'])} {c.t(('→','←'))}</a></div>
<div class="box"><h3>{c.t(('More briefs','موجزات أخرى'))}</h3><div class="mini">{others}</div></div>
</aside></div></div>'''
    schema=[crumbs_schema(c,items),{"@context":"https://schema.org","@type":"Article","headline":d['title'],"description":d['sum'],"datePublished":b["date"],"dateModified":b["date"],"inLanguage":c.lang,
            "author":{"@type":"Organization","name":"Laprocx Business Services"},"publisher":{"@type":"Organization","name":"Laprocx Business Services","logo":{"@type":"ImageObject","url":BASE+"/assets/app-icon-512.png"}},"mainEntityOfPage":BASE+c.here()}]
    write_page(c, d['title'], d['sum'], body, schema, og_type='article')

def brief_index(c):
    items=[HOME_CRUMB,('/brief/',('Daily Brief','الموجز اليومي'))]
    topic_k={'visa':('Visas','الإقامات'),'golden':('Golden visa','الإقامة الذهبية'),'business':('Business','الأعمال')}
    def card(b):
        d=brief_dict(b,c)
        return f'<a class="card" href="{c.url(bpath(b))}" data-t="{b["topic"]}"><div class="meta"><span class="tag">{d["topic"]}</span><span class="src">{b["src"]}</span></div><h3>{d["title"]}</h3><p>{d["sum"]}</p><span class="go">{c.t(("Read →","اقرأ ←"))}</span></a>'
    days=[]
    for b in BRIEFS:
        if not days or days[-1][0]!=b['date']: days.append((b['date'],[]))
        days[-1][1].append(b)
    days_html=''.join(f'<div class="day"><h2>{dlong(c,dt)}</h2><div class="cards">{"".join(card(b) for b in bs)}</div></div>' for dt,bs in days)
    fb=f'<button type="button" data-t="all" aria-pressed="true">{c.t(("All","الكل"))}</button>'+''.join(f'<button type="button" data-t="{k}" aria-pressed="false">{c.t(v)}</button>' for k,v in topic_k.items())
    body=f'''<div class="wrap">{crumbs_html(c,items)}<div class="ix-head">
<p class="eyebrow">{c.t(('Laprocx Daily Brief','الموجز اليومي من لابروكس'))}</p><h1>{c.t(('What you need to know today','ما الذي تحتاج معرفته اليوم'))}</h1>
<p>{c.t(('Short updates every working day on UAE visas, business rules and fees. Each one tells you what it is, who it affects and what to do, with a link to the official source.','موجزات قصيرة كل يوم عمل عن الإقامات والأعمال والرسوم في الإمارات. كل موجز يذكر ما الموضوع، ومن يتأثر، وماذا تفعل، مع رابط المصدر الرسمي.'))}</p>
<div class="filters" role="group" aria-label="{c.t(('Topic','الموضوع'))}">{fb}</div></div>
{days_html}</div>'''
    write_page(c, c.t(('Laprocx Daily Brief: UAE Visa and Business Updates','الموجز اليومي من لابروكس: تحديثات الإقامات والأعمال في الإمارات')),
      c.t(('Short daily updates on UAE visas, business rules and fees, with what to do and a link to the official source.','تحديثات يومية قصيرة عن الإقامات وقواعد الأعمال والرسوم في الإمارات، مع ما يجب فعله ورابط المصدر الرسمي.')), body,
      [crumbs_schema(c,items),{"@context":"https://schema.org","@type":"Blog","name":"Laprocx Daily Brief","url":BASE+c.here(),"inLanguage":c.lang}])

# ---------------------------------------------------------------- home
CARD_SLUG = {s['name'][0]: s['slug'] for s in SERVICES}
def home(c):
    soup = BeautifulSoup(open(HOME_SRC).read(), 'lxml')
    main = soup.find('main')
    for el in main.select('[data-ar]'):
        if c.ar:
            frag = BeautifulSoup(el['data-ar'], 'html.parser')
            el.clear()
            nodes = list(frag.contents)
            for n in nodes: el.append(n)
        del el['data-ar']
    for el in main.select('[data-ar-placeholder]'):
        if c.ar: el['placeholder'] = el['data-ar-placeholder']
        del el['data-ar-placeholder']
    for a in main.find_all('a', href=True):
        h = a['href']
        if h.startswith('brief-') and h.endswith('.html'):
            a['href'] = c.url(BRIEF_PATH[h[:-5]])
        elif h == 'brief.html': a['href'] = c.url('/brief/')
        elif h == '#plans': a['href'] = c.url('/pro-plans/')
        elif h.startswith('https://wa.me'): pass
    for a in main.select('a.svc'):
        en = a.get('data-en-name')
        if en and en in CARD_SLUG: a['href'] = c.url(CARD_SLUG[en])
        del a['data-en-name']
    for a in main.select('a[data-href]'):
        a['href'] = c.url(a['data-href']); del a['data-href']
    # Daily Brief section: newest brief big, next two beside it
    top=BRIEFS[0]; d=brief_dict(top,c)
    first_dd=lambda h: BeautifulSoup(h,'html.parser').get_text(' ',strip=True)
    today_html=f'''<article class="today"><div class="meta"><time datetime="{top['date']}">{dmeta(c,top['date'])}</time><span class="src">{top['src']}</span><span>{c.t(('1 min read','قراءة دقيقة واحدة'))}</span></div>
<h3><a href="{c.url(bpath(top))}" style="text-decoration:none">{d['title']}</a></h3>
<dl><div><dt>{c.t(('What it is','ما الموضوع'))}</dt><dd>{d['sum']}</dd></div><div><dt>{c.t(('Who it affects','من يتأثر'))}</dt><dd>{first_dd(d['who'])}</dd></div></dl>
<a class="more" href="{c.url(bpath(top))}">{c.t(('Read the full brief →','اقرأ الموجز كاملاً ←'))}</a></article>'''
    old_today=main.select_one('article.today')
    if old_today: old_today.replace_with(BeautifulSoup(today_html,'html.parser'))
    past=main.select_one('div.past')
    if past:
        for a in past.find_all('a', recursive=False):
            if 'btn' not in (a.get('class') or []): a.decompose()
        ins=''
        for b in BRIEFS[1:3]:
            dd=__import__('datetime').date.fromisoformat(b['date'])
            mon=c.t((dd.strftime('%b'), ['ينا','فبر','مار','أبر','مايو','يون','يول','أغس','سبت','أكت','نوف','ديس'][dd.month-1]))
            day=f"{dd.day:02d}".translate(_AR_DIG) if c.ar else f"{dd.day:02d}"
            ins+=f'<a href="{c.url(bpath(b))}"><span class="d"><b>{day}</b><span>{mon}</span></span><span><h4>{c.t((b["title_en"],b["title_ar"]))}</h4><small>{c.t((b["topic_en"],b["topic_ar"]))} · {b["src"]}</small></span></a>'
        frag=BeautifulSoup(ins,'html.parser')
        for n in reversed(list(frag.contents)): past.insert(0,n)
    body = ''.join(str(x) for x in main.contents)
    ld = {"@context":"https://schema.org","@type":"ProfessionalService","name":"Laprocx Business Services","alternateName":"لابروكس لخدمات الأعمال",
          "url":BASE+'/',"logo":BASE+"/assets/app-icon-512.png","image":BASE+"/assets/og-image.png","telephone":PHONE,"email":EMAIL,
          "description":c.t(('Company setup, PRO services and visas for UAE businesses and professionals.','تأسيس الشركات وخدمات المندوب والإقامات للشركات والمهنيين في الإمارات.')),
          "areaServed":{"@type":"Country","name":"United Arab Emirates"},"knowsLanguage":["en","ar"],
          "openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"09:00","closes":"22:00"}]}
    site = {"@context":"https://schema.org","@type":"WebSite","name":"Laprocx Business Services","url":BASE+'/',"inLanguage":["en","ar"]}
    write_page(c, c.t(('Laprocx Business Services | Company Setup, PRO and Visas in the UAE','لابروكس لخدمات الأعمال | تأسيس الشركات وخدمات المندوب والإقامات في الإمارات')),
      c.t(('Company setup, PRO services and Golden, Freelance and Investor visas, plus typing, attestation and travel. Send documents online and track every step.','تأسيس الشركات وخدمات المندوب والإقامات الذهبية والعمل الحر والمستثمر، مع الطباعة والتصديق والسفر. أرسل مستنداتك أونلاين وتابع كل خطوة.')),
      body, [ld, site])

def notfound(c):
    body=f'''<div class="wrap notfound"><h1>{c.t(('This page is not here','هذه الصفحة غير موجودة'))}</h1><p class="lede" style="margin:0 auto 1.6rem;color:var(--slate)">{c.t(('The link may be old. Try the services list or ask us on WhatsApp.','قد يكون الرابط قديماً. جرّب قائمة الخدمات أو اسألنا على واتساب.'))}</p>
<div style="display:flex;gap:.7rem;justify-content:center;flex-wrap:wrap"><a class="btn btn-gold" href="{c.url('/services/')}">{c.t(('See all services','كل الخدمات'))}</a>{wa_btn(c,('Ask on WhatsApp','اسأل على واتساب'))}</div></div>'''
    write_page(c, c.t(('Page not found','الصفحة غير موجودة')), c.t(('Page not found','الصفحة غير موجودة')), body, noindex=True, has_ar=False)

# ---------------------------------------------------------------- build
def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'assets'))
    for f in os.listdir(BRAND): shutil.copy(os.path.join(BRAND, f), os.path.join(OUT, 'assets', f))
    css = open(os.path.join(HERE,'site.css')).read() + open(os.path.join(HERE,'extra.css')).read()
    css = css.replace('url("assets/', 'url("').replace('url("/assets/', 'url("')
    open(os.path.join(OUT,'assets','site.css'),'w').write(css)
    shutil.copy(os.path.join(HERE,'site.js'), os.path.join(OUT,'assets','site.js'))
    for lang in ('en','ar'):
        home(Ctx('/',lang)); services_index(Ctx('/services/',lang)); pro_plans(Ctx('/pro-plans/',lang))
        estimate(Ctx('/estimate/',lang)); about(Ctx('/about/',lang)); contact(Ctx('/contact/',lang))
        legal(Ctx('/privacy/',lang),'/privacy/',('Privacy policy','سياسة الخصوصية'),PRIVACY)
        legal(Ctx('/terms/',lang),'/terms/',('Terms of service','شروط الخدمة'),TERMS)
        for s in SERVICES: service_page(Ctx(s['slug'],lang), s)
        brief_index(Ctx('/brief/',lang))
        for b in BRIEFS: brief_page(Ctx(bpath(b),lang), b)
    notfound(Ctx('/404/','en'))
    # sitemap + robots + manifest
    urls=[]
    for p,lang,noi in PAGES:
        if noi or lang!='en': continue
        urls.append(f'<url><loc>{BASE}{p}</loc><lastmod>2026-11-09</lastmod><xhtml:link rel="alternate" hreflang="en" href="{BASE}{p}"/><xhtml:link rel="alternate" hreflang="ar" href="{BASE}/ar{p}"/></url>'
                    f'<url><loc>{BASE}/ar{p}</loc><lastmod>2026-11-09</lastmod><xhtml:link rel="alternate" hreflang="en" href="{BASE}{p}"/><xhtml:link rel="alternate" hreflang="ar" href="{BASE}/ar{p}"/></url>')
    open(os.path.join(OUT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+'\n'.join(urls)+'\n</urlset>\n')
    shutil.copy(os.path.join(BRAND,'favicon.ico'), os.path.join(OUT,'favicon.ico')); shutil.copy(os.path.join(BRAND,'app-icon-192.png'), os.path.join(OUT,'favicon-192.png'))
    open(os.path.join(OUT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    open(os.path.join(OUT,'assets','site.webmanifest'),'w').write(json.dumps({"name":"Laprocx Business Services","short_name":"Laprocx","icons":[{"src":"/assets/app-icon-192.png","sizes":"192x192","type":"image/png"},{"src":"/assets/app-icon-512.png","sizes":"512x512","type":"image/png"}],"theme_color":"#0B4F45","background_color":"#F3F7F5","display":"browser"}))
    print(len(PAGES),'pages ->',OUT)

build()
