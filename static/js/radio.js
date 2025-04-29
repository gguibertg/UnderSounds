document.addEventListener("DOMContentLoaded", function () {
    const playBtn = document.getElementById("play-btn");

    if (playBtn) {
        playBtn.addEventListener("click", function () {
            const songSource = playBtn.getAttribute("data-source");
            const songTitle = playBtn.getAttribute("data-title");
            const songArtist = playBtn.getAttribute("data-artist");
            const songCover = playBtn.getAttribute("data-cover");

            if (!songSource) {
                console.error("No se ha proporcionado una fuente de canción.");
                return;
            }

            // Realizamos el fetch para cargar el mini-player
            fetch("/play")
                .then(response => response.text())
                .then(data => {
                    // Cargar el mini-player en el contenedor placeholder
                    const placeholder = document.getElementById("mini-player-placeholder");
                    placeholder.innerHTML = data;

                    // Configuramos los controles después de cargar el mini-player
                    const miniPlayerContainer = placeholder.querySelector(".mini-player");
                    const audio = miniPlayerContainer.querySelector("#mini-audio");
                    const playPauseBtn = miniPlayerContainer.querySelector("#play-pause-btn");
                    const progressBar = miniPlayerContainer.querySelector(".mini-progress");
                    const closeBtn = miniPlayerContainer.querySelector(".mini-close-btn");

                    // Actualizar portada, título y artista con un retardo para asegurarnos de que el DOM está completamente listo
                    const miniCover = miniPlayerContainer.querySelector("#mini-cover");
                    const miniTitle = miniPlayerContainer.querySelector("#mini-title");
                    const miniArtist = miniPlayerContainer.querySelector("#mini-artist");

                    // Garantizar que la portada, título y artista se asignen correctamente
                    if (miniCover) {
                        miniCover.src = songCover;
                        miniCover.style.maxWidth = "100px"; // Limitar el tamaño de la portada
                        miniCover.style.maxHeight = "100px"; // Limitar el tamaño de la portada
                    }
                    if (miniTitle) {
                        miniTitle.textContent = songTitle;
                    }
                    if (miniArtist) {
                        miniArtist.textContent = songArtist;
                    }

                    // Establecer la fuente del audio
                    if (audio) {
                        audio.src = songSource;
                        setupAudioPlayer(audio, playPauseBtn, progressBar);
                    }

                    // Cerrar el mini-player
                    if (closeBtn) {
                        closeBtn.addEventListener("click", () => {
                            placeholder.innerHTML = "";  // Limpiar el mini-player
                        });
                    }
                })
                .catch(error => console.error("Error al cargar el mini-player:", error));
        });
    }
});

// Función para configurar el reproductor de audio
function setupAudioPlayer(audio, playPauseBtn, progressBar) {
    // Reproducir automáticamente al cargarse
    audio.play().then(() => {
        // Cuando el audio comienza a reproducirse, configurar la barra de progreso
        updateProgressBar(audio, progressBar);
    }).catch(error => {
        console.error("Error al intentar reproducir el audio automáticamente:", error);
    });

    audio.addEventListener("timeupdate", () => {
        // Actualizar la barra de progreso mientras se reproduce la canción
        updateProgressBar(audio, progressBar);
    });

    playPauseBtn.addEventListener("click", () => {
        togglePlayPause(audio, playPauseBtn); // Alternar entre pausar y reproducir
    });

    progressBar.addEventListener("input", () => {
        seekAudio(audio, progressBar); // Buscar una posición específica en el audio
    });
}

// Función para alternar entre play y pause
function togglePlayPause(audio, playPauseBtn) {
    if (audio.paused) {
        audio.play();
        playPauseBtn.textContent = "⏸️"; // Cambiar a "Pausa"
    } else {
        audio.pause();
        playPauseBtn.textContent = "⏯️"; // Cambiar a "Reproducir"
    }
}

// Función para actualizar la barra de progreso
function updateProgressBar(audio, progressBar) {
    if (!isNaN(audio.duration)) {
        // Actualizar el valor de la barra de progreso según el tiempo de reproducción
        progressBar.value = (audio.currentTime / audio.duration) * 100;
    }
}

// Función para avanzar o retroceder en el audio con la barra de progreso
function seekAudio(audio, progressBar) {
    if (!isNaN(audio.duration)) {
        audio.currentTime = (progressBar.value / 100) * audio.duration; // Mover el audio al tiempo seleccionado en la barra de progreso
    }
}
