document.addEventListener("DOMContentLoaded", function () {
    const verMasBtn = document.getElementById("ver-canciones");
    const cancionesContainer = document.getElementById("canciones-filtradas-placeholder");

    if (verMasBtn && cancionesContainer) {
        verMasBtn.addEventListener("click", function () {
            // Cambiar el display entre "none" y "block"
            if (cancionesContainer.style.display === "none" || cancionesContainer.style.display === "") {
                cancionesContainer.style.display = "block"; // Mostrar el contenedor
                verMasBtn.textContent = "Ver menos canciones"; // Cambiar texto del botón
            } else {
                cancionesContainer.style.display = "none"; // Ocultar el contenedor
                verMasBtn.textContent = "Ver más canciones"; // Cambiar texto del botón
            }
        });
    }
});
