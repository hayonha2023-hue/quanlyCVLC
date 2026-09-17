"""Compact sign-in screen using native accessible form controls."""
from contextlib import contextmanager
import streamlit as st

LOGIN_CSS = """<style>
.stApp:has(.login-brand) {background:#f2f5f8;color:#203149;}
.stApp:has(.login-brand) [data-testid="stHeader"] {background:transparent;}
.stApp:has(.login-brand) [data-testid="stMainBlockContainer"] {max-width:480px;padding:8vh 24px 32px;}
.login-brand {display:flex;align-items:center;justify-content:center;gap:12px;margin:14px 0 30px;}
.login-mark {display:grid;place-items:center;width:44px;height:44px;border-radius:10px;background:#214e78;color:white;font-size:27px;font-weight:750;}
.login-brand strong {font-size:24px;letter-spacing:.03em;color:#203149;display:block;line-height:1.2;}
.login-brand small {font-size:12px;color:#66778a;display:block;margin-top:3px;}
.st-key-htcv_login {padding:30px;background:#fff;border:1px solid #dae2eb;border-radius:12px;box-shadow:0 8px 28px #20314908;}
.st-key-htcv_login [data-testid="stForm"] {padding:0;border:0;background:transparent;}
.login-heading h1 {font-size:25px!important;color:#203149!important;letter-spacing:-.02em;padding:0;margin:0 0 8px;}
.login-heading p {font-size:14px;color:#67778a!important;line-height:1.5;margin:0 0 14px;}
.st-key-htcv_login [data-testid="stWidgetLabel"] p {font-size:14px;font-weight:600;color:#203149;}
.st-key-htcv_login input {font-size:16px!important;background:#fff!important;color:#203149!important;}
.st-key-htcv_login [data-testid="stTextInputRootElement"],.st-key-htcv_login [data-baseweb="input"] {border:1px solid #cdd7e3!important;border-radius:7px;min-height:48px;background:#fff;}
.st-key-htcv_login [data-testid="stTextInputRootElement"]:focus-within {border-color:#296797!important;}
.st-key-htcv_login [data-testid="stFormSubmitButton"] button {width:100%;min-height:48px;border-radius:7px;background:#214e78;border:1px solid #214e78;margin-top:8px;}
.st-key-htcv_login [data-testid="stFormSubmitButton"] button p {color:white!important;font-weight:600;}
.st-key-htcv_login [data-testid="stExpander"] {background:transparent;border:0;border-top:1px solid #e5ebf1;border-radius:0;margin-top:14px;}
.st-key-htcv_login [data-testid="stExpander"] details {border:0;background:transparent;}
.st-key-htcv_login [data-testid="stExpander"] summary {padding-left:0;min-height:44px;}
.st-key-htcv_login [data-testid="stExpander"] p {font-size:13px;color:#67778a;}
.login-footer {text-align:center;font-size:12px;color:#738194;margin-top:22px;}
@media(max-width:600px) {
.stApp:has(.login-brand) [data-testid="stMainBlockContainer"] {padding:4rem 20px 24px;}
.st-key-htcv_login {padding:24px;}
.login-brand {margin:0 0 24px;}
}
</style>"""

@contextmanager
def login_form():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.markdown('<div class="login-brand"><span class="login-mark">H</span><div><strong>HTCV</strong><small>Quản lý nội bộ</small></div></div>', unsafe_allow_html=True)
    with st.container(key='htcv_login'):
        with st.form('login_form', border=False):
            st.markdown('<div class="login-heading"><h1>Đăng nhập</h1><p>Nhập tài khoản HTCV của bạn để tiếp tục.</p></div>', unsafe_allow_html=True)
            yield
        with st.expander('Hỗ trợ đăng nhập'):
            st.write('Dùng tài khoản đang sử dụng trên app HTCV. Nếu quên mật khẩu hoặc chưa có tài khoản, liên hệ quản trị viên chi nhánh.')
    st.markdown('<div class="login-footer">HTCV · Web 2.7.2</div>', unsafe_allow_html=True)
