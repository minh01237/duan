import streamlit as st
import pandas as pd
from datetime import datetime

# Cấu hình trang web
st.set_page_config(page_title="Minh Quest 90 - Hệ thống tích điểm", layout="wide")

# --- MÔ PHỎNG DỮ LIỆU (Thay bằng kết nối Google Sheets thực tế của bạn) ---
# Trong thực tế, bạn sẽ dùng gspread để đọc/ghi các dataframe này trực tiếp từ Google Sheet
if 'history_db' not in st.session_state:
    st.session_state.history_db = pd.DataFrame([
        {"Ngay": "2026-06-04", "Morning_XP": 25, "Day_XP": 19, "Evening_XP": 30, "Tong_XP": 74},
        {"Ngay": "2026-06-05", "Morning_XP": 15, "Day_XP": 14, "Evening_XP": 20, "Tong_XP": 49},
    ])
if 'tong_xp_hiendai' not in st.session_state:
    st.session_state.tong_xp_hiendai = 123  # Giả lập điểm tích lũy hiện tại đang có

# --- GIAO DIỆN CHÍNH ---
st.title("🎮 MINH QUEST 90 - DASHBOARD")

# Tạo các Tab chức năng trên Web
tab_daily, tab_history, tab_rewards = st.tabs(
    ["📝 Nhiệm Vụ Hằng Ngày", "📊 Lịch Sử Cho Bố Check", "🎁 Quy Tắc Đổi Thưởng"])

# ================= TAB 1: NHIỆM VỤ HẰNG NGÀY =================
with tab_daily:
    st.header(f"Hôm nay: {datetime.now().strftime('%d/%m/%Y')}")
    st.write("Target hằng ngày: ~55 XP | Realistic 70-80% là tốt")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🌅 MORNING")
        m1 = st.checkbox("Dậy trước 7h (+10 XP)")
        m2 = st.checkbox("Kéo xà 3x30s [video] (+5 XP)")
        m3 = st.checkbox("Nhảy dây 5p [video] (+5 XP)")
        m4 = st.checkbox("Sáng protein ≥15g [photo] (+5 XP)")
        m5 = st.checkbox("Chạy (+10 XP)")

    with col2:
        st.subheader("☀️ DAY")
        d1 = st.checkbox("Uống ≥2L nước (+5 XP)")
        d2 = st.checkbox("Trưa protein [photo] (+5 XP)")
        d3 = st.checkbox("Đọc sách 15p (+2 XP)")
        d4 = st.checkbox("Ngoài trời 30p+ (+10 XP)")

    with col3:
        st.subheader("🌙 EVENING")
        e1 = st.checkbox("Tối protein [photo] (+5 XP)")
        e2 = st.checkbox("Stretching 10p [video] (+5 XP)")
        e3 = st.checkbox("Giao điện thoại 21h (+10 XP)")
        e4 = st.checkbox("Tắt đèn 22h (+10 XP)")
        e5 = st.checkbox("Thuốc (+5 XP)")

    # Tính toán điểm tạm tính dựa trên các checkbox được tích
    morning_score = (10 if m1 else 0) + (5 if m2 else 0) + (5 if m3 else 0) + (5 if m4 else 0) + (10 if m5 else 0)
    day_score = (5 if d1 else 0) + (5 if d2 else 0) + (2 if d3 else 0) + (10 if d4 else 0)
    evening_score = (5 if e1 else 0) + (5 if e2 else 0) + (10 if e3 else 0) + (10 if e4 else 0) + (5 if e5 else 0)
    total_today = morning_score + day_score + evening_score

    st.metric(label="Tổng điểm tạm tính hôm nay", value=f"{total_today} XP")

    if st.button("🚀 Gửi điểm lên Google Sheet"):
        # Logic cập nhật dữ liệu
        new_data = {
            "Ngay": datetime.now().strftime('%Y-%m-%d'),
            "Morning_XP": morning_score,
            "Day_XP": day_score,
            "Evening_XP": evening_score,
            "Tong_XP": total_today
        }
        st.session_state.history_db = pd.concat([st.session_state.history_db, pd.DataFrame([new_data])],
                                                ignore_index=True)
        st.session_state.tong_xp_hiendai += total_today
        st.success("Đã đồng bộ thành công lên Google Sheet cho bố kiểm tra!")

# ================= TAB 2: LỊCH SỬ CHO BỐ CHECK =================
with tab_history:
    st.header("📊 Nhật ký theo dõi hiệu suất")

    # Hiển thị tổng số điểm hiện tại
    st.普及 = st.metric(label="💰 Quỹ điểm XP hiện tại đang có để đổi thưởng",
                        value=f"{st.session_state.tong_xp_hiendai} XP")

    # Bộ lọc thời gian cho bố dễ xem
    filter_option = st.selectbox("Chọn chế độ xem lịch sử", ["Theo Ngày (Chi tiết)", "Theo Tuần", "Theo Tháng"])

    df_display = st.session_state.history_db.copy()
    df_display['Ngay'] = pd.to_datetime(df_display['Ngay'])

    if filter_option == "Theo Ngày (Chi tiết)":
        st.dataframe(df_display, use_container_width=True)

    elif filter_option == "Theo Tuần":
        # Gom nhóm dữ liệu theo tuần
        df_display['Tuần'] = df_display['Ngay'].dt.to_period('W').astype(str)
        df_weekly = df_display.groupby('Tuần')['Tong_XP'].sum().reset_index()
        st.bar_chart(data=df_weekly, x='Tuần', y='Tong_XP')
        st.dataframe(df_weekly, use_container_width=True)

    elif filter_option == "Theo Tháng":
        # Gom nhóm dữ liệu theo tháng
        df_display['Tháng'] = df_display['Ngay'].dt.to_period('M').astype(str)
        df_monthly = df_display.groupby('Tháng')['Tong_XP'].sum().reset_index()
        st.bar_chart(data=df_monthly, x='Tháng', y='Tong_XP')
        st.dataframe(df_monthly, use_container_width=True)

# ================= TAB 3: QUY TẮC ĐỔI THƯỞNG =================
with tab_rewards:
    st.header("🛒 Cửa hàng đổi thưởng (Game Time +)")
    st.info("⚠️ Lưu ý từ bố: Chỉ áp dụng khung giờ 8h-12h cuối tuần. Không chơi buổi tối.")

    rewards = [
        {"Phần thưởng": "Game +30p sáng T7/CN", "Giá": "50 XP"},
        {"Phần thưởng": "Game +1h sáng cuối tuần", "Giá": "100 XP"},
        {"Phần thưởng": "Marathon 2h sáng CN", "Giá": "200 XP"},
        {"Phần thưởng": "Mua game mới", "Giá": "500 - 1500 XP"}
    ]
    st.table(rewards)