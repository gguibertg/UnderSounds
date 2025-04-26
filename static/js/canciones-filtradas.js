document.addEventListener("DOMContentLoaded", function () {
    const botonesGeneros = document.querySelectorAll(".foto-genero");

    botonesGeneros.forEach((boton) => {
        boton.addEventListener("click", async function (event) {
            // Evitar que el formulario se envíe (recurso de la página)
            event.preventDefault();

            // Obtener el ID del género desde el atributo `data-genero-id`
            const generoId = boton.getAttribute("data-genero-id");

            try {
                // Hacer la llamada a la API para obtener canciones del género
                const url = `${window.location.origin}/songs/genre?id=${encodeURIComponent(generoId)}`;
                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error("Error al obtener las canciones");
                }

                const canciones = await response.json();
                console.log("Canciones recibidas:", canciones);

                // Obtenemos el contenedor de las canciones filtradas
                const cancionesContainer = document.getElementById("canciones-filtradas-placeholder");
                const titulo_seccion = document.getElementById("titulo_canciones_filtradas");

                // Solo proceder si el objeto canciones no está vacío ni es null
                if (canciones && canciones.length > 0) {
                    // Mostrar el contenedor de canciones
                    cancionesContainer.style.display = "block";
                    titulo_seccion.style.display = "block";
                    titulo_seccion.style.marginTop = "60px";

                    // Limpiar el contenedor antes de agregar nuevas canciones
                    cancionesContainer.innerHTML = ""; 

                    // Crear el contenedor principal del carrusel
                    const carruselContainer = document.createElement("div");
                    carruselContainer.classList.add("carrusel-container");

                    // Crear la lista de canciones dinámicamente
                    canciones.forEach(cancion => {
                        // Crear el contenedor de cada canción
                        const songItem = document.createElement("div");
                        songItem.style.margin = "0 1rem";

                        // Crear la imagen de la canción (portada)
                        const img = document.createElement("img");
                        img.src = 'https://i.etsystatic.com/33525265/r/il/f91956/3592770954/il_fullxfull.3592770954_kdac.jpg' 
                        //img.src = cancion.portada; // Aquí tomamos la portada
                        img.alt = cancion.titulo;  // Usamos el título como alt
                        img.classList.add("foto-artista");
                        img.onclick = function() {
                            window.location.href = `/song?id=${cancion.id}`;
                        };

                        // Crear el párrafo con el título de la canción (nombre de la canción)
                        const titulo = document.createElement("p");
                        titulo.classList.add("texto-producto");
                        titulo.textContent = cancion.titulo; // Solo el título de la canción

                        // Crear el párrafo con el nombre del artista
                        const artista = document.createElement("p");
                        artista.classList.add("texto-artista");
                        artista.textContent = cancion.artista; // El nombre del artista

                        // Crear el formulario y el botón de "Añadir"
                        const form = document.createElement("form");
                        form.action = "/cart";
                        form.method = "post";
                        form.innerHTML = `
                            <input type="hidden" name="action" value="add">
                            <input type="hidden" name="item_id" value="${cancion.id}">
                            <input type="hidden" name="item_titulo" value="${cancion.titulo}">
                            <input type="hidden" name="item_portada" value="${cancion.portada}">
                            <input type="hidden" name="artist_name" value="${cancion.artista}">
                            <input type="hidden" name="item_desc" value="${cancion.descripcion || ''}">
                            <input type="hidden" name="item_precio" value="${cancion.precio || 0}">
                            <button type="submit" class="button-comprar-item">Añadir</button>
                        `;

                        // Añadir la imagen, el título y el nombre del artista al contenedor de la canción
                        songItem.appendChild(img);
                        songItem.appendChild(titulo);
                        songItem.appendChild(artista);
                        songItem.appendChild(form);

                        // Añadir el item al carrusel
                        carruselContainer.appendChild(songItem);
                    });
                    
                    // Añadir el carrusel al contenedor de canciones
                    cancionesContainer.appendChild(carruselContainer);
                } else {
                    // Si no hay canciones, ocultamos el contenedor y mostramos un mensaje
                    cancionesContainer.style.display = "none";
                    alert("No hay canciones disponibles para este género.");
                }

            } catch (error) {
                console.error("Error:", error);
            }
        });
    });
});