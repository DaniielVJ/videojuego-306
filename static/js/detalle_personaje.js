/* ===================================================
   DETALLE_PERSONAJE.JS — MOTOR DE FICHA DEL HÉROE
   World of Warcraft / Dark Fantasy RPG Engine
   =================================================== */

(function () {
  'use strict';

  /* ─────────────────────────────────────────
     1. MOTOR DE BRASAS / CENIZAS (Canvas 60 FPS)
     ───────────────────────────────────────── */
  const canvas = document.getElementById('bgCanvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    const PX = 4; // Tamaño base del pixel de brasa

    class Ember {
      constructor() {
        this.reset(true);
      }

      reset(init = false) {
        const W = canvas.width, H = canvas.height;
        this.x = Math.random() * W;
        this.y = init ? Math.random() * H : H + 10;
        this.vy = -0.5 - Math.random() * 1.5;
        this.sway = (Math.random() - 0.5) * 0.03;
        this.swayPhase = Math.random() * Math.PI * 2;
        this.swayAmp = 0.5 + Math.random() * 2;

        const colors = ['#ff4500', '#ff8c00', '#ff3300', '#ffaa00'];
        this.color = colors[Math.floor(Math.random() * colors.length)];

        this.size = 0.5 + Math.random() * 0.8;
        this.baseAlpha = 0.4 + Math.random() * 0.5;
        this.pulsePhase = Math.random() * Math.PI * 2;
        this.pulseSpeed = 0.05 + Math.random() * 0.05;
      }

      update() {
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
        ctx.globalAlpha = currentAlpha * 0.4;
        ctx.fillStyle = this.color;
        ctx.fillRect(-ps * 1.5, -ps * 1.5, ps * 3, ps * 3);

        ctx.globalAlpha = currentAlpha;
        ctx.fillRect(-ps / 2, -ps / 2, ps, ps);
        ctx.restore();
      }
    }

    let embers = [];
    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const count = Math.floor((canvas.width * canvas.height) / 22000);
      embers = Array.from({ length: Math.min(count, 55) }, () => new Ember());
    }

    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 100);
    });
    resize();

    function loop() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < embers.length; i++) {
        embers[i].update();
        embers[i].draw();
      }
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  /* ─────────────────────────────────────────
     2. GESTIÓN DE LA FICHA TÁCTICA
     ───────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    
    /* 2.1 Animar Barra de Experiencia */
    const expTrack = document.getElementById('heroExpTrack');
    const expFill = document.getElementById('heroExpFill');
    if (expTrack && expFill) {
      const current = parseFloat(expTrack.dataset.current) || 0;
      const max = parseFloat(expTrack.dataset.max) || 100;
      let pct = max > 0 ? (current / max) * 100 : 0;
      pct = Math.min(Math.max(pct, 0), 100);

      // Leve retardo para que la transición sea visible y gratificante
      setTimeout(() => {
        expFill.style.width = pct.toFixed(1) + '%';
      }, 200);
    }

    /* 2.2 Animar Medidores de Atributos */
    const attrRows = document.querySelectorAll('.attribute-row-card');
    const MAX_ATTR_SCALE = 30; // Escala máxima referencial para el gauge
    attrRows.forEach((row, index) => {
      const fill = row.querySelector('.attr-meter-fill');
      const val = parseFloat(row.dataset.val) || 0;
      if (fill) {
        let pct = (val / MAX_ATTR_SCALE) * 100;
        pct = Math.min(Math.max(pct, 5), 100); // Mínimo 5% visible
        setTimeout(() => {
          fill.style.width = pct.toFixed(1) + '%';
        }, 150 + index * 60);
      }
    });

    /* 2.3 Calcular Peso Total del Arsenal */
    const itemCards = document.querySelectorAll('.item-codex-card');
    let totalWeight = 0;
    itemCards.forEach(card => {
      const peso = parseFloat(card.dataset.peso) || 0;
      totalWeight += peso;
    });

    const weightDisplay = document.getElementById('totalInventoryWeight');
    if (weightDisplay) {
      weightDisplay.textContent = totalWeight.toFixed(1) + ' kg';
    }

    const carryMetric = document.getElementById('metricCarryVal');
    if (carryMetric) {
      carryMetric.textContent = totalWeight.toFixed(1) + ' kg';
    }

    /* 2.4 Modal de Notificación de Edición */
    const btnEditar = document.getElementById('btnEditarHeroe');
    const modalEdit = document.getElementById('modalEditWarning');
    const btnCerrarModal = document.getElementById('btnCerrarModalEdit');

    function openModal() {
      if (!modalEdit) return;
      modalEdit.classList.add('is-active');
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      if (!modalEdit) return;
      modalEdit.classList.remove('is-active');
      document.body.style.overflow = '';
    }

    if (btnEditar) {
      btnEditar.addEventListener('click', (e) => {
        e.preventDefault();
        openModal();
      });
    }

    if (btnCerrarModal) {
      btnCerrarModal.addEventListener('click', closeModal);
    }

    if (modalEdit) {
      modalEdit.addEventListener('click', (e) => {
        if (e.target === modalEdit) {
          closeModal();
        }
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalEdit && modalEdit.classList.contains('is-active')) {
        closeModal();
      }
    });

    // Exponer API pública para integración futura con el backend
    window.HeroDetailEngine = {
      openEditNotice: openModal,
      closeEditNotice: closeModal
    };
  });

})();
