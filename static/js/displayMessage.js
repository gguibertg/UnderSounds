function displayMessage(type, message) {
    // Validar que el tipo sea "error", "success" o "warn"
    if (type !== "error" && type !== "success" && type !== "warn") {
        console.error("El tipo de mensaje debe ser 'error', 'success' o 'warn'.");
        return;
    }

    // Eliminar los divs existentes de tipo error, success o warn si ya existen
    const existingErrorDiv = document.querySelector(".div-error");
    if (existingErrorDiv) {
        existingErrorDiv.remove();
    }
    const existingSuccessDiv = document.querySelector(".div-success");
    if (existingSuccessDiv) {
        existingSuccessDiv.remove();
    }
    const existingWarnDiv = document.querySelector(".div-warn");
    if (existingWarnDiv) {
        existingWarnDiv.remove();
    }

    // Crear un nuevo div de mensaje
    const messageDiv = document.createElement("div");
    messageDiv.className = `div-${type}`;
    const messageContent = document.createElement("p");
    messageContent.textContent = message;
    messageDiv.appendChild(messageContent);

    // Insertar el div dentro de main, justo después del inicio de main y antes de div-bg
    const mainElement = document.querySelector("main");
    const divBgElement = mainElement.querySelector(".div-bg");
    mainElement.insertBefore(messageDiv, divBgElement);
}