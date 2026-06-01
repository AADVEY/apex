from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import random
from news_dashboard import router as news_router

app = FastAPI()
app.include_router(news_router)

# ── HTML ───────────────────────────────────────────────────────────────────────
HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>APEX — Market Intelligence</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8/hammer.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
<style>
:root {
  --bg:       #07080d;
  --s1:       #0d1018;
  --s2:       #12151f;
  --s3:       #181c28;
  --border:   #1c2235;
  --border2:  #252d42;
  --accent:   #f0b429;
  --accent2:  #e05c2a;
  --blue:     #3d8ef8;
  --green:    #23d18b;
  --red:      #f0493e;
  --text:     #d4dbe8;
  --muted:    #3d4d68;
  --muted2:   #5a6e8f;
  --display:  'Bebas Neue', cursive;
  --mono:     'DM Mono', monospace;
}
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{
  background:var(--bg);
  color:var(--text);
  font-family:var(--mono);
  min-height:100vh;
  overflow-x:hidden;
}
body::after{
  content:'';
  position:fixed;inset:0;
  background:radial-gradient(ellipse 80% 50% at 50% -20%, rgba(240,180,41,0.04) 0%, transparent 70%);
  pointer-events:none;z-index:0;
}
/* HEADER */
header{
  display:flex;align-items:center;justify-content:space-between;
  padding:0 32px;height:56px;
  background:var(--s1);
  border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:100;
}
.logo{
  font-family:var(--display);
  font-size:28px;letter-spacing:6px;
  color:var(--accent);
  text-shadow:0 0 30px rgba(240,180,41,0.35);
}
.logo sub{font-size:10px;letter-spacing:3px;color:var(--muted2);vertical-align:middle;margin-left:6px;font-family:var(--mono);}
.hdr-center{display:flex;gap:6px;align-items:center;}
.hdr-pill{
  padding:4px 10px;font-size:9px;letter-spacing:1.5px;
  background:var(--s2);border:1px solid var(--border);
  color:var(--muted2);border-radius:2px;
}
.hdr-right{font-size:10px;color:var(--muted);text-align:right;line-height:1.9;}
/* WORLD CLOCKS */
.world-clocks{display:flex;gap:2px;}
.wclock{
  padding:3px 8px;background:var(--s2);border:1px solid var(--border);
  display:flex;flex-direction:column;align-items:center;
  min-width:62px;
}
.wclock-label{font-size:7px;letter-spacing:1.5px;color:var(--muted);text-transform:uppercase;line-height:1.4;}
.wclock-time{font-size:11px;color:var(--text);letter-spacing:1px;font-family:var(--mono);}
.wclock-time.open{color:var(--green);}
.wclock-time.closed{color:var(--muted2);}
.live{display:inline-flex;align-items:center;gap:5px;color:var(--green);font-size:9px;letter-spacing:1.5px;}
.dot{width:5px;height:5px;border-radius:50%;background:var(--green);animation:blink 1.4s infinite;}
@keyframes blink{0%,100%{opacity:1;box-shadow:0 0 4px var(--green);}50%{opacity:0.4;box-shadow:none;}}
/* LAYOUT */
.wrap{max-width:1440px;margin:0 auto;padding:24px 32px;position:relative;z-index:1;}
/* SEARCH */
.search{
  display:flex;align-items:center;gap:10px;
  padding:0 16px;height:52px;
  background:var(--s1);border:1px solid var(--border2);
  margin-bottom:22px;
}
.search-prompt{color:var(--accent);font-size:13px;font-weight:500;}
.search input{
  background:none;border:none;outline:none;
  color:var(--accent);font-family:var(--display);
  font-size:22px;letter-spacing:4px;
  text-transform:uppercase;width:220px;
}
.search input::placeholder{color:var(--muted);}
.btn{
  padding:9px 20px;
  font-family:var(--mono);font-size:10px;font-weight:500;
  letter-spacing:2px;text-transform:uppercase;
  cursor:pointer;border:1px solid;border-radius:1px;
  transition:all .15s;white-space:nowrap;
}
.btn-gold{background:var(--accent);color:var(--bg);border-color:var(--accent);}
.btn-gold:hover{background:transparent;color:var(--accent);box-shadow:0 0 14px rgba(240,180,41,.25);}
.btn-ghost{background:transparent;color:var(--muted2);border-color:var(--border);}
.btn-ghost:hover{border-color:var(--accent);color:var(--accent);}
.btn-ghost.on{border-color:var(--accent);color:var(--accent);background:rgba(240,180,41,.06);}
.loading{display:none;align-items:center;gap:8px;color:var(--muted2);font-size:10px;letter-spacing:2px;}
.spin{width:14px;height:14px;border:2px solid var(--border2);border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
/* TABS */
.tabs{display:flex;gap:0;border-bottom:1px solid var(--border);margin-bottom:22px;}
.tab{
  padding:10px 22px;font-family:var(--mono);font-size:10px;
  letter-spacing:2px;text-transform:uppercase;
  cursor:pointer;background:none;border:none;
  color:var(--muted);border-bottom:2px solid transparent;
  margin-bottom:-1px;transition:all .15s;
}
.tab:hover{color:var(--text);}
.tab.on{color:var(--accent);border-bottom-color:var(--accent);}
/* STAT STRIP */
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:18px;}
.sc{
  background:var(--s1);border:1px solid var(--border);
  padding:14px 16px;position:relative;overflow:hidden;
  transition:border-color .2s;
}
.sc:hover{border-color:var(--border2);}
.sc::before{content:'';position:absolute;left:0;top:0;width:2px;height:100%;background:var(--accent);opacity:.5;}
.sc-label{font-size:8px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:7px;}
.sc-val{font-family:var(--display);font-size:24px;letter-spacing:1px;line-height:1;}
.sc-sub{font-size:9px;color:var(--muted2);margin-top:4px;}
.up{color:var(--green)!important;}
.dn{color:var(--red)!important;}
.neu{color:var(--accent)!important;}
/* PANELS */
.panels{display:grid;grid-template-columns:1fr 360px;gap:14px;margin-bottom:14px;}
.panels-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px;}
.panel{background:var(--s1);border:1px solid var(--border);padding:20px;}
.panel-sm{background:var(--s1);border:1px solid var(--border);padding:16px;}
.ptitle{
  font-size:9px;letter-spacing:2.5px;text-transform:uppercase;
  color:var(--muted2);margin-bottom:14px;
  display:flex;align-items:center;gap:7px;
}
.ptitle::before{content:'';display:block;width:6px;height:6px;background:var(--accent);clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%);}
/* CHART */
.chart-wrap{position:relative;height:360px;}
.empty{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;height:100%;
  color:var(--muted);font-size:10px;letter-spacing:2px;gap:10px;
}
.empty-big{font-family:var(--display);font-size:64px;color:var(--border2);}
/* TABLES */
table{width:100%;border-collapse:collapse;font-size:10px;}
th{
  text-align:left;padding:5px 8px;font-size:8px;
  letter-spacing:1.5px;text-transform:uppercase;
  color:var(--muted);border-bottom:1px solid var(--border);
}
td{padding:6px 8px;border-bottom:1px solid rgba(28,34,53,.6);font-family:var(--mono);}
tr:hover td{background:rgba(240,180,41,.02);}
/* BADGES */
.badge{display:inline-block;padding:2px 6px;font-size:8px;letter-spacing:1px;font-weight:500;border-radius:1px;}
.b-buy{background:rgba(35,209,139,.12);color:var(--green);border:1px solid rgba(35,209,139,.25);}
.b-sell{background:rgba(240,73,62,.1);color:var(--red);border:1px solid rgba(240,73,62,.25);}
.b-call{background:rgba(35,209,139,.1);color:var(--green);border:1px solid rgba(35,209,139,.2);}
.b-put{background:rgba(240,73,62,.1);color:var(--red);border:1px solid rgba(240,73,62,.2);}
.b-sweep{background:rgba(240,180,41,.1);color:var(--accent);border:1px solid rgba(240,180,41,.25);}
.b-block{background:rgba(61,142,248,.1);color:var(--blue);border:1px solid rgba(61,142,248,.25);}
.b-neutral{background:rgba(90,110,143,.1);color:var(--muted2);border:1px solid rgba(90,110,143,.2);}
/* INSIGHT */
.insight{
  background:var(--s2);border-left:2px solid var(--accent);
  padding:12px 14px;margin-top:12px;
  font-size:10px;line-height:1.9;color:var(--muted2);
}
/* SCENARIO */
.scen-row{display:flex;align-items:center;gap:8px;margin:7px 0;font-size:10px;}
.scen-lbl{width:44px;color:var(--muted);text-transform:uppercase;font-size:8px;letter-spacing:1px;}
.scen-bar{flex:1;height:7px;background:var(--s3);}
.scen-fill{height:100%;}
.scen-pct{width:52px;text-align:right;font-weight:500;}
/* RSI */
.rsi-track{height:7px;background:linear-gradient(90deg,var(--red) 0%,var(--accent) 30%,var(--green) 70%,var(--red) 100%);position:relative;margin:8px 0 4px;}
.rsi-pin{position:absolute;top:-3px;width:2px;height:13px;background:#fff;transform:translateX(-50%);}
/* DELTA BAR */
.delta-bar{height:7px;background:var(--s3);position:relative;overflow:visible;margin:6px 0;}
/* NEWS */
.news-item{padding:10px 0;border-bottom:1px solid var(--border);display:flex;gap:12px;align-items:flex-start;}
.news-sent{width:5px;flex-shrink:0;align-self:stretch;border-radius:0;}
.news-body{flex:1;}
.news-headline{font-size:11px;color:var(--text);line-height:1.6;margin-bottom:4px;}
.news-meta{font-size:9px;color:var(--muted);letter-spacing:1px;}
/* MACD / BB */
.ind-row{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border);font-size:10px;}
.ind-lbl{color:var(--muted2);font-size:9px;letter-spacing:1px;text-transform:uppercase;}
/* WATCHLIST */
.wl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;}
.wl-card{
  background:var(--s1);border:1px solid var(--border);
  padding:16px;transition:border-color .2s,transform .2s;
}
.wl-card:hover{border-color:var(--border2);transform:translateY(-2px);}
.wl-tick{font-family:var(--display);font-size:32px;letter-spacing:2px;color:var(--accent);}
.wl-theme{font-size:8px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin:3px 0 12px;}
/* VOLUME PROFILE */
.vp-row{display:flex;align-items:center;gap:6px;margin:2px 0;font-size:9px;}
.vp-price{width:58px;color:var(--muted2);text-align:right;}
.vp-bar{height:8px;background:var(--blue);opacity:.6;min-width:2px;transition:width .4s;}
.vp-bar.poc{background:var(--accent);opacity:1;}
/* CORRELATION */
.corr-cell{
  width:52px;height:52px;display:flex;align-items:center;
  justify-content:center;font-size:9px;font-weight:500;
  border:1px solid var(--border);
}
/* SUPPORT RESISTANCE */
.sr-line{
  display:flex;justify-content:space-between;align-items:center;
  padding:6px 10px;margin:4px 0;font-size:10px;
  border-left:3px solid;
}
/* PORTFOLIO */
.port-row{display:flex;justify-content:space-between;align-items:center;padding:8px 10px;border-bottom:1px solid var(--border);font-size:10px;}
/* CANDLESTICK placeholder note */
.candle-note{font-size:9px;color:var(--muted);letter-spacing:1px;margin-top:6px;}
/* CANDLESTICK TOGGLE */
.toggle-wrap{display:inline-flex;cursor:pointer;}
.toggle-track{width:32px;height:17px;background:var(--s3);border:1px solid var(--border2);border-radius:9px;position:relative;transition:background .2s;}
.toggle-track.on{background:rgba(240,180,41,.2);border-color:var(--accent);}
.toggle-thumb{position:absolute;top:2px;left:2px;width:11px;height:11px;background:var(--muted);border-radius:50%;transition:all .2s;}
.toggle-track.on .toggle-thumb{left:17px;background:var(--accent);}
/* TF BUTTONS */
.tf-btn{
  padding:4px 9px;font-family:var(--mono);font-size:9px;letter-spacing:1px;
  background:var(--s2);border:1px solid var(--border);color:var(--muted2);
  cursor:pointer;transition:all .15s;
}
.tf-btn:hover{border-color:var(--accent);color:var(--accent);}
.tf-btn.on{background:rgba(240,180,41,.1);border-color:var(--accent);color:var(--accent);}
/* scrollbar */
::-webkit-scrollbar{width:3px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);}
/* SAVED TICKERS */
.saved-wrap{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto;}
.saved-chip{
  padding:4px 10px;font-size:9px;letter-spacing:1.5px;
  background:var(--s2);border:1px solid var(--border);
  color:var(--muted2);cursor:pointer;transition:all .15s;
  display:flex;align-items:center;gap:5px;
}
.saved-chip:hover{border-color:var(--accent);color:var(--accent);}
.saved-chip .x{color:var(--muted);font-size:10px;}
.saved-chip .x:hover{color:var(--red);}
/* EARNINGS BADGE */
.earn-badge{
  display:inline-block;padding:3px 8px;
  background:rgba(240,180,41,.12);
  border:1px solid rgba(240,180,41,.3);
  color:var(--accent);font-size:9px;letter-spacing:1px;
  margin-left:8px;
}
/* MACD chart */
.macd-wrap{position:relative;height:120px;margin-top:14px;}
</style>
</head>
<body>

<header>
  <div class="logo">APEX <sub>INTELLIGENCE</sub></div>
  <div class="hdr-center">
    <div class="hdr-pill"><span class="live"><span class="dot"></span>LIVE</span></div>
    <div class="hdr-pill" id="mkt-status">MARKETS —</div>
    <div class="world-clocks" id="world-clocks"></div>
    <a href="/news" class="hdr-pill" style="text-decoration:none;color:var(--accent);border-color:rgba(240,180,41,.3);cursor:pointer">📰 NEWS</a>
  </div>
  <div class="hdr-right">
    <div>MARKET INTELLIGENCE TERMINAL</div>
    <div style="color:var(--muted)">DATA · YFINANCE</div>
  </div>
</header>

<div class="wrap">

  <!-- SEARCH -->
  <div class="search">
    <span class="search-prompt">›</span>
    <input id="ticker" placeholder="AAPL" maxlength="12" />
    <button class="btn btn-gold" onclick="runAll()">ANALYZE</button>
    <button class="btn btn-ghost" onclick="saveTicker()" title="Save to watchlist">+ SAVE</button>
    <div class="loading" id="loading"><div class="spin"></div><span id="load-msg">FETCHING DATA...</span></div>
    <div class="saved-wrap" id="saved-chips"></div>
  </div>

  <!-- TABS -->
  <div class="tabs">
    <button class="tab on"  onclick="showTab('overview',this)">Overview</button>
    <button class="tab"     onclick="showTab('technical',this)">Technical</button>
    <button class="tab"     onclick="showTab('orderflow',this)">Order Flow</button>
    <button class="tab"     onclick="showTab('options',this)">Options Flow</button>
    <button class="tab"     onclick="showTab('news',this)">News + Sentiment</button>
    <button class="tab"     onclick="showTab('portfolio',this)">Portfolio</button>
    <button class="tab"     onclick="showTab('watchlist',this)">Watchlist</button>
  </div>

  <!-- ══ OVERVIEW ══════════════════════════════════════════════════════════════ -->
  <div id="tab-overview">
    <div class="strip" id="stat-strip">
      <div class="sc"><div class="sc-label">Price</div><div class="sc-val" id="s-price">—</div><div class="sc-sub" id="s-chg">enter ticker</div></div>
      <div class="sc"><div class="sc-label">Trend</div><div class="sc-val" id="s-trend" style="font-size:18px;padding-top:3px">—</div><div class="sc-sub" id="s-ema">EMA 20/50</div></div>
      <div class="sc"><div class="sc-label">RSI 14</div><div class="sc-val" id="s-rsi">—</div><div class="sc-sub" id="s-rsi-lbl">—</div></div>
      <div class="sc"><div class="sc-label">Volatility</div><div class="sc-val" id="s-vol">—</div><div class="sc-sub" id="s-risk">—</div></div>
      <div class="sc"><div class="sc-label">52W High</div><div class="sc-val" id="s-52h">—</div><div class="sc-sub" id="s-from-h">—</div></div>
      <div class="sc"><div class="sc-label">7D Forecast</div><div class="sc-val" id="s-7d">—</div><div class="sc-sub" id="s-30d">—</div></div>
      <div class="sc"><div class="sc-label">Confidence</div><div class="sc-val" id="s-conf">—</div><div class="sc-sub">monte carlo</div></div>
      <div class="sc"><div class="sc-label">Earnings</div><div class="sc-val" id="s-earn" style="font-size:14px;padding-top:5px">—</div><div class="sc-sub" id="s-earn-sub">—</div></div>
    </div>

    <div class="panels">
      <div class="panel">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
          <div class="ptitle" style="margin-bottom:0">Price · EMA · Monte Carlo Forecast</div>
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
            <div style="display:flex;gap:3px;" id="tf-buttons">
              <button class="tf-btn on" onclick="changeTF('1wk',this)">1W</button>
              <button class="tf-btn" onclick="changeTF('1mo',this)">1M</button>
              <button class="tf-btn" onclick="changeTF('3mo',this)">3M</button>
              <button class="tf-btn" onclick="changeTF('1y',this)">1Y</button>
              <button class="tf-btn" onclick="changeTF('5y',this)">5Y</button>
              <button class="tf-btn" onclick="changeTF('max',this)">ALL</button>
            </div>
            <label style="display:flex;align-items:center;gap:6px;cursor:pointer;font-size:9px;letter-spacing:1.5px;color:var(--muted2);text-transform:uppercase">
              <div class="toggle-wrap" onclick="toggleCandle()">
                <div class="toggle-track" id="candle-track">
                  <div class="toggle-thumb" id="candle-thumb"></div>
                </div>
              </div>
              CANDLE
            </label>
          </div>
        </div>
        <div class="chart-wrap">
          <canvas id="mainChart"></canvas>
          <div class="empty" id="chart-empty"><div class="empty-big">A</div><div>ENTER TICKER TO LOAD</div></div>
        </div>
        <div class="candle-note" id="chart-note"></div>
      </div>

      <div class="panel" style="display:flex;flex-direction:column;gap:0">
        <div class="ptitle">30-Day Scenarios</div>
        <div id="scenarios"><div class="empty" style="height:90px"><div>—</div></div></div>

        <div class="ptitle" style="margin-top:18px">RSI Signal</div>
        <div id="rsi-vis"><div style="font-size:10px;color:var(--muted)">—</div></div>

        <div class="ptitle" style="margin-top:18px">Support / Resistance</div>
        <div id="sr-section"><div class="empty" style="height:80px"><div>—</div></div></div>

        <div class="ptitle" style="margin-top:18px">Insight</div>
        <div class="insight" id="insight">Load a ticker to generate insight.</div>
      </div>
    </div>
  </div>

  <!-- ══ TECHNICAL ═════════════════════════════════════════════════════════════ -->
  <div id="tab-technical" style="display:none">
    <div class="panels">
      <div class="panel">
        <div class="ptitle">Bollinger Bands + Price</div>
        <div class="chart-wrap"><canvas id="bbChart"></canvas><div class="empty" id="bb-empty"><div class="empty-big">B</div><div>LOAD TICKER</div></div></div>
        <div class="ptitle" style="margin-top:20px">MACD</div>
        <div class="macd-wrap"><canvas id="macdChart"></canvas><div class="empty" id="macd-empty" style="height:120px"><div>—</div></div></div>
      </div>
      <div class="panel">
        <div class="ptitle">Indicators Summary</div>
        <div id="ind-summary"><div class="empty" style="height:120px"><div>LOAD TICKER</div></div></div>
        <div class="ptitle" style="margin-top:18px">Volume Profile (Price Levels)</div>
        <div id="vol-profile"><div class="empty" style="height:160px"><div>—</div></div></div>
      </div>
    </div>
  </div>

  <!-- ══ ORDER FLOW ═════════════════════════════════════════════════════════════ -->
  <div id="tab-orderflow" style="display:none">
    <div class="panels">
      <div class="panel">
        <div class="ptitle">Delta · Buy vs Sell Pressure</div>
        <div id="of-delta"><div class="empty" style="height:100px"><div>LOAD TICKER FIRST</div></div></div>
        <div class="ptitle" style="margin-top:18px">Simulated Tape</div>
        <div id="of-tape"><div class="empty" style="height:180px"><div>—</div></div></div>
      </div>
      <div class="panel">
        <div class="ptitle">Signals</div>
        <div id="of-signals"><div class="empty" style="height:160px"><div>—</div></div></div>
        <div class="insight" id="of-insight">Order flow insight loads after analysis.</div>
      </div>
    </div>
  </div>

  <!-- ══ OPTIONS FLOW ══════════════════════════════════════════════════════════ -->
  <div id="tab-options" style="display:none">
    <div class="panels">
      <div class="panel">
        <div class="ptitle">Unusual Options Activity</div>
        <p style="font-size:9px;color:var(--muted);margin-bottom:12px;line-height:1.8;letter-spacing:.5px">
          Tracks large sweep and block orders. Premium $100K+ shown. ⚠ Simulated from IV/price — live flow requires Unusual Whales / Cheddar Flow.
        </p>
        <div id="opt-table"><div class="empty" style="height:220px"><div>LOAD TICKER FIRST</div></div></div>
      </div>
      <div class="panel" style="display:flex;flex-direction:column;gap:14px">
        <div>
          <div class="ptitle">Put / Call Ratio</div>
          <div id="opt-pcr"><div class="empty" style="height:100px"><div>—</div></div></div>
        </div>
        <div>
          <div class="ptitle">Implied vs Historical Volatility</div>
          <div id="opt-iv"><div class="empty" style="height:80px"><div>—</div></div></div>
        </div>
        <div>
          <div class="ptitle">Max Pain + Gamma Exposure</div>
          <div id="opt-gex"><div class="empty" style="height:80px"><div>—</div></div></div>
        </div>
        <div class="insight" id="opt-insight">Options insight loads after analysis.</div>
      </div>
    </div>
  </div>

  <!-- ══ NEWS ══════════════════════════════════════════════════════════════════ -->
  <div id="tab-news" style="display:none">
    <div class="panels">
      <div class="panel">
        <div class="ptitle">Recent Headlines + Sentiment</div>
        <div id="news-feed"><div class="empty" style="height:300px"><div class="empty-big">N</div><div>LOAD TICKER TO FETCH NEWS</div></div></div>
      </div>
      <div class="panel">
        <div class="ptitle">Sentiment Score</div>
        <div id="sent-score"><div class="empty" style="height:120px"><div>—</div></div></div>
        <div class="ptitle" style="margin-top:18px">Sector Context</div>
        <div id="sector-ctx"><div class="empty" style="height:100px"><div>—</div></div></div>
        <div class="insight" id="news-insight">News insight loads after analysis.</div>
      </div>
    </div>
  </div>

  <!-- ══ PORTFOLIO ═════════════════════════════════════════════════════════════ -->
  <div id="tab-portfolio" style="display:none">
    <div style="margin-bottom:14px;display:flex;gap:8px;align-items:center">
      <input id="port-ticker" class="search" style="width:120px;height:38px;margin:0;padding:0 12px;font-family:var(--display);font-size:18px;letter-spacing:3px" placeholder="AAPL">
      <input id="port-qty" type="number" placeholder="100" style="width:80px;height:38px;background:var(--s1);border:1px solid var(--border);color:var(--text);font-family:var(--mono);font-size:12px;padding:0 10px;outline:none">
      <input id="port-entry" type="number" placeholder="Entry $" style="width:100px;height:38px;background:var(--s1);border:1px solid var(--border);color:var(--text);font-family:var(--mono);font-size:12px;padding:0 10px;outline:none">
      <button class="btn btn-gold" onclick="addPosition()">ADD POSITION</button>
      <button class="btn btn-ghost" onclick="runCorrelation()">RUN CORRELATION</button>
    </div>
    <div class="panels">
      <div class="panel">
        <div class="ptitle">Positions</div>
        <div id="positions"><div class="empty" style="height:200px"><div>ADD POSITIONS ABOVE</div></div></div>
        <div class="ptitle" style="margin-top:18px">Portfolio Risk</div>
        <div id="port-risk"><div class="empty" style="height:80px"><div>—</div></div></div>
      </div>
      <div class="panel">
        <div class="ptitle">Correlation Matrix</div>
        <div id="corr-matrix"><div class="empty" style="height:200px"><div>ADD 2+ POSITIONS THEN CLICK RUN CORRELATION</div></div></div>
      </div>
    </div>
  </div>

  <!-- ══ WATCHLIST ═════════════════════════════════════════════════════════════ -->
  <div id="tab-watchlist" style="display:none">
    <div style="margin-bottom:16px;display:flex;gap:8px;align-items:center">
      <button class="btn btn-gold" onclick="runWatchlist()">GENERATE WATCHLIST</button>
      <span style="font-size:9px;color:var(--muted);letter-spacing:1px">TOP 5 LIQUID NAMES BY MOMENTUM + VOLATILITY</span>
    </div>
    <div id="wl-result"><div class="empty" style="height:280px"><div class="empty-big">W</div><div>CLICK GENERATE</div></div></div>
  </div>

</div><!-- /wrap -->

<script>
// ── STATE ─────────────────────────────────────────────────────────────────────
let D = null;
let charts = {};
let portfolio = JSON.parse(localStorage.getItem('apex_port') || '[]');
let savedTickers = JSON.parse(localStorage.getItem('apex_saved') || '[]');
let candleMode = false;
let currentTF = '1wk';

// ── WORLD CLOCKS ──────────────────────────────────────────────────────────────
const ZONES = [
  {label:'NYSE',   tz:'America/New_York',   sessions:[[9.5,16]]},
  {label:'GMT',    tz:'GMT',                sessions:[]},
  {label:'BST',    tz:'Europe/London',      sessions:[[8,16.5]]},
  {label:'CET',    tz:'Europe/Paris',       sessions:[[9,17.5]]},
  {label:'HKT',    tz:'Asia/Hong_Kong',     sessions:[[9.5,16]]},
  {label:'JPY',    tz:'Asia/Tokyo',         sessions:[[9,15.5]]},
];

function isSessionOpen(tz, sessions) {
  if (!sessions.length) return false;
  const now = new Date();
  const local = new Date(now.toLocaleString('en-US',{timeZone:tz}));
  const h = local.getHours() + local.getMinutes()/60;
  const day = local.getDay();
  if (day===0||day===6) return false;
  return sessions.some(([s,e])=>h>=s&&h<e);
}

function tick() {
  const wc = document.getElementById('world-clocks');
  if (wc) {
    wc.innerHTML = ZONES.map(z=>{
      const now = new Date();
      const t = now.toLocaleTimeString('en-GB',{timeZone:z.tz,hour:'2-digit',minute:'2-digit'});
      const open = isSessionOpen(z.tz, z.sessions);
      return `<div class="wclock">
        <div class="wclock-label">${z.label}</div>
        <div class="wclock-time ${z.sessions.length?(open?'open':'closed'):''}">${t}</div>
      </div>`;
    }).join('');
  }
  const el = document.getElementById('mkt-status');
  if (el) {
    const isOpen = isSessionOpen('America/New_York',[[9.5,16]]);
    el.textContent = isOpen ? 'NYSE OPEN' : 'NYSE CLOSED';
    el.style.color = isOpen ? 'var(--green)' : 'var(--muted)';
  }
}
setInterval(tick, 1000); tick();

// ── CANDLE TOGGLE ─────────────────────────────────────────────────────────────
function toggleCandle() {
  candleMode = !candleMode;
  const track = document.getElementById('candle-track');
  if (track) track.classList.toggle('on', candleMode);
  if (D) drawMainChart(D);
}

// ── TIMEFRAME ─────────────────────────────────────────────────────────────────
function changeTF(tf, el) {
  currentTF = tf;
  document.querySelectorAll('.tf-btn').forEach(b=>b.classList.remove('on'));
  if (el) el.classList.add('on');
  if (D) fetchAndDrawTF();
}

const TF_MAP = {
  '1wk': {period:'1mo',   interval:'1h',  label:'1 Week'},
  '1mo': {period:'3mo',   interval:'1d',  label:'1 Month'},
  '3mo': {period:'6mo',   interval:'1d',  label:'3 Months'},
  '1y':  {period:'1y',    interval:'1d',  label:'1 Year'},
  '5y':  {period:'5y',    interval:'1wk', label:'5 Years'},
  'max': {period:'max',   interval:'1mo', label:'All Time'},
};

async function fetchAndDrawTF() {
  if (!D) return;
  const cfg = TF_MAP[currentTF];
  try {
    const res = await fetch(`/ohlcv/${D.ticker}?period=${cfg.period}&interval=${cfg.interval}`);
    const hist = await res.json();
    if (hist.error) return;
    D._ohlcv = hist;
    drawMainChart(D);
  } catch(e) { console.error(e); }
}

// ── TABS ──────────────────────────────────────────────────────────────────────
function showTab(id, el) {
  ['overview','technical','orderflow','options','news','portfolio','watchlist'].forEach(t =>
    document.getElementById('tab-'+t).style.display = 'none');
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('on'));
  document.getElementById('tab-'+id).style.display = 'block';
  if (el) el.classList.add('on');
}

// ── SAVED TICKERS ─────────────────────────────────────────────────────────────
function renderSaved() {
  const w = document.getElementById('saved-chips');
  w.innerHTML = savedTickers.map(t => `
    <div class="saved-chip" onclick="loadSaved('${t}')">
      ${t}<span class="x" onclick="removeSaved(event,'${t}')">×</span>
    </div>`).join('');
}
function saveTicker() {
  const t = (document.getElementById('ticker').value || '').trim().toUpperCase();
  if (!t || savedTickers.includes(t)) return;
  savedTickers.push(t);
  localStorage.setItem('apex_saved', JSON.stringify(savedTickers));
  renderSaved();
}
function removeSaved(e, t) {
  e.stopPropagation();
  savedTickers = savedTickers.filter(x => x !== t);
  localStorage.setItem('apex_saved', JSON.stringify(savedTickers));
  renderSaved();
}
function loadSaved(t) {
  document.getElementById('ticker').value = t;
  runAll();
}
renderSaved();

// ── HELPERS ───────────────────────────────────────────────────────────────────
const fmt = v => v > 0 ? '+'+v : ''+v;
const clr = v => v > 0 ? 'var(--green)' : v < 0 ? 'var(--red)' : 'var(--accent)';
function destroyChart(id) { if (charts[id]) { charts[id].destroy(); delete charts[id]; } }

function setLoad(msg) {
  document.getElementById('loading').style.display = 'flex';
  document.getElementById('load-msg').textContent = msg || 'FETCHING DATA...';
}
function clearLoad() { document.getElementById('loading').style.display = 'none'; }

// ── MAIN FETCH ────────────────────────────────────────────────────────────────
async function runAll() {
  const ticker = (document.getElementById('ticker').value || 'AAPL').trim().toUpperCase();
  setLoad('ANALYZING ' + ticker + '...');
  try {
    const res = await fetch('/forecast/' + ticker);
    D = await res.json();
    if (D.error) { alert(D.error); return; }
    // Also fetch OHLCV for current TF
    const cfg = TF_MAP[currentTF];
    const ohlcvRes = await fetch(`/ohlcv/${ticker}?period=${cfg.period}&interval=${cfg.interval}`);
    D._ohlcv = await ohlcvRes.json();
    renderOverview(D);
    renderTechnical(D);
    renderOrderFlow(D);
    renderOptions(D);
    renderNews(D);
  } catch(e) { alert('Error: ' + e.message); }
  finally { clearLoad(); }
}

// ── OVERVIEW ──────────────────────────────────────────────────────────────────
function renderOverview(d) {
  const set = (id, v) => { const el = document.getElementById(id); if(el) el.textContent = v; };
  const setC = (id, v, c) => { const el = document.getElementById(id); if(el){el.textContent=v;el.style.color=c||'';} };

  setC('s-price', '$'+d.current_price);
  setC('s-chg', fmt(d.change_1d_pct)+'% today', clr(d.change_1d_pct));
  setC('s-trend', d.trend, d.trend==='Uptrend'?'var(--green)':d.trend==='Downtrend'?'var(--red)':'var(--accent)');
  set('s-ema', 'EMA20 $'+d.ema20+' / EMA50 $'+d.ema50);
  setC('s-rsi', d.rsi14, d.rsi14>70?'var(--red)':d.rsi14<30?'var(--green)':'var(--accent)');
  set('s-rsi-lbl', d.rsi14>70?'overbought':d.rsi14<30?'oversold':'neutral');
  set('s-vol', d.volatility+'%');
  set('s-risk', 'risk '+d.risk_score+'/100');
  setC('s-52h', '$'+d.high_52w);
  set('s-from-h', d.from_high_52w+'% from high');
  setC('s-7d', '$'+d.forecast_7d);
  set('s-30d', '30D: $'+d.forecast_30d);
  set('s-conf', d.confidence+'%');

  // Earnings
  const earnEl = document.getElementById('s-earn');
  if (d.earnings_date) {
    earnEl.textContent = d.earnings_date;
    earnEl.style.color = 'var(--accent)';
    set('s-earn-sub', d.earnings_surprise ? 'last surprise: '+d.earnings_surprise : 'upcoming');
  } else {
    earnEl.textContent = 'N/A';
    earnEl.style.color = 'var(--muted)';
    set('s-earn-sub', 'no data');
  }

  // RSI visual
  document.getElementById('rsi-vis').innerHTML = `
    <div style="display:flex;justify-content:space-between;font-size:8px;color:var(--muted);margin-bottom:4px;letter-spacing:1px">
      <span>OVERSOLD 30</span><span style="color:${d.rsi14>70?'var(--red)':d.rsi14<30?'var(--green)':'var(--accent)'}">RSI ${d.rsi14}</span><span>OVERBOUGHT 70</span>
    </div>
    <div class="rsi-track"><div class="rsi-pin" style="left:${d.rsi14}%"></div></div>
    <div style="font-size:9px;color:var(--muted2);margin-top:4px">${d.rsi14>70?'⚠ Overbought — possible pullback':d.rsi14<30?'⚠ Oversold — possible bounce':'✓ Neutral territory'}</div>`;

  // Scenarios
  const mx = Math.max(Math.abs(d.bull),Math.abs(d.bear),1);
  document.getElementById('scenarios').innerHTML = `
    <div class="scen-row"><div class="scen-lbl">BULL</div><div class="scen-bar"><div class="scen-fill" style="width:${(d.bull/mx)*100}%;background:var(--green)"></div></div><div class="scen-pct up">${fmt(d.bull)}%</div></div>
    <div class="scen-row"><div class="scen-lbl">BASE</div><div class="scen-bar"><div class="scen-fill" style="width:${(Math.abs(d.base)/mx)*100}%;background:var(--accent)"></div></div><div class="scen-pct neu">${fmt(d.base)}%</div></div>
    <div class="scen-row"><div class="scen-lbl">BEAR</div><div class="scen-bar"><div class="scen-fill" style="width:${(Math.abs(d.bear)/mx)*100}%;background:var(--red)"></div></div><div class="scen-pct dn">${fmt(d.bear)}%</div></div>
    <div style="font-size:9px;color:var(--muted);margin-top:8px">Monte Carlo · 500 paths · 30 days</div>`;

  // Support / Resistance
  if (d.support_levels && d.resistance_levels) {
    let sr = '';
    d.resistance_levels.forEach(l => sr += `<div class="sr-line" style="border-color:var(--red);background:rgba(240,73,62,.04)"><span style="font-size:9px;color:var(--muted)">RESISTANCE</span><span style="color:var(--red)">$${l}</span></div>`);
    d.support_levels.forEach(l => sr += `<div class="sr-line" style="border-color:var(--green);background:rgba(35,209,139,.04)"><span style="font-size:9px;color:var(--muted)">SUPPORT</span><span style="color:var(--green)">$${l}</span></div>`);
    document.getElementById('sr-section').innerHTML = sr;
  }

  document.getElementById('insight').textContent = d.explanation;
  document.getElementById('chart-empty').style.display = 'none';
  drawMainChart(d);
}

// ── MAIN CHART ────────────────────────────────────────────────────────────────
function drawMainChart(d) {
  destroyChart('main');
  const ctx = document.getElementById('mainChart').getContext('2d');
  const ohlcv = d._ohlcv;
  const useLine = !candleMode || !ohlcv || ohlcv.error;

  let labels, datasets;

  if (useLine) {
    // Line chart with forecast
    const hLen = d.history_dates.length;
    labels = d.history_dates.concat(d.forecast_dates);
    const hist = d.history_prices.concat(new Array(d.forecast_dates.length).fill(null));
    const med  = new Array(hLen-1).fill(null).concat([d.history_prices[hLen-1]]).concat(d.forecast_median.slice(1));
    const p10  = new Array(hLen-1).fill(null).concat([d.history_prices[hLen-1]]).concat(d.forecast_p10.slice(1));
    const p90  = new Array(hLen-1).fill(null).concat([d.history_prices[hLen-1]]).concat(d.forecast_p90.slice(1));
    const e20  = d.ema20_series ? d.ema20_series.concat(new Array(d.forecast_dates.length).fill(null)) : [];
    const e50  = d.ema50_series ? d.ema50_series.concat(new Array(d.forecast_dates.length).fill(null)) : [];
    const base = {fill:false,tension:.2,pointRadius:0,borderWidth:1.5};
    datasets = [
      {...base,label:'Price',    data:hist,borderColor:'rgba(240,180,41,.9)',backgroundColor:'rgba(240,180,41,.04)'},
      {...base,label:'Forecast', data:med, borderColor:'rgba(35,209,139,.8)',borderDash:[5,4]},
      {...base,label:'P90',      data:p90, borderColor:'rgba(61,142,248,.35)',borderDash:[3,3]},
      {...base,label:'P10',      data:p10, borderColor:'rgba(240,73,62,.35)', borderDash:[3,3],fill:'-1',backgroundColor:'rgba(240,73,62,.04)'},
      {...base,label:'EMA20',    data:e20, borderColor:'rgba(61,142,248,.6)', borderWidth:1},
      {...base,label:'EMA50',    data:e50, borderColor:'rgba(224,92,42,.6)',  borderWidth:1},
    ];
  } else {
    // Candlestick (rendered as float bar chart simulation)
    labels = ohlcv.dates;
    // We simulate candles using bar chart with floating bars
    const bullColor = 'rgba(35,209,139,0.8)';
    const bearColor = 'rgba(240,73,62,0.8)';
    const bodyData = ohlcv.open.map((o,i)=>[Math.min(o,ohlcv.close[i]), Math.max(o,ohlcv.close[i])]);
    const wickHigh = ohlcv.open.map((o,i)=>[ohlcv.low[i], ohlcv.high[i]]);
    const colors   = ohlcv.open.map((o,i)=>ohlcv.close[i]>=o?bullColor:bearColor);
    datasets = [
      {
        label:'Wick',
        data: wickHigh,
        backgroundColor: colors.map(c=>c.replace('0.8','0.4')),
        borderWidth: 0,
        barPercentage: 0.12,
        categoryPercentage: 1,
      },
      {
        label:'Body',
        data: bodyData,
        backgroundColor: colors,
        borderWidth: 0,
        barPercentage: 0.55,
        categoryPercentage: 1,
      },
    ];
  }

  const chartConfig = {
    type: useLine ? 'line' : 'bar',
    data: {labels, datasets},
    options:{
      responsive:true,maintainAspectRatio:false,
      animation:{duration:400,easing:'easeOutQuart'},
      interaction:{mode:'index',intersect:false},
      plugins:{
        legend:{position:'bottom',labels:{color:'#3d4d68',font:{family:"'DM Mono',monospace",size:9},boxWidth:18,padding:12}},
        tooltip:{
          backgroundColor:'#0d1018',borderColor:'#1c2235',borderWidth:1,
          titleColor:'#f0b429',bodyColor:'#5a6e8f',
          titleFont:{family:"'DM Mono',monospace",size:10},
          bodyFont:{family:"'DM Mono',monospace",size:9},
          callbacks:{label:c=>{
            if(Array.isArray(c.parsed.y)) return ` ${c.dataset.label}: $${c.parsed.y[0].toFixed(2)} – $${c.parsed.y[1].toFixed(2)}`;
            return c.parsed.y!=null?` ${c.dataset.label}: $${c.parsed.y.toFixed(2)}`:null;
          }}
        },
        zoom:{
          pan:{enabled:true,mode:'x'},
          zoom:{wheel:{enabled:true},pinch:{enabled:true},mode:'x'},
        },
        ...(useLine ? {annotation:{annotations:{fl:{type:'line',xMin:d.history_dates.length-1,xMax:d.history_dates.length-1,
          borderColor:'rgba(240,180,41,.2)',borderWidth:1,borderDash:[4,4],
          label:{display:true,content:'FORECAST →',color:'rgba(240,180,41,.4)',font:{family:"'DM Mono',monospace",size:8},position:'start',yAdjust:-10}}}}} : {})
      },
      scales:{
        x:{ticks:{color:'#1c2235',font:{family:"'DM Mono',monospace",size:8},maxTicksLimit:10,maxRotation:0},grid:{color:'rgba(28,34,53,.5)'}},
        y:{position:'right',stacked:false,ticks:{color:'#1c2235',font:{family:"'DM Mono',monospace",size:8},callback:v=>'$'+v.toFixed(0)},grid:{color:'rgba(28,34,53,.5)'}}
      }
    }
  };

  charts['main'] = new Chart(ctx, chartConfig);
  document.getElementById('chart-note').textContent = candleMode && !useLine
    ? `Candlestick · ${TF_MAP[currentTF].label} · Scroll to zoom · Drag to pan`
    : `Line chart · ${TF_MAP[currentTF].label} · Toggle candle for OHLC view`;
}

// ── TECHNICAL ─────────────────────────────────────────────────────────────────
function renderTechnical(d) {
  // Indicators summary
  document.getElementById('ind-summary').innerHTML = `
    <div class="ind-row"><span class="ind-lbl">EMA 20</span><span>$${d.ema20}</span></div>
    <div class="ind-row"><span class="ind-lbl">EMA 50</span><span>$${d.ema50}</span></div>
    <div class="ind-row"><span class="ind-lbl">RSI 14</span><span style="color:${d.rsi14>70?'var(--red)':d.rsi14<30?'var(--green)':'var(--accent)'}">${d.rsi14}</span></div>
    <div class="ind-row"><span class="ind-lbl">MACD</span><span style="color:${d.macd_val>=0?'var(--green)':'var(--red)'}">${d.macd_val} (signal: ${d.macd_signal})</span></div>
    <div class="ind-row"><span class="ind-lbl">BB Upper</span><span style="color:var(--red)">$${d.bb_upper}</span></div>
    <div class="ind-row"><span class="ind-lbl">BB Middle</span><span>$${d.bb_mid}</span></div>
    <div class="ind-row"><span class="ind-lbl">BB Lower</span><span style="color:var(--green)">$${d.bb_lower}</span></div>
    <div class="ind-row"><span class="ind-lbl">BB Width</span><span>${d.bb_width}%</span></div>
    <div class="ind-row"><span class="ind-lbl">Volatility</span><span>${d.volatility}%</span></div>
    <div class="ind-row"><span class="ind-lbl">Risk Score</span><span>${d.risk_score}/100</span></div>
  `;

  // Volume profile
  if (d.vol_profile) {
    const maxV = Math.max(...d.vol_profile.map(r=>r.vol));
    document.getElementById('vol-profile').innerHTML = d.vol_profile.map(r=>`
      <div class="vp-row">
        <div class="vp-price">$${r.price}</div>
        <div class="vp-bar ${r.poc?'poc':''}" style="width:${Math.max(4,(r.vol/maxV)*200)}px"></div>
        ${r.poc?'<span style="font-size:8px;color:var(--accent);letter-spacing:1px">POC</span>':''}
      </div>`).join('');
  }

  // BB Chart
  if (d.bb_series) {
    document.getElementById('bb-empty').style.display = 'none';
    destroyChart('bb');
    const ctx2 = document.getElementById('bbChart').getContext('2d');
    const lbl = d.history_dates;
    charts['bb'] = new Chart(ctx2, {
      type:'line',
      data:{labels:lbl,datasets:[
        {label:'Price',data:d.history_prices,borderColor:'rgba(240,180,41,.9)',fill:false,tension:.2,pointRadius:0,borderWidth:1.5},
        {label:'BB Upper',data:d.bb_series.upper,borderColor:'rgba(240,73,62,.4)',fill:false,tension:.2,pointRadius:0,borderWidth:1,borderDash:[3,3]},
        {label:'BB Mid',data:d.bb_series.mid,borderColor:'rgba(90,110,143,.4)',fill:false,tension:.2,pointRadius:0,borderWidth:1},
        {label:'BB Lower',data:d.bb_series.lower,borderColor:'rgba(35,209,139,.4)',fill:'-2',backgroundColor:'rgba(35,209,139,.04)',tension:.2,pointRadius:0,borderWidth:1,borderDash:[3,3]},
      ]},
      options:{responsive:true,maintainAspectRatio:false,
        plugins:{legend:{position:'bottom',labels:{color:'#3d4d68',font:{size:9},boxWidth:14,padding:10}},
          tooltip:{backgroundColor:'#0d1018',borderColor:'#1c2235',borderWidth:1,titleColor:'#f0b429',bodyColor:'#5a6e8f'}},
        scales:{x:{ticks:{color:'#1c2235',font:{size:8},maxTicksLimit:8,maxRotation:0},grid:{color:'rgba(28,34,53,.5)'}},
          y:{position:'right',ticks:{color:'#1c2235',font:{size:8},callback:v=>'$'+v.toFixed(0)},grid:{color:'rgba(28,34,53,.5)'}}}}
    });
  }

  // MACD Chart
  if (d.macd_series) {
    document.getElementById('macd-empty').style.display = 'none';
    destroyChart('macd');
    const ctx3 = document.getElementById('macdChart').getContext('2d');
    charts['macd'] = new Chart(ctx3, {
      type:'bar',
      data:{labels:d.history_dates,datasets:[
        {label:'MACD Histogram',data:d.macd_series.hist,backgroundColor:d.macd_series.hist.map(v=>v>=0?'rgba(35,209,139,.6)':'rgba(240,73,62,.6)'),borderWidth:0},
        {type:'line',label:'MACD',data:d.macd_series.macd,borderColor:'rgba(240,180,41,.8)',fill:false,tension:.3,pointRadius:0,borderWidth:1.5},
        {type:'line',label:'Signal',data:d.macd_series.signal,borderColor:'rgba(61,142,248,.8)',fill:false,tension:.3,pointRadius:0,borderWidth:1.5},
      ]},
      options:{responsive:true,maintainAspectRatio:false,
        plugins:{legend:{position:'bottom',labels:{color:'#3d4d68',font:{size:9},boxWidth:14,padding:8}}},
        scales:{x:{ticks:{color:'#1c2235',font:{size:8},maxTicksLimit:8,maxRotation:0},grid:{color:'rgba(28,34,53,.4)'}},
          y:{position:'right',ticks:{color:'#1c2235',font:{size:8}},grid:{color:'rgba(28,34,53,.4)'}}}}
    });
  }
}

// ── ORDER FLOW ────────────────────────────────────────────────────────────────
function renderOrderFlow(d) {
  const pct = Math.min(100, Math.max(0, (d.of_delta + 1) / 2 * 100));
  document.getElementById('of-delta').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px">
      <div class="sc"><div class="sc-label">Delta</div>
        <div class="sc-val ${d.of_delta>0?'up':'dn'}" style="font-size:20px">${d.of_delta>0?'+':''}${(d.of_delta*100).toFixed(1)}%</div>
        <div class="sc-sub">${d.of_delta>0?'buyers dominant':'sellers dominant'}</div></div>
      <div class="sc"><div class="sc-label">Buy Vol</div>
        <div class="sc-val up" style="font-size:20px">${(d.of_buy_vol/1e6).toFixed(2)}M</div>
        <div class="sc-sub">aggressive bids</div></div>
      <div class="sc"><div class="sc-label">Sell Vol</div>
        <div class="sc-val dn" style="font-size:20px">${(d.of_sell_vol/1e6).toFixed(2)}M</div>
        <div class="sc-sub">aggressive asks</div></div>
    </div>
    <div style="font-size:8px;letter-spacing:1.5px;color:var(--muted);display:flex;justify-content:space-between;margin-bottom:4px"><span>SELL</span><span>DELTA BALANCE</span><span>BUY</span></div>
    <div class="delta-bar"><div style="height:7px;background:linear-gradient(90deg,var(--red),var(--green));width:${pct}%"></div></div>`;

  const rows = d.of_tape.map(t=>`<tr>
    <td style="color:var(--muted2)">${t.time}</td>
    <td><span class="badge ${t.side==='BUY'?'b-buy':'b-sell'}">${t.side}</span></td>
    <td>$${t.price}</td><td>${t.size.toLocaleString()}</td>
    <td><span class="badge ${t.type==='SWEEP'?'b-sweep':'b-block'}">${t.type}</span></td>
  </tr>`).join('');
  document.getElementById('of-tape').innerHTML = `<table><thead><tr><th>TIME</th><th>SIDE</th><th>PRICE</th><th>SIZE</th><th>TYPE</th></tr></thead><tbody>${rows}</tbody></table>`;

  document.getElementById('of-signals').innerHTML = d.of_signals.map(s=>`
    <div style="padding:10px 12px;border-left:3px solid ${s.bullish?'var(--green)':'var(--red)'};background:var(--s2);margin-bottom:8px">
      <div style="font-size:8px;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:4px">${s.label}</div>
      <div style="font-size:10px;color:var(--text);line-height:1.7">${s.desc}</div>
    </div>`).join('');
  document.getElementById('of-insight').textContent = d.of_summary;
}

// ── OPTIONS FLOW ──────────────────────────────────────────────────────────────
function renderOptions(d) {
  const rows = d.opt_flow.map(o=>`<tr>
    <td style="color:var(--muted2)">${o.time}</td>
    <td style="font-weight:500">${o.expiry}</td>
    <td style="color:var(--muted2)">$${o.strike}</td>
    <td><span class="badge ${o.type==='CALL'?'b-call':'b-put'}">${o.type}</span></td>
    <td><span class="badge ${o.exec==='SWEEP'?'b-sweep':'b-block'}">${o.exec}</span></td>
    <td style="color:var(--accent)">$${o.premium}</td>
    <td style="color:var(--muted2)">${o.oi.toLocaleString()}</td>
    <td style="color:${o.sentiment==='BULLISH'?'var(--green)':'var(--red)'};font-size:9px;font-weight:500">${o.sentiment}</td>
  </tr>`).join('');
  document.getElementById('opt-table').innerHTML = `<table><thead><tr><th>TIME</th><th>EXPIRY</th><th>STRIKE</th><th>TYPE</th><th>EXEC</th><th>PREMIUM</th><th>OI</th><th>SIGNAL</th></tr></thead><tbody>${rows}</tbody></table>`;

  const pcr = d.put_call_ratio;
  document.getElementById('opt-pcr').innerHTML = `
    <div style="display:flex;align-items:flex-end;gap:10px;margin-bottom:10px">
      <div style="font-family:var(--display);font-size:48px;color:${pcr>1?'var(--red)':pcr<.7?'var(--green)':'var(--accent)'}">${pcr.toFixed(2)}</div>
      <div style="padding-bottom:8px;font-size:9px;color:var(--muted2);line-height:1.8">PUT/CALL<br>${pcr>1.2?'Bearish':pcr<.7?'Bullish':'Neutral'}</div>
    </div>
    <div style="height:7px;background:var(--s3)"><div style="height:100%;width:${Math.min(100,pcr*50)}%;background:${pcr>1?'var(--red)':'var(--green)'}"></div></div>
    <div style="font-size:9px;color:var(--muted);margin-top:6px">PCR > 1.2 = bearish hedge · < 0.7 = bullish spec</div>`;

  document.getElementById('opt-iv').innerHTML = `
    <div style="display:flex;gap:24px">
      <div><div class="sc-label">Implied Vol</div>
        <div style="font-family:var(--display);font-size:32px;color:${d.iv>50?'var(--red)':d.iv>30?'var(--accent)':'var(--green)'}">${d.iv.toFixed(1)}%</div>
        <div style="font-size:9px;color:var(--muted2)">${d.iv>50?'Elevated':'d.iv>30?Moderate:Low'}</div></div>
      <div><div class="sc-label">Hist Vol</div>
        <div style="font-family:var(--display);font-size:32px;color:var(--muted2)">${d.hv.toFixed(1)}%</div>
        <div style="font-size:9px;color:${d.iv>d.hv?'var(--red)':'var(--green)'}">${d.iv>d.hv?'IV > HV (premiums rich)':'IV < HV (options cheap)'}</div></div>
    </div>`;

  document.getElementById('opt-gex').innerHTML = `
    <div style="display:flex;gap:24px">
      <div><div class="sc-label">Max Pain</div>
        <div style="font-family:var(--display);font-size:28px;color:var(--accent)">$${d.max_pain}</div>
        <div style="font-size:9px;color:var(--muted2)">options expiry magnet</div></div>
      <div><div class="sc-label">GEX Exposure</div>
        <div style="font-family:var(--display);font-size:28px;color:${d.gex>0?'var(--green)':'var(--red)'}">${d.gex>0?'+':''}${d.gex}B</div>
        <div style="font-size:9px;color:var(--muted2)">${d.gex>0?'Positive — suppresses vol':'Negative — amplifies vol'}</div></div>
    </div>`;

  document.getElementById('opt-insight').textContent = d.opt_summary;
}

// ── NEWS ──────────────────────────────────────────────────────────────────────
function renderNews(d) {
  if (!d.news || !d.news.length) {
    document.getElementById('news-feed').innerHTML = '<div class="empty" style="height:200px"><div>NO NEWS DATA</div></div>';
    return;
  }
  document.getElementById('news-feed').innerHTML = d.news.map(n=>`
    <div class="news-item">
      <div class="news-sent" style="background:${n.score>0.1?'var(--green)':n.score<-0.1?'var(--red)':'var(--muted)'}"></div>
      <div class="news-body">
        <div class="news-headline">${n.title}</div>
        <div class="news-meta">${n.source} · ${n.age} · <span style="color:${n.score>0.1?'var(--green)':n.score<-0.1?'var(--red)':'var(--muted2)'}">${n.score>0.1?'BULLISH':n.score<-0.1?'BEARISH':'NEUTRAL'} (${(n.score*100).toFixed(0)})</span></div>
      </div>
    </div>`).join('');

  const avg = d.news_sentiment_avg;
  document.getElementById('sent-score').innerHTML = `
    <div style="display:flex;align-items:flex-end;gap:8px;margin-bottom:10px">
      <div style="font-family:var(--display);font-size:52px;color:${avg>10?'var(--green)':avg<-10?'var(--red)':'var(--accent)'}">${avg>0?'+':''}${avg}</div>
      <div style="padding-bottom:8px;font-size:9px;color:var(--muted2);line-height:1.8">SENTIMENT SCORE<br>${avg>15?'Very Bullish':avg>5?'Bullish':avg<-15?'Very Bearish':avg<-5?'Bearish':'Neutral'}</div>
    </div>
    <div style="height:7px;background:var(--s3)"><div style="height:100%;width:${Math.min(100,Math.abs(avg)+50)}%;background:${avg>0?'var(--green)':'var(--red)'}"></div></div>`;

  document.getElementById('sector-ctx').innerHTML = `
    <div style="font-size:10px;color:var(--text);line-height:1.9">${d.sector_context}</div>`;
  document.getElementById('news-insight').textContent = d.news_insight;
}

// ── PORTFOLIO ─────────────────────────────────────────────────────────────────
function addPosition() {
  const t = document.getElementById('port-ticker').value.trim().toUpperCase();
  const q = parseFloat(document.getElementById('port-qty').value)||1;
  const e = parseFloat(document.getElementById('port-entry').value)||0;
  if (!t) return;
  portfolio = portfolio.filter(p=>p.ticker!==t);
  portfolio.push({ticker:t,qty:q,entry:e});
  localStorage.setItem('apex_port', JSON.stringify(portfolio));
  renderPortfolio();
}

async function renderPortfolio() {
  if (!portfolio.length) return;
  let totalValue=0, totalPnl=0;
  let rows = '';
  for (const p of portfolio) {
    try {
      const r = await fetch('/price/'+p.ticker);
      const pr = await r.json();
      const price = pr.price || p.entry;
      const value = price * p.qty;
      const pnl = p.entry ? (price - p.entry) * p.qty : 0;
      const pnlPct = p.entry ? ((price-p.entry)/p.entry*100).toFixed(2) : '—';
      totalValue += value;
      totalPnl += pnl;
      rows += `<div class="port-row">
        <span style="font-family:var(--display);font-size:18px;color:var(--accent)">${p.ticker}</span>
        <span style="color:var(--muted2)">${p.qty} @ $${p.entry||'—'}</span>
        <span>$${price.toFixed(2)}</span>
        <span>$${value.toFixed(0)}</span>
        <span style="color:${pnl>=0?'var(--green)':'var(--red)'}">${pnl>=0?'+':''}$${pnl.toFixed(0)} (${pnlPct}%)</span>
        <button onclick="removePos('${p.ticker}')" style="background:none;border:none;color:var(--muted);cursor:pointer;font-size:12px">×</button>
      </div>`;
    } catch(e) { console.log(e); }
  }
  document.getElementById('positions').innerHTML = `
    <div style="display:flex;justify-content:space-between;font-size:8px;letter-spacing:1.5px;color:var(--muted);padding:0 10px 8px;text-transform:uppercase">
      <span>Ticker</span><span>Position</span><span>Price</span><span>Value</span><span>P&L</span><span></span>
    </div>${rows}`;
  document.getElementById('port-risk').innerHTML = `
    <div style="display:flex;gap:24px;padding:10px">
      <div><div class="sc-label">Total Value</div><div style="font-family:var(--display);font-size:24px">$${totalValue.toFixed(0)}</div></div>
      <div><div class="sc-label">Total P&L</div><div style="font-family:var(--display);font-size:24px;color:${totalPnl>=0?'var(--green)':'var(--red)'}">${totalPnl>=0?'+':''}$${totalPnl.toFixed(0)}</div></div>
      <div><div class="sc-label">Positions</div><div style="font-family:var(--display);font-size:24px">${portfolio.length}</div></div>
    </div>`;
}

function removePos(t) {
  portfolio = portfolio.filter(p=>p.ticker!==t);
  localStorage.setItem('apex_port', JSON.stringify(portfolio));
  renderPortfolio();
}

async function runCorrelation() {
  if (portfolio.length < 2) { alert('Add at least 2 positions.'); return; }
  setLoad('COMPUTING CORRELATION...');
  try {
    const tickers = portfolio.map(p=>p.ticker).join(',');
    const res = await fetch('/correlation?tickers='+tickers);
    const d = await res.json();
    if (d.error) { alert(d.error); return; }
    const n = d.tickers.length;
    let cells = '';
    for (let i=0;i<n;i++) {
      cells += `<div style="display:flex">`;
      for (let j=0;j<n;j++) {
        const v = d.matrix[i][j];
        const bg = v>0.7?'rgba(240,73,62,.25)':v>0.3?'rgba(240,180,41,.15)':v<-0.3?'rgba(35,209,139,.2)':'rgba(28,34,53,.5)';
        cells += `<div class="corr-cell" style="background:${bg};color:${i===j?'var(--muted)':'var(--text)'}">${v.toFixed(2)}</div>`;
      }
      cells += `</div>`;
    }
    document.getElementById('corr-matrix').innerHTML = `
      <div style="font-size:9px;color:var(--muted);margin-bottom:8px;letter-spacing:1px">RED = high correlation (move together) · GREEN = negative correlation (hedge)</div>
      <div style="display:flex;gap:2px;margin-bottom:4px">${d.tickers.map(t=>`<div style="width:52px;font-size:8px;letter-spacing:1px;color:var(--accent);text-align:center">${t}</div>`).join('')}</div>
      ${cells}`;
  } catch(e) { alert(e.message); }
  finally { clearLoad(); }
}

// ── WATCHLIST ─────────────────────────────────────────────────────────────────
async function runWatchlist() {
  setLoad('SCANNING UNIVERSE...');
  try {
    const res = await fetch('/watchlist');
    const d = await res.json();
    if (d.error) { alert(d.error); return; }
    let html = `<div class="insight" style="margin-bottom:16px"><b style="color:var(--text)">Macro View:</b> ${d.week_summary}</div><div class="wl-grid">`;
    for (const s of d.stocks) {
      html += `<div class="wl-card">
        <div class="wl-tick">${s.ticker}</div>
        <div class="wl-theme">${s.theme}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
          <div><div class="sc-label">Price</div><div style="font-size:18px;font-weight:500">$${s.current_price}</div></div>
          <div><div class="sc-label">1M Return</div><div style="font-size:18px;color:${s.return_1m>=0?'var(--green)':'var(--red)'}">${s.return_1m>0?'+':''}${s.return_1m}%</div></div>
          <div><div class="sc-label">Volatility</div><div style="font-size:18px">${s.volatility}%</div></div>
          <div><div class="sc-label">RSI</div><div style="font-size:18px;color:${s.rsi>70?'var(--red)':s.rsi<30?'var(--green)':'var(--accent)'}">${s.rsi}</div></div>
        </div>
        <div style="font-size:9px;color:var(--muted2);line-height:1.8">${s.reason}</div>
        <button class="btn btn-ghost" style="margin-top:10px;width:100%;font-size:9px" onclick="document.getElementById('ticker').value='${s.ticker}';runAll();showTab('overview',document.querySelector('.tab'))">ANALYZE →</button>
      </div>`;
    }
    html += '</div>';
    document.getElementById('wl-result').innerHTML = html;
  } catch(e) { alert(e.message); }
  finally { clearLoad(); }
}

// Init portfolio
if (portfolio.length) renderPortfolio();

// Enter key
document.getElementById('ticker').addEventListener('keydown', e => { if(e.key==='Enter') runAll(); });
</script>
</body>
</html>
"""

# ── HELPERS ────────────────────────────────────────────────────────────────────
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return float(round((100 - 100/(1+rs)).iloc[-1], 2))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def compute_bollinger(series, period=20, std_dev=2):
    mid = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    return upper, mid, lower

def monte_carlo_paths(last_price, mu, sigma, days=30, n_paths=500):
    paths = np.zeros((days, n_paths))
    paths[0] = last_price
    for t in range(1, days):
        z = np.random.normal(size=n_paths)
        paths[t] = paths[t-1] * np.exp((mu - 0.5*sigma**2) + sigma * z)
    return paths

def get_support_resistance(close, n=5):
    prices = close.values
    highs, lows = [], []
    for i in range(n, len(prices)-n):
        if prices[i] == max(prices[i-n:i+n+1]):
            highs.append(round(float(prices[i]), 2))
        if prices[i] == min(prices[i-n:i+n+1]):
            lows.append(round(float(prices[i]), 2))
    current = float(close.iloc[-1])
    resistance = sorted([h for h in highs if h > current], reverse=True)[:2]
    support = sorted([l for l in lows if l < current])[-2:]
    return resistance, support

def get_volume_profile(close, volume, bins=12):
    price_min, price_max = float(close.min()), float(close.max())
    edges = np.linspace(price_min, price_max, bins+1)
    vols = []
    for i in range(len(edges)-1):
        mask = (close >= edges[i]) & (close < edges[i+1])
        v = float(volume[mask].sum())
        vols.append({"price": round(float((edges[i]+edges[i+1])/2), 2), "vol": v, "poc": False})
    max_vol = max(r["vol"] for r in vols) if vols else 1
    poc_idx = max(range(len(vols)), key=lambda i: vols[i]["vol"])
    vols[poc_idx]["poc"] = True
    return vols

def simulate_news_sentiment(ticker, trend):
    rng = np.random.default_rng(hash(ticker) % 9999)
    headlines_bull = [
        f"{ticker} beats Q earnings estimates, raises full-year guidance",
        f"Analysts raise {ticker} price target following strong demand signals",
        f"{ticker} secures major new partnership deal, shares surge",
        f"Institutional buying accelerates in {ticker} ahead of catalyst",
        f"{ticker} reports record revenue in latest quarter",
    ]
    headlines_bear = [
        f"{ticker} misses revenue estimates, CFO flags macro headwinds",
        f"Analyst downgrades {ticker} citing valuation concerns",
        f"{ticker} faces regulatory scrutiny over new product line",
        f"Insider selling reported at {ticker} ahead of lock-up expiry",
        f"{ticker} cuts guidance amid softening demand environment",
    ]
    headlines_neutral = [
        f"{ticker} in talks with potential strategic partner",
        f"{ticker} announces share repurchase programme",
        f"{ticker} appoints new Chief Technology Officer",
        f"Mixed signals on {ticker} as market awaits next catalyst",
    ]
    sources = ["Bloomberg", "Reuters", "WSJ", "FT", "CNBC", "Seeking Alpha", "MarketWatch"]
    ages = ["2m ago", "14m ago", "38m ago", "1h ago", "2h ago", "4h ago", "6h ago", "9h ago"]
    news = []
    bias = 0.55 if trend == "Uptrend" else 0.35 if trend == "Downtrend" else 0.45
    for i in range(8):
        r = float(rng.random())
        if r < bias:
            title = str(rng.choice(headlines_bull))
            score = float(rng.uniform(0.15, 0.45))
        elif r < bias + 0.3:
            title = str(rng.choice(headlines_bear))
            score = float(rng.uniform(-0.45, -0.1))
        else:
            title = str(rng.choice(headlines_neutral))
            score = float(rng.uniform(-0.08, 0.08))
        news.append({
            "title": title,
            "source": str(rng.choice(sources)),
            "age": ages[i % len(ages)],
            "score": round(score, 2)
        })
    avg_score = round(float(np.mean([n["score"] for n in news])) * 100, 1)
    return news, avg_score

def simulate_order_flow(current_price, returns, volume, trend):
    rng = np.random.default_rng(42)
    avg_vol = float(volume.mean())
    total_vol = float(volume.sum())
    delta = round(float(rng.uniform(0.05, 0.32)) if trend == "Uptrend"
                  else float(rng.uniform(-0.32, -0.05)) if trend == "Downtrend"
                  else float(rng.uniform(-0.1, 0.1)), 3)
    buy_vol = int(total_vol * (0.5 + delta * 0.5))
    sell_vol = int(total_vol * (0.5 - delta * 0.5))
    tape, times = [], [2,5,8,12,17,23,31,42,55,67,82,95]
    for t in times:
        side = "BUY" if rng.random() < 0.5 + delta * 0.4 else "SELL"
        price = round(current_price * (1 + float(rng.uniform(-0.003, 0.003))), 2)
        mult = float(rng.uniform(0.5, 4.5))
        size = int(avg_vol * mult * 0.01)
        etype = "SWEEP" if mult > 3.0 else "BLOCK" if mult > 2.0 else "PRINT"
        ts = (datetime.utcnow() - timedelta(minutes=t)).strftime("%H:%M")
        tape.append({"time":ts,"side":side,"price":price,"size":size,"type":etype})
    signals = []
    if delta > 0.15:
        signals.append({"label":"Aggressive Buying","bullish":True,"desc":f"Buy delta {delta*100:.1f}% — buyers lifting the offer. Sustained near-term bullish pressure."})
    elif delta < -0.15:
        signals.append({"label":"Aggressive Selling","bullish":False,"desc":f"Sell delta {delta*100:.1f}% — sellers hitting the bid. Watch for breakdown."})
    else:
        signals.append({"label":"Balanced Flow","bullish":True,"desc":"Delta near neutral. Wait for directional conviction spike."})
    if float(rng.random()) > 0.6:
        signals.append({"label":"Absorption Detected","bullish":trend=="Uptrend","desc":"Large limit orders absorbing flow near current level — possible institutional defence."})
    if float(rng.random()) > 0.7:
        signals.append({"label":"Order Book Imbalance","bullish":bool(rng.random()>0.5),"desc":"Significant bid/ask imbalance. Stacked orders may act as magnet or barrier."})
    summary = (f"Order flow {trend.lower()}: delta {delta*100:+.1f}%. "
               f"{'Buy pressure dominant.' if delta > 0 else 'Sell pressure elevated.'} "
               f"Session vol {total_vol/1e6:.1f}M. ⚠ Simulated from price/volume — live flow requires L2 feed.")
    return {"of_delta":delta,"of_buy_vol":buy_vol,"of_sell_vol":sell_vol,"of_tape":tape,"of_signals":signals,"of_summary":summary}

def simulate_options_flow(current_price, sigma, trend, ticker):
    rng = np.random.default_rng(99)
    iv = round(sigma * np.sqrt(252) * float(rng.uniform(0.9,1.3)) * 100, 1)
    hv = round(sigma * np.sqrt(252) * 100, 1)
    pcr = float(rng.uniform(1.1,1.7) if trend=="Downtrend" else rng.uniform(0.5,0.9) if trend=="Uptrend" else rng.uniform(0.8,1.2))
    exps = ["Jun 6","Jun 13","Jun 20","Jul 18","Aug 15","Jan 2027"]
    flow = []
    for i, t in enumerate([3,7,14,22,35,48,60,75]):
        is_call = bool(rng.random() < (0.6 if trend=="Uptrend" else 0.4))
        strike = round(current_price * float(rng.choice([0.90,0.95,1.0,1.05,1.10,1.15])), 0)
        exec_type = "SWEEP" if float(rng.random()) > 0.55 else "BLOCK"
        contracts = int(rng.integers(200,8000))
        prem = round(contracts * float(rng.uniform(0.5,12)) * 100 / 1000, 0)
        oi = int(rng.integers(500,50000))
        ts = (datetime.utcnow()-timedelta(minutes=t)).strftime("%H:%M")
        flow.append({"time":ts,"expiry":exps[i%len(exps)],"strike":strike,
                     "type":"CALL" if is_call else "PUT","exec":exec_type,
                     "premium":f"{int(prem)}K","oi":oi,
                     "sentiment":"BULLISH" if is_call else "BEARISH"})
    max_pain = round(current_price * float(rng.uniform(0.92,1.05)), 2)
    gex = round(float(rng.uniform(-2.5,3.5)), 1)
    calls = sum(1 for f in flow if f["type"]=="CALL")
    puts  = sum(1 for f in flow if f["type"]=="PUT")
    sweeps = sum(1 for f in flow if f["exec"]=="SWEEP")
    summary = (f"Options: {calls} calls vs {puts} puts, {sweeps} sweeps. "
               f"PCR {pcr:.2f} — {'bearish hedging dominant' if pcr>1 else 'bullish positioning'}. "
               f"IV {iv:.1f}% vs HV {hv:.1f}% — premiums {'rich, mean-reversion edge' if iv>hv else 'cheap relative to moves'}. "
               f"Max pain ${max_pain}. GEX {gex:+}B {'suppresses' if gex>0 else 'amplifies'} volatility. "
               f"⚠ Simulated data.")
    return {"opt_flow":flow,"put_call_ratio":round(pcr,2),"iv":iv,"hv":hv,
            "max_pain":max_pain,"gex":gex,"opt_summary":summary}

# ── ROUTES ─────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.get("/price/{ticker}")
def get_price(ticker: str):
    try:
        df = yf.download(ticker, period="2d", progress=False)
        if df is None or df.empty:
            return {"error": "No data"}
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        return {"price": round(float(close.iloc[-1]), 2)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/correlation")
def correlation(tickers: str):
    try:
        tkrs = [t.strip().upper() for t in tickers.split(",") if t.strip()]
        prices = {}
        for t in tkrs:
            df = yf.download(t, period="3mo", progress=False)
            if df is None or df.empty:
                continue
            close = df["Close"]
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            prices[t] = close.pct_change().dropna()
        if len(prices) < 2:
            return {"error": "Need at least 2 valid tickers"}
        price_df = pd.DataFrame(prices).dropna()
        corr = price_df.corr()
        tickers_out = list(corr.columns)
        matrix = [[round(float(corr.iloc[i,j]), 2) for j in range(len(tickers_out))] for i in range(len(tickers_out))]
        return {"tickers": tickers_out, "matrix": matrix}
    except Exception as e:
        return {"error": str(e)}

@app.get("/forecast/{ticker}")
def forecast(ticker: str):
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df is None or df.empty:
            return {"error": f"No data for {ticker}"}

        close = df["Close"].copy()
        volume = df["Volume"].copy()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:,0]
        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:,0]

        current_price = float(close.iloc[-1])
        prev_price    = float(close.iloc[-2]) if len(close)>1 else current_price
        change_1d_pct = round((current_price - prev_price)/prev_price*100, 2)

        high_52w      = float(close.max())
        low_52w       = float(close.min())
        from_high_52w = round((current_price - high_52w)/high_52w*100, 2)

        returns    = close.pct_change().dropna()
        volatility = round(float(returns.std()*100), 2)

        ema20_s = close.ewm(span=20, adjust=False).mean()
        ema50_s = close.ewm(span=50, adjust=False).mean()
        ema20   = round(float(ema20_s.iloc[-1]), 2)
        ema50   = round(float(ema50_s.iloc[-1]), 2)
        trend   = "Uptrend" if ema20>ema50 else "Downtrend" if ema20<ema50 else "Sideways"

        rsi14  = compute_rsi(close)

        # MACD
        macd_line, signal_line, macd_hist = compute_macd(close)
        macd_val    = round(float(macd_line.iloc[-1]), 3)
        macd_sig    = round(float(signal_line.iloc[-1]), 3)

        # Bollinger
        bb_u, bb_m, bb_l = compute_bollinger(close)
        bb_upper = round(float(bb_u.iloc[-1]), 2)
        bb_mid   = round(float(bb_m.iloc[-1]), 2)
        bb_lower = round(float(bb_l.iloc[-1]), 2)
        bb_width = round(float(((bb_u - bb_l)/bb_m * 100).iloc[-1]), 2)

        # Forecasts
        mu    = float(returns.mean())
        sigma = float(returns.std())
        days  = 30
        paths = monte_carlo_paths(current_price, mu, sigma, days=days, n_paths=500)
        p10   = float(np.percentile(paths[-1], 10))
        p50   = float(np.percentile(paths[-1], 50))
        p90   = float(np.percentile(paths[-1], 90))
        bull  = round((p90/current_price-1)*100, 2)
        base  = round((p50/current_price-1)*100, 2)
        bear  = round((p10/current_price-1)*100, 2)

        risk_score = min(100, round(volatility*2, 2))
        confidence = max(20, min(95, int(100-volatility)))

        forecast_7d  = round(current_price*(1+mu*7), 2)
        forecast_30d = round(current_price*(1+mu*30), 2)

        # Support / Resistance
        resistance_levels, support_levels = get_support_resistance(close)

        # Volume profile
        vol_profile = get_volume_profile(close, volume)

        # History slice (last 120 days)
        sl     = df.iloc[-120:]
        sl_c   = sl["Close"]
        if isinstance(sl_c, pd.DataFrame): sl_c = sl_c.iloc[:,0]

        history_dates  = [d.strftime("%b %d") for d in sl.index]
        history_prices = [round(float(p),2) for p in sl_c]
        ema20_list     = [round(float(v),2) for v in ema20_s.iloc[-120:]]
        ema50_list     = [round(float(v),2) for v in ema50_s.iloc[-120:]]

        # BB series
        bb_series = {
            "upper": [round(float(v),2) if not np.isnan(v) else None for v in bb_u.iloc[-120:]],
            "mid":   [round(float(v),2) if not np.isnan(v) else None for v in bb_m.iloc[-120:]],
            "lower": [round(float(v),2) if not np.isnan(v) else None for v in bb_l.iloc[-120:]],
        }

        # MACD series
        macd_series = {
            "macd":   [round(float(v),4) if not np.isnan(v) else None for v in macd_line.iloc[-120:]],
            "signal": [round(float(v),4) if not np.isnan(v) else None for v in signal_line.iloc[-120:]],
            "hist":   [round(float(v),4) if not np.isnan(v) else None for v in macd_hist.iloc[-120:]],
        }

        last_date      = df.index[-1]
        forecast_dates = [(last_date+timedelta(days=i+1)).strftime("%b %d") for i in range(days)]
        forecast_median= [round(float(x),2) for x in np.percentile(paths, 50, axis=1)]
        forecast_p10   = [round(float(x),2) for x in np.percentile(paths, 10, axis=1)]
        forecast_p90   = [round(float(x),2) for x in np.percentile(paths, 90, axis=1)]

        # Earnings
        earnings_date = None
        earnings_surprise = None
        try:
            info = yf.Ticker(ticker).calendar
            if info is not None and not info.empty:
                ed = info.columns[0] if hasattr(info, 'columns') else None
                if ed:
                    earnings_date = str(ed)[:10]
        except Exception:
            pass

        # News + sentiment
        news, news_sentiment_avg = simulate_news_sentiment(ticker, trend)

        sector_context = (
            f"{ticker.upper()} operates in a market currently showing {trend.lower()} momentum. "
            f"Broader sector sentiment {'aligns with' if trend!='Downtrend' else 'contradicts'} recent price action. "
            f"Volatility at {volatility}% suggests {'elevated' if volatility>3 else 'moderate'} near-term risk."
        )
        news_insight = (
            f"News sentiment score {news_sentiment_avg:+} reflects {'positive' if news_sentiment_avg>5 else 'negative' if news_sentiment_avg<-5 else 'neutral'} "
            f"market narrative for {ticker.upper()}. "
            f"{'Bullish catalysts dominate recent headlines.' if news_sentiment_avg>10 else 'Bearish headlines elevated — monitor for continuation.' if news_sentiment_avg<-10 else 'Mixed signals — await clearer directional catalyst.'}"
        )

        # Order flow + Options flow
        of_data  = simulate_order_flow(current_price, returns, volume, trend)
        opt_data = simulate_options_flow(current_price, sigma, trend, ticker)

        # Explanation
        explanation = (
            f"Trend: {trend} (EMA20 ${ema20} / EMA50 ${ema50}). "
            f"RSI {rsi14} — {'overbought, watch for pullback' if rsi14>70 else 'oversold, potential bounce' if rsi14<30 else 'neutral'}. "
            f"MACD {macd_val} vs signal {macd_sig} — {'bullish crossover' if macd_val>macd_sig else 'bearish crossover'}. "
            f"Price {'above' if current_price>bb_upper else 'below' if current_price<bb_lower else 'within'} Bollinger Bands. "
            f"Monte Carlo 30d: base {base:+}%, bull {bull:+}%, bear {bear:+}%. "
            f"Confidence {confidence}% based on {volatility}% daily volatility."
        )

        return {
            "ticker": ticker.upper(),
            "current_price": round(current_price,2),
            "change_1d_pct": change_1d_pct,
            "high_52w": round(high_52w,2), "low_52w": round(low_52w,2),
            "from_high_52w": from_high_52w,
            "trend": trend, "ema20": ema20, "ema50": ema50,
            "rsi14": rsi14,
            "macd_val": macd_val, "macd_signal": macd_sig,
            "bb_upper": bb_upper, "bb_mid": bb_mid, "bb_lower": bb_lower, "bb_width": bb_width,
            "volatility": volatility, "risk_score": risk_score, "confidence": confidence,
            "forecast_7d": forecast_7d, "forecast_30d": forecast_30d,
            "bull": bull, "base": base, "bear": bear,
            "support_levels": support_levels, "resistance_levels": resistance_levels,
            "vol_profile": vol_profile,
            "earnings_date": earnings_date, "earnings_surprise": earnings_surprise,
            "explanation": explanation,
            "history_dates": history_dates, "history_prices": history_prices,
            "ema20_series": ema20_list, "ema50_series": ema50_list,
            "bb_series": bb_series, "macd_series": macd_series,
            "forecast_dates": forecast_dates,
            "forecast_median": forecast_median, "forecast_p10": forecast_p10, "forecast_p90": forecast_p90,
            "news": news, "news_sentiment_avg": news_sentiment_avg,
            "sector_context": sector_context, "news_insight": news_insight,
            **of_data, **opt_data
        }
    except Exception as e:
        import traceback
        return {"error": str(e) + "\n" + traceback.format_exc()}

@app.get("/ohlcv/{ticker}")
def ohlcv(ticker: str, period: str = "3mo", interval: str = "1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df is None or df.empty:
            return {"error": "No data"}
        df = df.reset_index()
        ts_col = "Datetime" if "Datetime" in df.columns else "Date"
        close  = df["Close"];  close  = close.iloc[:,0]  if isinstance(close,  pd.DataFrame) else close
        open_  = df["Open"];   open_  = open_.iloc[:,0]  if isinstance(open_,  pd.DataFrame) else open_
        high   = df["High"];   high   = high.iloc[:,0]   if isinstance(high,   pd.DataFrame) else high
        low    = df["Low"];    low    = low.iloc[:,0]    if isinstance(low,    pd.DataFrame) else low
        fmt = "%b %d %H:%M" if interval in ("1h","30m","15m") else "%b %d"
        dates = [d.strftime(fmt) for d in df[ts_col]]
        return {
            "dates":  dates,
            "open":   [round(float(v),2) for v in open_],
            "high":   [round(float(v),2) for v in high],
            "low":    [round(float(v),2) for v in low],
            "close":  [round(float(v),2) for v in close],
        }
    except Exception as e:
        return {"error": str(e)}


def watchlist():
    universe = [
        ("AAPL","Mega-cap Tech"),("MSFT","Cloud/AI"),("NVDA","AI/Semis"),
        ("TSLA","EV/Growth"),("AMZN","E-Commerce"),("META","Social/Ads"),
        ("GOOGL","Search/Cloud"),("JPM","Financials"),("XOM","Energy"),("AMD","Chips/AI")
    ]
    results = []
    for ticker, theme in universe:
        df = yf.download(ticker, period="3mo", progress=False)
        if df is None or df.empty: continue
        close = df["Close"].copy()
        if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
        if len(close) < 21: continue
        current_price = float(close.iloc[-1])
        rets = close.pct_change().dropna()
        vol  = float(rets.std()*100)
        ret_1m = float((close.iloc[-1]/close.iloc[-21]-1)*100)
        rsi  = compute_rsi(close)
        if ret_1m>10 and vol>2:     reason = "Strong momentum + elevated volatility; continuation or reversal watch."
        elif ret_1m<-8:             reason = "Drawdown candidate; rebound possible if macro stabilises."
        elif vol>3:                 reason = "High volatility; strong reaction to macro/sector catalysts likely."
        else:                       reason = "Stable benchmark name; moderate moves, low noise."
        results.append({"ticker":ticker,"theme":theme,"current_price":round(current_price,2),
                        "return_1m":round(ret_1m,2),"volatility":round(vol,2),"rsi":rsi,"reason":reason})
    if not results: return {"error":"No data"}
    results.sort(key=lambda x:(abs(x["return_1m"]),x["volatility"]),reverse=True)
    week_summary = ("Focus on names with strong recent moves and sensitivity to macro headlines. "
                    "Watchlist ranked by absolute 1M return and volatility. Cross-check with current events.")
    return {"week_summary":week_summary,"stocks":results[:5]}
