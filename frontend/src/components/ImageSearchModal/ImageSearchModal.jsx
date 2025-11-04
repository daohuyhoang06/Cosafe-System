import { useState } from 'react';
import { imageService } from '@/services';
import './ImageSearchModal.css';

const ImageSearchModal = ({ isOpen, onClose, onSearch }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

    const handleDragEnter = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) {
            handleImageFile(file);
        }
    };

    const handleFileInput = (e) => {
        const file = e.target.files[0];
        if (file) {
            handleImageFile(file);
        }
        e.target.value = '';
    };

    const handleImageFile = async (file) => {
        if (isProcessing) return;

        if (!file.type.startsWith('image/')) {
            alert('Only image files are accepted!');
            return;
        }

        setIsProcessing(true);

        try {
            const data = await imageService.processImage(file);

            if (data.labels && data.labels.length > 0) {
                const productName = data.labels[0].description || '';
                if (productName) {
                    onSearch(productName);
                    onClose();
                } else {
                    alert('Could not recognize product name.');
                }
            } else {
                alert('Could not detect product name from image.');
            }
        } catch (error) {
            alert('Error processing image: ' + error.message);
        } finally {
            setIsProcessing(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className={`image-search-modal ${isOpen ? 'active' : ''}`} onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="close-modal" onClick={onClose}>&times;</span>
                <h2>Search by Image</h2>

                <div
                    className={`drop-area ${isDragging ? 'dragover' : ''}`}
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                >
                    <img
                        src="/assets/images/imagesearching.jpg"
                        alt="Drop area"
                        className="drop-image"
                    />
                    <p>
                        Drag an image here or{' '}
                        <label htmlFor="imageInput" className="upload-link">
                            upload a file
                        </label>
                    </p>
                    <input
                        type="file"
                        id="imageInput"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={handleFileInput}
                    />
                </div>

                {isProcessing && (
                    <div className="loading">Processing image...</div>
                )}
            </div>
        </div>
    );
};

export default ImageSearchModal;
