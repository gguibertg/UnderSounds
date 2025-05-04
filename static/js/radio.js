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
                    const currentTimeEl = miniPlayerContainer.querySelector("#current-time");
                    const remainingTimeEl = miniPlayerContainer.querySelector("#remaining-time");

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

                    // Función auxiliar para formatear segundos a mm:ss
                    function formatTime(sec) {
                        const m = Math.floor(sec / 60).toString().padStart(1, '0');
                        const s = Math.floor(sec % 60).toString().padStart(2, '0');
                        return `${m}:${s}`;
                    }

                    // En timeupdate, actualiza progreso y tiempos
                    audio.addEventListener("timeupdate", () => {
                        updateProgressBar(audio, progressBar);
                        if (!isNaN(audio.duration)) {
                            currentTimeEl.textContent = formatTime(audio.currentTime);
                            remainingTimeEl.textContent = formatTime(audio.duration);
                        }
                    });

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
        playPauseBtn.textContent = "▶️"; // Cambiar a "Reproducir"
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

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".playlist-btn").forEach(button => {
        button.addEventListener("click", function () {
            // Obtener las listas de canciones (títulos, artistas, portadas, pistas)
            const titulos = button.getAttribute("data-titulos").split("|||");
            const artistas = button.getAttribute("data-artistas").split("|||");
            const covers = button.getAttribute("data-covers").split("|||");
            const id = button.getAttribute("data-pistas").split("|||");

            // Comprobamos que haya al menos una canción
            if (titulos.length > 0) {
                let currentIndex = 0; // Índice de la canción actual

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
                        const currentTimeEl = miniPlayerContainer.querySelector("#current-time");
                        const remainingTimeEl = miniPlayerContainer.querySelector("#remaining-time");

                        // Actualizamos la portada, título y artista
                        const miniCover = miniPlayerContainer.querySelector("#mini-cover");
                        const miniTitle = miniPlayerContainer.querySelector("#mini-title");
                        const miniArtist = miniPlayerContainer.querySelector("#mini-artist");

                        // Función para actualizar la canción actual
                        function updateSong(index) {
                            const song = {
                                titulo: titulos[index],
                                artista: artistas[index],
                                portada: covers[index],
                                id: id[index]
                            };

                            if (miniCover) {
                                miniCover.src = song.portada;
                                miniCover.style.maxWidth = "100px";
                                miniCover.style.maxHeight = "100px";
                            }
                            if (miniTitle) {
                                miniTitle.textContent = song.titulo;
                            }
                            if (miniArtist) {
                                miniArtist.textContent = song.artista;
                            }

                            if (audio) {
                                audio.src = `/mp3/${song.id}`;
                                audio.play();
                            }
                        }

                        // Cargar la primera canción al principio
                        updateSong(currentIndex);

                        // Configurar la acción de play/pause
                        playPauseBtn.addEventListener("click", function () {
                            if (audio.paused) {
                                audio.play();
                            } else {
                                audio.pause();
                            }
                        });

                        // Acción de siguiente canción
                        const nextBtn = miniPlayerContainer.querySelector("#next-btn");
                        nextBtn.addEventListener("click", function () {
                            if (currentIndex < titulos.length - 1) {
                                currentIndex++; // Aumentar el índice para la siguiente canción
                                updateSong(currentIndex);
                            } else {
                                currentIndex = 0; // Volver al principio si es la última canción
                                updateSong(currentIndex);
                            }
                        });

                        // Acción de anterior canción
                        const prevBtn = miniPlayerContainer.querySelector("#prev-btn");
                        prevBtn.addEventListener("click", function () {
                            if (currentIndex > 0) {
                                currentIndex--; // Disminuir el índice para la canción anterior
                                updateSong(currentIndex);
                            } else {
                                currentIndex = titulos.length - 1; // Ir a la última canción si estamos en la primera
                                updateSong(currentIndex);
                            }
                        });

                        // Configuración de la barra de progreso
                        if (progressBar) {
                            // Actualizar la barra de progreso mientras se reproduce el audio
                            audio.addEventListener("timeupdate", function () {
                                const progress = (audio.currentTime / audio.duration) * 100;
                                progressBar.value = progress;
                                if (!isNaN(audio.duration)) {
                                    currentTimeEl.textContent = formatTime(audio.currentTime);
                                    remainingTimeEl.textContent = formatTime(audio.duration);
                                }
                            });

                            // Permitir que el usuario mueva la barra de progreso para cambiar la posición del audio
                            progressBar.addEventListener("input", function () {
                                const newTime = (progressBar.value / 100) * audio.duration;
                                audio.currentTime = newTime;
                            });
                        }

                        // Evento para pasar a la siguiente canción cuando se termine
                        audio.addEventListener("ended", function () {
                            if (currentIndex < titulos.length - 1) {
                                currentIndex++; // Pasar a la siguiente canción
                            } else {
                                currentIndex = 0; // Volver a la primera canción si es la última
                            }
                            updateSong(currentIndex); // Actualizar la canción
                        });

                        // Cerrar el mini-player
                        if (closeBtn) {
                            closeBtn.addEventListener("click", () => {
                                placeholder.innerHTML = ""; // Limpiar el mini-player
                            });
                        }
                    })
                    .catch(error => console.error("Error al cargar el mini-player:", error));
            }
        });
    });
});





