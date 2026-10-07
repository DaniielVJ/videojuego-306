// Lógica para efectos épicos (Canvas) en la pantalla de destierro
document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("bgCanvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  
  // Ajuste al tamaño de ventana
  const resizeCanvas = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();

  // Partículas de brasas/cenizas rojas para representar destrucción (Horda/Destierro)
  const particles = [];
  const particleCount = 80; // Un poco menos denso para no distraer del mensaje

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 3 + 1,
      speedY: Math.random() * 1.5 + 0.5,
      speedX: (Math.random() - 0.5) * 1,
      opacity: Math.random() * 0.8 + 0.2
    });
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach(p => {
      ctx.beginPath();
      // Color de fuego/sangre (Rojos/Naranjas oscuros)
      ctx.fillStyle = `rgba(255, ${Math.floor(Math.random() * 60)}, 0, ${p.opacity})`;
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();

      // Subir
      p.y -= p.speedY;
      p.x += p.speedX;

      // Reiniciar desde abajo
      if (p.y < 0) {
        p.y = canvas.height;
        p.x = Math.random() * canvas.width;
      }
    });

    requestAnimationFrame(animate);
  }

  animate();
  
  // Logic to handle "es_equipable" checkbox and "tipo_equipamiento" select
  const esEquipableCheckbox = document.querySelector('input[name="es_equipable"]');
  const tipoEquipamientoSelect = document.querySelector('select[name="tipo_equipamiento"]');
  
  if (esEquipableCheckbox && tipoEquipamientoSelect) {
    const toggleSelect = () => {
      if (esEquipableCheckbox.checked) {
        tipoEquipamientoSelect.disabled = false;
        tipoEquipamientoSelect.style.opacity = '1';
        tipoEquipamientoSelect.style.cursor = 'pointer';
      } else {
        tipoEquipamientoSelect.disabled = true;
        tipoEquipamientoSelect.value = ''; // clear value
        tipoEquipamientoSelect.style.opacity = '0.4';
        tipoEquipamientoSelect.style.cursor = 'not-allowed';
      }
    };
    
    // Initial check on load
    toggleSelect();
    
    // Listen for changes
    esEquipableCheckbox.addEventListener('change', toggleSelect);
  }
});
