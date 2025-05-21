// Modal image search logic
const imageModal = document.getElementById('imageSearchModal');
const openBtn = document.getElementById('openImageModal');
const closeBtn = document.getElementById('closeImageModal');
openBtn.onclick = () => imageModal.classList.add('active');
closeBtn.onclick = () => imageModal.classList.remove('active');
window.onclick = function(e) {
  if (e.target === imageModal) imageModal.classList.remove('active');
};

// Kéo-thả
const dropArea = document.getElementById('dropArea');
const imageInput = document.getElementById('imageInput');
const searchLoading = document.getElementById('imageSearchLoading');
const textSearchBar = document.getElementById('textSearchBar');
const searchForm = document.getElementById('searchForm');

// Drag & drop
['dragenter','dragover'].forEach(evt =>
  dropArea.addEventListener(evt, e => { e.preventDefault(); dropArea.classList.add('dragover'); }, false));
['dragleave','drop'].forEach(evt =>
  dropArea.addEventListener(evt, e => { e.preventDefault(); dropArea.classList.remove('dragover'); }, false));
dropArea.addEventListener('drop', e => {
  const file = e.dataTransfer.files[0];
  if (file) handleImageSearchFile(file);
});

// Click upload link
let isProcessing = false;
imageInput.onchange = e => { 
    if (isProcessing) return;
    if (e.target.files[0]) handleImageSearchFile(e.target.files[0]);
    e.target.value = "";
};
function handleImageSearchFile(file) {
    if (isProcessing) return;
    isProcessing = true;
    if (!file.type.startsWith('image/')) { alert('Only image files are accepted!'); isProcessing = false; return; }
    searchLoading.style.display = 'block';
    const formData = new FormData();
    formData.append('file', file);
    fetch('http://127.0.0.1:8000/image-process', { method:'POST', body: formData })
      .then(res => res.json().then(data=>({status:res.status,body:data})))
      .then(({status,body}) => {
        searchLoading.style.display = 'none';
        isProcessing = false;
        if (status!==200) { alert(body.detail||'Image search failed!'); return;}
        if (body.labels && body.labels.length > 0) {
          const label = body.labels[0].description || '';
          if (!label) { alert('Could not recognize product name.'); return; }
          textSearchBar.value = label;
          imageModal.classList.remove('active');
          searchForm.submit();
        } else alert('Could not detect product name from image.');
      }).catch(err=>{
        searchLoading.style.display='none'; 
        alert('Error: '+err.message); 
        isProcessing = false;
      });
}