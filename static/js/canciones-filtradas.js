document.addEventListener("DOMContentLoaded", function () {
    const botonesGeneros = document.querySelectorAll(".foto-genero");
    const tipoUsuario = document.body.dataset.tipoUsuario; // <-- Añade esta línea

    botonesGeneros.forEach(boton => {
        boton.addEventListener("click", async event => {
            event.preventDefault();

            displayMessage("warn", "Buscando canciones...", "msg-spawner");

            const generoId = boton.dataset.generoId;

            try {
                const response = await fetch(`${window.location.origin}/songs/genre?id=${encodeURIComponent(generoId)}`);
                if (!response.ok) throw new Error("Error al obtener las canciones");

                const canciones = await response.json();
                const placeholder = document.getElementById("canciones-filtradas-placeholder");
                const tituloSeccion = document.getElementById("titulo_canciones_filtradas");

                placeholder.innerHTML = "";
                placeholder.style.display = "block";
                tituloSeccion.style.display = "block";
                tituloSeccion.style.marginTop = "60px";

                if (canciones.length > 0) {
                    const carruselContainer = document.createElement("div");
                    carruselContainer.classList.add("carrusel-container");

                    canciones.forEach(cancion => {
                        const songItem = document.createElement("div");
                        songItem.classList.add("song-item");
                        songItem.classList.add("div-pannel-sub");
                        
                            let htmlContent = `
                                <img src="${cancion.portada}" alt="${cancion.titulo}" class="foto-artista" onclick="window.location.href='/song?id=${cancion.id}'">
                                <p class="texto-producto">${cancion.titulo}</p>
                                <p class="texto-artista">${cancion.artista}</p>
                            `;
                        
                        if (tipoUsuario) {
                            htmlContent += `
                                <form action="/cart" method="post">
                                    <input type="hidden" name="action" value="add">
                                    <input type="hidden" name="item_id" value="${cancion.id}">
                                    <input type="hidden" name="item_titulo" value="${cancion.titulo}">
                                    <input type="hidden" name="item_portada" value="${cancion.portada}">
                                    <input type="hidden" name="artist_name" value="${cancion.artista}">
                                    <input type="hidden" name="item_desc" value="${cancion.descripcion || ''}">
                                    <input type="hidden" name="item_precio" value="${cancion.precio || 0}">
                                    <button type="submit" class="button-comprar-item">Añadir</button>
                                </form>
                            `;
                        }
                        songItem.innerHTML = htmlContent;
                        carruselContainer.appendChild(songItem);
                    });

                    placeholder.appendChild(carruselContainer);
                    displayMessage("success", "Búsqueda completada", "msg-spawner");

                } else {
                    placeholder.style.display = "none";
                    displayMessage("error", "No hay canciones para este género", "msg-spawner");
                }

            } catch (error) {
                console.error(error);
                displayMessage("error", `Error en la búsqueda: ${error.message}`, "msg-spawner");
            }
        });
    });
});
