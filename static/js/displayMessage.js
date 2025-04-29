function displayMessage(type, message, containerId = "") {
    // Validar que el tipo sea "error", "success" o "warn"
    if (type !== "error" && type !== "success" && type !== "warn") {
        console.error("El tipo de mensaje debe ser 'error', 'success' o 'warn'.");
        return;
    }

    // Obtener el contenedor donde se colocará el mensaje
    let containerElement;
    if (containerId === "") {
        containerElement = document.querySelector("main");
        if (!containerElement) {
            console.error("No se encontró una etiqueta <main> en el documento.");
            return;
        }
    } else {
        containerElement = document.getElementById(containerId);
        if (!containerElement) {
            console.error(`No se encontró un elemento con el ID '${containerId}'.`);
            return;
        }
    }

    // Eliminar los divs existentes de tipo error, success o warn si ya existen en el contenedor
    const existingErrorDiv = containerElement.querySelector(".div-error");
    if (existingErrorDiv) {
        existingErrorDiv.remove();
    }
    const existingSuccessDiv = containerElement.querySelector(".div-success");
    if (existingSuccessDiv) {
        existingSuccessDiv.remove();
    }
    const existingWarnDiv = containerElement.querySelector(".div-warn");
    if (existingWarnDiv) {
        existingWarnDiv.remove();
    }

    // Crear un nuevo div de mensaje
    const messageDiv = document.createElement("div");
    messageDiv.className = `div-${type}`;
    const messageContent = document.createElement("p");
    messageContent.textContent = message;
    messageDiv.appendChild(messageContent);

    // Insertar el div justo después del contenedor especificado, antes de cualquier otro contenido
    containerElement.insertAdjacentElement("afterbegin", messageDiv);

    // Forzar a la página a desplazarse al mensaje con desplazamiento suave
    window.scrollTo({
        top: messageDiv.offsetTop,
        behavior: "smooth"
    });
}