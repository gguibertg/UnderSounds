document.addEventListener("DOMContentLoaded", function () {
    fetch("/header")
        .then(response => response.text())
        .then(data => {
            document.getElementById("header-placeholder").innerHTML = data;
            //document.dispatchEvent(new Event("headerLoaded")); // Evento para dark-mode
        })
        .catch(error => console.error('Error al cargar el header:', error));
});

ocument.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const suggestionsContainer = document.getElementById("search-suggestions");

    let data = []; // Aquí pondrás la lista de artistas, canciones y álbumes.

    // Podrías cargarla dinámicamente también
    fetch("/api/get-search-data") // Cambia esta URL según tu configuración
        .then(response => response.json())
        .then(jsonData => {
            data = jsonData;
        })
        .catch(error => console.error("Error al cargar los datos de búsqueda:", error));


    searchInput.addEventListener("input", function () {
        const query = this.value.toLowerCase();
        suggestionsContainer.innerHTML = "";
    
        if (query.length === 0) {
            suggestionsContainer.style.display = "none";
            return;
        }
    
        const filtered = data.filter(item => item.name.toLowerCase().includes(query));
    
        filtered.forEach(item => {
            const div = document.createElement("div");
            div.textContent = item.name;
            div.classList.add("suggestion-item");
            div.addEventListener("click", function () {
                window.location.href = item.url; // Redirigir al hacer click
            });
            suggestionsContainer.appendChild(div);
        });
    
        suggestionsContainer.style.display = filtered.length ? "block" : "none";
    });

    div.addEventListener("click", function () {
        window.location.href = item.url; // Redirigir al hacer clic
    });
});

