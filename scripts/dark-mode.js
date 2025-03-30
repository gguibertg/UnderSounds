document.addEventListener("DOMContentLoaded", () => {
    const interval = setInterval(() => {
        const contrastButton = document.querySelector(".contrast-btn");
        const logo = document.querySelector(".logo"); // Seleccionar el logo
        const fLogo = document.querySelector(".footer-logo"); // Seleccionar el logo
        const shop = document.querySelector(".shop"); // Seleccionar el carrito
        
        // Elementos a modificar
        const elementos = [
            { className: "song-love", icon: "favouriteicon" },
            { className: "song-comment", icon: "commenticon" },
            { className: "song-view", icon: "viewsicon" },
            { className: "song-visible", icon: "isvisibleicon" }
        ];
        
        if (contrastButton && logo && shop) {
            clearInterval(interval); // Detener la búsqueda cuando encontramos los elementos

            // Función para actualizar el tema y los iconos
            const actualizarModo = (modo) => {
                const esOscuro = modo === "dark";
                document.body.classList.toggle("dark-mode", esOscuro);
                
                logo.src = esOscuro ? "/images/logooscuro.png" : "/images/logoclaro.png";
                fLogo.src = esOscuro ? "/images/logooscuro.png" : "/images/logoclaro.png";
                shop.src = esOscuro ? "/images/carritoicons/shopping_oscuro.png" : "/images/carritoicons/shopping_claro.png";
                
                elementos.forEach(({ className, icon }) => {
                    document.querySelectorAll(`.${className}`).forEach(elemento => {
                        elemento.src = `images/studioicons/${icon}${esOscuro ? "_oscuro" : ""}.png`;
                    });
                });
                
                localStorage.setItem("theme", modo); // Guardar preferencia
            };

            // Observar cambios en el DOM para actualizar imágenes dinámicamente
            const observer = new MutationObserver(() => {
                const userTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
                actualizarModo(userTheme);
            });

            observer.observe(document.body, { childList: true, subtree: true });

            // Verificar la preferencia del usuario o usar la del sistema
            const userTheme = localStorage.getItem("theme");
            if (userTheme) {
                actualizarModo(userTheme);
            } else {
                const sistemaOscuro = window.matchMedia("(prefers-color-scheme: dark)").matches;
                actualizarModo(sistemaOscuro ? "dark" : "light");
            }

            // Alternar entre modo oscuro y claro cuando el usuario haga clic
            contrastButton.addEventListener("click", () => {
                const isDarkMode = document.body.classList.toggle("dark-mode");
                actualizarModo(isDarkMode ? "dark" : "light");
            });
        }
    }, 100); // Verificar cada 100ms hasta encontrar el botón y el logo
});