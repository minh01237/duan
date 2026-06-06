import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Minh Quest 90 - Hệ thống tích điểm", page_icon="🎮", layout="wide")

# --- HỆ THỐNG CƠ SỞ DỮ LIỆU CỤC BỘ (LOCAL DATABASE) ---
# Dữ liệu sẽ được lưu thẳng vào một file CSV trên máy tính của bạn
DB_FILE = "nhat_ky_diem_xp.csv"


def load_data():
    """Đọc dữ liệu lịch sử từ file CSV"""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Nếu file chưa tồn tại (chạy lần đầu), tạo bảng trống với các cột này
        return pd.DataFrame(columns=["Ngày", "Morning_XP", "Day_XP", "Evening_XP", "Tổng_XP_Ngày"])


def save_data(ngay, m_xp, d_xp, e_xp, tong_xp):
    """Lưu dữ liệu ngày mới vào file CSV"""
    df = load_data()

    # Kiểm tra xem ngày hôm nay đã có dữ liệu chưa. Nếu có rồi thì cập nhật lại (Ghi đè)
    if ngay in df["Ngày"].values:
        df.loc[df["Ngày"] == ngay, ["Morning_XP", "Day_XP", "Evening_XP", "Tổng_XP_Ngày"]] = [m_xp, d_xp, e_xp, tong_xp]
    else:
        # Nếu là ngày mới tinh thì thêm một dòng mới
        new_row = pd.DataFrame(
            {"Ngày": [ngay], "Morning_XP": [m_xp], "Day_XP": [d_xp], "Evening_XP": [e_xp], "Tổng_XP_Ngày": [tong_xp]})
        df = pd.concat([df, new_row], ignore_index=True)

    # Lưu lại vào máy tính
    df.to_csv(DB_FILE, index=False)


# --- TÍNH TOÁN QUỸ ĐIỂM HIỆN TẠI ---
df_history = load_data()
tong_xp_tich_luy = df_history["Tổng_XP_Ngày"].sum() if not df_history.empty else 0

# ================= GIAO DIỆN CHÍNH =================
st.title("🎮 MINH QUEST 90 - DASHBOARD")

# Tạo 3 tab chức năng
tab_daily, tab_history, tab_rewards = st.tabs(
    ["📝 Nhiệm Vụ Hằng Ngày", "📊 Lịch Sử Cho Bố Check", "🎁 Quy Tắc Đổi Thưởng"])

# ----------------------------------------------------------------------
# TAB 1: GIAO DIỆN NHIỆM VỤ THEO NGÀY (Chuẩn 100% theo ảnh thiết kế)
# ----------------------------------------------------------------------
with tab_daily:
    ngay_hien_tai = datetime.now().strftime('%d/%m/%Y')
    st.header(f"Hôm nay: {ngay_hien_tai}")
    st.markdown("**DAILY TARGET: ~55 XP • Realistic 70-80% là tốt • Off-day OK**")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🌅 MORNING")
        m1 = st.checkbox("Dậy trước 7h (+10 XP)")
        m2 = st.checkbox("Kéo xà 3x30s [video] (+5 XP)")
        m3 = st.checkbox("Nhảy dây 5p [video] (+5 XP)")
        m4 = st.checkbox("Sáng protein ≥15g [photo] (+5 XP)")
        m5 = st.checkbox("Chạy (+10 XP)")  # Chữ viết tay thêm vào

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
        e5 = st.checkbox("Thuốc (+5 XP)")  # Chữ viết tay thêm vào

    # Tính điểm tự động
    morning_score = (10 if m1 else 0) + (5 if m2 else 0) + (5 if m3 else 0) + (5 if m4 else 0) + (10 if m5 else 0)
    day_score = (5 if d1 else 0) + (5 if d2 else 0) + (2 if d3 else 0) + (10 if d4 else 0)
    evening_score = (5 if e1 else 0) + (5 if e2 else 0) + (10 if e3 else 0) + (10 if e4 else 0) + (5 if e5 else 0)

    total_today = morning_score + day_score + evening_score

    st.divider()
    st.metric(label="Tổng điểm hôm nay", value=f"{total_today} XP")

    # Nút lưu dữ liệu
    if st.button("💾 Ghi Nhận Điểm Số Hôm Nay", type="primary"):
        # Format ngày chuẩn để lưu database: Năm-Tháng-Ngày (để dễ sort)
        db_date = datetime.now().strftime('%Y-%m-%d')
        save_data(db_date, morning_score, day_score, evening_score, total_today)
        st.success("🎉 Đã lưu điểm thành công vào máy tính! Bố có thể sang tab Lịch sử để kiểm tra.")

# ----------------------------------------------------------------------
# TAB 2: LỊCH SỬ THỐNG KÊ (DÀNH CHO BỐ)
# ----------------------------------------------------------------------
with tab_history:
    st.header("📊 Nhật ký theo dõi hiệu suất")

    # Load lại dữ liệu mới nhất
    df_current = load_data()
    current_wallet = df_current["Tổng_XP_Ngày"].sum() if not df_current.empty else 0

    st.metric(label="💰 TỔNG QUỸ ĐIỂM HIỆN CÓ", value=f"{current_wallet} XP")

    if not df_current.empty:
        # Sắp xếp lịch sử ngày mới nhất lên đầu
        df_display = df_current.sort_values(by="Ngày", ascending=False).reset_index(drop=True)

        col_chart, col_table = st.columns([1.5, 1])

        with col_chart:
            st.write("**Biểu đồ tổng điểm các ngày gần đây**")
            # Vẽ biểu đồ cột để trực quan hóa
            st.bar_chart(data=df_current.set_index("Ngày")["Tổng_XP_Ngày"])

        with col_table:
            st.write("**Chi tiết điểm từng ngày**")
            st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu. Hãy hoàn thành nhiệm vụ và bấm Ghi nhận ở Tab 1 nhé!")

# ----------------------------------------------------------------------
# TAB 3: CỬA HÀNG ĐỔI THƯỞNG (Game Time +)
# ----------------------------------------------------------------------
with tab_rewards:
    st.header("🛒 Cửa hàng đổi thưởng (Game Time +)")
    st.info("⚠️ Ghi chú từ hệ thống: Chỉ khung 8h-12h cuối tuần. Không buổi tối.")

    rewards = [
        {"Phần thưởng": "Game +30p sáng T7/CN", "Giá (XP)": "50"},
        {"Phần thưởng": "Game +1h sáng cuối tuần", "Giá (XP)": "100"},
        {"Phần thưởng": "Marathon 2h sáng CN", "Giá (XP)": "200"},
        {"Phần thưởng": "Mua game mới", "Giá (XP)": "500 - 1500"}
    ]
    st.table(rewards)

    st.write(f"**Số dư hiện tại của bạn:** `{tong_xp_tich_luy} XP`")