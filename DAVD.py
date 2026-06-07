import streamlit as st
import pandas as pd
import datetime
import os

# Cấu hình file CSV
CSV_FILE = "nhat_ky_diem_xp.csv"


# Khởi tạo file CSV nếu chưa có
def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Ngày", "Morning_XP", "Day_XP", "Evening_XP", "Tổng_XP_Ngày", "Chi_Tiet_Nhiem_Vu"])
        df.to_csv(CSV_FILE, index=False)
    else:
        # Tương thích với file cũ chưa có cột Chi_Tiet_Nhiem_Vu
        df = pd.read_csv(CSV_FILE)
        if "Chi_Tiet_Nhiem_Vu" not in df.columns:
            df["Chi_Tiet_Nhiem_Vu"] = ""
            df.to_csv(CSV_FILE, index=False)


# Hàm load dữ liệu
def load_data():
    df = pd.read_csv(CSV_FILE)
    if "Chi_Tiet_Nhiem_Vu" not in df.columns:
        df["Chi_Tiet_Nhiem_Vu"] = ""
    return df


# Hàm lưu dữ liệu
def save_data(date, morning_xp, day_xp, evening_xp, tasks_done):
    df = load_data()
    total_xp = morning_xp + day_xp + evening_xp
    date_str = str(date)
    tasks_str = ", ".join(tasks_done)

    # Cập nhật nếu đã có, ngược lại thêm mới
    if date_str in df["Ngày"].values:
        df.loc[df["Ngày"] == date_str, ["Morning_XP", "Day_XP", "Evening_XP", "Tổng_XP_Ngày", "Chi_Tiet_Nhiem_Vu"]] = [
            morning_xp, day_xp, evening_xp, total_xp, tasks_str]
    else:
        new_row = {"Ngày": date_str, "Morning_XP": morning_xp, "Day_XP": day_xp, "Evening_XP": evening_xp,
                   "Tổng_XP_Ngày": total_xp, "Chi_Tiet_Nhiem_Vu": tasks_str}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(CSV_FILE, index=False)


# Hàm tính tổng XP tuần hiện tại
def get_current_week_xp():
    df = load_data()
    today = datetime.date.today()
    current_year, current_week, _ = today.isocalendar()

    # Lọc dữ liệu theo tuần
    total_week_xp = 0
    for index, row in df.iterrows():
        try:
            row_date = datetime.datetime.strptime(row["Ngày"], "%Y-%m-%d").date()
            year, week, _ = row_date.isocalendar()
            if year == current_year and week == current_week:
                total_week_xp += row["Tổng_XP_Ngày"]
        except ValueError:
            pass  # Bỏ qua nếu lỗi định dạng ngày
    return total_week_xp


# --- Hệ thống Đăng nhập ---
def login():
    st.title("🔐 Đăng nhập Minh Quest 90")
    username = st.selectbox("Chọn tài khoản", ["minh", "bo"])
    password = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if username == "minh" and password == "minh123":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "admin"
            st.rerun()
        elif username == "bo" and password == "bo123":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "viewer"
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")


def logout():
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.rerun()


# --- Main App ---
def main():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login()
        return
    init_csv()
    role = st.session_state["role"]
    is_admin = role == "admin"
    # Sidebar
    with st.sidebar:
        st.header(f"👤 Chào mừng, {role.capitalize()}!")
        if st.button("Đăng xuất"):
            logout()

        st.markdown("---")
        st.subheader("Tiến trình Tuần này")
        week_xp = get_current_week_xp()
        st.metric("Tổng XP Tuần", f"{week_xp} XP")

        target_week = 375
        progress_val = min(week_xp / target_week, 1.0)
        st.progress(progress_val)
        st.caption(f"Mục tiêu chuẩn: {target_week} XP")
    # Layout chính
    st.title("🚀 Minh Quest 90")

    tab1, tab2, tab3 = st.tabs(["Nhiệm vụ (Daily Quest)", "Lịch sử (Analytics)", "Hệ thống Đổi thưởng"])

    # TAB 1: Nhiệm vụ
    with tab1:
        st.header("📝 Ghi nhận thói quen hàng ngày")
        st.info("DAILY TARGET: ~55 XP • Realistic 70-80% là tốt • Off-day OK")

        # Admin hay Viewer đều chọn được ngày để xem
        selected_date = st.date_input("Chọn ngày", datetime.date.today())

        # Lấy dữ liệu cũ nếu có
        df = load_data()
        date_str = str(selected_date)
        old_data = df[df["Ngày"] == date_str]

        saved_tasks_list = []
        if not old_data.empty:
            st.write(f"**Dữ liệu đã lưu cho ngày {date_str}:**")
            st.write(
                f"- Morning: {old_data.iloc[0]['Morning_XP']} XP | Day: {old_data.iloc[0]['Day_XP']} XP | Evening: {old_data.iloc[0]['Evening_XP']} XP")
            st.write(f"- Tổng: **{old_data.iloc[0]['Tổng_XP_Ngày']} XP**")

            chi_tiet = old_data.iloc[0].get('Chi_Tiet_Nhiem_Vu', '')
            if pd.notna(chi_tiet) and str(chi_tiet).strip():
                st.write(f"- **Các mục đã hoàn thành:** {chi_tiet}")
                saved_tasks_list = [x.strip() for x in str(chi_tiet).split(',')]

            if is_admin:
                st.warning("Việc thay đổi tích chọn và nhấn Lưu dưới đây sẽ GHI ĐÈ dữ liệu của ngày này.")

        col1, col2, col3 = st.columns(3)
        morning_xp = 0
        day_xp = 0
        evening_xp = 0
        tasks_done = []

        with col1:
            st.subheader("🌅 Morning")
            if st.checkbox("Dậy trước 7h (+10)", value=("Dậy trước 7h" in saved_tasks_list), disabled=not is_admin):
                morning_xp += 10
                tasks_done.append("Dậy trước 7h")
            if st.checkbox("Kéo xà 3x30s (+5)", value=("Kéo xà" in saved_tasks_list), disabled=not is_admin):
                morning_xp += 5
                tasks_done.append("Kéo xà")
            if st.checkbox("Nhảy dây 5p (+5)", value=("Nhảy dây" in saved_tasks_list), disabled=not is_admin):
                morning_xp += 5
                tasks_done.append("Nhảy dây")
            if st.checkbox("Sáng protein ≥15g (+5)", value=("Sáng protein" in saved_tasks_list), disabled=not is_admin):
                morning_xp += 5
                tasks_done.append("Sáng protein")
            if st.checkbox("Chạy (+10)", value=("Chạy" in saved_tasks_list), disabled=not is_admin):
                morning_xp += 10
                tasks_done.append("Chạy")

        with col2:
            st.subheader("☀️ Day")
            if st.checkbox("Uống ≥2L nước (+5)", value=("Uống nước" in saved_tasks_list), disabled=not is_admin):
                day_xp += 5
                tasks_done.append("Uống nước")
            if st.checkbox("Trưa protein (+5)", value=("Trưa protein" in saved_tasks_list), disabled=not is_admin):
                day_xp += 5
                tasks_done.append("Trưa protein")
            if st.checkbox("Đọc sách 15p (+2)", value=("Đọc sách" in saved_tasks_list), disabled=not is_admin):
                day_xp += 2
                tasks_done.append("Đọc sách")
            if st.checkbox("Ngoài trời 30p+ (+10)", value=("Ngoài trời" in saved_tasks_list), disabled=not is_admin):
                day_xp += 10
                tasks_done.append("Ngoài trời")

        with col3:
            st.subheader("🌙 Evening")
            if st.checkbox("Tối protein (+5)", value=("Tối protein" in saved_tasks_list), disabled=not is_admin):
                evening_xp += 5
                tasks_done.append("Tối protein")
            if st.checkbox("Stretching 10p (+5)", value=("Stretching" in saved_tasks_list), disabled=not is_admin):
                evening_xp += 5
                tasks_done.append("Stretching")
            if st.checkbox("Giao ĐT 21h (+10)", value=("Giao ĐT 21h" in saved_tasks_list), disabled=not is_admin):
                evening_xp += 10
                tasks_done.append("Giao ĐT 21h")
            if st.checkbox("Tắt đèn 22h (+10)", value=("Tắt đèn 22h" in saved_tasks_list), disabled=not is_admin):
                evening_xp += 10
                tasks_done.append("Tắt đèn 22h")
            if st.checkbox("Thuốc (+5)", value=("Thuốc" in saved_tasks_list), disabled=not is_admin):
                evening_xp += 5
                tasks_done.append("Thuốc")

        st.markdown("---")
        total_xp_today = morning_xp + day_xp + evening_xp
        st.subheader(f"Điểm tạm tính: {total_xp_today} XP")

        if is_admin:
            if st.button("💾 Lưu Điểm", type="primary"):
                save_data(selected_date, morning_xp, day_xp, evening_xp, tasks_done)
                st.success(f"Đã lưu {total_xp_today} XP cho ngày {selected_date}!")
                st.rerun()
    # TAB 2: Lịch sử
    with tab2:
        st.header("📊 Phân tích dữ liệu & Lịch sử")
        df_history = load_data()
        if df_history.empty:
            st.info("Chưa có dữ liệu.")
        else:
            df_history["Ngày"] = pd.to_datetime(df_history["Ngày"])
            df_history = df_history.sort_values(by="Ngày", ascending=False)

            st.subheader("Biểu đồ Tổng XP theo ngày")
            st.bar_chart(data=df_history, x="Ngày", y="Tổng_XP_Ngày")

            st.subheader("Chi tiết Dữ liệu (Bao gồm các mục đã hoàn thành)")
            st.dataframe(df_history, use_container_width=True)
    # TAB 3: Đổi thưởng
    with tab3:
        st.header("🎁 Hệ thống Đổi thưởng")
        st.warning("Quy tắc: Chỉ khung 8h-12h cuối tuần. Không chơi buổi tối.")

        st.markdown(f"**Tổng XP Tuần hiện tại: {week_xp}**")
        st.markdown("---")

        rewards = [
            {"name": "Game +30p sáng T7/CN", "bonus_needed": 50},
            {"name": "Game +1h sáng cuối tuần", "bonus_needed": 100},
            {"name": "Marathon 2h sáng CN", "bonus_needed": 200},
            {"name": "Mua game mới", "bonus_needed": 500},
        ]

        base_xp = 275
        for rw in rewards:
            target = base_xp + rw["bonus_needed"]
            st.subheader(f"🎯 {rw['name']}")
            st.write(f"Công thức: Cần đạt **{target} XP** = 275 XP cơ bản + {rw['bonus_needed']} XP thưởng.")

            progress = min(week_xp / target, 1.0)
            st.progress(progress)

            if week_xp >= target:
                st.success("🎉 Đã mở khóa!")
            else:
                st.error(f"⏳ Cần tích lũy thêm {target - week_xp} XP")
            st.markdown("---")


if __name__ == "__main__":
    st.set_page_config(page_title="Minh Quest 90", page_icon="🚀", layout="wide")
    main()

