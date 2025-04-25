document.addEventListener("DOMContentLoaded", function () {
    const playBtn = document.getElementById("play-btn");

    if (playBtn) {
        playBtn.addEventListener("click", function () {
            fetch("/play")
                .then(response => response.text())
                .then(data => {
                    const placeholder = document.getElementById("mini-player-placeholder");
                    placeholder.innerHTML = data;

                    // Esperamos al DOM ya actualizado para asignar evento al botón de cerrar
                    const closeBtn = placeholder.querySelector(".mini-close-btn");
                    if (closeBtn) {
                        closeBtn.addEventListener("click", function () {
                            placeholder.innerHTML = ""; // Borra el mini-player del DOM
                        });
                    }
                })
                .catch(error => console.error('Error al cargar el mini-player:', error));
        });
    }
});
