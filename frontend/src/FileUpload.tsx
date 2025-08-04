import React from 'react';
import { showToast } from './components/Toast'

export function FileUpload() {
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!fileInputRef.current?.files?.[0]) return;
    const file = fileInputRef.current.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const responseData = await response.json();
      showToast(`ℹ️ ${responseData.message}`, 3000);
    } else {
      console.error("File upload failed");
    }
  }

  const handleClear = async () => {
    const response = await fetch('http://localhost:5000/api/clear-store', {
      method: 'GET',
    });
    

    if (response.ok) {
      const responseData = await response.json();
      showToast(`ℹ️ ${responseData.message}`, 3000);
      if (fileInputRef.current) {
        fileInputRef.current.value = ''; // Clear the file input
      }
    } else {
      console.error("Failed to clear upload");
    }
  }

  return (
    <div className='file-upload-container'>
      <input type="file" ref={fileInputRef} />
        <button onClick={handleUpload}>Upload</button>
        <button onClick={handleClear}>Clear</button>
    </div>
  );
}