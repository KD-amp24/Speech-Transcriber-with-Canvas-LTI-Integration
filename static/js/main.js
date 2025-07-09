document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const fileInput = document.querySelector('input[type="file"]');
    const submitBtn = form.querySelector('button[type="submit"]');

    const recordBtn = document.getElementById('recordBtn');
    const stopBtn = document.getElementById('stopBtn');
    const status = document.getElementById('recordingStatus');

    let mediaRecorder;
    let audioChunks = [];

    // Spinner setup
    let spinnerContainer = document.getElementById('loading-spinner');
    if (!spinnerContainer) {
        spinnerContainer = document.createElement('div');
        spinnerContainer.id = 'loading-spinner';
        spinnerContainer.style.display = 'none';
        spinnerContainer.style.textAlign = 'center';
        spinnerContainer.style.marginTop = '15px';
        spinnerContainer.innerHTML = `
            <img src="/static/img/spinner.gif" alt="Loading..." width="50" />
            <p>Transcribing... Please wait.</p>
        `;
        form.appendChild(spinnerContainer);
    }

    // Form file upload handler
    if (form && fileInput && submitBtn) {
        form.addEventListener('submit', function (e) {
            if (!fileInput.files.length) {
                e.preventDefault();
                alert('Please select a file before submitting.');
                return;
            }
            spinnerContainer.style.display = 'block';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Uploading...';
        });
    }

    // Recording logic
    if (recordBtn && stopBtn && status) {
        recordBtn.addEventListener('click', async () => {
            audioChunks = [];
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = e => {
                    if (e.data.size > 0) audioChunks.push(e.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const formData = new FormData();
                    formData.append('audio_file', audioBlob, 'recording.webm');

                    // Show spinner
                    spinnerContainer.style.display = 'block';
                    status.textContent = 'Uploading recording...';

                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    })
                        .then(res => res.text())
                        .then(html => {
                            document.open();
                            document.write(html);
                            document.close();
                        })
                        .catch(err => {
                            alert('Error uploading recording: ' + err);
                        });
                };

                mediaRecorder.start();
                status.textContent = 'Recording...';
                recordBtn.disabled = true;
                stopBtn.disabled = false;
            } catch (err) {
                alert('Microphone access denied or error: ' + err.message);
            }
        });

        stopBtn.addEventListener('click', () => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                status.textContent = 'Processing...';
                stopBtn.disabled = true;
                recordBtn.disabled = false;
            }
        });
    }

    // Scroll to results if available
    const results = document.querySelector('#results');
    if (results) {
        results.scrollIntoView({ behavior: 'smooth' });
    }
});
