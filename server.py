import os
from flask import Flask, request, jsonify, render_template_string, Response
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#05080e">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>J.A.R.V.I.S.</title>
<link rel="manifest" href="/manifest.json">
<link rel="icon" href="/icon.svg" type="image/svg+xml">

<style>
*{box-sizing:border-box;margin:0;padding:0}

body{
    min-height:100vh;
    background:radial-gradient(circle at center,#09202b 0%,#05080e 45%,#020408 100%);
    color:#d9fbff;
    font-family:Arial,sans-serif;
    overflow-x:hidden
}

body:before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    background:
        linear-gradient(rgba(0,234,255,.025) 1px,transparent 1px),
        linear-gradient(90deg,rgba(0,234,255,.025) 1px,transparent 1px);
    background-size:35px 35px;
    z-index:-1
}

#splash{
    position:fixed;
    inset:0;
    z-index:9999;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    background:#02060a;
    transition:opacity .8s ease,visibility .8s ease
}

#splash.hide{
    opacity:0;
    visibility:hidden
}

.splash-title{
    color:#8feeff;
    font-size:clamp(35px,9vw,75px);
    font-weight:700;
    letter-spacing:9px;
    text-shadow:0 0 10px #00eaff,0 0 30px rgba(0,234,255,.7)
}

.splash-sub{
    margin-top:12px;
    color:#55cfe3;
    letter-spacing:5px;
    font-size:12px;
    text-align:center
}

.radar{
    width:180px;
    height:180px;
    margin:35px 0;
    border:1px solid rgba(0,234,255,.55);
    border-radius:50%;
    position:relative;
    background:
        radial-gradient(circle,transparent 0 30%,rgba(0,234,255,.05) 31% 31.5%,transparent 32% 60%,rgba(0,234,255,.05) 61% 61.5%,transparent 62%);
    box-shadow:0 0 30px rgba(0,234,255,.15)
}

.radar:before{
    content:"";
    position:absolute;
    left:50%;
    top:0;
    width:1px;
    height:100%;
    background:rgba(0,234,255,.25)
}

.radar:after{
    content:"";
    position:absolute;
    top:50%;
    left:0;
    width:100%;
    height:1px;
    background:rgba(0,234,255,.25)
}

.radar-line{
    position:absolute;
    width:50%;
    height:2px;
    left:50%;
    top:50%;
    transform-origin:left center;
    background:linear-gradient(90deg,#00eaff,transparent);
    animation:radar 2s linear infinite
}

@keyframes radar{
    from{transform:rotate(0deg)}
    to{transform:rotate(360deg)}
}

.progress{
    width:min(330px,80vw);
    height:4px;
    border-radius:10px;
    overflow:hidden;
    background:#10222a
}

#progressBar{
    width:0%;
    height:100%;
    background:#00eaff;
    box-shadow:0 0 15px #00eaff;
    transition:width .25s linear
}

#systemText{
    margin-top:14px;
    font-size:11px;
    color:#55cfe3;
    letter-spacing:2px
}

.app{
    width:min(1500px,100%);
    min-height:100vh;
    margin:auto;
    padding:15px
}

header{
    height:65px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    border-bottom:1px solid rgba(0,234,255,.25);
    margin-bottom:15px
}

.brand{
    font-size:22px;
    font-weight:bold;
    letter-spacing:4px;
    color:#a5f5ff;
    text-shadow:0 0 12px rgba(0,234,255,.7)
}

.status{
    display:flex;
    align-items:center;
    gap:8px;
    color:#65f6bd;
    font-size:11px;
    letter-spacing:2px
}

.status-dot{
    width:8px;
    height:8px;
    border-radius:50%;
    background:#65f6bd;
    box-shadow:0 0 12px #65f6bd
}

.grid{
    display:grid;
    grid-template-columns:270px 1fr 270px;
    gap:15px
}

.panel{
    border:1px solid rgba(0,234,255,.25);
    background:rgba(3,12,18,.72);
    box-shadow:inset 0 0 30px rgba(0,234,255,.025),0 0 20px rgba(0,0,0,.25);
    padding:15px;
    position:relative
}

.panel-title{
    font-size:10px;
    color:#55cfe3;
    letter-spacing:3px;
    margin-bottom:15px
}

.metric{margin-bottom:18px}

.metric-row{
    display:flex;
    justify-content:space-between;
    font-size:11px;
    margin-bottom:7px
}

.metric-value{color:#8feeff}

.bar{
    height:5px;
    background:#10242c;
    overflow:hidden
}

.bar span{
    display:block;
    height:100%;
    width:65%;
    background:#00eaff;
    box-shadow:0 0 10px #00eaff
}

.center{
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    min-height:650px
}

.core{
    width:min(330px,65vw);
    height:min(330px,65vw);
    max-width:330px;
    max-height:330px;
    min-width:220px;
    min-height:220px;
    border-radius:50%;
    border:2px solid rgba(0,234,255,.6);
    display:flex;
    align-items:center;
    justify-content:center;
    position:relative;
    box-shadow:0 0 25px rgba(0,234,255,.25),inset 0 0 50px rgba(0,234,255,.08)
}

.core:before,.core:after{
    content:"";
    position:absolute;
    border-radius:50%;
    border:1px solid rgba(0,234,255,.35)
}

.core:before{
    inset:25px;
    animation:spin 12s linear infinite
}

.core:after{
    inset:55px;
    border-style:dashed;
    animation:spinReverse 8s linear infinite
}

@keyframes spin{
    to{transform:rotate(360deg)}
}

@keyframes spinReverse{
    to{transform:rotate(-360deg)}
}

.core-letter{
    font-size:105px;
    font-weight:bold;
    color:#d7fbff;
    text-shadow:0 0 10px #00eaff,0 0 35px #00eaff;
    z-index:2
}

.core-label{
    margin-top:25px;
    color:#67dbea;
    font-size:12px;
    letter-spacing:4px
}

.command-button{
    margin-top:22px;
    width:75px;
    height:75px;
    border-radius:50%;
    border:2px solid #00eaff;
    background:rgba(0,234,255,.06);
    color:#9ff6ff;
    font-size:27px;
    cursor:pointer;
    box-shadow:0 0 20px rgba(0,234,255,.25);
    transition:.2s
}

.command-button:hover,.command-button.active{
    background:rgba(0,234,255,.18);
    box-shadow:0 0 25px rgba(0,234,255,.5),inset 0 0 20px rgba(0,234,255,.15);
    transform:scale(1.05)
}

.equalizer{
    display:flex;
    align-items:end;
    justify-content:center;
    gap:4px;
    height:40px;
    margin-top:20px
}

.equalizer i{
    display:block;
    width:4px;
    height:8px;
    background:#00eaff;
    box-shadow:0 0 8px #00eaff
}

.equalizer.active i{
    animation:eq .6s ease-in-out infinite alternate
}

.equalizer i:nth-child(2){animation-delay:.1s}
.equalizer i:nth-child(3){animation-delay:.2s}
.equalizer i:nth-child(4){animation-delay:.3s}
.equalizer i:nth-child(5){animation-delay:.15s}
.equalizer i:nth-child(6){animation-delay:.25s}
.equalizer i:nth-child(7){animation-delay:.05s}

@keyframes eq{
    from{height:6px}
    to{height:35px}
}

.log{
    height:250px;
    overflow-y:auto;
    font-family:monospace;
    font-size:10px;
    line-height:1.7;
    color:#65d6e8
}

.log-line{
    border-bottom:1px solid rgba(0,234,255,.05);
    padding:3px 0
}

.voice-box{margin-top:15px}

select{
    width:100%;
    background:#07131a;
    color:#bff8ff;
    border:1px solid rgba(0,234,255,.3);
    padding:10px;
    outline:none
}

.chat{
    margin-top:15px;
    border:1px solid rgba(0,234,255,.3);
    background:rgba(3,12,18,.9);
    padding:12px
}

#messages{
    height:180px;
    overflow-y:auto;
    padding:5px;
    margin-bottom:10px
}

.message{
    margin-bottom:10px;
    padding:9px 11px;
    border-left:2px solid #00eaff;
    background:rgba(0,234,255,.035);
    font-size:13px;
    line-height:1.45
}

.message.user{border-left-color:#65f6bd}

.message .who{
    color:#55cfe3;
    font-size:9px;
    letter-spacing:2px;
    margin-bottom:4px
}

.input-row{
    display:flex;
    gap:8px
}

input{
    flex:1;
    min-width:0;
    background:#061017;
    border:1px solid rgba(0,234,255,.35);
    color:white;
    padding:13px;
    outline:none
}

input:focus{
    border-color:#00eaff;
    box-shadow:0 0 10px rgba(0,234,255,.15)
}

button.small{
    border:1px solid #00eaff;
    background:rgba(0,234,255,.06);
    color:#bff8ff;
    padding:0 16px;
    cursor:pointer
}

button.small:hover{background:rgba(0,234,255,.18)}

.mic{
    width:50px;
    font-size:19px
}

.terminal{
    margin-top:15px;
    font-family:monospace;
    font-size:10px;
    color:#49bccc
}

.terminal-line{margin-bottom:5px}

.green{color:#65f6bd}
.blue{color:#8feeff}

footer{
    text-align:center;
    color:#28636d;
    font-size:9px;
    letter-spacing:2px;
    padding:15px
}

@media(max-width:950px){
    .grid{grid-template-columns:1fr}
    .center{order:-1;min-height:550px}
    .panel{width:100%}
}

@media(max-width:500px){
    .app{padding:9px}
    header{height:55px}
    .brand{font-size:17px}
    .center{min-height:470px}
    .core{min-width:220px;min-height:220px}
    .core-letter{font-size:80px}
    .input-row{flex-wrap:wrap}
    input{width:100%;flex-basis:100%}
    button.small{height:45px}
}
</style>
</head>

<body>

<div id="splash">
    <div class="splash-title">J.A.R.V.I.S.</div>
    <div class="splash-sub">JUST A RATHER VERY INTELLIGENT SYSTEM</div>
    <div class="radar"><div class="radar-line"></div></div>
    <div class="progress"><div id="progressBar"></div></div>
    <div id="systemText">INITIALIZING SYSTEM...</div>
</div>

<div class="app">

<header>
    <div class="brand">J.A.R.V.I.S.</div>
    <div class="status">
        <span class="status-dot"></span>
        SYSTEM ONLINE
    </div>
</header>

<div class="grid">

<aside>

<div class="panel">
<div class="panel-title">VITAL SYSTEMS</div>

<div class="metric">
<div class="metric-row">
<span>CPU</span>
<span class="metric-value" id="cpuValue">42%</span>
</div>
<div class="bar"><span id="cpuBar"></span></div>
</div>

<div class="metric">
<div class="metric-row">
<span>MEMORY</span>
<span class="metric-value" id="memoryValue">61%</span>
</div>
<div class="bar"><span id="memoryBar"></span></div>
</div>

<div class="metric">
<div class="metric-row">
<span>NETWORK</span>
<span class="metric-value">SECURE</span>
</div>
<div class="bar"><span style="width:94%"></span></div>
</div>

<div class="metric">
<div class="metric-row">
<span>AI CORE</span>
<span class="metric-value green">READY</span>
</div>
<div class="bar"><span style="width:100%"></span></div>
</div>
</div>

<div class="panel" style="margin-top:15px">
<div class="panel-title">NETWORK LINK</div>
<div class="terminal">
<div class="terminal-line green">● ENCRYPTION: ACTIVE</div>
<div class="terminal-line">● CHANNEL: OPENROUTER</div>
<div class="terminal-line">● CONNECTION: HTTPS</div>
<div class="terminal-line">● STATUS: STABLE</div>
</div>
</div>

</aside>

<main>

<div class="panel center">

<div class="core">
<div class="core-letter">J</div>
</div>

<div class="core-label">JARVIS CORE</div>

<button class="command-button" id="commandButton" title="Activar micrófono">🎙</button>

<div class="equalizer" id="equalizer">
<i></i><i></i><i></i><i></i><i></i><i></i><i></i>
</div>

<div id="voiceStatus" class="core-label" style="font-size:9px">
VOICE STANDBY
</div>

</div>

</main>

<aside>

<div class="panel">
<div class="panel-title">LIVE LOG</div>

<div class="log" id="log">
<div class="log-line">[SYSTEM] Boot sequence initialized.</div>
<div class="log-line">[SYSTEM] Neural interface ready.</div>
<div class="log-line">[NETWORK] Secure channel established.</div>
<div class="log-line">[AI] Waiting for command.</div>
</div>
</div>

<div class="panel" style="margin-top:15px">
<div class="panel-title">VOICE SYSTEM</div>

<div class="voice-box">
<select id="voiceMode">
<option value="auto">AUTO // BEST AVAILABLE</option>
<option value="kokoro">KOKORO // NEURAL</option>
<option value="device">DEVICE // PHONE VOICE</option>
</select>
</div>

<div class="terminal">
<div class="terminal-line">
VOICE ENGINE: <span id="voiceEngine">AUTO</span>
</div>
<div class="terminal-line">LANGUAGE: ES-PA</div>
</div>
</div>

</aside>

</div>

<div class="chat panel">

<div class="panel-title">COMMAND TERMINAL</div>

<div id="messages">
<div class="message">
<div class="who">JARVIS</div>
Sistema listo. ¿En qué puedo ayudarte?
</div>
</div>

<div class="input-row">

<button class="small mic" id="micButton" title="Hablar">🎙</button>

<input
id="messageInput"
type="text"
autocomplete="off"
placeholder="Escribe un comando para JARVIS..."
>

<button class="small" id="sendButton">ENVIAR</button>

</div>
</div>

<footer>
J.A.R.V.I.S. // PERSONAL AI INTERFACE
</footer>

</div>

<script>
"use strict";

let recognition=null;
let isListening=false;
let kokoroTTS=null;
let kokoroLoading=false;

const messages=document.getElementById("messages");
const messageInput=document.getElementById("messageInput");
const sendButton=document.getElementById("sendButton");
const micButton=document.getElementById("micButton");
const commandButton=document.getElementById("commandButton");
const voiceMode=document.getElementById("voiceMode");
const voiceStatus=document.getElementById("voiceStatus");
const voiceEngine=document.getElementById("voiceEngine");
const equalizer=document.getElementById("equalizer");
const logBox=document.getElementById("log");

function addLog(text){
    const line=document.createElement("div");
    line.className="log-line";

    const time=new Date().toLocaleTimeString("es-PA",{hour12:false});

    line.textContent="["+time+"] "+text;
    logBox.appendChild(line);
    logBox.scrollTop=logBox.scrollHeight;
}

function addMessage(who,text,isUser){
    const box=document.createElement("div");
    box.className="message"+(isUser?" user":"");

    const name=document.createElement("div");
    name.className="who";
    name.textContent=who;

    const content=document.createElement("div");
    content.textContent=text;

    box.appendChild(name);
    box.appendChild(content);
    messages.appendChild(box);
    messages.scrollTop=messages.scrollHeight;
}

function setSpeaking(active){
    if(active){
        equalizer.classList.add("active");
        voiceStatus.textContent="JARVIS SPEAKING";
    }else{
        equalizer.classList.remove("active");
        voiceStatus.textContent="VOICE STANDBY";
    }
}

function browserSpeak(text){
    return new Promise(function(resolve){

        if(!("speechSynthesis" in window)){
            resolve(false);
            return;
        }

        try{
            window.speechSynthesis.cancel();

            const utterance=new SpeechSynthesisUtterance(text);

            utterance.lang="es-PA";
            utterance.rate=1.0;
            utterance.pitch=.95;
            utterance.volume=1.0;

            const voices=window.speechSynthesis.getVoices();

            const spanishVoice=voices.find(function(v){
                return v.lang &&
                    v.lang.toLowerCase().startsWith("es");
            });

            if(spanishVoice){
                utterance.voice=spanishVoice;
            }

            utterance.onstart=function(){
                setSpeaking(true);
                addLog("VOICE: device speech active");
            };

            utterance.onend=function(){
                setSpeaking(false);
                resolve(true);
            };

            utterance.onerror=function(){
                setSpeaking(false);
                resolve(false);
            };

            window.speechSynthesis.speak(utterance);

        }catch(error){
            setSpeaking(false);
            resolve(false);
        }
    });
}

async function loadKokoro(){

    if(kokoroTTS){
        return kokoroTTS;
    }

    if(kokoroLoading){
        return null;
    }

    kokoroLoading=true;

    voiceStatus.textContent="LOADING NEURAL VOICE...";
    addLog("VOICE: loading Kokoro neural engine");

    try{

        const module=await import(
            "https://cdn.jsdelivr.net/npm/kokoro-js@1.2.1/+esm"
        );

        const KokoroTTS=module.KokoroTTS;

        kokoroTTS=await KokoroTTS.from_pretrained(
            "onnx-community/Kokoro-82M-v1.0-ONNX",
            {
                dtype:"q8",
                device:"wasm"
            }
        );

        voiceEngine.textContent="KOKORO";
        addLog("VOICE: Kokoro neural engine ready");

        return kokoroTTS;

    }catch(error){

        console.error(error);
        addLog("VOICE: Kokoro unavailable");
        kokoroTTS=null;

        return null;

    }finally{
        kokoroLoading=false;
    }
}

async function kokoroSpeak(text){

    const tts=await loadKokoro();

    if(!tts){
        return false;
    }

    try{

        setSpeaking(true);
        voiceStatus.textContent="KOKORO SPEAKING";

        const audio=await tts.generate(text,{
            voice:"ef_dora"
        });

        if(audio && typeof audio.play==="function"){

            await audio.play();

        }else if(audio && audio.audio){

            const blob=new Blob(
                [audio.audio],
                {type:"audio/wav"}
            );

            const url=URL.createObjectURL(blob);
            const player=new Audio(url);

            player.onended=function(){
                URL.revokeObjectURL(url);
                setSpeaking(false);
            };

            await player.play();

            return true;

        }else{

            setSpeaking(false);
            return false;
        }

        setSpeaking(false);
        return true;

    }catch(error){

        console.error(error);
        addLog("VOICE: Kokoro playback failed");
        setSpeaking(false);

        return false;
    }
}

async function speakJarvis(text){

    const mode=voiceMode.value;

    if(!text){
        return;
    }

    if(mode==="device"){

        voiceEngine.textContent="DEVICE";

        const worked=await browserSpeak(text);

        if(!worked){
            addLog("VOICE: device speech unavailable");
        }

        return;
    }

    if(mode==="kokoro"){

        const worked=await kokoroSpeak(text);

        if(!worked){
            voiceEngine.textContent="DEVICE FALLBACK";
            await browserSpeak(text);
        }

        return;
    }

    const kokoroWorked=await kokoroSpeak(text);

    if(kokoroWorked){
        return;
    }

    voiceEngine.textContent="DEVICE";
    await browserSpeak(text);
}

function setupSpeechRecognition(){

    const SpeechRecognition=
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if(!SpeechRecognition){
        addLog("VOICE: speech recognition unavailable");
        return;
    }

    recognition=new SpeechRecognition();

    recognition.lang="es-PA";
    recognition.continuous=false;
    recognition.interimResults=false;
    recognition.maxAlternatives=1;

    recognition.onstart=function(){

        isListening=true;

        commandButton.classList.add("active");
        micButton.classList.add("active");

        voiceStatus.textContent="LISTENING...";
        addLog("VOICE: listening");
    };

    recognition.onresult=function(event){

        const result=
            event.results[0][0].transcript;

        messageInput.value=result;

        addLog("VOICE INPUT: "+result);

        sendMessage();
    };

    recognition.onerror=function(event){

        addLog("VOICE ERROR: "+event.error);

        isListening=false;

        commandButton.classList.remove("active");
        micButton.classList.remove("active");

        voiceStatus.textContent="VOICE STANDBY";
    };

    recognition.onend=function(){

        isListening=false;

        commandButton.classList.remove("active");
        micButton.classList.remove("active");

        if(!equalizer.classList.contains("active")){
            voiceStatus.textContent="VOICE STANDBY";
        }
    };
}

function toggleListening(){

    if(!recognition){
        addLog("VOICE: recognition not supported");
        return;
    }

    if(isListening){

        recognition.stop();

    }else{

        try{
            recognition.start();
        }catch(error){
            console.error(error);
        }
    }
}

async function sendMessage(){

    const message=messageInput.value.trim();

    if(!message){
        return;
    }

    messageInput.value="";

    addMessage("TÚ",message,true);
    addLog("COMMAND: "+message);

    sendButton.disabled=true;
    sendButton.textContent="...";

    try{

        const response=await fetch("/chat",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                message:message
            })
        });

        const data=await response.json();

        if(!response.ok){
            throw new Error(
                data.error || "Error del servidor"
            );
        }

        const answer=
            data.response ||
            "No recibí una respuesta.";

        addMessage("JARVIS",answer,false);
        addLog("AI: response received");

        await speakJarvis(answer);

    }catch(error){

        console.error(error);

        const errorText=
            "No pude completar la solicitud: "+
            error.message;

        addMessage("JARVIS",errorText,false);
        addLog("ERROR: "+error.message);

    }finally{

        sendButton.disabled=false;
        sendButton.textContent="ENVIAR";
    }
}

sendButton.addEventListener(
    "click",
    sendMessage
);

messageInput.addEventListener(
    "keydown",
    function(event){
        if(event.key==="Enter"){
            sendMessage();
        }
    }
);

micButton.addEventListener(
    "click",
    toggleListening
);

commandButton.addEventListener(
    "click",
    toggleListening
);

voiceMode.addEventListener(
    "change",
    function(){

        const value=voiceMode.value;

        if(value==="auto"){
            voiceEngine.textContent="AUTO";
        }else if(value==="kokoro"){
            voiceEngine.textContent="KOKORO";
        }else{
            voiceEngine.textContent="DEVICE";
        }

        addLog(
            "VOICE MODE: "+
            value.toUpperCase()
        );
    }
);

if("speechSynthesis" in window){

    window.speechSynthesis.onvoiceschanged=function(){
        addLog("VOICE: device voices detected");
    };
}

function updateSystemMetrics(){

    const cpu=
        Math.floor(35+Math.random()*35);

    const memory=
        Math.floor(48+Math.random()*25);

    document.getElementById(
        "cpuValue"
    ).textContent=cpu+"%";

    document.getElementById(
        "memoryValue"
    ).textContent=memory+"%";

    document.getElementById(
        "cpuBar"
    ).style.width=cpu+"%";

    document.getElementById(
        "memoryBar"
    ).style.width=memory+"%";
}

setInterval(
    updateSystemMetrics,
    2500
);

function startBootSequence(){

    const progressBar=
        document.getElementById("progressBar");

    const systemText=
        document.getElementById("systemText");

    const splash=
        document.getElementById("splash");

    const steps=[
        "INITIALIZING CORE...",
        "LOADING NEURAL INTERFACE...",
        "ESTABLISHING SECURE LINK...",
        "CHECKING VOICE SYSTEM...",
        "CALIBRATING HUD...",
        "JARVIS ONLINE."
    ];

    let progress=0;
    let step=0;

    const timer=setInterval(function(){

        progress+=20;

        if(progress>100){
            progress=100;
        }

        progressBar.style.width=
            progress+"%";

        if(step<steps.length){
            systemText.textContent=
                steps[step];

            step++;
        }

        if(progress>=100){

            clearInterval(timer);

            setTimeout(function(){

                splash.classList.add("hide");

                addLog(
                    "SYSTEM: JARVIS online"
                );

            },500);
        }

    },350);
}

if("serviceWorker" in navigator){

    window.addEventListener(
        "load",
        function(){

            navigator.serviceWorker
                .register("/service-worker.js")
                .then(function(){
                    addLog(
                        "PWA: service worker registered"
                    );
                })
                .catch(function(error){

                    console.error(error);

                    addLog(
                        "PWA: service worker unavailable"
                    );
                });
        }
    );
}

setupSpeechRecognition();
startBootSequence();
updateSystemMetrics();
</script>

</body>
</html>
"""

MANIFEST = r"""
{
    "name": "J.A.R.V.I.S.",
    "short_name": "JARVIS",
    "description": "Just A Rather Very Intelligent System",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "background_color": "#05080e",
    "theme_color": "#00eaff",
    "orientation": "portrait",
    "icons": [
        {
            "src": "/icon.svg",
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}
"""

SERVICE_WORKER = r"""
const CACHE_NAME = "jarvis-pwa-v1";

const CORE_FILES = [
    "/",
    "/manifest.json",
    "/icon.svg"
];

self.addEventListener("install", function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(CORE_FILES);
        })
    );

    self.skipWaiting();
});

self.addEventListener("activate", function(event) {
    event.waitUntil(
        caches.keys().then(function(keys) {
            return Promise.all(
                keys
                    .filter(function(key) {
                        return key !== CACHE_NAME;
                    })
                    .map(function(key) {
                        return caches.delete(key);
                    })
            );
        })
    );

    self.clients.claim();
});

self.addEventListener("fetch", function(event) {
    if (event.request.method !== "GET") {
        return;
    }

    event.respondWith(
        fetch(event.request).catch(function() {
            return caches.match(event.request);
        })
    );
});
"""

ICON = r"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
    <rect width="512" height="512" rx="96" fill="#05080e"/>
    <circle
        cx="256"
        cy="256"
        r="205"
        fill="none"
        stroke="#00eaff"
        stroke-width="7"
    />
    <circle
        cx="256"
        cy="256"
        r="170"
        fill="none"
        stroke="#00eaff"
        stroke-width="2"
        opacity=".55"
    />
    <path
        d="M256 92 L420 256 L256 420 L92 256 Z"
        fill="none"
        stroke="#00eaff"
        stroke-width="8"
    />
    <circle
        cx="256"
        cy="256"
        r="82"
        fill="#062431"
        stroke="#8feeff"
        stroke-width="6"
    />
    <text
        x="256"
        y="282"
        text-anchor="middle"
        font-family="Arial,sans-serif"
        font-size="82"
        font-weight="700"
        fill="#d6fbff"
    >J</text>
</svg>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/manifest.json")
def manifest():
    return Response(
        MANIFEST,
        mimetype="application/manifest+json"
    )


@app.route("/service-worker.js")
def service_worker():
    return Response(
        SERVICE_WORKER,
        mimetype="application/javascript"
    )


@app.route("/icon.svg")
def icon():
    return Response(
        ICON,
        mimetype="image/svg+xml"
    )


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}

        message = str(
            data.get("message", "")
        ).strip()

        if not message:
            return jsonify({
                "error": "Mensaje vacío"
            }), 400

        response = client.responses.create(
            model="openrouter/free",
            input=message
        )

        answer = response.output_text

        if not answer:
            answer = "No recibí una respuesta del modelo."

        return jsonify({
            "response": answer
        })

    except Exception as e:
        print("CHAT ERROR:", e)

        return jsonify({
            "error": str(e)
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
