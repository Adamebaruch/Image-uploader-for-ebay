// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('eBay AI Photo Lister application loaded');
    
    // Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.querySelector('.browse-btn');
    const imagePreview = document.getElementById('imagePreview');
    const processBtn = document.getElementById('processImages');
    const ebayForm = document.getElementById('ebayForm');
    
    // Handle file browsing
    browseBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener('change', handleFiles);
    
    // Handle drag and drop
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('highlight');
    });
    
    dropZone.addEventListener('dragleave', function() {
        dropZone.classList.remove('highlight');
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('highlight');
        const files = e.dataTransfer.files;
        handleFiles({ target: { files: files } });
    });
    
    // Process images button
    processBtn.addEventListener('click', processImages);
    
    // Form submission
    ebayForm.addEventListener('submit', createListing);
    
    /**
     * Handle files selected by user
     */
    function handleFiles(e) {
        const files = e.target.files;
        
        if (files.length === 0) return;
        
        // Clear existing previews if needed
        // imagePreview.innerHTML = '';
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // Only process image files
            if (!file.type.match('image.*')) {
                continue;
            }
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                // Create preview element
                const preview = document.createElement('div');
                preview.className = 'image-preview';
                
                const img = document.createElement('img');
                img.src = e.target.result;
                
                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-btn';
                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                removeBtn.addEventListener('click', function() {
                    preview.remove();
                });
                
                preview.appendChild(img);
                preview.appendChild(removeBtn);
                imagePreview.appendChild(preview);
            };
            
            reader.readAsDataURL(file);
        }
        
        // Show the process button if we have images
        processBtn.style.display = 'block';
    }
    
    /**
     * Process images with AI
     */
    function processImages() {
        // Get selected options
        const removeBackground = document.getElementById('removeBackground').checked;
        const enhanceColors = document.getElementById('enhanceColors').checked;
        const removeShadows = document.getElementById('removeShadows').checked;
        const removeDefects = document.getElementById('removeDefects').checked;
        
        // Get all images in preview
        const images = imagePreview.querySelectorAll('.image-preview img');
        
        if (images.length === 0) {
            alert('Please upload at least one image to process');
            return;
        }
        
        // Show loading state
        processBtn.textContent = 'Processing...';
        processBtn.disabled = true;
        
        // Collect image data
        const imageData = [];
        images.forEach(img => {
            imageData.push(img.src);
        });
        
        // Prepare options
        const options = {
            removeBackground,
            enhanceColors,
            removeShadows,
            removeDefects
        };
        
        // Send to backend for processing
        fetch('/api/process-images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                images: imageData,
                options: options
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Replace image previews with processed images
            data.processedImages.forEach((processedImg, index) => {
                if (images[index]) {
                    images[index].src = processedImg;
                    
                    // Add a "processed" indicator
                    const preview = images[index].parentElement;
                    if (!preview.querySelector('.processed-badge')) {
                        const badge = document.createElement('div');
                        badge.className = 'processed-badge';
                        badge.textContent = 'AI Enhanced';
                        preview.appendChild(badge);
                    }
                }
            });
            
            // Update UI
            processBtn.textContent = 'Process Images';
            processBtn.disabled = false;
            
            // Scroll to the form section
            document.querySelector('.listing-form').scrollIntoView({
                behavior: 'smooth'
            });
            
            // Show success message
            showNotification('Images processed successfully!', 'success');
        })
        .catch(error => {
            console.error('Error processing images:', error);
            processBtn.textContent = 'Process Images';
            processBtn.disabled = false;
            
            // For demo purposes, simulate processed images
            simulateProcessedImages();
        });
    }
    
    /**
     * Create eBay listing
     */
    function createListing(e) {
        e.preventDefault();
        
        // Validate form
        const title = document.getElementById('title').value;
        const price = document.getElementById('price').value;
        const category = document.getElementById('category').value;
        const description = document.getElementById('description').value;
        
        if (!title || !price || !category || !description) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Get processed images
        const images = imagePreview.querySelectorAll('.image-preview img');
        const imageUrls = [];
        
        images.forEach(img => {
            imageUrls.push(img.src);
        });
        
        if (imageUrls.length === 0) {
            alert('Please upload and process at least one image');
            return;
        }
        
        // Prepare listing data
        const listingData = {
            title,
            price,
            category,
            description,
            condition: document.getElementById('condition').value,
            shipping: document.getElementById('shipping').value,
            images: imageUrls
        };
        
        // Show loading state
        const submitBtn = ebayForm.querySelector('.submit-btn');
        submitBtn.textContent = 'Creating Listing...';
        submitBtn.disabled = true;
        
        // Send to backend
        fetch('/api/create-listing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(listingData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update UI
            submitBtn.textContent = 'Create eBay Listing';
            submitBtn.disabled = false;
            
            // Show success message
            showNotification('eBay listing created successfully!', 'success');
            
            // Reset form and images
            ebayForm.reset();
            imagePreview.innerHTML = '';
            
            // Redirect to listing view
            setTimeout(() => {
                // window.location.href = `/listing/${data.listingId}`;
                alert('eBay listing created successfully! Listing ID: ' + data.listingId);
            }, 2000);
        })
        .catch(error => {
            console.error('Error creating listing:', error);
            submitBtn.textContent = 'Create eBay Listing';
            submitBtn.disabled = false;
            
            // For demo purposes
            simulateListingCreation();
        });
    }
    
    /**
     * Show notification
     */
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    /**
     * Simulate processed images (for demo)
     */
    function simulateProcessedImages() {
        const images = imagePreview.querySelectorAll('.image-preview img');
        
        images.forEach(img => {
            // Add a slight brightness filter to simulate processing
            img.style.filter = 'brightness(1.1) contrast(1.1)';
            
            // Add a "processed" indicator
            const preview = img.parentElement;
            if (!preview.querySelector('.processed-badge')) {
                const badge = document.createElement('div');
                badge.className = 'processed-badge';
                badge.textContent = 'AI Enhanced';
                badge.style.position = 'absolute';
                badge.style.bottom = '5px';
                badge.style.left = '5px';
                badge.style.backgroundColor = 'rgba(46, 204, 113, 0.8)';
                badge.style.color = 'white';
                badge.style.padding = '3px 8px';
                badge.style.borderRadius = '3px';
                badge.style.fontSize = '10px';
                preview.appendChild(badge);
            }
        });
        
        // Show success message
        showNotification('Images processed successfully! (Demo mode)', 'success');
        
        // Scroll to the form section
        document.querySelector('.listing-form').scrollIntoView({
            behavior: 'smooth'
        });
    }
    
    /**
     * Simulate listing creation (for demo)
     */
    function simulateListingCreation() {
        // Show success message
        showNotification('eBay listing created successfully! (Demo mode)', 'success');
        
        // Reset form and images after a delay
        setTimeout(() => {
            ebayForm.reset();
            imagePreview.innerHTML = '';
            alert('Demo: eBay listing creation simulated. In a real application, this would create an actual eBay listing.');
        }, 2000);
    }
    
    // Initialize with some additional UI adjustments
    function init() {
        // Hide process button initially
        processBtn.style.display = 'none';
        
        // Add notification styles
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                z-index: 9999;
                opacity: 0;
                transform: translateY(-20px);
                transition: opacity 0.3s, transform 0.3s;
            }
            
            .notification.show {
                opacity: 1;
                transform: translateY(0);
            }
            
            .notification.success {
                background-color: #2ecc71;
            }
            
            .notification.error {
                background-color: #e74c3c;
            }
            
            .notification.warning {
                background-color: #f39c12;
            }
            
            .upload-area.highlight {
                background-color: #edf2f7;
                border-color: #2980b9;
            }
            
            .processed-badge {
                position: absolute;
                bottom: 5px;
                left: 5px;
                background-color: rgba(46, 204, 113, 0.8);
                color: white;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Run initialization
    init();
});