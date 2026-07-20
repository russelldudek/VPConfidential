from pathlib import Path
import zlib, textwrap, re

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'; DOCS.mkdir(exist_ok=True)
W,H=612,792
INK=(7/255,16/255,21/255); PAPER=(246/255,242/255,230/255); AMBER=(1,176/255,0); TEAL=(69/255,208/255,199/255); MUTED=(93/255,110/255,121/255)
LIVE='https://russelldudek.github.io/VPConfidential/'

def clean(s):
    return s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–','-').replace('—','-').replace('•','-')

def esc(s):
    s=clean(s)
    return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)').replace('\r',' ').replace('\n',' ')

def wrap(s, width):
    s=clean(s)
    return textwrap.wrap(s, width=width, break_long_words=False, break_on_hyphens=False) or ['']

def rgb(c): return ' '.join(f'{v:.3f}' for v in c)

def page_stream(page, pno, total, doc_label):
    out=[]
    def rect(x,y,w,h,c): out.append(f'q {rgb(c)} rg {x} {y} {w} {h} re f Q')
    def line(x1,y1,x2,y2,c,w=1): out.append(f'q {rgb(c)} RG {w} w {x1} {y1} m {x2} {y2} l S Q')
    def txt(x,y,s,size=9,bold=False,c=INK):
        out.append(f'BT {rgb(c)} rg /F{2 if bold else 1} {size} Tf 1 0 0 1 {x} {y} Tm ({esc(s)}) Tj ET')
    def para(x,y,s,size=8.2,lead=11,maxchars=98,bold=False,c=INK):
        for ln in wrap(s,maxchars): txt(x,y,ln,size,bold,c); y-=lead
        return y
    rect(0,0,W,H,(1,1,1))
    rect(0,H-104,W,104,INK)
    rect(0,H-8,W,8,AMBER)
    txt(40,H-32,page.get('kicker',doc_label).upper(),7.2,True,TEAL)
    title=page['title']; ts=22 if len(title)<45 else 17
    txt(40,H-61,title,ts,True,(1,1,1))
    y=H-82
    if page.get('subtitle'):
        for ln in wrap(page['subtitle'],95): txt(40,y,ln,8,False,(.78,.84,.86)); y-=10
    y=H-130
    for sec in page['sections']:
        label=sec.get('label')
        if label:
            txt(40,y,label.upper(),7.2,True,(.45,.32,0)); line(40,y-5,572,y-5,(.82,.78,.68),.6); y-=22
        if 'p' in sec:
            y=para(40,y,sec['p'],8.4,11,104); y-=9
        for h,b in sec.get('items',[]):
            rect(40,y-2,4,4,AMBER)
            txt(52,y,h,8.6,True,INK); y-=12
            y=para(52,y,b,7.9,10,96,c=MUTED); y-=7
        for b in sec.get('bullets',[]):
            rect(42,y+2,3,3,TEAL); y=para(52,y,b,8.1,10.5,96); y-=4
        if 'quote' in sec:
            rect(40,y-84,532,84,PAPER); line(40,y,40,y-84,AMBER,4)
            yq=y-20
            for ln in wrap(sec['quote'],92): txt(56,yq,ln,8.4,False,INK); yq-=11
            y-=96
        if y<60: break
    line(40,30,572,30,(.82,.78,.68),.6)
    txt(40,16,doc_label.upper(),6.2,True,MUTED)
    txt(505,16,f'{pno} / {total}',6.2,True,MUTED)
    return '\n'.join(out).encode('latin-1')

def write_pdf(path,title,subject,pages,label):
    n=len(pages); objs=[]
    # reserve catalog/pages/fonts/info + page/content pairs
    catalog=1; pages_obj=2; font1=3; font2=4; info=5
    page_ids=[]
    nextid=6
    streams=[]
    for i,p in enumerate(pages,1):
        pid=nextid; cid=nextid+1; nextid+=2; page_ids.append(pid)
        data=zlib.compress(page_stream(p,i,n,label),9); streams.append((cid,data))
    objs_map={}
    objs_map[catalog]=b'<< /Type /Catalog /Pages 2 0 R /PageMode /UseNone >>'
    kids=' '.join(f'{x} 0 R' for x in page_ids)
    objs_map[pages_obj]=f'<< /Type /Pages /Count {n} /Kids [ {kids} ] >>'.encode()
    objs_map[font1]=b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>'
    objs_map[font2]=b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>'
    objs_map[info]=f'<< /Title ({esc(title)}) /Author (Russell Dudek) /Subject ({esc(subject)}) /Creator (Independent candidate campaign) >>'.encode('latin-1')
    for idx,pid in enumerate(page_ids):
        cid=pid+1
        objs_map[pid]=f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W} {H}] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {cid} 0 R >>'.encode()
    for cid,data in streams:
        objs_map[cid]=b'<< /Length '+str(len(data)).encode()+b' /Filter /FlateDecode >>\nstream\n'+data+b'\nendstream'
    maxid=max(objs_map)
    out=bytearray(b'%PDF-1.4\n%RDCC\n')
    offsets=[0]*(maxid+1)
    for i in range(1,maxid+1):
        offsets[i]=len(out); out+=f'{i} 0 obj\n'.encode()+objs_map[i]+b'\nendobj\n'
    xref=len(out); out+=f'xref\n0 {maxid+1}\n'.encode()+b'0000000000 65535 f \n'
    for i in range(1,maxid+1): out+=f'{offsets[i]:010d} 00000 n \n'.encode()
    out+=f'trailer\n<< /Size {maxid+1} /Root 1 0 R /Info 5 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    path.write_bytes(out)

resume=[
{'kicker':'Role-aligned resume','title':'Russell Dudek','subtitle':'Manufacturing Strategy & Operations Executive | Confidential Organization','sections':[
 {'label':'Executive profile','p':'Operator-technologist who makes complex manufacturing work visible, connects technical and business teams, and builds operating mechanisms that turn emerging technology into adopted, measurable outcomes.'},
 {'label':'Role-aligned capabilities','bullets':['Global manufacturing strategy; safety, quality, delivery, cost and customer promise.','Advanced electronics and high-reliability operations.','Capacity, constraints, capital, make-buy and technology-transfer logic.','Lean, Gemba, standard work, root cause and continuous improvement.','Digital operations, robotics, machine vision, telemetry, ERP and AI-assisted workflows.']},
 {'label':'Selected experience','items':[
 ('Vape-Jet | Director of Operations | 2025-Present','Leads AI-first operating transformation across production, purchasing, quality, customer success, support, engineering issue flow, ERP/Odoo, Jira, HubSpot, Slack, telemetry and AI-assisted workflows. Connects factory, field, customer and machine-fleet signals into prioritized work. Operates in a robotics and machine-vision environment with approximately 1,000 fielded robots.'),
 ('Compunetics | Director of Operations and Engineering Management | 2000-2013','Progressed through R&D program management, production management, strategic acquisition, operations management and director-level leadership. Led engineering, manufacturing, quality, customer delivery and complex technical programs in advanced electronics and high-reliability environments. Built quality systems, standard work, root-cause practices, performance measures and process controls.')]}]},
{'kicker':'Role-aligned resume','title':'Russell Dudek | Evidence Continuity','subtitle':'Advanced manufacturing, distributed operations, technical translation and leadership systems','sections':[
 {'label':'Selected experience continued','items':[
 ('Amazon | Operations Management / Site Leader | 2014-2018','Led launch and execution for Amazon Prime Pittsburgh in a 24/7 customer-backward environment supporting approximately five million second-day orders annually. Built leadership routines, labor planning, throughput visibility, escalation paths, standard work and operating mechanisms across safety, quality, throughput, customer experience and team engagement.'),
 ('ZeusVu | Founder / Operator','Led regulated autonomous drone operations across medical, energy, logistics and restricted-airspace use cases with a verified 100% safety record and no FAA incidents.'),
 ('Technical foundation','B.S., University of Pittsburgh. Materials science and physical chemistry grounding. Published industry articles, delivered technical talks, participated in the HyperTransport Consortium, and translated novel materials and high-speed electronics concepts for partners including Intel and AMD.') ]},
 {'label':'Leadership thesis','p':'Standardize the operating contract. Differentiate the technical capability. One enterprise cadence for customer promise, capacity, capital, escalation and learning - without erasing legitimate local process knowledge.'},
 {'label':'First 120 days','bullets':['0-30: Read the promise and earn site-leader trust.','31-60: Make the network shape, constraints and decision rights visible.','61-90: Prove one consequential capacity, NPI, footprint, make-buy or transfer decision.','91-120: Commit a sequenced manufacturing portfolio and leadership operating calendar.']},
 {'label':'Contact','p':'Pittsburgh, Pennsylvania | 412.287.8640 | russelldudek@gmail.com | linkedin.com/in/russelldudek | '+LIVE}]}]
cover=[{'kicker':'Cover letter','title':'Change the shape. Hold the promise.','subtitle':'Vice President, Global Manufacturing Strategy | Confidential Organization','sections':[
 {'p':'Hiring Committee,'},
 {'p':'The mandate behind this role is not simply to run plants. It is to make a technically diverse global manufacturing network behave like one enterprise system: scalable enough for growth, disciplined enough for margin, capable enough for technology transition, and reliable enough to protect every customer commitment.'},
 {'p':'My career has been built at the intersection of technical manufacturing, quality, distributed operations, customer promise and emerging technology. At Compunetics, I progressed through R&D, production, strategic acquisition, operations and director-level leadership in advanced electronics and high-reliability environments. At Amazon, I led 24/7 launch and execution supporting approximately five million second-day orders annually. At Vape-Jet, I now connect production, quality, purchasing, engineering, customer, support, telemetry, ERP and AI-assisted workflows in a robotics and machine-vision business.'},
 {'p':'My candidate thesis is direct: standardize the operating contract; differentiate the technical capability. The enterprise should share one language for safety, quality, delivery, cost, capacity, capital, escalation and learning. Sites should retain the process knowledge and judgment that create real customer value.'},
 {'p':'I have not claimed a verified five-year record as a global manufacturing VP. I would ask you to evaluate the transferability of the operating mechanisms I have built and the rigor of my entry plan. I would begin by learning the network with site leaders, clarifying decision rights, and proving one consequential capacity, NPI, footprint, make-buy or technology-transfer decision before scaling broader change.'},
 {'p':'The independent candidate vision at '+LIVE+' includes the Manufacturing Shape Contract, executive scorecard, interview thesis, hard-objection analysis and first-120-day plan.'},
 {'p':'Carpe diem,\nRussell Dudek'}]}]
brief=[
{'kicker':'Interview thesis brief','title':'Change the shape. Hold the promise.','subtitle':'The real mandate and candidate thesis','sections':[
 {'label':'Actual mandate','p':'Turn a diverse manufacturing footprint into one enterprise system that can scale capacity, improve economics, support NPI and technology transitions, and protect customer commitments without erasing legitimate local technical capability.'},
 {'label':'White-space thesis','p':'Standardize the operating contract. Differentiate the technical capability. Define the customer promise, capability map, capacity logic and control system so the network can change shape with evidence.'},
 {'label':'Four layers','items':[('Promise','Safety, quality, delivery, reliability, customer recovery and economic non-negotiables.'),('Capability','Process knowledge, technology, utilities, suppliers, talent and legitimate site differentiation.'),('Capacity','Demand, bottlenecks, utilization, alternatives, make-buy, capital, timing and resilience.'),('Control','Decision rights, cadence, escalation, metrics, confidence, learning and leadership bench.')]},
 {'label':'Cost of inaction','p':'Growth without shared decision architecture can amplify local optimization, capital delay, transfer risk, recurring quality loss, brittle capacity and leadership overload.'}]},
{'kicker':'Interview thesis brief','title':'The operating tensions','subtitle':'Manage contradictions rather than choosing one side permanently','sections':[
 {'items':[('Global standards / local judgment','Standardize performance language and decisions; preserve process knowledge closest to the work.'),('Delivery now / capacity later','Protect current commitments while building options for future demand and product transitions.'),('Utilization / resilience','Use asset economics without making the network brittle.'),('NPI speed / process stability','Move technology when capability, quality, training and recovery evidence are explicit.'),('Automation / adoption','Attach digital investments to changed work, human authority, training and results.'),('Enterprise ambition / site capacity','Sequence change so leaders and teams can absorb it without degrading execution.')]},
 {'label':'Decision rights','bullets':['Enterprise: portfolio, standards, capital logic and cross-site tradeoffs.','Site: execution, containment, local process control and daily management.','Joint: customer risk, capability evidence, transfer readiness, alternatives and closure.']}]},
{'kicker':'Interview thesis brief','title':'Why Russell’s evidence transfers','subtitle':'Direct and adjacent proof without title inflation','sections':[
 {'items':[('Advanced electronics manufacturing','Thirteen years across R&D, production, strategic acquisition, operations and director-level leadership at Compunetics.'),('High-consequence quality','Engineering, manufacturing, quality, customer delivery, root cause, standard work, performance measures and process controls.'),('Distributed customer promise','Amazon Prime Pittsburgh launch and 24/7 execution supporting approximately five million second-day orders annually.'),('Robotics and digital operations','Current transformation across production, quality, purchasing, support, engineering issue flow, ERP, telemetry and AI-assisted workflows.'),('Regulated autonomous systems','Drone operations with a verified 100% safety record and no FAA incidents.'),('Technical translation','Materials science and physical chemistry grounding, industry writing, talks and consortium participation.')]},
 {'label':'Strongest concern','p':'Adjacent scale is not identical to verified global VP tenure. Test transferability through operating evidence: map the system, establish trust with site leaders, clarify authority, and prove one consequential cross-site mechanism.'}]},
{'kicker':'Interview thesis brief','title':'Executive questions and first proof','subtitle':'Surface the real mandate; demonstrate a bounded operating mechanism','sections':[
 {'label':'Questions','bullets':['Where does the network most often break the customer promise?','Which site differences are strategic capabilities versus historical variation?','What capital or footprint decision must be made in the first year?','How are NPI readiness and technology transfer governed today?','Which metrics are trusted across every site, and which are debated?','Where is make-versus-buy logic driven by evidence versus precedent?','What leadership bench risk would concern the CEO most?','What must be measurably different twelve months after this hire?']},
 {'label':'First proof','p':'Run one real capacity, NPI, technology-transfer, footprint or make-buy question through the Manufacturing Shape Contract. Define the promise and constraints; map capability; compare capacity, capital, timing and partner options; clarify authority; document assumptions, risks, leading indicators and review date.'}]}]
plan=[
{'kicker':'First 120 days','title':'Earn the right to reshape the network.','subtitle':'Evidence-first entry sequence','sections':[
 {'label':'0-30 | Read the promise','items':[('Listen at the work','Visit or virtually observe representative sites; meet operators, technicians, engineers, quality leaders and site heads.'),('Map the customer promise','Identify critical products, service levels, reliability requirements, recovery commitments and customer concentration.'),('Baseline with confidence','Define safety, quality, delivery, cost, productivity, utilization, capacity, NPI and talent measures with source and confidence.'),('Protect continuity','Make no broad structural change before understanding current risk, authority and technical dependencies.')]},
 {'label':'Outputs','bullets':['Stakeholder and decision map.','Customer-promise and critical-capability map.','Top risk and constraint register.','Metric-definition and data-confidence record.']}]},
{'kicker':'First 120 days','title':'31-90 | Make the shape visible; prove the contract','subtitle':'Convert discovery into one shared decision mechanism','sections':[
 {'label':'31-60','items':[('Expose network shape','Map site roles, process capability, redundancy, single points, flex options and partner dependencies.'),('Clarify authority','Define enterprise, business, site, engineering, quality, finance and supply-chain decision rights.'),('Select the proof','Choose one real cross-site capacity, NPI, footprint, make-buy or transfer decision with sponsor and decision date.')]},
 {'label':'61-90','items':[('Run the proof','Apply the Manufacturing Shape Contract and document assumptions, alternatives, risks and confidence.'),('Establish cadence','Launch weekly promise-risk, monthly operating-economics and quarterly network-shape reviews.'),('Build adoption','Co-design with site leaders and train teams on decisions, not slide templates.'),('Stabilize now','Address a small number of visible safety, quality, delivery or constraint issues.')]},
 {'label':'Evidence','bullets':['One improved cross-site decision record.','Clear owners and escalation paths.','Site-leader pull for the mechanism.','Credible early execution wins.']}]},
{'kicker':'First 120 days','title':'91-120 | Commit the manufacturing portfolio','subtitle':'Sequence choices, capital, capability and leadership action','sections':[
 {'items':[('Protect','Strategic process capability, customer-critical capacity, safety and quality systems, technical centers and leadership depth.'),('Improve','Yield, uptime, labor productivity, flow, maintenance, quality loss, working capital and decision latency.'),('Flex / Partner','Qualified alternate capacity, make-buy boundaries, surge response, supplier and contract-manufacturing posture.'),('Expand / Stop','Sequenced capital, footprint changes, technology moves and sunset decisions with owners and review dates.')]},
 {'label':'Leadership outputs','bullets':['Weekly, monthly, quarterly and annual operating calendar tied to real decisions.','Leadership bench map: critical roles, successors, gaps, development and retention risk.','Prioritized capital portfolio with assumptions, alternatives, timing, risk and benefits.','Bounded transformation backlog by customer risk, economics, readiness and change burden.']},
 {'label':'Credible evidence by day 120','p':'Leaders describe the same priorities and decision rights; top customer, capacity, technical and leadership risks have owners; one consequential decision improved; metrics expose confidence; and the portfolio distinguishes what to protect, improve, flex, expand, partner or stop.'}]}]
hard=[
{'kicker':'Hard-objection analysis','title':'The question the campaign should not hide','subtitle':'Can adjacent scale translate into global multi-site executive leadership?','sections':[
 {'label':'What is verified','items':[('Senior manufacturing depth','Director-level engineering, manufacturing, quality and technical-program leadership in advanced electronics and high-reliability environments.'),('Distributed operating scale','24/7 Amazon launch and execution supporting approximately five million second-day orders annually.'),('Technology-rich operations','Current robotics, machine vision, telemetry, ERP, cross-functional issue flow and AI-assisted operating transformation.'),('Technical foundation','Materials science and physical chemistry grounding, industry writing, talks and consortium participation.')]},
 {'label':'What is not claimed','p':'Russell does not claim a verified record of five years as a VP directly owning a global multi-site manufacturing network. The candidacy should be judged on transferable operating judgment, technical credibility, mechanism building and a disciplined entry strategy - not title equivalence.'}]},
{'kicker':'Hard-objection analysis','title':'The affirmative answer','subtitle':'Make transferability observable and ramp risk bounded','sections':[
 {'items':[('Lead with the work','Frame the role around customer promise, capacity, technical capability, capital, cadence and leadership bench.'),('Use tactical empathy','Learn what variation is strategic before standardizing it.'),('Bound the ramp','Map the system, clarify decisions and prove one mechanism before broad change.'),('Invite a work sample','Walk through a real or anonymized capacity, NPI, footprint or make-buy decision.')]},
 {'label':'Interview language','quote':'I would not ask you to treat adjacent experience as identical experience. I would ask you to evaluate whether the operating mechanisms I have built across advanced electronics, high-reliability quality, 24/7 distributed execution, robotics, data and AI-assisted operations are the right foundation for the decisions this role must make.'},
 {'label':'Discovery questions','bullets':['Which first-year decision best reveals integrated technical, customer and financial judgment?','What site-leader behaviors distinguish useful standards from corporate overhead?','Where has manufacturing data failed to become a timely decision?','What would earn trust fastest with the current leadership team?']}]}]
review=[
{'kicker':'Executive operating artifact','title':'Manufacturing Shape Review','subtitle':'A recurring mechanism for promise, capability, capacity and control','sections':[
 {'items':[('1 | Promise','Which customer, safety, quality, delivery or recovery commitment is at risk or changing? Define non-negotiables.'),('2 | Capability','Which process knowledge, technology, site competency, supplier, utility or talent dependency matters? Protect real differentiation.'),('3 | Capacity','What constraint, utilization, demand, make-buy, capital and timing evidence changes the configuration? Compare options.'),('4 | Control','Who decides, who executes, what escalates, what is measured, and how does learning return? Make execution durable.')]},
 {'label':'Required record','bullets':['Decision, owner, scope, timing and review point.','Demand, capability, cost, timing, quality, resource and customer assumptions.','Alternatives: protect, improve, flex, expand, partner, transfer, consolidate or stop.','Baseline, units, source, freshness, uncertainty and missing proof.']}]},
{'kicker':'Executive operating artifact','title':'Scorecard and cadence','subtitle':'Define baselines, units, ownership and confidence before targets','sections':[
 {'label':'Balanced scorecard','items':[('Safety','Events, leading observations, corrective closure and process safety.'),('Quality','Escapes, yield, scrap, rework, capability and recurrence.'),('Delivery','Service, schedule, past due, recovery and constraints.'),('Cost / productivity','Conversion, labor, uptime, maintenance, inventory and losses.'),('Capacity','Rate, utilization, bottleneck, demand and flex.'),('NPI / technology','Readiness, capability, training, yield and ramp risk.'),('Leadership','Critical-role coverage, succession, skill depth and change load.')]},
 {'label':'Cadence','bullets':['Weekly: promise risk, containment, customer impact, owner and recovery date.','Monthly: operating economics, root cause, productivity, capacity, quality loss, cash and closure.','Quarterly: network shape, footprint, capital, make-buy, technology and leadership.','Annual: growth, portfolio, product roadmaps, risks, transitions and investment sequence.']}]}]

write_pdf(DOCS/'resume.pdf','Russell Dudek - Vice President Global Manufacturing Strategy Resume','Role-aligned resume',resume,'Role-aligned resume')
write_pdf(DOCS/'cover-letter.pdf','Russell Dudek - Cover Letter','Vice President Global Manufacturing Strategy cover letter',cover,'Cover letter')
write_pdf(DOCS/'interview-thesis-brief.pdf','Interview Thesis Brief','Interview Thesis Brief',brief,'Interview thesis brief')
write_pdf(DOCS/'120-day-entry-plan.pdf','120-Day Entry Plan','120-Day Entry Plan',plan,'120-day entry plan')
write_pdf(DOCS/'hard-objection-analysis.pdf','Hard-Objection Analysis','Hard-Objection Analysis',hard,'Hard-objection analysis')
write_pdf(DOCS/'manufacturing-shape-review.pdf','Manufacturing Shape Review','Manufacturing Shape Review',review,'Manufacturing Shape Review')
print('compact PDFs written')
