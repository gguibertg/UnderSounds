function displayMessage(type, message) {
    // Validar que el tipo sea "error" o "success"
    if (type !== "error" && type !== "success") {
        console.error("El tipo de mensaje debe ser 'error' o 'success'.");
        return;
    }

    // Eliminar los divs existentes de tipo error o success si ya existen
    const existingErrorDiv = document.querySelector(".div-error");
    if (existingErrorDiv) {
        existingErrorDiv.remove();
    }
    const existingSuccessDiv = document.querySelector(".div-success");
    if (existingSuccessDiv) {
        existingSuccessDiv.remove();
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