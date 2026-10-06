document.addEventListener("DOMContentLoaded", () => {
    // Simple particle effect for the shop background
    const bg = document.querySelector('.shop-background');
    if(bg) {
        // Create some dust particles floating around
        for(let i=0; i<30; i++) {
            const particle = document.createElement('div');
            particle.style.position = 'absolute';
            particle.style.width = Math.random() * 3 + 'px';
            particle.style.height = particle.style.width;
            particle.style.background = 'rgba(241, 196, 15, ' + (Math.random() * 0.3 + 0.1) + ')';
            particle.style.borderRadius = '50%';
            
            // Random start position
            particle.style.left = Math.random() * 100 + 'vw';
            particle.style.top = Math.random() * 100 + 'vh';
            
            // Animation
            const duration = Math.random() * 10 + 5; // 5 to 15s
            particle.style.animation = `float ${duration}s infinite linear`;
            
            bg.appendChild(particle);
        }
    }
    
    // Add the CSS animation dynamically
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes float {
            0% { transform: translateY(0) translateX(0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100px) translateX(20px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});
