async function getJSON(url, options={}) {
  const r=await fetch(url,options);
  return r.json();
}
function status(stock,min){
  return stock<=min?'<span class="badge b-high">LOW</span>':'<span class="badge b-ok">GOOD</span>';
}
function riskClass(v){return v>=4?'high':v>=2?'med':'low'}

async function dashboard(){
 const d=await getJSON('/api/dashboard');
 const cards=[
  ['▣','Total SKUs',d.kpis.skus,'All Locations','c-blue'],
  ['▤','Total Inventory Value',d.kpis.value,'Across all DCs','c-green'],
  ['!','Low Stock Alerts',d.kpis.low_stock,'Requires attention','c-orange'],
  ['⌁','Demand Increase (7D)',d.kpis.demand_increase,'vs last 7 days','c-purple'],
  ['◷','Stock Near Expiry',d.kpis.expiry+' SKUs','In next 30 days','c-red']
 ];
 document.querySelector('#kpis').innerHTML=cards.map(c=>`<div class="kpi"><div class="ico ${c[4]}">${c[0]}</div><div><small>${c[1]}</small><b>${c[2]}</b><p>${c[3]}</p></div></div>`).join('');

 const rows=d.inventory;
 document.querySelector('#risk').innerHTML=`<table class="risk-table"><tr><th>DC</th><th>At Risk SKUs</th><th>Stock Status</th><th>Risk</th></tr>`+
 [...new Set(rows.map(x=>x.dc_name))].map(dc=>{
   const n=rows.filter(x=>x.dc_name===dc&&x.current_stock<=x.min_stock).length;
   const cls=riskClass(n);
   return `<tr><td>${dc}</td><td>${n}</td><td><div class="risk-bar"><span style="width:${Math.max(18,n*20)}%;background:${cls==='high'?'#ef3340':cls==='med'?'#f19a28':'#19a66d'}"></span></div></td><td class="${cls}">${cls.toUpperCase()}</td></tr>`
 }).join('')+'</table>';

 document.querySelector('#recs').innerHTML='<div class="rec-row"><b>Medicine</b><b>DC</b><b>Current</b><b>Replenish</b><b>Priority</b><b>Action</b></div>'+
 d.recs.map(x=>`<div class="rec-row"><div><b>${x.medicine}</b><div class="muted">${x.sku}</div></div><div class="muted">${x.dc_name}</div><div class="${x.current_stock<500?'redtxt':''}">${x.current_stock} Units</div><div class="redtxt">${x.recommended_qty} Units</div><div><span class="badge ${x.priority==='High'?'b-high':x.priority==='Medium'?'b-med':'b-low'}">${x.priority}</span></div><a class="btn" href="/replenishment">View Plan</a></div>`).join('');

 document.querySelector('#expiry').innerHTML='<table class="data-table"><tr><th>Medicine</th><th>Batch</th><th>Days</th><th>Qty</th><th>DC</th></tr>'+
 d.expiry.map(x=>`<tr><td>${x.medicine}</td><td>${x.batch_no}</td><td class="redtxt">${x.days_to_expiry}</td><td>${x.current_stock}</td><td>${x.dc_name}</td></tr>`).join('')+'</table>';

 document.querySelector('#alerts').innerHTML=d.alerts.map(x=>`<div class="alert-row"><div class="alert-icon ${x.type}">${x.type==='danger'?'!':x.type==='warning'?'▱':x.type==='success'?'✓':'i'}</div><div><b>${x.title}</b><small>${x.detail}</small></div><time>${x.time_text}</time></div>`).join('');

 const demand=(await getJSON('/api/demand')).filter(x=>x.medicine==='Paracetamol 500mg');
 new Chart(document.querySelector('#demandChart'),{type:'line',data:{labels:demand.map(x=>x.day),datasets:[
 {label:'Demand',data:demand.map(x=>x.actual),borderColor:'#315fe8',backgroundColor:'#315fe81a',fill:true,tension:.35,pointRadius:2},
 {label:'Forecast',data:demand.map(x=>x.forecast),borderColor:'#24a86c',borderDash:[5,4],tension:.35,pointRadius:2}
 ]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{font:{size:9}}}},scales:{x:{grid:{display:false},ticks:{font:{size:8}}},y:{ticks:{font:{size:8}}}}}});
 new Chart(document.querySelector('#signalChart'),{type:'doughnut',data:{labels:['Sales History','Current Orders','Seasonality','Promotions','Other Signals'],datasets:[{data:[45,25,15,10,5],backgroundColor:['#3564eb','#20a76d','#21a59a','#f2912c','#7546e9'],borderWidth:0}]},options:{cutout:'67%',plugins:{legend:{display:false}}}});
}

async function inventory(){
 const d=await getJSON('/api/inventory');
 document.querySelector('#inventory').innerHTML='<table class="data-table"><tr><th>Medicine</th><th>SKU</th><th>DC</th><th>Batch</th><th>Current Stock</th><th>Min Stock</th><th>Expiry</th><th>Status</th></tr>'+
 d.map(x=>`<tr><td><b>${x.medicine}</b></td><td>${x.sku}</td><td>${x.dc_name}</td><td>${x.batch_no}</td><td>${x.current_stock}</td><td>${x.min_stock}</td><td>${x.days_to_expiry} days</td><td>${status(x.current_stock,x.min_stock)}</td></tr>`).join('')+'</table>';
}
async function demand(){
 const d=(await getJSON('/api/demand')).filter(x=>x.medicine==='Paracetamol 500mg');
 new Chart(document.querySelector('#fullchart'),{type:'line',data:{labels:d.map(x=>x.day),datasets:[
 {label:'Actual Demand',data:d.map(x=>x.actual),borderColor:'#315fe8',backgroundColor:'#315fe81a',fill:true,tension:.35},
 {label:'Forecast',data:d.map(x=>x.forecast),borderColor:'#20a76d',borderDash:[6,4],tension:.35}
 ]},options:{responsive:true,maintainAspectRatio:false}});
}
async function repl(){
 const d=await getJSON('/api/replenishments');
 document.querySelector('#plans').innerHTML='<table class="data-table"><tr><th>Medicine</th><th>DC</th><th>Recommended Qty</th><th>Source</th><th>Priority</th><th>Reason</th><th>Action</th></tr>'+
 d.map(x=>`<tr><td><b>${x.medicine}</b></td><td>${x.dc_name}</td><td class="redtxt">${x.recommended_qty}</td><td>${x.source}</td><td><span class="badge ${x.priority==='High'?'b-high':x.priority==='Medium'?'b-med':'b-low'}">${x.priority}</span></td><td>${x.reason}</td><td>${x.status==='Pending'?`<button class="primary" onclick="approve(${x.id})">Approve</button>`:'<span class="badge b-ok">Approved</span>'}</td></tr>`).join('')+'</table>';
}
async function approve(id){await getJSON('/api/replenishments/'+id+'/approve',{method:'POST'});repl()}
async function simulate(){
 const d=await getJSON('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({increase:20})});
 document.querySelector('#scenario').innerHTML='<h3>What-if Analysis — Demand +20%</h3><p class="muted">Simulated impact if demand increases by 20%.</p><div class="scenario-grid">'+d.filter(x=>x.shortage>0).slice(0,4).map(x=>`<div class="scenario-box"><b>${x.medicine}</b><p>Base forecast: ${x.base}</p><p>New forecast: <b>${x.forecast}</b></p><p class="redtxt">Potential shortage: ${x.shortage}</p></div>`).join('')+'</div>';
}
async function alerts(){
 const d=await getJSON('/api/dashboard');
 document.querySelector('#allalerts').innerHTML=d.alerts.map(x=>`<div class="alert-row"><div class="alert-icon ${x.type}">${x.type==='danger'?'!':x.type==='warning'?'▱':x.type==='success'?'✓':'i'}</div><div><b>${x.title}</b><small>${x.detail}</small></div><time>${x.time_text}</time></div>`).join('');
}
document.addEventListener('DOMContentLoaded',()=>{
 const p=location.pathname;
 if(p==='/') dashboard();
 if(p==='/inventory') inventory();
 if(p==='/demand') demand();
 if(p==='/replenishment') repl();
 if(p==='/alerts') alerts();
});
