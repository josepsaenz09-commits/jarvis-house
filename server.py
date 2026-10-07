import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

# ============================================================
# OPENROUTER — CEREBRO DE JARVIS
# ============================================================

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ============================================================
# INTERFAZ COMPLETA JARVIS
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>

<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0,user-scalable=no">

<title>J.A.R.V.I.S.</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&display=swap"
      rel="stylesheet">

<style>

*{
    box-sizing:border-box;
    margin:0;
    padding:0;
}

body{
    background:#05080e;
    color:#8feeff;
    font-family:'Rajdhani',sans-serif;
    overflow-x:hidden;
}

/* ============================================================
   SPLASH
   ============================================================ */

#splash{
    position:fixed;
    inset:0;
    background:#05080e;
    z-index:9999;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
}

.splashTitle{
    font-family:'Orbitron';
    font-size:38px;
    letter-spacing:8px;
    color:#8feeff;
    text-shadow:0 0 20px #00d9ff;
}

.splashSub{
    margin-top:8px;
    letter-spacing:3px;
    color:#5ca8bb;
    font-size:12px;
}

.radar{
    width:150px;
    height:150px;
    margin:40px 0 25px;
    border-radius:50%;
    border:1px solid #00d9ff;
    position:relative;
    box-shadow:
        0 0 15px #00d9ff44,
        inset 0 0 30px #00d9ff22;
}

.radar:before{
    content:"";
    position:absolute;
    inset:12px;
    border-radius:50%;
    border:1px solid #00d9ff55;
}

.radar:after{
    content:"";
    position:absolute;
    left:50%;
    top:50%;
    width:65px;
    height:1px;
    background:#00eaff;
    transform-origin:left center;
    animation:sweep 2s linear infinite;
    box-shadow:0 0 10px #00eaff;
}

@keyframes sweep{
    from{transform:rotate(0deg);}
    to{transform:rotate(360deg);}
}

.calibrate{
    font-family:'Orbitron';
    font-size:11px;
    letter-spacing:4px;
}

.progress{
    width:260px;
    height:3px;
    background:#12303a;
    margin-top:15px;
    overflow:hidden;
}

.progressBar{
    height:100%;
    width:0%;
    background:#00eaff;
    box-shadow:0 0 10px #00eaff;
    transition:width .1s;
}

/* ============================================================
   APP
   ============================================================ */

#app{
    display:none;
    min-height:100vh;
    padding:14px;
    background:
        radial-gradient(circle at center,#09202a 0%,#05080e 45%,#020407 100%);
}

/* ============================================================
   HEADER
   ============================================================ */

.header{
    height:60px;
    border:1px solid #00cce844;
    background:#07121acc;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 16px;
    box-shadow:0 0 25px #00d9ff08;
}

.logo{
    display:flex;
    align-items:center;
    gap:12px;
}

.diamond{
    width:27px;
    height:27px;
    border:2px solid #00eaff;
    transform:rotate(45deg);
    box-shadow:0 0 15px #00d9ff66;
}

.logoText{
    font-family:'Orbitron';
    font-size:17px;
    letter-spacing:3px;
}

.status{
    color:#4dffbb;
    font-size:12px;
    letter-spacing:2px;
}

.headerRight{
    display:flex;
    gap:10px;
    align-items:center;
}

.icon{
    width:32px;
    height:32px;
    border:1px solid #00cce855;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#67dff1;
}

.avatar{
    width:34px;
    height:34px;
    border-radius:50%;
    border:1px solid #00eaff;
    display:flex;
    align-items:center;
    justify-content:center;
    font-family:'Orbitron';
    font-size:11px;
}

/* ============================================================
   MAIN GRID
   ============================================================ */

.grid{
    margin-top:14px;
    display:grid;
    grid-template-columns:250px 1fr 250px;
    gap:14px;
}

/* ============================================================
   PANELS
   ============================================================ */

.panel{
    border:1px solid #00cce833;
    background:#07131bd9;
    padding:14px;
    position:relative;
    overflow:hidden;
}

.panelTitle{
    font-family:'Orbitron';
    font-size:10px;
    letter-spacing:2px;
    color:#6ad9ed;
    margin-bottom:14px;
}

.panelTitle:before{
    content:"";
    display:inline-block;
    width:6px;
    height:6px;
    background:#00eaff;
    margin-right:7px;
    box-shadow:0 0 8px #00eaff;
}

/* ============================================================
   LEFT
   ============================================================ */

.metric{
    margin-bottom:18px;
}

.metricHead{
    display:flex;
    justify-content:space-between;
    font-size:11px;
    letter-spacing:1px;
}

.metricValue{
    color:#ffffff;
}

.bar{
    height:5px;
    margin-top:7px;
    background:#10232b;
}

.barFill{
    height:100%;
    background:#00d9ff;
    box-shadow:0 0 10px #00d9ff88;
}

/* ============================================================
   CENTER CORE
   ============================================================ */

.coreArea{
    min-height:580px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    position:relative;
}

.core{
    width:300px;
    height:300px;
    border-radius:50%;
    border:1px solid #00eaff;
    position:relative;
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow:
        0 0 30px #00eaff22,
        inset 0 0 50px #00eaff11;
}

.core:before{
    content:"";
    position:absolute;
    inset:25px;
    border-radius:50%;
    border:1px dashed #00d9ff77;
    animation:spin 20s linear infinite;
}

.core:after{
    content:"";
    position:absolute;
    inset:50px;
    border-radius:50%;
    border:1px solid #00d9ff44;
}

@keyframes spin{
    from{transform:rotate(0deg);}
    to{transform:rotate(360deg);}
}

.coreCenter{
    width:120px;
    height:120px;
    border-radius:50%;
    background:#062431;
    border:1px solid #00eaff;
    box-shadow:
        0 0 35px #00eaff44,
        inset 0 0 25px #00eaff33;
    display:flex;
    align-items:center;
    justify-content:center;
    font-family:'Orbitron';
    font-size:11px;
    letter-spacing:2px;
    z-index:2;
}

.sweepLine{
    position:absolute;
    width:130px;
    height:1px;
    background:#00eaff;
    transform-origin:left center;
    left:50%;
    top:50%;
    box-shadow:0 0 12px #00eaff;
    animation:sweep 3s linear infinite;
}

.coreStatus{
    margin-top:25px;
    font-family:'Orbitron';
    letter-spacing:3px;
    font-size:12px;
    color:#4dffbb;
}

.equalizer{
    display:flex;
    align-items:end;
    gap:4px;
    height:30px;
    margin-top:15px;
}

.eq{
    width:4px;
    background:#00eaff;
    animation:eq 1s ease-in-out infinite alternate;
}

.eq:nth-child(1){height:10px;animation-delay:.1s}
.eq:nth-child(2){height:20px;animation-delay:.3s}
.eq:nth-child(3){height:14px;animation-delay:.2s}
.eq:nth-child(4){height:27px;animation-delay:.5s}
.eq:nth-child(5){height:17px;animation-delay:.1s}
.eq:nth-child(6){height:24px;animation-delay:.4s}
.eq:nth-child(7){height:12px;animation-delay:.2s}

@keyframes eq{
    from{transform:scaleY(.5)}
    to{transform:scaleY(1)}
}

/* ============================================================
   COMMAND BUTTON
   ============================================================ */

.commandBtn{
    margin-top:28px;
    width:250px;
    height:48px;
    border:1px solid #00eaff;
    background:#06202a;
    color:#8feeff;
    font-family:'Orbitron';
    letter-spacing:2px;
    cursor:pointer;
    box-shadow:0 0 18px #00eaff22;
}

.commandBtn:active{
    background:#00eaff22;
}

/* ============================================================
   RIGHT
   ============================================================ */

.log{
    height:150px;
    overflow:hidden;
    font-size:10px;
    line-height:1.8;
    color:#67b8c8;
}

.log span{
    color:#4dffbb;
}

.terminal{
    height:160px;
    overflow:auto;
    font-family:monospace;
    font-size:10px;
    color:#65d7e8;
    background:#02070b;
    padding:8px;
}

/* ============================================================
   VOICE PANEL
   ============================================================ */

.voicePanel{
    margin-top:14px;
}

.voiceRow{
    margin-bottom:13px;
}

.voiceLabel{
    font-size:10px;
    letter-spacing:2px;
    color:#6ad9ed;
    margin-bottom:6px;
}

select,
input[type=range]{
    width:100%;
}

select{
    background:#041017;
    color:#8feeff;
    border:1px solid #00cce855;
    padding:8px;
}

input[type=range]{
    accent-color:#00eaff;
}

/* ============================================================
   CHAT
   ============================================================ */

.bottom{
    margin-top:14px;
    border:1px solid #00cce833;
    padding:10px;
    display:flex;
    gap:10px;
    background:#07131bd9;
}

#message{
    flex:1;
    background:#02080c;
    border:1px solid #00cce855;
    color:white;
    padding:13px;
    outline:none;
    font-family:'Rajdhani';
    font-size:15px;
}

.send{
    width:100px;
    background:#06202a;
    border:1px solid #00eaff;
    color:#8feeff;
    font-family:'Orbitron';
    cursor:pointer;
}

.mic{
    width:55px;
    border:1px solid #00eaff;
    background:#06202a;
    color:#8feeff;
    font-size:20px;
    cursor:pointer;
}

.mic.listening{
    background:#00eaff33;
    box-shadow:0 0 25px #00eaff;
}

#voiceStatus{
    text-align:center;
    margin-top:7px;
    font-size:10px;
    letter-spacing:2px;
    color:#6ad9ed;
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media(max-width:900px){

    .grid{
        grid-template-columns:1fr;
    }

    .coreArea{
        min-height:470px;
        order:-1;
    }

    .core{
        width:250px;
        height:250px;
    }

    .panel{
        min-height:auto;
    }

}

</style>
</head>

<body>

<!-- ============================================================
     SPLASH
     ============================================================ -->

<div id="splash">

    <div class="splashTitle">J.A.R.V.I.S</div>

    <div class="splashSub">
        JUST A RATHER VERY INTELLIGENT SYSTEM
    </div>

    <div class="radar"></div>

    <div class="calibrate">
        CALIBRATING
    </div>

    <div class="progress">
        <div class="progressBar" id="progressBar"></div>
    </div>

</div>


<!-- ============================================================
     APP
     ============================================================ -->

<div id="app">

    <div class="header">

        <div class="logo">

            <div class="diamond"></div>

            <div>
                <div class="logoText">J.A.R.V.I.S</div>
                <div class="status">● SYSTEM ONLINE</div>
            </div>

        </div>

        <div class="headerRight">

            <div class="icon">⌁</div>
            <div class="icon">◌</div>

            <div class="avatar">TS</div>

        </div>

    </div>


    <div class="grid">

        <!-- ====================================================
             LEFT
             ==================================================== -->

        <div>

            <div class="panel">

                <div class="panelTitle">
                    VITAL SIGNS
                </div>

                <div class="metric">

                    <div class="metricHead">
                        <span>CPU LOAD</span>
                        <span class="metricValue" id="cpu">32%</span>
                    </div>

                    <div class="bar">
                        <div class="barFill"
                             id="cpuBar"
                             style="width:32%">
                        </div>
                    </div>

                </div>

                <div class="metric">

                    <div class="metricHead">
                        <span>MEMORY</span>
                        <span class="metricValue" id="memory">48%</span>
                    </div>

                    <div class="bar">
                        <div class="barFill"
                             id="memoryBar"
                             style="width:48%">
                        </div>
                    </div>

                </div>

                <div class="metric">

                    <div class="metricHead">
                        <span>NETWORK</span>
                        <span class="metricValue">SECURE</span>
                    </div>

                    <div class="bar">
                        <div class="barFill"
                             style="width:94%">
                        </div>
                    </div>

                </div>

            </div>


            <div class="panel"
                 style="margin-top:14px">

                <div class="panelTitle">
                    RT-MONITOR
                </div>

                <div class="log" id="systemLog">

                    <div><span>[OK]</span> Neural core online</div>
                    <div><span>[OK]</span> OpenRouter connected</div>
                    <div><span>[OK]</span> Voice system ready</div>
                    <div><span>[OK]</span> HUD interface loaded</div>
                    <div><span>[OK]</span> Secure link active</div>

                </div>

            </div>


            <div class="panel"
                 style="margin-top:14px">

                <div class="panelTitle">
                    NETWORK SECURE LINK
                </div>

                <div style="font-size:11px;line-height:2">

                    ENCRYPTION
                    <span style="float:right;color:#4dffbb">
                        AES-256
                    </span>

                    <br>

                    CONNECTION
                    <span style="float:right;color:#4dffbb">
                        SECURE
                    </span>

                    <br>

                    LATENCY
                    <span style="float:right">
                        42 ms
                    </span>

                </div>

            </div>

        </div>


        <!-- ====================================================
             CENTER
             ==================================================== -->

        <div class="panel coreArea">

            <div class="core">

                <div class="sweepLine"></div>

                <div class="coreCenter">
                    CORE ACTIVE
                </div>

            </div>

            <div class="coreStatus" id="coreStatus">
                AWAITING COMMAND
            </div>

            <div class="equalizer">

                <div class="eq"></div>
                <div class="eq"></div>
                <div class="eq"></div>
                <div class="eq"></div>
                <div class="eq"></div>
                <div class="eq"></div>
                <div class="eq"></div>

            </div>


            <button class="commandBtn"
                    onclick="focusChat()">

                ◉ &nbsp; AWAITING COMMAND...

            </button>

        </div>


        <!-- ====================================================
             RIGHT
             ==================================================== -->

        <div>

            <div class="panel">

                <div class="panelTitle">
                    POWER CORE
                </div>

                <div class="metric">

                    <div class="metricHead">
                        <span>ENERGY</span>
                        <span>87%</span>
                    </div>

                    <div class="bar">
                        <div class="barFill"
                             style="width:87%">
                        </div>
                    </div>

                </div>

            </div>


            <div class="panel"
                 style="margin-top:14px">

                <div class="panelTitle">
                    DEFENSE SYSTEMS
                </div>

                <div style="line-height:2;font-size:11px">

                    PERIMETER
                    <span style="float:right;color:#4dffbb">
                        ONLINE
                    </span>

                    <br>

                    FIREWALL
                    <span style="float:right;color:#4dffbb">
                        ACTIVE
                    </span>

                    <br>

                    SECURITY
                    <span style="float:right;color:#4dffbb">
                        MAX
                    </span>

                </div>

            </div>


            <div class="panel"
                 style="margin-top:14px">

                <div class="panelTitle">
                    LIVE LOG
                </div>

                <div class="log"
                     id="liveLog">

                    <div>> Initializing...</div>
                    <div>> Waiting...</div>

                </div>

            </div>


            <div class="panel"
                 style="margin-top:14px">

                <div class="panelTitle">
                    COMMAND TERMINAL
                </div>

                <div class="terminal"
                     id="terminal">

                    JARVIS TERMINAL<br>
                    ------------------<br>
                    System ready.<br>

                </div>

            </div>


            <!-- =================================================
                 VOICE
                 ================================================= -->

            <div class="panel voicePanel">

                <div class="panelTitle">
                    JARVIS // VOICE CONTROL
                </div>

                <div class="voiceRow">

                    <div class="voiceLabel">
                        NEURAL VOICE
                    </div>

                    <select id="voiceSelect">

                        <option value="em_alex">
                            ALEX // ESPAÑOL MASCULINO
                        </option>

                        <option value="em_santa">
                            SANTA // ESPAÑOL MASCULINO
                        </option>

                        <option value="ef_dora">
                            DORA // ESPAÑOL FEMENINO
                        </option>

                    </select>

                </div>


                <div class="voiceRow">

                    <div class="voiceLabel">
                        VELOCIDAD
                    </div>

                    <input
                        id="speed"
                        type="range"
                        min="0.7"
                        max="1.3"
                        step="0.05"
                        value="0.95">

                </div>


                <div class="voiceRow">

                    <div class="voiceLabel">
                        VOLUMEN
                    </div>

                    <input
                        id="volume"
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value="1">

                </div>

                <div id="voiceStatus">
                    NEURAL VOICE READY
                </div>

            </div>

        </div>

    </div>


    <!-- ========================================================
         CHAT
         ======================================================== -->

    <div class="bottom">

        <button
            class="mic"
            id="micButton"
            onclick="startListening()">

            🎙

        </button>

        <input
            id="message"
            placeholder="Habla con JARVIS..."
            autocomplete="off">

        <button
            class="send"
            onclick="sendMessage()">

            SEND

        </button>

    </div>

</div>


<script type="module">

/* ============================================================
   KOKORO TTS
   ============================================================ */

let kokoro = null;
let kokoroLoading = false;
let currentAudio = null;

const voiceStatus =
    document.getElementById("voiceStatus");

const coreStatus =
    document.getElementById("coreStatus");


/*
   Cargamos Kokoro directamente en el navegador.

   El modelo se descarga la primera vez y el navegador
   puede guardarlo en caché.
*/

async function loadKokoro(){

    if(kokoro || kokoroLoading)
        return;

    kokoroLoading = true;

    voiceStatus.innerText =
        "LOADING NEURAL VOICE...";

    try{

        const module =
            await import(
                "https://cdn.jsdelivr.net/npm/kokoro-js@1.2.1/+esm"
            );

        const KokoroTTS =
            module.KokoroTTS;

        kokoro =
            await KokoroTTS.from_pretrained(
                "onnx-community/Kokoro-82M-v1.0-ONNX",
                {
                    dtype:"q8",
                    device:"wasm"
                }
            );

        voiceStatus.innerText =
            "NEURAL VOICE READY";

        addLog("Kokoro neural voice online");

    }catch(error){

        console.error(error);

        voiceStatus.innerText =
            "VOICE ERROR";

        addLog(
            "Kokoro error: " + error.message
        );

    }

    kokoroLoading = false;
}


/* ============================================================
   GENERAR VOZ
   ============================================================ */

async function speakJarvis(text){

    if(!text)
        return;

    await loadKokoro();

    if(!kokoro)
        return;

    try{

        if(currentAudio){

            currentAudio.pause();

            currentAudio = null;

        }

        coreStatus.innerText =
            "SPEAKING";

        voiceStatus.innerText =
            "GENERATING NEURAL SPEECH...";

        const voice =
            document.getElementById(
                "voiceSelect"
            ).value;

        const speed =
            parseFloat(
                document.getElementById(
                    "speed"
                ).value
            );

        const volume =
            parseFloat(
                document.getElementById(
                    "volume"
                ).value
            );


        const audio =
            await kokoro.generate(
                text,
                {
                    voice:voice,
                    speed:speed
                }
            );


        /*
           Kokoro devuelve audio PCM/WAV.
           Creamos un Blob y lo reproducimos.
        */

        const blob =
            new Blob(
                [audio.toBlob
                    ? await audio.toBlob()
                    : audio.audio],
                {
                    type:"audio/wav"
                }
            );


        const url =
            URL.createObjectURL(blob);

        currentAudio =
            new Audio(url);

        currentAudio.volume =
            volume;

        currentAudio.onended =
            function(){

                coreStatus.innerText =
                    "AWAITING COMMAND";

                voiceStatus.innerText =
                    "NEURAL VOICE READY";

                URL.revokeObjectURL(url);

            };


        await currentAudio.play();

        voiceStatus.innerText =
            "SPEAKING";

    }catch(error){

        console.error(error);

        voiceStatus.innerText =
            "VOICE PLAYBACK ERROR";

        coreStatus.innerText =
            "AWAITING COMMAND";

    }

}


/* ============================================================
   HACER DISPONIBLE GLOBALMENTE
   ============================================================ */

window.speakJarvis =
    speakJarvis;


/* ============================================================
   MICRÓFONO
   ============================================================ */

let recognition = null;

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if(SpeechRecognition){

    recognition =
        new SpeechRecognition();

    recognition.lang = "es-PA";

    recognition.continuous = false;

    recognition.interimResults = false;


    recognition.onstart =
        function(){

            document
                .getElementById("micButton")
                .classList.add("listening");

            coreStatus.innerText =
                "LISTENING";

            voiceStatus.innerText =
                "LISTENING...";

        };


    recognition.onresult =
        function(event){

            const text =
                event.results[0][0].transcript;

            document
                .getElementById("message")
                .value = text;

            sendMessage();

        };


    recognition.onerror =
        function(event){

            console.error(event.error);

            coreStatus.innerText =
                "AWAITING COMMAND";

            voiceStatus.innerText =
                "MIC ERROR";

        };


    recognition.onend =
        function(){

            document
                .getElementById("micButton")
                .classList.remove(
                    "listening"
                );

        };

}


/* ============================================================
   ESCUCHAR
   ============================================================ */

window.startListening =
    function(){

        if(!recognition){

            alert(
                "Tu navegador no permite reconocimiento de voz."
            );

            return;

        }

        try{

            recognition.start();

        }catch(error){

            console.log(error);

        }

    };


/* ============================================================
   ENVIAR MENSAJE
   ============================================================ */

window.sendMessage =
    async function(){

        const input =
            document.getElementById(
                "message"
            );

        const message =
            input.value.trim();

        if(!message)
            return;

        input.value = "";

        coreStatus.innerText =
            "THINKING";

        voiceStatus.innerText =
            "JARVIS THINKING...";

        addLog(
            "User: " + message
        );


        try{

            const response =
                await fetch(
                    "/chat",
                    {
                        method:"POST",

                        headers:{
                            "Content-Type":
                                "application/json"
                        },

                        body:JSON.stringify({
                            message:message
                        })
                    }
                );


            const data =
                await response.json();


            if(data.error){

                throw new Error(
                    data.error
                );

            }


            const answer =
                data.response;


            addLog(
                "JARVIS: " + answer
            );


            document.getElementById(
                "terminal"
            ).innerHTML +=
                "<br>JARVIS > " +
                escapeHtml(answer);


            await speakJarvis(answer);


        }catch(error){

            console.error(error);

            coreStatus.innerText =
                "SYSTEM ERROR";

            voiceStatus.innerText =
                "CONNECTION ERROR";

            addLog(
                "ERROR: " +
                error.message
            );

        }

    };


/* ============================================================
   ENTER
   ============================================================ */

document
    .getElementById("message")
    .addEventListener(
        "keydown",
        function(event){

            if(event.key === "Enter"){

                sendMessage();

            }

        }
    );


/* ============================================================
   FOCUS
   ============================================================ */

window.focusChat =
    function(){

        document
            .getElementById("message")
            .focus();

    };


/* ============================================================
   LOG
   ============================================================ */

function addLog(text){

    const log =
        document.getElementById(
            "liveLog"
        );

    const item =
        document.createElement("div");

    item.innerText =
        "> " + text;

    log.prepend(item);

    while(log.children.length > 8){

        log.removeChild(
            log.lastChild
        );

    }

}


/* ============================================================
   ESCAPE HTML
   ============================================================ */

function escapeHtml(text){

    return text
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;");

}


/* ============================================================
   CARGAR VOZ
   ============================================================ */

loadKokoro();


/* ============================================================
   SPLASH
   ============================================================ */

let progress = 0;

const interval =
    setInterval(
        function(){

            progress += 2;

            document
                .getElementById(
                    "progressBar"
                )
                .style.width =
                progress + "%";


            if(progress >= 100){

                clearInterval(interval);

                setTimeout(
                    function(){

                        document
                            .getElementById(
                                "splash"
                            )
                            .style.display =
                            "none";

                        document
                            .getElementById(
                                "app"
                            )
                            .style.display =
                            "block";

                    },
                    500
                );

            }

        },
        25
    );


/* ============================================================
   RELOJ
   ============================================================ */

setInterval(
    function(){

        const now =
            new Date();

        document.title =
            "J.A.R.V.I.S // " +
            now.toLocaleTimeString();

    },
    1000
);


/* ============================================================
   SIMULACIÓN DE SISTEMA
   ============================================================ */

setInterval(
    function(){

        const cpu =
            Math.floor(
                25 + Math.random()*30
            );

        const memory =
            Math.floor(
                40 + Math.random()*20
            );


        document.getElementById(
            "cpu"
        ).innerText =
            cpu + "%";


        document.getElementById(
            "cpuBar"
        ).style.width =
            cpu + "%";


        document.getElementById(
            "memory"
        ).innerText =
            memory + "%";


        document.getElementById(
            "memoryBar"
        ).style.width =
            memory + "%";

    },
    2000
);

</script>


</body>
</html>
"""


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.route("/")
def home():

    return render_template_string(HTML)


# ============================================================
# CHAT — OPENROUTER
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        message = data.get("message", "").strip()

        if not message:

            return jsonify({
                "error":"Mensaje vacío"
            }),400


        response = client.responses.create(

            model="openrouter/free",

            input=message

        )


        return jsonify({
            "response":response.output_text
        })


    except Exception as e:

        print("CHAT ERROR:",e)

        return jsonify({
            "error":str(e)
        }),500


# ============================================================
# SERVER
# ============================================================

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
