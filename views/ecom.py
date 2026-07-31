import streamlit as st

def render_ecom():
    # Sử dụng thẻ div HTML để tạo khối giao diện
    st.markdown("""
    <div class='html-card'>
        <h3 style='color: #0D6EFD; margin-top: 0px; margin-bottom: 5px;'>🛒 QUẢN LÝ LỊCH ECOM</h3>
        <p style='color: #6c757d; margin-top: 0px;'>Khu vực chia ca Sáng/Chiều cho đội Ecom</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<b>Ca Sáng</b>", unsafe_allow_html=True)
        st.text_input("Nhập tên nhân viên ca sáng", key="ecom_sang")
    with col2:
        st.markdown("<b>Ca Chiều</b>", unsafe_allow_html=True)
        st.text_input("Nhập tên nhân viên ca chiều", key="ecom_chieu")
        
    st.button("💾 LƯU LỊCH ECOM", type="primary")
