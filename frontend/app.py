import os
from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

import ui


API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")


# ---------------- basic API helper ----------------
def api_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_get(path):
    r = requests.get(API_BASE + path, headers=api_headers(), timeout=20)
    if r.status_code >= 400:
        raise Exception(f"Error {r.status_code}: {r.text}")
    return r.json()


def api_post(path, data=None):
    r = requests.post(API_BASE + path, json=data or {}, headers=api_headers(), timeout=20)
    if r.status_code >= 400:
        raise Exception(f"Error {r.status_code}: {r.text}")
    return r.json()


# ---------------- page setup ----------------
st.set_page_config(
    page_title="HCM Lite",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.inject_css()


# ---------------- session helpers ----------------
def logout():
    st.session_state.clear()
    st.rerun()


def is_logged_in():
    return bool(st.session_state.get("token"))


def current_user():
    return st.session_state.get("user", {})


# ---------------- setup / login ----------------
def render_setup():
    ui.page_header("First Run Setup", "Create company profile and first Admin account")

    with st.container(border=True):
        with st.form("setup_form"):
            company_name = st.text_input("Company name", placeholder="Example: Saylani Tech")
            admin_name = st.text_input("Admin name", placeholder="Admin User")
            admin_email = st.text_input("Admin email", placeholder="admin@company.com")
            admin_password = st.text_input("Admin password", type="password")

            submitted = st.form_submit_button("Create company and Admin")

        if submitted:
            try:
                api_post(
                    "/setup",
                    {
                        "company_name": company_name,
                        "admin_name": admin_name,
                        "admin_email": admin_email,
                        "admin_password": admin_password,
                    },
                )
                st.success("Setup complete. Now login.")
                st.rerun()
            except Exception as e:
                st.error(str(e))


def render_login():
    ui.page_header("Welcome back", "Login to HCM Lite")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <h3 style="margin-top:0;color:#f8fafc">HCM Lite</h3>
                <p style="color:#94a3b8">
                AI-assisted Human Capital Management for Admin, HR and Employees.
                </p>
                <ul style="color:#cbd5e1;line-height:1.9">
                    <li>Role based dashboard</li>
                    <li>Attendance and leave workflows</li>
                    <li>Payroll lite</li>
                    <li>AI assistant ready</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        with st.container(border=True):
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")

            if submitted:
                try:
                    res = api_post("/auth/login", {"email": email, "password": password})

                    st.session_state["token"] = res["token"]
                    st.session_state["user"] = {
                        "name": res["name"],
                        "role": res["role"],
                        "must_change_password": res["must_change_password"],
                    }

                    me = api_get("/auth/me")
                    st.session_state["user"].update(me)

                    st.success("Login successful")
                    st.rerun()

                except Exception as e:
                    st.error(str(e))


# ---------------- sidebar ----------------
MENUS = {
    "admin": [
        "Dashboard",
        "Departments",
        "HR Users",
        "Employees",
        "Change Password",
    ],
    "hr": [
        "Dashboard",
        "Employees",
        "Leave Approvals",
        "Change Password",
    ],
    "employee": [
        "My Dashboard",
        "Apply Leave",
        "My Leaves",
        "Change Password",
    ],
}


ICONS = {
    "Dashboard": "📊",
    "Departments": "🏬",
    "HR Users": "🧑‍💼",
    "Employees": "👥",
    "Leave Approvals": "✅",
    "My Dashboard": "🏠",
    "Apply Leave": "📝",
    "My Leaves": "🌴",
    "Change Password": "🔑",
}


def render_sidebar():
    user = current_user()
    name = user.get("name", "User")
    role = user.get("role", "employee")
    initial = name[:1].upper()

    role_label = {
        "admin": "System Administrator",
        "hr": "HR Manager",
        "employee": "Employee Self-Service",
    }.get(role, "User")

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-logo">🏢</div>
                <div>
                    <div class="brand-title">HCM <b>CONTROL ROOM</b></div>
                    <div class="brand-sub">Human Capital<br/>Management Platform</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="system-box">
                <div class="system-online"><span class="pulse-dot"></span>System Online</div>
                <div class="system-sub">{role} access · API connected</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)

        menu = MENUS.get(role, MENUS["employee"])

        if "page" not in st.session_state or st.session_state["page"] not in menu:
            st.session_state["page"] = menu[0]

        for item in menu:
            label = f"{ICONS.get(item, '•')}  {item}"
            btn_type = "primary" if st.session_state["page"] == item else "secondary"

            if st.button(label, use_container_width=True, type=btn_type, key=f"nav_{item}"):
                st.session_state["page"] = item
                st.rerun()

        st.markdown(
            f"""
            <div class="sidebar-user">
                <div class="user-avatar">{initial}</div>
                <div>
                    <div class="user-name">{name}</div>
                    <div class="user-role">{role_label}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚪 Sign out", use_container_width=True, key="logout_sidebar"):
            logout()

        st.markdown('<div class="sidebar-footer">HCM LITE · v0.1</div>', unsafe_allow_html=True)


# ---------------- shared loaders ----------------
def load_departments():
    try:
        return api_get("/org/departments")
    except Exception as e:
        st.error(f"Departments load error: {e}")
        return []


def load_employees():
    try:
        return api_get("/employees")
    except Exception as e:
        st.error(f"Employees load error: {e}")
        return []


# ---------------- admin dashboard ----------------
def render_admin_dashboard():
    departments = load_departments()
    employees = load_employees()

    dept_map = {d["id"]: d["name"] for d in departments}

    now = datetime.now()
    first_name = current_user().get("name", "Admin").split()[0]

    top_left, top_right = st.columns([4, 1.2])

    with top_left:
        search = st.text_input(
            "Search",
            placeholder="🔍 Search employees, departments, payroll...",
            label_visibility="collapsed",
            key="admin_search",
        )

        part = "Morning" if now.hour < 12 else "Afternoon" if now.hour < 18 else "Evening"

        st.markdown(
            f"""
            <div class="page-title">
                Good {part}, <span class="accent">{first_name}</span>
            </div>
            <div class="page-subtitle">
                Here's what's happening in your HCM control room.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown(
            f"""
            <div style="text-align:right">
                <div style="color:#9fb0e6;font-size:.8rem">{now.strftime("%a, %d %b %Y")}</div>
                <div style="font-size:2rem;font-weight:950;color:white">{now.strftime("%H:%M")}</div>
                <div style="color:#22c55e;font-size:.78rem">● Updated {now.strftime("%H:%M:%S")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    total_employees = len(employees)
    total_departments = len(departments)

    payroll_cost = 0
    avg_salary = 0

    if employees:
        for e in employees:
            payroll_cost += float(e.get("basic_salary") or 0) * 1.5
        avg_salary = payroll_cost / total_employees if total_employees else 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        ui.kpi_card("Employees", total_employees, "active headcount", "👥", "#f43f5e")

    with c2:
        ui.kpi_card("Departments", total_departments, "organization units", "🏬", "#f59e0b")

    with c3:
        ui.kpi_card("Payroll Cost", f"{payroll_cost:,.0f}", "estimated gross / month", "💰", "#8b5cf6")

    with c4:
        ui.kpi_card("Avg Salary", f"{avg_salary:,.0f}", "average gross salary", "✅", "#22d3ee")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.9, 1])

    with left:
        with st.container(border=True):
            ui.panel_start("Workforce Growth Trend", "Employees joined over time")

            if employees:
                df = pd.DataFrame(employees)

                if "joining_date" in df.columns:
                    df["joining_date"] = pd.to_datetime(df["joining_date"], errors="coerce")
                    df = df.dropna(subset=["joining_date"])

                if not df.empty and "joining_date" in df.columns:
                    start = df["joining_date"].min()
                    end = pd.Timestamp.today().normalize()

                    days = pd.date_range(start=start, end=end, freq="D")

                    trend = []
                    for day in days:
                        trend.append(
                            {
                                "date": day,
                                "employees": int((df["joining_date"] <= day).sum()),
                            }
                        )

                    trend_df = pd.DataFrame(trend)

                    fig = go.Figure()

                    fig.add_trace(
                        go.Scatter(
                            x=trend_df["date"],
                            y=trend_df["employees"],
                            mode="lines+markers",
                            line=dict(color="#f43f5e", width=3, shape="spline"),
                            marker=dict(size=6, color="#f43f5e"),
                            fill="tozeroy",
                            fillcolor="rgba(244,63,94,.18)",
                            name="Headcount",
                        )
                    )

                    fig.update_layout(
                        height=315,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#9fb0e6"),
                        margin=dict(l=20, r=20, t=20, b=20),
                        xaxis=dict(gridcolor="rgba(148,163,184,.08)"),
                        yaxis=dict(gridcolor="rgba(148,163,184,.12)", rangemode="tozero"),
                        hovermode="x unified",
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Joining dates not available yet.")
            else:
                st.info("Register employees to see trend.")

    with right:
        with st.container(border=True):
            ui.panel_start("Department Distribution", "Employees by department")

            if employees and departments:
                df = pd.DataFrame(employees)
                df["department"] = df["department_id"].map(dept_map).fillna("Unknown")

                pie_df = df.groupby("department").size().reset_index(name="employees")

                fig = go.Figure(
                    go.Pie(
                        labels=pie_df["department"],
                        values=pie_df["employees"],
                        hole=0.58,
                        marker=dict(
                            colors=["#f43f5e", "#f59e0b", "#0ea5e9", "#8b5cf6", "#22c55e"],
                            line=dict(color="#081332", width=3),
                        ),
                        textinfo="percent",
                        textfont=dict(color="white"),
                    )
                )

                fig.add_annotation(
                    text=f"<b>{total_employees}</b><br><span style='font-size:11px;color:#8c9ac4'>employees</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=24, color="#ffffff"),
                )

                fig.update_layout(
                    height=315,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=True,
                    font=dict(color="#9fb0e6"),
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No department data yet.")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    b1, b2 = st.columns([1.35, 1])

    with b1:
        with st.container(border=True):
            ui.panel_start("Department Headcount", "Current employees per department")

            if employees and departments:
                df = pd.DataFrame(employees)
                df["department"] = df["department_id"].map(dept_map).fillna("Unknown")

                bar_df = df.groupby("department").size().reset_index(name="employees")

                fig = go.Figure()

                fig.add_trace(
                    go.Bar(
                        x=bar_df["department"],
                        y=bar_df["employees"],
                        text=bar_df["employees"],
                        textposition="outside",
                        marker=dict(
                            color=["#4f46e5", "#06b6d4", "#8b5cf6", "#f59e0b", "#22c55e"],
                            line=dict(color="rgba(255,255,255,.15)", width=1),
                        ),
                    )
                )

                fig.update_layout(
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#9fb0e6"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(gridcolor="rgba(148,163,184,.08)"),
                    yaxis=dict(gridcolor="rgba(148,163,184,.12)", rangemode="tozero"),
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Add employees to see department chart.")

    with b2:
        with st.container(border=True):
            ui.panel_start("Recent Employees", "Latest registered employee records")

            if employees:
                show_df = pd.DataFrame(employees)

                if search:
                    s = search.lower()
                    show_df = show_df[
                        show_df.astype(str).apply(
                            lambda row: row.str.lower().str.contains(s).any(),
                            axis=1,
                        )
                    ]

                ui.data_table(
                    show_df,
                    columns=["code", "name", "email", "designation", "status"],
                    headers={
                        "code": "Code",
                        "name": "Employee",
                        "email": "Email",
                        "designation": "Designation",
                        "status": "Status",
                    },
                    max_rows=8,
                    empty_text="No recent employees found.",
                )
            else:
                st.info("No employees yet.")


# ---------------- hr dashboard ----------------
def render_hr_dashboard():
    ui.page_header("HR Dashboard", "People operations, employee activity and approvals")

    employees = load_employees()

    try:
        pending_leaves = api_get("/leave/pending")
        pending_count = len(pending_leaves)
    except Exception:
        pending_count = "—"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        ui.kpi_card("Employees", len(employees), "registered employees", "👥", "#22d3ee")
    with c2:
        ui.kpi_card("Pending Leaves", pending_count, "awaiting HR approval", "✅", "#f59e0b")
    with c3:
        ui.kpi_card("Attendance", "Ready", "next module", "🕒", "#8b5cf6")
    with c4:
        ui.kpi_card("Payroll", "Draft", "next module", "💰", "#22c55e")

    st.markdown("### Employee Directory")

    if employees:
        ui.data_table(
            pd.DataFrame(employees),
            columns=["code", "name", "email", "designation", "status"],
            headers={
                "code": "Code",
                "name": "Employee",
                "email": "Email",
                "designation": "Designation",
                "status": "Status",
            },
            empty_text="No employees registered yet.",
        )
    else:
        st.info("No employees registered yet.")


# ---------------- employee dashboard ----------------
def render_employee_dashboard():
    ui.page_header("My Dashboard", "Your personal HR self-service area")

    c1, c2, c3 = st.columns(3)

    with c1:
        ui.kpi_card("Attendance", "Ready", "check-in module next", "🕒", "#22d3ee")
    with c2:
        ui.kpi_card("Leave", "Apply", "request your leave", "📝", "#f59e0b")
    with c3:
        ui.kpi_card("Payslip", "Coming", "payroll module next", "💰", "#22c55e")

    st.info("Employee dashboard ready. Attendance and payroll will connect here.")


# ---------------- departments ----------------
def render_departments():
    ui.page_header("Departments", "Create and manage company departments")

    with st.container(border=True):
        with st.form("dept_form"):
            name = st.text_input("Department name", placeholder="IT, HR, Sales, Finance")
            submitted = st.form_submit_button("Add department")

        if submitted:
            try:
                api_post("/org/departments", {"name": name})
                st.success(f"'{name}' created successfully")
                st.rerun()
            except Exception as e:
                st.error(str(e))

    st.markdown("### All Departments")

    departments = load_departments()

    if departments:
        ui.data_table(
            pd.DataFrame(departments),
            columns=["id", "name"],
            headers={
                "id": "ID",
                "name": "Department Name",
            },
            empty_text="No departments yet.",
        )
    else:
        st.info("No departments yet.")


# ---------------- HR Users ----------------
def render_hr_users():
    ui.page_header("HR Users", "Create HR logins with temporary password")

    with st.container(border=True):
        with st.form("hr_form"):
            name = st.text_input("HR name")
            email = st.text_input("HR email")
            submitted = st.form_submit_button("Create HR user")

        if submitted:
            try:
                res = api_post("/users/hr", {"name": name, "email": email})
                st.success("HR user created")
                st.code(f"Email: {res['email']}\nTemporary Password: {res['temporary_password']}")
            except Exception as e:
                st.error(str(e))


# ---------------- employees ----------------
def render_employees():
    role = current_user().get("role")

    if role == "hr":
        ui.page_header("Employees", "Register employees and create their login")

        departments = load_departments()

        if not departments:
            st.warning("Please ask Admin to create departments first.")
            return

        dept_options = {f"{d['name']} — ID {d['id']}": d["id"] for d in departments}

        with st.container(border=True):
            with st.form("emp_form"):
                col1, col2 = st.columns(2)

                with col1:
                    employee_code = st.text_input("Employee code", placeholder="EMP001")
                    full_name = st.text_input("Full name")
                    email = st.text_input("Email")
                    phone = st.text_input("Phone")

                with col2:
                    department_label = st.selectbox("Department", list(dept_options.keys()))
                    designation = st.text_input("Designation", placeholder="Developer, HR Officer")
                    joining_date = st.date_input("Joining date", value=date.today())
                    basic_salary = st.number_input("Basic salary", min_value=1.0, step=1000.0)

                address = st.text_area("Address")

                submitted = st.form_submit_button("Register employee")

            if submitted:
                try:
                    res = api_post(
                        "/employees",
                        {
                            "employee_code": employee_code,
                            "full_name": full_name,
                            "email": email,
                            "department_id": dept_options[department_label],
                            "designation": designation,
                            "joining_date": str(joining_date),
                            "basic_salary": basic_salary,
                            "phone": phone,
                            "address": address,
                        },
                    )

                    st.success("Employee registered successfully")
                    st.code(
                        f"Email: {res['email']}\nTemporary Password: {res['temporary_password']}"
                    )

                except Exception as e:
                    st.error(str(e))

    else:
        ui.page_header("Employees", "View employee directory")

    employees = load_employees()

    st.markdown("### Employee List")

    if employees:
        ui.data_table(
            pd.DataFrame(employees),
            columns=["code", "name", "email", "designation", "status", "basic_salary"],
            headers={
                "code": "Code",
                "name": "Employee",
                "email": "Email",
                "designation": "Designation",
                "status": "Status",
                "basic_salary": "Basic Salary",
            },
            empty_text="No employees yet.",
        )
    else:
        st.info("No employees yet.")


# ---------------- leave approvals ----------------
def render_leave_approvals():
    ui.page_header("Leave Approvals", "Approve or reject employee leave requests")

    try:
        leaves = api_get("/leave/pending")
    except Exception as e:
        st.error(str(e))
        return

    if not leaves:
        st.success("No pending leave requests.")
        return

    for leave in leaves:
        with st.container(border=True):
            top1, top2 = st.columns([3, 1])

            with top1:
                st.markdown(f"### {leave['employee_name']} ({leave['employee_code']})")
                st.markdown(
                    f"""
                    **Leave type:** {leave['leave_type']}  
                    **Dates:** {leave['start_date']} → {leave['end_date']}  
                    **Days:** {leave['days_count']}  
                    **Reason:** {leave.get('reason') or '—'}
                    """
                )

            with top2:
                st.markdown(ui.status_pill(leave["status"]), unsafe_allow_html=True)

            comment = st.text_input(
                "HR comment",
                key=f"comment_{leave['id']}",
                placeholder="Optional comment",
            )

            c1, c2, c3 = st.columns([1, 1, 4])

            with c1:
                if st.button("✅ Approve", key=f"approve_{leave['id']}", use_container_width=True):
                    try:
                        api_post(f"/leave/{leave['id']}/approve", {"comment": comment})
                        st.success("Leave approved")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

            with c2:
                if st.button("❌ Reject", key=f"reject_{leave['id']}", use_container_width=True):
                    try:
                        api_post(f"/leave/{leave['id']}/reject", {"comment": comment})
                        st.warning("Leave rejected")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


# ---------------- employee leave apply ----------------
def render_apply_leave():
    ui.page_header("Apply Leave", "Submit leave request for HR approval")

    with st.container(border=True):
        with st.form("leave_apply_form"):
            leave_type = st.selectbox("Leave type", ["annual", "sick", "casual", "unpaid"])

            col1, col2 = st.columns(2)

            with col1:
                start_date = st.date_input("Start date", value=date.today())

            with col2:
                end_date = st.date_input("End date", value=date.today())

            reason = st.text_area("Reason")

            submitted = st.form_submit_button("Submit leave request")

        if submitted:
            try:
                api_post(
                    "/leave/apply",
                    {
                        "leave_type": leave_type,
                        "start_date": str(start_date),
                        "end_date": str(end_date),
                        "reason": reason,
                    },
                )
                st.success("Leave request submitted")
            except Exception as e:
                st.error(str(e))


def render_my_leaves():
    ui.page_header("My Leaves", "Track your leave requests")

    try:
        rows = api_get("/leave/my")
    except Exception as e:
        st.error(str(e))
        return

    if rows:
        ui.data_table(
            pd.DataFrame(rows),
            columns=["id", "leave_type", "start_date", "end_date", "days_count", "status", "hr_comment"],
            headers={
                "id": "ID",
                "leave_type": "Type",
                "start_date": "Start",
                "end_date": "End",
                "days_count": "Days",
                "status": "Status",
                "hr_comment": "HR Comment",
            },
            empty_text="No leave requests yet.",
        )
    else:
        st.info("No leave requests yet.")


# ---------------- change password ----------------
def render_change_password():
    ui.page_header("Change Password", "Update your account password")

    with st.container(border=True):
        with st.form("change_pwd"):
            old_password = st.text_input("Old password", type="password")
            new_password = st.text_input("New password", type="password")
            submitted = st.form_submit_button("Change password")

        if submitted:
            try:
                api_post(
                    "/auth/change-password",
                    {
                        "old_password": old_password,
                        "new_password": new_password,
                    },
                )
                st.success("Password changed successfully")
            except Exception as e:
                st.error(str(e))


# ---------------- router ----------------
def render_page():
    role = current_user().get("role")
    page = st.session_state.get("page")

    if page == "Dashboard":
        if role == "admin":
            render_admin_dashboard()
        elif role == "hr":
            render_hr_dashboard()
        else:
            render_employee_dashboard()

    elif page == "My Dashboard":
        render_employee_dashboard()

    elif page == "Departments":
        render_departments()

    elif page == "HR Users":
        render_hr_users()

    elif page == "Employees":
        render_employees()

    elif page == "Leave Approvals":
        render_leave_approvals()

    elif page == "Apply Leave":
        render_apply_leave()

    elif page == "My Leaves":
        render_my_leaves()

    elif page == "Change Password":
        render_change_password()

    else:
        st.warning("Page not found")


# ---------------- main ----------------
def main():
    try:
        setup = api_get("/setup/status")
    except Exception:
        st.error("Backend API not running. Start FastAPI first.")
        st.code("uvicorn backend.main:app --reload")
        return

    if not setup.get("setup_done"):
        render_setup()
        return

    if not is_logged_in():
        render_login()
        return

    render_sidebar()
    render_page()


main()