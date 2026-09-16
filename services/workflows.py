"""Desktop-compatible web workflows. No Windows automation or filesystem staging."""
import copy
import hashlib
import io
import json
import re
import zipfile
import pandas as pd
from services.app_data import mapping, schedule_data, shop_data, DEFAULT_SHOP
from services.auth import roles
from services.schedule_service import ScheduleService


def allowed(db, user, shop, permission):
    record = mapping(mapping(db.get('users')).get(user))
    if not record: return False
    admin, super_admin = roles(user, record)
    if not super_admin and (record.get('shop_id') or DEFAULT_SHOP) != shop: return False
    return admin or permission in (record.get('edit_permissions') or [])


def schedule_token(data):
    keys = ('schedule_v2', 'detailed_history', 'stats', 'schedule_fairness_stats', 'schedule_lock')
    return hashlib.sha256(json.dumps({k:data.get(k) for k in keys}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def names(raw):
    result=[]; seen=set()
    for name in str(raw).replace(',', '\n').splitlines():
        name=name.strip()
        if name and name.casefold() not in seen:
            result.append(name); seen.add(name.casefold())
    return result


def make_draft(data, pools, special):
    pools={shift:names('\n'.join(staff)) for shift,staff in pools.items()}
    if not any(pools.values()): raise ValueError('Nhập ít nhất một nhân viên vào danh sách ca.')
    if mapping(data.get('schedule_lock')).get('locked'): raise ValueError('Lịch đã chốt. Cần quản trị mở khóa trên app trước.')
    # Keep a single spelling for the same person across different pools.
    spelling={}
    for shift, staff in pools.items():
        pools[shift]=[spelling.setdefault(n.casefold(), n) for n in staff]
    _,stats=schedule_data(data)
    history,new_stats=ScheduleService.generate_weekly_schedule(pools, special, stats)
    return {'history':history, 'stats':new_stats, 'base':schedule_token(data),
            'inputs':{**{'input_'+shift.lower():'\n'.join(staff) for shift,staff in pools.items()}, 'entry_ex':', '.join(special)}}


def schedule_payload(draft):
    return {'schema_version':2, 'deleted':False,
            'days':[{'date_label':day, 'shifts':[{'name':shift,'staff':staff} for shift,staff in shifts.items()]} for day,shifts in draft['history'].items()],
            'stats':[{'name':name,'value':value} for name,value in draft['stats'].items()]}


def apply_schedule(db, user, shop, draft):
    if not allowed(db,user,shop,'CHIA LỊCH TỰ ĐỘNG'): raise ValueError('Tài khoản không còn quyền sắp lịch tại chi nhánh này.')
    data=shop_data(db,shop)
    if mapping(data.get('schedule_lock')).get('locked'): raise ValueError('Lịch đã được chốt. Bản xem trước chưa được lưu.')
    if schedule_token(data)!=draft['base']: raise ValueError('Lịch hoặc tích lũy đã thay đổi. Hãy tạo lại bản xem trước để tránh ghi đè.')
    result=copy.deepcopy(db)
    node=result if shop==DEFAULT_SHOP else result.setdefault('shops',{}).setdefault(shop,{})
    if 'inputs' in draft:
        result.setdefault('settings',{}).update(copy.deepcopy(draft['inputs']))
    node['schedule_v2']=schedule_payload(draft)
    node['schedule_fairness_stats']=copy.deepcopy(draft['stats'])
    for key in ('detailed_history','stats','schedule_manual_undo','schedule_lock'): node.pop(key,None)
    return result


def split_workbook(content, filename, recipients):
    recipients=names('\n'.join(recipients))
    if not recipients: raise ValueError('Chọn ít nhất một người nhận.')
    if len(content)>20*1024*1024: raise ValueError('File tối đa 20 MB.')
    if filename.lower().endswith('.xlsx'):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            if sum(i.file_size for i in z.infolist())>150*1024*1024: raise ValueError('File Excel giải nén quá lớn. Hãy chia nhỏ file nguồn.')
    frame=pd.read_excel(io.BytesIO(content), dtype=object)
    if frame.empty: raise ValueError('File Excel chưa có dòng dữ liệu.')
    if len(frame)>100000: raise ValueError('Tối đa 100.000 dòng mỗi lượt chia.')
    output=io.BytesIO(); report=[]; start=0
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for i,name in enumerate(recipients):
            end=start+len(frame)//len(recipients)+(i<len(frame)%len(recipients))
            safe=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',name).strip(' .')[:80] or 'Nhan_vien'
            path=f'{i+1:02d}_{safe}.xlsx'
            buf=io.BytesIO()
            # Write literal strings; imported data beginning '=' must not become formulas.
            with pd.ExcelWriter(buf,engine='xlsxwriter',engine_kwargs={'options':{'strings_to_formulas':False,'strings_to_urls':False}}) as writer:
                frame.iloc[start:end].to_excel(writer,index=False)
            archive.writestr(path,buf.getvalue())
            report.append({'Người nhận':name,'Số dòng':end-start,'File':path})
            start=end
    return output.getvalue(),report
