document.addEventListener("DOMContentLoaded", () => {
    const contrastButton = document.querySelector(".contrast-btn");
    const logo = document.querySelector(".logo");
    const fLogo = document.querySelector(".footer-logo");
    const shop = document.querySelector(".shop");

    const elementos = [
        { className: "song-love", icon: "favouriteicon" },
        { className: "song-comment", icon: "commenticon" },
        { className: "song-view", icon: "viewsicon" },
        { className: "song-visible", icon: "isvisibleicon" }
    ];

    const actualizarModo = (modo) => {
        const esOscuro = modo === "dark";
        document.body.classList.toggle("dark-mode", esOscuro);

        // Solo cambia imágenes si existen
        if (logo) logo.src = esOscuro ? "/images/logooscuro.png" : "/images/logoclaro.png";
        if (fLogo) fLogo.src = esOscuro ? "/images/logooscuro.png" : "/images/logoclaro.png";
        if (shop) shop.src = esOscuro ? "/images/carritoicons/shopping_oscuro.png" : "/images/carritoicons/shopping_claro.png";

        elementos.forEach(({ className, icon }) => {
            document.querySelectorAll(`.${className}`).forEach(el => {
                el.src = `images/studioicons/${icon}${esOscuro ? "_oscuro" : ""}.png`;
            });
        });

        localStorage.setItem("theme", modo);
    };

    const aplicarModoPreferido = () => {
        const userTheme = localStorage.getItem("theme");
        if (userTheme) {
            actualizarModo(userTheme);
        } else {
            const sistemaOscuro = window.matchMedia("(prefers-color-scheme: dark)").matches;
            actualizarModo(sistemaOscuro ? "dark" : "light");
        }
    };

    // Siempre aplica el modo preferido
    aplicarModoPreferido();

    // Si hay botón de contraste, lo hace interactivo
    if (contrastButton) {
        contrastButton.addEventListener("click", () => {
            const isDark = document.body.classList.toggle("dark-mode");
            actualizarModo(isDark ? "dark" : "light");
        });

        const observer = new MutationObserver(() => {
            const userTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
            actualizarModo(userTheme);
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }
});
