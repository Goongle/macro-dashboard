"""macro-dashboard 카드 9종 생성기.

좁은 Notion 카드(실측 193x320)에서 TradingView 가격축이 잘리는 문제를 해결하기 위해
상단 시세·하단 차트를 각각 고정 폭으로 렌더한 뒤 transform: scale()로 축소한다.
차트를 CHART_W(px)로 그린 뒤 줄이므로, 폭이 좁아져도 축 숫자가 통째로 남는다.
"""

import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

QUOTE_W = 340    # single-quote 위젯이 시세를 숨기지 않는 최소 폭
CHART_W = 250    # 가격축이 온전히 나오는 최소 폭 (193px에서는 잘림)

# (파일명, 제목, 심볼, range)
# range=None 은 advanced-chart에 range를 넘기지 않는다는 뜻.
# FRED 시리즈는 range를 주면 TradingView가 일봉보다 작은 인터벌을 잡으려다
# "인터벌은 지원되지 않습니다"로 깨진다. 그래서 금리 2개만 range를 뺀다.
CARDS = [
    ("sp500",  "S&P 500",       "FOREXCOM:SPXUSD", "1M"),
    ("nasdaq", "NASDAQ 100",    "FOREXCOM:NSXUSD", "1M"),
    ("tv2y",   "미국 2Y 금리",   "FRED:DGS2",       None),
    ("tv10y",  "미국 10Y 금리",  "FRED:DGS10",      None),
    ("gold",   "금",            "OANDA:XAUUSD",    "1M"),
    ("silver", "은",            "OANDA:XAGUSD",    "1M"),
    ("wti",    "WTI 원유",      "TVC:USOIL",       "1M"),
    ("dxy",    "달러 인덱스",    "CAPITALCOM:DXY",  "1M"),
    ("usdkrw", "USD/KRW",       "FX_IDC:USDKRW",   "1M"),
]

TEMPLATE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>
*{{box-sizing:border-box}}
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#fff;font-family:Arial,sans-serif}}
.card{{height:100%;display:flex;flex-direction:column;border:1px solid #e5e7eb;background:#fff}}
.clip{{position:relative;overflow:hidden}}
.scale{{position:absolute;top:0;left:0;transform-origin:0 0}}
.quote-clip{{flex:0 0 72px;border-bottom:1px solid #f1f3f5}}
.quote-scale{{width:{qw}px;height:112px}}
.chart-clip{{flex:1;min-height:100px}}
.chart-scale{{width:{cw}px;height:100%}}
.scale>div,.scale>div>div{{width:100%;height:100%}}
</style></head><body>
<div class="card">
<div class="clip quote-clip" id="qc"><div class="scale quote-scale" id="qs">
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script src="https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js" async>\
{{"symbol":"{symbol}","width":"100%","isTransparent":true,"colorTheme":"light","locale":"kr"}}</script>
</div></div></div>
<div class="clip chart-clip" id="cc"><div class="scale chart-scale" id="cs">
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>\
{{"autosize":true,"symbol":"{symbol}","interval":"D",{range}"timezone":"Asia/Seoul",\
"theme":"light","style":"2","locale":"kr","backgroundColor":"rgba(255, 255, 255, 1)",\
"gridColor":"rgba(240, 243, 250, 0.35)","hide_top_toolbar":true,"hide_side_toolbar":true,\
"hide_legend":true,"save_image":false,"calendar":false,"hide_volume":true,\
"support_host":"https://www.tradingview.com"}}</script>
</div></div></div>
</div>
<script>
function fit(){{
  var qc=document.getElementById('qc'),qs=document.getElementById('qs');
  var q=Math.min(1,qc.clientWidth/{qw});
  qs.style.transform='scale('+q+')';
  qc.style.flexBasis=Math.ceil(112*q)+'px';
  var cc=document.getElementById('cc'),cs=document.getElementById('cs');
  var c=Math.min(1,cc.clientWidth/{cw});
  cs.style.transform='scale('+c+')';
  // 축소한 만큼 내부 높이를 키워야 세로가 카드에 꽉 찬다
  cs.style.height=Math.ceil(cc.clientHeight/c)+'px';
}}
fit();
addEventListener('resize',fit);
// 위젯이 늦게 뜨면 컨테이너 크기가 바뀌므로 한 번 더 맞춘다
addEventListener('load',fit);
setTimeout(fit,1200);
</script></body></html>
"""

INDEX = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Macro Dashboard</title><style>
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;width:100%;height:100%;background:#fff;font-family:Arial,sans-serif}}
body{{padding:4px}}
.grid{{height:100vh;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
grid-template-rows:repeat(3,minmax(0,1fr));gap:6px}}
.cell{{min-width:0;min-height:0;display:flex;flex-direction:column}}
.cell h2{{margin:0 0 3px;font-size:12px;font-weight:700;color:#374151;white-space:nowrap}}
.cell iframe{{flex:1;width:100%;border:0}}
@media(max-width:600px){{
html,body{{height:auto}}
.grid{{height:auto;grid-template-columns:1fr;grid-template-rows:none}}
.cell{{height:240px}}
}}
</style></head><body><div class="grid">
{cells}
</div></body></html>
"""


def main():
    for name, title, symbol, rng in CARDS:
        html = TEMPLATE.format(title=title, symbol=symbol, qw=QUOTE_W, cw=CHART_W,
                               range=f'"range":"{rng}",' if rng else "")
        with open(os.path.join(OUT, f"{name}.html"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(html)

    cells = "\n".join(
        f'<div class="cell"><h2>{title}</h2>'
        f'<iframe src="{name}.html" title="{title}"></iframe></div>'
        for name, title, _, _ in CARDS)
    with open(os.path.join(OUT, "index.html"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write(INDEX.format(cells=cells))

    print(f"generated {len(CARDS)} cards + index.html -> {OUT}")


if __name__ == "__main__":
    main()
