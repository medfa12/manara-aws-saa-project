const API_ENDPOINT = 'https://l0shs01ytb.execute-api.us-east-1.amazonaws.com/prod'; // Your API Gateway Invoke URL
let selectedFile = null;

// DOM elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const progress = document.getElementById('progress');
const progressBar = document.getElementById('progress-bar');
const result = document.getElementById('result');

// File selection handlers
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#007bff';
});
dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '#ccc';
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#ccc';
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFileSelect(files[0]);
});
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
});

function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    selectedFile = file;
    dropZone.textContent = `Selected: ${file.name}`;
    uploadBtn.disabled = false;
}

// Upload handler
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    try {
        uploadBtn.disabled = true;
        progress.style.display = 'block';
        result.innerHTML = '';
        
        // Step 1: Get presigned upload URL
        const filename = `${Date.now()}-${selectedFile.name}`;
        const uploadResponse = await fetch(`${API_ENDPOINT}/upload?filename=${filename}`, {
            method: 'POST'
        });
        const uploadData = await uploadResponse.json();
        
        if (!uploadResponse.ok) throw new Error(uploadData.error || 'Failed to get upload URL');
        
        progressBar.value = 25;
        
        // Step 2: Upload file to S3
        const uploadResult = await fetch(uploadData.upload_url, {
            method: 'PUT',
            body: selectedFile,
            headers: { 'Content-Type': selectedFile.type }
        });
        
        if (!uploadResult.ok) throw new Error('Upload failed');
        
        progressBar.value = 50;
        
        // Step 3: Wait for processing and get result
        const processedFilename = filename.replace(/\.[^/.]+$/, '_processed.jpg');
        await pollForResult(processedFilename);
        
    } catch (error) {
        result.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    } finally {
        progress.style.display = 'none';
        uploadBtn.disabled = false;
        progressBar.value = 0;
    }
});

async function pollForResult(processedFilename) {
    const maxAttempts = 30; // 30 seconds max
    let attempts = 0;
    
    while (attempts < maxAttempts) {
        try {
            progressBar.value = 50 + (attempts / maxAttempts) * 45;
            
            const viewResponse = await fetch(`${API_ENDPOINT}/view?key=${processedFilename}`);
            const viewData = await viewResponse.json();
            
            if (viewResponse.ok) {
                // Success - display the processed image
                progressBar.value = 100;
                result.innerHTML = `
                    <h3>Processing Complete!</h3>
                    <img src="${viewData.view_url}" alt="Processed image">
                    <p>Your image has been resized to 800x600 and watermarked.</p>
                `;
                return;
            }
            
            // Wait 1 second before next attempt
            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
            
        } catch (error) {
            attempts++;
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
    
    // Timeout
    throw new Error('Processing timed out. Please try again.');
} 