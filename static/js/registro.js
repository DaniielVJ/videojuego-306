/* =============================================
   EPIC WARCRAFT REGISTER PAGE — registro.js
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


  /* ─────────────────────────────────────────
     FORMULARIO REGISTRO Y VALIDACIÓN
     ───────────────────────────────────────── */
  const form = document.getElementById('registerForm');

  if (form) {
    const pass1 = form.querySelector('[name="password1"]');
    const pass2 = form.querySelector('[name="password2"]');

    const validarPasswords = () => {
      if (!pass1 || !pass2) return;
      const wrapper2 = pass2.parentElement;

      if (pass2.value.length > 0 && pass1.value !== pass2.value) {
          wrapper2.classList.add('error-border');
          wrapper2.classList.remove('success-border');
      } else if (pass2.value.length > 0 && pass1.value === pass2.value) {
          wrapper2.classList.remove('error-border');
          wrapper2.classList.add('success-border');
      } else {
          wrapper2.classList.remove('error-border', 'success-border');
      }
    };

    if (pass1 && pass2) {
        pass1.addEventListener('input', validarPasswords);
        pass2.addEventListener('input', validarPasswords);
    }

    form.addEventListener('submit', function (e) {
      const usernameInput = form.querySelector('[name="username"]');
      const emailInput = form.querySelector('[name="email"]');
      
      const user = usernameInput ? usernameInput.value.trim() : '';
      const email = emailInput ? emailInput.value.trim() : '';
      const p1 = pass1 ? pass1.value : '';
      const p2 = pass2 ? pass2.value : '';
    
      if (!user || !email || !p1 || !p2 || (p1 !== p2)) { 
        e.preventDefault();
        shake(form); 
        return; 
      }
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
