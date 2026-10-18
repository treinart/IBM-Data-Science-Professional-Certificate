/* Static, browser-only equivalent of spacex-dash-app.py.
   Same source CSV; same filtering, aggregation, chart titles, and Plotly chart semantics. */
'use strict';
const ALL_SITES = 'ALL';
const OUTCOME_COLORS = { Failure: '#c0392b', Success: '#1f8f4e' };
let launches = [];
let sites = [];
let categories = [];
let selectedSite = ALL_SITES;
const siteInput = document.querySelector('#site-dropdown');
const optionsEl = document.querySelector('#site-options');
const lowEl = document.querySelector('#payload-low');
const highEl = document.querySelector('#payload-high');
const lowValueEl = document.querySelector('#payload-low-value');
const highValueEl = document.querySelector('#payload-high-value');
const MAX_PAYLOAD = 10000;
const PAYLOAD_TICK_INTERVAL = 1000;
const fmt = n => n.toLocaleString('en-US');
const chartConfig = { responsive:true, displaylogo:false };

// CSV data does not contain quoted commas, but this parser supports standard CSV quoting.
function parseCSV(text) {
  const records=[]; let row=[], field='', quoted=false;
  for (let i=0;i<text.length;i++) {
    const ch=text[i];
    if (ch==='"') { if(quoted && text[i+1]==='"') {field+='"';i++;} else quoted=!quoted; }
    else if(ch===',' && !quoted) {row.push(field);field='';}
    else if((ch==='\n'||ch==='\r') && !quoted) {
      if(ch==='\r' && text[i+1]==='\n')i++;
      row.push(field); if(row.some(x=>x.length)) records.push(row); row=[];field='';
    } else field+=ch;
  }
  if(field.length||row.length) {row.push(field);records.push(row);}
  const headers=records.shift();
  return records.map(values=>Object.fromEntries(headers.map((h,i)=>[h,values[i]??''])));
}
function layout(title, extra={}) {
  return {
    title:{text:title,x:0.5,xanchor:'center'},
    margin:{l:50,r:30,t:70,b:50}, paper_bgcolor:'white',plot_bgcolor:'white',
    font:{family:'Arial, sans-serif'}, ...extra
  };
}
function renderPie() {
  let names, values, title, colors;
  if(selectedSite===ALL_SITES) {
    title='Total Successful Launches by Site';
    names=sites;
    values=sites.map(site=>launches.filter(row=>row.site===site).reduce((sum,row)=>sum+row.success,0));
    // Plotly Express's default qualitative color sequence and category order.
    colors=['#636efa','#ef553b','#00cc96','#ab63fa','#ffa15a','#19d3f3','#ff6692','#b6e880'];
  } else {
    title=`Launch Outcomes for ${selectedSite}`;
    names=['Success','Failure'];
    const selected=launches.filter(row=>row.site===selectedSite);
    const successes=selected.reduce((sum,row)=>sum+row.success,0);
    values=[successes,selected.length-successes];
    colors=[OUTCOME_COLORS.Success,OUTCOME_COLORS.Failure];
  }
  const trace={type:'pie',labels:names,values,marker:{colors:colors.slice(0,names.length)},
    textinfo:'percent',hovertemplate:'%{label}<br>%{value}<extra></extra>'};
  return Plotly.react('success-pie-chart',[trace],layout(title,{showlegend:true,
    legend:{title:{text:selectedSite===ALL_SITES?'Launch Site':'Launch Outcome'}}}),chartConfig);
}
function renderScatter() {
  const min=Number(lowEl.value), max=Number(highEl.value);
  const data=launches.filter(row=>(selectedSite===ALL_SITES||row.site===selectedSite)
    && row.mass>=min && row.mass<=max);
  const displaySite=selectedSite===ALL_SITES?'All Sites':selectedSite;
  const title=`Payload Mass and Launch Outcome for ${displaySite}`;
  // Plotly Express scatter groups by Booster Version Category and keeps its
  // sorted global category order even when a range has no observations.
  const colorway=['#636efa','#ef553b','#00cc96','#ab63fa','#ffa15a','#19d3f3','#ff6692','#b6e880'];
  const traces=categories.filter(category=>data.some(row=>row.category===category)).map(category=>{
    const rows=data.filter(row=>row.category===category);
    return {type:'scatter',mode:'markers',name:category,
      x:rows.map(row=>row.mass),y:rows.map(row=>row.success),
      customdata:rows.map(row=>[row.site,row.booster]),
      marker:{size:10,opacity:0.8,color:colorway[categories.indexOf(category)%colorway.length]},
      hovertemplate:'Payload Mass (kg)=%{x}<br>Launch Outcome=%{y}<br>Launch Site=%{customdata[0]}<br>Booster Version=%{customdata[1]}<br>Booster Version Category='+category+'<extra></extra>'};
  });
  return Plotly.react('success-payload-scatter-chart',traces,layout(title,{
    xaxis:{title:{text:'Payload Mass (kg)'},showgrid:true,gridcolor:'#e2e8f0',zeroline:true},
    yaxis:{title:{text:'Launch Outcome'},tickmode:'array',tickvals:[0,1],ticktext:['Failure','Success'],range:[-0.15,1.15]},
    legend:{title:{text:'Booster Version Category'}},showlegend:true
  }),chartConfig);
}
function renderOptions(search='') {
  optionsEl.replaceChildren();
  const all=[{label:'All Sites',value:ALL_SITES},...sites.map(s=>({label:s,value:s}))];
  const matches=all.filter(o=>o.label.toLowerCase().includes(search.toLowerCase()));
  for(const entry of matches) {
    const button=document.createElement('button');
    button.className='site-option';button.type='button';button.role='option';
    button.textContent=entry.label;button.dataset.value=entry.value;
    button.setAttribute('aria-selected',String(entry.value===selectedSite));
    button.addEventListener('mousedown',event=>event.preventDefault());
    button.addEventListener('click',()=>chooseSite(entry.value));
    optionsEl.append(button);
  }
}
function openOptions(search='') {renderOptions(search);optionsEl.hidden=false;siteInput.setAttribute('aria-expanded','true');}
function closeOptions() {optionsEl.hidden=true;siteInput.setAttribute('aria-expanded','false');}
function chooseSite(value) {
  selectedSite=value;
  siteInput.value=value===ALL_SITES?'All Sites':value;
  closeOptions();renderPie();renderScatter();
}
siteInput.addEventListener('focus',()=>openOptions(''));
siteInput.addEventListener('input',()=>openOptions(siteInput.value));
siteInput.addEventListener('keydown',event=>{
  if(event.key==='Escape'){closeOptions();siteInput.value=selectedSite===ALL_SITES?'All Sites':selectedSite;siteInput.blur();}
  if(event.key==='Enter') {const option=optionsEl.querySelector('.site-option');if(option)chooseSite(option.dataset.value);}
  if(event.key==='ArrowDown'&&!optionsEl.hidden){event.preventDefault();optionsEl.querySelector('.site-option')?.focus();}
});
optionsEl.addEventListener('keydown',event=>{
  if(event.key==='ArrowDown'||event.key==='ArrowUp') {
    event.preventDefault();const elements=[...optionsEl.querySelectorAll('.site-option')];
    const i=elements.indexOf(document.activeElement);
    elements[Math.max(0,Math.min(elements.length-1,i+(event.key==='ArrowDown'?1:-1)))]?.focus();
  }
  if(event.key==='Escape'){closeOptions();siteInput.focus();}
});
document.querySelector('#site-arrow').addEventListener('click',()=>{
  if(optionsEl.hidden){siteInput.focus();openOptions('');}else {closeOptions();siteInput.blur();}
});
document.addEventListener('click',event=>{if(!document.querySelector('#select-wrap').contains(event.target)){
  closeOptions();siteInput.value=selectedSite===ALL_SITES?'All Sites':selectedSite;
}});
function refreshSlider() {
  const low=Number(lowEl.value),high=Number(highEl.value);
  document.querySelector('#slider-fill').style.left=`${100*low/MAX_PAYLOAD}%`;
  document.querySelector('#slider-fill').style.right=`${100*(MAX_PAYLOAD-high)/MAX_PAYLOAD}%`;
  lowValueEl.value=String(low);
  highValueEl.value=String(high);
  lowEl.title=`${fmt(low)} kg`;highEl.title=`${fmt(high)} kg`;
}
lowEl.addEventListener('input',()=>{
  if(+lowEl.value>+highEl.value)lowEl.value=highEl.value;
  refreshSlider();renderScatter();
});
highEl.addEventListener('input',()=>{
  if(+highEl.value<+lowEl.value)highEl.value=lowEl.value;
  refreshSlider();renderScatter();
});
function commitPayloadValue(field, slider, otherSlider, isLower) {
  const entered=Number(field.value);
  if(field.value.trim()==='' || !Number.isFinite(entered)) {
    refreshSlider();
    return;
  }
  const bounded=Math.max(0,Math.min(MAX_PAYLOAD,entered));
  slider.value=String(isLower ? Math.min(bounded,Number(otherSlider.value))
    : Math.max(bounded,Number(otherSlider.value)));
  refreshSlider();
  renderScatter();
}
lowValueEl.addEventListener('change',()=>commitPayloadValue(lowValueEl,lowEl,highEl,true));
highValueEl.addEventListener('change',()=>commitPayloadValue(highValueEl,highEl,lowEl,false));
for(const field of [lowValueEl,highValueEl]) {
  field.addEventListener('keydown',event=>{if(event.key==='Enter')field.blur();});
}
async function main() {
  try {
    if(typeof Plotly==='undefined') throw new Error('Plotly could not load. Check the internet connection.');
    const response=await fetch('./spacex_launch_dash.csv');
    if(!response.ok) throw new Error(`Unable to load CSV (${response.status})`);
    const raw=parseCSV(await response.text());
    for(const required of ['Launch Site','class','Payload Mass (kg)','Booster Version Category']) {
      if(raw.length===0 || !(required in raw[0]))throw new Error(`Missing required dataset column: ${required}`);
    }
    launches=raw.map(row=>({site:row['Launch Site'],success:Number(row.class),mass:Number(row['Payload Mass (kg)']),
      booster:row['Booster Version'],category:row['Booster Version Category']}));
    if(launches.some(r=>!r.site||!r.category||!Number.isFinite(r.mass)||![0,1].includes(r.success)))
      throw new Error('Invalid or missing launch data in the CSV');
    sites=[...new Set(launches.map(r=>r.site))].sort();
    categories=[...new Set(launches.map(r=>r.category))].sort();
    const ticks=document.querySelector('#slider-ticks');
    for(let n=0;n<=MAX_PAYLOAD;n+=PAYLOAD_TICK_INTERVAL) {const el=document.createElement('span');el.textContent=fmt(n);ticks.append(el);}
    refreshSlider();await Promise.all([renderPie(),renderScatter()]);
  } catch(error) {
    const el=document.querySelector('#error-message');el.hidden=false;el.textContent=`Dashboard error: ${error.message}`;
    console.error(error);
  }
}
main();
