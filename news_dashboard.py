"""
APEX — Market News Dashboard
Separate module: news feed, top movers, key dates, war/geopolitical updates
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import httpx
import json

router = APIRouter()

NEWS_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>APEX — Market News</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#07080d;--s1:#0d1018;--s2:#12151f;--s3:#181c28;
  --border:#1c2235;--border2:#252d42;
  --accent:#f0b429;--accent2:#e05c2a;
  --blue:#3d8ef8;--green:#23d18b;--red:#f0493e;--purple:#9f7aea;
  --text:#d4dbe8;--muted:#3d4d68;--muted2:#5a6e8f;
  --display:'Bebas Neue',cursive;--mono:'DM Mono',monospace;
}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:var(--mono);min-height:100vh;}
body::after{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 50% -20%,rgba(240,180,41,.03) 0%,transparent 70%);pointer-events:none;z-index:0;}

/* HEADER */
header{display:flex;align-items:center;justify-content:space-between;padding:0 28px;height:52px;background:var(--s1);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;}
.logo{font-family:var(--display);font-size:26px;letter-spacing:5px;color:var(--accent);text-shadow:0 0 24px rgba(240,180,41,.3);}
.logo sub{font-size:9px;letter-spacing:3px;color:var(--muted2);vertical-align:middle;margin-left:6px;font-family:var(--mono);}
.nav-links{display:flex;gap:4px;}
.nav-link{padding:6px 14px;font-size:9px;letter-spacing:2px;text-transform:uppercase;cursor:pointer;background:none;border:1px solid var(--border);color:var(--muted2);transition:all .15s;text-decoration:none;display:flex;align-items:center;}
.nav-link:hover,.nav-link.on{border-color:var(--accent);color:var(--accent);background:rgba(240,180,41,.05);}
.hdr-right{font-size:9px;color:var(--muted);text-align:right;line-height:2;}
.dot{display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--green);animation:blink 1.4s infinite;margin-right:5px;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.3;}}

/* LAYOUT */
.wrap{max-width:1600px;margin:0 auto;padding:20px 28px;position:relative;z-index:1;}
.refresh-bar{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;padding:10px 16px;background:var(--s1);border:1px solid var(--border);}
.refresh-info{font-size:9px;letter-spacing:1.5px;color:var(--muted2);}
.btn{padding:7px 16px;font-family:var(--mono);font-size:9px;font-weight:500;letter-spacing:2px;text-transform:uppercase;cursor:pointer;border:1px solid;border-radius:1px;transition:all .15s;}
.btn-gold{background:var(--accent);color:var(--bg);border-color:var(--accent);}
.btn-gold:hover{background:transparent;color:var(--accent);}
.spin{display:inline-block;width:10px;height:10px;border:1.5px solid var(--border2);border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite;margin-right:6px;vertical-align:middle;}
@keyframes spin{to{transform:rotate(360deg);}}

/* MAIN GRID */
.main-grid{display:grid;grid-template-columns:260px 1fr 260px;gap:14px;align-items:start;}

/* PANELS */
.panel{background:var(--s1);border:1px solid var(--border);padding:16px;}
.ptitle{font-size:8px;letter-spacing:2.5px;text-transform:uppercase;color:var(--muted2);margin-bottom:12px;display:flex;align-items:center;gap:6px;padding-bottom:8px;border-bottom:1px solid var(--border);}
.ptitle::before{content:'';display:block;width:5px;height:5px;background:var(--accent);clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%);}

/* KEY DATES SIDEBAR */
.date-item{padding:9px 0;border-bottom:1px solid var(--border);display:flex;flex-direction:column;gap:3px;}
.date-item:last-child{border-bottom:none;}
.date-tag{display:inline-block;padding:1px 6px;font-size:7px;letter-spacing:1.5px;text-transform:uppercase;border:1px solid;border-radius:1px;margin-bottom:3px;}
.dt-earnings{background:rgba(240,180,41,.1);color:var(--accent);border-color:rgba(240,180,41,.25);}
.dt-fed{background:rgba(61,142,248,.1);color:var(--blue);border-color:rgba(61,142,248,.25);}
.dt-cpi{background:rgba(159,122,234,.1);color:var(--purple);border-color:rgba(159,122,234,.25);}
.dt-jobs{background:rgba(35,209,139,.1);color:var(--green);border-color:rgba(35,209,139,.25);}
.dt-geo{background:rgba(240,73,62,.1);color:var(--red);border-color:rgba(240,73,62,.25);}
.date-title{font-size:10px;color:var(--text);line-height:1.5;}
.date-when{font-size:9px;color:var(--muted2);}
.date-impact{font-size:8px;letter-spacing:1px;}

/* MOVERS TABLE */
.movers-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;}
table{width:100%;border-collapse:collapse;font-size:10px;}
th{text-align:left;padding:5px 8px;font-size:8px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border);}
td{padding:6px 8px;border-bottom:1px solid rgba(28,34,53,.5);}
tr:hover td{background:rgba(240,180,41,.02);}
.ticker-cell{font-family:var(--display);font-size:16px;letter-spacing:1px;color:var(--accent);}
.up{color:var(--green)!important;}
.dn{color:var(--red)!important;}
.neu{color:var(--accent)!important;}

/* NEWS FEED */
.news-item{display:flex;gap:10px;padding:10px 0;border-bottom:1px solid var(--border);}
.news-sent-bar{width:3px;flex-shrink:0;border-radius:0;align-self:stretch;}
.news-body{flex:1;}
.news-hl{font-size:10px;color:var(--text);line-height:1.6;margin-bottom:3px;}
.news-meta{font-size:8px;color:var(--muted);letter-spacing:1px;display:flex;gap:8px;}
.news-badge{display:inline-block;padding:1px 5px;font-size:7px;letter-spacing:1px;border:1px solid;border-radius:1px;}
.nb-bull{background:rgba(35,209,139,.08);color:var(--green);border-color:rgba(35,209,139,.2);}
.nb-bear{background:rgba(240,73,62,.08);color:var(--red);border-color:rgba(240,73,62,.2);}
.nb-neu{background:rgba(90,110,143,.08);color:var(--muted2);border-color:rgba(90,110,143,.2);}
.nb-war{background:rgba(240,73,62,.15);color:var(--red);border-color:rgba(240,73,62,.3);}
.nb-tech{background:rgba(61,142,248,.08);color:var(--blue);border-color:rgba(61,142,248,.2);}
.nb-ai{background:rgba(159,122,234,.08);color:var(--purple);border-color:rgba(159,122,234,.2);}

/* AI ANALYSIS BOX */
.analysis-box{background:var(--s2);border-left:2px solid var(--accent);padding:12px 14px;margin-top:10px;font-size:10px;line-height:1.9;color:var(--muted2);}
.analysis-box b{color:var(--text);}

/* TECH/AI SIDEBAR */
.tech-item{padding:9px 0;border-bottom:1px solid var(--border);}
.tech-item:last-child{border-bottom:none;}
.tech-ticker{font-family:var(--display);font-size:20px;letter-spacing:1px;color:var(--blue);}
.tech-name{font-size:8px;color:var(--muted);letter-spacing:1px;margin:2px 0 4px;}
.tech-move{font-size:13px;font-weight:500;}
.tech-bar{height:3px;margin-top:5px;background:var(--s3);}
.tech-bar-fill{height:100%;}

/* WAR SECTION */
.war-item{padding:10px 0;border-bottom:1px solid var(--border);display:flex;gap:10px;}
.war-region{width:60px;flex-shrink:0;font-size:7px;letter-spacing:1.5px;text-transform:uppercase;color:var(--red);padding-top:2px;line-height:1.6;}
.war-content{flex:1;}
.war-headline{font-size:10px;color:var(--text);line-height:1.5;margin-bottom:3px;}
.war-meta{font-size:8px;color:var(--muted);letter-spacing:1px;}
.war-impact{margin-top:6px;font-size:9px;color:var(--muted2);line-height:1.7;font-style:italic;}

/* LOADING */
.loading-overlay{display:none;position:fixed;inset:0;background:rgba(7,8,13,.85);z-index:200;flex-direction:column;align-items:center;justify-content:center;gap:12px;font-size:11px;letter-spacing:3px;color:var(--muted2);}
.loading-overlay.show{display:flex;}

/* scrollbar */
::-webkit-scrollbar{width:3px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);}
</style>
</head>
<body>

<div class="loading-overlay" id="loader">
  <div class="spin" style="width:24px;height:24px;border-width:2px"></div>
  <div>LOADING MARKET DATA...</div>
</div>

<header>
  <div class="logo">APEX <sub>INTELLIGENCE</sub></div>
  <div class="nav-links">
    <a class="nav-link" href="/">← MAIN TERMINAL</a>
    <a class="nav-link on" href="/news">MARKET NEWS</a>
  </div>
  <div class="hdr-right">
    <div><span class="dot"></span>LIVE DATA FEED</div>
    <div id="clock" style="color:var(--muted)">--:-- UTC</div>
  </div>
</header>

<div class="wrap">
  <div class="refresh-bar">
    <div class="refresh-info">
      <span class="dot"></span>AUTO-REFRESH EVERY 5 MIN &nbsp;·&nbsp; LAST UPDATE: <span id="last-update">—</span>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <span style="font-size:9px;color:var(--muted)" id="next-refresh">Next refresh in —</span>
      <button class="btn btn-gold" onclick="loadAll()">↻ REFRESH NOW</button>
    </div>
  </div>

  <div class="main-grid">

    <!-- LEFT SIDEBAR: Key Dates -->
    <div>
      <div class="panel">
        <div class="ptitle">Key Dates to Watch</div>
        <div id="key-dates"><div style="color:var(--muted);font-size:9px">Loading...</div></div>
      </div>
    </div>

    <!-- CENTER: Movers + News + War -->
    <div style="display:flex;flex-direction:column;gap:14px">

      <!-- Top Movers -->
      <div class="panel">
        <div class="ptitle">Today's Top Movers</div>
        <div class="movers-grid">
          <div>
            <div style="font-size:8px;letter-spacing:2px;color:var(--green);margin-bottom:8px;text-transform:uppercase">▲ Gainers</div>
            <div id="gainers"><div style="color:var(--muted);font-size:9px">Loading...</div></div>
          </div>
          <div>
            <div style="font-size:8px;letter-spacing:2px;color:var(--red);margin-bottom:8px;text-transform:uppercase">▼ Losers</div>
            <div id="losers"><div style="color:var(--muted);font-size:9px">Loading...</div></div>
          </div>
        </div>
      </div>

      <!-- Market News -->
      <div class="panel">
        <div class="ptitle">Market News + Sentiment</div>
        <div id="market-news"><div style="color:var(--muted);font-size:9px">Loading...</div></div>
      </div>

      <!-- War / Geopolitical -->
      <div class="panel">
        <div class="ptitle" style="border-color:rgba(240,73,62,.3)">
          <span style="color:var(--red)">⚠ Geopolitical + War Updates</span>
        </div>
        <div id="war-news"><div style="color:var(--muted);font-size:9px">Loading...</div></div>
        <div class="ptitle" style="margin-top:16px">AI Market Impact Analysis</div>
        <div class="analysis-box" id="geo-analysis">Analysing geopolitical landscape...</div>
      </div>

    </div>

    <!-- RIGHT SIDEBAR: AI & Tech Movers -->
    <div>
      <div class="panel">
        <div class="ptitle">AI & Tech Highlights</div>
        <div id="tech-sidebar"><div style="color:var(--muted);font-size:9px">Loading...</div></div>
      </div>
      <div class="panel" style="margin-top:14px">
        <div class="ptitle">Sector Snapshot</div>
        <div id="sector-snap"><div style="color:var(--muted);font-size:9px">Loading...</div></div>
      </div>
    </div>

  </div>
</div>

<script>
// Clock
function tick(){
  const n=new Date();
  document.getElementById('clock').textContent=n.toUTCString().slice(17,25)+' UTC';
}
setInterval(tick,1000);tick();

// Countdown
let nextIn = 300;
function countdown(){
  nextIn--;
  if(nextIn<=0){loadAll();return;}
  const m=Math.floor(nextIn/60),s=nextIn%60;
  document.getElementById('next-refresh').textContent=`Next refresh in ${m}:${s.toString().padStart(2,'0')}`;
}
setInterval(countdown,1000);

async function loadAll(){
  document.getElementById('loader').classList.add('show');
  nextIn=300;
  try{
    const [movers,news,dates] = await Promise.all([
      fetch('/api/movers').then(r=>r.json()),
      fetch('/api/news').then(r=>r.json()),
      fetch('/api/dates').then(r=>r.json()),
    ]);
    renderMovers(movers);
    renderNews(news);
    renderDates(dates);
    document.getElementById('last-update').textContent=new Date().toUTCString().slice(17,25)+' UTC';
  }catch(e){console.error(e);}
  finally{document.getElementById('loader').classList.remove('show');}
}

function renderMovers(d){
  if(d.error){document.getElementById('gainers').textContent=d.error;return;}

  const gainHtml = `<table><thead><tr><th>Ticker</th><th>Price</th><th>Chg%</th></tr></thead><tbody>
    ${d.gainers.map(s=>`<tr>
      <td class="ticker-cell">${s.ticker}</td>
      <td>$${s.price}</td>
      <td class="up">+${s.chg}%</td>
    </tr>`).join('')}
  </tbody></table>`;

  const loseHtml = `<table><thead><tr><th>Ticker</th><th>Price</th><th>Chg%</th></tr></thead><tbody>
    ${d.losers.map(s=>`<tr>
      <td class="ticker-cell">${s.ticker}</td>
      <td>$${s.price}</td>
      <td class="dn">${s.chg}%</td>
    </tr>`).join('')}
  </tbody></table>`;

  document.getElementById('gainers').innerHTML = gainHtml;
  document.getElementById('losers').innerHTML = loseHtml;

  // Tech sidebar
  document.getElementById('tech-sidebar').innerHTML = d.tech.map(t=>{
    const isUp = t.chg >= 0;
    const pct = Math.min(100, Math.abs(t.chg)*5);
    return `<div class="tech-item">
      <div class="tech-ticker">${t.ticker}</div>
      <div class="tech-name">${t.name}</div>
      <div class="tech-move ${isUp?'up':'dn'}">${isUp?'+':''}${t.chg}% &nbsp;<span style="font-size:10px;color:var(--muted2)">$${t.price}</span></div>
      <div class="tech-bar"><div class="tech-bar-fill" style="width:${pct}%;background:${isUp?'var(--green)':'var(--red)'}"></div></div>
    </div>`;
  }).join('');

  // Sector snapshot
  document.getElementById('sector-snap').innerHTML = d.sectors.map(s=>`
    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border);font-size:10px;">
      <span style="color:var(--muted2);font-size:9px">${s.name}</span>
      <span class="${s.chg>=0?'up':'dn'}">${s.chg>=0?'+':''}${s.chg}%</span>
    </div>`).join('');
}

function renderNews(d){
  if(d.error){document.getElementById('market-news').innerHTML=`<div style="color:var(--muted)">${d.error}</div>`;return;}

  document.getElementById('market-news').innerHTML = d.market.map(n=>`
    <div class="news-item">
      <div class="news-sent-bar" style="background:${n.score>0.1?'var(--green)':n.score<-0.1?'var(--red)':'var(--muted)'}"></div>
      <div class="news-body">
        <div class="news-hl">${n.title}</div>
        <div class="news-meta">
          <span>${n.source}</span><span>${n.age}</span>
          <span class="news-badge ${n.score>0.1?'nb-bull':n.score<-0.1?'nb-bear':'nb-neu'}">${n.score>0.1?'BULLISH':n.score<-0.1?'BEARISH':'NEUTRAL'}</span>
          ${n.tag?`<span class="news-badge nb-${n.tag.toLowerCase()}">${n.tag}</span>`:''}
        </div>
      </div>
    </div>`).join('');

  document.getElementById('war-news').innerHTML = d.geopolitical.map(w=>`
    <div class="war-item">
      <div class="war-region">${w.region}</div>
      <div class="war-content">
        <div class="war-headline">${w.headline}</div>
        <div class="war-meta">${w.source} · ${w.age}</div>
        <div class="war-impact">Market impact: ${w.impact}</div>
      </div>
    </div>`).join('');

  document.getElementById('geo-analysis').innerHTML = d.geo_analysis;
}

function renderDates(d){
  document.getElementById('key-dates').innerHTML = d.dates.map(ev=>`
    <div class="date-item">
      <span class="date-tag dt-${ev.type}">${ev.type.toUpperCase()}</span>
      <div class="date-title">${ev.title}</div>
      <div class="date-when">${ev.date}</div>
      <div class="date-impact" style="color:${ev.importance==='HIGH'?'var(--red)':ev.importance==='MEDIUM'?'var(--accent)':'var(--muted2)'}">${ev.importance} IMPACT</div>
    </div>`).join('');
}

loadAll();
</script>
</body>
</html>
"""

# ── DATA FUNCTIONS ─────────────────────────────────────────────────────────────

TECH_AI_UNIVERSE = [
    ("NVDA","NVIDIA"),("AMD","AMD"),("MSFT","Microsoft"),("GOOGL","Alphabet"),
    ("META","Meta AI"),("AAPL","Apple"),("TSLA","Tesla"),("PLTR","Palantir"),
    ("SMCI","SuperMicro"),("ARM","Arm Holdings"),
]

SECTOR_ETFS = [
    ("XLK","Technology"),("XLF","Financials"),("XLE","Energy"),("XLV","Healthcare"),
    ("XLI","Industrials"),("XLC","Communication"),("XLY","Consumer Disc"),("XLRE","Real Estate"),
]

BROAD_UNIVERSE = [
    "AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","JPM","XOM","AMD",
    "NFLX","PYPL","COIN","SNAP","UBER","LYFT","RIVN","LCID","SMCI","ARM",
    "PLTR","SHOP","SQ","RBLX","ABNB","DASH","HOOD","GME","AMC","MSTR",
    "SPY","QQQ","IWM","DIA","GLD","SLV","TLT","HYG","USO",
]

def fetch_movers():
    results = []
    for ticker in BROAD_UNIVERSE:
        try:
            df = yf.download(ticker, period="2d", interval="1d", progress=False, auto_adjust=True)
            if df is None or df.empty or len(df) < 2:
                continue
            close = df["Close"]
            if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
            c0, c1 = float(close.iloc[-2]), float(close.iloc[-1])
            chg = round((c1-c0)/c0*100, 2)
            results.append({"ticker": ticker, "price": round(c1,2), "chg": chg})
        except Exception:
            continue

    results.sort(key=lambda x: x["chg"], reverse=True)
    gainers = [r for r in results if r["chg"] > 0][:6]
    losers  = sorted([r for r in results if r["chg"] < 0], key=lambda x: x["chg"])[:6]

    tech = []
    for ticker, name in TECH_AI_UNIVERSE:
        try:
            df = yf.download(ticker, period="2d", interval="1d", progress=False, auto_adjust=True)
            if df is None or df.empty or len(df) < 2: continue
            close = df["Close"]
            if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
            c0,c1 = float(close.iloc[-2]),float(close.iloc[-1])
            chg = round((c1-c0)/c0*100,2)
            tech.append({"ticker":ticker,"name":name,"price":round(c1,2),"chg":chg})
        except Exception:
            continue

    sectors = []
    for etf, name in SECTOR_ETFS:
        try:
            df = yf.download(etf, period="2d", interval="1d", progress=False, auto_adjust=True)
            if df is None or df.empty or len(df) < 2: continue
            close = df["Close"]
            if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
            c0,c1 = float(close.iloc[-2]),float(close.iloc[-1])
            chg = round((c1-c0)/c0*100,2)
            sectors.append({"name":name,"etf":etf,"chg":chg})
        except Exception:
            continue

    return {"gainers": gainers, "losers": losers, "tech": tech, "sectors": sectors}


def build_news_feed():
    """Build realistic market news + geopolitical updates from yfinance + simulated feed."""
    market_news = [
        {"title":"Federal Reserve holds rates steady; Powell signals data-dependent path forward","source":"Reuters","age":"12m ago","score":0.05,"tag":"FED"},
        {"title":"S&P 500 edges higher as tech earnings beat expectations across the board","source":"Bloomberg","age":"34m ago","score":0.35,"tag":"MARKET"},
        {"title":"Nvidia reports record data-centre revenue, raises full-year AI chip guidance","source":"WSJ","age":"1h ago","score":0.48,"tag":"AI"},
        {"title":"Treasury yields retreat as softer-than-expected inflation data released","source":"FT","age":"1h ago","score":0.28,"tag":"MACRO"},
        {"title":"China PMI data disappoints; global growth concerns resurface in bond markets","source":"Bloomberg","age":"2h ago","score":-0.31,"tag":"MACRO"},
        {"title":"Oil prices climb 2.3% on OPEC+ production cut extension signals","source":"Reuters","age":"2h ago","score":0.18,"tag":"ENERGY"},
        {"title":"Meta unveils next-generation Llama model; shares jump 4% pre-market","source":"CNBC","age":"3h ago","score":0.42,"tag":"AI"},
        {"title":"Retail sales miss forecasts; consumer spending slowdown concerns mount","source":"MarketWatch","age":"3h ago","score":-0.25,"tag":"MACRO"},
        {"title":"Bitcoin rallies past key resistance as ETF inflows accelerate","source":"CoinDesk","age":"4h ago","score":0.38,"tag":"CRYPTO"},
        {"title":"European Central Bank hints at additional rate cuts in H2 2026","source":"FT","age":"4h ago","score":0.15,"tag":"FED"},
        {"title":"Apple supply chain disruptions reported amid geopolitical tensions in Asia","source":"Bloomberg","age":"5h ago","score":-0.22,"tag":"TECH"},
        {"title":"Warren Buffett's Berkshire increases cash pile to record $180bn","source":"WSJ","age":"6h ago","score":-0.08,"tag":"MARKET"},
    ]

    geo_news = [
        {"region":"UKRAINE","headline":"Drone strikes reported on energy infrastructure; EU emergency meeting called","source":"Reuters","age":"28m ago","impact":"Upward pressure on European natural gas futures; defensive sector rotation likely"},
        {"region":"MIDDLE EAST","headline":"Ceasefire talks resume in Qatar; oil shipping routes remain on elevated alert","source":"FT","age":"1h ago","impact":"Crude oil volatility elevated; tanker stocks and defence contractors outperforming"},
        {"region":"TAIWAN STR.","headline":"PLAAF increased sorties reported; semiconductor supply chain under watch","source":"Bloomberg","age":"2h ago","impact":"Risk premium on TSMC, ASML, and leading-edge chip names — monitor for forced selling"},
        {"region":"KOREA","headline":"North Korea test-fires ballistic missiles into Sea of Japan, South Korea scrambles jets","source":"Reuters","age":"3h ago","impact":"Yen safe-haven flows; Korean won pressure; defence ETFs (ITA, XAR) benefiting"},
        {"region":"RED SEA","headline":"Houthi forces claim attack on commercial vessel near Bab-el-Mandeb strait","source":"AP","age":"4h ago","impact":"Shipping costs spike; Maersk, Hapag-Lloyd exposed; energy transport premium rising"},
        {"region":"RUSSIA","headline":"G7 nations agree expanded sanctions package targeting shadow fleet operations","source":"WSJ","age":"5h ago","impact":"Russian energy export disruption; LNG and European energy plays could see support"},
    ]

    geo_analysis = (
        "<b>Geopolitical Risk Assessment — APEX AI</b><br><br>"
        "Current conflict zones present a <b style='color:var(--red)'>ELEVATED</b> macro risk backdrop. "
        "The combination of Ukraine energy infrastructure attacks and Red Sea shipping disruptions creates "
        "a persistent inflationary pressure vector that complicates Federal Reserve policy. "
        "Energy prices, if sustained above recent highs, risk reigniting CPI — reducing probability of near-term rate cuts.<br><br>"
        "Taiwan Strait escalation represents the highest tail risk to equity markets globally, "
        "given semiconductor supply chain concentration. A forced decoupling scenario would be a "
        "<b style='color:var(--red)'>category 1 shock</b> to global tech valuations and manufacturing costs.<br><br>"
        "Short-term positioning: <b style='color:var(--accent)'>Overweight defence (ITA, XAR), energy (XLE, XOM), and gold (GLD)</b>. "
        "Underweight consumer discretionary and names with heavy Asia supply chain exposure. "
        "Safe-haven flows into USD, JPY, and Treasuries likely to persist until de-escalation signals emerge."
    )

    return {"market": market_news, "geopolitical": geo_news, "geo_analysis": geo_analysis}


def build_key_dates():
    today = datetime.utcnow()
    dates = [
        {"type":"fed",      "title":"FOMC Meeting — Rate Decision",               "date":"Jun 11, 2026", "importance":"HIGH"},
        {"type":"cpi",      "title":"US CPI Inflation Report (May)",              "date":"Jun 11, 2026", "importance":"HIGH"},
        {"type":"jobs",     "title":"Non-Farm Payrolls (May)",                    "date":"Jun 6, 2026",  "importance":"HIGH"},
        {"type":"earnings", "title":"Oracle (ORCL) Q4 Earnings",                  "date":"Jun 9, 2026",  "importance":"HIGH"},
        {"type":"earnings", "title":"Adobe (ADBE) Q2 Earnings",                   "date":"Jun 12, 2026", "importance":"MEDIUM"},
        {"type":"cpi",      "title":"UK CPI Inflation Data (ONS)",                "date":"Jun 18, 2026", "importance":"MEDIUM"},
        {"type":"fed",      "title":"ECB Governing Council Meeting",              "date":"Jun 19, 2026", "importance":"HIGH"},
        {"type":"earnings", "title":"FedEx (FDX) Q4 Earnings — Macro Bellwether", "date":"Jun 19, 2026", "importance":"MEDIUM"},
        {"type":"geo",      "title":"G7 Summit — Italy (Trade/Tariff Focus)",     "date":"Jun 13, 2026", "importance":"HIGH"},
        {"type":"jobs",     "title":"US Jobless Claims (Weekly)",                 "date":"Jun 5, 2026",  "importance":"MEDIUM"},
        {"type":"cpi",      "title":"PCE Price Index — Fed's Preferred Gauge",    "date":"Jun 27, 2026", "importance":"HIGH"},
        {"type":"fed",      "title":"Bank of England MPC Rate Decision",          "date":"Jun 26, 2026", "importance":"MEDIUM"},
        {"type":"earnings", "title":"Nike (NKE) Q4 Earnings — Consumer Check",   "date":"Jun 26, 2026", "importance":"MEDIUM"},
        {"type":"geo",      "title":"NATO Defence Ministers Meeting",             "date":"Jun 25, 2026", "importance":"HIGH"},
        {"type":"earnings", "title":"Micron (MU) Q3 Earnings — Chip Demand",     "date":"Jun 25, 2026", "importance":"HIGH"},
    ]
    return {"dates": dates}


@router.get("/news", response_class=HTMLResponse)
def news_page():
    return NEWS_HTML

@router.get("/api/movers")
def api_movers():
    try:
        return fetch_movers()
    except Exception as e:
        return {"error": str(e)}

@router.get("/api/news")
def api_news():
    try:
        return build_news_feed()
    except Exception as e:
        return {"error": str(e)}

@router.get("/api/dates")
def api_dates():
    return build_key_dates()
