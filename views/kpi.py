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
    except Exception as e:
        st.error(f"Lỗi đồng bộ: {e}")

def render_kpi():
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>📈 Bảng Theo Dõi KPI & Cấn Trừ Nợ</h3>", unsafe_allow_html=True)
    
    # Mã JavaScript giúp tự động nảy dấu chấm khi gõ tiền (VD: 1.000.000)
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

    full_db = st.session_state.get("db", {})
    shop_id = st.session_state.get("current_shop", "Shop Chính (Mặc định)")
    
    users = full_db.get("users", {})
    # Lọc danh sách nhân viên thuộc nhánh hiện tại (bỏ qua Admin)
    shop_users = [u for u, info in users.items() if info.get("shop_id", "Shop Chính (Mặc định)") == shop_id and u.lower() != "admin"]
    
    kpi_data = full_db.get("kpi", {}).get(shop_id, {})
    
    # Kiểm tra quyền
    current_user = st.session_state.get("current_user", "")
    u_info = users.get(current_user, {})
    user_role = u_info.get("role", "")
    edit_perms = u_info.get("edit_permissions", [])
    
    can_edit = current_user.lower() == "admin" or user_role == "admin" or "SỬA SỐ KPI" in edit_perms

    if can_edit:
        with st.expander("⚙️ NHẬP LIỆU & CHỈNH SỬA KPI NHÂN VIÊN", expanded=True):
            selected_user = st.selectbox("👤 Chọn Nhân Viên", shop_users)
            if selected_user:
                u_kpi = kpi_data.get(selected_user, {})
                c1, c2, c3 = st.columns(3)
                
                target = c1.text_input("🎯 Mục tiêu tháng này", value=fmt_dot(u_kpi.get("target", 0)), placeholder="Mục tiêu...")
                debt = c2.text_input("⚠️ Nợ tháng trước", value=fmt_dot(u_kpi.get("debt", 0)), placeholder="Nợ...")
                achieved = c3.text_input("✅ Đã đạt (Thực tế)", value=fmt_dot(u_kpi.get("achieved", 0)), placeholder="Đã đạt...")
                
                if st.button("💾 LƯU DỮ LIỆU KPI", type="primary", use_container_width=True):
                    t_val, d_val, a_val = s_float(target), s_float(debt), s_float(achieved)
                    update_kpi_db(shop_id, selected_user, {"target": t_val, "debt": d_val, "achieved": a_val})
                    
                    # Cập nhật RAM cục bộ để load lại ngay
                    if "kpi" not in st.session_state.db: st.session_state.db["kpi"] = {}
                    if shop_id not in st.session_state.db["kpi"]: st.session_state.db["kpi"][shop_id] = {}
                    st.session_state.db["kpi"][shop_id][selected_user] = {"target": t_val, "debt": d_val, "achieved": a_val}
                    
                    st.success(f"Đã lưu KPI cho nhân viên {selected_user.upper()}!"); time.sleep(1); st.rerun()

    st.markdown("<br><b>📊 BẢNG TỔNG HỢP KPI & NỢ TỒN ĐỌNG (CẬP NHẬT THEO THỜI GIAN THỰC)</b>", unsafe_allow_html=True)
    
    df_list = []
    for u in shop_users:
        u_kpi = kpi_data.get(u, {})
        t_val = s_float(u_kpi.get("target", 0))
        d_val = s_float(u_kpi.get("debt", 0))
        a_val = s_float(u_kpi.get("achieved", 0))
        
        # Gom chung Nợ + Mục tiêu mới thành Tổng Mục Tiêu
        total_target = t_val + d_val
        
        # Tính phần nợ tháng trước còn thiếu để CÔNG KHAI (Cho thấy nhân viên đã trả hết nợ cũ chưa)
        missing_last = d_val - a_val if d_val > a_val else 0
        
        # Tính tổng còn thiếu để gối sang tháng sau
        total_missing = total_target - a_val if total_target > a_val else 0
        
        df_list.append({
            "👤 Nhân Viên": u.upper(),
            "🎯 Mục Tiêu (Tháng)": fmt_dot(t_val),
            "⚠️ Nợ (Tháng Trước)": fmt_dot(d_val),
            "📌 TỔNG MỤC TIÊU": fmt_dot(total_target),
            "✅ Đã Đạt": fmt_dot(a_val),
            "🔥 Còn Thiếu Nợ Cũ": fmt_dot(missing_last),
            "🛑 TỔNG CÒN THIẾU": fmt_dot(total_missing)
        })
        
    if df_list:
        df = pd.DataFrame(df_list)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("Chưa có nhân viên nào trong danh sách. Vui lòng duyệt hoặc phân bổ nhân viên vào nhánh này.")
