document.addEventListener("DOMContentLoaded", () => {
    const isLoginPage = document.body.classList.contains("login-page");

    let logo = null;
    let fLogo = null;
    let shop = null;

    const elementos = [
        { className: "song-love", icon: "favouriteicon" },
        { className: "song-comment", icon: "commenticon" },
        { className: "song-view", icon: "viewsicon" },
        { className: "song-visible", icon: "isvisibleicon" }
    ];

    const actualizarModo = (modo) => {
        const esOscuro = modo === "dark";
        document.body.classList.toggle("dark-mode", esOscuro);

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
        }
    };

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

    const capturarElementos = () => {
        logo = document.querySelector(".logo");
        fLogo = document.querySelector(".footer-logo");
        shop = document.querySelector(".shop");
    };

    aplicarModoPreferido();

    if (isLoginPage) {
        capturarElementos();
        vincularBoton();
    } else {
        document.addEventListener("headerLoaded", () => {
            capturarElementos();
            aplicarModoPreferido(); // Aplicar modo cuando header ya está listo
        });

        document.addEventListener("footerLoaded", () => {
            vincularBoton(); // Conectar el botón de contraste del footer
        });

        // Extra: intento por si ya están en el DOM antes de que se dispare el evento
        setTimeout(() => {
            capturarElementos();
            vincularBoton();
        }, 500);
    }
});