/**
 * AUDIO_PLAYER.JS - Gestor de Música Global del Videojuego
 * - Música continua: musica-game.mp3 en todo el sitio
 * - Volumen configurado al 50%
 * - Persistencia de estado de silencio (localStorage)
 * - Continuidad de reproducción entre páginas (sessionStorage)
 * - Autoplay inteligente con desbloqueo al primer gesto del usuario
 */

(function () {
  const STORAGE_KEY_MUTED = 'warcraft_audio_muted';
  const STORAGE_KEY_TIME = 'warcraft_audio_time';

  function initGlobalAudio() {
    const audio = document.getElementById('globalGameAudio');
    const btn = document.getElementById('btnGlobalAudio');
    const iconPlaying = document.getElementById('globalAudioIconPlaying');
    const iconMuted = document.getElementById('globalAudioIconMuted');

    if (!audio || !btn) return;

    // 1. Configurar volumen inicial al 50%
    audio.volume = 0.5;

    // 2. Comprobar preferencia guardada del usuario
    const isMutedStored = localStorage.getItem(STORAGE_KEY_MUTED) === 'true';
    audio.muted = isMutedStored;

    // 3. Restaurar posición de reproducción entre páginas si existe
    const savedTime = sessionStorage.getItem(STORAGE_KEY_TIME);
    if (savedTime && !isNaN(parseFloat(savedTime))) {
      audio.currentTime = parseFloat(savedTime);
    }

    // 4. Actualizar estado visual del botón
    function updateButtonUI(isAudible) {
      if (isAudible && !audio.muted && !audio.paused) {
        btn.classList.add('playing');
        btn.classList.remove('muted');
        btn.setAttribute('title', 'Música activa (Click para silenciar)');
        if (iconPlaying) iconPlaying.style.display = 'inline-block';
        if (iconMuted) iconMuted.style.display = 'none';
      } else {
        btn.classList.remove('playing');
        btn.classList.add('muted');
        btn.setAttribute('title', 'Música silenciada (Click para activar)');
        if (iconPlaying) iconPlaying.style.display = 'none';
        if (iconMuted) iconMuted.style.display = 'inline-block';
      }
    }

    updateButtonUI(!audio.muted);

    // 5. Guardar posición de reproducción continuamente
    let lastSavedTime = 0;
    audio.addEventListener('timeupdate', () => {
      const now = Math.floor(audio.currentTime);
      if (now !== lastSavedTime) {
        lastSavedTime = now;
        sessionStorage.setItem(STORAGE_KEY_TIME, audio.currentTime.toString());
      }
    });

    window.addEventListener('beforeunload', () => {
      sessionStorage.setItem(STORAGE_KEY_TIME, audio.currentTime.toString());
    });

    // 6. Intento de reproducción automática
    function tryPlayAudio() {
      const promise = audio.play();
      if (promise !== undefined) {
        promise
          .then(() => {
            updateButtonUI(!audio.muted);
            cleanupGestureListeners();
          })
          .catch(() => {
            // Si el navegador bloqueó el autoplay sin interacción previa
            if (!audio.muted) {
              updateButtonUI(false);
              setupGestureListeners();
            }
          });
      }
    }

    function onUserGesture() {
      if (!audio.muted && audio.paused) {
        tryPlayAudio();
      }
    }

    function setupGestureListeners() {
      window.addEventListener('pointerdown', onUserGesture, { once: true });
      window.addEventListener('click', onUserGesture, { once: true });
      window.addEventListener('keydown', onUserGesture, { once: true });
    }

    function cleanupGestureListeners() {
      window.removeEventListener('pointerdown', onUserGesture);
      window.removeEventListener('click', onUserGesture);
      window.removeEventListener('keydown', onUserGesture);
    }

    // Iniciar reproducción
    if (!isMutedStored) {
      tryPlayAudio();
    } else {
      updateButtonUI(false);
    }

    // 7. Manejo del clic en el botón cuadradito de silenciar
    btn.addEventListener('click', (e) => {
      e.stopPropagation();

      if (audio.muted || audio.paused) {
        // Desmutear y reproducir
        audio.muted = false;
        audio.volume = 0.5;
        localStorage.setItem(STORAGE_KEY_MUTED, 'false');
        tryPlayAudio();
        updateButtonUI(true);
      } else {
        // Silenciar
        audio.muted = true;
        localStorage.setItem(STORAGE_KEY_MUTED, 'true');
        updateButtonUI(false);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGlobalAudio);
  } else {
    initGlobalAudio();
  }
})();
