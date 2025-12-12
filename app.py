from flask import Flask, render_template_string

app = Flask(__name__)

SNAKE_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Virtual Arcade - Snake</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; }
    .wrap { max-width: 900px; margin: 0 auto; }
    canvas { border: 2px solid #222; border-radius: 12px; background: #f5f5f5; display:block; }
    .row { display:flex; gap: 12px; flex-wrap: wrap; align-items:center; margin: 12px 0; }
    .stat { padding: 8px 10px; border: 1px solid #ddd; border-radius: 10px; background:#fff; }
    button { padding: 10px 14px; cursor:pointer; }
    .hint { color:#555; margin-top: 8px; }
  </style>
</head>
<body>
<div class="wrap">
  <h1 style="margin:0;">🐍 Virtual Arcade — Snake</h1>

  <div class="row">
    <button id="startBtn">Start / Restart</button>
    <div class="stat">Score: <b id="score">0</b></div>
    <div class="stat">High Score: <b id="highScore">0</b></div>
    <div class="stat">Speed: <b id="speed">8</b> ticks/s</div>
  </div>

  <canvas id="c" width="600" height="600"></canvas>

  <div class="hint">
    Controls: Arrow Keys or WASD. Eat apples to grow. Don’t hit walls or yourself.
  </div>
</div>

<script>
  const canvas = document.getElementById("c");
  const ctx = canvas.getContext("2d");

  const scoreEl = document.getElementById("score");
  const highScoreEl = document.getElementById("highScore");
  const speedEl = document.getElementById("speed");
  const startBtn = document.getElementById("startBtn");

  const GRID = 20;
  const TILE = canvas.width / GRID;

  let tickRate = 8;
  let tickMs = 1000 / tickRate;

  let snake, dir, nextDir, apple, score, highScore, alive, timer;

  function loadHighScore() {
    const v = parseInt(localStorage.getItem("snake_highscore") || "0", 10);
    return isNaN(v) ? 0 : v;
  }
  function saveHighScore(v) { localStorage.setItem("snake_highscore", String(v)); }

  function reset() {
    snake = [{x: 10, y: 10}, {x: 9, y: 10}, {x: 8, y: 10}];
    dir = {x: 1, y: 0};
    nextDir = {x: 1, y: 0};
    score = 0;
    alive = true;
    tickRate = 8;
    tickMs = 1000 / tickRate;
    apple = spawnApple();
    updateUI();
    draw();
  }

  function updateUI() {
    scoreEl.textContent = score;
    highScoreEl.textContent = highScore;
    speedEl.textContent = tickRate;
  }

  function spawnApple() {
    while (true) {
      const a = { x: Math.floor(Math.random() * GRID), y: Math.floor(Math.random() * GRID) };
      const onSnake = snake.some(s => s.x === a.x && s.y === a.y);
      if (!onSnake) return a;
    }
  }

  function setSpeedFromScore() {
    const newRate = Math.min(16, 8 + Math.floor(score / 4));
    if (newRate !== tickRate) {
      tickRate = newRate;
      tickMs = 1000 / tickRate;
      updateUI();
      if (timer) {
        clearInterval(timer);
        timer = setInterval(tick, tickMs);
      }
    }
  }

  function tick() {
    if (!alive) return;
    dir = nextDir;

    const head = snake[0];
    const newHead = { x: head.x + dir.x, y: head.y + dir.y };

    if (newHead.x < 0 || newHead.x >= GRID || newHead.y < 0 || newHead.y >= GRID) { gameOver(); return; }
    if (snake.some(seg => seg.x === newHead.x && seg.y === newHead.y)) { gameOver(); return; }

    snake.unshift(newHead);

    if (newHead.x === apple.x && newHead.y === apple.y) {
      score += 1;
      if (score > highScore) { highScore = score; saveHighScore(highScore); }
      apple = spawnApple();
      setSpeedFromScore();
    } else {
      snake.pop();
    }

    updateUI();
    draw();
  }

  function gameOver() {
    alive = false;
    draw(true);
  }

  function draw(isGameOver=false) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // grid
    ctx.globalAlpha = 0.12;
    for (let i = 0; i <= GRID; i++) {
      ctx.beginPath(); ctx.moveTo(i * TILE, 0); ctx.lineTo(i * TILE, canvas.height); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, i * TILE); ctx.lineTo(canvas.width, i * TILE); ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // apple
    ctx.fillStyle = "#e53935";
    ctx.beginPath();
    ctx.arc((apple.x + 0.5) * TILE, (apple.y + 0.5) * TILE, TILE * 0.35, 0, Math.PI * 2);
    ctx.fill();

    // snake
    ctx.fillStyle = "#111";
    snake.forEach((seg, i) => {
      ctx.fillRect(seg.x * TILE + 2, seg.y * TILE + 2, TILE - 4, TILE - 4);
      if (i === 0) {
        ctx.globalAlpha = 0.9;
        ctx.fillStyle = "#fff";
        ctx.fillRect(seg.x * TILE + TILE * 0.65, seg.y * TILE + TILE * 0.25, 4, 4);
        ctx.fillRect(seg.x * TILE + TILE * 0.65, seg.y * TILE + TILE * 0.55, 4, 4);
        ctx.globalAlpha = 1;
        ctx.fillStyle = "#111";
      }
    });

    if (isGameOver) {
      ctx.globalAlpha = 0.85;
      ctx.fillStyle = "#000";
      ctx.fillRect(0, canvas.height/2 - 55, canvas.width, 110);
      ctx.globalAlpha = 1;
      ctx.fillStyle = "#fff";
      ctx.textAlign = "center";
      ctx.font = "bold 34px system-ui";
      ctx.fillText("Game Over", canvas.width/2, canvas.height/2 - 8);
      ctx.font = "18px system-ui";
      ctx.fillText("Press Start / Restart", canvas.width/2, canvas.height/2 + 26);
      ctx.fillStyle = "#111";
    }
  }

  function trySetDir(dx, dy) {
    if (dx === -dir.x && dy === -dir.y) return;
    nextDir = {x: dx, y: dy};
  }

  document.addEventListener("keydown", (e) => {
    const k = e.key.toLowerCase();
    if (k === "arrowup" || k === "w") trySetDir(0, -1);
    else if (k === "arrowdown" || k === "s") trySetDir(0, 1);
    else if (k === "arrowleft" || k === "a") trySetDir(-1, 0);
    else if (k === "arrowright" || k === "d") trySetDir(1, 0);
  });

  startBtn.addEventListener("click", () => {
    if (timer) clearInterval(timer);
    reset();
    timer = setInterval(tick, tickMs);
  });

  highScore = loadHighScore();
  reset();
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(SNAKE_HTML)
