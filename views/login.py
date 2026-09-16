"""Responsive login presentation; authentication stays in app.py."""
from contextlib import contextmanager

import streamlit as st


LOGIN_CSS = """
<style>
.stApp:has(.htcv-login-brandbar) {
    background:radial-gradient(ellipse at 12% 0%,#e9f0fb 0,transparent 48%),#f5f7fb;
    color:#182d4a;
}
.stApp:has(.htcv-login-brandbar) [data-testid="stHeader"] {background:transparent;}
.stApp:has(.htcv-login-brandbar) [data-testid="stMainBlockContainer"] {
    max-width:1136px;padding:3.5rem 2rem 2rem;
}
.htcv-login-brandbar {
    display:flex;align-items:center;justify-content:space-between;gap:16px;
    margin:0 0 24px;
}
.htcv-login-brand {display:flex;align-items:center;gap:12px;}
.htcv-login-monogram {
    display:grid;place-items:center;width:42px;height:42px;border-radius:13px;
    background:#173b64;color:white;font-size:25px;font-weight:800;
    box-shadow:0 4px 12px #173b6417;
}
.htcv-login-wordmark {font-size:23px;font-weight:800;letter-spacing:.035em;color:#19375b;}
.htcv-login-web {
    font-size:10px;letter-spacing:.12em;font-weight:700;padding:3px 7px;
    border:1px solid #d5deea;border-radius:5px;color:#5e7088;margin-left:7px;vertical-align:middle;
}
.htcv-login-brandnote {color:#62738a;font-size:13px;}
.st-key-htcv_login {
    background:#fff;border:1px solid #e3e9f2;border-radius:24px;
    box-shadow:0 24px 70px -28px #15355638;overflow:hidden;
}
.st-key-htcv_login [data-testid="stHorizontalBlock"] {gap:0;align-items:stretch;}
.st-key-htcv_login [data-testid="stColumn"] {min-width:0!important;}
.st-key-htcv_login [data-testid="stColumn"]:first-child > div {height:100%;}
.st-key-htcv_login [data-testid="stColumn"]:first-child [data-testid="stMarkdown"] {height:100%;}
.htcv-login-story {
    position:relative;overflow:hidden;box-sizing:border-box;min-height:590px;height:100%;
    padding:46px 40px 34px;display:flex;flex-direction:column;justify-content:space-between;
    background:radial-gradient(ellipse at 100% 0,#245a83 0,transparent 65%),#152e50;
}
.htcv-login-story::after {
    content:"";position:absolute;width:330px;height:330px;border:1px solid #ffffff0b;
    border-radius:50%;right:-205px;bottom:-155px;box-shadow:0 0 0 46px #ffffff03,0 0 0 92px #ffffff02;
    pointer-events:none;
}
.htcv-login-eyebrow {font-size:11px;font-weight:700;letter-spacing:.16em;color:#a6cce6;}
.htcv-login-story h2 {
    color:#fff!important;font-size:39px!important;font-weight:750;line-height:1.23;
    letter-spacing:-.035em;margin:22px 0 16px;padding:0;
}
.htcv-login-story h2 span {color:#acd7ef;}
.htcv-login-story .htcv-login-intro {
    color:#c0d0e2!important;font-size:15px;line-height:1.7;max-width:350px;margin:0;
}
.htcv-login-features {display:grid;gap:23px;margin:36px 0;}
.htcv-login-feature {display:flex;gap:14px;align-items:center;}
.htcv-login-feature-icon {
    display:grid;place-items:center;flex:0 0 42px;height:42px;
    background:#ffffff0a;border:1px solid #ffffff17;border-radius:12px;color:#b6d9f1;
}
.htcv-login-feature-icon svg {width:20px;height:20px;}
.htcv-login-feature strong {display:block;font-size:14px;line-height:1.5;color:#f2f7fd;font-weight:600;}
.htcv-login-feature small {display:block;color:#b4c8df;font-size:12px;line-height:1.6;margin-top:3px;}
.htcv-login-story-footer {
    border-top:1px solid #ffffff1c;padding-top:20px;font-size:12px;color:#adc3da;
    display:flex;align-items:center;gap:8px;
}
.htcv-login-story-footer svg {width:15px;height:15px;flex:none;}
.st-key-htcv_login [data-testid="stColumn"]:nth-child(2) {padding:42px 40px 32px;align-self:center;}
.st-key-htcv_login [data-testid="stForm"] {
    background:transparent;padding:0;border:0;border-radius:0;
}
.st-key-htcv_login [data-testid="stForm"] > [data-testid="stVerticalBlock"] {gap:20px;}
.htcv-login-heading {margin:0 0 9px;}
.htcv-login-heading .htcv-login-kicker {
    color:#276aa6;font-size:11px;letter-spacing:.14em;font-weight:700;margin:0 0 12px;
}
.htcv-login-heading h1 {
    font-size:28px!important;line-height:1.35;letter-spacing:-.035em;
    color:#193451!important;margin:0 0 10px;padding:0;font-weight:750;
}
.htcv-login-heading p {font-size:14px;color:#67778d!important;line-height:1.7;margin:0;}
.st-key-htcv_login [data-testid="stWidgetLabel"] p {font-size:13px;font-weight:600;color:#30465f;}
.st-key-htcv_login [data-baseweb="input"] {
    min-height:52px;background:#f8fafc;border:1px solid #d8e1ed!important;
    border-radius:11px;transition:border-color .15s,box-shadow .15s;
}
.st-key-htcv_login [data-baseweb="input"]:focus-within {border-color:#367bbe!important;box-shadow:0 0 0 3px #367bbe15;}
.st-key-htcv_login input {font-size:16px!important;background:transparent!important;color:#203c5c!important;}
.st-key-htcv_login input::placeholder {color:#8493a5;opacity:1;}
.st-key-htcv_login [data-baseweb="input"] button {min-width:44px;color:#637991;}
.st-key-htcv_login [data-testid="stFormSubmitButton"] {margin-top:4px;}
.st-key-htcv_login [data-testid="stFormSubmitButton"] button {
    min-height:52px;border-radius:11px;background:#1f5b99;border:1px solid #1f5b99;
    box-shadow:0 5px 12px #1f5b991c;transition:background .15s,box-shadow .15s;
}
.st-key-htcv_login [data-testid="stFormSubmitButton"] button:hover {background:#174b80;border-color:#174b80;box-shadow:0 7px 16px #1f5b9926;}
.st-key-htcv_login [data-testid="stFormSubmitButton"] button p {color:#fff!important;font-size:15px;font-weight:650;}
.st-key-htcv_login [data-testid="stExpander"] {border:0;border-top:1px solid #edf1f6;border-radius:0;background:transparent;margin-top:8px;}
.st-key-htcv_login [data-testid="stExpander"] summary {min-height:46px;padding:10px 0;}
.st-key-htcv_login [data-testid="stExpander"] summary p {font-size:13px;color:#5e728c;}
.st-key-htcv_login [data-testid="stExpanderDetails"] {padding:0 0 8px;}
.st-key-htcv_login [data-testid="stExpanderDetails"] p {font-size:13px;line-height:1.7;color:#5e728c;}
.st-key-htcv_login [data-testid="stAlert"] p {font-size:13px;}
.htcv-login-account-note {color:#7a8799;font-size:12px;text-align:center;line-height:1.6;margin-top:2px;}
.htcv-login-footer {text-align:center;color:#7b899b;font-size:12px;margin-top:22px;line-height:1.7;}
@media(max-width:900px) {
    .htcv-login-story {padding:38px 28px;}
    .htcv-login-story h2 {font-size:33px!important;}
    .st-key-htcv_login [data-testid="stColumn"]:nth-child(2) {padding:32px 28px;}
}
@media(max-width:760px) {
    .stApp:has(.htcv-login-brandbar) [data-testid="stMainBlockContainer"] {max-width:500px;padding:2.5rem 1.15rem 1.5rem;}
    .htcv-login-brandbar {margin-bottom:24px;}
    .htcv-login-brandnote {display:none;}
    .st-key-htcv_login {border-radius:20px;box-shadow:0 16px 40px -25px #15355630;}
    .st-key-htcv_login [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
    .st-key-htcv_login [data-testid="stColumn"]:first-child {display:none;}
    .st-key-htcv_login [data-testid="stColumn"]:nth-child(2) {width:100%!important;flex:1 1 100%!important;padding:30px 24px 24px;}
    .htcv-login-heading h1 {font-size:26px!important;}
    .htcv-login-heading p {font-size:13px;}
    .htcv-login-footer {max-width:290px;margin:20px auto 0;}
}
@media(prefers-reduced-motion:reduce) {.st-key-htcv_login * {transition:none!important;}}
</style>
"""


def _icon(paths):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{paths}</svg>')


@contextmanager
def login_form():
    """Place the existing native Streamlit fields inside a responsive shell."""
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.markdown('''<div class="htcv-login-brandbar">
<div class="htcv-login-brand"><div class="htcv-login-monogram" aria-hidden="true">H</div>
<div class="htcv-login-wordmark">HTCV<span class="htcv-login-web">WEB</span></div></div>
<div class="htcv-login-brandnote">Không gian quản lý công việc</div></div>''', unsafe_allow_html=True)

    calendar = _icon('<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M16 3v4M8 3v4M3 11h18M8 16l2 2 5-4"/>')
    chart = _icon('<path d="M4 4v16h16M9 15v-4M14 15V7M19 15v-6"/>')
    data = _icon('<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M3 10h18M10 10v10"/>')
    account = _icon('<rect x="5" y="3" width="14" height="18" rx="3"/><path d="M10 17h4"/>')

    with st.container(key="htcv_login"):
        story, panel = st.columns([1.04, 1], gap="small")
        with story:
            st.markdown(f'''<section class="htcv-login-story" aria-label="Không gian làm việc HTCV">
<div><div class="htcv-login-eyebrow">KẾT NỐI CÔNG VIỆC MỖI NGÀY</div>
<h2>Mọi công việc.<br><span>Một không gian.</span></h2>
<p class="htcv-login-intro">Theo dõi công việc và phối hợp cùng đội ngũ, ngay trong một nơi quen thuộc.</p></div>
<div class="htcv-login-features">
<div class="htcv-login-feature"><div class="htcv-login-feature-icon">{calendar}</div><div><strong>Lịch &amp; ca làm</strong><small>Nắm rõ lịch làm việc của bạn và đội ngũ.</small></div></div>
<div class="htcv-login-feature"><div class="htcv-login-feature-icon">{chart}</div><div><strong>KPI &amp; kết quả</strong><small>Theo dõi chỉ tiêu, chủ động tiến độ.</small></div></div>
<div class="htcv-login-feature"><div class="htcv-login-feature-icon">{data}</div><div><strong>Dữ liệu công việc</strong><small>Tra cứu thuận tiện, xử lý tập trung.</small></div></div>
</div><div class="htcv-login-story-footer">{account}<span>Một tài khoản, sử dụng trên app và web.</span></div>
</section>''', unsafe_allow_html=True)
        with panel:
            with st.form("login_form", border=False):
                st.markdown('''<div class="htcv-login-heading">
<div class="htcv-login-kicker">ĐĂNG NHẬP HTCV</div>
<h1>Chào mừng trở lại</h1>
<p>Đăng nhập để bắt đầu ngày làm việc của bạn.</p>
</div>''', unsafe_allow_html=True)
                yield
            with st.expander("Bạn cần hỗ trợ đăng nhập?", expanded=False):
                st.write("Sử dụng tài khoản và mật khẩu đang dùng trên app HTCV. "
                         "Nếu quên mật khẩu hoặc chưa có tài khoản, hãy liên hệ quản trị viên "
                         "của chi nhánh để được hỗ trợ.")
            st.markdown('<div class="htcv-login-account-note">Dành cho nhân viên và quản trị viên HTCV</div>', unsafe_allow_html=True)
    st.markdown('<div class="htcv-login-footer">HTCV · Công việc kết nối, đội ngũ đồng hành.</div>', unsafe_allow_html=True)
