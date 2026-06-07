import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= CẤU HÌNH TRANG =================
st.set_page_config(page_title="Minh Quest 90 - Hệ thống", page_icon="🎮", layout="wide")

# ================= HỆ THỐNG CƠ SỞ DỮ LIỆU =================
DB_FILE = "nhat_ky_diem_xp.csv"


def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
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


# ================= MÔ-ĐUN ĐĂNG NHẬP & PHÂN QUYỀN =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    st.title("🎮 ĐĂNG NHẬP HỆ THỐNG")
    col1, _ = st.columns([1, 2])
    with col1:
        u = st.text_input("Tài khoản:")
        p = st.text_input("Mật khẩu:", type="password")
        if st.button("Đăng nhập", type="primary"):
            if (u == "minh" and p == "minh123"):
                st.session_state.logged_in = True
                st.session_state.role = "Minh"
                st.rerun()
            elif (u == "bo" and p == "bo123"):
                st.session_state.logged_in = True
                st.session_state.role = "Bố"
                st.rerun()
            else:
                st.error("❌ Sai tài khoản hoặc mật khẩu!")
else:
    # ================= MÔ-ĐUN XỬ LÝ LỊCH SỬ & LOGIC TUẦN =================
    df = load_data()
    df["Tổng_XP_Ngày"] = pd.to_numeric(df["Tổng_XP_Ngày"], errors='coerce').fillna(0)

    tuan_hien_tai = datetime.now().isocalendar()[1]
    nam_hien_tai = datetime.now().isocalendar()[0]

    df['Date_Format'] = pd.to_datetime(df['Ngày'], format='%Y-%m-%d', errors='coerce')
    df_tuan_nay = df[(df['Date_Format'].dt.isocalendar().week == tuan_hien_tai) &
                     (df['Date_Format'].dt.isocalendar().year == nam_hien_tai)]

    tong_xp_tuan_nay = int(df_tuan_nay["Tổng_XP_Ngày"].sum())

    # Mốc tối đa của tuần để thanh progress bar Sidebar hiển thị đẹp (Giả sử 375 là mốc 1h game)
    MOC_TUAN = 375

    # ================= GIAO DIỆN SIDEBAR =================
    st.sidebar.title(f"Chào {st.session_state.role} 👋")
    st.sidebar.divider()
    st.sidebar.metric("Tổng XP tuần này", f"{tong_xp_tuan_nay} XP")
    st.sidebar.progress(min(tong_xp_tuan_nay / MOC_TUAN, 1.0))
    st.sidebar.write(f"Mục tiêu chuẩn: **{MOC_TUAN} XP**")
    st.sidebar.divider()
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    # ================= GIAO DIỆN CHÍNH (DASHBOARD) =================
    st.title("🎮 MINH QUEST 90 - DASHBOARD")
    is_admin = (st.session_state.role == "Minh")

    tab_daily, tab_history, tab_rewards = st.tabs(["📝 Nhiệm Vụ", "📊 Lịch Sử", "🎁 Đổi Thưởng"])

    # ---------------- TAB 1: NHIỆM VỤ ----------------
    with tab_daily:
        if not is_admin:
            st.warning("🔒 Tài khoản của Bố chỉ có quyền XEM, không thể lưu điểm nhiệm vụ.")

        col_date, _ = st.columns([1, 2])
        with col_date:
            date_sel = st.date_input("🗓️ Chọn ngày:", datetime.now(), disabled=not is_admin)

        d_str = date_sel.strftime('%Y-%m-%d')
        st.markdown("**DAILY TARGET: ~55 XP • Realistic 70-80% là tốt • Off-day OK**")
        st.divider()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("🌅 MORNING")
            m1 = st.checkbox("Dậy trước 7h (+10 XP)", disabled=not is_admin)
            m2 = st.checkbox("Kéo xà 3x30s [video] (+5 XP)", disabled=not is_admin)
            m3 = st.checkbox("Nhảy dây 5p [video] (+5 XP)", disabled=not is_admin)
            m4 = st.checkbox("Sáng protein ≥15g [photo] (+5 XP)", disabled=not is_admin)
            m5 = st.checkbox("Chạy (+10 XP)", disabled=not is_admin)
        with c2:
            st.subheader("☀️ DAY")
            d1 = st.checkbox("Uống ≥2L nước (+5 XP)", disabled=not is_admin)
            d2 = st.checkbox("Trưa protein [photo] (+5 XP)", disabled=not is_admin)
            d3 = st.checkbox("Đọc sách 15p (+2 XP)", disabled=not is_admin)
            d4 = st.checkbox("Ngoài trời 30p+ (+10 XP)", disabled=not is_admin)
        with c3:
            st.subheader("🌙 EVENING")
            e1 = st.checkbox("Tối protein [photo] (+5 XP)", disabled=not is_admin)
            e2 = st.checkbox("Stretching 10p [video] (+5 XP)", disabled=not is_admin)
            e3 = st.checkbox("Giao ĐT 21h (+10 XP)", disabled=not is_admin)
            e4 = st.checkbox("Tắt đèn 22h (+10 XP)", disabled=not is_admin)
            e5 = st.checkbox("Thuốc (+5 XP)", disabled=not is_admin)

        m_score = (10 if m1 else 0) + (5 if m2 else 0) + (5 if m3 else 0) + (5 if m4 else 0) + (10 if m5 else 0)
        d_score = (5 if d1 else 0) + (5 if d2 else 0) + (2 if d3 else 0) + (10 if d4 else 0)
        e_score = (5 if e1 else 0) + (5 if e2 else 0) + (10 if e3 else 0) + (10 if e4 else 0) + (5 if e5 else 0)

        total_today = m_score + d_score + e_score

        st.divider()
        st.metric("Tổng điểm tạm tính hôm nay", f"{total_today} XP")

        if st.button("💾 Lưu Điểm", type="primary", disabled=not is_admin):
            save_data(d_str, m_score, d_score, e_score, total_today)
            st.success(f"🎉 Đã lưu {total_today} XP cho ngày {d_str}!")
            st.rerun()

    # ---------------- TAB 2: LỊCH SỬ DỮ LIỆU ----------------
    with tab_history:
        st.header("📊 Lịch sử nhiệm vụ")
        if not df.empty:
            col_chart, col_data = st.columns([1.5, 1])
            df_display = df.sort_values(by="Ngày", ascending=False).reset_index(drop=True)

            with col_chart:
                st.write("**Biểu đồ tổng điểm các ngày**")
                st.bar_chart(data=df.set_index("Ngày")["Tổng_XP_Ngày"])
            with col_data:
                st.write("**Bảng dữ liệu chi tiết**")
                cols_to_show = [c for c in df_display.columns if c != 'Date_Format']
                st.dataframe(df_display[cols_to_show], use_container_width=True)
        else:
            st.info("Chưa có dữ liệu lịch sử.")

    # ---------------- TAB 3: HỆ THỐNG ĐỔI THƯỞNG ----------------
    with tab_rewards:
        st.header("🎁 HỆ THỐNG ĐỔI THƯỞNG")
        st.error("⚠️ Quy tắc: Chỉ khung 8h-12h cuối tuần. Không chơi buổi tối.")
        st.write("---")

        # LOGIC MỚI: Yêu cầu đạt mức duy trì trước khi đổi thưởng
        MOC_CO_BAN = 275

        rewards = [
            {"Mục": "Game +30p sáng T7/CN", "Gia_XP": 50, "Mục_tieu": MOC_CO_BAN + 50},
            {"Mục": "Game +1h sáng cuối tuần", "Gia_XP": 100, "Mục_tieu": MOC_CO_BAN + 100},
            {"Mục": "Marathon 2h sáng CN", "Gia_XP": 200, "Mục_tieu": MOC_CO_BAN + 200},
            {"Mục": "Mua game mới", "Gia_XP": 500, "Mục_tieu": MOC_CO_BAN + 500}
        ]

        st.subheader(f"⚡ Điểm đã tích lũy tuần này: {tong_xp_tuan_nay} XP")
        st.info(f"💡 Cần hoàn thành mốc cơ bản **{MOC_CO_BAN} XP** (tương đương 5 ngày) trước khi nhận thưởng.")
        st.write("---")

        for r in rewards:
            val = r["Mục_tieu"]
            gia = r["Gia_XP"]

            # Hiển thị rõ ràng công thức cho người xem
            st.markdown(f"**{r['Mục']}**")
            st.write(f"*(Cần đạt: {val} XP = {MOC_CO_BAN} XP cơ bản + {gia} XP thưởng)*")

            progress = min(tong_xp_tuan_nay / val, 1.0)
            st.progress(progress)

            if tong_xp_tuan_nay >= val:
                st.success(f"✅ Đã đủ điểm mở khóa mốc này!")
            else:
                st.warning(f"🔒 Cần tích lũy thêm {val - tong_xp_tuan_nay} XP nữa")
            st.write("")