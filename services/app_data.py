"""Read the desktop HTCV cloud schema without migrations or writes."""
import copy
import math

DEFAULT_SHOP = 'Shop Chính (Mặc định)'
LOCAL_KEYS = ('kpi','quy_shop','market_history','ecom_history','schedule_images',
              'schedule_edit_log','schedule_lock','kpi_images','daily_targets', 'schedule_fairness_stats')

def mapping(value):
    return value if isinstance(value, dict) else {}

def rows(value):
    if isinstance(value, list): return [v for v in value if v is not None]
    if isinstance(value, dict): return list(value.values())
    return []

def shop_data(db, shop):
    return mapping(db) if shop == DEFAULT_SHOP else mapping(mapping(mapping(db).get('shops')).get(shop))

def schedule_data(data):
    v2 = mapping(data.get('schedule_v2'))
    if v2.get('schema_version') == 2:
        if v2.get('deleted'):
            return {}, {}
        history, stats = {}, {}
        for day in rows(v2.get('days')):
            if not isinstance(day, dict): continue
            label = str(day.get('date_label', '')).strip()
            if not label: continue
            history[label] = {}
            for shift in rows(day.get('shifts')):
                if not isinstance(shift, dict): continue
                name = str(shift.get('name', '')).strip()
                if name:
                    history[label][name] = [str(n) for n in rows(shift.get('staff')) if str(n).strip()]
        for item in rows(v2.get('stats')):
            if isinstance(item, dict) and str(item.get('name','')).strip():
                stats[str(item['name']).strip()] = copy.deepcopy(item.get('value', {}))
        return history, stats
    history = {}
    for day,value in mapping(data.get('detailed_history')).items():
        if not isinstance(value, dict): continue
        if {'Sáng','Chiều','10h30'} & value.keys():
            history[str(day)] = copy.deepcopy(value)
        else:
            for suffix,shifts in value.items():
                if isinstance(shifts, dict) and {'Sáng','Chiều','10h30'} & shifts.keys():
                    history[str(day)+'/'+str(suffix)] = copy.deepcopy(shifts)
    return history, copy.deepcopy(mapping(data.get('stats')))

def snapshot(db, shop):
    data = shop_data(db, shop)
    result = {key:copy.deepcopy(data.get(key, {})) for key in LOCAL_KEYS}
    result['detailed_history'], result['stats'] = schedule_data(data)
    result['phones'] = copy.deepcopy(mapping(db.get('phones')))
    result['shop'] = shop
    return result

def number(value):
    if isinstance(value, (int,float)):
        return float(value) if math.isfinite(value) else 0.0
    s = str(value or '').strip().replace(' ', '')
    try:
        # Desktop fields may be serialized as 1.500.000 or 1,500,000.
        if ',' in s and '.' in s: s=s.replace('.', '').replace(',', '.')
        elif ',' in s: s=s.replace(',', '') if len(s.split(',')[-1]) == 3 else s.replace(',', '.')
        elif s.count('.') > 1 or (s.count('.') == 1 and len(s.split('.')[-1]) == 3): s=s.replace('.', '')
        result=float(s)
        return result if math.isfinite(result) else 0.0
    except (ValueError,TypeError): return 0.0

def kpi_records(db, shop):
    data = shop_data(db, shop)
    node = mapping(data.get('kpi'))
    if isinstance(node.get(shop), dict) and 'emp' in node[shop]: node=node[shop]
    # Explicit canonical node wins even when the employee collection was deleted.
    if any(k in node for k in ('emp','m','tot')):
        emp = node.get('emp', {})
        if isinstance(emp,list): emp={str(i):v for i,v in enumerate(emp) if v is not None}
        return mapping(emp), node, 'desktop'
    legacy = mapping(mapping(db.get('kpi')).get(shop))
    if not legacy and shop == DEFAULT_SHOP: legacy=node
    legacy={k:v for k,v in legacy.items() if isinstance(v,dict) and any(f in v for f in ('target','achieved','debt'))}
    return legacy, {}, 'legacy'

def kpi_table(db,shop):
    records,meta,schema = kpi_records(db,shop)
    table=[]
    for name,record in records.items():
        if not isinstance(record,dict): continue
        if schema=='desktop':
            base,short,sold = (number(record.get(k,0)) for k in ('base','short','sold'))
            target=number(record.get('tgt',base+short))
        else:
            base,short,sold = (number(record.get(k,0)) for k in ('target','debt','achieved'))
            target=base+short
        table.append({'Nhân viên':name,'Target gốc':base,'Thiếu / dư tháng trước':short,
                      'Target tháng':target,'Đã bán':sold,'Còn thiếu':max(0,target-sold),
                      'Vượt':max(0,sold-target),'Hoàn thành (%)':round(sold/target*100,1) if target>0 else (100 if sold>0 else 0)})
    return table,meta

def target_tables(data):
    """Show saved results exactly; do not recalculate or rewrite monthly targets."""
    data=mapping(data); metrics=mapping(data.get('metrics')); results=mapping(data.get('results'))
    desktop=any(k in data for k in ('nv','ca1','ca2','results'))
    inputs=[]
    for name,record in metrics.items():
        if not isinstance(record,dict):continue
        if desktop:
            inputs.append({'Chỉ số':name,'Gốc':record.get('goc',''),'Tỷ lệ (%)':record.get('pct',''),
                           'Tháng cần bán':record.get('thang',''),'Ngày cần bán':record.get('ngay','')})
        else:
            inputs.append({'Chỉ số':name,'Gốc':record.get('g',''),'Tỷ lệ (%)':record.get('p',''),
                           'Nợ':record.get('tt',''),'Đã bán':record.get('db',''),'Còn lại':record.get('cl',''),'Ngày cần bán':record.get('n','')})
    output={}
    for key,columns in {
        'per_employee':{'thang':'Tháng / người','ngay':'Ngày / người'},
        'per_shift':{'tong_ngay':'Tổng ngày','ca1':'Ca sáng','ca2':'Ca chiều'},
        'per_shift_person':{'ca1':'Ca sáng / người','ca2':'Ca chiều / người'}
    }.items():
        output[key]=[dict({'Chỉ số':name},**{label:value.get(field,'') for field,label in columns.items()})
                     for name,value in mapping(results.get(key)).items() if isinstance(value,dict)]
    return inputs, output
