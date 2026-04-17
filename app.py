import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
import time

st.set_page_config(page_title="AI Outreach Engine", page_icon="", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; background:#f5f7fa !important; color:#1a1a2e !important; }
  .main .block-container { padding: 2rem 2.5rem; }
  section[data-testid="stSidebar"] { background: #1e1b4b !important; }
  section[data-testid="stSidebar"] * { color: #ffffff !important; }
  section[data-testid="stSidebar"] input,
  section[data-testid="stSidebar"] textarea {
    background: #312e81 !important; color: #fff !important;
    border: 1px solid #6366f1 !important; border-radius: 8px !important;
  }
  section[data-testid="stSidebar"] label p { color: #c7d2fe !important; font-weight: 500 !important; }
  section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #312e81 !important; border: 1.5px solid #6366f1 !important;
    border-radius: 8px !important; color: #ffffff !important;
  }
  section[data-testid="stSidebar"] .stSelectbox > div > div > div { color: #ffffff !important; }
  section[data-testid="stSidebar"] .stSelectbox svg { fill: #ffffff !important; }
  [data-baseweb="popover"] ul { background: #312e81 !important; border: 1px solid #6366f1 !important; }
  [data-baseweb="popover"] li { background: #312e81 !important; color: #ffffff !important; }
  [data-baseweb="popover"] li:hover { background: #4f46e5 !important; }
  h1 { font-size:2rem !important; font-weight:700 !important; color:#1e1b4b !important; }
  h2, h3 { font-weight:600 !important; color:#1e1b4b !important; }
  .stTabs [data-baseweb="tab-list"] { background:#fff; border-radius:12px; padding:4px; border:1.5px solid #e0e7ff; gap:4px; }
  .stTabs [data-baseweb="tab"] { background:transparent; color:#6b7280 !important; font-weight:500; border-radius:8px; padding:0.5rem 1.2rem; }
  .stTabs [aria-selected="true"] { background:#4f46e5 !important; color:#fff !important; font-weight:600 !important; }
  .stButton > button { background:#4f46e5 !important; color:#fff !important; border:none !important; border-radius:8px !important; font-weight:600 !important; padding:0.6rem 1.8rem !important; width:100%; }
  .stButton > button:hover { background:#4338ca !important; }
  .stDownloadButton > button { background:#059669 !important; color:#fff !important; border:none !important; border-radius:8px !important; font-weight:600 !important; }
  .stTextInput input, .stTextArea textarea { background:#fff !important; color:#111827 !important; border:1.5px solid #d1d5db !important; border-radius:8px !important; }
  .stSelectbox > div > div { background:#fff !important; border:1.5px solid #d1d5db !important; border-radius:8px !important; color:#111827 !important; }
  [data-testid="stFileUploader"] { background:#fff !important; border:2px dashed #c7d2fe !important; border-radius:10px !important; }
  .stProgress > div > div > div { background: linear-gradient(90deg,#4f46e5,#7c3aed) !important; border-radius:4px !important; }
  .metric-card { background:#fff; border:1.5px solid #e0e7ff; border-radius:14px; padding:1.2rem 1rem; text-align:center; box-shadow:0 2px 8px rgba(79,70,229,0.07); }
  .metric-card .num { font-size:2rem; font-weight:700; color:#4f46e5; line-height:1.1; }
  .metric-card .label { font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.8px; margin-top:4px; }
  .msg-preview { background:#fff; border:1.5px solid #e0e7ff; border-left:4px solid #4f46e5; border-radius:10px; padding:1rem 1.2rem; margin-bottom:0.6rem; color:#374151; font-size:0.9rem; line-height:1.6; }
  .msg-lead { font-size:0.78rem; font-weight:600; color:#4f46e5; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px; }
  label p { color:#374151 !important; font-weight:500 !important; }
  hr { border-color:#e0e7ff !important; }
  #MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

SAMPLE_CSV = (
    "name,company,role,extra_context\n"
    "Alice Johnson,Acme Corp,VP of Sales,Recently expanded into APAC markets\n"
    "Bob Chen,TechFlow,CTO,Open-source contributor and developer tools enthusiast\n"
    "Maria Gomez,StartupX,Founder,Just raised a Series A and is aggressively hiring\n"
    "David Kim,RetailGiant,Head of Marketing,Keynote speaker at NRF 2024 on AI personalization\n"
    "Priya Patel,FinTech Inc,Product Manager,Background in ML and payments infrastructure\n"
    "James Wright,HealthPlus,Director of Operations,Overseeing digital transformation of a large hospital\n"
    "Sophie Dubois,GreenWave,Sustainability Lead,Running a net-zero initiative and presented at COP28\n"
    "Luca Ferrari,AutoTech,VP Engineering,Building autonomous vehicle software and is ex-Tesla\n"
    "Ananya Iyer,EduLeap,Co-founder,EdTech platform serving 200k students across India\n"
    "Carlos Mendoza,LogiChain,COO,Recently migrated supply chain to cloud-native architecture\n"
)

def parse_csv(content: str) -> pd.DataFrame:
    cleaned = content.strip()
    if not cleaned:
        return pd.DataFrame()
    try:
        df = pd.read_csv(io.StringIO(cleaned))
        return df
    except Exception:
        try:
            df = pd.read_csv(io.StringIO(cleaned), on_bad_lines="skip", engine="python")
            return df
        except Exception as e:
            st.error(f"Could not parse CSV: {e}")
            return pd.DataFrame()

def build_prompt(row, purpose, tone, sender_name, sender_company, extra, message_type):
    lead_info = "\n".join(f"  {k}: {v}" for k, v in row.items())
    return f"""You are an expert outreach specialist. Generate a highly personalized {message_type}.

OUTREACH PURPOSE: {purpose}
TONE: {tone}
FROM: {sender_name} at {sender_company}
EXTRA INSTRUCTIONS: {extra if extra else "None"}

LEAD DETAILS:
{lead_info}

RULES:
- Reference specific details about this lead (name, company, role, context)
- Keep it concise: 3-5 short paragraphs
- End with a clear easy CTA
- Do NOT use "I hope this finds you well" or generic openers
- Sound human and specific, not like a template
- Output ONLY the message body, no subject line, no extra commentary
"""

def generate_message(client, prompt):
    response = client.generate_content(prompt)
    return response.text.strip()

def results_to_csv(df, messages):
    out = df.copy()
    out["generated_message"] = messages
    return out.to_csv(index=False)

for key, default in [("lead_df", pd.DataFrame()), ("messages_out", []),
                     ("processed_df", pd.DataFrame()), ("limit", 5),
                     ("selected_df", pd.DataFrame()), ("random_df", pd.DataFrame())]:
    if key not in st.session_state:
        st.session_state[key] = default

# Sidebar
with st.sidebar:
    st.markdown("## Configuration")
    st.markdown("---")
    st.markdown("### API Key")
    api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIza...")
    if api_key:
        st.success("Key entered")

    st.markdown("---")
    st.markdown("### Campaign Settings")
    purpose      = st.text_area("Outreach Purpose *",
                                 placeholder="e.g. Invite prospects to a free demo of our AI platform",
                                 height=100)
    message_type = st.selectbox("Message Type",
                                 ["email", "LinkedIn message", "cold DM", "follow-up email"])
    tone         = st.selectbox("Tone",
                                 ["Professional & concise", "Friendly & conversational",
                                  "Bold & direct", "Warm & empathetic", "Formal"])

    st.markdown("---")
    st.markdown("### Sender Info")
    sender_name    = st.text_input("Your Name *",    placeholder="e.g. Rahul Sharma")
    sender_company = st.text_input("Your Company *", placeholder="e.g. Nexus AI")
    extra          = st.text_area("Extra Instructions (optional)",
                                   placeholder="e.g. Mention free trial. Avoid competitor names.",
                                   height=80)
    st.markdown("---")

# Header
st.markdown("# AI Outreach Engine")
st.markdown("Generate **personalized messages at scale** — powered by Gemini AI")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["  Step 1 - Add Leads  ", "  Step 2 - Generate  ", "  Step 3 - Results  "])

# TAB 1
with tab1:
    st.markdown("### Add Your Lead List")
    st.markdown("Choose one of the three options below to load your leads.")
    st.markdown("")

    st.markdown("#### Option 1 - Try with sample data")
    if st.button("Load Sample Data (10 leads) - recommended for first try"):
        st.session_state.lead_df = parse_csv(SAMPLE_CSV)
        st.success("Sample data loaded! Scroll down to see the leads table.")

    st.markdown("")
    st.markdown("---")
    st.markdown("#### Option 2 - Upload your CSV file")
    uploaded = st.file_uploader("Drag and drop or browse your CSV", type=["csv"],
                                 label_visibility="collapsed")
    if uploaded is not None:
        raw = uploaded.read().decode("utf-8")
        df_up = parse_csv(raw)
        if not df_up.empty:
            st.session_state.lead_df = df_up
            st.success(f"File loaded — {len(df_up)} leads found!")

    st.markdown("")
    st.markdown("---")
    st.markdown("#### Option 3 - Paste CSV text")
    csv_text = st.text_area(
        "Paste your CSV content here (must have a header row)",
        height=120,
        placeholder="name,company,role\nAlice Johnson,Acme Corp,VP Sales\nBob Chen,TechFlow,CTO",
        label_visibility="collapsed"
    )
    if st.button("Parse Pasted CSV"):
        if csv_text.strip() and len(csv_text.strip().splitlines()) > 1:
            df_pasted = parse_csv(csv_text)
            if not df_pasted.empty:
                st.session_state.lead_df = df_pasted
                st.success(f"Parsed — {len(df_pasted)} leads found!")
        else:
            st.warning("Please paste at least 2 lines (header + 1 lead).")

    if not st.session_state.lead_df.empty:
        df = st.session_state.lead_df
        st.markdown("---")
        st.markdown("### Leads Loaded Successfully")

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><div class="num">{len(df)}</div><div class="label">Total Leads</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="num">{len(df.columns)}</div><div class="label">Data Fields</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="num">~{len(df)*4}s</div><div class="label">Est. Time</div></div>', unsafe_allow_html=True)

        st.markdown("")
        st.dataframe(df, use_container_width=True, height=260)

        st.markdown("")
        st.markdown("### Select Leads to Process")

        select_mode = st.radio(
            "How do you want to select leads?",
            ["First N leads (sequential)", "Hand-pick specific leads", "Random sample"],
            horizontal=True
        )

        if select_mode == "First N leads (sequential)":
            st.session_state.limit = st.slider(
                "How many leads from the top?", 1, len(df), min(len(df), 5),
                label_visibility="collapsed"
            )
            selected_df = df.head(st.session_state.limit).reset_index(drop=True)
            st.info(f"Will use first **{st.session_state.limit}** leads in order.")

        elif select_mode == "Hand-pick specific leads":
            lead_options = df["name"].tolist()
            picked = st.multiselect(
                "Select leads by name (search or scroll):",
                options=lead_options,
                default=lead_options[:5]
            )
            selected_df = df[df["name"].isin(picked)].reset_index(drop=True)
            st.session_state.limit = len(selected_df)
            if picked:
                st.info(f"**{len(picked)}** leads selected.")
            else:
                st.warning("Please select at least one lead.")
                selected_df = pd.DataFrame()

        elif select_mode == "Random sample":
            n = st.slider("How many random leads?", 1, len(df), min(len(df), 5),
                          label_visibility="collapsed")
            if st.button("Randomise Selection"):
                st.session_state.random_df = df.sample(n=n).reset_index(drop=True)
            if st.session_state.random_df.empty or len(st.session_state.random_df) != n:
                st.session_state.random_df = df.sample(n=n).reset_index(drop=True)
            selected_df = st.session_state.random_df
            st.session_state.limit = n
            st.info(f"**{n}** random leads selected. Click Randomise to shuffle again.")

        st.session_state.selected_df = selected_df

        if not selected_df.empty:
            st.markdown("**Preview of selected leads:**")
            preview_cols = [c for c in ["name", "company", "role"] if c in selected_df.columns]
            st.dataframe(selected_df[preview_cols].reset_index(drop=True),
                         use_container_width=True, height=200)
            st.success(f"{len(selected_df)} lead(s) ready - go to Step 2 to generate!")
    else:
        st.markdown("")
        st.info("Use any option above to load your leads.")

# TAB 2
with tab2:
    st.markdown("### Generate Personalized Messages")
    st.markdown("")

    missing = []
    if not api_key:                                        missing.append("API Key (sidebar)")
    if not purpose:                                        missing.append("Outreach Purpose (sidebar)")
    if not sender_name:                                    missing.append("Your Name (sidebar)")
    if not sender_company:                                 missing.append("Your Company (sidebar)")
    if st.session_state.get("selected_df", pd.DataFrame()).empty and st.session_state.lead_df.empty:
        missing.append("Lead list (Step 1 tab)")

    if missing:
        st.warning("**Please complete the following before generating:**")
        for m in missing:
            st.markdown(f"   - {m}")
    else:
        sel_df = st.session_state.get("selected_df", pd.DataFrame())
        if sel_df.empty:
            sel_df = st.session_state.lead_df.head(st.session_state.get("limit", 5))
        limit = len(sel_df)

        st.markdown("#### Campaign Summary")
        ca, cb, cc, cd = st.columns(4)
        ca.markdown(f'<div class="metric-card"><div class="num">{limit}</div><div class="label">Messages</div></div>', unsafe_allow_html=True)
        cb.markdown(f'<div class="metric-card"><div class="num" style="font-size:1rem;padding-top:6px">{message_type}</div><div class="label">Type</div></div>', unsafe_allow_html=True)
        cc.markdown(f'<div class="metric-card"><div class="num" style="font-size:0.9rem;padding-top:6px">{tone.split()[0]}</div><div class="label">Tone</div></div>', unsafe_allow_html=True)
        cd.markdown(f'<div class="metric-card"><div class="num" style="font-size:0.9rem;padding-top:6px">{sender_name.split()[0] if sender_name else ""}</div><div class="label">Sender</div></div>', unsafe_allow_html=True)
        st.markdown("")

        if st.button("Generate Messages Now"):
            genai.configure(api_key=api_key)
            client = genai.GenerativeModel("gemini-2.5-flash")
            messages_out, errors = [], []

            st.markdown("---")
            st.markdown("#### Generating...")
            prog    = st.progress(0)
            status  = st.empty()
            preview = st.empty()

            for i, (_, row) in enumerate(sel_df.iterrows()):
                name    = str(row.get("name",    f"Lead {i+1}"))
                company = str(row.get("company", ""))
                status.markdown(f"**Processing:** {name} - {company}   ({i+1}/{limit})")

                try:
                    msg = generate_message(
                        client,
                        build_prompt(row.to_dict(), purpose, tone,
                                     sender_name, sender_company, extra, message_type)
                    )
                    messages_out.append(msg)
                    preview.markdown(
                        f'<div class="msg-preview">' +
                        f'<div class="msg-lead">{name} · {company}</div>' +
                        f'{msg[:300]}{"..." if len(msg) > 300 else ""}</div>',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    messages_out.append(f"[ERROR] {e}")
                    errors.append(name)

                prog.progress((i + 1) / limit)
                time.sleep(4)

            st.session_state.messages_out = messages_out
            st.session_state.processed_df = sel_df.reset_index(drop=True)
            status.empty()
            preview.empty()

            if errors:
                st.warning(f"Failed for: {', '.join(errors)}")
            st.success(f"Done! **{limit - len(errors)} messages** generated. Go to Step 3 to view and download!")

# TAB 3
with tab3:
    st.markdown("### Results")

    if not st.session_state.messages_out:
        st.info("No messages yet - complete Steps 1 and 2 first.")
    else:
        msgs   = st.session_state.messages_out
        df_out = st.session_state.processed_df
        total  = len(msgs)
        ok     = sum(1 for m in msgs if not m.startswith("[ERROR]"))

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><div class="num">{total}</div><div class="label">Generated</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="num" style="color:#059669">{ok}</div><div class="label">Succeeded</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="num" style="color:#dc2626">{total - ok}</div><div class="label">Errors</div></div>', unsafe_allow_html=True)
        st.markdown("")

        st.download_button(
            "Download All Messages as CSV",
            data=results_to_csv(df_out, msgs),
            file_name="outreach_messages.csv",
            mime="text/csv"
        )

        st.markdown("---")
        st.markdown("### Browse Messages")
        search = st.text_input("Filter by name", placeholder="Type a name to search...")

        for i, (_, row) in enumerate(df_out.iterrows()):
            name    = str(row.get("name",    f"Lead {i+1}"))
            company = str(row.get("company", ""))
            role    = str(row.get("role",    ""))

            if search.strip() and search.strip().lower() not in name.lower():
                continue

            label = f"{name}"
            if company: label += f"  -  {company}"
            if role:    label += f"  |  {role}"

            with st.expander(label):
                msg = msgs[i]
                st.text_area("", value=msg, height=240, key=f"ta_{i}")
                st.download_button(
                    "Download this message",
                    data=f'name,message\n"{name}","{msg.replace(chr(34), chr(39))}"\n',
                    file_name=f"msg_{name.replace(' ', '_')}.csv",
                    key=f"dl_{i}"
                )
