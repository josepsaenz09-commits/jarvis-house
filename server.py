import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>J.A.R.V.I.S</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@400;500;600&display=swap');

:root{
    --bg:#070b12;
    --panel:rgba(8,18,30,.78);
    --cyan:#22d3ee;
    --blue:#00d9ff;
    --green:#54f7a5;
    --red:#ff5577;
    --text:#d9f9ff;
    --muted:#71859a;
    --line:rgba(34,211,238,.28);
    --soft:rgba(34,211,238,.12);
}

*{
    box-sizing:border-box;
}

html,body{
    margin:0;
    min-height:100%;
    background:var(--bg);
    color:var(--text);
    font-family:Rajdhani,Arial,sans-serif;
}

body{
    overflow-x:hidden;

    background:
        radial-gradient(circle at 50% 45%,
        rgba(0,217,255,.08),
        transparent 35%),
        linear-gradient(rgba(34,211,238,.025) 1px,
        transparent 1px),
        linear-gradient(90deg,
        rgba(34,211,238,.025) 1px,
        transparent 1px),
        var(--bg);

    background-size:auto,32px 32px,32px 32px;
}

body:before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    background:radial-gradient(
        ellipse at center,
        transparent 45%,
        rgba(0,0,0,.65)
    );
    z-index:20;
}

/* SPLASH */

#splash{
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
    text-align:center;
    padding:24px;
}

.brand{
    font-family:Orbitron,sans-serif;
    letter-spacing:12px;
    color:var(--blue);
    font-size:clamp(38px,8vw,78px);
    text-shadow:
        0 0 8px var(--blue),
        0 0 30px rgba(0,217,255,.45);
}

.tagline{
    color:#8293a4;
    letter-spacing:4px;
    font-size:12px;
    margin-top:12px;
}

.loader{
    width:150px;
    height:150px;
    border:1px solid var(--line);
    border-radius:50%;
    margin:42px 0 18px;
    position:relative;
    box-shadow:
        0 0 30px rgba(0,217,255,.12),
        inset 0 0 25px rgba(0,217,255,.05);
    animation:spin 8s linear infinite;
}

.loader:before,
.loader:after{
    content:"";
    position:absolute;
    inset:13px;
    border:1px dashed rgba(34,211,238,.35);
    border-radius:50%;
}

.loader:after{
    inset:45px;
    border-style:solid;
    border-color:var(--cyan) transparent var(--cyan) transparent;
    animation:spin 2s linear infinite reverse;
}

.loader-dot{
    position:absolute;
    left:50%;
    top:50%;
    width:10px;
    height:10px;
    transform:translate(-50%,-50%);
    border-radius:50%;
    background:var(--cyan);
    box-shadow:0 0 20px 7px rgba(34,211,238,.55);
}

.loader-sweep{
    position:absolute;
    left:50%;
    top:50%;
    width:50%;
    height:1px;
    background:linear-gradient(90deg,var(--cyan),transparent);
    transform-origin:left;
    animation:radar 2.2s linear infinite;
}

.cal{
    font-family:Orbitron;
    color:#a7bac9;
    letter-spacing:5px;
    font-size:13px;
}

.progress{
    width:min(360px,80vw);
    height:3px;
    background:#17222d;
    margin-top:22px;
    overflow:hidden;
}

.progress i{
    display:block;
    height:100%;
    width:0;
    background:var(--cyan);
    box-shadow:0 0 12px var(--cyan);
    animation:load 3s ease forwards;
}

.percent{
    font-family:Orbitron;
    color:var(--cyan);
    font-size:11px;
    margin-top:9px;
}

.dots{
    display:flex;
    gap:8px;
    margin-top:32px;
}

.dots span{
    width:5px;
    height:5px;
    border-radius:50%;
    background:#33414d;
}

.dots span:first-child{
    background:var(--cyan);
    box-shadow:0 0 8px var(--cyan);
}

.hidden{
    display:none!important;
}

/* APP */

#app{
    padding:18px;
    max-width:1600px;
    margin:auto;
}

/* HEADER */

header{
    min-height:74px;
    border:1px solid var(--line);
    background:var(--panel);
    backdrop-filter:blur(12px);
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:12px 18px;
    position:relative;
}

.corner:before,
.corner:after{
    content:"";
    position:absolute;
    width:13px;
    height:13px;
    border-color:var(--cyan);
    border-style:solid;
    opacity:.8;
}

.corner:before{
    left:-1px;
    top:-1px;
    border-width:2px 0 0 2px;
}

.corner:after{
    right:-1px;
    bottom:-1px;
    border-width:0 2px 2px 0;
}

.logoWrap{
    display:flex;
    align-items:center;
    gap:13px;
}

.diamond{
    width:27px;
    height:27px;
    border:1px solid var(--cyan);
    transform:rotate(45deg);
    box-shadow:0 0 15px rgba(34,211,238,.4);
    position:relative;
}

.diamond i{
    position:absolute;
    inset:7px;
    background:var(--cyan);
    box-shadow:0 0 10px var(--cyan);
}

.logoText strong{
    display:block;
    font:600 21px Orbitron;
    letter-spacing:5px;
}

.logoText small{
    color:#708496;
    letter-spacing:2px;
    font-size:9px;
}

.headStats{
    display:flex;
    gap:28px;
    align-items:center;
}

.statLabel{
    font-size:9px;
    color:#63778a;
    letter-spacing:2px;
}

.statVal{
    font-family:Orbitron;
    font-size:12px;
    letter-spacing:1px;
}

.ok{
    color:var(--green);
    text-shadow:0 0 8px rgba(84,247,165,.6);
}

.headIcons{
    display:flex;
    gap:10px;
    align-items:center;
}

.iconBtn{
    width:34px;
    height:34px;
    border:1px solid var(--line);
    background:#08131f;
    color:var(--cyan);
    display:grid;
    place-items:center;
    cursor:pointer;
}

.avatar{
    width:34px;
    height:34px;
    border:1px solid var(--cyan);
    border-radius:50%;
    display:grid;
    place-items:center;
    font:11px Orbitron;
    color:var(--cyan);
    box-shadow:0 0 12px rgba(34,211,238,.15);
}

.avatarName{
    color:#71859a;
    font-size:9px;
    letter-spacing:1px;
}

/* GRID */

.grid{
    display:grid;
    grid-template-columns:1fr 1.55fr 1fr;
    gap:14px;
    margin-top:14px;
}

.col{
    display:flex;
    flex-direction:column;
    gap:14px;
}

.panel{
    position:relative;
    border:1px solid var(--line);
    background:var(--panel);
    backdrop-filter:blur(12px);
    padding:16px;
    min-height:150px;
    overflow:hidden;
}

.label{
    font:10px Orbitron;
    color:#60778b;
    letter-spacing:2px;
    margin-bottom:12px;
}

.label span{
    float:right;
    color:#345365;
}

.big{
    font:36px Orbitron;
    color:#e6fcff;
    text-shadow:0 0 12px rgba(34,211,238,.35);
}

.unit{
    font-size:11px;
    color:#63788b;
}

.row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:10px;
}

.tiny{
    font-size:11px;
    color:#7c91a2;
    letter-spacing:1px;
}

.green{
    color:var(--green);
}

.signal{
    font-size:30px;
    color:var(--cyan);
    text-shadow:0 0 15px var(--cyan);
}

/* BARS */

.bars{
    display:flex;
    align-items:end;
    gap:4px;
    height:38px;
    margin:9px 0;
}

.bars i{
    display:block;
    width:5px;
    background:var(--cyan);
    box-shadow:0 0 7px rgba(34,211,238,.45);
    animation:equal 1s infinite alternate;
}

.barLine{
    height:5px;
    background:#17232e;
    margin:6px 0 11px;
}

.barLine i{
    display:block;
    height:100%;
    background:linear-gradient(90deg,var(--cyan),#78f5ff);
    box-shadow:0 0 8px rgba(34,211,238,.5);
}

/* CENTER */

.center{
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    min-height:540px;
}

.hud{
    width:min(390px,75vw);
    aspect-ratio:1;
    border:1px solid var(--line);
    border-radius:50%;
    position:relative;
    display:grid;
    place-items:center;
    box-shadow:
        0 0 50px rgba(0,217,255,.08),
        inset 0 0 40px rgba(0,217,255,.05);
    overflow:hidden;
}

.hud:before,
.hud:after{
    content:"";
    position:absolute;
    border-radius:50%;
    border:1px solid var(--line);
}

.hud:before{
    inset:14%;
}

.hud:after{
    inset:31%;
}

.cross:before,
.cross:after{
    content:"";
    position:absolute;
    left:50%;
    top:7%;
    width:1px;
    height:86%;
    background:var(--soft);
}

.cross:after{
    transform:rotate(90deg);
}

.sweep{
    position:absolute;
    left:50%;
    top:50%;
    width:50%;
    height:2px;
    background:linear-gradient(90deg,var(--cyan),transparent);
    transform-origin:left;
    animation:radar 3s linear infinite;
    box-shadow:0 0 8px var(--cyan);
}

.ring{
    position:absolute;
    inset:6%;
    border-radius:50%;
    border:1px dashed rgba(34,211,238,.25);
    animation:spin 20s linear infinite;
}

.core{
    position:relative;
    border:1px solid var(--cyan);
    padding:13px 24px;
    font:13px Orbitron;
    letter-spacing:3px;
    color:var(--cyan);
    box-shadow:0 0 20px rgba(34,211,238,.16);
}

.core.active{
    box-shadow:
        0 0 25px rgba(34,211,238,.4),
        inset 0 0 15px rgba(34,211,238,.1);
}

.equalizer{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:5px;
    height:60px;
    margin-top:20px;
}

.equalizer i{
    width:5px;
    height:12px;
    background:var(--cyan);
    box-shadow:0 0 8px rgba(34,211,238,.55);
    animation:equal .8s infinite alternate;
}

/* COMMAND */

.commandBtn{
    margin-top:12px;
    border:1px solid var(--cyan);
    background:rgba(34,211,238,.05);
    color:var(--cyan);
    padding:13px 28px;
    border-radius:30px;
    font:11px Orbitron;
    letter-spacing:2px;
    box-shadow:0 0 18px rgba(34,211,238,.1);
    cursor:pointer;
    transition:.2s;
}

.commandBtn:hover,
.commandBtn.listening{
    background:rgba(34,211,238,.14);
    box-shadow:0 0 30px rgba(34,211,238,.35);
}

.commandBtn.speaking{
    border-color:var(--green);
    color:var(--green);
    box-shadow:0 0 30px rgba(84,247,165,.3);
}

/* VOICE PANEL */

.voicePanel{
    margin-top:14px;
}

.voiceGrid{
    display:grid;
    grid-template-columns:1.5fr .8fr .8fr;
    gap:10px;
}

.voiceSelect,
.voiceRange{
    width:100%;
    background:#050d15;
    color:#b9dbe4;
    border:1px solid var(--line);
    padding:9px;
    outline:none;
}

.voiceRange{
    padding:5px;
}

.rangeValue{
    color:var(--cyan);
    font-family:Orbitron;
}

/* DEFENSE */

.defense{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:8px;
    margin-top:12px;
}

.def{
    border:1px solid var(--soft);
    height:54px;
    display:grid;
    place-items:center;
    color:var(--cyan);
    background:#08131d;
    font-size:20px;
}

/* LOG */

.log{
    height:160px;
    overflow:auto;
    font-family:monospace;
    font-size:10px;
    color:#8097a8;
    line-height:1.8;
}

.log b{
    color:var(--cyan);
    font-weight:400;
}

/* TERMINAL */

.terminal{
    background:#03080d;
    border:1px solid var(--soft);
    padding:12px;
    font-family:monospace;
    font-size:11px;
    color:#9ab0bd;
    min-height:105px;
}

.prompt{
    color:var(--cyan);
}

.answer{
    color:#71818c;
    font-style:italic;
    margin-top:10px;
}

/* CHAT */

.chat{
    margin-top:5px;
    display:flex;
    gap:8px;
}

.chat input{
    flex:1;
    background:#050d15;
    border:1px solid var(--line);
    color:white;
    padding:13px;
    font:13px Rajdhani;
    outline:none;
}

.chat input:focus{
    border-color:var(--cyan);
    box-shadow:0 0 15px rgba(34,211,238,.1);
}

.chat button{
    border:1px solid var(--cyan);
    background:var(--cyan);
    color:#001018;
    padding:0 18px;
    font:bold 11px Orbitron;
    cursor:pointer;
}

.response{
    margin-top:10px;
    max-height:140px;
    overflow:auto;
    font-size:12px;
    color:#b9d2dd;
    line-height:1.5;
}

footer{
    text-align:center;
    color:#344a5a;
    font:8px Orbitron;
    letter-spacing:3px;
    padding:15px;
}

/* ANIMATIONS */

@keyframes spin{
    to{transform:rotate(360deg)}
}

@keyframes radar{
    to{transform:rotate(360deg)}
}

@keyframes load{
    to{width:100%}
}

@keyframes equal{
    to{height:38px}
}

/* MOBILE */

@media(max-width:1050px){

    .grid{
        grid-template-columns:1fr 1fr;
    }

    .center{
        grid-column:1/-1;
        order:-1;
    }

    .headStats{
        gap:12px;
    }
}

@media(max-width:700px){

    #app{
        padding:9px;
    }

    .grid{
        grid-template-columns:1fr;
    }

    .center{
        min-height:470px;
    }

    .headStats{
        display:none;
    }

    .iconBtn{
        display:none;
    }

    .logoText small{
        display:none;
    }

    .avatarName{
        display:none;
    }

    .hud{
        width:82vw;
    }

    .voiceGrid{
        grid-template-columns:1fr;
    }

    .chat button{
        padding:0 12px;
    }
}
</style>
</head>

<body>

<section id="splash">

    <div class="brand">J.A.R.V.I.S</div>

    <div class="tagline">
        JUST A RATHER VERY INTELLIGENT SYSTEM
    </div>

    <div class="loader">
        <div class="loader-sweep"></div>
        <div class="loader-dot"></div>
    </div>

    <div class="cal">CALIBRATING</div>

    <div class="progress">
        <i></i>
    </div>

    <div class="percent" id="pct">0%</div>

    <div class="dots">
        <span></span><span></span><span></span>
        <span></span><span></span><span></span>
    </div>

</section>


<main id="app" class="hidden">

<header class="corner">

    <div class="logoWrap">

        <div class="diamond">
            <i></i>
        </div>

        <div class="logoText">
            <strong>JARVIS</strong>
            <small>
                JUST A RATHER VERY INTELLIGENT SYSTEM
            </small>
        </div>

    </div>

    <div class="headStats">

        <div>
            <div class="statLabel">SYSTEM STATUS</div>
            <div class="statVal ok">
                ● OPTIMAL
            </div>
        </div>

        <div>
            <div class="statLabel">LOCAL TIME</div>
            <div class="statVal" id="clock">
                --:--:--
            </div>
        </div>

    </div>

    <div class="headIcons">

        <button class="iconBtn">♢</button>
        <button class="iconBtn">⚙</button>

        <div class="avatar">TS</div>

        <div class="avatarName">
            T. STARK
        </div>

    </div>

</header>


<section class="grid">


<div class="col">

    <div class="panel corner">

        <div class="label">
            SYSTEM // VITAL SIGNS
            <span>01</span>
        </div>

        <div class="row">

            <div>
                <div class="big">72</div>
                <div class="unit">
                    BPM / HEART RATE
                </div>
            </div>

            <div class="signal">⌁</div>

        </div>

        <div class="bars" id="pulseBars"></div>

        <div class="row tiny">
            <span>TEMP 36.6°C</span>

            <span class="green">
                NEURAL LINK: ACTIVE
            </span>
        </div>

    </div>


    <div class="panel corner">

        <div class="label">
            SYSTEM // RT-MONITOR
            <span>02</span>
        </div>

        <div class="tiny">
            CPU LOAD
            <b id="cpu">34%</b>
        </div>

        <div class="barLine">
            <i id="cpuBar" style="width:34%"></i>
        </div>

        <div class="tiny">
            MEMORY
            <b id="mem">61%</b>
        </div>

        <div class="barLine">
            <i id="memBar" style="width:61%"></i>
        </div>

        <div class="tiny">
            STORAGE
            <b>48%</b>
        </div>

        <div class="barLine">
            <i style="width:48%"></i>
        </div>

    </div>


    <div class="panel corner">

        <div class="label">
            NETWORK // SECURE LINK
            <span>03</span>
        </div>

        <div class="row">

            <div class="signal">◉</div>

            <div>
                <div class="statVal">
                    SIGNAL ENCRYPTED
                </div>

                <div class="tiny">
                    SAT-LINK // ORBITAL-7
                </div>
            </div>

        </div>

    </div>

</div>


<div class="col center">

    <div class="hud">

        <div class="ring"></div>
        <div class="cross"></div>
        <div class="sweep"></div>

        <div class="core" id="core">
            CORE ACTIVE
        </div>

    </div>

    <div class="equalizer" id="eq"></div>

    <button
        class="commandBtn"
        id="micButton"
        onclick="toggleVoice()">

        🎙️ &nbsp;
        <span id="micText">
            AWAITING COMMAND...
        </span>

    </button>

</div>


<div class="col">

    <div class="panel corner">

        <div class="label">
            SYSTEM // POWER CORE
            <span>04</span>
        </div>

        <div class="tiny">
            POWER CORE <b>94%</b>
        </div>

        <div class="barLine">
            <i style="width:94%"></i>
        </div>

        <div class="tiny">
            STRUCTURAL <b>87%</b>
        </div>

        <div class="barLine">
            <i style="width:87%"></i>
        </div>

        <div class="label" style="margin-top:13px">
            DEFENSE SYSTEMS
        </div>

        <div class="defense">

            <div class="def">⬡</div>
            <div class="def">ϟ</div>
            <div class="def">⌁</div>
            <div class="def">⏻</div>

        </div>

    </div>


    <div class="panel corner">

        <div class="label">
            SYSTEM // LIVE LOG
            <span>05</span>
        </div>

        <div class="log" id="log"></div>

    </div>


    <div class="panel corner">

        <div class="label">
            SYSTEM // COMMAND TERMINAL
            <span>06</span>
        </div>

        <div class="terminal">

            <div class="prompt">
                jarvis --analyze --current-environment
            </div>

            <div class="answer">
                Environment nominal.
                All primary systems operational.
                Awaiting user command.
            </div>

        </div>

    </div>

</div>

</section>


<!-- VOICE CONTROL -->

<div class="panel corner voicePanel">

    <div class="label">
        JARVIS // VOICE CONTROL
        <span>AUDIO CORE</span>
    </div>

    <div class="voiceGrid">

        <div>
            <div class="tiny">
                VOICE
            </div>

            <select
                id="voiceSelect"
                class="voiceSelect">
            </select>
        </div>

        <div>
            <div class="tiny">
                SPEED:
                <span
                    class="rangeValue"
                    id="speedValue">
                    0.92
                </span>
            </div>

            <input
                id="speed"
                class="voiceRange"
                type="range"
                min="0.65"
                max="1.15"
                step="0.01"
                value="0.92">
        </div>

        <div>
            <div class="tiny">
                PITCH:
                <span
                    class="rangeValue"
                    id="pitchValue">
                    0.92
                </span>
            </div>

            <input
                id="pitch"
                class="voiceRange"
                type="range"
                min="0.6"
                max="1.3"
                step="0.01"
                value="0.92">
        </div>

    </div>

</div>


<!-- COMMUNICATION -->

<div class="panel corner" style="margin-top:14px">

    <div class="label">
        JARVIS // DIRECT COMMUNICATION
        <span>VOICE / TEXT</span>
    </div>

    <div class="chat">

        <input
            id="message"
            placeholder="Habla con JARVIS..."
            autocomplete="off">

        <button onclick="sendMessage()">
            SEND
        </button>

    </div>

    <div
        class="response"
        id="response">
    </div>

</div>


<footer>
    J.A.R.V.I.S // CORE ONLINE // ENCRYPTED CONNECTION
</footer>

</main>


<script>

/* =========================
   SPLASH
========================= */

const splash =
    document.getElementById("splash");

const app =
    document.getElementById("app");

const pct =
    document.getElementById("pct");

let p = 0;

const timer =
    setInterval(() => {

        p += 2;

        pct.textContent =
            p + "%";

        if(p >= 100){

            clearInterval(timer);

            setTimeout(() => {

                splash.classList.add("hidden");
                app.classList.remove("hidden");

            },350);
        }

    },55);


/* =========================
   VISUAL BARS
========================= */

function makeBars(id,n){

    const el =
        document.getElementById(id);

    for(let i=0;i<n;i++){

        const x =
            document.createElement("i");

        x.style.height =
            (8 + Math.random()*30) + "px";

        el.appendChild(x);
    }
}

makeBars("pulseBars",32);
makeBars("eq",24);


/* =========================
   CLOCK
========================= */

function updateClock(){

    document.getElementById("clock")
        .textContent =
        new Date().toLocaleTimeString(
            "es-PA",
            {hour12:false}
        );
}

setInterval(updateClock,1000);
updateClock();


/* =========================
   LOG
========================= */

function logLine(text){

    const log =
        document.getElementById("log");

    const t =
        new Date().toLocaleTimeString(
            "es-PA",
            {hour12:false}
        );

    log.innerHTML =
        "<div><b>[" +
        t +
        "]</b> " +
        text +
        "</div>" +
        log.innerHTML;
}

[
    "SYSTEM INTEGRITY CHECK COMPLETE",
    "NEURAL LINK STANDBY",
    "ENCRYPTED SIGNAL ESTABLISHED",
    "CORE DIAGNOSTICS NOMINAL",
    "VOICE CORE INITIALIZED"
].forEach(
    (x,i) =>
        setTimeout(
            () => logLine(x),
            i*450
        )
);


/* =========================
   SYSTEM ACTIVITY
========================= */

setInterval(() => {

    const v =
        25 + Math.floor(Math.random()*55);

    document.getElementById("cpu")
        .textContent = v + "%";

    document.getElementById("cpuBar")
        .style.width = v + "%";


    const m =
        45 + Math.floor(Math.random()*25);

    document.getElementById("mem")
        .textContent = m + "%";

    document.getElementById("memBar")
        .style.width = m + "%";


    document.querySelectorAll(
        "#pulseBars i,#eq i"
    ).forEach(
        x =>
            x.style.height =
            (7 + Math.random()*34) + "px"
    );

},900);


/* =========================
   VOICE RECOGNITION
========================= */

let recognition = null;
let listening = false;
let speaking = false;

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

const micButton =
    document.getElementById("micButton");

const micText =
    document.getElementById("micText");

const core =
    document.getElementById("core");


if(SpeechRecognition){

    recognition =
        new SpeechRecognition();

    recognition.lang = "es-PA";
    recognition.continuous = false;
    recognition.interimResults = false;


    recognition.onstart = function(){

        listening = true;

        micText.textContent =
            "LISTENING...";

        micButton.classList.add(
            "listening"
        );

        core.classList.add("active");

        logLine(
            "MICROPHONE // LISTENING"
        );
    };


    recognition.onresult =
        function(event){

            const text =
                event.results[0][0]
                    .transcript;

            document.getElementById(
                "message"
            ).value = text;

            micText.textContent =
                "THINKING...";

            logLine(
                "VOICE COMMAND RECEIVED"
            );

            sendMessage();
        };


    recognition.onerror =
        function(event){

            listening = false;

            micButton.classList.remove(
                "listening"
            );

            micText.textContent =
                "MIC ERROR";

            logLine(
                "MIC ERROR // " +
                event.error
            );

            setTimeout(
                resetMic,
                1800
            );
        };


    recognition.onend =
        function(){

            listening = false;

            micButton.classList.remove(
                "listening"
            );

            if(!speaking){

                micText.textContent =
                    "AWAITING COMMAND...";
            }
        };
}


function resetMic(){

    if(!speaking){

        micText.textContent =
            "AWAITING COMMAND...";

        micButton.classList.remove(
            "listening",
            "speaking"
        );
    }
}


function toggleVoice(){

    if(!recognition){

        micText.textContent =
            "MIC NOT SUPPORTED";

        logLine(
            "VOICE INPUT NOT SUPPORTED"
        );

        return;
    }


    if(listening){

        recognition.stop();

        return;
    }


    try{

        recognition.start();

    }catch(error){

        console.log(error);

    }
}


/* =========================
   VOICE SYNTHESIS
========================= */

const voiceSelect =
    document.getElementById(
        "voiceSelect"
    );

const speed =
    document.getElementById(
        "speed"
    );

const pitch =
    document.getElementById(
        "pitch"
    );

const speedValue =
    document.getElementById(
        "speedValue"
    );

const pitchValue =
    document.getElementById(
        "pitchValue"
    );


function loadVoices(){

    if(!("speechSynthesis" in window))
        return;

    const voices =
        speechSynthesis.getVoices();

    voiceSelect.innerHTML = "";

    const spanish =
        voices.filter(
            v =>
                v.lang
                .toLowerCase()
                .startsWith("es")
        );

    const list =
        spanish.length
        ? spanish
        : voices;


    list.forEach(
        (voice,index) => {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                index;

            option.textContent =
                voice.name +
                " — " +
                voice.lang;

            voiceSelect.appendChild(
                option
            );
        }
    );
}


if("speechSynthesis" in window){

    speechSynthesis.onvoiceschanged =
        loadVoices;

    loadVoices();
}


speed.addEventListener(
    "input",
    () => {

        speedValue.textContent =
            speed.value;
    }
);


pitch.addEventListener(
    "input",
    () => {

        pitchValue.textContent =
            pitch.value;
    }
);


function speakJarvis(text){

    if(!("speechSynthesis" in window)){

        logLine(
            "AUDIO OUTPUT NOT SUPPORTED"
        );

        return;
    }


    speechSynthesis.cancel();


    const cleanText =
        text
        .replace(/[*#_`]/g,"")
        .replace(/\n+/g,". ")
        .trim();


    const utterance =
        new SpeechSynthesisUtterance(
            cleanText
        );


    utterance.lang = "es-PA";

    utterance.rate =
        Number(speed.value);

    utterance.pitch =
        Number(pitch.value);

    utterance.volume = 1;


    const voices =
        speechSynthesis.getVoices();


    const spanishVoices =
        voices.filter(
            v =>
                v.lang
                .toLowerCase()
                .startsWith("es")
        );


    if(spanishVoices.length){

        let selected =
            spanishVoices[
                Number(voiceSelect.value)
            ];

        if(!selected){

            selected =
                spanishVoices[0];
        }

        utterance.voice =
            selected;
    }


    utterance.onstart =
        function(){

            speaking = true;

            micText.textContent =
                "SPEAKING...";

            micButton.classList.add(
                "speaking"
            );

            core.classList.add(
                "active"
            );

            logLine(
                "AUDIO OUTPUT // SPEAKING"
            );
        };


    utterance.onend =
        function(){

            speaking = false;

            micButton.classList.remove(
                "speaking"
            );

            core.classList.remove(
                "active"
            );

            micText.textContent =
                "AWAITING COMMAND...";

            logLine(
                "AUDIO OUTPUT // COMPLETE"
            );
        };


    utterance.onerror =
        function(){

            speaking = false;

            micButton.classList.remove(
                "speaking"
            );

            micText.textContent =
                "AWAITING COMMAND...";

            logLine(
                "AUDIO OUTPUT // ERROR"
            );
        };


    speechSynthesis.speak(
        utterance
    );
}


/* =========================
   CHAT
========================= */

document
.getElementById("message")
.addEventListener(
    "keydown",
    function(e){

        if(e.key === "Enter"){

            sendMessage();

        }
    }
);


/* =========================
   SEND TO OPENROUTER
========================= */

async function sendMessage(){

    const input =
        document.getElementById(
            "message"
        );

    const response =
        document.getElementById(
            "response"
        );

    const msg =
        input.value.trim();


    if(!msg)
        return;


    micText.textContent =
        "THINKING...";

    response.textContent =
        "JARVIS // THINKING...";

    core.classList.add("active");


    logLine(
        "JARVIS // PROCESSING COMMAND"
    );


    input.value = "";


    try{

        const r =
            await fetch(
                "/chat",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message:msg
                        })
                }
            );


        const data =
            await r.json();


        const answer =
            data.response ||
            data.error ||
            "No response";


        response.textContent =
            answer;


        logLine(
            "JARVIS // RESPONSE READY"
        );


        if(data.response){

            speakJarvis(
                data.response
            );

        }else{

            resetMic();

        }


    }catch(error){

        response.textContent =
            "COMMUNICATION ERROR";

        micText.textContent =
            "CONNECTION ERROR";

        core.classList.remove(
            "active"
        );

        logLine(
            "JARVIS // CONNECTION ERROR"
        );

        setTimeout(
            resetMic,
            2000
        );
    }
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}

    message = data.get(
        "message",
        ""
    ).strip()

    if not message:

        return jsonify({
            "error":
            "No se recibió ningún mensaje"
        }), 400

    try:

        response = client.responses.create(
            model="openrouter/free",
            input=message
        )

        return jsonify({
            "response":
            response.output_text
        })

    except Exception as e:

        return jsonify({
            "error":
            str(e)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
