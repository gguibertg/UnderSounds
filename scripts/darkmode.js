document.addEventListener("DOMContentLoaded", () => {
    const contrastButton = document.querySelector(".contrast-btn");

    // Verifica la preferencia del usuario o usa la del sistema
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
    } else if (localStorage.getItem("theme") === "light") {
        document.body.classList.remove("dark-mode");
    } else {
        if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
        }
    }

    // Alternar entre modo oscuro y claro
    contrastButton.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        // Guardar la preferencia del usuario
        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });
});
