function startTimer(duration, display) {
    let timer = duration, minutes, seconds;

    function updateDisplay() {
        minutes = parseInt((timer % 3600) / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;
    }

    updateDisplay(); // Mostrar tiempo inicial

    const interval = setInterval(function () {
        timer--;
        updateDisplay();

        if (timer < 0) {
            clearInterval(interval);
            window.location.href = "/purchased"; // Cambia la URL si hace falta
        }
    }, 1000);
}

window.addEventListener("DOMContentLoaded", () => {
    const display = document.getElementById("timer");
    if (display) {
        const duration = 10; // Cambia el tiempo según necesidad
        startTimer(duration, display);
    }
});
