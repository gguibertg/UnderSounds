document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("cover-upload").addEventListener("change", function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById("cover-preview").src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});
