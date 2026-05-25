import re

with open('dashboards/integrated_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace HTML
old_html = r"""        <div class="day-toggle">
          <span class="day-lbl">Métricas:</span>
          <button class="day-btn active" onclick="setDay\('D1',this\)">D1 — Día 1</button>
          <button class="day-btn" onclick="setDay\('D3',this\)">D3 — Día 3</button>
          <button class="day-btn" onclick="setDay\('D7',this\)">D7 — Día 7</button>
        </div>

        <div class="chart-card rev" style="margin-bottom:16px;">
          <div class="chart-title" id="ct-views">Views por post — D1 / Total al mes</div>
          <div class="chart-sub">Reels en verde · Posts en dorado</div>
          <div class="legend">
            <div class="legend-item"><div class="ld" style="background:#7d9c6e"></div>Reel</div>
            <div class="legend-item"><div class="ld" style="background:#c4a96b"></div>Post</div>
          </div>
          <div class="cw-tall"><canvas id="cPostViews"></canvas></div>
        </div>

        <div class="chart-grid rev" style="margin-bottom:16px;">
          <div class="chart-card"><div class="chart-title" id="ct-likes">Likes por post</div>
            <div class="cw"><canvas id="cPostLikes"></canvas></div></div>
          <div class="chart-card"><div class="chart-title" id="ct-saves">Saves por post</div>
            <div class="cw"><canvas id="cPostSaves"></canvas></div></div>
        </div>"""

new_html = r"""        <div class="day-toggle">
          <span class="day-lbl">Métrica:</span>
          <select id="selMetric" onchange="buildPostCharts(this.value)" style="padding:6px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:12px;cursor:pointer;">
            <option value="views">Views</option>
            <option value="likes">Likes</option>
            <option value="comments">Comments</option>
            <option value="shared">Shared</option>
            <option value="saves">Saves</option>
            <option value="er">Engagement Rate</option>
          </select>
        </div>

        <div class="chart-card rev" style="margin-bottom:16px;">
          <div class="chart-title" id="ct-timeline">Línea de tiempo D1 · D3 · D7</div>
          <div class="chart-sub">Evolución de la métrica seleccionada por post cronológicamente</div>
          <div class="legend">
            <div class="legend-item"><div class="ld" style="background:var(--blue)"></div>D1</div>
            <div class="legend-item"><div class="ld" style="background:var(--gold)"></div>D3</div>
            <div class="legend-item"><div class="ld" style="background:var(--accent)"></div>D7</div>
          </div>
          <div class="cw-tall"><canvas id="cTimelineChart"></canvas></div>
        </div>"""

content = re.sub(old_html, new_html, content)

# Replace Javascript `var curDay="D1"` -> `var curMetric="views"`
content = content.replace('var curDay="D1"', 'var curMetric="views"')

# Find buildPostCharts to replace
old_build_func_pattern = r"function buildPostCharts\(day,c\)\{[\s\S]*?\n\}"

new_build_func = r"""function buildPostCharts(metric,c){
  if(metric && typeof metric === 'string') { curMetric = metric; }
  else { metric = curMetric; }
  if(!c)c=getC();
  
  var ps=filteredPosts();
  // Format labels like "20 Mar - Culinary"
  var labels=ps.map(function(p){return p.date + " " + (p.m||"").slice(0,3) + " - " + (p.tema||"").split(" ")[0].slice(0,12);});
  
  function extract(mArray, erValue) {
    if(!mArray || !mArray.length) return null;
    if(metric === "views") return mArray[0];
    if(metric === "likes") return mArray[1];
    if(metric === "comments") return mArray[2];
    if(metric === "shared") return mArray[3];
    if(metric === "saves") return mArray[5];
    if(metric === "er") return erValue;
    return null;
  }
  
  var d1Data = ps.map(function(p){ return extract(p.d1, p.er1); });
  var d3Data = ps.map(function(p){ return extract(p.d3, p.er3); });
  var d7Data = ps.map(function(p){ return extract(p.d7, p.er7); });

  var ds = [
    {
      label:"D1", data:d1Data,
      borderColor:c.blue, backgroundColor:c.blue+"22",
      borderWidth:2.5, tension:0.25, pointRadius:3, pointBackgroundColor:c.blue, pointHoverRadius:5,
      spanGaps:false
    },
    {
      label:"D3", data:d3Data,
      borderColor:c.gold, backgroundColor:c.gold+"22",
      borderWidth:2.5, tension:0.25, pointRadius:3, pointBackgroundColor:c.gold, pointHoverRadius:5,
      spanGaps:false
    },
    {
      label:"D7", data:d7Data,
      borderColor:c.green, backgroundColor:c.green+"22",
      borderWidth:2.5, tension:0.25, pointRadius:3, pointBackgroundColor:c.green, pointHoverRadius:5,
      spanGaps:false
    }
  ];

  var opt = JSON.parse(JSON.stringify(bOpts(c)));
  opt.scales = opt.scales || {};
  opt.scales.x = opt.scales.x || {};
  opt.scales.x.ticks = opt.scales.x.ticks || {};
  opt.scales.x.ticks.maxRotation = 45;
  opt.scales.x.ticks.minRotation = 45;
  opt.interaction = { mode: 'index', intersect: false };
  opt.plugins = opt.plugins || {};
  opt.plugins.tooltip = { enabled: true, mode: 'index', intersect: false };

  sc("cTimelineChart",{type:"line",data:{labels:labels,datasets:ds},options:opt});

  var tbody=document.getElementById("posts-tbody");tbody.innerHTML="";
  ps.forEach(function(p){
    var has = p.d1 && p.d1.length > 0;
    var tr=document.createElement("tr");
    var pill="<span class='pill pill-"+(p.tipo||"post").toLowerCase()+"'>"+(p.tipo||"")+"</span>";
    var src=p.leg
      ?"<span style='font-size:10px;color:var(--warning)'>Total al mes</span>"
      :"<span style='font-size:10px;color:var(--positive)'>Actual</span>";
    function ce(v){return(v==null)?"<td><span class='nn'>—</span></td>":"<td>"+v+"</td>";}
    tr.innerHTML="<td>"+p.date+" "+(p.m||"")+"</td><td>"+pill+"</td><td>"+(p.tema||"")+"</td>"
      +(has?ce(p.d1[0])+ce(p.d1[1])+ce(p.d1[2])+ce(p.d1[3])+ce(p.d1[5]):"<td colspan='5' style='color:var(--text-sec);font-size:11px'>Sin datos D1</td>")
      +"<td>"+src+"</td>";
    tbody.appendChild(tr);
  });
}"""

content = re.sub(old_build_func_pattern, new_build_func, content)

# Remove setDay function
set_day_func = r"function setDay\(day,btn\)\{[\s\S]*?\n\}"
content = re.sub(set_day_func, "", content)

# Replace buildPostCharts(curDay,c) with buildPostCharts(curMetric,c)
content = content.replace("buildPostCharts(curDay,c);", "buildPostCharts(curMetric,c);")
content = content.replace("buildPostCharts(curDay);", "buildPostCharts(curMetric);")

with open('dashboards/integrated_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
