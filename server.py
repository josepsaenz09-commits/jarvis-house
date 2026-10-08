import os,json,sqlite3,urllib.parse,urllib.request,re
from flask import Flask,request,jsonify,Response
from openai import OpenAI

app=Flask(__name__)
DB="jarvis_memory.db"

client=OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def db():
    c=sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY AUTOINCREMENT,text TEXT)")
    c.commit()
    return c

def remember(text):
    c=db()
    c.execute("INSERT INTO memory(text) VALUES(?)",(text,))
    c.commit()
    c.close()

def memories():
    c=db()
    rows=c.execute("SELECT text FROM memory ORDER BY id DESC LIMIT 30").fetchall()
    c.close()
    return [x[0] for x in rows]

def web_search(q):
    try:
        url="https://html.duckduckgo.com/html/?q="+urllib.parse.quote(q)
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        html=urllib.request.urlopen(req,timeout=10).read().decode("utf-8","ignore")
        items=[]
        for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',html,re.S):
            link=m.group(1)
            title=re.sub("<.*?>","",m.group(2)).strip()
            title=title.replace("&amp;","&")
            if title and link:
                items.append({"title":title,"url":link})
            if len(items)>=5: break
        return items
    except Exception as e:
        return [{"title":"No se pudo realizar la búsqueda","url":""}]

@app.route("/manifest.json")
def manifest():
    return Response(json.dumps({
        "name":"J.A.R.V.I.S.",
        "short_name":"JARVIS",
        "start_url":"/",
        "scope":"/",
        "display":"standalone",
        "background_color":"#05080e",
        "theme_color":"#00eaff",
        "orientation":"portrait",
        "icons":[{"src":"/icon.svg","sizes":"any","type":"image/svg+xml","purpose":"any maskable"}]
    }),mimetype="application/manifest+json")

@app.route("/icon.svg")
def icon():
    return Response("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="96" fill="#05080e"/>
<circle cx="256" cy="256" r="205" fill="none" stroke="#00eaff" stroke-width="7"/>
<circle cx="256" cy="256" r="170" fill="none" stroke="#00eaff" stroke-width="2" opacity=".55"/>
<path d="M256 92L420 256L256 420L92 256Z" fill="none" stroke="#00eaff" stroke-width="8"/>
<circle cx="256" cy="256" r="82" fill="#062431" stroke="#8feeff" stroke-width="6"/>
<text x="256" y="282" text-anchor="middle" font-family="Arial" font-size="82" font-weight="700" fill="#d6fbff">J</text>
</svg>""",mimetype="image/svg+xml")

@app.route("/service-worker.js")
def sw():
    return Response("""const C="jarvis-pwa-v1";
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(["/","/manifest.json","/icon.svg"])));self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(self.clients.claim())});
self.addEventListener("fetch",e=>{if(e.request.method==="GET")e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)))});
""",mimetype="application/javascript")

@app.route("/chat",methods=["POST"])
def chat():
    data=request.get_json(force=True)
    msg=str(data.get("message","")).strip()
    if not msg:
        return jsonify({"reply":"Te escucho."})

    low=msg.lower()

    if low.startswith(("recuerda ","recuerda que ","guarda ","guarda que ")):
        remember(re.sub(r"^(recuerda|recuerda que|guarda|guarda que)\s*","",msg,flags=re.I))
        return jsonify({"reply":"Entendido. Lo he guardado en mi memoria."})

    if "qué recuerdas" in low or "que recuerdas" in low:
        mem=memories()
        return jsonify({"reply":"Esto es lo que recuerdo:\n\n"+("\n".join("• "+x for x in mem) if mem else "Todavía no tengo recuerdos guardados.")})

    need_search=any(x in low for x in [
        "busca ","buscar ","búscame ","investiga ","investigar ",
        "qué pasó hoy","que paso hoy","últimas noticias","ultimas noticias",
        "noticias de hoy","en internet","en la web","precio actual",
        "hoy ","ahora mismo","actualmente"
    ])

    results=[]
    if need_search:
        results=web_search(msg)

    mem="\n".join("- "+x for x in memories())
    context=""
    if results:
        context="\nRESULTADOS DE INTERNET:\n"+json.dumps(results,ensure_ascii=False)
    prompt=f"""Eres J.A.R.V.I.S., un asistente personal inteligente.
Responde en español, de forma natural, clara y útil.
No inventes información.
Si se proporcionaron resultados de internet, úsalos y deja claro que son resultados encontrados en la web.
Memoria del usuario:
{mem or "Sin memoria todavía."}
{context}
"""

    try:
        r=client.responses.create(
            model="openrouter/free",
            input=prompt+"\nUsuario: "+msg
        )
        reply=getattr(r,"output_text",None)
        if not reply:
            reply=str(r)
    except Exception as e:
        reply="He tenido un problema al conectar con mi cerebro: "+str(e)

    return jsonify({"reply":reply,"web":results})

@app.route("/")
def home():
    return Response("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#05080e">
<link rel="manifest" href="/manifest.json">
<link rel="icon" href="/icon.svg">
<title>J.A.R.V.I.S.</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#0a0e17;color:#bffaff;font-family:Arial,sans-serif}
body{display:flex;align-items:center;justify-content:center}
.hud{position:relative;width:min(100vw,520px);height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden;background:radial-gradient(circle,#062431 0,#0a0e17 48%,#03060b 100%)}
.ring{position:absolute;border:1px solid #22d3ee;border-radius:50%;box-shadow:0 0 15px #22d3ee55,inset 0 0 15px #22d3ee22}
.r1{width:330px;height:330px;animation:spin 13s linear infinite}
.r2{width:270px;height:270px;border-style:dashed;animation:spin 8s linear infinite reverse}
.r3{width:410px;height:410px;border-color:#22d3ee55;animation:spin 22s linear infinite}
.r4{width:190px;height:190px;border-width:2px;animation:pulse 2s ease-in-out infinite}
.center{position:relative;width:120px;height:120px;border-radius:50%;border:3px solid #22d3ee;background:#07151f;box-shadow:0 0 25px #22d3ee,0 0 70px #22d3ee55;display:flex;align-items:center;justify-content:center;font-size:50px;z-index:4;animation:pulse 2s ease-in-out infinite}
.mic{position:absolute;bottom:24px;width:74px;height:74px;border-radius:50%;border:2px solid #22d3ee;background:#07151f;color:#bffaff;font-size:32px;box-shadow:0 0 22px #22d3ee88;z-index:10}
.status{position:absolute;bottom:108px;text-align:center;font-size:13px;letter-spacing:4px;color:#22d3ee;text-shadow:0 0 10px #22d3ee}
.eq{position:absolute;bottom:150px;display:flex;gap:4px;height:35px;align-items:end}
.eq i{display:block;width:4px;background:#22d3ee;box-shadow:0 0 8px #22d3ee;height:8px}
.log{position:absolute;top:25px;left:18px;right:18px;max-height:105px;overflow:hidden;font-size:12px;color:#8deffc;opacity:.75}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{transform:scale(.96);opacity:.85}50%{transform:scale(1.04);opacity:1}}
.listening .r1{animation-duration:4s}
.listening .r2{animation-duration:2.5s}
.listening .r3{animation-duration:7s}
.listening .r4{animation-duration:.8s}
</style>
</head>
<body>
<div class="hud" id="hud">
<div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div><div class="ring r4"></div>
<div class="center">J</div>
<div class="eq" id="eq"></div>
<div class="status" id="status">AWAITING COMMAND...</div>
<button class="mic" id="mic">🎙</button>
<div class="log" id="log"></div>
</div>

<script>
const hud=document.getElementById("hud"),mic=document.getElementById("mic"),status=document.getElementById("status"),log=document.getElementById("log"),eq=document.getElementById("eq");

for(let i=0;i<18;i++){let x=document.createElement("i");eq.appendChild(x)}

function equalizer(){
 [...eq.children].forEach(x=>x.style.height=(hud.classList.contains("listening")?(8+Math.random()*28):(4+Math.random()*10))+"px");
}
setInterval(equalizer,120);

function say(t){
 if(!("speechSynthesis" in window))return;
 speechSynthesis.cancel();
 let u=new SpeechSynthesisUtterance(t);
 u.lang="es-PA";u.rate=.95;u.pitch=1;
 let vs=speechSynthesis.getVoices();
 let v=vs.find(x=>x.lang&&x.lang.toLowerCase().startsWith("es"));
 if(v)u.voice=v;
 speechSynthesis.speak(u);
}

async function ask(t){
 log.innerHTML+="<div>USER: "+t+"</div>";
 status.textContent="THINKING...";
 try{
  let r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:t})});
  let d=await r.json();
  log.innerHTML+="<div>JARVIS: "+d.reply+"</div>";
  say(d.reply);
 }catch(e){log.innerHTML+="<div>ERROR DE CONEXIÓN</div>"}
 status.textContent="AWAITING COMMAND...";
}

let rec=null;
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;

if(SR){
 rec=new SR();
 rec.lang="es-PA";
 rec.continuous=false;
 rec.interimResults=false;
 rec.onstart=()=>{hud.classList.add("listening");status.textContent="LISTENING..."}
 rec.onend=()=>{hud.classList.remove("listening");if(status.textContent==="LISTENING...")status.textContent="AWAITING COMMAND..."}
 rec.onresult=e=>{let t=e.results[0][0].transcript;ask(t)}
}else{
 status.textContent="MICROPHONE NO DISPONIBLE";
}

mic.onclick=()=>{
 if(rec){
  try{rec.start()}catch(e){}
 }else{
  let t=prompt("Escribe tu comando para JARVIS:");
  if(t)ask(t);
 }
};

if("serviceWorker" in navigator)navigator.serviceWorker.register("/service-worker.js");
</script>
</body>
</html>""",mimetype="text/html")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",8000)))
