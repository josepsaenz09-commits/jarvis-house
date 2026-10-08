import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

# =========================
# OPENROUTER — CEREBRO
# =========================

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "openrouter/free"


# =========================
# INTERFAZ J.A.R.V.I.S.
# =========================

HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>J.A.R.V.I.S — Command Interface</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --bg: #0a0e17;
    --panel: rgba(8,18,30,.78);
    --cyan: #22d3ee;
    --blue: #00d9ff;
    --green: #39ff88;
    --text: #d9faff;
    --muted: #63808e;
}

body {
    min-height: 100vh;
    background:
        radial-gradient(circle at center, #102338 0%, #0a0e17 45%, #05080e 100%);
    color: var(--text);
    font-family: "Rajdhani", sans-serif;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background:
        linear-gradient(rgba(34,211,238,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34,211,238,.025) 1px, transparent 1px);
    background-size: 40px 40px;
}

.hidden {
    display: none !important;
}

/* =========================
   SPLASH
========================= */

#splash {
    position: fixed;
    inset: 0;
    z-index: 50;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    background: #060a12;
}

.splash-title {
    font-family: "Orbitron", sans-serif;
    font-size: clamp(38px, 9vw, 80px);
    letter-spacing: 12px;
    color: var(--cyan);
    text-shadow:
        0 0 10px var(--cyan),
        0 0 30px var(--cyan),
        0 0 60px rgba(34,211,238,.5);
}

.splash-sub {
    margin-top: 12px;
    color: #6c8795;
    letter-spacing: 5px;
    text-align: center;
    font-size: 12px;
}

.radar-loader {
    width: 130px;
    height: 130px;
    margin: 45px 0 25px;
    border: 1px solid rgba(34,211,238,.25);
    border-radius: 50%;
    position: relative;
    box-shadow:
        0 0 25px rgba(34,211,238,.15),
        inset 0 0 25px rgba(34,211,238,.1);
}

.radar-loader::before,
.radar-loader::after {
    content: "";
    position: absolute;
    inset: 18px;
    border: 1px solid rgba(34,211,238,.25);
    border-radius: 50%;
}

.radar-loader::after {
    inset: 38px;
}

.radar-line {
    position: absolute;
    width: 50%;
    height: 1px;
    background: var(--cyan);
    top: 50%;
    left: 50%;
    transform-origin: left;
    animation: radar 2s linear infinite;
    box-shadow: 0 0 10px var(--cyan);
}

.radar-dot {
    position: absolute;
    width: 8px;
    height: 8px;
    background: white;
    border-radius: 50%;
    left: calc(50% - 4px);
    top: calc(50% - 4px);
    box-shadow: 0 0 15px var(--cyan);
}

.calibration {
    font-family: "Orbitron", sans-serif;
    color: var(--cyan);
    letter-spacing: 5px;
    font-size: 13px;
}

.progress {
    width: 260px;
    height: 3px;
    margin-top: 16px;
    background: #17232e;
    overflow: hidden;
}

.progress-bar {
    width: 0%;
    height: 100%;
    background: var(--cyan);
    box-shadow: 0 0 12px var(--cyan);
    transition: width .2s;
}

.percent {
    margin-top: 8px;
    font-family: "Orbitron", sans-serif;
    color: #7c98a5;
    font-size: 11px;
}

.dots {
    display: flex;
    gap: 9px;
    margin-top: 30px;
}

.dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #263b47;
}

.dot.active {
    background: var(--cyan);
    box-shadow: 0 0 10px var(--cyan);
}

@keyframes radar {
    to {
        transform: rotate(360deg);
    }
}

/* =========================
   DASHBOARD
========================= */

#dashboard {
    min-height: 100vh;
    padding: 20px;
}

.header {
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(34,211,238,.18);
    margin-bottom: 18px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-icon {
    color: var(--cyan);
    font-size: 29px;
    text-shadow: 0 0 12px var(--cyan);
}

.brand-name {
    font-family: "Orbitron", sans-serif;
    font-weight: 700;
    letter-spacing: 5px;
    color: white;
}

.brand-sub {
    color: #5f7885;
    font-size: 9px;
    letter-spacing: 3px;
    margin-top: 3px;
}

.status {
    text-align: center;
    font-family: "Orbitron", sans-serif;
    font-size: 9px;
    letter-spacing: 2px;
}

.status strong {
    color: var(--green);
    text-shadow: 0 0 10px var(--green);
}

.clock {
    margin-top: 4px;
    color: var(--cyan);
    font-size: 14px;
}

.profile {
    display: flex;
    align-items: center;
    gap: 12px;
}

.profile-icon {
    width: 38px;
    height: 38px;
    border: 1px solid var(--cyan);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--cyan);
}

.profile-name {
    font-family: "Orbitron", sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
}

/* =========================
   GRID
========================= */

.grid {
    display: grid;
    grid-template-columns: 280px minmax(320px, 1fr) 320px;
    gap: 18px;
    max-width: 1600px;
    margin: auto;
}

.column {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.panel {
    position: relative;
    background: var(--panel);
    border: 1px solid rgba(34,211,238,.18);
    padding: 17px;
    backdrop-filter: blur(12px);
    box-shadow:
        inset 0 0 30px rgba(34,211,238,.025),
        0 0 20px rgba(0,0,0,.25);
}

.panel::before,
.panel::after {
    content: "";
    position: absolute;
    width: 12px;
    height: 12px;
    pointer-events: none;
}

.panel::before {
    top: -1px;
    left: -1px;
    border-top: 2px solid var(--cyan);
    border-left: 2px solid var(--cyan);
}

.panel::after {
    right: -1px;
    bottom: -1px;
    border-right: 2px solid var(--cyan);
    border-bottom: 2px solid var(--cyan);
}

.label {
    font-family: "Orbitron", sans-serif;
    font-size: 9px;
    letter-spacing: 3px;
    color: var(--cyan);
    margin-bottom: 15px;
}

.big-number {
    font-family: "Orbitron", sans-serif;
    font-size: 25px;
    color: white;
}

.unit {
    color: #5e7c89;
    font-size: 10px;
    margin-left: 4px;
}

.row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 13px 0;
}

.muted {
    color: #5f7885;
    font-size: 11px;
    letter-spacing: 1px;
}

.value {
    color: var(--cyan);
    font-family: "Orbitron", sans-serif;
    font-size: 12px;
}

.bar {
    height: 4px;
    background: #172631;
    margin-top: 6px;
}

.bar span {
    display: block;
    height: 100%;
    background: var(--cyan);
    box-shadow: 0 0 8px var(--cyan);
}

.ecg {
    height: 45px;
    margin-top: 8px;
    position: relative;
    overflow: hidden;
}

.ecg svg {
    width: 100%;
    height: 100%;
}

.ecg path {
    fill: none;
    stroke: var(--cyan);
    stroke-width: 1.5;
    filter: drop-shadow(0 0 3px var(--cyan));
    animation: ecgMove 2s linear infinite;
}

@keyframes ecgMove {
    from { transform: translateX(0); }
    to { transform: translateX(-50px); }
}

/* =========================
   CORE
========================= */

.core-panel {
    min-height: 490px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
}

.core {
    width: min(360px, 70vw);
    aspect-ratio: 1;
    border-radius: 50%;
    position: relative;
    border: 1px solid rgba(34,211,238,.25);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 35px rgba(34,211,238,.08),
        inset 0 0 35px rgba(34,211,238,.05);
}

.core::before {
    content: "";
    position: absolute;
    inset: 35px;
    border: 1px solid rgba(34,211,238,.28);
    border-radius: 50%;
}

.core::after {
    content: "";
    position: absolute;
    inset: 70px;
    border: 1px dashed rgba(34,211,238,.3);
    border-radius: 50%;
    animation: spin 12s linear infinite;
}

.crosshair {
    position: absolute;
    width: 100%;
    height: 1px;
    background: rgba(34,211,238,.2);
}

.crosshair.vertical {
    transform: rotate(90deg);
}

.core-ring {
    position: absolute;
    inset: 12px;
    border: 1px dashed rgba(34,211,238,.25);
    border-radius: 50%;
    animation: spinReverse 20s linear infinite;
}

.core-ring-2 {
    position: absolute;
    inset: 52px;
    border: 2px dotted rgba(34,211,238,.22);
    border-radius: 50%;
    animation: spin 10s linear infinite;
}

.core-center {
    z-index: 3;
    text-align: center;
    border: 1px solid var(--cyan);
    padding: 17px 28px;
    box-shadow: 0 0 20px rgba(34,211,238,.12);
}

.core-status {
    font-family: "Orbitron", sans-serif;
    font-size: 15px;
    letter-spacing: 3px;
    color: var(--cyan);
    text-shadow: 0 0 12px var(--cyan);
}

.core-id {
    margin-top: 6px;
    font-size: 9px;
    color: #56717e;
    letter-spacing: 2px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@keyframes spinReverse {
    to { transform: rotate(-360deg); }
}

/* =========================
   EQUALIZER
========================= */

.equalizer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    height: 55px;
    margin-top: 18px;
}

.eq {
    width: 3px;
    height: 15px;
    background: var(--cyan);
    box-shadow: 0 0 6px var(--cyan);
    animation: eq 1s ease-in-out infinite alternate;
}

.eq:nth-child(2) { animation-delay: .1s; }
.eq:nth-child(3) { animation-delay: .2s; }
.eq:nth-child(4) { animation-delay: .3s; }
.eq:nth-child(5) { animation-delay: .15s; }
.eq:nth-child(6) { animation-delay: .35s; }
.eq:nth-child(7) { animation-delay: .25s; }
.eq:nth-child(8) { animation-delay: .4s; }
.eq:nth-child(9) { animation-delay: .2s; }
.eq:nth-child(10) { animation-delay: .1s; }

@keyframes eq {
    from { height: 7px; opacity: .35; }
    to { height: 40px; opacity: 1; }
}

.command {
    width: min(430px, 90%);
    border: 1px solid rgba(34,211,238,.45);
    background: rgba(0,0,0,.2);
    padding: 14px 18px;
    border-radius: 30px;
    color: var(--cyan);
    font-family: "Orbitron", sans-serif;
    font-size: 10px;
    letter-spacing: 2px;
    cursor: pointer;
    text-align: center;
    transition: .2s;
}

.command:hover {
    background: rgba(34,211,238,.08);
    box-shadow: 0 0 25px rgba(34,211,238,.15);
}

.command.listening {
    border-color: var(--green);
    color: var(--green);
    box-shadow: 0 0 25px rgba(57,255,136,.15);
}

/* =========================
   POWER
========================= */

.power {
    text-align: center;
}

.power-number {
    font-family: "Orbitron", sans-serif;
    font-size: 38px;
    color: var(--cyan);
    text-shadow: 0 0 15px var(--cyan);
}

.defenses {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 7px;
    margin-top: 17px;
}

.defense {
    border: 1px solid rgba(34,211,238,.2);
    padding: 10px 2px;
    text-align: center;
    color: var(--cyan);
    font-size: 18px;
}

.defense small {
    display: block;
    font-size: 6px;
    margin-top: 5px;
    color: #587582;
    letter-spacing: 1px;
}

/* =========================
   LOG
========================= */

.log {
    height: 220px;
    overflow: hidden;
    font-family: monospace;
    font-size: 9px;
    color: #5f8794;
    line-height: 1.8;
}

.log .active {
    color: var(--cyan);
}

.terminal {
    min-height: 180px;
    font-family: monospace;
    font-size: 10px;
    color: #617c87;
    line-height: 1.7;
}

.terminal .prompt {
    color: var(--cyan);
}

.cursor {
    display: inline-block;
    width: 6px;
    height: 12px;
    background: var(--cyan);
    vertical-align: middle;
    animation: blink 1s infinite;
}

@keyframes blink {
    50% { opacity: 0; }
}

/* =========================
   CHAT
========================= */

.chat {
    margin-top: 18px;
}

.chat-box {
    display: flex;
    gap: 8px;
}

.chat-box input {
    flex: 1;
    min-width: 0;
    background: rgba(0,0,0,.25);
    border: 1px solid rgba(34,211,238,.2);
    padding: 12px;
    color: white;
    outline: none;
    font-family: "Rajdhani", sans-serif;
}

.chat-box button {
    background: transparent;
    border: 1px solid var(--cyan);
    color: var(--cyan);
    padding: 0 18px;
    cursor: pointer;
    font-family: "Orbitron", sans-serif;
    font-size: 9px;
}

.chat-response {
    margin-top: 12px;
    color: #8daab5;
    font-size: 12px;
    min-height: 30px;
}

/* =========================
   RESPONSIVE
========================= */

@media(max-width:1100px) {
    .grid {
        grid-template-columns: 1fr 1fr;
    }

    .center-column {
        grid-column: 1 / -1;
        grid-row: 1;
    }
}

@media(max-width:700px) {
    #dashboard {
        padding: 10px;
    }

    .header {
        height: auto;
        padding: 10px 0 15px;
        gap: 10px;
        flex-wrap: wrap;
    }

    .status {
        order: 3;
        width: 100%;
    }

    .grid {
        display: flex;
        flex-direction: column;
    }

    .center-column {
        order: -1;
    }

    .core-panel {
        min-height: 410px;
    }

    .splash-title {
        letter-spacing: 6px;
    }

    .profile-name {
        display: none;
    }
}
</style>
</head>

<body>

<!-- SPLASH -->
<div id="splash">

    <div class="splash-title">J.A.R.V.I.S</div>

    <div class="splash-sub">
        JUST A RATHER VERY INTELLIGENT SYSTEM
    </div>

    <div class="radar-loader">
        <div class="radar-line"></div>
        <div class="radar-dot"></div>
    </div>

    <div class="calibration">CALIBRATING</div>

    <div class="progress">
        <div class="progress-bar" id="progressBar"></div>
    </div>

    <div class="percent" id="percent">0%</div>

    <div class="dots">
        <div class="dot active"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>

</div>


<!-- DASHBOARD -->
<div id="dashboard" class="hidden">

<header class="header">

    <div class="brand">
        <div class="brand-icon">◇</div>

        <div>
            <div class="brand-name">JARVIS</div>
            <div class="brand-sub">PERSONAL ARTIFICIAL INTELLIGENCE</div>
        </div>
    </div>

    <div class="status">
        SYSTEM STATUS:
        <strong>● OPTIMAL</strong>
        <div class="clock" id="clock">00:00:00</div>
    </div>

    <div class="profile">
        <div>◉</div>
        <div>⚙</div>

        <div class="profile-icon">T</div>

        <div class="profile-name">
            T. STARK
        </div>
    </div>

</header>


<div class="grid">

<!-- LEFT -->
<div class="column">

    <div class="panel">

        <div class="label">SYSTEM // VITAL SIGNS</div>

        <div class="row">
            <span class="muted">HEART RATE</span>
            <span class="value">
                <span id="heart">72</span> BPM
            </span>
        </div>

        <div class="ecg">
            <svg viewBox="0 0 300 50" preserveAspectRatio="none">
                <path d="M0 27 L30 27 L38 26 L45 27 L53 27 L60 10 L66 43 L73 27 L100 27 L108 26 L115 27 L125 27 L132 11 L138 43 L145 27 L175 27 L183 26 L190 27 L198 27 L205 10 L212 43 L219 27 L250 27 L258 26 L265 27 L275 27 L282 10 L288 43 L295 27 L320 27"/>
            </svg>
        </div>

        <div class="row">
            <span class="muted">BODY TEMP</span>
            <span class="value">36.6 °C</span>
        </div>

        <div class="row">
            <span class="muted">NEURAL LINK</span>
            <span class="value">98.4%</span>
        </div>

    </div>


    <div class="panel">

        <div class="label">SYSTEM // RT-MONITOR</div>

        <div class="row">
            <span class="muted">CPU LOAD</span>
            <span class="value">24%</span>
        </div>

        <div class="bar">
            <span style="width:24%"></span>
        </div>

        <div class="row">
            <span class="muted">MEMORY</span>
            <span class="value">41%</span>
        </div>

        <div class="bar">
            <span style="width:41%"></span>
        </div>

        <div class="row">
            <span class="muted">STORAGE</span>
            <span class="value">37%</span>
        </div>

        <div class="bar">
            <span style="width:37%"></span>
        </div>

    </div>


    <div class="panel">

        <div class="label">NETWORK // SECURE LINK</div>

        <div class="row">
            <span class="muted">CONNECTION</span>
            <span class="value">ENCRYPTED</span>
        </div>

        <div class="row">
            <span class="muted">SATELLITE</span>
            <span class="value">ONLINE</span>
        </div>

        <div class="row">
            <span class="muted">SIGNAL</span>
            <span class="value">████████</span>
        </div>

    </div>

</div>


<!-- CENTER -->
<div class="column center-column">

    <div class="panel core-panel">

        <div class="label">
            CORE // ARTIFICIAL INTELLIGENCE
        </div>

        <div class="core">

            <div class="core-ring"></div>
            <div class="core-ring-2"></div>

            <div class="crosshair"></div>
            <div class="crosshair vertical"></div>

            <div class="core-center">

                <div class="core-status">
                    CORE ACTIVE
                </div>

                <div class="core-id">
                    JARVIS-001
                </div>

            </div>

        </div>


        <div class="equalizer">

            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>
            <div class="eq"></div>

        </div>


        <button class="command" id="micButton">
            🎙 &nbsp; AWAITING COMMAND...
        </button>


        <div class="chat">

            <div class="chat-box">

                <input
                    id="message"
                    placeholder="Escribe un comando para JARVIS..."
                    autocomplete="off"
                >

                <button onclick="sendMessage()">
                    SEND
                </button>

            </div>

            <div class="chat-response" id="response"></div>

        </div>

    </div>

</div>


<!-- RIGHT -->
<div class="column">

    <div class="panel power">

        <div class="label">POWER // CORE</div>

        <div class="power-number">97%</div>

        <div class="row">
            <span class="muted">STRUCTURAL</span>
            <span class="value">94%</span>
        </div>

        <div class="bar">
            <span style="width:94%"></span>
        </div>

        <div class="defenses">

            <div class="defense">
                ◇
                <small>SHIELD</small>
            </div>

            <div class="defense">
                ⚡
                <small>ENERGY</small>
            </div>

            <div class="defense">
                ◎
                <small>SIGNAL</small>
            </div>

            <div class="defense">
                ⬢
                <small>POWER</small>
            </div>

        </div>

    </div>


    <div class="panel">

        <div class="label">SYSTEM // LIVE LOG</div>

        <div class="log" id="log">

            <div>[17:02:01] SYSTEM BOOT</div>
            <div>[17:02:02] NEURAL CORE ONLINE</div>
            <div>[17:02:03] OPENROUTER LINK ESTABLISHED</div>
            <div>[17:02:04] MEMORY SYSTEM READY</div>
            <div>[17:02:05] AGENTS INITIALIZED</div>
            <div class="active">[17:02:06] JARVIS ONLINE</div>

        </div>

    </div>


    <div class="panel">

        <div class="label">TERMINAL // COMMAND</div>

        <div class="terminal">

            <div>
                <span class="prompt">jarvis@core:~$</span>
                jarvis --analyze --current-environment
            </div>

            <br>

            <div>
                Environment analysis complete.
            </div>

            <div>
                All primary systems operational.
            </div>

            <br>

            <div>
                <span class="prompt">jarvis@core:~$</span>
                <span class="cursor"></span>
            </div>

        </div>

    </div>

</div>

</div>
</div>


<script>

/* =========================
   SPLASH
========================= */

let progress = 0;

const progressTimer = setInterval(() => {

    progress += Math.floor(Math.random() * 7) + 3;

    if (progress >= 100) {
        progress = 100;
        clearInterval(progressTimer);

        setTimeout(() => {
            document.getElementById("splash").classList.add("hidden");
            document.getElementById("dashboard").classList.remove("hidden");
        }, 500);
    }

    document.getElementById("progressBar").style.width = progress + "%";
    document.getElementById("percent").innerText = progress + "%";

}, 120);


/* =========================
   CLOCK
========================= */

function updateClock() {

    const now = new Date();

    document.getElementById("clock").innerText =
        now.toLocaleTimeString("es-PA", {
            hour12: false
        });

}

setInterval(updateClock, 1000);
updateClock();


/* =========================
   HEART RATE
========================= */

setInterval(() => {

    const heart =
        68 + Math.floor(Math.random() * 12);

    document.getElementById("heart").innerText = heart;

}, 2500);


/* =========================
   MICROPHONE
========================= */

const micButton =
    document.getElementById("micButton");

let recognition = null;

if ("webkitSpeechRecognition" in window ||
    "SpeechRecognition" in window) {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    recognition = new SpeechRecognition();

    recognition.lang = "es-ES";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {

        micButton.classList.add("listening");

        micButton.innerText =
            "🎙  LISTENING...";

    };

    recognition.onend = () => {

        micButton.classList.remove("listening");

        micButton.innerText =
            "🎙  AWAITING COMMAND...";

    };

    recognition.onresult = event => {

        const text =
            event.results[0][0].transcript;

        document.getElementById("message").value =
            text;

        sendMessage();

    };

}

micButton.onclick = () => {

    if (recognition) {

        recognition.start();

    } else {

        alert(
            "El reconocimiento de voz no está disponible en este navegador."
        );

    }

};


/* =========================
   CHAT
========================= */

async function sendMessage() {

    const input =
        document.getElementById("message");

    const response =
        document.getElementById("response");

    const message =
        input.value.trim();

    if (!message) return;

    response.innerText =
        "JARVIS está procesando...";

    addLog("COMANDO RECIBIDO");

    try {

        const result =
            await fetch("/chat", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message: message
                })

            });

        const data =
            await result.json();

        response.innerText =
            data.response || data.error ||
            "No recibí respuesta.";

        addLog("RESPUESTA DEL CEREBRO");

        speak(data.response);

    } catch (error) {

        response.innerText =
            "Error de conexión con JARVIS.";

        addLog("ERROR DE CONEXIÓN");

    }

    input.value = "";

}


/* =========================
   ENTER
========================= */

document
.getElementById("message")
.addEventListener("keydown", event => {

    if (event.key === "Enter") {
        sendMessage();
    }

});


/* =========================
   VOICE
========================= */

function speak(text) {

    if (!text) return;

    if ("speechSynthesis" in window) {

        window.speechSynthesis.cancel();

        const speech =
            new SpeechSynthesisUtterance(text);

        speech.lang = "es-ES";
        speech.rate = 1;
        speech.pitch = 1;

        window.speechSynthesis.speak(speech);

    }

}


/* =========================
   LOG
========================= */

function addLog(message) {

    const log =
        document.getElementById("log");

    const time =
        new Date().toLocaleTimeString(
            "es-PA",
            { hour12: false }
        );

    const line =
        document.createElement("div");

    line.className = "active";

    line.innerText =
        "[" + time + "] " + message;

    log.appendChild(line);

    while (log.children.length > 9) {
        log.removeChild(log.firstChild);
    }

}

</script>

</body>
</html>
"""


# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route("/")
def home():
    return render_template_string(HTML)


# =========================
# CHAT CON OPENROUTER
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True) or {}

        message = str(data.get("message", "")).strip()

        if not message:
            return jsonify({
                "error": "No recibí ningún comando."
            }), 400

        response = client.responses.create(
            model=MODEL,
            input=message
        )

        answer = getattr(response, "output_text", None)

        if not answer:

            answer = str(response)

        return jsonify({
            "response": answer
        })

    except Exception as e:

        print("CHAT ERROR:", repr(e))

        return jsonify({
            "error": "Error del cerebro JARVIS: " + str(e)
        }), 500


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "name": "J.A.R.V.I.S"
    })


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", "8000")
    )

    app.run(
        host="0.0.0.0",
        port=port
)
