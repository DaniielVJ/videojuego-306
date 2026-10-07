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

  /* ─────────────────────────────────────────
     MOSTRAR / OCULTAR CONTRASEÑA
     ───────────────────────────────────────── */
  const passwordInputs = document.querySelectorAll('input[type="password"]');
  
  const iconOpen = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:1.5rem; height:1.5rem;"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`;
  const iconClosed = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:1.5rem; height:1.5rem;"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" /></svg>`;

  passwordInputs.forEach(input => {
    // Wrapper para alinear perfectamente el ícono sin depender de la altura del label
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    wrapper.style.width = '100%';
    
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    // Añadir padding para que el texto no pise el ícono
    input.style.width = '100%';
    input.style.paddingRight = '2.5rem';

    // Crear botón del ojito
    const eyeBtn = document.createElement('button');
    eyeBtn.type = 'button';
    eyeBtn.className = 'toggle-password-btn';
    eyeBtn.innerHTML = iconOpen; 
    eyeBtn.title = 'Mostrar contraseña';
    
    // Insertarlo justo después del input dentro del wrapper
    wrapper.appendChild(eyeBtn);

    eyeBtn.addEventListener('click', () => {
      if (input.type === 'password') {
        input.type = 'text';
        eyeBtn.innerHTML = iconClosed; 
        eyeBtn.title = 'Ocultar contraseña';
      } else {
        input.type = 'password';
        eyeBtn.innerHTML = iconOpen; 
        eyeBtn.title = 'Mostrar contraseña';
      }
    });
  });

})();
