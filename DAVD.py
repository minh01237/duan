import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Minh Quest 90 - Hệ thống tích điểm", page_icon="🎮", layout="wide")

# --- HỆ THỐNG CƠ SỞ DỮ LIỆU CỤC BỘ ---
DB_FILE = "nhat_ky_diem_xp.csv"


def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Ngày", "Morning_XP", "Day_XP", "Evening_XP", "Tổng_XP_Ngày"])


def save_data(ngay, m_xp, d_xp, e_xp, tong_xp):
    df = load_data()
    if ngay in df["Ngày"].values:
        df.loc[df["Ngày"] == ngay, ["Morning_XP", "Day_XP", "Evening_XP", "Tổng_XP_Ngày"]] = [m_xp, d_xp, e_xp, tong_xp]
    else:
        new_row = pd.DataFrame(
            {"Ngày": [ngay], "Morning_XP": [m_xp], "Day_XP": [d_xp], "Evening_XP": [e_xp], "Tổng_XP_Ngày": [tong_xp]})
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DB_FILE, index=False)


df_history = load_data()
tong_xp_tich_luy = df_history["Tổng_XP_Ngày"].sum() if not df_history.empty else 0

# ================= GIAO DIỆN CHÍNH =================
st.title("🎮 MINH QUEST 90 - DASHBOARD")

tab_daily, tab_history, tab_rewards = st.tabs(
    ["📝 Nhiệm Vụ Hằng Ngày", "📊 Lịch Sử Cho Bố Check", "🎁 Quy Tắc Đổi Thưởng"])

# ----------------------------------------------------------------------
# TAB 1: GIAO DIỆN NHIỆM VỤ THEO NGÀY
# ----------------------------------------------------------------------
with tab_daily:
    # --- TÍNH NĂNG MỚI: CHỌN NGÀY ---
    col_date, _ = st.columns([1, 2])  # Làm cho cái ô chọn ngày bé lại cho đẹp
    with col_date:
        # Tạo một bộ chọn lịch trên web, mặc định hiển thị ngày hôm nay
        ngay_chon = st.date_input("🗓️ Chọn ngày bạn muốn nhập/sửa điểm:", datetime.now())

    # Chuyển đổi định dạng ngày để hiển thị và lưu
    ngay_hien_tai = ngay_chon.strftime('%d/%m/%Y')
    db_date = ngay_chon.strftime('%Y-%m-%d')

    st.header(f"Nhiệm vụ ngày: {ngay_hien_tai}")
    st.markdown("**DAILY TARGET: ~55 XP • Realistic 70-80% là tốt • Off-day OK**")
    st.divider()

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

    morning_score = (10 if m1 else 0) + (5 if m2 else 0) + (5 if m3 else 0) + (5 if m4 else 0) + (10 if m5 else 0)
    day_score = (5 if d1 else 0) + (5 if d2 else 0) + (2 if d3 else 0) + (10 if d4 else 0)
    evening_score = (5 if e1 else 0) + (5 if e2 else 0) + (10 if e3 else 0) + (10 if e4 else 0) + (5 if e5 else 0)

    total_today = morning_score + day_score + evening_score

    st.divider()
    st.metric(label="Tổng điểm", value=f"{total_today} XP")

    if st.button("💾 Ghi Nhận Điểm Số", type="primary"):
        # Lưu vào file CSV với cái ngày cụ thể mà bạn đã chọn trên lịch
        save_data(db_date, morning_score, day_score, evening_score, total_today)
        st.success(f"🎉 Đã lưu thành công {total_today} XP cho ngày {ngay_hien_tai} vào két sắt!")

# ----------------------------------------------------------------------
# TAB 2 & TAB 3 GIỮ NGUYÊN
# ----------------------------------------------------------------------
with tab_history:
    st.header("📊 Nhật ký theo dõi hiệu suất")
    df_current = load_data()
    current_wallet = df_current["Tổng_XP_Ngày"].sum() if not df_current.empty else 0
    st.metric(label="💰 TỔNG QUỸ ĐIỂM HIỆN CÓ", value=f"{current_wallet} XP")

    if not df_current.empty:
        df_display = df_current.sort_values(by="Ngày", ascending=False).reset_index(drop=True)
        col_chart, col_table = st.columns([1.5, 1])
        with col_chart:
            st.write("**Biểu đồ tổng điểm các ngày gần đây**")
            st.bar_chart(data=df_current.set_index("Ngày")["Tổng_XP_Ngày"])
        with col_table:
            st.write("**Chi tiết điểm từng ngày**")
            st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu. Hãy hoàn thành nhiệm vụ và bấm Ghi nhận ở Tab 1 nhé!")

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