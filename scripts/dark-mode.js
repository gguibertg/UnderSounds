document.addEventListener("DOMContentLoaded", () => {
    const interval = setInterval(() => {
        const contrastButton = document.querySelector(".contrast-btn");
        const logo = document.querySelector(".logo"); // Seleccionar el logo
        const shop = document.querySelector(".shop"); // Seleccionar el carrito

        if (contrastButton && logo) {
            clearInterval(interval); // Detener la búsqueda cuando encontramos los elementos

            // Función para actualizar el tema y el logo
            const actualizarModo = (modo) => {
                if (modo === "dark") {
                    document.body.classList.add("dark-mode");
                    logo.src = "/images/logooscuro.png"; // Cambiar al logo oscuro
                    shop.src = "/images/carritoicons/shopping_oscuro.png"; // Cambiar al carrito oscuro
                } else {
                    document.body.classList.remove("dark-mode");
                    logo.src = "/images/logoclaro.png"; // Cambiar al logo claro
                    shop.src = "/images/carritoicons/shopping_claro.png"; // Cambiar al carrito oscuro
                }
                localStorage.setItem("theme", modo); // Guardar preferencia
            };

            // Verificar la preferencia del usuario o usar la del sistema
            const userTheme = localStorage.getItem("theme");

            if (userTheme) {
                actualizarModo(userTheme);
            } else {
                // Si no hay preferencia guardada, usar la del sistema
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
