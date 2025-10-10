import sys
import os
import streamlit as st
import streamlit as st
from datetime import datetime, timedelta, time
from streamlit_autorefresh import st_autorefresh


# --------------------------------
# Add project root to sys.path
# --------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.commander import parse_command
from agents import aws_agent, db_agent, docker_agent, logs_agent, scheduler_agent as scheduler

# --------------------------------
# Streamlit Config
# --------------------------------
st.set_page_config(page_title="Jarvis Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center;'>🧠 Jarvis - DevOps Automation Dashboard</h1>", unsafe_allow_html=True)

# --------------------------------
# Sidebar Navigation with Session State (Fixed)
# --------------------------------
if "menu" not in st.session_state:
    st.session_state.menu = "Command Console"

menu = st.sidebar.radio(
    "🧩 Choose Module",
    [
        "Command Console",
        "EC2 Instances",
        "Databases",
        "Docker Containers",
        "Logs",
        "Tickets",
        "Scheduled Tasks"
    ],
    index=[
        "Command Console",
        "EC2 Instances",
        "Databases",
        "Docker Containers",
        "Logs",
        "Tickets",
        "Scheduled Tasks"
    ].index(st.session_state.menu),
)

# ✅ Update only if user changed selection
if menu != st.session_state.menu:
    st.session_state.menu = menu
    st.rerun()

# Use the persisted menu state
menu = st.session_state.menu


# -----------------------
# Compute time options
# -----------------------
def generate_time_options(interval_minutes=30):
    now = datetime.now()
    # Round up to next interval
    minute = (now.minute // interval_minutes + 1) * interval_minutes
    hour = now.hour
    if minute >= 60:
        minute -= 60
        hour = (hour + 1) % 24
    start_time = datetime(now.year, now.month, now.day, hour, minute)
    
    # Generate all 30-min slots in 24h format
    times = []
    current = start_time
    while True:
        times.append(current.strftime("%H:%M"))
        current += timedelta(minutes=interval_minutes)
        if current.hour == start_time.hour and current.minute == start_time.minute:
            break
    return times


# --------------------------------
# Helper Function
# --------------------------------
def handle_action_with_schedule(action_fn, description, schedule=False, delay_seconds=10):
    if schedule:
        scheduler.schedule_action(action_fn, delay_seconds=delay_seconds, description=description)
        st.success(f"✅ Scheduled {description} in {delay_seconds} seconds")
    else:
        result = action_fn()
        st.success(result)


# =================================================================
# 1️⃣ COMMAND CONSOLE
# =================================================================
if menu == "Command Console":
    st.subheader("💬 Command Console")
    user_input = st.text_input("Enter your command:", "")

    if st.button("Send Command", type="primary") and user_input.strip():
        parsed = parse_command(user_input)
        action = parsed.get("action")
        user_input_lower = user_input.lower()

        if action == "list_ec2":
            st.json(aws_agent.list_ec2_instances())

        elif action == "start_ec2":
            instance_id = parsed.get("instance_id")
            handle_action_with_schedule(
                lambda: aws_agent.start_ec2(instance_id),
                f"Start EC2 {instance_id}",
                schedule="at" in user_input_lower
            )

        elif action == "stop_ec2":
            instance_id = parsed.get("instance_id")
            handle_action_with_schedule(
                lambda: aws_agent.stop_ec2(instance_id),
                f"Stop EC2 {instance_id}",
                schedule="at" in user_input_lower
            )

        elif action == "list_db":
            st.json(db_agent.list_databases())

        elif action == "start_db":
            db_id = parsed.get("db_id")
            handle_action_with_schedule(
                lambda: db_agent.start_db(db_id),
                f"Start DB {db_id}",
                schedule="at" in user_input_lower
            )

        elif action == "stop_db":
            db_id = parsed.get("db_id")
            handle_action_with_schedule(
                lambda: db_agent.stop_db(db_id),
                f"Stop DB {db_id}",
                schedule="at" in user_input_lower
            )

        elif action == "list_container":
            st.json(docker_agent.list_containers())

        elif action == "start_container":
            cid = parsed.get("cid")
            handle_action_with_schedule(
                lambda: docker_agent.start_container(cid),
                f"Start container {cid}",
                schedule="at" in user_input_lower
            )

        elif action == "stop_container":
            cid = parsed.get("cid")
            handle_action_with_schedule(
                lambda: docker_agent.stop_container(cid),
                f"Stop container {cid}",
                schedule="at" in user_input_lower
            )

        elif action == "show_logs":
            level = parsed.get("level")
            files = parsed.get("files")
            logs = logs_agent.show_logs(level=level, files=files, all_logs=True)
            st.json(logs)

        elif action == "create_ticket_from_error":
            files = parsed.get("files")
            created = logs_agent.create_ticket_from_error(files=files)
            st.success(f"Created {len(created)} ticket(s)")
            st.json(created)

        elif action == "list_tickets":
            tickets = logs_agent.list_tickets()
            st.json(tickets)

        else:
            st.info(f"🤖 Jarvis says: {parsed.get('message')}")


# =================================================================
# 2️⃣ EC2 DASHBOARD
# =================================================================
elif menu == "EC2 Instances":
    st.subheader("💻 EC2 Instances Overview")
    ec2_list = aws_agent.list_ec2_instances()

    if not ec2_list:
        st.warning("No EC2 instances found.")
    else:
        for ec2 in ec2_list:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            # -----------------------
            # EC2 Info
            # -----------------------
            with col1:
                st.write(f"**{ec2['id']}** - {ec2['name']}")

            with col2:
                st.write(ec2['state'])

            # -----------------------
            # Start / Stop buttons
            # -----------------------
            with col3:
                if ec2['state'] == 'stopped':
                    if st.button(f"Start {ec2['id']}", key=f"start_{ec2['id']}"):
                        st.success(aws_agent.start_ec2(ec2['id']))
                else:
                    if st.button(f"Stop {ec2['id']}", key=f"stop_{ec2['id']}"):
                        st.warning(aws_agent.stop_ec2(ec2['id']))

            # -----------------------
            # Scheduling section (collapsible)
            # -----------------------
            with col4:
                with st.expander("⏰ Schedule"):
                    # Initialize default session state once
                    time_key = f"time_{ec2['id']}"
                    action_key = f"action_{ec2['id']}"
                    if time_key not in st.session_state:
                        st.session_state[time_key] = datetime.now().time()
                    if action_key not in st.session_state:
                        st.session_state[action_key] = "Start"

                    # -----------------------
                    # Determine available actions based on EC2 state
                    # -----------------------
                    if ec2['state'] == "stopped":
                        available_actions = ["Start"]
                        st.session_state[action_key] = "Start"
                    else:
                        available_actions = ["Stop"]
                        st.session_state[action_key] = "Stop"

                    # -----------------------
                    # Start/Stop action dropdown (adapt to EC2 state)
                    # -----------------------
                    if ec2['state'] == 'stopped':
                        action_options = ["Start"]
                    else:
                        action_options = ["Stop"]

                    action_choice = st.selectbox("Action", action_options, key=action_key)

                    # -----------------------
                    # Time selection with 30-min increments
                    # -----------------------
                    now = datetime.now()
                    minute = now.minute
                    # Round up to next half-hour
                    if minute < 30:
                        start_minute = 30
                    else:
                        start_minute = 0
                        now += timedelta(hours=1)
                    start_hour = now.hour

                    # Generate 48 time options for 30-min intervals
                    time_options = []
                    for h in range(start_hour, start_hour + 24):
                        hour = h % 24
                        time_options.append(time(hour, start_minute))
                        start_minute = 30 if start_minute == 0 else 0

                    # Use unique key for selectbox to avoid duplicate-element errors
                    time_key_select = f"time_select_{ec2['id']}"
                    if time_key_select not in st.session_state:
                        st.session_state[time_key_select] = time_options[0]

                    schedule_time = st.selectbox(
                        "Select Time",
                        options=time_options,
                        index=time_options.index(st.session_state[time_key_select]),
                        key=time_key_select
                    )



                    if st.button("Schedule", key=f"schedule_btn_{ec2['id']}"):
                        # Compute delay
                        now = datetime.now()
                        schedule_dt = datetime.combine(now.date(), schedule_time)
                        if schedule_dt < now:
                            schedule_dt += timedelta(days=1)
                        delay_seconds = (schedule_dt - now).total_seconds()

                        # Schedule the action
                        if action_choice == "Start":
                            scheduler.schedule_action(
                                lambda: aws_agent.start_ec2(ec2['id']),
                                delay_seconds=delay_seconds,
                                description=f"Start EC2 {ec2['id']}"
                            )
                        else:
                            scheduler.schedule_action(
                                lambda: aws_agent.stop_ec2(ec2['id']),
                                delay_seconds=delay_seconds,
                                description=f"Stop EC2 {ec2['id']}"
                            )
                        st.success(f"✅ Scheduled {action_choice} for {ec2['id']} at {schedule_time}")


# =================================================================
# 3️⃣ DATABASE DASHBOARD
# =================================================================
elif menu == "Databases":
    st.subheader("🗄️ Database Instances")
    db_list = db_agent.list_databases()

    if not db_list:
        st.warning("No databases found.")
    else:
        # Dropdown to select DB
        db_names = [f"{db['id']} - {db['name']} ({db['engine']})" for db in db_list]
        selected_db_idx = st.selectbox("Select Database", range(len(db_list)), format_func=lambda i: db_names[i])
        db = db_list[selected_db_idx]

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        # -----------------------
        # DB Info
        # -----------------------
        with col1:
            st.write(f"**{db['id']}** - {db['name']} ({db['engine']})")
            st.write(f"Region: {db['region']}")
            st.write(f"Created At: {db['created_at']}")
            st.write(f"Size: {db['size']}")

        # -----------------------
        # Status
        # -----------------------
        with col2:
            st.write(db['status'])

        # -----------------------
        # Start / Stop buttons
        # -----------------------
        with col3:
            if db['status'] in ['stopped', 'creating']:
                if st.button(f"Start {db['id']}", key=f"start_{db['id']}"):
                    st.success(db_agent.start_db(db['id']))
            else:
                if st.button(f"Stop {db['id']}", key=f"stop_{db['id']}"):
                    st.warning(db_agent.stop_db(db['id']))

        # -----------------------
        # Scheduling section (collapsible)
        # -----------------------
        with col4:
            with st.expander("⏰ Schedule"):
                # Unique keys per DB
                time_key = f"time_{db['id']}_schedule"
                action_key = f"action_{db['id']}_schedule"
                btn_key = f"btn_{db['id']}_schedule"

                now = datetime.now()
                # Generate list of time options starting from next nearest 30-minute slot
                minute = 30 if now.minute < 30 else 0
                hour = now.hour + (1 if now.minute >= 30 else 0)
                time_options = [
                    (datetime.now().replace(hour=(hour+i)%24, minute=minute, second=0, microsecond=0).strftime("%H:%M"))
                    for i in range(24)
                ]

                # Initialize session state
                if time_key not in st.session_state:
                    st.session_state[time_key] = time_options[0]

                if action_key not in st.session_state:
                    # Only allow relevant action based on status
                    st.session_state[action_key] = "Stop" if db['status'] not in ["stopped", "creating"] else "Start"

                # Determine available action
                available_actions = ["Stop"] if db['status'] not in ["stopped", "creating"] else ["Start"]

                # Dropdowns
                action_choice = st.selectbox("Action", available_actions, key=action_key)
                schedule_time = st.selectbox(
                    "Time",
                    options=time_options,
                    index=time_options.index(st.session_state[time_key]),
                    key=time_key
                )

                # Schedule button
                if st.button("Schedule", key=btn_key):
                    # Compute delay in seconds
                    now = datetime.now()
                    selected_time_dt = datetime.strptime(schedule_time, "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day
                    )
                    if selected_time_dt < now:
                        selected_time_dt += timedelta(days=1)
                    delay_seconds = (selected_time_dt - now).total_seconds()

                    # Schedule action
                    if action_choice == "Start":
                        scheduler.schedule_action(
                            lambda: db_agent.start_db(db['id']),
                            delay_seconds=delay_seconds,
                            description=f"Start DB {db['id']}"
                        )
                    else:
                        scheduler.schedule_action(
                            lambda: db_agent.stop_db(db['id']),
                            delay_seconds=delay_seconds,
                            description=f"Stop DB {db['id']}"
                        )
                    st.success(f"✅ Scheduled {action_choice} for {db['id']} at {schedule_time}")


        # -----------------------
        # Metrics chart for selected DB
        # -----------------------
        metrics = db_agent.get_db_metrics(db['id'])
        st.line_chart({
            "CPU (%)": metrics["CPU_Utilization"],
            "Storage (GB)": metrics["Storage_Usage_GB"]
        })


# =================================================================
# 4️⃣ DOCKER DASHBOARD
# =================================================================
elif menu == "Docker Containers":
    st.subheader("🐳 Docker Containers Overview")
    containers = docker_agent.list_containers()

    if not containers:
        st.warning("No containers found.")
    else:
        for c in containers:
            # -----------------------
            # Container Header + Start/Stop
            # -----------------------
            col_name, col_status, col_btn = st.columns([3,1,1])
            with col_name:
                st.markdown(f"**{c['name']}** ({c['id']})")
            with col_status:
                status_color = "#28a745" if c["status"] == "running" else "#dc3545"
                st.markdown(
                    f"<span style='color:white; background-color:{status_color}; padding:4px 8px; border-radius:8px; font-size:12px;'>{c['status'].upper()}</span>",
                    unsafe_allow_html=True
                )
            with col_btn:
                if c["status"] == "running":
                    if st.button("Stop", key=f"stop_{c['id']}", use_container_width=True):
                        st.warning(docker_agent.stop_container(c["id"]))
                        st.experimental_rerun()
                else:
                    if st.button("Start", key=f"start_{c['id']}", use_container_width=True):
                        st.success(docker_agent.start_container(c["id"]))
                        st.experimental_rerun()

            # -----------------------
            # Metrics section (compact)
            # -----------------------
            metrics = docker_agent.get_container_metrics(c["id"])
            cpu_latest = metrics.get("CPU_History", [0])[-1]
            mem_latest = metrics.get("Memory_History", [0])[-1]

            col_cpu, col_mem = st.columns(2)
            with col_cpu:
                st.markdown(
                    f"<div style='background:#d9f7be; padding:6px; border-radius:8px; text-align:center;'><b>CPU</b><br>{cpu_latest:.1f}%</div>",
                    unsafe_allow_html=True
                )
                st.line_chart(metrics.get("CPU_History", []), height=10)
            with col_mem:
                st.markdown(
                    f"<div style='background:#ffd6d6; padding:6px; border-radius:8px; text-align:center;'><b>Memory</b><br>{mem_latest:.1f} MB</div>",
                    unsafe_allow_html=True
                )
                st.line_chart(metrics.get("Memory_History", []), height=10)

            # -----------------------
            # Logs directly below metrics
            # -----------------------
            logs = docker_agent.get_container_logs(c["id"], lines=5)
            with st.expander("📜 Recent Logs", expanded=False):
                if logs:
                    st.markdown(
                        f"<div style='background:#f5f5f5; padding:6px; border-radius:6px;'><pre>{'\n'.join(logs)}</pre></div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.info("No logs available.")

            # -----------------------
            # Separator line for next container
            # -----------------------
            st.markdown("<hr style='border:1px solid #ccc; margin:4px 0;'>", unsafe_allow_html=True)


# =================================================================
# 5️⃣ LOGS DASHBOARD
# =================================================================
elif menu == "Logs":
    st.subheader("📄 Logs Dashboard")

    # -----------------------
    # Select files & level
    # -----------------------
    log_files = ["All"] + logs_agent.available_logs
    selected_file = st.selectbox("Select Log File", log_files)
    level = st.selectbox("Level", ["ALL", "INFO", "WARNING", "ERROR"])

    # Auto-refresh interval
    refresh_interval = st.number_input("Refresh every (seconds)", min_value=1, max_value=60, value=5)

    # Determine files to read
    files_to_read = logs_agent.available_logs if selected_file == "All" else [selected_file]

    # -----------------------
    # Read logs in tail fashion
    # -----------------------
    logs_to_show = {}
    for f in files_to_read:
        new_logs = logs_agent.read_new_logs(f, level)
        if not new_logs:
            # If no new logs, show all existing lines
            new_logs = logs_agent.read_all_logs(f, level)
        logs_to_show[f] = new_logs

    # -----------------------
    # Display logs
    # -----------------------
    for f, lines in logs_to_show.items():
        st.markdown(f"**{f}**")
        if not lines:
            st.info(f"No {level} logs in {f}")
        else:
            st.markdown(
                "<div style='background:#f0f0f0; padding:8px; border-radius:6px; white-space:pre-wrap;'>"
                + "\n".join(lines) +
                "</div>",
                unsafe_allow_html=True
            )

    # -----------------------
    # Create tickets for ERROR logs (only if level is ERROR or ALL)
    # -----------------------
    if level in ["ERROR", "ALL"]:
        if st.button("Create Tickets from ERROR logs"):
            created = logs_agent.create_ticket_from_error(files=files_to_read)
            st.success(f"Created {len(created)} ticket(s)")

    # -----------------------
    # Auto-refresh
    # -----------------------
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=refresh_interval*1000, key="logs_autorefresh")


# =================================================================
# 6️⃣ TICKETS
# =================================================================
elif menu == "Tickets":
    st.subheader("🎫 Active Tickets")
    tickets = logs_agent.list_tickets()
    if not tickets:
        st.info("No tickets available.")
    else:
        for t in tickets:
            with st.expander(f"🎟️ {t['id']} - {t['summary']}"):
                st.write(f"File: {t['source']}")
                st.write(f"Status: {t['status']}")


# =================================================================
# 7️⃣ SCHEDULED TASKS
# =================================================================
elif menu == "Scheduled Tasks":
    st.subheader("⏰ Scheduled Actions")

    scheduled = scheduler.list_scheduled()  # Expected: list of dicts with keys: id, type, target, run_time, status

    if not scheduled:
        st.info("No scheduled actions.")
    else:
        # Sort tasks by scheduled time
        scheduled_sorted = sorted(scheduled, key=lambda x: x['run_time'])

        for task in scheduled_sorted:
            # Format time nicely
            run_time_str = task['run_time'].strftime("%Y-%m-%d %H:%M:%S")

            # Colored/emoji tags for action and status
            action_tag = "▶️ Start" if task['type'] == "Start" else "⏹️ Stop"
            status_tag = "✅ Completed" if task['status'] == "completed" else "⏳ Pending"

            # Expander for clean layout
            with st.expander(f"{action_tag} | {task['target']} | {status_tag}"):
                st.markdown(f"**Target:** {task['target']}")
                st.markdown(f"**Action:** {task['type']}")
                st.markdown(f"**Scheduled Time:** {run_time_str}")
                st.markdown(f"**Status:** {task['status'].capitalize()}")

                # Only show cancel button for pending tasks
                if task['status'] == "pending":
                    if st.button(f"Cancel {task['id']}", key=f"cancel_{task['id']}"):
                        scheduler.cancel_action(task['id'])
                        st.warning(f"⚠️ Scheduled action {task['id']} canceled.")
                        st.rerun()


