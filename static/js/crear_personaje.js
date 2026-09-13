/**
 * CREAR_PERSONAJE.JS - Motor Épico de Creación de Personaje (100vh)
 * - Partículas de brasas en canvas a 60 FPS
 * - Escenario 3D con vitrina de razas (cuerpo entero y miniaturas de rostro)
 * - Sistema independiente de atributos (Modelo Atributo) con cálculo de HP/SP tipo Metin2
 * - Gestor de Habilidades con Drag & Drop usando SortableJS (Máximo 2 habilidades)
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Inicializar Canvas de brasas
  initParticleCanvas();

  // 2. Inicializar Escenario de Razas
  initRaceStage();

  // 3. Inicializar Reparto de Atributos
  initAttributeSystem();

  // 4. Inicializar Drag & Drop de Habilidades con SortableJS
  initSortableSkills();

  // 5. Validación de Envío de Formulario
  initFormValidation();
});

/* ===================================================
   1. CANVAS DE BRASAS / CENIZAS (60 FPS)
   =================================================== */
function initParticleCanvas() {
  const canvas = document.getElementById('bgCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = [];
  const PARTICLE_COUNT = 40;

  class AshParticle {
    constructor() {
      this.reset(true);
    }
    reset(initial = false) {
      this.x = Math.random() * width;
      this.y = initial ? Math.random() * height : height + 10;
      this.size = Math.random() * 2.2 + 1;
      this.speedY = Math.random() * 0.8 + 0.3;
      this.speedX = (Math.random() - 0.5) * 0.4;
      this.opacity = Math.random() * 0.7 + 0.3;
      this.fadeSpeed = Math.random() * 0.003 + 0.001;
      this.color = Math.random() > 0.4 ? '#ffcc00' : '#ff5522';
    }
    update() {
      this.y -= this.speedY;
      this.x += this.speedX + Math.sin(this.y * 0.015) * 0.25;
      this.opacity -= this.fadeSpeed;
      if (this.y < -10 || this.opacity <= 0) {
        this.reset();
      }
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.globalAlpha = Math.max(0, this.opacity);
      ctx.shadowBlur = 6;
      ctx.shadowColor = this.color;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.shadowBlur = 0;
    }
  }

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(new AshParticle());
  }

  function loop() {
    ctx.clearRect(0, 0, width, height);
    for (let p of particles) {
      p.update();
      p.draw();
    }
    requestAnimationFrame(loop);
  }
  loop();
}

/* ===================================================
   2. ESCENARIO 3D DE RAZAS (LINEUP ESTILO METIN2)
   =================================================== */
let raceData = [];
let currentRaceIndex = 0;

function initRaceStage() {
  const standees = Array.from(document.querySelectorAll('.character-standee'));
  const pills = Array.from(document.querySelectorAll('.stage-head-pill'));
  const btnPrev = document.getElementById('btnPrevRace');
  const btnNext = document.getElementById('btnNextRace');
  const selectedRazaInput = document.getElementById('selectedRazaInput');

  // Leer JSON de razas serializado desde Django
  const rawDataScript = document.getElementById('raceDataJson');
  if (rawDataScript) {
    try {
      raceData = JSON.parse(rawDataScript.textContent);
    } catch (e) {
      console.warn('No se pudo parsear raceDataJson:', e);
    }
  }

  if (standees.length === 0) return;

  function updateStage(newIndex) {
    if (newIndex < 0) newIndex = standees.length - 1;
    if (newIndex >= standees.length) newIndex = 0;
    currentRaceIndex = newIndex;

    // Actualizar personajes en el escenario
    standees.forEach((standee, idx) => {
      standee.classList.remove('active', 'pos-left', 'pos-right', 'pos-hidden');
      if (idx === currentRaceIndex) {
        standee.classList.add('active');
      } else if (idx === (currentRaceIndex - 1 + standees.length) % standees.length) {
        standee.classList.add('pos-left');
      } else if (idx === (currentRaceIndex + 1) % standees.length) {
        standee.classList.add('pos-right');
      } else {
        standee.classList.add('pos-hidden');
      }
    });

    // Actualizar miniaturas de rostro
    pills.forEach((pill, idx) => {
      pill.classList.toggle('active', idx === currentRaceIndex);
    });

    // Actualizar datos de texto de la raza
    const currentRaza = raceData[currentRaceIndex];
    if (currentRaza) {
      if (selectedRazaInput) selectedRazaInput.value = currentRaza.id;

      const loreName = document.getElementById('raceLoreName');
      const loreDesc = document.getElementById('raceLoreDesc');
      const bonusesRow = document.getElementById('raceBonusesRow');

      if (loreName) loreName.textContent = currentRaza.nombre;
      if (loreDesc) loreDesc.textContent = currentRaza.descripcion || 'Sin descripción disponible.';

      // Renderizar bonos y penalizaciones raciales
      if (bonusesRow) {
        bonusesRow.innerHTML = '';
        let hasBonuses = false;

        if (currentRaza.bonificadores && typeof currentRaza.bonificadores === 'object') {
          for (let [stat, val] of Object.entries(currentRaza.bonificadores)) {
            hasBonuses = true;
            const pill = document.createElement('span');
            pill.className = 'bonus-pill bonus-positive';
            pill.textContent = `+${val} ${stat.toUpperCase()}`;
            bonusesRow.appendChild(pill);
          }
        }
        if (currentRaza.handicap && typeof currentRaza.handicap === 'object') {
          for (let [stat, val] of Object.entries(currentRaza.handicap)) {
            hasBonuses = true;
            const pill = document.createElement('span');
            pill.className = 'bonus-pill bonus-negative';
            pill.textContent = `${val} ${stat.toUpperCase()}`;
            bonusesRow.appendChild(pill);
          }
        }
        if (!hasBonuses) {
          const pill = document.createElement('span');
          pill.className = 'bonus-pill';
          pill.style.background = 'rgba(255, 204, 0, 0.1)';
          pill.style.border = '1px solid #8c7335';
          pill.style.color = '#c4ab7c';
          pill.textContent = 'Atributos Equilibrados';
          bonusesRow.appendChild(pill);
        }
      }

      // Notificar al sistema de atributos
      if (window.onRaceChanged) {
        window.onRaceChanged(currentRaza);
      }
    }
  }

  // Clic en los personajes del escenario
  standees.forEach((standee, idx) => {
    standee.addEventListener('click', () => updateStage(idx));
  });

  // Clic en las miniaturas de rostro inferiores
  pills.forEach((pill, idx) => {
    pill.addEventListener('click', () => updateStage(idx));
  });

  // Flechas de navegación del escenario
  if (btnPrev) btnPrev.addEventListener('click', () => updateStage(currentRaceIndex - 1));
  if (btnNext) btnNext.addEventListener('click', () => updateStage(currentRaceIndex + 1));

  // Navegación con teclado
  window.addEventListener('keydown', (e) => {
    if (document.activeElement && document.activeElement.tagName === 'INPUT') return;
    if (e.key === 'ArrowLeft') updateStage(currentRaceIndex - 1);
    if (e.key === 'ArrowRight') updateStage(currentRaceIndex + 1);
  });

  // Iniciar en la primera raza
  updateStage(0);
}

/* ===================================================
   3. SISTEMA DE ATRIBUTOS (MODELO ATRIBUTO)
   =================================================== */
function initAttributeSystem() {
  const TOTAL_POINTS = 20;
  const BASE_STAT = 5;
  const MAX_STAT_SCALE = 25;

  const attributes = [
    'fuerza',
    'destreza',
    'vigor',
    'inteligencia',
    'percepcion',
    'carisma',
    'suerte'
  ];

  const state = {
    availablePoints: TOTAL_POINTS,
    allocated: {
      fuerza: 0,
      destreza: 0,
      vigor: 0,
      inteligencia: 0,
      percepcion: 0,
      carisma: 0,
      suerte: 0
    },
    racialBonus: {
      fuerza: 0,
      destreza: 0,
      vigor: 0,
      inteligencia: 0,
      percepcion: 0,
      carisma: 0,
      suerte: 0
    }
  };

  const poolValEl = document.getElementById('pointsPoolVal');

  window.onRaceChanged = function (raza) {
    attributes.forEach(attr => (state.racialBonus[attr] = 0));

    if (raza.bonificadores && typeof raza.bonificadores === 'object') {
      for (let [k, v] of Object.entries(raza.bonificadores)) {
        const keyLower = k.toLowerCase();
        if (state.racialBonus.hasOwnProperty(keyLower)) {
          state.racialBonus[keyLower] += parseInt(v, 10) || 0;
        }
      }
    }
    if (raza.handicap && typeof raza.handicap === 'object') {
      for (let [k, v] of Object.entries(raza.handicap)) {
        const keyLower = k.toLowerCase();
        if (state.racialBonus.hasOwnProperty(keyLower)) {
          state.racialBonus[keyLower] += parseInt(v, 10) || 0;
        }
      }
    }
    renderAllAttributes();
  };

  function renderAllAttributes() {
    if (poolValEl) poolValEl.textContent = state.availablePoints;

    // Cálculo dinámico de HP (Vigor x 20) y SP (Inteligencia x 15)
    const currentVigor = BASE_STAT + (state.allocated['vigor'] || 0) + (state.racialBonus['vigor'] || 0);
    const currentInt = BASE_STAT + (state.allocated['inteligencia'] || 0) + (state.racialBonus['inteligencia'] || 0);

    const calculatedHp = currentVigor * 20;
    const calculatedSp = currentInt * 15;

    const hpValEl = document.getElementById('vitalHpVal');
    const hpBarEl = document.getElementById('vitalHpBar');
    const spValEl = document.getElementById('vitalSpVal');
    const spBarEl = document.getElementById('vitalSpBar');

    if (hpValEl) hpValEl.textContent = `${calculatedHp}`;
    if (hpBarEl) hpBarEl.style.width = `${Math.min(100, Math.max(10, (calculatedHp / 400) * 100))}%`;

    if (spValEl) spValEl.textContent = `${calculatedSp}`;
    if (spBarEl) spBarEl.style.width = `${Math.min(100, Math.max(10, (calculatedSp / 300) * 100))}%`;

    attributes.forEach(attr => {
      const row = document.querySelector(`.attr-row.attr-${attr}`);
      if (!row) return;

      const bonus = state.racialBonus[attr] || 0;
      const allocated = state.allocated[attr] || 0;
      const total = BASE_STAT + allocated + bonus;

      const numEl = row.querySelector('.attr-num');
      if (numEl) numEl.textContent = total;

      const fillEl = row.querySelector('.attr-fill');
      if (fillEl) {
        const pct = Math.min(100, Math.max(8, (total / MAX_STAT_SCALE) * 100));
        fillEl.style.width = `${pct}%`;
      }

      const btnDec = row.querySelector('.btn-attr-dec');
      const btnInc = row.querySelector('.btn-attr-inc');

      if (btnDec) btnDec.disabled = allocated <= 0;
      if (btnInc) btnInc.disabled = state.availablePoints <= 0;

      const hiddenInput = document.getElementById(`input_${attr}`);
      if (hiddenInput) hiddenInput.value = total;
    });
  }

  attributes.forEach(attr => {
    const row = document.querySelector(`.attr-row.attr-${attr}`);
    if (!row) return;

    const btnDec = row.querySelector('.btn-attr-dec');
    const btnInc = row.querySelector('.btn-attr-inc');

    if (btnDec) {
      btnDec.addEventListener('click', (e) => {
        e.preventDefault();
        if (state.allocated[attr] > 0) {
          state.allocated[attr]--;
          state.availablePoints++;
          renderAllAttributes();
        }
      });
    }

    if (btnInc) {
      btnInc.addEventListener('click', (e) => {
        e.preventDefault();
        if (state.availablePoints > 0) {
          state.allocated[attr]++;
          state.availablePoints--;
          renderAllAttributes();
        }
      });
    }
  });

  renderAllAttributes();
}

/* ===================================================
   4. GESTOR DE HABILIDADES CON SORTABLEJS (MÁXIMO 2)
   =================================================== */
function initSortableSkills() {
  const availableContainer = document.getElementById('availableSkills');
  const assignedContainer = document.getElementById('assignedSkills');
  const quadrantAssigned = document.querySelector('.quadrant-assigned');
  const counterBadge = document.getElementById('assignedCounterBadge');
  const warningToast = document.getElementById('skillLimitWarning');
  const inputsContainer = document.getElementById('assignedSkillsInputs');

  if (!availableContainer || !assignedContainer) return;

  const MAX_SKILLS = 2;
  let toastTimeout = null;

  function showSkillLimitWarning() {
    if (!warningToast) return;
    warningToast.classList.add('show');
    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
      warningToast.classList.remove('show');
    }, 2800);
  }

  function syncSkillsState() {
    const assignedCards = Array.from(assignedContainer.querySelectorAll('.skill-card'));
    const count = assignedCards.length;

    // Actualizar badge de conteo
    if (counterBadge) {
      counterBadge.textContent = `${count} / ${MAX_SKILLS}`;
      counterBadge.classList.toggle('limit-reached', count >= MAX_SKILLS);
    }

    // Actualizar atributo data-count en el contenedor para placeholders
    if (quadrantAssigned) {
      quadrantAssigned.setAttribute('data-count', count);
    }

    // Actualizar botones toggle (+ / ×) y estilos de las tarjetas
    assignedContainer.querySelectorAll('.skill-card').forEach(card => {
      const toggle = card.querySelector('.btn-card-toggle .toggle-symbol');
      if (toggle) toggle.textContent = '×';
    });

    availableContainer.querySelectorAll('.skill-card').forEach(card => {
      const toggle = card.querySelector('.btn-card-toggle .toggle-symbol');
      if (toggle) toggle.textContent = '+';
    });

    // Sincronizar inputs ocultos <input type="hidden" name="habilidades" value="PK">
    if (inputsContainer) {
      inputsContainer.innerHTML = '';
      assignedCards.forEach(card => {
        const skillId = card.dataset.skillId;
        if (skillId) {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = 'habilidades';
          input.value = skillId;
          inputsContainer.appendChild(input);
        }
      });
    }

    // Actualizar etiqueta de disponibles
    const availCountTag = document.getElementById('availableCountTag');
    if (availCountTag) {
      const availCount = availableContainer.querySelectorAll('.skill-card').length;
      availCountTag.textContent = `${availCount} disponibles`;
    }
  }

  // Instanciar Sortable en Habilidades Disponibles
  new Sortable(availableContainer, {
    group: {
      name: 'skills-group',
      pull: true,
      put: true
    },
    animation: 200,
    ghostClass: 'sortable-ghost',
    chosenClass: 'sortable-chosen',
    dragClass: 'sortable-drag',
    handle: '.skill-drag-grip, .skill-card-body',
    onEnd: () => syncSkillsState()
  });

  // Instanciar Sortable en Habilidades Asignadas (Con restricción estricta de máximo 2)
  new Sortable(assignedContainer, {
    group: {
      name: 'skills-group',
      pull: true,
      put: function (to) {
        // Impedir que se suelte un 3er elemento si ya hay 2 asignados
        const currentAssigned = to.el.querySelectorAll('.skill-card').length;
        if (currentAssigned >= MAX_SKILLS) {
          showSkillLimitWarning();
          return false;
        }
        return true;
      }
    },
    animation: 200,
    ghostClass: 'sortable-ghost',
    chosenClass: 'sortable-chosen',
    dragClass: 'sortable-drag',
    handle: '.skill-drag-grip, .skill-card-body',
    onAdd: function (evt) {
      const currentAssigned = assignedContainer.querySelectorAll('.skill-card');
      if (currentAssigned.length > MAX_SKILLS) {
        // Revertir de inmediato a disponibles si se excede el límite
        availableContainer.appendChild(evt.item);
        showSkillLimitWarning();
      }
      syncSkillsState();
    },
    onRemove: () => syncSkillsState(),
    onSort: () => syncSkillsState()
  });

  // Manejo de clic rápido en el botón '+' / '×' de cada tarjeta
  document.addEventListener('click', (e) => {
    const toggleBtn = e.target.closest('.btn-card-toggle');
    if (!toggleBtn) return;

    const card = toggleBtn.closest('.skill-card');
    if (!card) return;

    const isAssigned = assignedContainer.contains(card);

    if (isAssigned) {
      // Mover de regreso a disponibles
      availableContainer.appendChild(card);
      syncSkillsState();
    } else {
      // Intentar asignar
      const currentAssigned = assignedContainer.querySelectorAll('.skill-card').length;
      if (currentAssigned >= MAX_SKILLS) {
        showSkillLimitWarning();
        return;
      }
      assignedContainer.appendChild(card);
      syncSkillsState();
    }
  });

  // Sincronización inicial
  syncSkillsState();
}

/* ===================================================
   5. VALIDACIÓN DEL FORMULARIO DE CREACIÓN
   =================================================== */
function initFormValidation() {
  const form = document.getElementById('formCrearPersonaje');
  const inputName = document.getElementById('inputHeroName');

  if (!form) return;

  form.addEventListener('submit', (e) => {
    const nameVal = inputName ? inputName.value.trim() : '';

    if (!nameVal || nameVal.length < 3) {
      e.preventDefault();
      alert('⚠️ Por favor ingresa un nombre para el héroe de al menos 3 caracteres.');
      if (inputName) inputName.focus();
      return;
    }

    const poolValEl = document.getElementById('pointsPoolVal');
    const remaining = poolValEl ? parseInt(poolValEl.textContent, 10) : 0;

    if (remaining > 0) {
      const confirmSpend = confirm(`Aún tienes ${remaining} puntos de atributos sin asignar. ¿Deseas forjar el guerrero de todas formas?`);
      if (!confirmSpend) {
        e.preventDefault();
        return;
      }
    }
  });
}
