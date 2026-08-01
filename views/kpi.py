import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def s_float(val):
    if val is None or str(val).strip() == "": return 0.0
    try: return float(str(val).replace(',', '').replace('.', ''))
    except: return 0.0

def fmt_dot(val):
    if val == 0: return "0"
    v = s_float(val)
    if v.is_integer(): return f"{int(v):,}".replace(",", ".")
    return f"{v:,.1f}".replace(",", ".")

def update_kpi_db(shop_id, user_kpi, data):
    path = f"kpi/{shop_id}/{user_kpi}"
    try:
        requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{path}.json", json=data)
    except: pass

def render_kpi():
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 5px; font-weight:800;'>📈 THEO DÕI & CẬP NHẬT KPI</h3>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom: 25px; color: #d1d5db;'>Xem tiến độ và đồng bộ số liệu chạy số thời gian thực</p>", unsafe_allow_html=True)
    
    components.html("""
    <script>
    const doc = window.parent.document;
    if (!doc.getElementById("kpi-format-money")) {
        let s = doc.createElement("script");
        s.id = "kpi-format-money";
        s.innerHTML = `
            document.addEventListener('input', function(e) {
                if (e.isTrusted && e.target && e.target.tagName === 'INPUT') {
                    let p = e.target.placeholder || "";
                    if (p.includes("Mục tiêu") || p.includes("Nợ") || p.includes("Đã đạt")) {
                        let oldVal = e.target.value;
                        let oldCursor = e.target.selectionStart;
                        let raw = oldVal.replace(/[^0-9]/g, '');
                        if (raw) {
                            let formatted = Number(raw).toLocaleString('vi-VN').replace(/,/g, '.');
                            if (formatted !== oldVal) {
                                let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                nativeSetter.call(e.target, formatted);
                                e.target.dispatchEvent(new Event('input', { bubbles: true }));
                                let diff = formatted.length - oldVal.length;
                                e.target.setSelectionRange(oldCursor + diff, oldCursor + diff);
                            }
                        }
                    }
                }
            });
        `;
        doc.body.appendChild(s);
    }
    </script>
    """, height=0, width=0)

    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    # Ép hệ thống kéo dữ liệu TƯƠI SỐNG nhất từ Firebase về để quét
    full_db = st.session_state.get("db", {})
    try:
        r = requests.get(FIREBASE_URL)
        if r.status_code == 200:
            fresh_db = r.json() or {}
            if isinstance(fresh_db, dict):
                full_db = fresh_db
                st.session_state.db = full_db
    except: pass
    
    # ==========================================
    # THUẬT TOÁN "MÁY HÚT DỮ LIỆU" - VÉT SẠCH MỌI NGÓC NGÁCH
    # ==========================================
    kpi_merged = {}
    
    # 1. Đi càn quét tìm tất cả những hồ sơ có chữ "target", "achieved", "debt"
    def hunt_kpi(node):
        if isinstance(node, dict):
            if "target" in node and "achieved" in node and "debt" in node:
                return True
            for k, v in node.items():
                if hunt_kpi(v):
                    # Tìm thấy dữ liệu cũ, nhặt bỏ vào giỏ
                    if k not in kpi_merged:
                        kpi_merged[k] = v
        elif isinstance(node, list):
            for item in node:
                hunt_kpi(item)
        return False
        
    hunt_kpi(full_db)
    
    # 2. Ghi đè ưu tiên bằng dữ liệu của nhánh hiện tại (nếu nhân viên vừa được cập nhật mới ở nhánh này)
    shop_kpi = full_db.get("kpi", {}).get(shop_id, {})
    if isinstance(shop_kpi, dict):
        for k, v in shop_kpi.items():
            if isinstance(v, dict) and "target" in v:
                kpi_merged[k] = v

    kpi_users = list(kpi_merged.keys())
    kpi_users.sort()
    
    users = full_db.get("users", {})
    current_user = st.session_state.get("current_user", "")
    u_info = users.get(current_user, {})
    user_role = u_info.get("role", "")
    edit_perms = u_info.get("edit_permissions", [])
    
    can_edit = current_user.lower() == "admin" or user_role == "admin" or "SỬA SỐ KPI" in edit_perms

    t1, t2 = st.tabs(["🖼️ BẢNG KPI (ẢNH)", "📊 DỮ LIỆU CHI TIẾT & CẬP NHẬT"])

    with t1:
        if not kpi_users:
            st.info("Chưa có dữ liệu KPI nào được lưu. Hãy sang tab 'Dữ liệu chi tiết' để thêm mới!")
        else:
            cols = st.columns(3)
            medals = ["🥇", "🥈", "🥉"]
            
            user_metrics = []
            for u in kpi_users: 
                u_kpi = kpi_merged.get(u, {})
                t_val = s_float(u_kpi.get("target", 0))
                d_val = s_float(u_kpi.get("debt", 0))
                a_val = s_float(u_kpi.get("achieved", 0))
                
                total_target = t_val + d_val
                percent = (a_val / total_target * 100) if total_target > 0 else (100 if a_val > 0 else 0)
                missing = total_target - a_val if total_target > a_val else 0
                surpassed = a_val - total_target if a_val > total_target else 0
                
                user_metrics.append({
                    "name": str(u).upper(), "target": t_val, "debt": d_val, "total_target": total_target,
                    "achieved": a_val, "percent": percent, "missing": missing, "surpassed": surpassed
                })
            
            user_metrics.sort(key=lambda x: x["percent"], reverse=True)

            for i, um in enumerate(user_metrics):
                col = cols[i % 3]
                medal = medals[i] if i < 3 else "👤"
                
                html_card = f"""
                <div style="background-color: #fafafa; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                        <div style="font-weight: 900; color: #1e40af; font-size: 16px; margin-top: -3px;">{medal} {um['name']}</div>
                        <div style="text-align: right; font-size: 14px; line-height: 1.5;">
                            <div style="color: #64748b;">Mục tiêu: <b>{fmt_dot(um['target'])}</b></div>
                            <div style="color: #ea580c;">Nợ cũ: <b>{fmt_dot(um['debt'])}</b></div>
                            <div style="color: #334155; margin-bottom: 8px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">Tổng MT: <b>{fmt_dot(um['total_target'])}</b></div>
                            
                            <div style="color: #059669; font-size: 18px; font-weight: 900; margin-bottom: 2px;">{fmt_dot(um['achieved'])}</div>
                            """
                if um['surpassed'] > 0:
                    html_card += f"""<div style="color: #2563eb; font-weight: 800; font-size: 15px;">+{fmt_dot(um['surpassed'])} (Vượt)</div>"""
                else:
                    html_card += f"""<div style="color: #dc2626; font-weight: 800; font-size: 15px;">{fmt_dot(um['missing'])}</div>"""
                
                html_card += f"""
                        </div>
                    </div>
                    <div style="font-size: 13px; color: #334155; margin-bottom: 6px; font-weight: 700;">
                        Hoàn thành: {um['percent']:.1f}%
                    </div>
                    <div style="width: 100%; background-color: #cbd5e1; border-radius: 99px; height: 8px; overflow: hidden;">
                        <div style="width: {min(um['percent'], 100)}%; background-color: {'#3b82f6' if um['percent'] >= 100 else '#10b981'}; height: 100%; border-radius: 99px;"></div>
                    </div>
                </div>
                """
                col.markdown(html_card, unsafe_allow_html=True)

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        if can_edit:
            st.markdown("#### ⚙️ CẬP NHẬT SỐ LIỆU NHÂN VIÊN")
            
            db_users = [u for u in users.keys() if u.lower() != "admin"]
            all_options = list(set(kpi_users + db_users))
            all_options.sort()
            
            c_sel, c_new = st.columns(2)
            selected_user_dd = c_sel.selectbox("👤 Chọn Nhân Viên để sửa", ["-- Thêm nhân viên mới (Gõ tay) --"] + all_options)
            
            if selected_user_dd == "-- Thêm nhân viên mới (Gõ tay) --":
                selected_user = c_new.text_input("➕ Nhập TÊN NHÂN VIÊN MỚI", placeholder="VD: NGỌC, HOÀNG...")
            else:
                selected_user = selected_user_dd
            
            if selected_user and selected_user.strip() != "":
                u_kpi = kpi_merged.get(selected_user, {})
                c1, c2, c3 = st.columns(3)
                
                target = c1.text_input("🎯 Mục tiêu tháng này", value=fmt_dot(u_kpi.get("target", 0)), placeholder="Mục tiêu...")
                debt = c2.text_input("⚠️ Nợ tháng trước", value=fmt_dot(u_kpi.get("debt", 0)), placeholder="Nợ...")
                achieved = c3.text_input("✅ Đã đạt (Thực tế)", value=fmt_dot(u_kpi.get("achieved", 0)), placeholder="Đã đạt...")
                
                if st.button("💾 LƯU DỮ LIỆU KPI", type="primary", use_container_width=True):
                    t_val, d_val, a_val = s_float(target), s_float(debt), s_float(achieved)
                    update_kpi_db(shop_id, selected_user, {"target": t_val, "debt": d_val, "achieved": a_val})
                    
                    if "kpi" not in st.session_state.db: st.session_state.db["kpi"] = {}
                    if shop_id not in st.session_state.db["kpi"]: st.session_state.db["kpi"][shop_id] = {}
                    st.session_state.db["kpi"][shop_id][selected_user] = {"target": t_val, "debt": d_val, "achieved": a_val}
                    
                    st.success(f"Đã cập nhật dữ liệu cho {selected_user} vào chi nhánh {shop_id}!"); time.sleep(1); st.rerun()
                    
        st.markdown("#### 📋 BẢNG CHỮ TỔNG HỢP (DÙNG ĐỂ COPY/PASTE)")
        df_list = []
        for u in kpi_users:
            u_kpi = kpi_merged.get(u, {})
            t_val = s_float(u_kpi.get("target", 0))
            d_val = s_float(u_kpi.get("debt", 0))
            a_val = s_float(u_kpi.get("achieved", 0))
            
            total_target = t_val + d_val
            missing = total_target - a_val if total_target > a_val else 0
            surpassed = a_val - total_target if a_val > total_target else 0
            
            df_list.append({
                "👤 Tên": str(u).upper(),
                "🎯 Mục Tiêu": fmt_dot(t_val),
                "⚠️ Nợ Cũ": fmt_dot(d_val),
                "📌 Tổng MT": fmt_dot(total_target),
                "✅ Đã Đạt": fmt_dot(a_val),
                "🛑 Còn Thiếu": fmt_dot(missing),
                "🔥 Vượt": fmt_dot(surpassed)
            })
        if df_list:
            st.dataframe(pd.DataFrame(df_list), hide_index=True, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu.")
