import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import time

FIREBASE_URL = "https://htcv-5c857-default-rtdb.firebaseio.com/htcv.json"

def s_float(val):
    if val is None or str(val).strip() == "": return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).strip()
    try:
        return float(s)
    except ValueError:
        try: return float(s.replace('.', '').replace(',', ''))
        except: return 0.0
    
def fmt_dot(val):
    v = s_float(val)
    if v == 0: return ""
    if v.is_integer(): return f"{int(v):,}".replace(",", ".")
    return f"{v:,.1f}".replace(",", ".")

def fmt_num(val):
    v = s_float(val)
    return f"{int(v)}" if v.is_integer() else f"{v}"

def update_firebase_target(path, data, shop_id):
    db_path = path if shop_id == "Shop Chính (Mặc định)" else f"shops/{shop_id}/{path}"
    try:
        requests.patch(f"{FIREBASE_URL.replace('.json', '')}/{db_path}.json", json=data)
    except Exception as e:
        st.error(f"Lỗi đồng bộ: {e}")

def render_target():
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📊 Công Cụ Chia Target Đa Nền Tảng</h3>", unsafe_allow_html=True)
    
    components.html("""
    <script>
    const doc = window.parent.document;
    if (!doc.getElementById("live-format-money")) {
        let s = doc.createElement("script");
        s.id = "live-format-money";
        s.innerHTML = `
            document.addEventListener('input', function(e) {
                if (e.isTrusted && e.target && e.target.tagName === 'INPUT') {
                    let p = e.target.placeholder || "";
                    // Bổ sung thêm từ khóa "Nợ" để tự động format số tiền cho ô Nợ tháng trước
                    if (p.includes("1.500.000") || p.includes("Mục tiêu") || p.includes("Nợ") || p.includes("Ngày") || p.includes("Đã bán") || p.includes("Còn lại") || p.includes("Mỗi ngày") || p.includes("VD: 30") || p.includes("để trống") || p.includes("Gợi ý")) {
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
    full_db = st.session_state.get("db", {})
    db = full_db if shop_id == "Shop Chính (Mặc định)" else full_db.get("shops", {}).get(shop_id, {})
    
    dt_data = db.get("daily_targets", {})
    dt_cfg = dt_data.get("config", {})
    dt_mts = dt_data.get("metrics", {})

    current_user = st.session_state.get("current_user", st.session_state.get("user", ""))
    is_sys_admin = st.session_state.get("is_admin", False)
    is_sys_super = st.session_state.get("is_super_admin", False)
    
    u_info = full_db.get("users", {}).get(current_user, {})
    user_role = u_info.get("role", "")
    edit_perms = u_info.get("edit_permissions", [])
    
    can_edit = (str(current_user).lower() == "admin") or is_sys_admin or is_sys_super or (user_role == "admin") or ("TÍNH TARGET" in edit_perms)

    live_mts = {}
    
    if can_edit:
        st.markdown("<h5 style='color:#0ea5e9; font-weight: bold;'>⚙️ BẢNG NHẬP LIỆU TÙY CHỈNH (Nảy số tự động)</h5>", unsafe_allow_html=True)
        
        tab_chung, tab_ca, tab_chiso = st.tabs(["⚙️ 1. CHUNG", "👥 2. CA TRỰC", "🎯 3. CHỈ SỐ"])
        
        with tab_chung:
            c1, c2 = st.columns(2)
            nv_str = c1.text_input("👥 Tổng NV", value=fmt_num(dt_cfg.get("nv", 1)))
            nv = s_float(nv_str)
            nc_str = c2.text_input("⏳ Số ngày còn lại", value=fmt_num(dt_cfg.get("nc", 30)), placeholder="VD: 30")
            nc = s_float(nc_str)
            
            c3, c4 = st.columns(2)
            vac_str = c3.text_input("💉 Bán Vắc Xin (VNĐ)", value=fmt_dot(dt_cfg.get("vac", 0)), placeholder="VD: 1.500.000")
            vac = s_float(vac_str)
            st.markdown("""<style> .stCheckbox {padding-top: 30px;} </style>""", unsafe_allow_html=True)
            vac_chk = c4.checkbox("☑️ Trừ Vắc Xin", value=dt_cfg.get("vac_chk", True))
            
        with tab_ca:
            c5, c6 = st.columns(2)
            pc1_str = c5.text_input("☀️ CA 1 (%)", value=fmt_num(dt_cfg.get("pc1", 45)))
            pc1 = s_float(pc1_str)
            ng1_str = c6.text_input("☀️ CA 1 (Người)", value=fmt_num(dt_cfg.get("ng1", 1)))
            ng1 = s_float(ng1_str)
            
            c7, c8 = st.columns(2)
            pc2_str = c7.text_input("🌙 CA 2 (%)", value=fmt_num(dt_cfg.get("pc2", 55)))
            pc2 = s_float(pc2_str)
            ng2_str = c8.text_input("🌙 CA 2 (Người)", value=fmt_num(dt_cfg.get("ng2", 1)))
            ng2 = s_float(ng2_str)
            
        with tab_chiso:
            st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
            metrics = ["Doanh Số (VNĐ)", "Tổng Số Bill", "Cắt Liều", "Tỷ Lệ HOT", "Tỷ Lệ FS", "Tỷ Lệ 5 Sao"]
            icon_map = {"Doanh Số (VNĐ)": "💰", "Tổng Số Bill": "🧾", "Cắt Liều": "💊", "Tỷ Lệ HOT": "🔥", "Tỷ Lệ FS": "⚡", "Tỷ Lệ 5 Sao": "⭐"}
            
            for m in metrics:
                m_data = dt_mts.get(m, {})
                icon = icon_map.get(m, "🔹")
                
                with st.expander(f"{icon} {m}", expanded=False):
                    # KHÔI PHỤC Ô NHẬP NỢ THÁNG TRƯỚC
                    r1c1, r1c2, r1c3 = st.columns([1.5, 1, 1.5])
                    g_str = r1c1.text_input("Mục tiêu gốc", value=fmt_dot(m_data.get("g", 0)), key=f"g_{m}", placeholder="Mục tiêu...")
                    p_str = r1c2.text_input("% Đạt", value=fmt_num(m_data.get("p", 100)), key=f"p_{m}", placeholder="%...")
                    tt_str = r1c3.text_input("Nợ tháng trước", value=fmt_dot(m_data.get("tt", 0)), key=f"tt_{m}", placeholder="Nợ...")
                    
                    r2c1, r2c2 = st.columns(2)
                    db_str = r2c1.text_input("Đã bán (Cộng dồn)", value=fmt_dot(m_data.get("db", 0)), key=f"db_{m}", placeholder="Đã bán...")
                    
                    g_val = s_float(g_str)
                    p_val = s_float(p_str)
                    tt_val = s_float(tt_str)
                    db_val = s_float(db_str)
                    
                    # LOGIC CỘNG DỒN MỚI
                    t_val = ((g_val * p_val) / 100) + tt_val
                    if m == "Doanh Số (VNĐ)" and vac_chk:
                        t_val -= vac
                        
                    cl_val = t_val - db_val
                    if cl_val < 0: cl_val = 0
                    
                    auto_n = cl_val / nc if nc > 0 else 0
                    
                    r2c2.markdown(f"<div style='font-size:14px; margin-bottom:5px; color:#94a3b8;'>Còn phải bán</div><div style='background-color: transparent; border: 1px solid #334155; padding: 10px; border-radius: 6px; color:#10b981; font-weight:bold;'>{fmt_dot(cl_val)}</div>", unsafe_allow_html=True)
                    
                    n_str = st.text_input("Mỗi ngày cần (Để trống máy tự chia, nhập số để đè)", value=m_data.get("n_str_saved", ""), placeholder=f"Gợi ý chia đều: {fmt_dot(auto_n)}", key=f"n_{m}")
                    
                    final_n = s_float(n_str) if n_str.strip() else auto_n
                    
                    live_mts[m] = {
                        "g": g_val, "p": p_val, "tt": tt_val, "db": db_val,
                        "cl": cl_val, "n": final_n,
                        "g_str": g_str, "p_str": p_str, "tt_str": tt_str, "db_str": db_str, "n_str": n_str
                    }
            
        st.markdown("<br>", unsafe_allow_html=True)
        btn_c1, btn_c2 = st.columns([1, 1])
        
        del_btn = btn_c1.button("🗑️ XÓA SỐ TẠM LÀM LẠI", use_container_width=True)
        sub_btn = btn_c2.button("☁️ LƯU LÊN WEB", type="primary", use_container_width=True)
        
        if del_btn:
            update_firebase_target("daily_targets", {"config": {}, "metrics": {}}, shop_id)
            if shop_id == "Shop Chính (Mặc định)":
                st.session_state.db["daily_targets"] = {"config": {}, "metrics": {}}
            else:
                st.session_state.db["shops"][shop_id]["daily_targets"] = {"config": {}, "metrics": {}}
            st.success("✅ Đã dọn sạch bảng chia Target!")
            time.sleep(1)
            st.rerun()

        if sub_btn:
            if pc1 + pc2 != 100:
                st.error("❌ Tổng tỷ lệ 2 ca phải bằng 100%!")
            else:
                fmt = lambda x: f"{int(x)}" if float(x).is_integer() else str(float(x))
                new_config = {"nv": fmt(nv), "vac": fmt(vac), "vac_chk": vac_chk, "nc": fmt(nc), "pc1": fmt(pc1), "ng1": fmt(ng1), "pc2": fmt(pc2), "ng2": fmt(ng2)}
                save_mts = {}
                
                for m in metrics:
                    lm = live_mts[m]
                    # LƯU KÈM BIẾN NỢ (tt) LÊN FIREBASE CHO WINDOW KÉO VỀ
                    save_mts[m] = {"g": fmt(lm["g"]), "p": fmt(lm["p"]), "tt": fmt(lm["tt"]), "db": fmt(lm["db"]), "cl": fmt(lm["cl"]), "n": fmt(lm["n"])}
                    save_mts[m]["n_str_saved"] = lm["n_str"]
                
                updated_data = {"config": new_config, "metrics": save_mts}
                update_firebase_target("daily_targets", updated_data, shop_id)
                
                if shop_id == "Shop Chính (Mặc định)":
                    st.session_state.db["daily_targets"] = updated_data
                else:
                    if "shops" not in st.session_state.db: st.session_state.db["shops"] = {}
                    if shop_id not in st.session_state.db["shops"]: st.session_state.db["shops"][shop_id] = {}
                    st.session_state.db["shops"][shop_id]["daily_targets"] = updated_data
                    
                st.success("✅ Đã lưu kết quả (bao gồm Nợ tháng trước) lên hệ thống!")
                time.sleep(1)
                st.rerun()

    else:
        nv = s_float(dt_cfg.get("nv", 1))
        pc1 = s_float(dt_cfg.get("pc1", 45))
        ng1 = s_float(dt_cfg.get("ng1", 1))
        pc2 = s_float(dt_cfg.get("pc2", 55))
        ng2 = s_float(dt_cfg.get("ng2", 1))
        
        for m in ["Doanh Số (VNĐ)", "Tổng Số Bill", "Cắt Liều", "Tỷ Lệ HOT", "Tỷ Lệ FS", "Tỷ Lệ 5 Sao"]:
            m_data = dt_mts.get(m, {})
            live_mts[m] = {
                "cl": s_float(m_data.get("cl", 0)),
                "n": s_float(m_data.get("n", 0))
            }

    # ==========================================
    # KHU VỰC HIỂN THỊ KẾT QUẢ
    # ==========================================
    st.markdown("<br><b>📊 KẾT QUẢ PHÂN BỔ (Tự động cập nhật nhảy số)</b>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["👤 BẢNG CÁ NHÂN", "🏪 BẢNG CA TRỰC"])
    
    nv_cur = int(nv or 1)
    pc1_cur = pc1
    ng1_cur = int(ng1 or 1)
    pc2_cur = pc2
    ng2_cur = int(ng2 or 1)

    res1_data, res2_data = [], []
    
    for m in ["Doanh Số (VNĐ)", "Tổng Số Bill", "Cắt Liều", "Tỷ Lệ HOT", "Tỷ Lệ FS", "Tỷ Lệ 5 Sao"]:
        val_cl = live_mts[m]["cl"] 
        val_n = live_mts[m]["n"]
        
        thang_1 = round(val_cl / nv_cur) if nv_cur > 0 else 0
        
        ca1_t = val_n * (pc1_cur / 100)
        ca2_t = val_n * (pc2_cur / 100)
        
        ca1_1 = round(ca1_t / ng1_cur) if ng1_cur > 0 else 0
        ca2_1 = round(ca2_t / ng2_cur) if ng2_cur > 0 else 0
        
        fm_res = lambda num, is_ds: f"{int(num):,}".replace(",", ".") + (" đ" if is_ds else "")
        is_ds = (m == "Doanh Số (VNĐ)")
        
        res1_data.append({"Chỉ Số": m, "CÒN PHẢI BÁN": fm_res(thang_1, is_ds)})
        res2_data.append({"Chỉ Số": m, "Mỗi Ngày Cần": fm_res(val_n, is_ds), f"↓ CA 1 ({pc1_cur:g}%)": fm_res(round(ca1_t), is_ds), f"1 Người C1": fm_res(ca1_1, is_ds), f"CA 2 ({pc2_cur:g}%)": fm_res(round(ca2_t), is_ds), f"1 Người C2": fm_res(ca2_1, is_ds)})
        
    with t1: 
        st.dataframe(pd.DataFrame(res1_data), hide_index=True, use_container_width=True)
    with t2: 
        st.dataframe(pd.DataFrame(res2_data), hide_index=True, use_container_width=True)
