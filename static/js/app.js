document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Mostrar spinner de carga
    document.getElementById('upload-section').style.display = 'none';
    document.getElementById('loading-section').style.display = 'block';
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Ocultar spinner
            document.getElementById('loading-section').style.display = 'none';
            
            // Mostrar botón para ver resultados
            const resultsSection = document.getElementById('results-section');
            resultsSection.style.display = 'block';
            
            // Configurar el botón para redirigir al dashboard
            document.getElementById('view-dashboard').addEventListener('click', function() {
                window.location.href = `/dashboard.html?file=${data.filename}`;
            });
        } else {
            alert(data.error || 'Error al procesar el archivo');
            document.getElementById('upload-section').style.display = 'block';
            document.getElementById('loading-section').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al subir el archivo');
        document.getElementById('upload-section').style.display = 'block';
        document.getElementById('loading-section').style.display = 'none';
    });
});