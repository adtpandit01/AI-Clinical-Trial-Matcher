import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Clinical Trial Matcher",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 AI Clinical Trial Matcher")
st.markdown("AI system that matches patient descriptions to relevant clinical trials.")

# -----------------------------
# SESSION STATE
# -----------------------------
if "token" not in st.session_state:
    st.session_state["token"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("User Account")

# -----------------------------
# LOGGED IN VIEW
# -----------------------------
if st.session_state["token"]:

    st.sidebar.success(f"Logged in as {st.session_state['username']}")

    if st.sidebar.button("Logout"):
        st.session_state["token"] = None
        st.session_state["username"] = None
        st.rerun()

# -----------------------------
# NOT LOGGED IN VIEW
# -----------------------------
else:

    auth_option = st.sidebar.radio(
        "Authentication",
        ["Login", "Register", "Reset Password"]
    )

    # -----------------------------
    # REGISTER
    # -----------------------------
    if auth_option == "Register":

        st.sidebar.subheader("Create Account")

        username = st.sidebar.text_input("Username", key="register_user")
        email = st.sidebar.text_input("Email", key="register_email")
        password = st.sidebar.text_input("Password", type="password", key="register_pass")

        if st.sidebar.button("Register"):

            payload = {
                "username": username,
                "email": email,
                "password": password,
                "role": "user"
            }

            response = requests.post(f"{API_URL}/register", json=payload)

            if response.status_code == 200:
                st.sidebar.success("Account created successfully")
            else:
                st.sidebar.error("Registration failed")

    # -----------------------------
    # LOGIN
    # -----------------------------
    elif auth_option == "Login":

        st.sidebar.subheader("Login")

        username = st.sidebar.text_input("Username", key="login_user")
        password = st.sidebar.text_input("Password", type="password", key="login_pass")

        if st.sidebar.button("Login"):

            payload = {
                "username": username,
                "password": password
            }

            response = requests.post(f"{API_URL}/login", json=payload)

            if response.status_code == 200:

                token = response.json()["access_token"]

                st.session_state["token"] = token
                st.session_state["username"] = username

                st.sidebar.success("Login successful")
                st.rerun()

            else:
                st.sidebar.error("Invalid credentials")

    # -----------------------------
    # RESET PASSWORD
    # -----------------------------
    elif auth_option == "Reset Password":

        st.sidebar.subheader("Reset Password")

        username = st.sidebar.text_input("Username", key="reset_user")
        new_password = st.sidebar.text_input("New Password", type="password", key="reset_pass")

        if st.sidebar.button("Reset Password"):

            payload = {
                "username": username,
                "new_password": new_password
            }

            response = requests.post(f"{API_URL}/reset-password", params=payload)

            if response.status_code == 200:
                st.sidebar.success("Password updated")
            else:
                st.sidebar.error("Reset failed")


# -----------------------------
# MAIN APP
# -----------------------------

st.divider()

st.header("Clinical Trial Search")

patient_text = st.text_area(
    "Patient Description",
    placeholder="Example: 60 year old male with stage IV lung cancer"
)

if st.button("Find Matching Trials"):

    if not st.session_state["token"]:
        st.error("Please login first to use the AI matcher.")
        st.stop()

    payload = {"patient_profile": patient_text}

    headers = {
        "Authorization": f"Bearer {st.session_state['token']}"
    }

    with st.spinner("AI is analyzing patient eligibility and searching clinical trials..."):

        response = requests.post(
            f"{API_URL}/match-patient",
            json=payload,
            headers=headers
        )

    if response.status_code != 200:
        st.error("API request failed")
        st.stop()

    data = response.json()
    matches = data.get("matches", [])

    if not matches:
        st.warning("No matching trials found.")
        st.stop()

    st.success(f"{len(matches)} matching trials found")

    # -----------------------------
    # RESULTS DISPLAY
    # -----------------------------
    for i, match in enumerate(matches):

        score = match["similarity_score"]
        percent = int(score * 100)

        if i == 0:
            label = "🏆 Best Match"
        elif i == 1:
            label = "🥈 Strong Match"
        else:
            label = "🥉 Possible Match"

        with st.container():

            st.markdown(f"### {label}")

            st.markdown(f"#### {match['title']}")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Condition:**")
                st.write(match["condition"])

            with col2:
                st.write("**Trial ID:**")
                st.write(match["nct_id"])

            st.write("**Similarity Score**")

            st.progress(score)

            st.write(f"{percent}% match")

            trial_link = f"https://clinicaltrials.gov/study/{match['nct_id']}"

            st.link_button("View Full Trial Details", trial_link)

            st.write("**AI Explanation**")

            st.success(match["reason"])

            st.divider()