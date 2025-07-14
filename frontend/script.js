const API_ENDPOINT = 'https://l0shs01ytb.execute-api.us-east-1.amazonaws.com/prod'; // Your API Gateway endpoint

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const progress = document.getElementById('progress');
const progressBar = document.getElementById('progress-bar');
const result = document.getElementById('result');
let selectedFile = null;

dropZone.addEventListener('click', () => fileInput.click());


fileInput.addEventListener('change', (e) => {
    handleFile(e.target.files[0]);
});


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
    handleFile(e.dataTransfer.files[0]);
});


uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        result.innerHTML = 'Please select a file first.';
        return;
    }
    await uploadFile(selectedFile);
});



function handleFile(file) {
    if (file && file.type.startsWith('image/')) {
        selectedFile = file;
        dropZone.textContent = `Selected: ${file.name}`;
    } else {
        selectedFile = null;
        dropZone.textContent = 'Invalid file type. Please select an image.';
    }
}

async function uploadFile(file) {
    progress.style.display = 'block';
    result.innerHTML = '';
    
    try {
    
        const filename = `${Date.now()}-${file.name}`;
        const contentType = file.type;
        
        const uploadResponse = await fetch(`${API_ENDPOINT}/upload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: filename, contentType: contentType })
        });
        
        const uploadData = await uploadResponse.json();
        
        if (!uploadResponse.ok) {
            throw new Error(`Failed to get presigned URL: ${uploadData.error}`);
        }

        const uploadUrl = uploadData.upload_url;
        progressBar.value = 25;

    
        const uploadResult = await fetch(uploadUrl, {
            method: 'PUT',
            body: file,
            headers: {
                'Content-Type': contentType
            }
        });

        if (!uploadResult.ok) {
            throw new Error('S3 upload failed.');
        }

        progressBar.value = 100;
        
  
        const processedKey = `${filename.split('.').slice(0, -1).join('.')}_processed.jpg`;
        await new Promise(resolve => setTimeout(resolve, 5000)); 
        const viewResponse = await fetch(`${API_ENDPOINT}/view?key=${encodeURIComponent(processedKey)}`);
        if (!viewResponse.ok) {
            throw new Error('Failed to get view URL');
        }
        const viewData = await viewResponse.json();
        const processedUrl = viewData.view_url;
        
        result.innerHTML = `
            <h3>Processing Complete!</h3>
            <img src="${processedUrl}" alt="Processed image" style="max-width: 100%;">
            <p>Image uploaded and processed successfully.</p>
        `;

    } catch (error) {
        result.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        console.error(error);
    } finally {
        progress.style.display = 'none';
        progressBar.value = 0;

    }
} 