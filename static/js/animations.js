//JS para los efectos de click
document.addEventListener('click', function (e) {
    const nota = document.createElement('div');
    nota.classList.add('musical-note');

    // Elige un símbolo aleatorio
    const simbolos = ['🎵', '🎶', '♩', '♫', '♬'];
    nota.textContent = simbolos[Math.floor(Math.random() * simbolos.length)];

    // Posición absoluta respecto a la ventana
    nota.style.left = e.clientX + 'px';
    nota.style.top = e.clientY + 'px';

    document.body.appendChild(nota);

    // Elimina la nota tras la animación
    nota.addEventListener('animationend', () => {
        nota.remove();
    });
});

//JS para las animaciones de imágenes y texto
document.addEventListener('DOMContentLoaded', () => {
    const selectors = ['.foto-artista', '.foto-genero', '.texto-artista']; // Añade más si necesitas
    const elements = document.querySelectorAll(selectors.join(','));

    elements.forEach(el => {
        el.classList.add('scroll-anim');
    });

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                obs.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.4
    });

    elements.forEach(el => observer.observe(el));
});

//JS para animar círculos de fondo
const canvas = document.getElementById('backgroundCanvas');
const ctx = canvas.getContext('2d');
let width, height;
let circles = [];

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

const colors = ['#ff4081', '#00e5ff', '#7c4dff', '#69f0ae', '#ffc107'];

class Circle {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 1.5;
        this.vy = (Math.random() - 0.5) * 1.5;
        this.radius = Math.random() * 10 + 5;
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.alpha = Math.random() * 0.5 + 0.3;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.alpha;
        ctx.fill();
        ctx.globalAlpha = 1;
    }

    update(scrollY) {
        this.x += this.vx;
        this.y += this.vy + scrollY * 0.001;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;

        this.draw();
    }
}

// Crear círculos
for (let i = 0; i < 80; i++) {
    circles.push(new Circle());
}

let lastScroll = window.scrollY;

function animate() {
    ctx.clearRect(0, 0, width, height);
    const scrollDelta = window.scrollY - lastScroll;
    lastScroll = window.scrollY;

    circles.forEach(circle => circle.update(scrollDelta));
    requestAnimationFrame(animate);
}

animate();

//Animación para añadir cosas al carrito
document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.button-comprar-item');
  
    buttons.forEach(button => {
      button.addEventListener('click', e => {
        const form = e.target.closest('form');
        const img = form?.parentElement?.querySelector('img');
        const cartIcon = document.querySelector('#header-placeholder #cart-icon');
  
        if (!img || !cartIcon) return;
  
        const imgRect = img.getBoundingClientRect();
        const cartRect = cartIcon.getBoundingClientRect();
  
        const imgClone = img.cloneNode(true);
        imgClone.style.position = 'fixed';
        imgClone.style.left = imgRect.left + 'px';
        imgClone.style.top = imgRect.top + 'px';
        imgClone.style.width = imgRect.width + 'px';
        imgClone.style.height = imgRect.height + 'px';
        imgClone.style.zIndex = 10000;
        imgClone.style.transition = 'all 0.8s ease-in-out';
        imgClone.style.borderRadius = '10px';
        imgClone.style.pointerEvents = 'none';
        imgClone.style.opacity = '0.9';
  
        document.body.appendChild(imgClone);
  
        setTimeout(() => {
          imgClone.style.left = cartRect.left + 'px';
          imgClone.style.top = cartRect.top + 'px';
          imgClone.style.width = '20px';
          imgClone.style.height = '20px';
          imgClone.style.opacity = '0';
        }, 10);
  
        imgClone.addEventListener('transitionend', () => {
          imgClone.remove();
        });
      });
    });
  });
  
  




