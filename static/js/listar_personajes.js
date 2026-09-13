/* =============================================
   LISTAR PERSONAJES (GM) — WARCRAFT THEME
   static/js/listar_personajes.js
   Lienzo de brasas/cenizas + Interactividad de Filtros
   ============================================= */

(function () {
  'use strict';

  /* ─────────────────────────────────────────
     1. MOTOR DE BRASAS / CENIZAS (Canvas)
     ───────────────────────────────────────── */
  const canvas = document.getElementById('bgCanvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    const PX = 4; // Tamaño base

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
     2. GESTIÓN DE CHECKBOXES DE RAZAS
     ───────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    // Sincronizar estado inicial desde la URL
    const urlParams = new URLSearchParams(window.location.search);
    const selectedRazas = urlParams.getAll('raza');

    const raceChips = document.querySelectorAll('.race-chip');
    raceChips.forEach(chip => {
      const checkbox = chip.querySelector('input[type="checkbox"]');
      if (!checkbox) return;

      // Si el id está en los params de la URL, marcarlo
      if (selectedRazas.includes(checkbox.value)) {
        checkbox.checked = true;
        chip.classList.add('active');
      }

      // Al cambiar manualmente el checkbox, actualizar clase active
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
          chip.classList.add('active');
        } else {
          chip.classList.remove('active');
        }
      });
    });

    /* ─────────────────────────────────────────
       3. NAVEGACIÓN DE PAGINACIÓN CON FILTROS
       ───────────────────────────────────────── */
    // Permite que al dar clic en un número o flecha de página,
    // se mantengan los filtros de búsqueda 'q' y las razas seleccionadas.
    const paginationLinks = document.querySelectorAll('.pagination-action');
    paginationLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetPage = link.getAttribute('data-page');
        if (!targetPage) return;

        const currentParams = new URLSearchParams(window.location.search);
        currentParams.set('page', targetPage);
        window.location.search = currentParams.toString();
      });
    });

    /* ─────────────────────────────────────────
       4. ORDENAMIENTO POR ENCABEZADOS DE TABLA
       ───────────────────────────────────────── */
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    const currentOrder = urlParams.get('orden') || '';

    sortableHeaders.forEach(th => {
      const sortField = th.getAttribute('data-sort');
      const isAsc = currentOrder === sortField;
      const isDesc = currentOrder === `-${sortField}`;

      if (isAsc) {
        th.classList.add('sorted-asc');
      } else if (isDesc) {
        th.classList.add('sorted-desc');
      }

      th.addEventListener('click', () => {
        const params = new URLSearchParams(window.location.search);

        // Si ya está ordenado asc, alternar a desc (-sortField)
        // En caso contrario, ordenar asc (sortField)
        if (currentOrder === sortField) {
          params.set('orden', `-${sortField}`);
        } else {
          params.set('orden', sortField);
        }

        // Reiniciar a página 1 al cambiar el orden para ver los primeros resultados
        params.delete('page');

        window.location.search = params.toString();
      });
    });
  });

})();
