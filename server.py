import os,json,sqlite3,urllib.parse,urllib.request,re
from flask import Flask,request,jsonify,Response
from openai import OpenAI

app=Flask(__name__)
DB="jarvis_memory.db"

ai=OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ================= MEMORIA =================

def database():
    c=sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY AUTOINCREMENT,text TEXT)")
    c.commit()
    return c

def save_memory(text):
    c=database()
    c.execute("INSERT INTO memory(text) VALUES(?)",(text,))
    c.commit()
    c.close()

def get_memory():
    c=database()
    r=c.execute("SELECT text FROM memory ORDER BY id DESC LIMIT 40").fetchall()
    c.close()
    return [x[0] for x in r]

# ================= WEB =================

def search_web(query):
    try:
        url="https://html.duckduckgo.com/html/?q="+urllib.parse.quote(query)
        req=urllib.request.Request(
            url,
            headers={"User-Agent":"Mozilla/5.0"}
        )
        page=urllib.request.urlopen(req,timeout=10).read().decode("utf-8","ignore")

        results=[]
        pattern=r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'

        for m in re.finditer(pattern,page,re.S):
            link=m.group(1)
            title=re.sub("<.*?>","",m.group(2))
            title=title.replace("&amp;","&").strip()

            if title and link:
                results.append({
                    "title":title,
                    "url":link
                })

            if len(results)>=6:
                break

        return results
    except:
        return []

# ================= PWA =================

@app.route("/manifest.json")
def manifest():
    return Response(json.dumps({
        "name":"J.A.R.V.I.S.",
        "short_name":"JARVIS",
        "description":"Just A Rather Very Intelligent System",
        "start_url":"/",
        "scope":"/",
        "display":"standalone",
        "background_color":"#05080e",
        "theme_color":"#22d3ee",
        "orientation":"portrait",
        "icons":[{
            "src":"/icon.svg",
            "sizes":"any",
            "type":"image/svg+xml",
            "purpose":"any maskable"
        }]
    }),mimetype="application/manifest+json")

@app.route("/icon.svg")
def icon():
    return Response("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="90" fill="#05080e"/>
<circle cx="256" cy="256" r="205" fill="none" stroke="#22d3ee" stroke-width="7"/>
<circle cx="256" cy="256" r="170" fill="none" stroke="#22d3ee" stroke-width="2" opacity=".5"/>
<path d="M256 75L437 256 256 437 75 256Z" fill="none" stroke="#22d3ee" stroke-width="8"/>
<circle cx="256" cy="256" r="82" fill="#062431" stroke="#b9f8ff" stroke-width="6"/>
<text x="256" y="283" text-anchor="middle" font-family="Arial" font-size="82" font-weight="bold" fill="#d6fbff">J</text>
</svg>""",mimetype="image/svg+xml")

@app.route("/service-worker.js")
def service_worker():
    return Response("""const CACHE="JARVIS-V3";
self.addEventListener("install",e=>{
 e.waitUntil(caches.open(CACHE).then(c=>c.addAll(["/","/manifest.json","/icon.svg"])));
 self.skipWaiting();
});
self.addEventListener("activate",e=>{
 e.waitUntil(self.clients.claim());
});
self.addEventListener("fetch",e=>{
 if(e.request.method==="GET"){
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
 }
});
""",mimetype="application/javascript")

# ================= CEREBRO =================

@app.route("/chat",methods=["POST"])
def chat():
    data=request.get_json(force=True)
    message=str(data.get("message","")).strip()

    if not message:
        return jsonify({"reply":"Te escucho."})

    low=message.lower()

    # MEMORIA
    if re.match(r"^(recuerda|recuerda que|guarda|guarda que)\b",low):
        text=re.sub(
            r"^(recuerda|recuerda que|guarda|guarda que)\s*",
            "",
            message,
            flags=re.I
        )
        if text:
            save_memory(text)
            return jsonify({"reply":"Entendido. Lo guardaré en mi memoria."})

    if "qué recuerdas" in low or "que recuerdas" in low:
        mem=get_memory()
        if not mem:
            return jsonify({"reply":"Todavía no tengo recuerdos guardados."})
        return jsonify({
            "reply":"Esto es lo que recuerdo:\n\n"+
            "\n".join("• "+x for x in mem)
        })

    # DETECTAR BÚSQUEDA
    search_words=[
        "busca ",
        "buscar ",
        "búscame ",
        "investiga ",
        "investigar ",
        "noticias",
        "qué pasó hoy",
        "que paso hoy",
        "últimas noticias",
        "ultimas noticias",
        "en internet",
        "en la web",
        "actualmente",
        "ahora mismo",
        "precio actual"
    ]

    use_web=any(x in low for x in search_words)
    web=[]

    if use_web:
        web=search_web(message)

    mem=get_memory()

    memory_text="\n".join(
        "• "+x for x in mem
    ) if mem else "No hay recuerdos todavía."

    web_text=""

    if web:
        web_text="\n\nRESULTADOS ENCONTRADOS EN INTERNET:\n"
        for x in web:
            web_text+=f"- {x['title']} | {x['url']}\n"

    system=f"""
Eres J.A.R.V.I.S., un asistente personal avanzado.

Tu personalidad:
- Inteligente.
- Natural.
- Educado.
- Directo.
- Útil.
- Hablas español salvo que el usuario pida otro idioma.

No inventes datos.

MEMORIA DEL USUARIO:
{memory_text}

{web_text}

Si existen resultados de internet, utilízalos para responder.
Indica cuando una información procede de una búsqueda web.

Tu objetivo es ayudar al usuario y ejecutar tareas cuando las herramientas disponibles lo permitan.
"""

    try:
        result=ai.responses.create(
            model="openrouter/free",
            input=system+"\n\nUSUARIO:\n"+message
        )

        answer=getattr(result,"output_text",None)

        if not answer:
            answer=str(result)

    except Exception as e:
        answer="Mi conexión con el cerebro tuvo un problema: "+str(e)

    return jsonify({
        "reply":answer,
        "web":web
    })

# ================= INTERFAZ =================

@app.route("/")
def home():
    return Response(r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">

<meta name="theme-color" content="#0a0e17">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">

<link rel="manifest" href="/manifest.json">
<link rel="icon" href="/icon.svg">

<title>J.A.R.V.I.S.</title>

<style>

*{
 box-sizing:border-box;
 -webkit-tap-highlight-color:transparent;
}

html,body{
 margin:0;
 width:100%;
 height:100%;
 overflow:hidden;
 background:#0a0e17;
 color:#c9fbff;
 font-family:Arial,Helvetica,sans-serif;
}

body{
 display:flex;
 justify-content:center;
 align-items:center;
}

.hud{
 position:relative;
 width:100%;
 max-width:600px;
 height:100vh;
 overflow:hidden;
 background:
 radial-gradient(circle at center,
 #092a38 0%,
 #071923 22%,
 #0a0e17 55%,
 #03060b 100%);
 display:flex;
 justify-content:center;
 align-items:center;
}

/* PARTÍCULAS */

.particle{
 position:absolute;
 width:2px;
 height:2px;
 background:#22d3ee;
 border-radius:50%;
 box-shadow:0 0 8px #22d3ee;
 opacity:.6;
 animation:float 6s infinite ease-in-out;
}

.p1{left:12%;top:20%;animation-delay:0s}
.p2{left:82%;top:17%;animation-delay:1s}
.p3{left:20%;top:73%;animation-delay:2s}
.p4{left:76%;top:70%;animation-delay:3s}
.p5{left:50%;top:10%;animation-delay:1.5s}
.p6{left:8%;top:48%;animation-delay:2.5s}
.p7{left:91%;top:45%;animation-delay:4s}
.p8{left:37%;top:87%;animation-delay:3.5s}
.p9{left:66%;top:88%;animation-delay:4.5s}
.p10{left:30%;top:35%;animation-delay:5s}

@keyframes float{
 0%,100%{transform:translateY(0);opacity:.25}
 50%{transform:translateY(-25px);opacity:1}
}

/* ANILLOS */

.ring{
 position:absolute;
 border-radius:50%;
 border:1px solid #22d3ee;
 box-shadow:
 0 0 15px #22d3ee55,
 inset 0 0 15px #22d3ee22;
 pointer-events:none;
}

.ring1{
 width:360px;
 height:360px;
 border-top-color:transparent;
 border-bottom-color:#22d3ee;
 animation:spin1 13s linear infinite;
}

.ring2{
 width:310px;
 height:310px;
 border-style:dashed;
 border-color:#22d3ee88;
 animation:spin2 9s linear infinite;
}

.ring3{
 width:440px;
 height:440px;
 border-color:#22d3ee44;
 border-left-color:#22d3ee;
 animation:spin1 22s linear infinite;
}

.ring4{
 width:245px;
 height:245px;
 border-width:2px;
 border-right-color:transparent;
 animation:spin2 6s linear infinite;
}

.ring5{
 width:190px;
 height:190px;
 border-color:#22d3ee55;
 animation:spin1 4s linear infinite;
}

@keyframes spin1{
 from{transform:rotate(0deg)}
 to{transform:rotate(360deg)}
}

@keyframes spin2{
 from{transform:rotate(360deg)}
 to{transform:rotate(0deg)}
}

/* NÚCLEO */

.core{
 position:absolute;
 width:125px;
 height:125px;
 border-radius:50%;
 background:
 radial-gradient(circle,#153d4b 0%,#071923 55%,#02070b 100%);
 border:3px solid #22d3ee;
 box-shadow:
 0 0 20px #22d3ee,
 0 0 50px #22d3ee77,
 inset 0 0 30px #22d3ee55;
 display:flex;
 align-items:center;
 justify-content:center;
 z-index:5;
 animation:corePulse 2s ease-in-out infinite;
}

.core:before{
 content:"";
 position:absolute;
 width:80px;
 height:80px;
 border-radius:50%;
 border:1px solid #8ef5ff;
 box-shadow:0 0 20px #22d3ee;
}

.core:after{
 content:"";
 position:absolute;
 width:15px;
 height:15px;
 border-radius:50%;
 background:#d9fcff;
 box-shadow:0 0 25px #22d3ee,0 0 50px #22d3ee;
}

.logo{
 position:relative;
 z-index:2;
 font-size:34px;
 font-weight:bold;
 color:#d9fcff;
 text-shadow:0 0 15px #22d3ee;
}

@keyframes corePulse{
 0%,100%{
  transform:scale(.94);
  box-shadow:0 0 20px #22d3ee,0 0 50px #22d3ee55;
 }
 50%{
  transform:scale(1.05);
  box-shadow:0 0 30px #22d3ee,0 0 90px #22d3ee88;
 }
}

/* ONDAS RADAR */

.wave{
 position:absolute;
 width:125px;
 height:125px;
 border:2px solid #22d3ee;
 border-radius:50%;
 opacity:0;
 animation:wave 3s infinite;
}

.wave2{animation-delay:1s}
.wave3{animation-delay:2s}

@keyframes wave{
 0%{
  transform:scale(1);
  opacity:.7;
 }
 100%{
  transform:scale(3.4);
  opacity:0;
 }
}

/* LÍNEAS RADAR */

.tick{
 position:absolute;
 width:2px;
 height:16px;
 background:#22d3ee;
 box-shadow:0 0 8px #22d3ee;
 opacity:.65;
}

.t1{top:12%;left:50%}
.t2{top:50%;left:8%;transform:rotate(90deg)}
.t3{top:50%;right:8%;transform:rotate(90deg)}
.t4{bottom:12%;left:50%}
.t5{top:25%;left:22%;transform:rotate(-45deg)}
.t6{top:25%;right:22%;transform:rotate(45deg)}
.t7{bottom:25%;left:22%;transform:rotate(45deg)}
.t8{bottom:25%;right:22%;transform:rotate(-45deg)}

/* TEXTO */

.status{
 position:absolute;
 bottom:135px;
 width:100%;
 text-align:center;
 color:#22d3ee;
 font-size:13px;
 letter-spacing:4px;
 text-shadow:0 0 12px #22d3ee;
 z-index:8;
}

.substatus{
 position:absolute;
 top:35px;
 width:100%;
 text-align:center;
 font-size:11px;
 letter-spacing:3px;
 color:#7bdce8;
 opacity:.7;
}

/* ECUALIZADOR */

.equalizer{
 position:absolute;
 bottom:175px;
 display:flex;
 gap:5px;
 align-items:end;
 height:40px;
 z-index:8;
}

.equalizer span{
 width:4px;
 height:7px;
 background:#22d3ee;
 box-shadow:0 0 9px #22d3ee;
 border-radius:3px;
}

/* MIC */

.mic{
 position:absolute;
 bottom:35px;
 width:76px;
 height:76px;
 border-radius:50%;
 border:2px solid #22d3ee;
 background:#06131c;
 color:#cfffff;
 font-size:31px;
 box-shadow:
 0 0 15px #22d3ee88,
 inset 0 0 15px #22d3ee33;
 z-index:20;
 transition:.2s;
}

.mic:active{
 transform:scale(.9);
 box-shadow:
 0 0 35px #22d3ee,
 inset 0 0 25px #22d3ee66;
}

/* PANEL DE RESPUESTA */

.response{
 position:absolute;
 top:62px;
 left:20px;
 right:20px;
 max-height:115px;
 overflow:auto;
 color:#a9f4ff;
 font-size:12px;
 line-height:1.45;
 text-shadow:0 0 8px #22d3ee55;
 z-index:10;
 scrollbar-width:none;
}

.response::-webkit-scrollbar{
 display:none;
}

/* ESCUCHANDO */

.listening .ring1{
 animation-duration:4s;
}

.listening .ring2{
 animation-duration:2.5s;
}

.listening .ring3{
 animation-duration:7s;
}

.listening .ring4{
 animation-duration:2s;
}

.listening .wave{
 animation-duration:1.4s;
}

.listening .mic{
 box-shadow:
 0 0 30px #22d3ee,
 0 0 70px #22d3ee88,
 inset 0 0 25px #22d3ee66;
}

.listening .status{
 color:#d9ffff;
}

</style>
</head>

<body>

<div class="hud" id="hud">

<div class="particle p1"></div>
<div class="particle p2"></div>
<div class="particle p3"></div>
<div class="particle p4"></div>
<div class="particle p5"></div>
<div class="particle p6"></div>
<div class="particle p7"></div>
<div class="particle p8"></div>
<div class="particle p9"></div>
<div class="particle p10"></div>

<div class="substatus">J.A.R.V.I.S. // ONLINE</div>

<div class="response" id="response"></div>

<div class="ring ring1"></div>
<div class="ring ring2"></div>
<div class="ring ring3"></div>
<div class="ring ring4"></div>
<div class="ring ring5"></div>

<div class="tick t1"></div>
<div class="tick t2"></div>
<div class="tick t3"></div>
<div class="tick t4"></div>
<div class="tick t5"></div>
<div class="tick t6"></div>
<div class="tick t7"></div>
<div class="tick t8"></div>

<div class="wave"></div>
<div class="wave wave2"></div>
<div class="wave wave3"></div>

<div class="core">
 <div class="logo">J</div>
</div>

<div class="equalizer" id="eq">
 <span></span><span></span><span></span><span></span>
 <span></span><span></span><span></span><span></span>
 <span></span><span></span><span></span><span></span>
 <span></span><span></span><span></span><span></span>
</div>

<div class="status" id="status">
AWAITING COMMAND...
</div>

<button class="mic" id="mic">🎙</button>

</div>

<script>

const hud=document.getElementById("hud");
const mic=document.getElementById("mic");
const status=document.getElementById("status");
const response=document.getElementById("response");
const bars=[...document.querySelectorAll(".equalizer span")];

let recognition=null;
let speaking=false;

/* ECUALIZADOR */

setInterval(()=>{
 bars.forEach(b=>{
  const max=hud.classList.contains("listening")?38:15;
  b.style.height=(5+Math.random()*max)+"px";
 });
},110);

/* VOZ */

function speak(text){

 if(!("speechSynthesis" in window)) return;

 speechSynthesis.cancel();

 const u=new SpeechSynthesisUtterance(text);
 u.lang="es-PA";
 u.rate=.95;
 u.pitch=1;

 const voices=speechSynthesis.getVoices();

 const spanish=voices.find(v=>
  v.lang &&
  v.lang.toLowerCase().startsWith("es")
 );

 if(spanish) u.voice=spanish;

 u.onstart=()=>{
  speaking=true;
 };

 u.onend=()=>{
  speaking=false;
 };

 speechSynthesis.speak(u);
}

/* COMUNICACIÓN */

async function ask(message){

 status.textContent="PROCESSING...";

 response.innerHTML=
 "<div>USER: "+escapeHtml(message)+"</div>";

 try{

  const r=await fetch("/chat",{
   method:"POST",
   headers:{
    "Content-Type":"application/json"
   },
   body:JSON.stringify({
    message:message
   })
  });

  const data=await r.json();

  response.innerHTML=
   "<div>USER: "+escapeHtml(message)+"</div>"+
   "<div style='margin-top:7px'>JARVIS: "+
   escapeHtml(data.reply)+"</div>";

  response.scrollTop=response.scrollHeight;

  speak(data.reply);

 }catch(error){

  response.innerHTML+="<div>JARVIS: Error de conexión.</div>";

 }

 status.textContent="AWAITING COMMAND...";
}

function escapeHtml(text){

 return String(text)
 .replaceAll("&","&amp;")
 .replaceAll("<","&lt;")
 .replaceAll(">","&gt;")
 .replaceAll('"',"&quot;");

}

/* RECONOCIMIENTO */

const SpeechRecognition=
 window.SpeechRecognition ||
 window.webkitSpeechRecognition;

if(SpeechRecognition){

 recognition=new SpeechRecognition();

 recognition.lang="es-PA";
 recognition.continuous=false;
 recognition.interimResults=false;

 recognition.onstart=()=>{

  hud.classList.add("listening");
  status.textContent="LISTENING...";

 };

 recognition.onresult=(event)=>{

  const text=
   event.results[0][0].transcript;

  ask(text);

 };

 recognition.onerror=()=>{

  hud.classList.remove("listening");
  status.textContent="AWAITING COMMAND...";

 };

 recognition.onend=()=>{

  hud.classList.remove("listening");

  if(!speaking){
   status.textContent="AWAITING COMMAND...";
  }

 };

}else{

 status.textContent="MICROPHONE UNAVAILABLE";

}

/* BOTÓN */

mic.onclick=()=>{

 if(recognition){

  try{
   recognition.start();
  }catch(e){}

 }else{

  const text=prompt("Escribe tu comando:");

  if(text) ask(text);

 }

};

/* PWA */

if("serviceWorker" in navigator){

 navigator.serviceWorker.register(
  "/service-worker.js"
 ).catch(()=>{});

}

</script>

</body>
</html>''',mimetype="text/html")

# ================= ARRANQUE =================

if __name__=="__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT",8000))
        )
