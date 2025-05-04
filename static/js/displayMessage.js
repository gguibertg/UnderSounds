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

    // Posicionar el mensaje como flotante
    messageDiv.style.position   = "fixed";
    messageDiv.style.top        = "20px";
    messageDiv.style.left       = "50%";
    messageDiv.style.transform  = "translateX(-50%)";
    messageDiv.style.marginLeft  = "30px";   // margen adicional a la izquierda
    messageDiv.style.marginRight = "30px";  // margen adicional a la derecha
    messageDiv.style.maxWidth    = "calc(100% - 60px)"; // evita que crezca más allá de márgenes
    messageDiv.style.width       = "auto";  // tamaño según contenido
    messageDiv.style.zIndex     = "9999";

    // Añadir padding y ajustar la fuente
    messageDiv.style.padding    = "10px 30px"; // 10px vertical, 30px horizontal
    messageDiv.style.fontSize   = "1.15em";     // fuente ligeramente más grande

    const messageContent = document.createElement("p");
    messageContent.textContent = message;
    messageDiv.appendChild(messageContent);

    // Insertar el div justo después del contenedor especificado, antes de cualquier otro contenido
    containerElement.insertAdjacentElement("afterbegin", messageDiv);

    // Mantener visible 5s, luego hacer fade de 2s y eliminar
    messageDiv.style.opacity = "1";
    messageDiv.style.transition = "opacity 2.5s ease";
    setTimeout(() => {
        messageDiv.style.opacity = "0";
        setTimeout(() => {
            messageDiv.remove();
        }, 2500);
    }, 3000);
}