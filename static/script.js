// script.js

// Flash message modal logic
const messages = JSON.parse(document.getElementById('flash-messages-data').textContent);
const flashModal = document.getElementById('flash-modal');
const modalContent = flashModal.querySelector('.modal-content');

if (messages.length > 0) {
  const [category, text] = messages[0];
  modalContent.textContent = text;
  modalContent.className = "modal-content " + category;
  flashModal.style.display = "flex";

  setTimeout(() => {
    flashModal.style.display = "none";
  }, 4000);
}

// Confirm modal open/close
function openConfirmModal(filename) {
  document.getElementById('confirm-filename').value = filename;
  document.getElementById('confirm-message').textContent =
    `Are you sure you want to delete "${filename}"?`;
  document.getElementById('confirm-modal').style.display = 'flex';
}

function closeConfirmModal() {
  document.getElementById('confirm-modal').style.display = 'none';
}

// Upload modal open/close
function openUploadModal() {
  document.getElementById('upload-modal').style.display = 'flex';
}

function closeUploadModal() {
  document.getElementById('upload-modal').style.display = 'none';
}

// Drag and Drop support for PDFs on the #drop-zone element
const dropZone = document.getElementById('drop-zone');

// Hidden file input inside drop zone
const hiddenFileInput = document.getElementById('hidden_pdf_file');
// Visible file input inside modal
const modalFileInput = document.getElementById('pdf_file');
// Choose file button in drop zone
const chooseFileBtn = document.getElementById('choose-file-btn');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropZone.addEventListener(eventName, e => e.preventDefault());
});

['dragenter', 'dragover'].forEach(eventName => {
  dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'));
});

['dragleave', 'drop'].forEach(eventName => {
  dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'));
});

dropZone.addEventListener('drop', e => {
  const files = e.dataTransfer.files;
  if (files.length === 0) return;

  const pdfFile = Array.from(files).find(file => file.type === 'application/pdf');
  if (!pdfFile) {
    alert('Please drop a PDF file.');
    return;
  }

  openUploadModal();

  // Delay setting files until modal is visible
  setTimeout(() => {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(pdfFile);
    modalFileInput.files = dataTransfer.files;

    document.getElementById('request_title').focus();
  }, 100);
});

// Choose file button triggers hidden file input click
chooseFileBtn.addEventListener('click', () => {
  hiddenFileInput.click();
});

// When file is chosen via hidden file input (file manager)
hiddenFileInput.addEventListener('change', () => {
  if (hiddenFileInput.files.length > 0) {
    openUploadModal();

    // Copy file to modal input after modal shows
    setTimeout(() => {
      modalFileInput.files = hiddenFileInput.files;
      document.getElementById('request_title').focus();
    }, 100);
  }
});
