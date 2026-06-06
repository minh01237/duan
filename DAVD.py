import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Cấu hình trang web
st.set_page_config(page_title="Minh Quest 90 - Hệ thống tích điểm", layout="wide")


# ================= HÀM KẾT NỐI GOOGLE SHEETS (THỰC TẾ) =================
@st.cache_resource
def ket_noi_sheet():
    try:
        # Khai báo quyền truy cập
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Đọc file key.json nằm cùng thư mục
        creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
        client = gspread.authorize(creds)
        sh = client.open("Điểm XP")
        # ⚠️ THAY TÊN FILE GOOGLE SHEET CỦA BẠN VÀO ĐÂY Y HỆT 100%
        # Ví dụ file trên Drive của bạn tên là "Minh Quest 90" thì điền vào đây
        sh = client.open("Điểm XP")

        # Lấy tab đầu tiên (Sheet1)
        return sh.sheet1
    except Exception as e:
        st.error(f"Lỗi kết nối Google Sheet: {e}")
        return None


# Gọi hàm kết nối
sheet = ket_noi_sheet()

# ================= GIAO DIỆN CHÍNH =================
st.title("🎮 MINH QUEST 90 - DASHBOARD")

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

    # Tính toán tổng điểm
    morning_score = (10 if m1 else 0) + (5 if m2 else 0) + (5 if m3 else 0) + (5 if m4 else 0) + (10 if m5 else 0)
    day_score = (5 if d1 else 0) + (5 if d2 else 0) + (2 if d3 else 0) + (10 if d4 else 0)
    evening_score = (5 if e1 else 0) + (5 if e2 else 0) + (10 if e3 else 0) + (10 if e4 else 0) + (5 if e5 else 0)
    total_today = morning_score + day_score + evening_score

    st.metric(label="Tổng điểm tạm tính hôm nay", value=f"{total_today} XP")

    # NÚT BẤM GỬI ĐIỂM THỰC TẾ
    if st.button("🚀 Gửi điểm lên Google Sheet"):
        if sheet is not None:
            try:
                ngay_hom_nay = datetime.now().strftime('%Y-%m-%d')

                # Tiến hành đẩy một dòng dữ liệu mới lên Google Sheet
                sheet.append_row([ngay_hom_nay, morning_score, day_score, evening_score, total_today])

                st.success(f"🎉 Đã gửi thành công {total_today} XP của ngày {ngay_hom_nay} lên Google Sheet của bố!")
            except Exception as e:
                st.error(f"Lỗi khi gửi dữ liệu: {e}")
        else:
            st.error("Chưa kết nối được với Google Sheet. Vui lòng kiểm tra lại tên file hoặc quyền chia sẻ.")

# ================= TAB 2 & 3 (HIỂN THỊ QUY TẮC) =================
with tab_history:
    st.header("📊 Nhật ký theo dõi")
    st.write("Sau khi kết nối ổn định, bạn có thể đọc ngược dữ liệu từ Sheet về đây để vẽ biểu đồ.")
    if sheet is not None:
        if st.button("🔄 Tải dữ liệu từ Google Sheet về xem"):
            data = sheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Sheet hiện tại đang trống, hãy thử gửi điểm trước nhé!")

with tab_rewards:
    st.header("🛒 Cửa hàng đổi thưởng (Game Time +)")
    st.info("⚠️ Khung giờ chơi: 8h-12h cuối tuần. Không chơi buổi tối.")
    rewards = [
        {"Phần thưởng": "Game +30p sáng T7/CN", "Giá": "50 XP"},
        {"Phần thưởng": "Game +1h sáng cuối tuần", "Giá": "100 XP"},
        {"Phần thưởng": "Marathon 2h sáng CN", "Giá": "200 XP"},
        {"Phần thưởng": "Mua game mới", "Giá": "500 - 1500 XP"}
    ]
    st.table(rewards)