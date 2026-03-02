document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileDetails = document.getElementById('file-details');
    const fileNameEl = document.getElementById('filename');
    const fileSizeEl = document.getElementById('filesize');
    const btnCompress = document.getElementById('btn-compress');

    const statusText = document.getElementById('status-text');
    const progressPercent = document.getElementById('progress-percent');
    const progressFill = document.getElementById('progress-fill');
    const errorMsg = document.getElementById('error-msg');
    const btnDownload = document.getElementById('btn-download');

    let selectedFile = null;
    const CHUNK_SIZE = 5 * 1024 * 1024; // 5 MB per chunk

    // --- DRAG & DROP UI ---
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (!file.type.startsWith('video/')) {
            alert('Por favor, selecciona un archivo de video válido.');
            return;
        }
        selectedFile = file;
        fileNameEl.textContent = file.name;
        fileSizeEl.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
        fileDetails.classList.remove('hidden');
        btnCompress.removeAttribute('disabled');
    }

    // --- UPLOAD LOGIC ---
    btnCompress.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Extract quality setting
        const quality = document.querySelector('input[name="quality"]:checked').value;

        btnCompress.setAttribute('disabled', 'true');
        btnCompress.textContent = "PROCESANDO...";
        dropZone.style.pointerEvents = 'none';

        updateProgressUI("INICIANDO", 0);

        try {
            // 1. Start Session
            const resStart = await fetch('/api/v1/upload/start/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: selectedFile.name })
            });
            const dataStart = await resStart.json();
            const taskId = dataStart.task_id;

            // 2. Upload Chunks (Sequential for stability on huge files)
            const totalChunks = Math.ceil(selectedFile.size / CHUNK_SIZE);
            updateProgressUI("SUBIENDO", 0);

            for (let i = 0; i < totalChunks; i++) {
                const start = i * CHUNK_SIZE;
                const end = Math.min(start + CHUNK_SIZE, selectedFile.size);
                const chunk = selectedFile.slice(start, end);

                const formData = new FormData();
                formData.append('file', chunk);
                formData.append('chunk_index', i);
                formData.append('total_chunks', totalChunks);
                formData.append('quality', quality);

                const resChunk = await fetch(`/api/v1/upload/chunk/${taskId}/`, {
                    method: 'POST',
                    body: formData
                });

                if (!resChunk.ok) throw new Error("Fallo al subir fragmento.");

                // If not last chunk, predict progress (only upload portion)
                if (i < totalChunks - 1) {
                    const progress = ((i + 1) / totalChunks) * 100;
                    // Cap UI at 99% for upload phase
                    updateProgressUI("SUBIENDO", (progress * 0.3).toFixed(1)); // Upload takes 30% of fake bar
                }
            }

            // 3. Polling for processing status
            updateProgressUI("COMPRIMIENDO...", 0); // Reset for actual FFmpeg progress
            pollTaskStatus(taskId);

        } catch (e) {
            updateProgressUI("ERROR", 0);
            errorMsg.textContent = e.message;
            errorMsg.classList.remove('hidden');
            btnCompress.removeAttribute('disabled');
            btnCompress.textContent = "REINTENTAR";
            dropZone.style.pointerEvents = 'auto';
        }
    });

    function pollTaskStatus(taskId) {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/v1/status/${taskId}/`);
                const data = await res.json();

                if (data.status === 'COMPLETED') {
                    clearInterval(interval);
                    updateProgressUI("COMPLETADO", 100);
                    statusText.classList.remove('status-active');
                    statusText.classList.add('status-success');
                    progressFill.style.background = 'var(--success)';
                    progressFill.style.boxShadow = '0 0 20px rgba(50, 215, 75, 0.4)';

                    btnCompress.classList.add('hidden');
                    btnDownload.classList.remove('hidden');
                    btnDownload.href = data.download_url;
                }
                else if (data.status === 'FAILED') {
                    clearInterval(interval);
                    updateProgressUI("ERROR CRÍTICO", 0);
                    errorMsg.textContent = data.error_message || "Error desconocido";
                    errorMsg.classList.remove('hidden');
                }
                else {
                    updateProgressUI("COMPRIMIENDO...", data.progress.toFixed(1));
                    statusText.classList.add('status-active');
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 1500); // Poll every 1.5s
    }

    function updateProgressUI(status, percent) {
        statusText.textContent = status;
        progressPercent.textContent = `${percent}%`;
        progressFill.style.width = `${percent}%`;
    }

});
