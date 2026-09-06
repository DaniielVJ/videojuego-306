/* =============================================
   EPIC WARCRAFT INICIO PAGE — inicio.js
   Canvas: partículas de cenizas/fuego (embers)
   ============================================= */

(function () {
  'use strict';

  const canvas = document.getElementById('bgCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');

  const PX = 4; // Tamaño base partículas

  /* ─────────────────────────────────────────
     CENIZAS / BRASAS (Embers)
     ───────────────────────────────────────── */
  class Ember {
    constructor() {
      this.reset(true);
    }

    reset(init = false) {
      const W = canvas.width, H = canvas.height;
      this.x     = Math.random() * W;
      this.y     = init ? Math.random() * H : H + 10;
      this.vy    = -0.5 - Math.random() * 1.5;      
      this.sway  = (Math.random() - 0.5) * 0.03;   
      this.swayPhase = Math.random() * Math.PI * 2;
      this.swayAmp   = 0.5 + Math.random() * 2;

      const colors = ['#ff4500', '#ff8c00', '#ff3300', '#ff6600']; // Fuego/Ceniza
      this.color   = colors[Math.floor(Math.random() * colors.length)];
      
      this.size  = 0.5 + Math.random() * 0.8;
      this.baseAlpha = 0.5 + Math.random() * 0.5;
      this.pulsePhase = Math.random() * Math.PI * 2;
      this.pulseSpeed = 0.05 + Math.random() * 0.05;
    }

    update(t) {
      this.swayPhase += this.sway;
      this.x += Math.sin(this.swayPhase) * this.swayAmp;
      this.y += this.vy;
      this.pulsePhase += this.pulseSpeed;

      if (this.y < -20) this.reset();
      if (this.x < -20 || this.x > canvas.width + 20) this.reset();
    }

    draw() {
      const ps = this.size * PX;
      const currentAlpha = this.baseAlpha * (0.4 + 0.6 * Math.sin(this.pulsePhase));

      ctx.save();
      ctx.translate(this.x, this.y);
      
      // Resplandor
      ctx.globalAlpha = currentAlpha * 0.4;
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.arc(0, 0, ps * 2.5, 0, Math.PI*2);
      ctx.fill();

      // Centro brillante
      ctx.globalAlpha = currentAlpha;
      ctx.fillStyle = '#ffccaa';
      ctx.beginPath();
      ctx.arc(0, 0, ps, 0, Math.PI*2);
      ctx.fill();

      ctx.restore();
    }
  }

  const NUM_EMBERS = 120;
  const embers = Array.from({ length: NUM_EMBERS }, () => new Ember());

  /* ─────────────────────────────────────────
     LOOP PRINCIPAL
     ───────────────────────────────────────── */
  function draw(timestamp = 0) {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    for (const ember of embers) {
      ember.update(timestamp);
      ember.draw();
    }

    requestAnimationFrame(draw);
  }

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(draw);

})();
