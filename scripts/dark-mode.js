document.addEventListener("DOMContentLoaded", () => {
    const interval = setInterval(() => {
        const contrastButton = document.querySelector(".contrast-btn");

        // Verifica si el botón existe antes de añadir el event listener
        if (contrastButton) {
            clearInterval(interval); // Detener la búsqueda cuando encontramos el botón

            // Verifica la preferencia del usuario o usa la del sistema
            const userTheme = localStorage.getItem("theme");

            if (userTheme === "dark") {
                document.body.classList.add("dark-mode");
            } else if (userTheme === "light") {
                document.body.classList.remove("dark-mode");
            } else {
                // Si no hay preferencia guardada, se ajusta según la preferencia del sistema
                if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
                    document.body.classList.add("dark-mode");
                    localStorage.setItem("theme", "dark"); // Guardar preferencia como "dark"
                } else {
                    document.body.classList.remove("dark-mode");
                    localStorage.setItem("theme", "light"); // Guardar preferencia como "light"
                }
            }

            // Alternar entre modo oscuro y claro cuando el usuario haga clic en el botón
            contrastButton.addEventListener("click", () => {
                const isDarkMode = document.body.classList.toggle("dark-mode");

                // Guardar la preferencia del usuario en localStorage
                localStorage.setItem("theme", isDarkMode ? "dark" : "light");
            });
        }
    }, 100); // Verificar cada 100ms hasta encontrar el botón
});
