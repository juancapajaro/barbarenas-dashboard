import pandas as pd
import json
import numpy as np

def main():
    posts_csv_path = "data-sources/Reporte Mensual Marketing - Registro Posts (3).csv"
    daily_csv_path = "data-sources/Reporte Mensual Marketing - Registro diario.csv"
    json_path      = "dashboards/marketing_data.json"   # kept for reference
    js_path        = "dashboards/marketing_data.js"     # loaded via <script> tag, no CORS
    
    month_map = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12",
        "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
        "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
        "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12",
    }
    month_es_names = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }

    # --- PROCESS POSTS ---
    df_posts = pd.read_csv(posts_csv_path, header=[0, 1])
    posts_data = []
    
    for idx, row in df_posts.iterrows():
        date_val = row[('Unnamed: 0_level_0', 'Date')]
        month_val = row[('Unnamed: 1_level_0', 'Month')]
        post_val = row[('Unnamed: 2_level_0', 'TIPO')]
        details_val = row[('Unnamed: 3_level_0', 'Detalles')]
        
        if pd.isna(date_val) or pd.isna(month_val) or pd.isna(post_val) or str(post_val).strip() == "":
            continue
            
        try:
            day_num = int(float(str(date_val).strip()))
        except ValueError:
            continue
            
        m_str = str(month_val).strip()
        m_key = None
        for k, v in month_map.items():
            if k.lower() in m_str.lower():
                m_key = v
                break
                
        if not m_key:
            continue
            
        ym = f"2026-{m_key}"
        full_date = f"{ym}-{day_num:02d}"
        is_leg = full_date < "2026-05-05"
        
        tipo_str = str(post_val).strip()
        label_str = f"{day_num}-{month_es_names[m_key][:3]} ({tipo_str})"
        
        def calc_interactions(prefix, alt_prefix):
            try:
                def get_val(c):
                    val = row.get((prefix, c), np.nan)
                    if pd.isna(val):
                        val = row.get((alt_prefix, c), np.nan)
                    if pd.isna(val): return np.nan
                    return pd.to_numeric(str(val).replace(',', ''), errors='coerce')
                    
                views = get_val('Views')
                likes = get_val('Likes')
                comments = get_val('Comments')
                shared = get_val('Shared')
                repost = get_val('Repost')
                saves = get_val('Saves')
                
                metrics = [views, likes, comments, shared, repost, saves]
                # If all metrics are NaN, return None
                if all(pd.isna(m) for m in metrics):
                    return None
                    
                interactions = np.nansum(metrics)
                return float(interactions)
            except Exception as e:
                return None
                
        def get_views_pure(prefix, alt_prefix):
            try:
                val = row.get((prefix, 'Views'), np.nan)
                if pd.isna(val):
                    val = row.get((alt_prefix, 'Views'), np.nan)
                if pd.isna(val): return None
                return float(pd.to_numeric(str(val).replace(',', ''), errors='coerce'))
            except:
                return None

        def get_metric_val(metric_name, prefix, alt_prefix):
            try:
                val = row.get((prefix, metric_name), np.nan)
                if pd.isna(val):
                    val = row.get((alt_prefix, metric_name), np.nan)
                if pd.isna(val): return None
                return float(pd.to_numeric(str(val).replace(',', ''), errors='coerce'))
            except:
                return None

        tot_d1 = calc_interactions('D1', 'DIA 1')
        tot_d3 = calc_interactions('D3', 'DIA 3')
        tot_d7 = calc_interactions('D7', 'DIA 7')
        views_d1   = get_metric_val('Views',    'D1', 'DIA 1')
        likes_d1   = get_metric_val('Likes',    'D1', 'DIA 1')
        comments_d1= get_metric_val('Comments', 'D1', 'DIA 1')
        shared_d1  = get_metric_val('Shared',   'D1', 'DIA 1')
        saves_d1   = get_metric_val('Saves',    'D1', 'DIA 1')
        
        post_dict = {
            "date": day_num,
            "m": month_es_names[m_key],
            "ym": ym,
            "tipo": tipo_str,
            "tema": str(details_val).strip() if not pd.isna(details_val) else "",
            "leg": is_leg,
            "label": label_str,
            "Total_Interacciones_D1": tot_d1,
            "Total_Interacciones_D3": tot_d3,
            "Total_Interacciones_D7": tot_d7,
            "Views_D1_Puras": views_d1,
            "Likes_D1":    likes_d1,
            "Comments_D1": comments_d1,
            "Shared_D1":   shared_d1,
            "Saves_D1":    saves_d1
        }
        posts_data.append(post_dict)

    # --- PROCESS DAILY ---
    daily_data = {}
    try:
        with open(daily_csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        header_idx = -1
        for i, line in enumerate(lines):
            if "Date" in line and "Month" in line:
                header_idx = i
                break
                
        if header_idx != -1:
            df_daily = pd.read_csv(daily_csv_path, skiprows=header_idx)
            for idx, row in df_daily.iterrows():
                d_val = row.get('Date')
                m_val = row.get('Month')
                s_val = row.get('Stories')
                f_val = row.get('Followers')
                
                if pd.isna(d_val) or pd.isna(m_val):
                    continue
                    
                try:
                    day_num = int(float(str(d_val).strip()))
                except ValueError:
                    continue
                    
                m_str = str(m_val).strip()
                m_key = None
                for k, v in month_map.items():
                    if k.lower() in m_str.lower():
                        m_key = v
                        break
                        
                if not m_key:
                    continue
                    
                ym = f"2026-{m_key}"
                
                s = int(float(str(s_val).strip())) if pd.notna(s_val) and str(s_val).strip() else 0
                f_num = int(float(str(f_val).strip())) if pd.notna(f_val) and str(f_val).strip() else 0
                
                if ym not in daily_data:
                    daily_data[ym] = []
                daily_data[ym].append({
                    "d": day_num,
                    "s": s,
                    "f": f_num
                })
    except Exception as e:
        print(f"Error processing daily CSV: {e}")
        
    payload = {"posts": posts_data, "daily": daily_data}

    # Write canonical JSON (for reference / HTTP server usage)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Write JS module so the dashboard works when opened via file:// (no CORS issues)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by process_data.py — do not edit manually\n")
        f.write("window.MARKETING_DATA = ")
        json.dump(payload, f, ensure_ascii=False)
        f.write(";\n")
        
    print(f"Processed {len(posts_data)} posts and daily data for {list(daily_data.keys())}")

if __name__ == "__main__":
    main()
