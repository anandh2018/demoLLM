# TelecomAI — Architecture & Flow Document

---

## 1. What Is This Project?

**TelecomAI** is a **Multi-Agent AI Customer Service System** for a telecom company.

Instead of a single chatbot, it uses **four specialised AI agents** that each own a specific domain. A supervisor agent (Nova) receives every customer message, verifies identity, and intelligently routes the conversation to the right specialist. Each specialist has access to purpose-built tools to take real actions — looking up invoices, running diagnostics, raising tickets, and fetching retention offers.

**Customer problems it handles:**

| Problem Type | Handled By |
|---|---|
| High bill, invoice query, payment, plan upgrade | Rajan — Billing Specialist |
| Slow internet, dropped calls, network outage | Priya — Tech Support Engineer |
| Wanting to cancel, port-out, loyalty deals | Arjun — Retention Specialist |
| Identity verification, general queries, ticket lookup | Nova — Supervisor |

**Two ways to run it:**
- `python main.py` — terminal / CLI mode
- `streamlit run app.py` — browser-based chat UI

---

## 2. Project File Structure

```
telecom-ai/
│
├── main.py                    ← CLI entry point
├── app.py                     ← Streamlit UI entry point
├── .env                       ← OPENAI_API_KEY
├── requirements.txt
│
└── src/
    ├── config.py              ← Model names, temperature, constants
    ├── models.py              ← LLM + Embeddings singletons (GPT-4o-mini)
    ├── session.py             ← In-memory customer session state
    ├── memory.py              ← FAISS vector store for conversation memory
    │
    ├── agents/
    │   ├── prompts.py         ← System prompts for all 4 agents
    │   └── nodes.py           ← LangGraph node functions for each agent
    │
    ├── graph/
    │   ├── state.py           ← TelecomState TypedDict (shared graph state)
    │   ├── routing.py         ← Conditional routing logic between nodes
    │   └── builder.py         ← Assembles and compiles the StateGraph
    │
    └── tools/
        ├── __init__.py        ← Exports all tool lists (BILLING, TECH, RETAIN, ALL)
        ├── general.py         ← verify_customer, check_ticket_status
        ├── billing.py         ← lookup_invoice, process_payment, upgrade_plan
        ├── technical.py       ← run_network_diagnostic, reset_network_settings, check_tower_status
        └── retention.py       ← get_available_offers, process_cancellation_request
```

---

## 3. Step-by-Step Flow

```
User Message
     │
     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  app.py / main.py  —  Entry Point                                   │
│  Collects user input, maintains conversation history (LangChain     │
│  HumanMessage / AIMessage list), calls graph.invoke()              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  graph.invoke({ messages, current_agent })
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  src/graph/builder.py  —  LangGraph StateGraph                      │
│  Compiled graph with 5 nodes: nova, rajan, priya, arjun, tools      │
│  Entry point is always the "nova" node                               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  START → nova
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  src/agents/nodes.py → nova_node()                                  │
│  1. Calls recall_from_memory() → gets past context from FAISS       │
│  2. Calls nova_system(ctx) → builds system prompt from prompts.py   │
│  3. Calls nova_llm.invoke([SystemMessage] + messages)               │
│     (nova_llm = gpt-4o-mini bound with ALL_TOOLS)                   │
│  4. Returns updated messages + current_agent = "nova"               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  route_nova() inspects last message
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  src/graph/routing.py → route_nova()                                │
│                                                                     │
│  Decision logic:                                                    │
│  ┌─ tool_calls in message? ──────────────────► "tools" node         │
│  ├─ "billing" / "rajan" in content? ──────────► "rajan" node        │
│  ├─ "tech" / "priya" in content? ─────────────► "priya" node        │
│  ├─ "retention" / "arjun" in content? ────────► "arjun" node        │
│  └─ otherwise ──────────────────────────────► END (reply to user)  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
              ┌─────────────────┼──────────────────────┐
              │                 │                      │
              ▼                 ▼                      ▼
        ┌──────────┐     ┌──────────┐          ┌──────────┐
        │  rajan   │     │  priya   │          │  arjun   │
        │  _node() │     │  _node() │          │  _node() │
        └────┬─────┘     └────┬─────┘          └────┬─────┘
             │                │                      │
             └────────────────┴──────────────────────┘
                                │
          Each specialist node does the same pattern:
          1. recall_from_memory(last message)
          2. Build system prompt (rajan/priya/arjun_system)
          3. Invoke LLM with domain-specific tools bound
          4. Returns messages + current_agent = own name
                                │
                                │  specialist_route():
                                │  tool_calls? → "tools"  |  else → END
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LangGraph ToolNode  —  src/tools/                                  │
│  Executes whichever tool the LLM decided to call                    │
│                                                                     │
│  NOVA tools (general.py):                                           │
│    verify_customer(id, phone_last4)  → sets session_state.verified  │
│    check_ticket_status(ticket_id)    → reads from session + memory  │
│                                                                     │
│  RAJAN tools (billing.py):                                          │
│    lookup_invoice(customer_id)       → returns invoice details      │
│    process_payment(customer_id, amt) → creates transaction ID       │
│    upgrade_plan(customer_id, plan)   → changes plan in session      │
│                                                                     │
│  PRIYA tools (technical.py):                                        │
│    run_network_diagnostic(id, type)  → runs check, raises ticket    │
│    reset_network_settings(id)        → sends remote reset command   │
│    check_tower_status(area_code)     → returns tower health status  │
│                                                                     │
│  ARJUN tools (retention.py):                                        │
│    get_available_offers(customer_id) → returns 2 personalised deals │
│    process_cancellation_request(id)  → logs cancellation ticket     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  after_tools():
                                │  return state["current_agent"]
                                │  → routes back to the specialist
                                ▼
                    (specialist processes tool result,
                     generates final natural language reply)
                                │
                                ▼
                              END
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  app.py / main.py  —  Display Response                              │
│  Extracts last AIMessage from result["messages"]                    │
│  Shows agent name + response in UI / terminal                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Detailed Description of Each Step

### Step 1 — Entry Point (`app.py` / `main.py`)

The user types a message. It is wrapped in a `HumanMessage` and appended to the
conversation history list. The full history is passed to `graph.invoke()` every turn
so the LLM always has the complete context.

- **`main.py`** — runs an infinite `input()` loop in the terminal
- **`app.py`** — uses `st.chat_input()` and `st.chat_message()` for a browser UI

---

### Step 2 — Graph Entry (`src/graph/builder.py`)

The `StateGraph` is assembled here and compiled into an executable `graph` object.

- Registers 5 nodes: `nova`, `rajan`, `priya`, `arjun`, `tools`
- Wires edges with conditional routing functions
- Every invocation starts at `nova` via `add_edge(START, "nova")`
- The compiled graph handles all state transitions automatically

---

### Step 3 — Shared State (`src/graph/state.py`)

```python
class TelecomState(TypedDict):
    messages: Annotated[list, add_messages]  # full conversation history
    current_agent: str                        # which agent is active
    memory_context: str                       # FAISS recall result
```

`add_messages` is a LangGraph reducer — it **appends** new messages rather than
replacing them, so every node automatically accumulates the conversation.

---

### Step 4 — Nova Supervisor Node (`src/agents/nodes.py` → `nova_node`)

Nova is the first responder. It:
1. Queries FAISS for relevant past interactions (`recall_from_memory`)
2. Builds a system prompt that includes memory + live session state
3. Invokes GPT-4o-mini with **all 9 tools** bound
4. Decides: answer directly, call a tool, or hand off to a specialist

Nova's system prompt (in `prompts.py`) explicitly instructs it to say
_"Connecting you to Rajan (Billing)"_ — this text triggers the keyword-based
router in `routing.py`.

---

### Step 5 — Routing (`src/graph/routing.py`)

Three routing functions:

| Function | Called After | Logic |
|---|---|---|
| `route_nova` | Nova responds | Keywords or tool_calls → specialist or tools or END |
| `specialist_route` | Any specialist responds | tool_calls → tools, else → END |
| `after_tools` | Tool executes | Returns `state["current_agent"]` → back to specialist |

---

### Step 6 — Specialist Nodes (`src/agents/nodes.py`)

Each specialist follows the same pattern but has a **different system prompt** and
**different tools bound**:

| Node | Bound Tools | Focus |
|---|---|---|
| `rajan_node` | `BILLING_TOOLS` | Invoices, payments, plan changes |
| `priya_node` | `TECH_TOOLS` | Diagnostics, resets, tower checks |
| `arjun_node` | `RETAIN_TOOLS` | Offers, cancellation requests |

---

### Step 7 — Tool Execution (`src/tools/`, LangGraph `ToolNode`)

LangGraph's built-in `ToolNode` automatically:
1. Reads the `tool_calls` from the last AI message
2. Finds the matching `@tool` function
3. Calls it with the arguments the LLM provided
4. Wraps the result in a `ToolMessage` and appends it to state

Each tool also calls `save_to_memory()` to persist the action in FAISS
so future turns can recall it.

---

### Step 8 — Vector Memory (`src/memory.py`)

FAISS in-memory vector store backed by OpenAI `text-embedding-3-small`.

| Function | What it does |
|---|---|
| `save_to_memory(content, metadata)` | Embeds and stores a fact |
| `recall_from_memory(query, k=4)` | Similarity search, returns top-k as a string |
| `create_ticket(type, desc, agent)` | Creates ticket + saves to memory + session |

Every agent query starts with `recall_from_memory(latest_message)` so the LLM
receives relevant history (past invoices, tickets, verifications) as context.

---

### Step 9 — Session State (`src/session.py`)

A plain Python dict that stores the **current user's live state** for the session:

```python
session_state = {
    "customer_id": None,
    "account_name": None,
    "open_tickets": [],
    "plan": None,
    "verified": False,
}
```

This is injected into every agent's system prompt as JSON so the LLM always
knows who it is talking to, what plan they have, and what tickets are open.

---

### Step 10 — System Prompts (`src/agents/prompts.py`)

Each agent has a **dynamic** system prompt. The prompt is a function that
receives the memory context and includes the live session state at call time.

This means the LLM always knows:
- Who the customer is (from `session_state`)
- What happened previously (from FAISS `memory_context`)
- What it is allowed to do (from hardcoded domain rules)

---

## 5. Technologies & Frameworks Used

### LangGraph
**File:** `src/graph/builder.py`, `src/graph/state.py`, `src/graph/routing.py`

LangGraph is the **orchestration engine**. It manages the multi-agent pipeline
as a directed graph of nodes and edges.

Key concepts used:
- `StateGraph` — defines the graph structure
- `TypedDict` state with `add_messages` reducer
- `add_conditional_edges` — dynamic routing based on runtime state
- `ToolNode` (prebuilt) — automatic tool-call execution
- `compile()` — turns the builder into an executable graph

---

### LangChain
**Files:** `src/models.py`, `src/agents/nodes.py`, `src/tools/`

LangChain provides the building blocks:
- `ChatOpenAI` — GPT-4o-mini wrapper with `bind_tools()` support
- `OpenAIEmbeddings` — text-embedding-3-small for FAISS
- `@tool` decorator — turns a Python function into an LLM-callable tool
- `HumanMessage`, `AIMessage`, `SystemMessage` — message types
- `FAISS.from_documents()` — in-memory vector store for memory

---

### FAISS Vector Memory
**File:** `src/memory.py`

FAISS (Facebook AI Similarity Search) is used as a **session-scoped vector memory store**.
Every significant event (verification, invoice lookup, ticket creation, payment) is
embedded and stored. Before each LLM call, the most relevant past events are retrieved
via similarity search and injected into the system prompt.

This gives the agents **persistent short-term memory** within a session.

---

### OpenAI GPT-4o-mini
**File:** `src/models.py`, `src/config.py`

The LLM powering all four agents. Used with:
- `temperature=0.3` — slightly creative but mostly deterministic
- `bind_tools()` — LangChain method that adds tool schemas to the model so it
  can decide when and how to call them (OpenAI function-calling)

---

### Streamlit
**File:** `app.py`

Streamlit turns the CLI application into a browser-based chat UI.

Features used:
- `st.chat_input()` / `st.chat_message()` — native chat components
- `st.session_state` — persists conversation across Streamlit reruns
- `st.sidebar` — shows customer info, tickets, active agent
- `st.rerun()` — refreshes the UI after each agent response

---

### python-dotenv
**File:** `src/models.py`, `.env`

Loads `OPENAI_API_KEY` from the `.env` file before the LLM clients are
instantiated. Critical because `ChatOpenAI` and `OpenAIEmbeddings` are
created at module import time.

---

## 6. Architecture Summary Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ENTRY POINT                                │
│                   app.py  (Streamlit UI)                            │
│                   main.py (Terminal CLI)                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ graph.invoke(messages)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LANGGRAPH STATE GRAPH                           │
│                   src/graph/builder.py                              │
│                                                                     │
│  ┌─────────────┐    route_nova()    ┌─────────┐ ┌───────┐ ┌──────┐ │
│  │    NOVA     │──────────────────► │  RAJAN  │ │ PRIYA │ │ARJUN │ │
│  │ Supervisor  │                    │ Billing │ │ Tech  │ │Reten.│ │
│  └─────────────┘                    └────┬────┘ └───┬───┘ └──┬───┘ │
│         │                               │           │        │     │
│         │     specialist_route()        └───────────┴────────┘     │
│         │           │                              │                │
│         └───────────┴──────────────────────────────┘               │
│                               │ tool_calls?                         │
│                               ▼                                     │
│                     ┌──────────────────┐                            │
│                     │   TOOL NODE      │                            │
│                     │ (LangGraph built-│                            │
│                     │  in ToolNode)    │                            │
│                     └────────┬─────────┘                           │
│                              │ after_tools() → back to agent        │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                     ▼
  ┌───────────────┐  ┌─────────────────┐  ┌────────────────────┐
  │ src/memory.py │  │ src/session.py  │  │   src/tools/       │
  │ FAISS vector  │  │ Customer state  │  │ 9 @tool functions  │
  │ memory store  │  │ (ID, plan,      │  │ Billing · Tech     │
  │ (embed+recall)│  │  tickets, etc.) │  │ Retain · General   │
  └───────────────┘  └─────────────────┘  └────────────────────┘
          │                    │
          └────────────────────┘
          Both injected into every agent's system prompt
          via src/agents/prompts.py before each LLM call
```

---

## 7. Key Design Decisions

| Decision | Why |
|---|---|
| Nova always receives every message first | Single entry point; enforces authentication before specialist access |
| Keyword-based routing in `route_nova` | Simple, fast, no extra LLM call needed; keywords are injected in Nova's prompt |
| Tools call `save_to_memory` internally | Ensures every action is automatically persisted without the agent needing to remember to save |
| Session state injected into system prompt as JSON | Agents always know the current customer context without reading from a database |
| FAISS over ChromaDB | Lightweight, no server needed, in-memory, perfect for session-scoped memory |
| `bind_tools()` per specialist | Each agent only sees its own tools — prevents Rajan from accidentally calling a network reset |
