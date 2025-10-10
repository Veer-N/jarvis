# 2025-10-10
# Author: Veer
# App Name: Jarvis

This App/tool is to automate the following:
1. Show details of all EC2s and RDSs from AWS
2. Local and remote Docker containers running
3. Logs of applications running on servers
4. Automated ticket generation from ERRORs in logs
5. Scheduling os start/stop of EC2s and RDSs

more to follow...

Perfect question 👍 — this is exactly what you’ll need to share if someone else wants to **run Jarvis locally** right now.

Here’s the clean **setup guide** you should send them 👇

---

## 🧠 Jarvis — Local Setup Guide

### 🔹 1. Prerequisites

Make sure these are installed on the system:

* **Python 3.12+** → [https://www.python.org/downloads/](https://www.python.org/downloads/)
* **Git** → [https://git-scm.com/downloads](https://git-scm.com/downloads)
* **Docker Desktop** (for Docker dashboard features) → [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
* **AWS CLI** (for EC2/RDS operations) → [https://aws.amazon.com/cli/](https://aws.amazon.com/cli/)

  ```bash
  aws configure
  ```

  (enter AWS Access Key, Secret, region, and default output as JSON)

### 🔹 2. Clone the project

```bash
git clone <YOUR_JARVIS_REPO_URL>
cd jarvis
```

### 🔹 3. Create a Python virtual environment

```bash
python -m venv venv
```

Activate it:

* On Windows

  ```bash
  venv\Scripts\activate
  ```
* On macOS/Linux

  ```bash
  source venv/bin/activate
  ```

### 🔹 4. Install dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, create one with:

```txt
streamlit
boto3
docker
requests
```

You can expand this list later as we add Jira integration (will add `jira` package then).

### 🔹 5. Run the Jarvis app

Inside the `ui` folder (where `main.py` is):

```bash
streamlit run main.py
```

The app will launch in your browser at:
👉 [http://localhost:8501](http://localhost:8501)

### 🔹 6. Optional (for mock logs demo)

If the app doesn’t automatically create mock logs, run this once:

```bash
python log_agent.py
```

---

✅ That’s it!
They’ll now have **Jarvis running locally** with EC2, RDS, Docker, and Logs dashboards (using their own AWS credentials).

Would you like me to generate a ready `requirements.txt` file right now (based on all modules used so far)?
