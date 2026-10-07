/* ===================================================
   ACTUALIZAR_PERSONAJE.JS — MOTOR DE EDICIÓN DEL HÉROE
   World of Warcraft / Dark Fantasy RPG Engine
   Manejo de Steppers, Barras Dinámicas y Métricas en Vivo
   =================================================== */

(function () {
  'use strict';

  /* ─────────────────────────────────────────
     1. MOTOR DE BRASAS / CENIZAS (Canvas 60 FPS)
     ───────────────────────────────────────── */
  const canvas = document.getElementById('bgCanvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    const PX = 4;

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
     2. GESTIÓN DE CONTROLES DESBLOQUEADOS
     ───────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    const MAX_ATTR_SCALE = 30; // Escala máxima referencial de la barra de atributo

    /* 2.1 Actualización de Barras de Atributos y Métricas */
    function updateAttrMeter(input) {
      if (!input) return;
      const val = parseFloat(input.value) || 0;
      const card = input.closest('.attr-edit-card');
      if (card) {
        const fill = card.querySelector('.attr-meter-fill');
        if (fill) {
          let pct = (val / MAX_ATTR_SCALE) * 100;
          pct = Math.min(Math.max(pct, 4), 100);
          fill.style.width = pct.toFixed(1) + '%';
        }
      }
      recalculateTacticalMetrics();
    }

    /* 2.2 Recálculo de Métricas Tácticas (Salud, Poder, Magia) */
    function recalculateTacticalMetrics() {
      const inputVigor = document.getElementById('input_vigor');
      const inputFuerza = document.getElementById('input_fuerza');
      const inputIntel = document.getElementById('input_inteligencia');
      const inputNivel = document.getElementById('inputNivel');

      const vigor = inputVigor ? (parseInt(inputVigor.value) || 0) : 10;
      const fuerza = inputFuerza ? (parseInt(inputFuerza.value) || 0) : 0;
      const intel = inputIntel ? (parseInt(inputIntel.value) || 0) : 0;
      const nivel = inputNivel ? (parseInt(inputNivel.value) || 1) : 1;

      // Métricas
      const metricHealth = document.getElementById('metricHealthVal');
      const metricCombat = document.getElementById('metricCombatVal');
      const metricMagic = document.getElementById('metricMagicVal');

      if (metricHealth) {
        // Base de 100 HP + (Vigor * 10)
        metricHealth.textContent = (100 + vigor * 10) + ' PV';
      }
      if (metricCombat) {
        metricCombat.textContent = fuerza + ' PTS';
      }
      if (metricMagic) {
        // Base de 50 Mana + (Intel * 10)
        metricMagic.textContent = (50 + intel * 10) + ' PM';
      }
    }

    /* 2.3 Inicializar Steppers de Atributos (+ / -) */
    document.querySelectorAll('.attr-step-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const action = btn.dataset.action;
        const targetId = btn.dataset.target;
        const input = document.getElementById(targetId);
        if (!input) return;

        let val = parseInt(input.value) || 0;
        const min = parseInt(input.min) || 0;
        const max = parseInt(input.max) || 100;

        if (action === 'increase' && val < max) {
          val++;
        } else if (action === 'decrease' && val > min) {
          val--;
        }

        input.value = val;
        updateAttrMeter(input);
      });
    });

    // Escuchar cambios directos por teclado en los atributos
    document.querySelectorAll('.attr-input-field').forEach(input => {
      input.addEventListener('input', () => updateAttrMeter(input));
      updateAttrMeter(input); // Inicialización
    });

    /* 2.4 Stepper del Nivel */
    document.querySelectorAll('.btn-step-action').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const action = btn.dataset.action;
        const targetId = btn.dataset.target;
        const input = document.getElementById(targetId);
        if (!input) return;

        let val = parseInt(input.value) || 1;
        const min = parseInt(input.min) || 1;
        const max = parseInt(input.max) || 100;

        if (action === 'increase' && val < max) {
          val++;
        } else if (action === 'decrease' && val > min) {
          val--;
        }

        input.value = val;
        recalculateTacticalMetrics();
      });
    });

    const levelInput = document.getElementById('inputNivel');
    if (levelInput) {
      levelInput.addEventListener('input', recalculateTacticalMetrics);
    }

    /* 2.5 Barra de Experiencia Dinámica */
    const expInput = document.getElementById('inputExp');
    const expMaxInput = document.getElementById('inputExpMax');
    const expFill = document.getElementById('heroExpFill');

    function updateExpBar() {
      if (!expFill) return;
      const current = parseFloat(expInput ? expInput.value : 0) || 0;
      const max = parseFloat(expMaxInput ? expMaxInput.value : 100) || 100;
      let pct = max > 0 ? (current / max) * 100 : 0;
      pct = Math.min(Math.max(pct, 0), 100);
      expFill.style.width = pct.toFixed(1) + '%';
    }

    if (expInput) expInput.addEventListener('input', updateExpBar);
    if (expMaxInput) expMaxInput.addEventListener('input', updateExpBar);
    updateExpBar();

    /* 2.6 Selector de Estado Vital (Radio Chips) */
    const statusLabels = document.querySelectorAll('.status-option-label');
    statusLabels.forEach(label => {
      const radio = label.querySelector('input[type="radio"]');
      if (radio) {
        radio.addEventListener('change', () => {
          statusLabels.forEach(l => l.classList.remove('is-selected'));
          if (radio.checked) {
            label.classList.add('is-selected');
          }
        });
      }
    });

    /* 2.7 Recálculo del Peso Total del Arsenal y Selección de Objetos */
    const itemCards = document.querySelectorAll('.item-checkbox-card');
    function updateInventoryWeight() {
      let totalWeight = 0;
      itemCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        const peso = parseFloat(card.dataset.peso) || 0;
        if (checkbox && checkbox.checked) {
          totalWeight += peso;
          card.classList.add('is-selected');
        } else {
          card.classList.remove('is-selected');
        }
      });

      const weightDisplay = document.getElementById('totalInventoryWeight');
      const carryMetric = document.getElementById('metricCarryVal');
      const formatted = totalWeight.toFixed(1) + ' kg';

      if (weightDisplay) weightDisplay.textContent = formatted + ' Total';
      if (carryMetric) carryMetric.textContent = formatted;
    }

    itemCards.forEach(card => {
      const checkbox = card.querySelector('input[type="checkbox"]');
      if (checkbox) {
        checkbox.addEventListener('change', updateInventoryWeight);
      }
      card.addEventListener('click', (e) => {
        if (e.target !== checkbox) {
          checkbox.checked = !checkbox.checked;
          updateInventoryWeight();
        }
      });
    });
    updateInventoryWeight();

    /* 2.8 Contador y Selección de Habilidades */
    const skillCards = document.querySelectorAll('.skill-checkbox-card');
    const skillCounterBadge = document.getElementById('skillCounterBadge');

    function updateSkillsSelection() {
      let count = 0;
      skillCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        if (checkbox && checkbox.checked) {
          count++;
          card.classList.add('is-selected');
        } else {
          card.classList.remove('is-selected');
        }
      });
      if (skillCounterBadge) {
        skillCounterBadge.textContent = count + ' Asignadas';
      }
    }

    skillCards.forEach(card => {
      const checkbox = card.querySelector('input[type="checkbox"]');
      if (checkbox) {
        checkbox.addEventListener('change', updateSkillsSelection);
      }
      card.addEventListener('click', (e) => {
        if (e.target !== checkbox) {
          checkbox.checked = !checkbox.checked;
          updateSkillsSelection();
        }
      });
    });
    updateSkillsSelection();

    /* 2.9 Buscadores Rápidos (Filtros en tiempo real) */
    const searchHabilidades = document.getElementById('searchHabilidades');
    if (searchHabilidades) {
      searchHabilidades.addEventListener('keydown', function(e) { if (e.key === 'Enter') e.preventDefault(); });
      searchHabilidades.addEventListener('input', function(e) {
        const text = e.target.value.toLowerCase();
        skillCards.forEach(card => {
          const name = card.querySelector('.skill-name').textContent.toLowerCase();
          if (name.includes(text)) {
            card.style.display = '';
          } else {
            card.style.display = 'none';
          }
        });
      });
    }

    const searchObjetos = document.getElementById('searchObjetos');
    if (searchObjetos) {
      searchObjetos.addEventListener('keydown', function(e) { if (e.key === 'Enter') e.preventDefault(); });
      searchObjetos.addEventListener('input', function(e) {
        const text = e.target.value.toLowerCase();
        itemCards.forEach(card => {
          const name = card.querySelector('.item-name').textContent.toLowerCase();
          if (name.includes(text)) {
            card.style.display = '';
          } else {
            card.style.display = 'none';
          }
        });
      });
    }

    // Inicialización general de métricas
    recalculateTacticalMetrics();
  });

})();
