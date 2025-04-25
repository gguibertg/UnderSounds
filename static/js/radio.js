document.addEventListener("DOMContentLoaded", function () {
    const playBtn = document.getElementById("play-btn");

    if (playBtn) {
        playBtn.addEventListener("click", function () {
            // Obtener la ruta del archivo desde el atributo 'data-source'
            const songSource = playBtn.getAttribute("data-source");

            if (!songSource) {
                console.error("No se ha proporcionado una fuente de canción.");
                return;
            }

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

                    // Agregamos funcionalidades adicionales para controlar el audio
                    const audio = placeholder.querySelector("#mini-audio");
                    const playPauseBtn = placeholder.querySelector("#play-pause-btn");
                    const progressBar = placeholder.querySelector(".mini-progress");

                    if (audio) {
                        audio.src = songSource; // Establecemos la fuente del audio
                        setupAudioPlayer(audio, playPauseBtn, progressBar);
                    }

                })
                .catch(error => console.error('Error al cargar el mini-player:', error));
        });
    }
});

// Función para configurar el reproductor de audio
function setupAudioPlayer(audio, playPauseBtn, progressBar) {
    audio.play();

    if (playPauseBtn) {
        playPauseBtn.textContent = "⏸️"; // Estado inicial al reproducir
        playPauseBtn.addEventListener("click", () => togglePlayPause(audio, playPauseBtn));
    }

    if (progressBar) {
        audio.addEventListener("timeupdate", () => updateProgress(audio, progressBar));
        progressBar.addEventListener("input", () => seekAudio(audio, progressBar));
    }
}

// Función para alternar entre play y pause
function togglePlayPause(audio, button) {
    if (audio.paused) {
        audio.play();
        button.textContent = "⏸️";
    } else {
        audio.pause();
        button.textContent = "⏯️";
    }
}

// Función para actualizar la barra de progreso
function updateProgress(audio, progressBar) {
    if (!isNaN(audio.duration)) {
        progressBar.value = (audio.currentTime / audio.duration) * 100;
    }
}

// Función para avanzar o retroceder en el audio con la barra de progreso
function seekAudio(audio, progressBar) {
    if (!isNaN(audio.duration)) {
        audio.currentTime = (progressBar.value / 100) * audio.duration;
    }
}
