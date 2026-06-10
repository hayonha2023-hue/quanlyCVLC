# ==========================================
# CẤU HÌNH GIAO DIỆN & TÀNG HÌNH NÚT THỪA
# ==========================================
st.set_page_config(page_title="HTCV System", page_icon="⚡", layout="wide")

# BÙA CHÚ CSS QUÉT SẠCH MỌI ICON TRÔI NỔI
custom_css = """
<style>
    /* Xóa Header và Footer mặc định */
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    
    /* Xóa thanh công cụ và nút Deploy */
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    
    /* Xóa cụm Manage App và Viewer Badge của Streamlit Cloud */
    .viewerBadge_container {display: none !important;}
    .viewerBadge_link {display: none !important;}
    [data-testid="manage-app-button"] {display: none !important;}
    
    /* LƯỚI BẮT CÁC ICON NỔI NGOÀI LUỒNG TRÊN MOBILE */
    div[style*="position: fixed"][style*="bottom:"] {display: none !important;}
    div[style*="position: fixed"][style*="right:"] {display: none !important;}
    iframe {display: none !important;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
