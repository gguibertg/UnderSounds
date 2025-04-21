document.addEventListener("DOMContentLoaded", () => {
    const isAuthPage = document.body.classList.contains("auth-page");

    let logo = null;
    let footerLogo = null;

    const updateTheme = (theme) => {
        const isDark = theme === "dark";
        document.body.classList.toggle("dark-mode", isDark);

        const logoSrc = `/static/img/utils/logo-${isDark ? "dark" : "light"}.png`;

        if (logo) logo.src = logoSrc;
        if (footerLogo) footerLogo.src = logoSrc;

        // Actualiza automáticamente todos los íconos temáticos
        document.querySelectorAll(".theme-icon").forEach(el => {
            const iconBase = el.dataset.icon;
            if (iconBase) {
                el.src = `/static/icons/site/${iconBase}-${isDark ? "dark" : "light"}.svg`;
            }
        });

        localStorage.setItem("theme", theme);
    };

    const applySavedTheme = () => {
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme) {
            updateTheme(savedTheme);
        }
    };

    const bindContrastButton = () => {
        const contrastBtn = document.querySelector(".contrast-btn");
        if (contrastBtn && !contrastBtn.dataset.listenerAttached) {
            contrastBtn.addEventListener("click", () => {
                const isDark = document.body.classList.contains("dark-mode");
                updateTheme(isDark ? "light" : "dark");
            });
            contrastBtn.dataset.listenerAttached = "true";
        }
    };

    const captureElements = () => {
        logo = document.querySelector(".logo");
        footerLogo = document.querySelector(".footer-logo");
    };

    const esperarElemento = (selector) => {
        return new Promise(resolve => {
            if (document.querySelector(selector)) return resolve();
            const observer = new MutationObserver(() => {
                if (document.querySelector(selector)) {
                    observer.disconnect();
                    resolve();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        });
    };

    const iniciarTemaYEventos = () => {
        captureElements();
        applySavedTheme();
        bindContrastButton();
    };

    applySavedTheme();

    if (isAuthPage) {
        iniciarTemaYEventos();
    } else {
        Promise.all([
            esperarElemento(".logo"),
            esperarElemento(".footer-logo"),
            esperarElemento(".contrast-btn")
        ]).then(iniciarTemaYEventos);
    }
});
