# ✉️ AI Outreach Engine

A mini AI-powered outreach system that generates **personalized messages/emails at scale** using Claude (Anthropic LLM).

---

## Features

-  **Generic purpose** — works for sales, recruiting, marketing, partnerships, anything
-  **CSV-based lead input** — upload a file, paste text, or load the sample
-  **Claude-powered generation** — each message is uniquely personalized using all lead fields
-  **Bulk generation** — process 1 to 500+ leads with a progress bar
-  **Configurable** — set tone, message type, sender info, and custom instructions
-  **CSV export** — download all results in one click
-  **Preview & filter** — browse individual messages by name

---

## Quick Start

### 1. Clone / download this folder

```bash
cd ai_outreach
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## How to Use

1. **Sidebar → API Key**: Enter your Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))
2. **Sidebar → Campaign Settings**: Set your outreach purpose, message type, and tone
3. **Sidebar → Sender Info**: Your name and company
4. **Leads tab**: Upload your CSV or click "Load Sample CSV"
5. **Generate tab**: Hit Generate — watch messages appear in real time
6. **Results tab**: Preview, filter, and download your personalized messages

---

## CSV Format

Your lead CSV can have **any columns** — Claude will use them all for personalization.

**Minimum required:**
```
name
```

**Recommended columns:**
```
name, company, role, extra_context
```

**Example:**
```csv
name,company,role,extra_context
Alice Johnson,Acme Corp,VP of Sales,Recently expanded into APAC
Bob Chen,TechFlow,CTO,Open-source contributor
```

A sample file `sample_leads.csv` (10 leads) is included.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| UI | Streamlit |
| LLM | Claude (claude-opus-4-5 via Anthropic API) |
| Data | Pandas |
| Language | Python 3.9+ |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                   │
│  ┌─────────┐  ┌───────────┐  ┌──────────────┐  │
│  │  Leads  │  │  Generate │  │   Results    │  │
│  │  Tab    │  │   Tab     │  │    Tab       │  │
│  └────┬────┘  └─────┬─────┘  └──────┬───────┘  │
│       │             │               │           │
│       ▼             ▼               ▼           │
│  ┌─────────────────────────────────────────┐    │
│  │           Session State                 │    │
│  │   lead_df | messages_out | processed_df │    │
│  └─────────────────┬───────────────────────┘    │
│                    │                            │
│                    ▼                            │
│  ┌─────────────────────────────────────────┐    │
│  │         generate_message()              │    │
│  │   build_prompt() → Anthropic API call   │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

---

## Notes

- Rate limiting: A 300ms delay between API calls prevents throttling
- Errors are captured per-lead; failed messages are marked `[ERROR]` in the export
- Works with any number of CSV columns — the more context, the better the personalization

API Key : AIzaSyB4RtblOVW4npnvkYrGTlci78S8tIts4ic
