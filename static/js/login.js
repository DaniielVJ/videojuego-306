/* =============================================
   PIXEL ART LOGIN PAGE — script.js
   Canvas: escena pixel art + hojas cayendo animadas
   ============================================= */

(function () {
  'use strict';

  const canvas = document.getElementById('bgCanvas');
  const ctx = canvas.getContext('2d');

  /* ── Paleta de colores ───────────────────── */
  const C = {
    skyTop:    '#6a2898',
    skyMid:    '#c060a0',
    skyLow:    '#e07848',
    skyGnd:    '#f0b030',
    gold:      '#f0c030',
    goldDark:  '#c89010',
    goldShadow:'#a07010',
    purple:    '#8030b0',
    purpleDk:  '#5a1a80',
    gray:      '#909090',
    grayDk:    '#606060',
    grayLt:    '#c0c0c0',
    white:     '#e0e0e0',
    treeGreen: '#30c040',
    treeLt:    '#60e050',
    treeDk:    '#1a8020',
    treeTrunk: '#806030',
    treeBark:  '#604020',
    cloud1:    '#e09030',
    cloud2:    '#c07020',
    cloud3:    '#f0b040',
  };

  /* ── Tamaño pixel ────────────────────────── */
  const PX = 6;

  /* ─────────────────────────────────────────
     LUCIÉRNAGAS (Fireflies) — Sistema de partículas
     ───────────────────────────────────────── */

  class Firefly {
    constructor() {
      this.reset(true);
    }

    reset(init = false) {
      const W = canvas.width, H = canvas.height;
      this.x     = Math.random() * W;
      this.y     = init ? Math.random() * H : H + PX * 6;
      this.vy    = -0.3 - Math.random() * 0.6;      // flotan hacia arriba
      this.sway  = (Math.random() - 0.5) * 0.02;   // oscilación lateral lenta
      this.swayPhase = Math.random() * Math.PI * 2;
      this.swayAmp   = 0.5 + Math.random() * 1.5;

      const colors = ['#f0e040', '#d0f040', '#ffd040', '#a0f050'];
      this.color   = colors[Math.floor(Math.random() * colors.length)];
      
      this.size  = 0.5 + Math.random() * 1.0;  // tamaño base del pixel
      this.baseAlpha = 0.4 + Math.random() * 0.6;
      this.pulsePhase = Math.random() * Math.PI * 2;
      this.pulseSpeed = 0.02 + Math.random() * 0.04;
    }

    update(t) {
      this.swayPhase += this.sway;
      this.x += Math.sin(this.swayPhase) * this.swayAmp;
      this.y += this.vy;
      this.pulsePhase += this.pulseSpeed;

      if (this.y < -PX * 5) this.reset();
      if (this.x < -PX * 10 || this.x > canvas.width + PX * 10) this.reset();
    }

    draw() {
      const ps = this.size * PX;
      
      // Pulso brillante
      const currentAlpha = this.baseAlpha * (0.6 + 0.4 * Math.sin(this.pulsePhase));

      ctx.save();
      ctx.translate(this.x, this.y);
      
      // Glow (resplandor)
      ctx.globalAlpha = currentAlpha * 0.3;
      ctx.fillStyle = this.color;
      ctx.fillRect(-ps, -ps, ps*3, ps*3);

      // Núcleo brillante
      ctx.globalAlpha = currentAlpha;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, ps, ps);

      ctx.restore();
    }
  }

  /* Crear luciérnagas */
  const NUM_FIREFLIES = 80;
  const fireflies = Array.from({ length: NUM_FIREFLIES }, () => new Firefly());

  /* ─────────────────────────────────────────
     CIELO DEGRADADO
     ───────────────────────────────────────── */
  function drawSky() {
    const W = canvas.width, H = canvas.height;
    const grad = ctx.createLinearGradient(0, 0, 0, H * 0.72);
    grad.addColorStop(0,    '#6a2898');
    grad.addColorStop(0.18, '#8a3aad');
    grad.addColorStop(0.42, '#c060a0');
    grad.addColorStop(0.62, '#e07848');
    grad.addColorStop(0.80, '#e89828');
    grad.addColorStop(1,    '#f0b030');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    const gndGrad = ctx.createLinearGradient(0, H * 0.70, 0, H);
    gndGrad.addColorStop(0, '#f0b030');
    gndGrad.addColorStop(1, '#e09020');
    ctx.fillStyle = gndGrad;
    ctx.fillRect(0, H * 0.70, W, H);
  }

  /* ─────────────────────────────────────────
     NUBE PIXEL
     ───────────────────────────────────────── */
  function drawCloud(cx, cy, scale = 1) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(scale, scale);

    function cpx(x, y, c, w = 1, h = 1) {
      ctx.fillStyle = c;
      ctx.fillRect(x * PX, y * PX, w * PX, h * PX);
    }

    cpx(-3,  1, C.cloud1, 6, 2);
    cpx(-2,  0, C.cloud3, 4, 1);
    cpx(-1, -1, C.cloud2, 2, 1);
    cpx(-4,  2, C.cloud2, 2, 1);
    cpx( 2,  2, C.cloud1, 2, 1);

    ctx.restore();
  }

  /* ─────────────────────────────────────────
     ÁRBOL BONSAI VERDE
     ───────────────────────────────────────── */
  function drawPixelTree(ox, oy) {
    ctx.save();
    ctx.translate(ox, oy);

    function t(x, y, c, w = 1, h = 1) {
      ctx.fillStyle = c;
      ctx.fillRect(x * PX, y * PX, w * PX, h * PX);
    }

    const treeData = [
      [ 2, -10, 2, 1, C.treeDk   ],
      [ 1,  -9, 4, 1, C.treeGreen],
      [ 0,  -8, 6, 2, C.treeGreen],
      [ 1,  -8, 2, 1, C.treeLt   ],
      [ 3,  -7, 1, 1, C.treeLt   ],
      [-1,  -7, 7, 1, C.treeGreen],
      [ 0,  -6, 6, 1, C.treeDk   ],
      [ 1,  -6, 3, 1, C.treeGreen],
      [-3,  -6, 3, 1, C.treeGreen],
      [-4,  -5, 4, 2, C.treeGreen],
      [-3,  -5, 2, 1, C.treeLt   ],
      [-5,  -4, 5, 1, C.treeDk   ],
      [ 3,  -5, 4, 2, C.treeGreen],
      [ 4,  -5, 2, 1, C.treeLt   ],
      [ 3,  -4, 5, 1, C.treeDk   ],
      [ 1,  -4, 2, 4, C.treeBark ],
      [ 0,  -3, 1, 2, C.treeTrunk],
      [ 3,  -3, 1, 2, C.treeTrunk],
      [ 1,  -2, 1, 1, C.treeTrunk],
    ];

    for (const [x, y, w, h, c] of treeData) t(x, y, c, w, h);
    ctx.restore();
  }

  /* ─────────────────────────────────────────
     MONTAÑA PIXEL
     ───────────────────────────────────────── */
  function drawMountain(ox, oy) {
    ctx.save();
    ctx.translate(ox, oy);

    function m(x, y, c, w = 1, h = 1) {
      ctx.fillStyle = c;
      ctx.fillRect(x * PX, y * PX, w * PX, h * PX);
    }

    const mountain = [
      [ 0, -2, 2, 1, C.gray   ],
      [-1, -1, 4, 1, C.grayDk ],
      [-1, -1, 1, 1, C.grayLt ],
      [-2,  0, 6, 1, C.gray   ],
      [-2,  0, 1, 1, C.grayLt ],
      [-3,  1, 8, 2, C.grayDk ],
      [-3,  1, 1, 1, C.gray   ],
      [ 1,  1, 2, 1, C.white  ],
      [-4,  3,10, 2, C.gray   ],
      [-4,  3, 2, 1, C.grayLt ],
      [ 3,  3, 2, 1, C.grayDk ],
    ];

    for (const [x, y, w, h, c] of mountain) m(x, y, c, w, h);
    ctx.restore();
  }

  /* ─────────────────────────────────────────
     SUELO DECORATIVO
     ───────────────────────────────────────── */
  function drawGroundDecor() {
    const W = canvas.width, H = canvas.height;
    const gndY = H * 0.72;

    for (let i = 0; i < Math.ceil(W / (PX * 5)); i++) {
      const x = i * PX * 5;
      const yVar = (i % 4 === 0) ? -PX : 0;
      const col   = (i % 4 < 2) ? C.gold   : C.purple;
      const colDk = (i % 4 < 2) ? C.goldDark : C.purpleDk;

      ctx.fillStyle = col;
      ctx.fillRect(x, gndY + yVar, PX * 4, PX * 3);
      ctx.fillStyle = colDk;
      ctx.fillRect(x, gndY + yVar + PX * 2, PX * 4, PX);
      ctx.fillStyle = col === C.gold ? '#ffe878' : '#d070f0';
      ctx.fillRect(x + PX, gndY + yVar, PX, PX);
    }

    for (let i = 0; i < 8; i++) {
      const x = i * PX * 6;
      const col = (i % 2 === 0) ? C.gold : C.purple;
      ctx.fillStyle = col;
      ctx.fillRect(x, gndY - PX * 4 + (i % 3) * PX, PX * 5, PX * 4);
      ctx.fillStyle = (i % 2 === 0) ? C.goldShadow : C.purpleDk;
      ctx.fillRect(x, gndY - PX + (i % 3) * PX, PX * 5, PX);
    }

    for (let i = 0; i < 6; i++) {
      const x = W - i * PX * 7 - PX * 3;
      const col = (i % 2 === 0) ? C.purple : C.gold;
      ctx.fillStyle = col;
      ctx.fillRect(x, gndY - PX * 2 + (i % 2) * PX, PX * 6, PX * 3);
      ctx.fillStyle = (i % 2 === 0) ? C.purpleDk : C.goldShadow;
      ctx.fillRect(x, gndY + PX + (i % 2) * PX, PX * 6, PX);
    }
  }

  /* ─────────────────────────────────────────
     ÁRBOL DORADO
     ───────────────────────────────────────── */
  function drawGoldTree(ox, oy, scale = 1) {
    ctx.save();
    ctx.translate(ox, oy);
    ctx.scale(scale, scale);

    function g(x, y, c, w = 1, h = 1) {
      ctx.fillStyle = c;
      ctx.fillRect(x * PX, y * PX, w * PX, h * PX);
    }

    const goldLeaf = '#e0a020', goldLt = '#f0c040',
          goldDk   = '#a07010', trunk  = '#6a4010';

    g(-3, -8, goldDk,   6, 1);
    g(-4, -7, goldLeaf, 8, 2);
    g(-3, -7, goldLt,   3, 1);
    g( 1, -6, goldLt,   2, 1);
    g(-5, -5, goldLeaf,10, 2);
    g(-4, -5, goldLt,   2, 1);
    g( 2, -5, goldLt,   2, 1);
    g(-4, -3, goldDk,   8, 1);
    g(-3, -4, goldLeaf, 6, 1);
    g(-1, -2, trunk,    2, 5);
    g(-2, -1, trunk,    1, 2);
    g( 1, -1, trunk,    1, 2);

    ctx.restore();
  }

  /* ─────────────────────────────────────────
     LOOP PRINCIPAL DE ANIMACIÓN
     ───────────────────────────────────────── */
  let animT = 0;
  let cloudOffset = 0;

  function draw(timestamp = 0) {
    animT = timestamp;
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    // Movimiento de nubes
    cloudOffset -= 0.2;
    if (cloudOffset < -W) cloudOffset += W;

    // 1. Cielo
    drawSky();

    // 2. Nubes (con paralaje horizontal)
    ctx.save();
    
    // Función auxiliar para dibujar nubes y clonarlas para el loop infinito
    function drawCloudLayer(xOffset) {
      drawCloud(W * 0.04 + xOffset, H * 0.06, 1.1);
      drawCloud(W * 0.10 + xOffset, H * 0.12, 0.8);
      drawCloud(W * 0.01 + xOffset, H * 0.17, 0.7);
      drawCloud(W * 0.82 + xOffset, H * 0.07, 0.9);
      drawCloud(W * 0.88 + xOffset, H * 0.14, 0.75);
      drawCloud(W * 0.72 + xOffset, H * 0.10, 1.0);
    }
    
    drawCloudLayer(cloudOffset);
    drawCloudLayer(cloudOffset + W); // Clon para que el bucle sea continuo
    
    ctx.restore();

    // 3. Árboles dorados izquierda
    drawGoldTree(W * 0.05, H * 0.55, 1.0);
    drawGoldTree(W * 0.12, H * 0.60, 1.3);
    drawGoldTree(W * 0.01, H * 0.62, 0.9);

    // 4. Suelo
    drawGroundDecor();

    // 5. Montañas
    drawMountain(W * 0.22, H * 0.78);
    drawMountain(W * 0.14, H * 0.82);

    // 6. Árbol bonsai
    drawPixelTree(W * 0.22, H * 0.72);

    // 7. Árbol dorado derecha
    drawGoldTree(W * 0.88, H * 0.65, 0.85);

    // 8. ✨ Luciérnagas flotando
    ctx.save();
    for (const firefly of fireflies) {
      firefly.update(timestamp);
      firefly.draw();
    }
    ctx.restore();

    requestAnimationFrame(draw);
  }

  /* ─────────────────────────────────────────
     RESIZE
     ───────────────────────────────────────── */
  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(draw);

  /* ─────────────────────────────────────────
     FORMULARIO
     ───────────────────────────────────────── */
  const form = document.getElementById('loginForm');

  if (form) {
    form.addEventListener('submit', function (e) {
      // Buscar los inputs por su atributo "name" es mucho más seguro para Django
      // (ya que Django a veces cambia los IDs a "id_username" o "id_password")
      const usernameInput = form.querySelector('[name="username"]');
      const passwordInput = form.querySelector('[name="password"]');

      const user = usernameInput ? usernameInput.value.trim() : '';
      const pass = passwordInput ? passwordInput.value.trim() : '';
    
    // Si los campos están vacíos, prevenimos el envío a Django y agitamos el formulario
    if (!user || !pass) { 
      e.preventDefault();
      shake(form); 
      return; 
    }
    
    // Si está todo correcto, NO hacemos e.preventDefault()
    // y el formulario hará un POST a tu URL de Django automáticamente.
  });
  } // fin de if(form)

  const registerLink = document.getElementById('registerLink');
  if (registerLink) {
    registerLink.addEventListener('click', function (e) {
      e.preventDefault();
      alert('Redirigiendo a registro... (demo)');
    });
  }

  function shake(el) {
    el.classList.remove('shake');
    void el.offsetWidth;
    el.classList.add('shake');
    el.addEventListener('animationend', () => el.classList.remove('shake'), { once: true });
  }

  const style = document.createElement('style');
  style.textContent = `
    @keyframes shake {
      0%,100% { transform: translateX(0); }
      20%      { transform: translateX(-8px); }
      40%      { transform: translateX(8px); }
      60%      { transform: translateX(-6px); }
      80%      { transform: translateX(6px); }
    }
    .shake { animation: shake 0.45s ease; }
  `;
  document.head.appendChild(style);

})();
