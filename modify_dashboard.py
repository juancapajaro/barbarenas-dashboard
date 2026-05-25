import re

with open('dashboards/integrated_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace HTML
old_html = r"""        <div class="day-toggle">
          <span class="day-lbl">Métrica:</span>
          <select id="selMetric" onchange="buildPostCharts\(this.value\)" style="padding:6px 12px;border-radius:6px;border:1px solid var\(--border\);background:var\(--surface\);color:var\(--text\);font-size:12px;cursor:pointer;">
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
            <div class="legend-item"><div class="ld" style="background:var\(--blue\)"></div>D1</div>
            <div class="legend-item"><div class="ld" style="background:var\(--gold\)"></div>D3</div>
            <div class="legend-item"><div class="ld" style="background:var\(--accent\)"></div>D7</div>
          </div>
          <div class="cw-tall"><canvas id="cTimelineChart"></canvas></div>
        </div>"""

new_html = r"""        <div class="chart-card rev" style="margin-bottom:16px;">
          <div class="chart-title">Evolución y Crecimiento de Interacciones (D1, D3, D7)</div>
          <div class="chart-sub">Suma de Views, Likes, Comments, Shared, Repost y Saves</div>
          <div class="legend">
            <div class="legend-item"><div class="ld" style="background:var(--blue)"></div>D1</div>
            <div class="legend-item"><div class="ld" style="background:var(--gold)"></div>D3</div>
            <div class="legend-item"><div class="ld" style="background:var(--accent)"></div>D7</div>
          </div>
          <div class="cw-tall"><canvas id="cInteractions"></canvas></div>
        </div>

        <div class="chart-card rev" style="margin-bottom:16px;">
          <div class="chart-title">Alcance Inmediato - Vistas Totales Día 1 (Views D1)</div>
          <div class="chart-sub">Volumen de reproducciones iniciales por publicación</div>
          <div class="cw-tall"><canvas id="cViewsD1"></canvas></div>
        </div>"""

content = re.sub(old_html, new_html, content)

# Table headers
old_table_headers = r"<th>Views</th><th>Likes</th><th>Comments</th><th>Shared</th><th>Saves</th>"
new_table_headers = r"<th>Views D1</th><th>Inter. D1</th><th>Inter. D3</th><th>Inter. D7</th><th></th>"
content = re.sub(old_table_headers, new_table_headers, content)

# Replace buildPostCharts function
old_build_func_pattern = r"function buildPostCharts\(metric,c\)\{[\s\S]*?\n\}"

new_build_func = r"""function buildPostCharts(c){
  if(!c)c=getC();
  
  var ps=filteredPosts();
  var labels=ps.map(function(p){return p.label;});
  
  var totD1 = ps.map(function(p){ return p.Total_Interacciones_D1; });
  var totD3 = ps.map(function(p){ return p.Total_Interacciones_D3; });
  var totD7 = ps.map(function(p){ return p.Total_Interacciones_D7; });
  var viewsD1 = ps.map(function(p){ return p.Views_D1_Puras; });

  var optBars = JSON.parse(JSON.stringify(bOpts(c)));
  optBars.scales = optBars.scales || {};
  optBars.scales.x = optBars.scales.x || {};
  optBars.scales.x.ticks = optBars.scales.x.ticks || {};
  optBars.scales.x.ticks.maxRotation = 45;
  optBars.scales.x.ticks.minRotation = 45;
  optBars.interaction = { mode: 'index', intersect: false };
  optBars.plugins = optBars.plugins || {};
  optBars.plugins.tooltip = { enabled: true, mode: 'index', intersect: false };

  sc("cInteractions",{
    type:"bar",
    data:{
      labels:labels,
      datasets:[
        {label:"Inter. D1", data:totD1, backgroundColor:c.blue+"cc", borderRadius:4},
        {label:"Inter. D3", data:totD3, backgroundColor:c.gold+"cc", borderRadius:4},
        {label:"Inter. D7", data:totD7, backgroundColor:c.green+"cc", borderRadius:4}
      ]
    },
    options:optBars
  });

  var optLines = JSON.parse(JSON.stringify(optBars));
  sc("cViewsD1",{
    type:"line",
    data:{
      labels:labels,
      datasets:[
        {
          label:"Views D1", data:viewsD1,
          borderColor:c.mauve, backgroundColor:c.mauve+"33",
          borderWidth:3, tension:0.3, fill:true, pointRadius:4, pointBackgroundColor:c.mauve, pointHoverRadius:6, spanGaps:false
        }
      ]
    },
    options:optLines
  });

  var tbody=document.getElementById("posts-tbody");tbody.innerHTML="";
  ps.forEach(function(p){
    var has = p.Total_Interacciones_D1 != null;
    var tr=document.createElement("tr");
    var pill="<span class='pill pill-"+(p.tipo||"post").toLowerCase()+"'>"+(p.tipo||"")+"</span>";
    var src=p.leg
      ?"<span style='font-size:10px;color:var(--warning)'>Pre-Mayo</span>"
      :"<span style='font-size:10px;color:var(--positive)'>Actual</span>";
    function ce(v){return(v==null)?"<td><span class='nn'>—</span></td>":"<td>"+v+"</td>";}
    tr.innerHTML="<td>"+p.date+" "+(p.m||"")+"</td><td>"+pill+"</td><td>"+(p.tema||"")+"</td>"
      +(has?ce(p.Views_D1_Puras)+ce(p.Total_Interacciones_D1)+ce(p.Total_Interacciones_D3)+ce(p.Total_Interacciones_D7)+"<td></td>":"<td colspan='5' style='color:var(--text-sec);font-size:11px'>Sin datos</td>")
      +"<td>"+src+"</td>";
    tbody.appendChild(tr);
  });
}"""

content = re.sub(old_build_func_pattern, new_build_func, content)

# Remove `var curMetric="views";`
content = content.replace('var curMetric="views";', '')
content = content.replace("buildPostCharts(curMetric,c);", "buildPostCharts(c);")
content = content.replace("buildPostCharts(curMetric);", "buildPostCharts(c);")
content = content.replace("buildPostCharts();", "buildPostCharts(c);")

# Update `applyMergedData` where it might call buildPostCharts
content = re.sub(r'buildPostCharts\([^\)]*\);', 'buildPostCharts();', content)

with open('dashboards/integrated_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
