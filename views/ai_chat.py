import streamlit as st
import requests

def render_ai_chat():
    st.markdown("<h3 style='margin-top: 0px; margin-bottom: 25px; font-weight:800;'>🤖 Trợ Lý AI Tư Vấn Y Khoa</h3>", unsafe_allow_html=True)
    
    # Khởi tạo tin nhắn chào mừng nếu chưa có
    if "vaccine_chat" not in st.session_state:
        st.session_state.vaccine_chat = [{"role": "assistant", "content": "Chào bạn! Tôi là Bác sĩ và Dược sĩ lâm sàng cấp cao. Bạn cần hỗ trợ phân tích ca bệnh khó, thông tin chi tiết về thuốc hay phác đồ vắc xin?"}]

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.vaccine_chat:
            with st.chat_message(msg["role"]): 
                st.markdown(msg["content"])

    # Xử lý khi người dùng nhập tin nhắn
    if prompt := st.chat_input("Nhập câu hỏi về thuốc, vắc xin hoặc ca lâm sàng..."):
        st.session_state.vaccine_chat.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"): 
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("⏳ Đang phân tích dữ liệu y khoa...")
                
                # Lấy API Key từ Database tổng
                full_db = st.session_state.get("db", {})
                k_list = full_db.get("settings", {}).get("api_keys", [])
                
                if not k_list: 
                    reply = "❌ Hệ thống chưa cấu hình API Key. Vui lòng báo Admin cập nhật trong mục Cài đặt."
                else:
                    # Thiết lập Prompt chỉ đạo AI
                    messages = [{"role": "system", "content": "Bạn là Bác sĩ và Dược sĩ lâm sàng cấp cao tại Việt Nam, chuyên gia hàng đầu về Thuốc và Vắc xin. Nhiệm vụ của bạn là giải đáp chuyên sâu các câu hỏi y khoa, bao gồm cả những ca lâm sàng khó, tương tác thuốc phức tạp. Yêu cầu: Văn phong chuyên nghiệp, đanh thép, bám sát y học thực chứng. Phân tích rõ ràng về cơ chế, dược động học, tương tác thuốc, chống chỉ định, và phác đồ. TUYỆT ĐỐI KHÔNG dùng văn phong dịch máy. Bắt buộc dùng đúng thuật ngữ y khoa/dược khoa chuẩn Việt Nam. Trình bày logic, chia mục thật rõ ràng. TUYỆT ĐỐI KHÔNG dùng emoji."}]
                    
                    # Nạp lịch sử chat (chỉ lấy 8 tin nhắn gần nhất để tiết kiệm token)
                    for m in st.session_state.vaccine_chat[-8:]:
                        if m["role"] == "user": 
                            messages.append({"role": "user", "content": m["content"]})
                        elif m["role"] == "assistant" and "Chào bạn! Tôi là" not in m["content"] and "⏳" not in m["content"] and "❌" not in m["content"]:
                            messages.append({"role": "assistant", "content": m["content"]})
                            
                    payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.3}
                    suc = False
                    reply = "❌ Máy chủ AI đang bận. Vui lòng thử lại sau."
                    
                    # Quét qua danh sách API Key, cái nào sống thì dùng
                    for k in k_list:
                        if suc: break
                        try:
                            headers = {"Authorization": f"Bearer {k}", "Content-Type": "application/json"}
                            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
                            if r.status_code == 200:
                                reply = "".join(c for c in r.json()['choices'][0]['message']['content'] if ord(c)<=0xFFFF)
                                suc = True
                                break
                            else:
                                reply = f"❌ LỖI API ({r.status_code}): {r.text}"
                        except Exception as e: 
                            reply = f"❌ LỖI MẠNG: {str(e)}"
                            continue
                                
                placeholder.markdown(reply)
                st.session_state.vaccine_chat.append({"role": "assistant", "content": reply})

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Làm Mới Cuộc Trò Chuyện", type="secondary", use_container_width=True):
        st.session_state.vaccine_chat = [{"role": "assistant", "content": "Chào bạn! Tôi là Bác sĩ chuyên gia tư vấn Vắc xin. Bạn cần hỗ trợ thông tin gì về các loại vắc xin, phác đồ tiêm hay chống chỉ định không?"}]
        st.rerun()
