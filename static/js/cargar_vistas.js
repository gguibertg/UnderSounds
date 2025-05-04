
export async function irACancion(songId) {
    const response = await fetch('/song', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ song_id: songId })
    });

    const result = await response.json();
    if (response.ok) {
        window.location.href = result.redirect_url;
    } else {
        displayMessage("error", "Error al obtener la canción");
    }
}

export async function irAlbum(albumId) {
    const response = await fetch('/album', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ album_id: albumId })
    });

    const result = await response.json();
    if (response.ok) {
        window.location.href = result.redirect_url;
    } else {
        displayMessage("error", "Error al obtener el álbum");
    }
}