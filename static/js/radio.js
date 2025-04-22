document.addEventListener("DOMContentLoaded", function () {
    const playBtn = document.getElementById("play-btn");

    if (playBtn) {
        playBtn.addEventListener("click", function () {
            fetch("../music/radio.html")
                .then(response => response.text())
                .then(data => {
                    document.getElementById("mini-player-placeholder").innerHTML = data;
                    //document.dispatchEvent(new Event("playerLoaded"));
                })
                .catch(error => console.error('Error al cargar el mini player:', error));
        });
    }
});

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('mini-close-btn')) {
        const player = e.target.closest('.mini-player');
        if (player) player.remove();
    }
});


