<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>J.A.R.V.I.S — Command Interface</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@400;500;600;700&display=swap');

:root{
  --bg:#0a0e17;
  --bg2:#060a12;
  --cyan:#22d3ee;
  --blue:#00d9ff;
  --green:#4dffb8;
  --red:#ff5577;
  --text:#d9faff;
  --muted:#617481;
  --line:rgba(34,211,238,.22);
  --glass:rgba(8,20,31,.72);
  --glow:0 0 8px rgba(34,211,238,.65),
         0 0 25px rgba(0,217,255,.18);
}

*{
  box-sizing:border-box;
  margin:0;
  padding:0;
}

html,body{
  width:100%;
  min-height:100%;
}

body{
  background:
    radial-gradient(circle at 50% 45%,rgba(0,217,255,.08),transparent 32%),
    radial-gradient(circle at 15% 20%,rgba(34,211,238,.04),transparent 25%),
    linear-gradient(135deg,var(--bg),var(--bg2));
  color:var(--text);
  font-family:'Rajdhani',sans-serif;
  overflow:hidden;
}

/* NETWORK BACKGROUND */

body:before{
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  opacity:.4;
  background-image:
    radial-gradient(circle,rgba(34,211,238,.35) 1px,transparent 1px),
    radial-gradient(circle,rgba(34,211,238,.18) 1px,transparent 1px);
  background-size:90px 90px,137px 137px;
  background-position:10px 20px,40px 70px;
}

/* SCANLINES */

body:after{
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  opacity:.06;
  background:repeating-linear-gradient(
    0deg,
    transparent 0,
    transparent 3px,
    rgba(34,211,238,.35) 4px
  );
}

/* SPLASH */

#splash{
  position:fixed;
  inset:0;
  z-index:100;
  display:flex;
  align-items:center;
  justify-content:center;
  background:#050911;
  transition:opacity 1s ease,visibility 1s ease;
}

#splash.hidden{
  opacity:0;
  visibility:hidden;
}

.boot{
  width:min(440px,85vw);
  text-align:center;
}

.boot-title{
  font-family:'Orbitron',sans-serif;
  font-size:clamp(34px,8vw,70px);
  letter-spacing:12px;
  color:var(--cyan);
  text-shadow:0 0 8px var(--cyan),0 0 35px rgba(0,217,255,.6);
  margin-right:-12px;
}

.boot-sub{
  margin-top:13px;
  color:#647781;
  font-size:12px;
  letter-spacing:4px;
}

.loader{
  width:145px;
  height:145px;
  margin:48px auto 24px;
  border:1px solid rgba(34,211,238,.25);
  border-radius:50%;
  position:relative;
  box-shadow:inset 0 0 30px rgba(34,211,238,.06);
}

.loader:before,
.loader:after{
  content:"";
  position:absolute;
  inset:12px;
  border:1px solid rgba(34,211,238,.2);
  border-radius:50%;
}

.loader:after{
  inset:0;
  border-color:transparent transparent var(--cyan) transparent;
  animation:spin 1.5s linear infinite;
}

.loader-dot{
  position:absolute;
  width:7px;
  height:7px;
  border-radius:50%;
  background:var(--cyan);
  box-shadow:0 0 12px var(--cyan),0 0 30px var(--cyan);
  top:50%;
  left:50%;
  transform:translate(-50%,-50%);
}

.loader-scan{
  position:absolute;
  width:50%;
  height:1px;
  top:50%;
  left:50%;
  transform-origin:left;
  background:linear-gradient(90deg,var(--cyan),transparent);
  animation:radar 2s linear infinite;
}

.calibrating{
  font-family:'Orbitron',sans-serif;
  font-size:13px;
  letter-spacing:5px;
  color:#b8d9df;
}

.progress{
  margin:20px auto 8px;
  height:3px;
  width:100%;
  background:#18232d;
  overflow:hidden;
}

.progress-fill{
  height:100%;
  width:0;
  background:var(--cyan);
  box-shadow:0 0 15px var(--cyan);
  transition:width .25s;
}

.percent{
  font-family:'Orbitron',sans-serif;
  font-size:11px;
  color:var(--cyan);
}

.dots{
  display:flex;
  justify-content:center;
  gap:9px;
  margin-top:35px;
}

.dots span{
  width:5px;
  height:5px;
  border-radius:50%;
  background:#34434c;
}

.dots span.active{
  background:var(--cyan);
  box-shadow:0 0 10px var(--cyan);
}

/* DASHBOARD */

#dashboard{
  width:100vw;
  height:100vh;
  padding:18px;
  opacity:0;
  transition:opacity 1s ease;
  overflow:auto;
}

#dashboard.visible{
  opacity:1;
}

.topbar{
  height:75px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  border-bottom:1px solid var(--line);
  padding:0 8px 15px;
  margin-bottom:15px;
}

.brand{
  display:flex;
  align-items:center;
  gap:14px;
}

.diamond{
  width:34px;
  height:34px;
  border:1px solid var(--cyan);
  transform:rotate(45deg);
  position:relative;
  box-shadow:var(--glow);
}

.diamond:after{
  content:"";
  position:absolute;
  inset:8px;
  border:1px solid var(--cyan);
}

.brand h1{
  font-family:'Orbitron',sans-serif;
  font-size:22px;
  letter-spacing:5px;
  color:var(--cyan);
}

.brand p{
  color:#627681;
  font-size:10px;
  letter-spacing:2px;
}

.status-area{
  display:flex;
  align-items:center;
  gap:35px;
}

.status,
.local{
  display:flex;
  flex-direction:column;
  gap:3px;
}

.label{
  color:#526570;
  font-size:9px;
  letter-spacing:3px;
}

.value{
  font-family:'Orbitron',sans-serif;
  font-size:12px;
  letter-spacing:2px;
}

.online-dot{
  display:inline-block;
  width:7px;
  height:7px;
  background:var(--green);
  border-radius:50%;
  box-shadow:0 0 10px var(--green);
  margin-right:7px;
  animation:pulse 1.5s infinite;
}

.utilities{
  display:flex;
  align-items:center;
  gap:13px;
}

.util{
  width:34px;
  height:34px;
  display:grid;
  place-items:center;
  border:1px solid var(--line);
  color:var(--cyan);
  cursor:pointer;
  transition:.25s;
}

.util:hover{
  background:rgba(34,211,238,.1);
  box-shadow:var(--glow);
}

.avatar{
  width:35px;
  height:35px;
  border:1px solid var(--cyan);
  border-radius:50%;
  display:grid;
  place-items:center;
  font-family:'Orbitron',sans-serif;
  font-size:10px;
  color:var(--cyan);
  box-shadow:var(--glow);
}

/* GRID */

.dashboard-grid{
  height:calc(100vh - 110px);
  min-height:650px;
  display:grid;
  grid-template-columns:1fr 1.45fr 1fr;
  gap:14px;
}

.column{
  display:flex;
  flex-direction:column;
  gap:14px;
  min-width:0;
}

.panel{
  position:relative;
  background:var(--glass);
  border:1px solid var(--line);
  backdrop-filter:blur(13px);
  -webkit-backdrop-filter:blur(13px);
  padding:18px;
  overflow:hidden;
}

.panel:before,
.panel:after{
  content:"";
  position:absolute;
  width:13px;
  height:13px;
  pointer-events:none;
}

.panel:before{
  top:-1px;
  left:-1px;
  border-top:1px solid var(--cyan);
  border-left:1px solid var(--cyan);
}

.panel:after{
  bottom:-1px;
  right:-1px;
  border-bottom:1px solid var(--cyan);
  border-right:1px solid var(--cyan);
}

.panel-label{
  display:flex;
  justify-content:space-between;
  color:#566c77;
  font-size:9px;
  letter-spacing:2px;
  margin-bottom:16px;
}

.panel-label span:last-child{
  color:#31515e;
}

/* LEFT */

.vitals{
  height:31%;
  min-height:190px;
}

.heart{
  display:flex;
  align-items:center;
  gap:13px;
}

.heart-icon{
  color:var(--red);
  font-size:25px;
  animation:heart 1s infinite;
  text-shadow:0 0 12px rgba(255,85,119,.7);
}

.heart-number{
  font-family:'Orbitron',sans-serif;
  font-size:34px;
  color:#e9fbff;
}

.unit{
  color:#637782;
  font-size:10px;
  letter-spacing:2px;
}

.ecg{
  height:48px;
  margin:14px 0;
  position:relative;
  overflow:hidden;
}

.ecg svg{
  width:100%;
  height:100%;
}

.ecg-line{
  fill:none;
  stroke:var(--cyan);
  stroke-width:1.5;
  stroke-dasharray:120 15;
  animation:ecgMove 2s linear infinite;
  filter:drop-shadow(0 0 5px var(--cyan));
}

.secondary{
  display:flex;
  justify-content:space-between;
}

.secondary div{
  color:#637782;
  font-size:10px;
  letter-spacing:1px;
}

.secondary b{
  display:block;
  color:#cceaf0;
  font-size:14px;
  margin-top:3px;
}

.monitor{
  flex:1;
  min-height:220px;
}

.metric{
  margin-bottom:19px;
}

.metric-head{
  display:flex;
  justify-content:space-between;
  color:#728791;
  font-size:10px;
  letter-spacing:2px;
  margin-bottom:7px;
}

.metric-head b{
  color:var(--cyan);
}

.bar{
  height:4px;
  background:#17242c;
}

.bar span{
  display:block;
  height:100%;
  background:var(--cyan);
  box-shadow:0 0 8px rgba(34,211,238,.6);
  animation:barGlow 2s infinite alternate;
}

.network{
  height:24%;
  min-height:150px;
  display:flex;
  flex-direction:column;
  justify-content:center;
}

.signal{
  display:flex;
  align-items:center;
  gap:15px;
}

.signal-icon{
  width:46px;
  height:46px;
  border:1px solid var(--cyan);
  border-radius:50%;
  display:grid;
  place-items:center;
  color:var(--cyan);
  font-size:20px;
  box-shadow:inset 0 0 15px rgba(34,211,238,.08);
}

.signal-title{
  font-family:'Orbitron',sans-serif;
  font-size:13px;
  letter-spacing:2px;
}

.signal-sub{
  color:#556c77;
  font-size:10px;
  letter-spacing:2px;
  margin-top:5px;
}

/* CENTER */

.center{
  align-items:center;
}

.core-panel{
  flex:1;
  width:100%;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  min-height:430px;
}

.core{
  width:min(390px,75%);
  aspect-ratio:1;
  position:relative;
  display:grid;
  place-items:center;
}

.ring{
  position:absolute;
  border-radius:50%;
  border:1px solid rgba(34,211,238,.25);
}

.r1{
  inset:3%;
  border-top-color:var(--cyan);
  animation:spin 8s linear infinite;
}

.r2{
  inset:12%;
  border-right-color:var(--cyan);
  animation:spinReverse 12s linear infinite;
}

.r3{
  inset:23%;
  border-left-color:var(--cyan);
  border-style:dashed;
  animation:spin 15s linear infinite;
}

.r4{
  inset:35%;
  border-bottom-color:var(--cyan);
  animation:spinReverse 5s linear infinite;
}

.cross-h,
.cross-v{
  position:absolute;
  background:rgba(34,211,238,.17);
}

.cross-h{
  height:1px;
  left:0;
  right:0;
}

.cross-v{
  width:1px;
  top:0;
  bottom:0;
}

.diagonal{
  position:absolute;
  width:100%;
  height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);
  transform:rotate(45deg);
  opacity:.25;
}

.diagonal.d2{
  transform:rotate(-45deg);
}

.orbit-dot{
  position:absolute;
  width:7px;
  height:7px;
  border-radius:50%;
  background:var(--cyan);
  box-shadow:0 0 12px var(--cyan);
}

.orbit-dot.one{
  top:7%;
  left:49%;
  animation:orbit1 4s linear infinite;
}

.core-center{
  width:145px;
  height:80px;
  border:1px solid rgba(34,211,238,.55);
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  position:relative;
  background:rgba(5,15,24,.6);
  box-shadow:0 0 25px rgba(0,217,255,.08);
}

.core-center:before,
.core-center:after{
  content:"";
  position:absolute;
  width:10px;
  height:10px;
}

.core-center:before{
  top:-1px;
  left:-1px;
  border-top:2px solid var(--cyan);
  border-left:2px solid var(--cyan);
}

.core-center:after{
  bottom:-1px;
  right:-1px;
  border-bottom:2px solid var(--cyan);
  border-right:2px solid var(--cyan);
}

.core-title{
  font-family:'Orbitron',sans-serif;
  font-size:15px;
  letter-spacing:4px;
  color:var(--cyan);
  text-shadow:0 0 10px var(--cyan);
}

.core-sub{
  color:#58717c;
  font-size:9px;
  letter-spacing:2px;
  margin-top:5px;
}

.equalizer{
  width:80%;
  height:60px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:4px;
  margin-top:15px;
}

.equalizer span{
  width:3px;
  height:20%;
  background:var(--cyan);
  box-shadow:0 0 8px rgba(34,211,238,.5);
  animation:eq .8s ease-in-out infinite alternate;
}

.equalizer span:nth-child(2n){animation-delay:.15s}
.equalizer span:nth-child(3n){animation-delay:.3s}
.equalizer span:nth-child(4n){animation-delay:.45s}

.command{
  width:min(410px,90%);
  height:48px;
  border:1px solid rgba(34,211,238,.5);
  border-radius:30px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:12px;
  color:var(--cyan);
  font-family:'Orbitron',sans-serif;
  font-size:10px;
  letter-spacing:2px;
  box-shadow:0 0 20px rgba(34,211,238,.07);
  cursor:pointer;
  transition:.3s;
}

.command:hover{
  background:rgba(34,211,238,.08);
  box-shadow:var(--glow);
}

.mic{
  width:24px;
  height:24px;
  border:1px solid var(--cyan);
  border-radius:50%;
  display:grid;
  place-items:center;
  font-size:11px;
}

/* RIGHT */

.power{
  height:31%;
  min-height:220px;
}

.power-row{
  margin-bottom:15px;
}

.power-info{
  display:flex;
  justify-content:space-between;
  font-size:10px;
  letter-spacing:2px;
  color:#738790;
  margin-bottom:6px;
}

.power-info b{
  color:var(--cyan);
}

.defense-title{
  margin-top:18px;
  color:#566c77;
  font-size:9px;
  letter-spacing:2px;
}

.defense{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:7px;
  margin-top:9px;
}

.defense button{
  height:40px;
  background:rgba(34,211,238,.025);
  border:1px solid var(--line);
  color:var(--cyan);
  cursor:pointer;
  transition:.2s;
}

.defense button:hover{
  background:rgba(34,211,238,.12);
  box-shadow:var(--glow);
}

.logs{
  flex:1;
  min-height:220px;
}

.log-list{
  font-family:'Share Tech Mono',monospace;
  font-size:9px;
  color:#6e8791;
  line-height:2;
  height:calc(100% - 25px);
  overflow:hidden;
}

.log-list .ok{
  color:#5fcfa8;
}

.log-list .cyan{
  color:var(--cyan);
}

.terminal{
  height:25%;
  min-height:165px;
  background:rgba(1,6,10,.7);
}

.terminal-body{
  font-family:'Share Tech Mono',monospace;
  font-size:10px;
  line-height:1.8;
  color:#8aa2ac;
}

.prompt{
  color:var(--cyan);
}

.response{
  color:#5d7079;
  font-style:italic;
  margin-top:9px;
}

/* ANIMATIONS */

@keyframes spin{
  to{transform:rotate(360deg)}
}

@keyframes spinReverse{
  to{transform:rotate(-360deg)}
}

@keyframes radar{
  to{transform:rotate(360deg)}
}

@keyframes pulse{
  50%{opacity:.45;box-shadow:0 0 3px var(--green)}
}

@keyframes heart{
  50%{transform:scale(1.15)}
}

@keyframes ecgMove{
  to{stroke-dashoffset:-270}
}

@keyframes barGlow{
  from{opacity:.65}
  to{opacity:1}
}

@keyframes eq{
  from{height:15%}
  to{height:90%}
}

@keyframes orbit1{
  0%{transform:rotate(0deg) translateX(165px)}
  100%{transform:rotate(360deg) translateX(165px)}
}

/* RESPONSIVE */

@media(max-width:1100px){
  body{overflow:auto}

  #dashboard{
    height:auto;
    min-height:100vh;
    overflow:visible;
  }

  .dashboard-grid{
    height:auto;
    min-height:0;
    grid-template-columns:1fr 1fr;
  }

  .center{
    grid-column:1/-1;
    grid-row:1;
  }

  .center .core-panel{
    min-height:560px;
  }

  .column.left{
    grid-column:1;
  }

  .column.right{
    grid-column:2;
  }
}

@media(max-width:700px){
  #dashboard{
    padding:10px;
  }

  .topbar{
    height:auto;
    min-height:70px;
    flex-wrap:wrap;
    gap:12px;
  }

  .brand p{
    display:none;
  }

  .status-area{
    gap:12px;
  }

  .status-area .local{
    display:none;
  }

  .utilities{
    margin-left:auto;
  }

  .dashboard-grid{
    display:flex;
    flex-direction:column;
  }

  .center{
    order:-1;
  }

  .center .core-panel{
    min-height:500px;
  }

  .core{
    width:min(330px,82vw);
  }

  .r1{inset:0}
  .r2{inset:11%}
  .r3{inset:22%}
  .r4{inset:34%}

  .orbit-dot.one{
    animation-name:none;
    top:3%;
    left:50%;
  }

  .panel{
    min-height:180px;
  }

  .vitals,
  .power,
  .network,
  .terminal{
    height:auto;
  }

  .monitor,
  .logs{
    min-height:230px;
  }

  .boot-title{
    letter-spacing:7px;
  }
}

@media(max-width:420px){
  .brand h1{
    font-size:18px;
    letter-spacing:3px;
  }

  .status .value{
    font-size:10px;
  }

  .command{
    font-size:8px;
  }
}
</style>
</head>

<body>

<!-- SPLASH SCREEN -->

<section id="splash">
  <div class="boot">

    <div class="boot-title">J.A.R.V.I.S</div>

    <div class="boot-sub">
      JUST A RATHER VERY INTELLIGENT SYSTEM
    </div>

    <div class="loader">
      <div class="loader-dot"></div>
      <div class="loader-scan"></div>
    </div>

    <div class="calibrating">CALIBRATING</div>

    <div class="progress">
      <div class="progress-fill" id="progressFill"></div>
    </div>

    <div class="percent" id="percent">00%</div>

    <div class="dots">
      <span class="active"></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
      <span></span>
    </div>

  </div>
</section>


<!-- MAIN DASHBOARD -->

<main id="dashboard">

  <!-- HEADER -->

  <header class="topbar">

    <div class="brand">
      <div class="diamond"></div>

      <div>
        <h1>JARVIS</h1>
        <p>JUST A RATHER VERY INTELLIGENT SYSTEM</p>
      </div>
    </div>

    <div class="status-area">

      <div class="status">
        <div class="label">SYSTEM STATUS</div>
        <div class="value">
          <span class="online-dot"></span>OPTIMAL
        </div>
      </div>

      <div class="local">
        <div class="label">LOCAL TIME</div>
        <div class="value" id="clock">00:00:00</div>
      </div>

      <div class="utilities">
        <button class="util">◉</button>
        <button class="util">⚙</button>
        <div class="avatar">TS</div>
      </div>

    </div>

  </header>


  <!-- DASHBOARD GRID -->

  <section class="dashboard-grid">

    <!-- LEFT COLUMN -->

    <div class="column left">

      <!-- VITAL SIGNS -->

      <section class="panel vitals">

        <div class="panel-label">
          <span>SYSTEM // VITAL SIGNS</span>
          <span>VS-01</span>
        </div>

        <div class="heart">

          <div class="heart-icon">♥</div>

          <div>
            <div class="heart-number">72</div>
            <div class="unit">BPM // HEART RATE</div>
          </div>

        </div>

        <div class="ecg">
          <svg viewBox="0 0 500 80" preserveAspectRatio="none">
            <polyline
              class="ecg-line"
              points="0,40 50,40 70,40 80,10 95,70 108,40 160,40 180,40 190,15 205,65 220,40 280,40 300,40 310,10 325,70 340,40 400,40 420,40 430,15 445,65 460,40 500,40"/>
          </svg>
        </div>

        <div class="secondary">

          <div>
            TEMPERATURE
            <b>36.6°C</b>
          </div>

          <div>
            NEURAL LINK
            <b style="color:var(--green)">STABLE</b>
          </div>

        </div>

      </section>


      <!-- RESOURCE MONITOR -->

      <section class="panel monitor">

        <div class="panel-label">
          <span>SYSTEM // RT-MONITOR</span>
          <span>RT-02</span>
        </div>

        <div class="metric">
          <div class="metric-head">
            <span>CPU LOAD</span>
            <b>34%</b>
          </div>
          <div class="bar"><span style="width:34%"></span></div>
        </div>

        <div class="metric">
          <div class="metric-head">
            <span>MEMORY</span>
            <b>61%</b>
          </div>
          <div class="bar"><span style="width:61%"></span></div>
        </div>

        <div class="metric">
          <div class="metric-head">
            <span>STORAGE</span>
            <b>42%</b>
          </div>
          <div class="bar"><span style="width:42%"></span></div>
        </div>

      </section>


      <!-- NETWORK -->

      <section class="panel network">

        <div class="panel-label">
          <span>NETWORK // LINK</span>
          <span>NET-07</span>
        </div>

        <div class="signal">

          <div class="signal-icon">⌁</div>

          <div>
            <div class="signal-title">SIGNAL ENCRYPTED</div>
            <div class="signal-sub">SAT-LINK // ORBITAL NODE 07</div>
          </div>

        </div>

      </section>

    </div>


    <!-- CENTER COLUMN -->

    <div class="column center">

      <section class="panel core-panel">

        <div class="panel-label" style="width:100%">
          <span>CORE // NEURAL INTERFACE</span>
          <span>CORE-01</span>
        </div>

        <div class="core">

          <div class="ring r1"></div>
          <div class="ring r2"></div>
          <div class="ring r3"></div>
          <div class="ring r4"></div>

          <div class="cross-h"></div>
          <div class="cross-v"></div>

          <div class="diagonal"></div>
          <div class="diagonal d2"></div>

          <div class="orbit-dot one"></div>

          <div class="core-center">
            <div class="core-title">CORE ACTIVE</div>
            <div class="core-sub">J.A.R.V.I.S // ONLINE</div>
          </div>

        </div>


        <div class="equalizer" id="equalizer"></div>


        <button class="command" id="commandButton">
          <span class="mic">●</span>
          <span id="commandText">AWAITING COMMAND...</span>
        </button>

      </section>

    </div>


    <!-- RIGHT COLUMN -->

    <div class="column right">

      <!-- POWER CORE -->

      <section class="panel power">

        <div class="panel-label">
          <span>SYSTEM // POWER CORE</span>
          <span>PWR-03</span>
        </div>

        <div class="power-row">

          <div class="power-info">
            <span>POWER CORE</span>
            <b>94%</b>
          </div>

          <div class="bar">
            <span style="width:94%"></span>
          </div>

        </div>

        <div class="power-row">

          <div class="power-info">
            <span>STRUCTURAL</span>
            <b>87%</b>
          </div>

          <div class="bar">
            <span style="width:87%"></span>
          </div>

        </div>

        <div class="defense-title">DEFENSE SYSTEMS</div>

        <div class="defense">
          <button>⬡</button>
          <button>ϟ</button>
          <button>⌁</button>
          <button>⏻</button>
        </div>

      </section>


      <!-- LOG -->

      <section class="panel logs">

        <div class="panel-label">
          <span>SYSTEM // LIVE LOG</span>
          <span>LOG-11</span>
        </div>

        <div class="log-list" id="logs">

          <div><span>[12:45:01]</span> <span class="ok">SYSTEM INTEGRITY CHECK COMPLETE</span></div>
          <div><span>[12:45:03]</span> NEURAL CORE SYNCHRONIZED</div>
          <div><span>[12:45:06]</span> MEMORY MATRIX ONLINE</div>
          <div><span>[12:45:09]</span> NETWORK CHANNEL ENCRYPTED</div>
          <div><span>[12:45:12]</span> <span class="cyan">AI CORE INITIALIZED</span></div>
          <div><span>[12:45:16]</span> SENSOR ARRAY NOMINAL</div>
          <div><span>[12:45:20]</span> DEFENSE SYSTEMS STANDBY</div>

        </div>

      </section>


      <!-- TERMINAL -->

      <section class="panel terminal">

        <div class="panel-label">
          <span>TOOLS // TERMINAL</span>
          <span>TERM-04</span>
        </div>

        <div class="terminal-body">

          <div>
            <span class="prompt">jarvis@core:~$</span>
            jarvis --analyze --current-environment
          </div>

          <div class="response">
            Environment analysis complete. All primary systems operating within nominal parameters.
          </div>

          <div>
            <span class="prompt">jarvis@core:~$</span>
            <span class="blink">_</span>
          </div>

        </div>

      </section>

    </div>

  </section>

</main>


<script>

/* =========================
   SPLASH CALIBRATION
========================= */

const splash = document.getElementById("splash");
const dashboard = document.getElementById("dashboard");
const progressFill = document.getElementById("progressFill");
const percent = document.getElementById("percent");

let progress = 0;

const calibration = setInterval(() => {

  progress += Math.floor(Math.random() * 5) + 1;

  if(progress >= 100){
    progress = 100;
    clearInterval(calibration);

    setTimeout(() => {
      splash.classList.add("hidden");
      dashboard.classList.add("visible");
      document.body.style.overflow = "auto";
    },700);
  }

  progressFill.style.width = progress + "%";
  percent.textContent = String(progress).padStart(2,"0") + "%";

},120);


/* =========================
   LIVE CLOCK
========================= */

function updateClock(){

  const now = new Date();

  const h = String(now.getHours()).padStart(2,"0");
  const m = String(now.getMinutes()).padStart(2,"0");
  const s = String(now.getSeconds()).padStart(2,"0");

  document.getElementById("clock").textContent =
    `${h}:${m}:${s}`;
}

setInterval(updateClock,1000);
updateClock();


/* =========================
   AUDIO EQUALIZER
========================= */

const equalizer = document.getElementById("equalizer");

for(let i=0;i<38;i++){

  const bar = document.createElement("span");

  bar.style.animationDuration =
    (0.45 + Math.random() * 0.8) + "s";

  bar.style.height =
    (15 + Math.random() * 65) + "%";

  equalizer.appendChild(bar);
}


/* =========================
   COMMAND BUTTON
========================= */

const commandButton =
  document.getElementById("commandButton");

const commandText =
  document.getElementById("commandText");

let listening = false;

commandButton.addEventListener("click",()=>{

  listening = !listening;

  if(listening){

    commandText.textContent =
      "LISTENING...";

    commandButton.style.boxShadow =
      "0 0 20px rgba(34,211,238,.6), inset 0 0 20px rgba(34,211,238,.08)";

  }else{

    commandText.textContent =
      "AWAITING COMMAND...";

    commandButton.style.boxShadow = "";

  }

});


/* =========================
   LIVE SYSTEM LOGS
========================= */

const logs = document.getElementById("logs");

const messages = [
  "AI CORE HEARTBEAT RECEIVED",
  "NEURAL NETWORK SYNCHRONIZED",
  "BACKGROUND SERVICES NOMINAL",
  "SECURE CHANNEL VERIFIED",
  "MEMORY INDEX UPDATED",
  "SENSOR ARRAY SCAN COMPLETE",
  "COMMAND INTERFACE READY",
  "SYSTEM TELEMETRY REFRESHED"
];

setInterval(()=>{

  const now = new Date();

  const time =
    [
      now.getHours(),
      now.getMinutes(),
      now.getSeconds()
    ]
    .map(x=>String(x).padStart(2,"0"))
    .join(":");

  const entry = document.createElement("div");

  entry.innerHTML =
    `<span>[${time}]</span> ${messages[Math.floor(Math.random()*messages.length)]}`;

  logs.appendChild(entry);

  while(logs.children.length > 8){
    logs.removeChild(logs.firstChild);
  }

},3500);


/* =========================
   TERMINAL CURSOR
========================= */

setInterval(()=>{

  const cursor =
    document.querySelector(".blink");

  if(cursor){
    cursor.style.opacity =
      cursor.style.opacity === "0" ? "1" : "0";
  }

},500);

</script>

</body>
</html>
