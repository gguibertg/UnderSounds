document.addEventListener("DOMContentLoaded", () => {
    // Detecta si estamos en una página de autenticación (sin header/footer dinámicos)
    const authPage = document.body.classList.contains("auth-page");

    // Referencias a elementos que se actualizarán según el tema
    let logo = null;
    let fLogo = null;
    let shop = null;

    // Íconos de acciones sobre la canción que deben cambiar según el tema
    const elementos = [
        { className: "song-love", icon: "fav-icon" },
        { className: "song-comment", icon: "comment-icon" },
        { className: "song-view", icon: "views-icon" },
        { className: "song-visible", icon: "visibility-icon" }
    ];    

    // Aplica el modo claro u oscuro, y actualiza los iconos y logos correspondientes
    const actualizarModo = (modo) => {
        const esOscuro = modo === "dark";
        document.body.classList.toggle("dark-mode", esOscuro);

        const logoSrc = `/static/img/utils/logo-${esOscuro ? "dark" : "light"}.png`;
        const cartSrc = `/static/icons/site/cart-icon-${esOscuro ? "dark" : "light"}.svg`;

        if (logo) logo.src = logoSrc;
        if (fLogo) fLogo.src = logoSrc;
        if (shop) shop.src = cartSrc;

        elementos.forEach(({ className, icon }) => {
            const iconSrc = `/static/icons/site/${icon}-${esOscuro ? "dark" : "light"}.svg`;
            document.querySelectorAll(`.${className}`).forEach(el => {
                el.src = iconSrc;
            });
        });

        localStorage.setItem("theme", modo);
    };

    // Aplica el modo previamente guardado en el navegador
    const aplicarModoPreferido = () => {
        const userTheme = localStorage.getItem("theme");
        if (userTheme) {
            actualizarModo(userTheme);
        }
    };

    // Asocia el botón de contraste para alternar el tema manualmente
    const vincularBoton = () => {
        const contrastButton = document.querySelector(".contrast-btn");
        if (contrastButton && !contrastButton.dataset.listenerAttached) {
            contrastButton.addEventListener("click", () => {
                const esModoOscuro = document.body.classList.contains("dark-mode");
                actualizarModo(esModoOscuro ? "light" : "dark");
            });
            contrastButton.dataset.listenerAttached = "true";
        }
    };

    // Captura referencias a los elementos clave para modificar sus recursos
    const capturarElementos = () => {
        logo = document.querySelector(".logo");
        fLogo = document.querySelector(".footer-logo");
        shop = document.querySelector(".shop");
    };

    aplicarModoPreferido();

    if (authPage) {
        // Si es una página de login/registro, los elementos ya están en el DOM
        capturarElementos();
        vincularBoton();
    } else {
        // En páginas con carga dinámica del header/footer:
        document.addEventListener("headerLoaded", () => {
            capturarElementos();
            aplicarModoPreferido();
        });

        document.addEventListener("footerLoaded", () => {
            vincularBoton();
        });

        // Por si header/footer ya estaban cargados antes de estos eventos
        setTimeout(() => {
            capturarElementos();
            vincularBoton();
        }, 500);
    }
});
