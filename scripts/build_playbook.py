"""Build the single-source RFQ launch playbook as printable PDF and web HTML."""
import hashlib
from html import escape
import json
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from project import ROOT, RFQ

source = RFQ / 'LAUNCH-PLAYBOOK.md'
inputs = [source, RFQ / 'quote-comparison.csv', ROOT / 'scripts/build_playbook.py']
frozen = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
pdfmetrics.registerFont(TTFont('Playbook', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('PlaybookBold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
styles = getSampleStyleSheet()
for style in styles.byName.values(): style.fontName = 'Playbook'
styles['BodyText'].fontSize = 9
styles['BodyText'].leading = 13
styles.add(ParagraphStyle(name='Cell', fontName='Playbook', fontSize=7, leading=10))
flow, web = [], []


def inline(text, pdf=False):
    text = escape(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'\1' if pdf else r'<code>\1</code>', text)
    if pdf:
        return re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<link href="\2" color="#1e5d50">\1</link>', text)
    return re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)


def paragraph(lines):
    if not lines: return
    text = ' '.join(line.removeprefix('> ').strip() for line in lines)
    flow.append(Paragraph(inline(text, True), styles['BodyText']))
    flow.append(Spacer(1, 6))
    web.append('<p>' + inline(text) + '</p>')


def table(lines):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if all(re.fullmatch(r'[-: ]+', cell) for cell in cells): continue
        rows.append(cells)
    widths = [519 / len(rows[0])] * len(rows[0])
    display = Table([[Paragraph(inline(cell, True), styles['Cell']) for cell in row] for row in rows], colWidths=widths, repeatRows=1)
    display.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce9df')),
        ('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#becdc5')), ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    flow.extend([display, Spacer(1, 10)])
    web.append('<div class="table"><table>' + ''.join('<tr>' + ''.join(('<th>' if i == 0 else '<td>') + inline(cell) + ('</th>' if i == 0 else '</td>') for cell in row) + '</tr>' for i,row in enumerate(rows)) + '</table></div>')


pending, tabular = [], []
for line in source.read_text().splitlines() + ['']:
    if line=='>' or line.startswith('> '): line=line[1:].lstrip()
    if line.startswith('|'):
        paragraph(pending); pending=[]; tabular.append(line); continue
    if tabular: table(tabular); tabular=[]
    if line.startswith('#'):
        paragraph(pending); pending=[]
        level = min(3, len(line) - len(line.lstrip('#')))
        text = line.lstrip('# ')
        flow.append(Paragraph(inline(text, True), styles['Title' if level == 1 else 'Heading2']))
        web.append(f'<h{level}>' + inline(text) + f'</h{level}>')
    elif not line.strip():
        paragraph(pending); pending=[]
    elif re.match(r'^(?:- |\d+\. )', line):
        paragraph(pending); pending=[]; paragraph([line])
    else: pending.append(line)


def footer(canvas, document):
    canvas.setFont('Playbook', 7)
    canvas.drawString(38, 24, 'Galia · GALIA-EVT-001 · quotation only · physical validation pending')
    canvas.drawRightString(557, 24, str(document.page))


pdf = RFQ / 'rfq-launch-playbook.pdf'
SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=38, rightMargin=38, topMargin=35, bottomMargin=40,
    title='Galia RFQ launch playbook', author='Galia').build(flow, onFirstPage=footer, onLaterPages=footer)
html = RFQ / 'rfq-launch-playbook.html'
html.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Galia RFQ launch playbook</title><style>body{font:18px/1.6 system-ui;color:#193e36;background:#fffaf1;max-width:72rem;margin:2rem auto;padding:0 1.5rem}h1,h2{line-height:1.2}h2{margin-top:2.5rem}a{color:#165949}code{overflow-wrap:anywhere}.table{overflow:auto}table{border-collapse:collapse;background:white;width:100%;font-size:1rem}th,td{padding:.8rem;border-bottom:1px solid #becdc5;vertical-align:top;text-align:left}th{background:#dce9df}p{max-width:95ch}@media print{body{font-size:11pt;background:white}.table{overflow:visible}}</style><nav><a href="rfq-launch-playbook.pdf">Download the printable PDF</a> · <a href="quote-comparison.csv">Download the quote worksheet</a> · <a href="LAUNCH-PLAYBOOK.md">Editable source</a></nav>' + ''.join(web) + '</html>')
assert frozen == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
outputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (pdf,html)}
(RFQ / 'playbook-receipt.json').write_text(json.dumps({'sources':frozen,'outputs':outputs,'fabrication_release':False},indent=2)+'\n')
print('RFQ launch playbook PDF and HTML generated.')
