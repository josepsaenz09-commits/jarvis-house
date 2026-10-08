import os
import re
import json
import sqlite3
import urllib.parse
import urllib.request
import urllib.error
import threading
import time
from datetime import datetime

from flask import Flask, request, jsonify, Response

from openai import OpenAI


# ============================================================
# J.A.R.V.I.S. COMMAND CENTER
# ALL-IN-ONE SERVER
# Brain + Memory + Web + Voice UI + Agents + Tools
# Gmail/WhatsApp integration points included
# ============================================================

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "8000"))

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

ai = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

DB_FILE = "jarvis_memory.db"


# ============================================================
# DATABASE / MEMORY
# ============================================================

def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


def save_memory(content):
    conn = db()
    conn.execute(
        "INSERT INTO memories(content, created_at) VALUES (?, ?)",
        (content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_memories(limit=30):
    conn = db()
    rows = conn.execute(
        "SELECT content, created_at FROM memories ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return list(rows)


def save_conversation(role, content):
    conn = db()
    conn.execute(
        "INSERT INTO conversations(role, content, created_at) VALUES (?, ?, ?)",
        (role, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


# ============================================================
# WEB SEARCH
# ============================================================

def search_web(query, max_results=6):
    """
    Basic internet search using DuckDuckGo HTML.
    No additional Python package required.
    """

    try:
        encoded = urllib.parse.quote_plus(query)

        url = (
            "https://html.duckduckgo.com/html/"
            "?q=" + encoded
        )

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0 (Linux; Android 14) "
                "AppleWebKit/537.36 "
                "Chrome/120 Mobile Safari/537.36"
            }
        )

        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode(
                "utf-8",
                errors="ignore"
            )

        results = []

        blocks = re.findall(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            re.I | re.S
        )

        for link, title in blocks[:max_results]:
            title = re.sub("<.*?>", "", title)
            title = title.replace("&amp;", "&")

            if link.startswith("//"):
                link = "https:" + link

            results.append({
                "title": title.strip(),
                "url": link.strip()
            })

        return results

    except Exception as e:
        return [{
            "title": "Web search error",
            "url": "",
            "error": str(e)
        }]


def format_search_results(results):
    if not results:
        return "No se encontraron resultados."

    text = []

    for i, result in enumerate(results, 1):
        text.append(
            f"{i}. {result.get('title', '')}\n"
            f"{result.get('url', '')}"
        )

    return "\n\n".join(text)


def needs_web_search(message):
    words = [
        "busca",
        "buscar",
        "búscame",
        "buscame",
        "investiga",
        "internet",
        "en la web",
        "web",
        "noticias",
        "últimas noticias",
        "ultimas noticias",
        "qué pasó hoy",
        "que paso hoy",
        "actualmente",
        "ahora mismo",
        "precio actual",
        "información actual",
        "informacion actual"
    ]

    msg = message.lower()

    return any(word in msg for word in words)


def extract_search_query(message):
    patterns = [
        r"búscame\s+(.+)",
        r"buscame\s+(.+)",
        r"busca\s+(.+)",
        r"buscar\s+(.+)",
        r"investiga\s+(.+)",
        r"noticias\s+(?:sobre\s+)?(.+)",
        r"qué pasó hoy\s+(.+)",
        r"que paso hoy\s+(.+)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            message,
            re.I
        )

        if match:
            return match.group(1).strip()

    return message


# ============================================================
# MEMORY COMMANDS
# ============================================================

def is_memory_command(message):
    msg = message.lower().strip()

    starts = [
        "recuerda ",
        "recuerda que ",
        "guarda ",
        "guarda que ",
        "memoriza ",
        "memoriza que "
    ]

    return any(msg.startswith(x) for x in starts)


def extract_memory(message):
    msg = message.strip()

    patterns = [
        r"^recuerda\s+que\s+(.+)$",
        r"^recuerda\s+(.+)$",
        r"^guarda\s+que\s+(.+)$",
        r"^guarda\s+(.+)$",
        r"^memoriza\s+que\s+(.+)$",
        r"^memoriza\s+(.+)$"
    ]

    for pattern in patterns:
        match = re.match(
            pattern,
            msg,
            re.I
        )

        if match:
            return match.group(1).strip()

    return msg


# ============================================================
# TASK SYSTEM
# ============================================================

def create_task(title):
    conn = db()

    conn.execute(
        """
        INSERT INTO tasks(title,status,created_at)
        VALUES (?, 'pending', ?)
        """,
        (title, datetime.utcnow().isoformat())
    )

    conn.commit()
    conn.close()


def get_tasks():
    conn = db()

    rows = conn.execute(
        """
        SELECT id,title,status,created_at
        FROM tasks
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# AGENT SYSTEM
# ============================================================

AGENTS = {
    "Coding Agent": {
        "icon": "⌘",
        "color": "cyan",
        "status": "active"
    },
    "Research Agent": {
        "icon": "◉",
        "color": "blue",
        "status": "active"
    },
    "Browser Agent": {
        "icon": "◎",
        "color": "purple",
        "status": "active"
    },
    "Memory Agent": {
        "icon": "◇",
        "color": "green",
        "status": "active"
    },
    "Task Agent": {
        "icon": "✓",
        "color": "orange",
        "status": "active"
    },
    "System Agent": {
        "icon": "⚙",
        "color": "red",
        "status": "active"
    }
}


# ============================================================
# TOOL / HAND SYSTEM
# ============================================================

def detect_tool_command(message):

    msg = message.lower().strip()

    if msg.startswith("crea una tarea"):
        return "task"

    if msg.startswith("crear una tarea"):
        return "task"

    if msg.startswith("nueva tarea"):
        return "task"

    if "qué tareas tengo" in msg:
        return "tasks"

    if "que tareas tengo" in msg:
        return "tasks"

    if "mis tareas" in msg:
        return "tasks"

    if "abre calendario" in msg:
        return "calendar"

    if "abrir calendario" in msg:
        return "calendar"

    if "nuevo chat" in msg:
        return "chat"

    return None


def execute_tool(message):

    tool = detect_tool_command(message)

    if tool == "task":

        title = re.sub(
            r"^(crea una tarea|crear una tarea|nueva tarea)\s*",
            "",
            message,
            flags=re.I
        ).strip()

        if not title:
            title = "Nueva tarea"

        create_task(title)

        return {
            "tool": "Task Agent",
            "success": True,
            "message":
                f"Tarea creada: {title}"
        }

    if tool == "tasks":

        tasks = get_tasks()

        if not tasks:
            return {
                "tool": "Task Agent",
                "success": True,
                "message":
                    "No tienes tareas pendientes."
            }

        lines = []

        for task in tasks:
            lines.append(
                f"• {task['title']} — {task['status']}"
            )

        return {
            "tool": "Task Agent",
            "success": True,
            "message":
                "Estas son tus tareas:\n" +
                "\n".join(lines)
        }

    if tool == "calendar":

        return {
            "tool": "Browser Agent",
            "success": True,
            "message":
                "El módulo de calendario está preparado. "
                "La conexión con tu calendario se agregará "
                "en la siguiente capa de herramientas."
        }

    if tool == "chat":

        return {
            "tool": "System Agent",
            "success": True,
            "message":
                "Nuevo canal de conversación preparado."
        }

    return None


# ============================================================
# WHATSAPP CONFIGURATION
# ============================================================

WHATSAPP_TOKEN = os.environ.get(
    "WHATSAPP_TOKEN",
    ""
)

WHATSAPP_PHONE_NUMBER_ID = os.environ.get(
    "WHATSAPP_PHONE_NUMBER_ID",
    ""
)

WHATSAPP_VERIFY_TOKEN = os.environ.get(
    "WHATSAPP_VERIFY_TOKEN",
    "jarvis_verify"
)


def whatsapp_available():
    return bool(
        WHATSAPP_TOKEN and
        WHATSAPP_PHONE_NUMBER_ID
    )


def send_whatsapp_message(to, message):

    if not whatsapp_available():

        return {
            "success": False,
            "error":
                "WhatsApp todavía no está configurado."
        }

    url = (
        "https://graph.facebook.com/v20.0/"
        + WHATSAPP_PHONE_NUMBER_ID
        + "/messages"
    )

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization":
                "Bearer " + WHATSAPP_TOKEN,
            "Content-Type":
                "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as response:

            body = response.read().decode(
                "utf-8",
                errors="ignore"
            )

            return {
                "success": True,
                "response": body
            }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# WHATSAPP WEBHOOK
# ============================================================

@app.route(
    "/whatsapp/webhook",
    methods=["GET"]
)
def whatsapp_verify():

    mode = request.args.get("hub.mode")
    token = request.args.get(
        "hub.verify_token"
    )
    challenge = request.args.get(
        "hub.challenge"
    )

    if (
        mode == "subscribe" and
        token == WHATSAPP_VERIFY_TOKEN
    ):
        return Response(
            challenge,
            status=200
        )

    return Response(
        "Verification failed",
        status=403
    )


@app.route(
    "/whatsapp/webhook",
    methods=["POST"]
)
def whatsapp_webhook():

    data = request.get_json(
        silent=True
    ) or {}

    try:

        entry = data.get(
            "entry",
            []
        )

        for item in entry:

            changes = item.get(
                "changes",
                []
            )

            for change in changes:

                value = change.get(
                    "value",
                    {}
                )

                messages = value.get(
                    "messages",
                    []
                )

                for msg in messages:

                    sender = msg.get(
                        "from"
                    )

                    msg_type = msg.get(
                        "type"
                    )

                    if msg_type != "text":
                        continue

                    incoming = (
                        msg.get("text", {})
                        .get("body", "")
                    )

                    if not incoming:
                        continue

                    result = process_message(
                        incoming,
                        source="whatsapp"
                    )

                    answer = result.get(
                        "reply",
                        "No pude procesar el mensaje."
                    )

                    if sender:
                        send_whatsapp_message(
                            sender,
                            answer
                        )

    except Exception as e:

        print(
            "WhatsApp webhook error:",
            e
        )

    return jsonify({
        "status": "received"
    })


# ============================================================
# GMAIL CONNECTION POINT
# ============================================================

@app.route(
    "/api/gmail/status",
    methods=["GET"]
)
def gmail_status():

    return jsonify({
        "connected": False,
        "message":
            "Gmail connector preparado. "
            "OAuth se configurará cuando conectemos la cuenta."
    })


# ============================================================
# AI BRAIN
# ============================================================

def ask_brain(
    message,
    memory_text="",
    web_text=""
):

    system_prompt = """
Eres J.A.R.V.I.S., un asistente personal avanzado.

Tu personalidad:
- inteligente
- directo
- natural
- educado
- eficiente
- con estilo tecnológico elegante
- habla español cuando el usuario habla español

No digas que tienes capacidades que realmente no tienes.

Tienes acceso a:
1. Memoria local
2. Búsqueda web proporcionada por el sistema
3. Sistema de tareas
4. Herramientas
5. Agentes especializados

Si hay resultados web disponibles:
- utilízalos
- distingue hechos de incertidumbre
- no inventes información

Si el usuario pide una acción que todavía no está conectada:
- explica brevemente que el módulo está preparado
- no afirmes que la acción ya ocurrió.

Responde de forma natural.
"""

    context = ""

    if memory_text:

        context += (
            "\nMEMORIA DEL USUARIO:\n"
            + memory_text
        )

    if web_text:

        context += (
            "\n\nRESULTADOS DE INTERNET:\n"
            + web_text
        )

    prompt = (
        system_prompt
        + context
        + "\n\nMENSAJE DEL USUARIO:\n"
        + message
    )

    try:

        response = ai.responses.create(
            model="openrouter/free",
            input=prompt
        )

        return response.output_text

    except Exception as e:

        print(
            "AI ERROR:",
            repr(e)
        )

        return (
            "No pude comunicarme con mi núcleo "
            "de inteligencia en este momento."
        )


# ============================================================
# MESSAGE PROCESSOR
# ============================================================

def process_message(
    message,
    source="web"
):

    message = str(
        message or ""
    ).strip()

    if not message:

        return {
            "reply":
                "Estoy listo. ¿Qué necesitas?"
        }

    save_conversation(
        "user",
        message
    )

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if is_memory_command(message):

        memory = extract_memory(
            message
        )

        save_memory(memory)

        answer = (
            "Entendido. Lo guardaré en mi memoria: "
            + memory
        )

        save_conversation(
            "assistant",
            answer
        )

        return {
            "reply": answer,
            "agent": "Memory Agent"
        }

    # --------------------------------------------------------
    # RECALL MEMORY
    # --------------------------------------------------------

    lower = message.lower()

    if (
        "qué recuerdas" in lower or
        "que recuerdas" in lower or
        "mis recuerdos" in lower or
        "qué sabes de mí" in lower or
        "que sabes de mi" in lower
    ):

        memories = get_memories()

        if not memories:

            answer = (
                "Todavía no tengo recuerdos "
                "guardados."
            )

        else:

            answer = (
                "Esto es lo que recuerdo:\n\n"
                + "\n".join(
                    "• " + row["content"]
                    for row in memories
                )
            )

        save_conversation(
            "assistant",
            answer
        )

        return {
            "reply": answer,
            "agent": "Memory Agent"
        }

    # --------------------------------------------------------
    # TOOLS / HANDS
    # --------------------------------------------------------

    tool_result = execute_tool(
        message
    )

    if tool_result:

        answer = tool_result["message"]

        save_conversation(
            "assistant",
            answer
        )

        return {
            "reply": answer,
            "agent": tool_result["tool"]
        }

    # --------------------------------------------------------
    # WEB / EYES
    # --------------------------------------------------------

    web_results = []

    if needs_web_search(message):

        query = extract_search_query(
            message
        )

        web_results = search_web(
            query
        )

    web_text = format_search_results(
        web_results
    )

    # --------------------------------------------------------
    # MEMORY CONTEXT
    # --------------------------------------------------------

    memories = get_memories(
        limit=20
    )

    memory_text = "\n".join(
        "• " + row["content"]
        for row in memories
    )

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    answer = ask_brain(
        message,
        memory_text,
        web_text
    )

    save_conversation(
        "assistant",
        answer
    )

    return {
        "reply": answer,
        "agent":
            "Research Agent"
            if web_results
            else "AI Core",
        "web_results":
            web_results
    }


# ============================================================
# API
# ============================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json(
        silent=True
    ) or {}

    message = data.get(
        "message",
        ""
    )

    result = process_message(
        message
    )

    return jsonify(result)


@app.route(
    "/api/tasks",
    methods=["GET"]
)
def api_tasks():

    return jsonify(
        get_tasks()
    )


@app.route(
    "/api/agents",
    methods=["GET"]
)
def api_agents():

    return jsonify(
        AGENTS
    )


@app.route(
    "/api/system",
    methods=["GET"]
)
def api_system():

    return jsonify({
        "status": "optimal",
        "brain": bool(
            OPENROUTER_API_KEY
        ),
        "memory": True,
        "web": True,
        "voice": True,
        "whatsapp":
            whatsapp_available(),
        "gmail": False,
        "agents": len(AGENTS),
        "time":
            datetime.now().isoformat()
    })


# ============================================================
# PWA MANIFEST
# ============================================================

@app.route(
    "/manifest.json"
)
def manifest():

    data = {
        "name":
            "J.A.R.V.I.S. Command Center",

        "short_name":
            "JARVIS",

        "description":
            "Personal AI Command Center",

        "start_url":
            "/",

        "scope":
            "/",

        "display":
            "standalone",

        "background_color":
            "#05080e",

        "theme_color":
            "#22d3ee",

        "orientation":
            "portrait",

        "icons": [
            {
                "src":
                    "/icon.svg",
                "sizes":
                    "any",
                "type":
                    "image/svg+xml",
                "purpose":
                    "any maskable"
            }
        ]
    }

    return jsonify(data)


# ============================================================
# ICON
# ============================================================

@app.route(
    "/icon.svg"
)
def icon():

    svg = """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 512 512">

<rect width="512"
      height="512"
      rx="100"
      fill="#05080e"/>

<circle cx="256"
        cy="256"
        r="205"
        fill="none"
        stroke="#22d3ee"
        stroke-width="7"/>

<circle cx="256"
        cy="256"
        r="170"
        fill="none"
        stroke="#22d3ee"
        stroke-width="2"
        opacity=".5"/>

<path d="M256 90
         L422 256
         L256 422
         L90 256 Z"
      fill="none"
      stroke="#22d3ee"
      stroke-width="8"/>

<circle cx="256"
        cy="256"
        r="82"
        fill="#082331"
        stroke="#a5f3fc"
        stroke-width="6"/>

<text x="256"
      y="284"
      text-anchor="middle"
      font-family="Arial,sans-serif"
      font-size="86"
      font-weight="700"
      fill="#e0fbff">J</text>

</svg>
"""

    return Response(
        svg,
        mimetype="image/svg+xml"
    )


# ============================================================
# SERVICE WORKER
# ============================================================

@app.route(
    "/service-worker.js"
)
def service_worker():

    js = """
const CACHE_NAME = "jarvis-command-center-v1";

const CORE = [
    "/",
    "/manifest.json",
    "/icon.svg"
];

self.addEventListener(
    "install",
    event => {

        event.waitUntil(
            caches.open(CACHE_NAME)
            .then(cache =>
                cache.addAll(CORE)
            )
        );

        self.skipWaiting();
    }
);

self.addEventListener(
    "activate",
    event => {

        event.waitUntil(
            caches.keys()
            .then(keys =>
                Promise.all(
                    keys
                    .filter(k =>
                        k !== CACHE_NAME
                    )
                    .map(k =>
                        caches.delete(k)
                    )
                )
            )
        );

        self.clients.claim();
    }
);

self.addEventListener(
    "fetch",
    event => {

        if (
            event.request.method !== "GET"
        ) {
            return;
        }

        event.respondWith(
            fetch(event.request)
            .catch(() =>
                caches.match(
                    event.request
                )
            )
        );
    }
);
"""

    return Response(
        js,
        mimetype="application/javascript"
    )


# ============================================================
# MAIN COMMAND CENTER UI
# ============================================================

@app.route("/")
def home():

    html = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,
               initial-scale=1.0,
               maximum-scale=1.0,
               user-scalable=no">

<title>J.A.R.V.I.S. Command Center</title>

<link rel="manifest"
      href="/manifest.json">

<meta name="theme-color"
      content="#05080e">

<meta name="mobile-web-app-capable"
      content="yes">

<meta name="apple-mobile-web-app-capable"
      content="yes">

<meta name="apple-mobile-web-app-status-bar-style"
      content="black-translucent">

<link rel="icon"
      href="/icon.svg">

<link rel="preconnect"
      href="https://fonts.googleapis.com">

<link rel="preconnect"
      href="https://fonts.gstatic.com"
      crossorigin>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Rajdhani:wght@500;600;700&display=swap"
      rel="stylesheet">


<style>

/* =========================================================
   CORE
========================================================= */

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {

    --bg:
        #05080e;

    --bg2:
        #0a0e1a;

    --panel:
        rgba(10,18,32,.72);

    --cyan:
        #22d3ee;

    --cyan2:
        #67e8f9;

    --blue:
        #3b82f6;

    --green:
        #34d399;

    --purple:
        #a78bfa;

    --orange:
        #f59e0b;

    --red:
        #fb7185;

    --text:
        #e5faff;

    --muted:
        #71869a;

    --border:
        rgba(34,211,238,.15);

    --glow:
        rgba(34,211,238,.35);
}

html,
body {

    width: 100%;
    min-height: 100%;

    background:
        radial-gradient(
            circle at 50% 20%,
            rgba(0,220,255,.08),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #05080e,
            #0a0e1a 45%,
            #0d1b2e
        );

    color: var(--text);

    font-family:
        Inter,
        sans-serif;

    overflow-x: hidden;
}


/* =========================================================
   BACKGROUND CONSTELLATION
========================================================= */

body::before {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    opacity: .28;

    background-image:
        radial-gradient(
            circle,
            rgba(34,211,238,.45)
            1px,
            transparent 1px
        );

    background-size:
        55px 55px;

    mask-image:
        linear-gradient(
            to bottom,
            black,
            transparent 90%
        );

    z-index: -2;
}

body::after {

    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    background:
        linear-gradient(
            rgba(34,211,238,.025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(34,211,238,.025) 1px,
            transparent 1px
        );

    background-size:
        80px 80px;

    z-index: -1;
}


/* =========================================================
   APP
========================================================= */

.app {

    display: flex;

    min-height: 100vh;

    padding-bottom: 115px;
}


/* =========================================================
   SIDEBAR
========================================================= */

.sidebar {

    position: fixed;

    left: 0;
    top: 0;
    bottom: 0;

    width: 245px;

    padding: 24px 15px;

    background:
        rgba(4,9,17,.82);

    backdrop-filter:
        blur(25px);

    border-right:
        1px solid var(--border);

    z-index: 50;

    display: flex;

    flex-direction: column;
}

.logo {

    padding:
        5px 12px 25px;
}

.logo-title {

    font-family:
        Rajdhani,
        sans-serif;

    font-size: 30px;

    font-weight: 700;

    letter-spacing: 6px;

    color: var(--cyan);

    text-shadow:
        0 0 20px
        rgba(34,211,238,.7);
}

.logo-sub {

    font-size: 9px;

    letter-spacing: 3px;

    color: #607588;

    margin-top: 2px;
}


.nav {

    display: flex;

    flex-direction: column;

    gap: 5px;
}

.nav-item {

    height: 43px;

    border-radius: 11px;

    display: flex;

    align-items: center;

    gap: 12px;

    padding:
        0 13px;

    color: #7e94a8;

    font-size: 12px;

    font-weight: 500;

    cursor: pointer;

    transition:
        .25s ease;

    border:
        1px solid transparent;
}

.nav-item:hover {

    color: var(--cyan2);

    background:
        rgba(34,211,238,.06);

    transform:
        translateX(2px);
}

.nav-item.active {

    color: var(--cyan2);

    background:
        linear-gradient(
            90deg,
            rgba(34,211,238,.15),
            rgba(34,211,238,.04)
        );

    border-color:
        rgba(34,211,238,.12);

    box-shadow:
        inset 3px 0 0 var(--cyan),
        0 0 20px rgba(34,211,238,.05);
}

.nav-icon {

    width: 19px;

    text-align: center;

    font-size: 16px;
}


/* =========================================================
   VOICE STATUS
========================================================= */

.voice-status {

    margin-top: auto;

    padding: 14px;

    border:
        1px solid var(--border);

    border-radius: 15px;

    background:
        rgba(10,20,34,.65);

    box-shadow:
        inset 0 0 25px
        rgba(34,211,238,.025);
}

.voice-title {

    color: #6f8799;

    font-size: 9px;

    letter-spacing: 2px;

    margin-bottom: 10px;
}

.wave-mini {

    height: 30px;

    display: flex;

    align-items: center;

    gap: 3px;

    overflow: hidden;
}

.wave-mini span {

    width: 3px;

    height: 10px;

    border-radius: 5px;

    background:
        var(--cyan);

    animation:
        voiceWave .75s
        ease-in-out
        infinite
        alternate;

    box-shadow:
        0 0 8px
        var(--cyan);
}

.wave-mini span:nth-child(2) {
    animation-delay: .08s;
}

.wave-mini span:nth-child(3) {
    animation-delay: .16s;
}

.wave-mini span:nth-child(4) {
    animation-delay: .24s;
}

.wave-mini span:nth-child(5) {
    animation-delay: .32s;
}

.wave-mini span:nth-child(6) {
    animation-delay: .4s;
}

.wave-mini span:nth-child(7) {
    animation-delay: .48s;
}

@keyframes voiceWave {

    from {
        height: 5px;
        opacity: .35;
    }

    to {
        height: 27px;
        opacity: 1;
    }
}

.voice-row {

    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-top: 8px;
}

.listening {

    font-size: 10px;

    color: var(--green);

    display: flex;

    align-items: center;

    gap: 6px;
}

.dot {

    width: 7px;
    height: 7px;

    border-radius: 50%;

    background:
        var(--green);

    box-shadow:
        0 0 12px
        var(--green);

    animation:
        blink 1.5s
        infinite;
}

@keyframes blink {

    0%,100% {
        opacity: .4;
    }

    50% {
        opacity: 1;
    }
}

.pause-btn {

    background:
        rgba(255,255,255,.04);

    color: #708496;

    border:
        1px solid rgba(255,255,255,.07);

    border-radius: 7px;

    padding:
        5px 8px;

    font-size: 9px;

    cursor: pointer;
}


/* =========================================================
   MAIN
========================================================= */

.main {

    margin-left: 245px;

    width: calc(100% - 245px);

    padding:
        20px 24px 40px;
}


/* =========================================================
   HEADER
========================================================= */

.header {

    height: 58px;

    display: grid;

    grid-template-columns:
        1fr auto 1fr;

    align-items: center;

    gap: 20px;

    margin-bottom: 20px;
}

.search {

    height: 38px;

    max-width: 390px;

    display: flex;

    align-items: center;

    gap: 10px;

    padding:
        0 14px;

    border:
        1px solid rgba(34,211,238,.1);

    border-radius: 10px;

    background:
        rgba(9,18,30,.55);

    color: #657d90;
}

.search input {

    width: 100%;

    border: none;

    outline: none;

    background: none;

    color: var(--text);

    font-size: 11px;
}

.search input::placeholder {
    color: #506678;
}

.time-center {

    text-align: center;

    white-space: nowrap;
}

.date {

    font-size: 10px;

    color: #6d8597;

    letter-spacing: 1px;
}

.clock {

    font-family:
        Rajdhani,
        sans-serif;

    color: var(--cyan);

    font-size: 22px;

    font-weight: 600;

    letter-spacing: 2px;

    text-shadow:
        0 0 15px
        rgba(34,211,238,.35);
}

.header-right {

    display: flex;

    align-items: center;

    justify-content: flex-end;

    gap: 12px;
}

.status {

    display: flex;

    align-items: center;

    gap: 7px;

    color: #7890a1;

    font-size: 9px;

    letter-spacing: 1px;
}

.util {

    width: 34px;
    height: 34px;

    display: grid;

    place-items: center;

    border:
        1px solid rgba(255,255,255,.06);

    border-radius: 9px;

    background:
        rgba(255,255,255,.025);

    color: #7890a1;

    cursor: pointer;

    transition: .2s;
}

.util:hover {

    color: var(--cyan);

    border-color:
        rgba(34,211,238,.2);

    box-shadow:
        0 0 15px
        rgba(34,211,238,.08);
}

.profile {

    display: flex;

    align-items: center;

    gap: 8px;

    font-size: 10px;

    color: #8296a7;
}

.avatar {

    width: 31px;
    height: 31px;

    border-radius: 50%;

    display: grid;

    place-items: center;

    background:
        linear-gradient(
            135deg,
            #113746,
            #14263b
        );

    border:
        1px solid
        rgba(34,211,238,.3);

    color: var(--cyan);
}


/* =========================================================
   PANEL
========================================================= */

.panel {

    background:
        linear-gradient(
            145deg,
            rgba(12,23,39,.78),
            rgba(5,13,24,.62)
        );

    border:
        1px solid var(--border);

    border-radius: 17px;

    backdrop-filter:
        blur(20px);

    box-shadow:
        inset 0 1px 0
        rgba(255,255,255,.025),
        0 10px 35px
        rgba(0,0,0,.15);

    transition:
        transform .25s,
        border-color .25s,
        box-shadow .25s;

    overflow: hidden;
}

.panel:hover {

    transform:
        translateY(-2px);

    border-color:
        rgba(34,211,238,.28);

    box-shadow:
        0 12px 40px
        rgba(0,0,0,.25),
        0 0 30px
        rgba(34,211,238,.035);
}

.panel-title {

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding:
        16px 17px 10px;

    color: #8da3b4;

    font-size: 9px;

    font-weight: 700;

    letter-spacing: 1.8px;
}

.panel-title span:first-child {

    display: flex;

    align-items: center;

    gap: 8px;
}

.panel-title-icon {

    color: var(--cyan);

    font-size: 13px;
}

.link {

    color: var(--cyan);

    font-size: 9px;

    cursor: pointer;

    text-decoration: none;
}


/* =========================================================
   AI CORE
========================================================= */

.core-grid {

    display:
        grid;

    grid-template-columns:
        245px
        minmax(350px,1fr)
        280px;

    gap: 16px;

    min-height: 345px;
}


/* overview */

.overview {

    padding-bottom: 12px;
}

.metrics {

    padding:
        3px 17px;
}

.metric {

    height: 47px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    border-bottom:
        1px solid
        rgba(255,255,255,.035);
}

.metric:last-child {
    border-bottom: none;
}

.metric-left {

    display: flex;

    align-items: center;

    gap: 9px;

    color: #8398a8;

    font-size: 11px;
}

.check {

    width: 18px;
    height: 18px;

    border-radius: 50%;

    display: grid;

    place-items: center;

    background:
        rgba(52,211,153,.1);

    border:
        1px solid
        rgba(52,211,153,.2);

    color: var(--green);

    font-size: 9px;
}

.online {

    color: var(--green);

    font-size: 8px;

    letter-spacing: .5px;
}


/* =========================================================
   CORE SPHERE
========================================================= */

.core-center {

    position: relative;

    display: grid;

    place-items: center;

    min-height: 345px;

    overflow: hidden;

    background:
        radial-gradient(
            circle at center,
            rgba(34,211,238,.06),
            transparent 48%
        );
}

.core-label {

    position: absolute;

    top: 23px;

    z-index: 4;

    text-align: center;

    pointer-events: none;
}

.core-label h1 {

    font-family:
        Rajdhani,
        sans-serif;

    font-size: 31px;

    letter-spacing: 10px;

    margin-left: 10px;

    color: #dffcff;

    text-shadow:
        0 0 25px
        rgba(34,211,238,.7);
}

.core-label p {

    color: var(--cyan);

    font-size: 8px;

    letter-spacing: 3px;

    margin-top: -2px;
}

.sphere {

    position: relative;

    width: 240px;
    height: 240px;

    border-radius: 50%;

    transform-style:
        preserve-3d;

    animation:
        sphereFloat 5s
        ease-in-out
        infinite;

    filter:
        drop-shadow(
            0 0 28px
            rgba(34,211,238,.23)
        );
}

@keyframes sphereFloat {

    0%,100% {
        transform:
            rotateX(8deg)
            rotateY(-10deg)
            translateY(0);
    }

    50% {
        transform:
            rotateX(-5deg)
            rotateY(15deg)
            translateY(-5px);
    }
}

.sphere-ring {

    position: absolute;

    inset: 0;

    border:
        1px solid
        rgba(34,211,238,.45);

    border-radius: 50%;

    box-shadow:
        0 0 18px
        rgba(34,211,238,.08);

    animation:
        rotateSphere 13s
        linear
        infinite;
}

.sphere-ring.r2 {

    inset: 17px;

    border-color:
        rgba(59,130,246,.4);

    animation-duration:
        10s;

    animation-direction:
        reverse;
}

.sphere-ring.r3 {

    inset: 35px;

    border-color:
        rgba(52,211,153,.28);

    animation-duration:
        8s;
}

.sphere-ring.r4 {

    inset: 53px;

    border-color:
        rgba(167,139,250,.3);

    animation-duration:
        16s;

    animation-direction:
        reverse;
}

@keyframes rotateSphere {

    from {
        transform:
            rotate(0deg)
            rotateX(65deg);
    }

    to {
        transform:
            rotate(360deg)
            rotateX(65deg);
    }
}

.sphere-core {

    position: absolute;

    inset: 85px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle at 35% 30%,
            #67e8f9,
            #0e6170 20%,
            #062531 58%,
            #03131c
        );

    box-shadow:
        0 0 35px
        rgba(34,211,238,.55),
        inset 0 0 30px
        rgba(34,211,238,.4);

    animation:
        corePulse 2.5s
        ease-in-out
        infinite;
}

@keyframes corePulse {

    0%,100% {
        transform: scale(.95);
        opacity: .8;
    }

    50% {
        transform: scale(1.08);
        opacity: 1;
    }
}

.sphere-dot {

    position: absolute;

    width: 4px;
    height: 4px;

    border-radius: 50%;

    background:
        var(--cyan);

    box-shadow:
        0 0 10px
        var(--cyan);

    animation:
        dotPulse 1.8s
        infinite;
}

.sphere-dot:nth-child(6) {
    left: 20%;
    top: 31%;
}

.sphere-dot:nth-child(7) {
    right: 17%;
    top: 28%;
    animation-delay: .3s;
}

.sphere-dot:nth-child(8) {
    left: 12%;
    bottom: 28%;
    animation-delay: .6s;
}

.sphere-dot:nth-child(9) {
    right: 12%;
    bottom: 26%;
    animation-delay: .9s;
}

@keyframes dotPulse {

    0%,100% {
        transform: scale(.6);
        opacity: .3;
    }

    50% {
        transform: scale(1.6);
        opacity: 1;
    }
}

.node-line {

    position: absolute;

    width: 95px;
    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--cyan)
        );

    opacity: .25;
}

.node-line.left {
    left: 4%;
}

.node-line.right {

    right: 4%;

    transform:
        rotate(180deg);
}


/* =========================================================
   INTELLIGENCE
========================================================= */

.feed {

    padding-bottom: 8px;
}

.feed-item {

    display: grid;

    grid-template-columns:
        27px 1fr auto;

    gap: 9px;

    padding:
        11px 15px;

    border-top:
        1px solid
        rgba(255,255,255,.035);
}

.feed-icon {

    width: 27px;
    height: 27px;

    display: grid;

    place-items: center;

    border-radius: 8px;

    font-size: 11px;

    background:
        rgba(34,211,238,.07);

    color:
        var(--cyan);
}

.feed-icon.alert {

    color: var(--red);

    background:
        rgba(251,113,133,.07);
}

.feed-text {

    font-size: 9px;

    line-height: 1.5;

    color: #9aacb9;
}

.feed-time {

    color: #52697a;

    font-size: 8px;

    white-space: nowrap;
}


/* =========================================================
   MIDDLE ROW
========================================================= */

.middle-grid {

    display:
        grid;

    grid-template-columns:
        1.4fr
        1fr
        .8fr;

    gap: 16px;

    margin-top: 16px;
}


/* agents */

.agent-grid {

    display:
        grid;

    grid-template-columns:
        repeat(3,1fr);

    gap: 8px;

    padding:
        4px 13px 15px;
}

.agent {

    min-height: 76px;

    padding: 10px;

    border-radius: 11px;

    background:
        rgba(255,255,255,.025);

    border:
        1px solid
        rgba(255,255,255,.045);

    transition: .2s;
}

.agent:hover {

    background:
        rgba(34,211,238,.045);

    border-color:
        rgba(34,211,238,.18);
}

.agent-icon {

    font-size: 17px;

    margin-bottom: 7px;
}

.agent-name {

    color: #899dac;

    font-size: 8px;

    line-height: 1.3;
}

.agent-status {

    display: flex;

    align-items: center;

    gap: 5px;

    margin-top: 5px;

    color: #607789;

    font-size: 7px;
}

.agent-status .dot {

    width: 5px;
    height: 5px;
}


/* timeline */

.timeline {

    padding:
        3px 16px 13px;
}

.timeline-item {

    position: relative;

    display: flex;

    gap: 10px;

    min-height: 42px;
}

.timeline-item:not(:last-child)::before {

    content: "";

    position: absolute;

    left: 8px;

    top: 17px;

    bottom: 0;

    width: 1px;

    background:
        rgba(34,211,238,.12);
}

.timeline-check {

    position: relative;

    z-index: 2;

    width: 17px;
    height: 17px;

    flex-shrink: 0;

    border-radius: 50%;

    display: grid;

    place-items: center;

    border:
        1px solid
        rgba(34,211,238,.3);

    color: var(--cyan);

    font-size: 8px;

    background:
        #08131f;
}

.timeline-item.done
.timeline-check {

    background:
        rgba(52,211,153,.1);

    border-color:
        rgba(52,211,153,.3);

    color: var(--green);
}

.timeline-text {

    color: #879ba9;

    font-size: 9px;

    padding-top: 2px;
}

.timeline-item.done
.timeline-text {

    color: #526778;

    text-decoration:
        line-through;
}


/* quick commands */

.quick {

    padding:
        3px 13px 14px;
}

.quick-btn {

    width: 100%;

    height: 39px;

    margin-bottom: 7px;

    display: flex;

    align-items: center;

    gap: 10px;

    border:
        1px solid
        rgba(255,255,255,.05);

    border-radius: 9px;

    background:
        rgba(255,255,255,.025);

    color: #8195a4;

    font-size: 9px;

    cursor: pointer;

    transition: .2s;

    padding:
        0 11px;
}

.quick-btn:hover {

    color: var(--cyan);

    border-color:
        rgba(34,211,238,.2);

    background:
        rgba(34,211,238,.04);
}


/* =========================================================
   LOWER
========================================================= */

.bottom-grid {

    display:
        grid;

    grid-template-columns:
        1.2fr
        .75fr
        1fr;

    gap: 16px;

    margin-top: 16px;
}


/* gauges */

.gauges {

    display:
        flex;

    justify-content:
        space-around;

    padding:
        7px 15px 19px;
}

.gauge {

    text-align: center;
}

.gauge-ring {

    --value: 75%;

    width: 90px;
    height: 90px;

    position: relative;

    display: grid;

    place-items: center;

    border-radius: 50%;

    background:
        conic-gradient(
            var(--gauge-color)
            var(--value),
            rgba(255,255,255,.045)
            0
        );

    box-shadow:
        0 0 20px
        color-mix(
            in srgb,
            var(--gauge-color),
            transparent 75%
        );
}

.gauge-ring::before {

    content: "";

    position: absolute;

    inset: 7px;

    border-radius: 50%;

    background:
        #09131f;

    border:
        1px solid
        rgba(255,255,255,.04);
}

.gauge-value {

    position: relative;

    z-index: 2;

    font-family:
        Rajdhani,
        sans-serif;

    font-size: 19px;

    color: #dffaff;
}

.gauge-label {

    margin-top: 8px;

    color: #647c8d;

    font-size: 8px;

    letter-spacing: 1px;
}


/* memory */

.memory {

    padding:
        7px 18px 20px;
}

.memory-number {

    font-family:
        Rajdhani,
        sans-serif;

    font-size: 48px;

    line-height: 1;

    color: var(--cyan);

    text-shadow:
        0 0 25px
        rgba(34,211,238,.25);
}

.memory-label {

    color: #607789;

    font-size: 8px;

    letter-spacing: 1px;

    margin-top: 3px;
}

.memory-secondary {

    margin-top: 19px;

    padding-top: 13px;

    border-top:
        1px solid
        rgba(255,255,255,.05);

    color: #8598a7;

    font-size: 9px;
}


/* LLM */

.providers {

    display:
        grid;

    grid-template-columns:
        repeat(3,1fr);

    gap: 7px;

    padding:
        5px 14px 17px;
}

.provider {

    padding: 9px;

    border-radius: 9px;

    background:
        rgba(255,255,255,.025);

    border:
        1px solid
        rgba(255,255,255,.04);
}

.provider-name {

    color: #8296a6;

    font-size: 8px;

    white-space: nowrap;

    overflow: hidden;

    text-overflow: ellipsis;
}

.provider-status {

    margin-top: 6px;

    display: flex;

    align-items: center;

    gap: 5px;

    font-size: 7px;

    color: #607789;
}


/* =========================================================
   CHAT PANEL
========================================================= */

.chat-panel {

    position: fixed;

    right: 20px;

    bottom: 110px;

    width: min(430px, calc(100vw - 30px));

    max-height: 60vh;

    display: none;

    flex-direction: column;

    z-index: 100;

    background:
        rgba(5,13,24,.94);

    border:
        1px solid
        rgba(34,211,238,.24);

    border-radius: 18px;

    backdrop-filter:
        blur(25px);

    box-shadow:
        0 20px 70px
        rgba(0,0,0,.5),
        0 0 35px
        rgba(34,211,238,.07);
}

.chat-panel.open {

    display: flex;
}

.chat-head {

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 14px 16px;

    border-bottom:
        1px solid
        rgba(255,255,255,.06);
}

.chat-head-title {

    color: var(--cyan);

    font-family:
        Rajdhani,
        sans-serif;

    letter-spacing: 2px;

    font-size: 14px;
}

.close-chat {

    border: none;

    background: none;

    color: #718697;

    font-size: 18px;

    cursor: pointer;
}

.messages {

    flex: 1;

    overflow-y: auto;

    padding: 15px;

    min-height: 170px;

    max-height: 42vh;
}

.message {

    max-width: 88%;

    padding: 10px 12px;

    border-radius: 12px;

    margin-bottom: 9px;

    font-size: 10px;

    line-height: 1.5;
}

.message.user {

    margin-left: auto;

    color: #d9fbff;

    background:
        rgba(34,211,238,.12);

    border:
        1px solid
        rgba(34,211,238,.13);
}

.message.jarvis {

    color: #9db1bf;

    background:
        rgba(255,255,255,.035);

    border:
        1px solid
        rgba(255,255,255,.05);
}

.chat-input {

    display: flex;

    gap: 8px;

    padding: 11px;

    border-top:
        1px solid
        rgba(255,255,255,.06);
}

.chat-input input {

    flex: 1;

    height: 38px;

    padding:
        0 12px;

    border:
        1px solid
        rgba(34,211,238,.12);

    border-radius: 9px;

    outline: none;

    background:
        rgba(255,255,255,.035);

    color: white;

    font-size: 10px;
}

.send {

    width: 40px;

    border: none;

    border-radius: 9px;

    background:
        var(--cyan);

    color:
        #03222a;

    cursor: pointer;

    font-weight: 800;
}


/* =========================================================
   BOTTOM TALK BAR
========================================================= */

.talkbar {

    position: fixed;

    left: 245px;
    right: 0;
    bottom: 0;

    height: 92px;

    z-index: 60;

    display: flex;

    justify-content: center;

    align-items: center;

    pointer-events: none;

    background:
        linear-gradient(
            to top,
            rgba(5,8,14,.96),
            rgba(5,8,14,.7),
            transparent
        );
}

.talk-wrap {

    position: relative;

    pointer-events: auto;

    display: flex;

    align-items: center;

    gap: 28px;
}

.audio-side {

    width: 115px;

    height: 35px;

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 3px;
}

.audio-side span {

    width: 3px;

    height: 8px;

    border-radius: 3px;

    background:
        var(--cyan);

    opacity: .5;

    animation:
        bottomWave .7s
        ease-in-out
        infinite
        alternate;
}

.audio-side span:nth-child(2) {
    animation-delay: .1s;
}

.audio-side span:nth-child(3) {
    animation-delay: .2s;
}

.audio-side span:nth-child(4) {
    animation-delay: .3s;
}

.audio-side span:nth-child(5) {
    animation-delay: .4s;
}

@keyframes bottomWave {

    from {
        height: 5px;
    }

    to {
        height: 27px;
    }
}

.talk-button {

    position: relative;

    min-width: 225px;

    height: 59px;

    padding:
        0 22px;

    border-radius: 18px;

    border:
        1px solid
        rgba(34,211,238,.42);

    background:
        linear-gradient(
            135deg,
            rgba(10,45,60,.9),
            rgba(7,20,33,.95)
        );

    color: var(--cyan);

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 12px;

    cursor: pointer;

    box-shadow:
        0 0 30px
        rgba(34,211,238,.1),
        inset 0 0 20px
        rgba(34,211,238,.035);

    transition: .25s;

    animation:
        talkGlow 2.3s
        ease-in-out
        infinite;
}

@keyframes talkGlow {

    0%,100% {
        box-shadow:
            0 0 20px
            rgba(34,211,238,.08);
    }

    50% {
        box-shadow:
            0 0 35px
            rgba(34,211,238,.25);
    }
}

.talk-button:hover {

    transform:
        translateY(-2px);

    border-color:
        rgba(34,211,238,.8);
}

.talk-button.listening {

    background:
        linear-gradient(
            135deg,
            rgba(0,125,145,.75),
            rgba(7,30,43,.95)
        );

    box-shadow:
        0 0 50px
        rgba(34,211,238,.4);
}

.mic {

    width: 35px;
    height: 35px;

    border-radius: 50%;

    display: grid;

    place-items: center;

    background:
        rgba(34,211,238,.1);

    border:
        1px solid
        rgba(34,211,238,.25);

    font-size: 16px;
}

.talk-text {

    text-align: left;
}

.talk-main {

    font-family:
        Rajdhani,
        sans-serif;

    font-size: 14px;

    font-weight: 700;

    letter-spacing: 2px;
}

.talk-sub {

    font-size: 8px;

    color: #698192;

    margin-top: 1px;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 1150px) {

    .sidebar {
        width: 210px;
    }

    .main {
        margin-left: 210px;
        width: calc(100% - 210px);
    }

    .talkbar {
        left: 210px;
    }

    .core-grid {
        grid-template-columns:
            200px
            minmax(280px,1fr)
            230px;
    }

    .middle-grid {
        grid-template-columns:
            1fr 1fr;
    }

    .middle-grid .quick-panel {
        grid-column: span 2;
    }

    .bottom-grid {
        grid-template-columns:
            1fr 1fr;
    }

    .bottom-grid .llm-panel {
        grid-column: span 2;
    }
}

@media (max-width: 850px) {

    .sidebar {

        width: 62px;

        padding:
            15px 8px;
    }

    .logo {
        text-align: center;
        padding:
            8px 0 20px;
    }

    .logo-title {
        font-size: 18px;
        letter-spacing: 2px;
    }

    .logo-sub {
        display: none;
    }

    .nav-item {
        justify-content: center;
        padding: 0;
    }

    .nav-item span:not(.nav-icon) {
        display: none;
    }

    .voice-status {
        display: none;
    }

    .main {

        margin-left: 62px;

        width:
            calc(100% - 62px);

        padding:
            14px;
    }

    .talkbar {
        left: 62px;
    }

    .header {

        grid-template-columns:
            1fr auto;

        height: auto;
    }

    .search {
        max-width: none;
    }

    .time-center {
        display: none;
    }

    .header-right .status,
    .header-right .profile {
        display: none;
    }

    .core-grid {
        grid-template-columns: 1fr;
    }

    .core-center {
        min-height: 380px;
    }

    .middle-grid,
    .bottom-grid {
        grid-template-columns: 1fr;
    }

    .middle-grid .quick-panel,
    .bottom-grid .llm-panel {
        grid-column: auto;
    }

    .agent-grid {
        grid-template-columns:
            repeat(2,1fr);
    }

    .audio-side {
        display: none;
    }
}

@media (max-width: 520px) {

    .header-right .util {
        display: none;
    }

    .clock {
        font-size: 18px;
    }

    .core-center {
        min-height: 330px;
    }

    .sphere {
        width: 205px;
        height: 205px;
    }

    .sphere-core {
        inset: 73px;
    }

    .talk-button {
        min-width: 205px;
    }

    .gauge-ring {
        width: 76px;
        height: 76px;
    }
}

</style>

</head>


<body>


<div class="app">


<!-- ======================================================
     SIDEBAR
====================================================== -->

<aside class="sidebar">

    <div class="logo">

        <div class="logo-title">
            JARVIS
        </div>

        <div class="logo-sub">
            COMMAND CENTER
        </div>

    </div>


    <nav class="nav">

        <div class="nav-item active">
            <span class="nav-icon">⌂</span>
            <span>Command Center</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">◉</span>
            <span>AI Core</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">◇</span>
            <span>Agents</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">✓</span>
            <span>Tasks</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">□</span>
            <span>Calendar</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">◈</span>
            <span>Memory</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">◌</span>
            <span>Conversations</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">▣</span>
            <span>Knowledge Base</span>
        </div>

        <div class="nav-item">
            <span class="nav-icon">⚙</span>
            <span>Tools & Skills</span>
        </div>

    </nav>


    <div class="voice-status">

        <div class="voice-title">
            VOICE STATUS
        </div>

        <div class="wave-mini">

            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>

        </div>

        <div class="voice-row">

            <div class="listening">

                <span class="dot"></span>

                <span>
                    Listening
                </span>

            </div>

            <button
                class="pause-btn"
                onclick="toggleVoice()">

                Pause Mode

            </button>

        </div>

    </div>

</aside>



<!-- ======================================================
     MAIN
====================================================== -->

<main class="main">


<header class="header">


    <div class="search">

        <span>⌕</span>

        <input
            id="searchInput"
            placeholder="Search command center..."
            autocomplete="off">

    </div>


    <div class="time-center">

        <div
            class="date"
            id="date">
        </div>

        <div
            class="clock"
            id="clock">
        </div>

    </div>


    <div class="header-right">

        <div class="status">

            <span class="dot"></span>

            SYSTEM STATUS: OPTIMAL

        </div>

        <button
            class="util"
            onclick="openChat()">
            ◌
        </button>

        <button
            class="util">
            ⚙
        </button>

        <div class="profile">

            <div class="avatar">
                O
            </div>

            Operator

        </div>

    </div>


</header>



<!-- ======================================================
     AI CORE
====================================================== -->

<section class="core-grid">


    <!-- overview -->

    <div class="panel overview">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ◉
                </span>

                AI CORE OVERVIEW
            </span>

            <span class="link">
                LIVE
            </span>

        </div>


        <div class="metrics">


            <div class="metric">

                <div class="metric-left">

                    <span class="check">
                        ✓
                    </span>

                    AI Core

                </div>

                <span class="online">
                    ONLINE
                </span>

            </div>


            <div class="metric">

                <div class="metric-left">

                    <span class="check">
                        ✓
                    </span>

                    Memory

                </div>

                <span class="online">
                    ONLINE
                </span>

            </div>


            <div class="metric">

                <div class="metric-left">

                    <span class="check">
                        ✓
                    </span>

                    Agents

                </div>

                <span class="online">
                    ONLINE
                </span>

            </div>


            <div class="metric">

                <div class="metric-left">

                    <span class="check">
                        ✓
                    </span>

                    LLMs

                </div>

                <span class="online">
                    ONLINE
                </span>

            </div>


            <div class="metric">

                <div class="metric-left">

                    <span class="check">
                        ✓
                    </span>

                    System

                </div>

                <span class="online">
                    OPTIMAL
                </span>

            </div>


        </div>

    </div>



    <!-- sphere -->

    <div class="panel core-center">


        <div class="core-label">

            <h1>
                JARVIS
            </h1>

            <p>
                AI CORE · v3.0.1
            </p>

        </div>


        <div class="node-line left"></div>
        <div class="node-line right"></div>


        <div class="sphere">

            <div class="sphere-ring"></div>

            <div class="sphere-ring r2"></div>

            <div class="sphere-ring r3"></div>

            <div class="sphere-ring r4"></div>

            <div class="sphere-core"></div>

            <span class="sphere-dot"></span>
            <span class="sphere-dot"></span>
            <span class="sphere-dot"></span>
            <span class="sphere-dot"></span>

        </div>

    </div>



    <!-- intelligence -->

    <div class="panel feed">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ◈
                </span>

                LIVE INTELLIGENCE FEED
            </span>

            <span class="link">
                View All
            </span>

        </div>


        <div class="feed-item">

            <div class="feed-icon alert">
                !
            </div>

            <div class="feed-text">
                JARVIS system initialized.
            </div>

            <div class="feed-time">
                now
            </div>

        </div>


        <div class="feed-item">

            <div class="feed-icon">
                ◉
            </div>

            <div class="feed-text">
                OpenRouter AI Core connected.
            </div>

            <div class="feed-time">
                1m
            </div>

        </div>


        <div class="feed-item">

            <div class="feed-icon">
                ◇
            </div>

            <div class="feed-text">
                Memory subsystem operational.
            </div>

            <div class="feed-time">
                2m
            </div>

        </div>


        <div class="feed-item">

            <div class="feed-icon">
                ◎
            </div>

            <div class="feed-text">
                Web intelligence ready.
            </div>

            <div class="feed-time">
                3m
            </div>

        </div>


        <div class="feed-item">

            <div class="feed-icon">
                ✓
            </div>

            <div class="feed-text">
                All core services stable.
            </div>

            <div class="feed-time">
                4m
            </div>

        </div>

    </div>

</section>



<!-- ======================================================
     MIDDLE
====================================================== -->

<section class="middle-grid">


    <!-- AGENTS -->

    <div class="panel">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ◇
                </span>

                ACTIVE AGENTS
            </span>

            <span class="link">
                6 ACTIVE
            </span>

        </div>


        <div class="agent-grid">


            <div class="agent">

                <div
                    class="agent-icon"
                    style="color:#22d3ee">
                    ⌘
                </div>

                <div class="agent-name">
                    Coding Agent
                </div>

                <div class="agent-status">
                    <span class="dot"></span>
                    ACTIVE
                </div>

            </div>


            <div class="agent">

                <div
                    class="agent-icon"
                    style="color:#3b82f6">
                    ◉
                </div>

                <div class="agent-name">
                    Research Agent
                </div>

                <div class="agent-status">
                    <span class="dot"></span>
                    ACTIVE
                </div>

            </div>


            <div class="agent">

                <div
                    class="agent-icon"
                    style="color:#a78bfa">
                    ◎
                </div>

                <div class="agent-name">
                    Browser Agent
                </div>

                <div class="agent-status">
                    <span class="dot"></span>
                    ACTIVE
                </div>

            </div>


            <div class="agent">

                <div
                    class="agent-icon"
                    style="color:#34d399">
                    ◇
                </div>

                <div class="agent-name">
                    Memory Agent
                </div>

                <div class="agent-status">
                    <span class="dot"></span>
                    ACTIVE
                </div>

            </div>


            <div class="agent">

                <div
                    class="agent-icon"
                    style="color:#f59e0b">
                    ✓
                </div>

                <div class="agent-name">
                    Task Agent
                </div>

                <div class="agent-status">
                    <span class="dot"></span>
                    ACTIVE
                </div>

            </div>


            <div class="agent">

                <div
                    class="agent-icon"
                    style="color:#fb7185">
                    ⚙
                </div>

                <div class="agent-name">
                    System Agent
                </div>

                <div class="agent-status">
                    <span class="dot"></span>
                    ACTIVE
                </div>

            </div>


        </div>

    </div>



    <!-- TIMELINE -->

    <div class="panel">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ◷
                </span>

                MISSION TIMELINE
            </span>

            <span class="link">
                Full Schedule
            </span>

        </div>


        <div class="timeline">


            <div class="timeline-item done">

                <div class="timeline-check">
                    ✓
                </div>

                <div class="timeline-text">
                    Initialize JARVIS Core
                </div>

            </div>


            <div class="timeline-item done">

                <div class="timeline-check">
                    ✓
                </div>

                <div class="timeline-text">
                    Connect AI provider
                </div>

            </div>


            <div class="timeline-item">

                <div class="timeline-check">
                    •
                </div>

                <div class="timeline-text">
                    Connect personal tools
                </div>

            </div>


            <div class="timeline-item">

                <div class="timeline-check">
                    •
                </div>

                <div class="timeline-text">
                    Configure communications
                </div>

            </div>


            <div class="timeline-item">

                <div class="timeline-check">
                    •
                </div>

                <div class="timeline-text">
                    Activate automation layer
                </div>

            </div>


        </div>

    </div>



    <!-- QUICK COMMANDS -->

    <div class="panel quick-panel">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ⚡
                </span>

                QUICK COMMANDS
            </span>

        </div>


        <div class="quick">

            <button
                class="quick-btn"
                onclick="quickCommand('nueva tarea')">

                <span>＋</span>

                New Task

            </button>


            <button
                class="quick-btn"
                onclick="quickCommand('abre calendario')">

                <span>□</span>

                Open Calendar

            </button>


            <button
                class="quick-btn"
                onclick="openChat()">

                <span>◌</span>

                Start New Chat

            </button>


            <button
                class="quick-btn"
                onclick="quickCommand('crea una tarea de revisar mi proyecto Jarvis')">

                <span>◇</span>

                New Workflow

            </button>

        </div>

    </div>

</section>



<!-- ======================================================
     BOTTOM
====================================================== -->

<section class="bottom-grid">


    <!-- SYSTEM MONITOR -->

    <div class="panel">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ◌
                </span>

                SYSTEM MONITOR
            </span>

            <span class="link">
                LIVE
            </span>

        </div>


        <div class="gauges">


            <div class="gauge">

                <div
                    class="gauge-ring"
                    style="
                        --value:64%;
                        --gauge-color:#22d3ee;
                    ">

                    <span
                        class="gauge-value">
                        64%
                    </span>

                </div>

                <div class="gauge-label">
                    CPU
                </div>

            </div>


            <div class="gauge">

                <div
                    class="gauge-ring"
                    style="
                        --value:48%;
                        --gauge-color:#3b82f6;
                    ">

                    <span
                        class="gauge-value">
                        48%
                    </span>

                </div>

                <div class="gauge-label">
                    RAM
                </div>

            </div>


            <div class="gauge">

                <div
                    class="gauge-ring"
                    style="
                        --value:82%;
                        --gauge-color:#34d399;
                    ">

                    <span
                        class="gauge-value">
                        82%
                    </span>

                </div>

                <div class="gauge-label">
                    HEALTH
                </div>

            </div>


        </div>

    </div>



    <!-- MEMORY -->

    <div class="panel">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ◈
                </span>

                MEMORY INSIGHTS
            </span>

        </div>


        <div class="memory">

            <div
                class="memory-number"
                id="memoryCount">
                3,380
            </div>

            <div class="memory-label">
                MEMORY FRAGMENTS
            </div>

            <div class="memory-secondary">
                Long-term memory subsystem
                <strong style="color:#34d399">
                    ONLINE
                </strong>
            </div>

            <div
                class="link"
                style="margin-top:13px">
                View Memory Map
            </div>

        </div>

    </div>



    <!-- LLM -->

    <div class="panel llm-panel">

        <div class="panel-title">

            <span>
                <span class="panel-title-icon">
                    ◎
                </span>

                LLM STATUS
            </span>

            <span class="link">
                Manage Providers
            </span>

        </div>


        <div class="providers">


            <div class="provider">

                <div class="provider-name">
                    OpenRouter
                </div>

                <div class="provider-status">
                    <span class="dot"></span>
                    CONNECTED
                </div>

            </div>


            <div class="provider">

                <div class="provider-name">
                    OpenAI
                </div>

                <div class="provider-status">
                    <span
                        class="dot"
                        style="background:#718096;
                               box-shadow:none">
                    </span>
                    READY
                </div>

            </div>


            <div class="provider">

                <div class="provider-name">
                    Claude
                </div>

                <div class="provider-status">
                    <span
                        class="dot"
                        style="background:#718096;
                               box-shadow:none">
                    </span>
                    READY
                </div>

            </div>


            <div class="provider">

                <div class="provider-name">
                    Gemini
                </div>

                <div class="provider-status">
                    <span
                        class="dot"
                        style="background:#718096;
                               box-shadow:none">
                    </span>
                    READY
                </div>

            </div>


            <div class="provider">

                <div class="provider-name">
                    Claude Code
                </div>

                <div class="provider-status">
                    <span
                        class="dot"
                        style="background:#718096;
                               box-shadow:none">
                    </span>
                    READY
                </div>

            </div>


            <div class="provider">

                <div class="provider-name">
                    WhatsApp
                </div>

                <div class="provider-status">

                    <span
                        class="dot"
                        id="whatsappDot"
                        style="background:#718096;
                               box-shadow:none">
                    </span>

                    <span id="whatsappStatus">
                        CONFIGURE
                    </span>

                </div>

            </div>


        </div>

    </div>

</section>


</main>

</div>



<!-- ======================================================
     CHAT WINDOW
====================================================== -->

<div
    class="chat-panel"
    id="chatPanel">


    <div class="chat-head">

        <div class="chat-head-title">
            J.A.R.V.I.S. LINK
        </div>

        <button
            class="close-chat"
            onclick="closeChat()">
            ×
        </button>

    </div>


    <div
        class="messages"
        id="messages">

        <div class="message jarvis">

            Sistemas en línea.

            <br><br>

            Soy JARVIS. ¿Qué necesitas,
            operador?

        </div>

    </div>


    <div class="chat-input">

        <input
            id="chatInput"
            placeholder="Habla con JARVIS..."
            autocomplete="off">

        <button
            class="send"
            onclick="sendMessage()">
            ➤
        </button>

    </div>

</div>



<!-- ======================================================
     TALK BAR
====================================================== -->

<div class="talkbar">


    <div class="talk-wrap">


        <div class="audio-side">

            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>

        </div>


        <button
            class="talk-button"
            id="talkButton"
            onclick="toggleListening()">


            <div class="mic">
                🎙
            </div>


            <div class="talk-text">

                <div class="talk-main">
                    TALK TO JARVIS
                </div>

                <div
                    class="talk-sub"
                    id="talkStatus">
                    Idle
                </div>

            </div>


        </button>


        <div class="audio-side">

            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>

        </div>


    </div>

</div>



<script>

/* =========================================================
   CLOCK
========================================================= */

function updateClock() {

    const now =
        new Date();

    const date =
        now.toLocaleDateString(
            "en-US",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric"
            }
        );

    const time =
        now.toLocaleTimeString(
            "en-US",
            {
                hour: "numeric",
                minute: "2-digit",
                second: "2-digit"
            }
        );

    document.getElementById(
        "date"
    ).textContent = date;

    document.getElementById(
        "clock"
    ).textContent = time;
}

setInterval(
    updateClock,
    1000
);

updateClock();


/* =========================================================
   CHAT
========================================================= */

const chatPanel =
    document.getElementById(
        "chatPanel"
    );

const chatInput =
    document.getElementById(
        "chatInput"
    );

const messages =
    document.getElementById(
        "messages"
    );


function openChat() {

    chatPanel.classList.add(
        "open"
    );

    setTimeout(
        () => chatInput.focus(),
        100
    );
}


function closeChat() {

    chatPanel.classList.remove(
        "open"
    );
}


function addMessage(
    text,
    type
) {

    const div =
        document.createElement(
            "div"
        );

    div.className =
        "message " + type;

    div.textContent =
        text;

    messages.appendChild(
        div
    );

    messages.scrollTop =
        messages.scrollHeight;
}


async function sendMessage(
    supplied = null
) {

    const message =
        supplied !== null
            ? supplied
            : chatInput.value.trim();

    if (!message) {
        return;
    }

    openChat();

    if (
        supplied === null
    ) {
        chatInput.value = "";
    }

    addMessage(
        message,
        "user"
    );

    addMessage(
        "Procesando...",
        "jarvis"
    );

    const loading =
        messages.lastElementChild;

    try {

        const response =
            await fetch(
                "/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message:
                                message
                        })
                }
            );

        const data =
            await response.json();

        loading.remove();

        const reply =
            data.reply ||
            "No recibí respuesta.";

        addMessage(
            reply,
            "jarvis"
        );

        speak(reply);

    } catch (error) {

        loading.remove();

        addMessage(
            "No pude comunicarme con el servidor.",
            "jarvis"
        );
    }
}


chatInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter"
        ) {
            sendMessage();
        }
    }
);


/* =========================================================
   QUICK COMMANDS
========================================================= */

function quickCommand(
    command
) {

    openChat();

    sendMessage(
        command
    );
}


/* =========================================================
   SPEECH
========================================================= */

let recognition = null;

let listening = false;


const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (SpeechRecognition) {

    recognition =
        new SpeechRecognition();

    recognition.lang =
        "es-PA";

    recognition.continuous =
        false;

    recognition.interimResults =
        false;


    recognition.onstart =
        function() {

            listening = true;

            setListeningUI(
                true
            );
        };


    recognition.onend =
        function() {

            listening = false;

            setListeningUI(
                false
            );
        };


    recognition.onerror =
        function() {

            listening = false;

            setListeningUI(
                false
            );
        };


    recognition.onresult =
        function(event) {

            const text =
                event.results[0][0].transcript;

            openChat();

            sendMessage(
                text
            );
        };
}


function toggleListening() {

    if (!recognition) {

        openChat();

        addMessage(
            "El navegador no permite reconocimiento de voz. Puedes escribir tu comando.",
            "jarvis"
        );

        return;
    }

    if (listening) {

        recognition.stop();

    } else {

        try {

            recognition.start();

        } catch(e) {

        }

    }
}


function setListeningUI(
    active
) {

    const button =
        document.getElementById(
            "talkButton"
        );

    const status =
        document.getElementById(
            "talkStatus"
        );

    if (active) {

        button.classList.add(
            "listening"
        );

        status.textContent =
            "Listening...";

    } else {

        button.classList.remove(
            "listening"
        );

        status.textContent =
            "Idle";
    }
}


/* =========================================================
   TEXT TO SPEECH
========================================================= */

function speak(text) {

    if (
        !window.speechSynthesis
    ) {
        return;
    }

    window.speechSynthesis.cancel();

    const clean =
        String(text)
        .replace(
            /https?:\/\/\S+/g,
            ""
        );

    const utterance =
        new SpeechSynthesisUtterance(
            clean
        );

    utterance.lang =
        "es-PA";

    utterance.rate =
        0.96;

    utterance.pitch =
        1.0;

    const voices =
        window.speechSynthesis
        .getVoices();

    const spanish =
        voices.find(
            v =>
                v.lang &&
                v.lang
                    .toLowerCase()
                    .startsWith("es")
        );

    if (spanish) {
        utterance.voice =
            spanish;
    }

    window.speechSynthesis
        .speak(
            utterance
        );
}


/* =========================================================
   VOICE PAUSE
========================================================= */

let voicePaused = false;


function toggleVoice() {

    voicePaused =
        !voicePaused;

    if (voicePaused) {

        if (
            window.speechSynthesis
        ) {
            window.speechSynthesis.cancel();
        }

        document.querySelector(
            ".listening span:last-child"
        ).textContent =
            "Paused";

    } else {

        document.querySelector(
            ".listening span:last-child"
        ).textContent =
            "Listening";
    }
}


/* =========================================================
   NAVIGATION INTERACTION
========================================================= */

document
    .querySelectorAll(
        ".nav-item"
    )
    .forEach(
        item => {

            item.addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll(
                            ".nav-item"
                        )
                        .forEach(
                            n =>
                                n.classList
                                 .remove(
                                     "active"
                                 )
                        );

                    item.classList.add(
                        "active"
                    );

                    const label =
                        item
                        .querySelector(
                            "span:last-child"
                        );

                    if (label) {

                        const name =
                            label.textContent
                            .trim();

                        if (
                            name !==
                            "Command Center"
                        ) {

                            quickCommand(
                                "abre " +
                                name
                            );
                        }
                    }
                }
            );

        }
    );


/* =========================================================
   SEARCH
========================================================= */

document
    .getElementById(
        "searchInput"
    )
    .addEventListener(
        "keydown",
        function(event) {

            if (
                event.key ===
                "Enter"
            ) {

                const value =
                    this.value.trim();

                if (value) {

                    openChat();

                    sendMessage(
                        "busca " +
                        value
                    );

                    this.value =
                        "";
                }
            }
        }
    );


/* =========================================================
   SYSTEM STATUS
========================================================= */

async function updateSystem() {

    try {

        const response =
            await fetch(
                "/api/system"
            );

        const data =
            await response.json();

        const dot =
            document.getElementById(
                "whatsappDot"
            );

        const status =
            document.getElementById(
                "whatsappStatus"
            );

        if (
            data.whatsapp
        ) {

            dot.style.background =
                "#34d399";

            dot.style.boxShadow =
                "0 0 12px #34d399";

            status.textContent =
                "CONNECTED";

        } else {

            dot.style.background =
                "#718096";

            dot.style.boxShadow =
                "none";

            status.textContent =
                "CONFIGURE";
        }

    } catch(e) {

    }
}

updateSystem();


/* =========================================================
   PWA
========================================================= */

if (
    "serviceWorker"
    in navigator
) {

    navigator
        .serviceWorker
        .register(
            "/service-worker.js"
        )
        .catch(
            () => {}
        );
}


/* =========================================================
   LOAD VOICES
========================================================= */

if (
    window.speechSynthesis
) {

    window.speechSynthesis
        .getVoices();

    window.speechSynthesis
        .onvoiceschanged =
        () => {

            window.speechSynthesis
                .getVoices();

        };
}

</script>


</body>

</html>
"""

    return Response(
        html,
        mimetype="text/html"
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        " J.A.R.V.I.S. COMMAND CENTER"
    )

    print(
        " Brain: OpenRouter"
    )

    print(
        " Memory: SQLite"
    )

    print(
        " Web: DuckDuckGo"
    )

    print(
        " Voice: Browser"
    )

    print(
        " Agents: 6"
    )

    print(
        " WhatsApp:",
        "READY"
        if whatsapp_available()
        else "NOT CONFIGURED"
    )

    print(
        "=========================================="
    )

    app.run(
        host="0.0.0.0",
        port=PORT
                )
