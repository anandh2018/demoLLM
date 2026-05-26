"""
TelecomAI — Streamlit Chat UI
Multi-agent customer service with Nova, Rajan, Priya, and Arjun.
Run: streamlit run app.py
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from src.graph.builder import graph
from src.session import session_state, reset_session_state
from src.memory import save_to_memory

# ── Agent metadata ─────────────────────────────────────────────────────────────
AGENTS = {
    "nova":  {"name": "Nova",  "role": "Supervisor",   "emoji": "🤖", "color": "#4A90D9"},
    "rajan": {"name": "Rajan", "role": "Billing",      "emoji": "💳", "color": "#E67E22"},
    "priya": {"name": "Priya", "role": "Tech Support", "emoji": "🔧", "color": "#2ECC71"},
    "arjun": {"name": "Arjun", "role": "Retention",    "emoji": "🤝", "color": "#9B59B6"},
}

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TelecomAI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .agent-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 4px;
        color: white;
    }
    .ticket-card {
        background: #1e2130;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-left: 3px solid #4A90D9;
    }
    .status-open   { border-left-color: #E74C3C !important; }
    .status-closed { border-left-color: #2ECC71 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state initialisation ───────────────────────────────────────────────
if "lc_messages" not in st.session_state:
    st.session_state.lc_messages = []       # actual LangChain message objects
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []  # {role, content, agent}
if "last_agent" not in st.session_state:
    st.session_state.last_agent = "nova"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📡 TelecomAI")
    st.caption("Multi-Agent Customer Service")
    st.divider()

    # ── Customer info ──────────────────────────────────────────────────────────
    st.markdown("### 👤 Customer")
    if session_state.get("verified"):
        st.success("Verified ✅")
        cols = st.columns(2)
        cols[0].metric("ID",   session_state.get("customer_id", "—"))
        cols[1].metric("Plan", session_state.get("plan", "—") or "—")
        if session_state.get("account_name"):
            st.caption(f"Name: {session_state['account_name']}")
    else:
        st.info("Not yet verified.\nProvide your customer ID to begin.")

    st.divider()

    # ── Active agent ───────────────────────────────────────────────────────────
    st.markdown("### 🤝 Active Agent")
    a = AGENTS.get(st.session_state.last_agent, AGENTS["nova"])
    color = a["color"]
    st.markdown(
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:10px;font-weight:600">{a["emoji"]} {a["name"]}</span> '
        f'<span style="color:#aaa;font-size:0.85rem">{a["role"]}</span>',
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Open tickets ───────────────────────────────────────────────────────────
    st.markdown("### 🎫 Tickets")
    tickets = session_state.get("open_tickets", [])
    if tickets:
        for t in reversed(tickets):
            status_class = "status-open" if t["status"] == "Open" else "status-closed"
            st.markdown(
                f'<div class="ticket-card {status_class}">'
                f'<b>{t["ticket_id"]}</b> · {t["issue_type"]}<br>'
                f'<span style="font-size:0.8rem;color:#aaa">'
                f'{t["status"]} · {t["assigned_to"]} · {t["created_at"]}'
                f'</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("No tickets yet.")

    st.divider()

    # ── Controls ───────────────────────────────────────────────────────────────
    if st.button("🔄 Reset Session", use_container_width=True, type="secondary"):
        st.session_state.lc_messages = []
        st.session_state.display_messages = []
        st.session_state.last_agent = "nova"
        reset_session_state()
        st.rerun()

    st.caption("Vector memory is preserved across resets.")

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("## 📡 TelecomAI Customer Service")
st.caption("Talk to our AI agents for billing, technical support, and account help.")
st.divider()

# Replay conversation
for msg in st.session_state.display_messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        agent_info = AGENTS.get(msg.get("agent", "nova"), AGENTS["nova"])
        with st.chat_message("assistant", avatar=agent_info["emoji"]):
            color = agent_info["color"]
            st.markdown(
                f'<span class="agent-badge" style="background:{color}">'
                f'{agent_info["emoji"]} {agent_info["name"]} · {agent_info["role"]}'
                f'</span>',
                unsafe_allow_html=True,
            )
            st.write(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
user_input = st.chat_input("Describe your issue or ask a question…")

if user_input:
    # Show user message right away
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.display_messages.append({"role": "user", "content": user_input})
    st.session_state.lc_messages.append(HumanMessage(content=user_input))

    # Persist to vector memory if customer known
    if session_state.get("customer_id"):
        save_to_memory(
            f"User said: {user_input}",
            {"type": "conversation", "customer_id": session_state["customer_id"]},
        )

    # Invoke the LangGraph pipeline
    with st.spinner("Agents thinking…"):
        result = graph.invoke(
            {
                "messages": st.session_state.lc_messages,
                "current_agent": "nova",
                "memory_context": "",
            },
            config={"recursion_limit": 20},
        )

    # Sync LangChain history with what the graph returned
    st.session_state.lc_messages = result["messages"]
    current_agent = result.get("current_agent", "nova")
    st.session_state.last_agent = current_agent
    agent_info = AGENTS.get(current_agent, AGENTS["nova"])

    # Extract the latest AI reply
    response_text = "I'm sorry, I couldn't process your request."
    for m in reversed(result["messages"]):
        if isinstance(m, AIMessage) and m.content:
            response_text = m.content
            break

    # Show the reply
    with st.chat_message("assistant", avatar=agent_info["emoji"]):
        color = agent_info["color"]
        st.markdown(
            f'<span class="agent-badge" style="background:{color}">'
            f'{agent_info["emoji"]} {agent_info["name"]} · {agent_info["role"]}'
            f'</span>',
            unsafe_allow_html=True,
        )
        st.write(response_text)

    st.session_state.display_messages.append({
        "role": "assistant",
        "content": response_text,
        "agent": current_agent,
    })

    # Rerun so sidebar (tickets, agent badge, customer info) refreshes
    st.rerun()
