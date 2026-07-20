
const scenarios = {
  growth: {
    posture: 'Selective expansion',
    capacity: 'Stage capital behind validated constraint evidence.',
    footprint: 'Protect technical centers; add flex where demand is volatile.',
    control: 'One review cadence, differentiated process ownership.',
    leadership: 'Build successors around the capabilities that cannot fail.',
    positions: [
      [128,145,1,'hot'],[288,145,1,'hot'],[448,145,1,'flex'],[608,145,.88,'dim'],
      [128,265,1,''],[288,265,1,'hot'],[448,265,1,'flex'],[608,265,1,''],
      [128,385,.9,''],[288,385,.9,''],[448,385,.9,''],[608,385,.9,'']]
  },
  transition: {
    posture: 'Capability-led transfer',
    capacity: 'Sequence ramp behind process capability and yield evidence.',
    footprint: 'Pair the NPI cell with a scale cell before wider transfer.',
    control: 'Use explicit readiness gates, technical owners, and stop criteria.',
    leadership: 'Put process experts and site operators in one transfer team.',
    positions: [
      [112,145,.86,'dim'],[280,145,.86,''],[448,145,1.15,'hot'],[632,145,.76,'dim'],
      [112,272,.86,''],[280,272,1.08,'hot'],[448,272,1.08,'hot'],[632,272,.76,'dim'],
      [112,392,.86,''],[280,392,.86,'flex'],[448,392,.86,''],[632,392,.76,'dim']]
  },
  margin: {
    posture: 'Productivity before footprint',
    capacity: 'Attack yield, uptime, labor, and flow before adding assets.',
    footprint: 'Consolidate legitimate redundancy; preserve strategic capability.',
    control: 'Create common loss categories and an enterprise productivity review.',
    leadership: 'Make site leaders owners of economics, not only output.',
    positions: [
      [150,145,1,''],[310,145,1,'hot'],[470,145,.85,'dim'],[630,145,.65,'dim'],
      [150,265,1,'hot'],[310,265,1.15,'hot'],[490,265,.9,'flex'],[650,265,.55,'dim'],
      [150,385,1,''],[310,385,1,''],[470,385,.85,''],[630,385,.65,'dim']]
  },
  disruption: {
    posture: 'Protected continuity',
    capacity: 'Reserve qualified flex for the few flows that threaten customers.',
    footprint: 'Shift load through prequalified alternates; isolate the disrupted node.',
    control: 'Run a single incident cadence with explicit customer and recovery owners.',
    leadership: 'Place decision authority closest to verified technical and customer facts.',
    positions: [
      [118,145,1,'hot'],[285,145,.92,''],[452,145,.92,'flex'],[619,145,.92,'flex'],
      [118,270,.66,'risk'],[285,270,1.05,'hot'],[462,270,1.05,'flex'],[639,270,.78,''],
      [118,392,.9,''],[285,392,.9,'hot'],[452,392,.9,''],[619,392,.9,'flex']]
  }
};
function applyScenario(name){
  const data=scenarios[name];
  document.querySelectorAll('.scenario-button').forEach(b=>{const active=b.dataset.scenario===name;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
  document.querySelectorAll('.site').forEach((site,i)=>{
    const [x,y,s,c]=data.positions[i]; site.style.transform=`translate(${x}px, ${y}px) scale(${s})`; site.className=`site site-${i} ${c}`.trim();
  });
  document.getElementById('posture').textContent=data.posture;
  document.getElementById('capacity-move').textContent=data.capacity;
  document.getElementById('footprint-move').textContent=data.footprint;
  document.getElementById('control-move').textContent=data.control;
  document.getElementById('leadership-move').textContent=data.leadership;
}
const scenarioButtons=document.querySelectorAll('.scenario-button');
scenarioButtons.forEach(b=>b.addEventListener('click',()=>applyScenario(b.dataset.scenario)));
if(scenarioButtons.length) applyScenario('growth');
const toggle=document.querySelector('.nav-toggle'); const links=document.querySelector('.nav-links');
if(toggle&&links){toggle.addEventListener('click',()=>{const open=links.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));});}
