document.addEventListener("DOMContentLoaded", function () {
    fetch("/header")
        .then(response => response.text())
        .then(data => {
            document.getElementById("header-placeholder").innerHTML = data;
            //document.dispatchEvent(new Event("headerLoaded")); // Evento para dark-mode
        })
        .catch(error => console.error('Error al cargar el header:', error));
});

