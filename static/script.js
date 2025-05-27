// script.js

document.addEventListener('DOMContentLoaded', () => {
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
  window.openConfirmModal = function(download_link, title) {
    document.getElementById('confirm-filename').value = download_link;
    document.getElementById('confirm-title').value = title;
    document.getElementById('confirm-message').textContent =
      `Are you sure you want to delete "${title}"?`;
    document.getElementById('confirm-modal').style.display = 'flex';
  };

  window.closeConfirmModal = function() {
    document.getElementById('confirm-modal').style.display = 'none';
  };

  // Upload modal open/close
  window.openUploadModal = function() {
    document.getElementById('upload-modal').style.display = 'flex';
  };

  window.closeUploadModal = function() {
    document.getElementById('upload-modal').style.display = 'none';
  };

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

  const uploadForm = document.getElementById('upload-form');

  if (uploadForm) {
    uploadForm.addEventListener('submit', function (e) {
      const authorsInput = document.getElementById('authors');
      const dateInput = document.getElementById('date');

      // Validate authors
      if (!authorsInput.value.trim()) {
        alert('Please enter at least one author.');
        authorsInput.focus();
        e.preventDefault();
        return;
      }

      // Validate date format: YYYY-MM-DD
      const rawDate = dateInput.value.trim();
      const datePattern = /^\d{4}-\d{2}-\d{2}$/;

      if (!datePattern.test(rawDate)) {
        alert('Please enter a valid date.');
        dateInput.focus();
        e.preventDefault();
        return;
      }

      // Convert date to MM/DD/YYYY before submitting
      const [year, month, day] = rawDate.split('-');
      const formattedDate = `${month}/${day}/${year}`;
      dateInput.value = formattedDate;

      // Now the form submits with the correct date format
    });
  }

  // Approval Sheet List: Search, Filter by Author & Date, and Sort
  
  const searchInput = document.getElementById('search-input');
  const filterAuthorsSelect = document.getElementById('filter-authors');
  const filterYearSelect = document.getElementById('filter-year');
  const sortSelect = document.getElementById('sort-select');
  const table = document.getElementById('approval-table');
  const tbody = table ? table.querySelector('tbody') : null;

  function parseDateFromCell(dateStr) {
    if (!dateStr) return null;
    const [month, day, year] = dateStr.split('/');
    return new Date(`${year}-${month}-${day}`);
  }

  function filterAndSortRows() {
    const searchTerm = searchInput.value.trim().toLowerCase();
    const authorFilter = filterAuthorsSelect.value.toLowerCase();
    const yearFilter = filterYearSelect.value;
    const sortValue = sortSelect.value;

    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.forEach(row => {
      const title = row.querySelector('.title-cell').textContent.toLowerCase();
      const authors = row.querySelector('.author-column').textContent.toLowerCase();
      const dateText = row.querySelector('.date-column').textContent.trim();
      const rowDate = parseDateFromCell(dateText);
      const rowYear = rowDate ? rowDate.getFullYear().toString() : "";

      const matchesSearch = !searchTerm || title.includes(searchTerm) || authors.includes(searchTerm);
      const matchesAuthor = !authorFilter || authors.includes(authorFilter);
      const matchesYear = !yearFilter || rowYear === yearFilter;

      if (matchesSearch && matchesAuthor && matchesYear) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });

    const visibleRows = rows.filter(row => row.style.display !== 'none');

    visibleRows.sort((a, b) => {
      const aTitle = a.querySelector('.title-cell').textContent.toLowerCase();
      const bTitle = b.querySelector('.title-cell').textContent.toLowerCase();
      const aAuthors = a.querySelector('.author-column').textContent.toLowerCase();
      const bAuthors = b.querySelector('.author-column').textContent.toLowerCase();
      const aDate = parseDateFromCell(a.querySelector('.date-column').textContent);
      const bDate = parseDateFromCell(b.querySelector('.date-column').textContent);

      switch (sortValue) {
        case 'title-asc':
          return aTitle.localeCompare(bTitle);
        case 'title-desc':
          return bTitle.localeCompare(aTitle);
        case 'authors-asc':
          return aAuthors.localeCompare(bAuthors);
        case 'authors-desc':
          return bAuthors.localeCompare(aAuthors);
        case 'date-asc':
          return (aDate || 0) - (bDate || 0);
        case 'date-desc':
          return (bDate || 0) - (aDate || 0);
        default:
          return 0;
      }
    });

    visibleRows.forEach(row => tbody.appendChild(row));
  }

  if (searchInput && filterAuthorsSelect && filterYearSelect && sortSelect && tbody) {
    searchInput.addEventListener('input', filterAndSortRows);
    filterAuthorsSelect.addEventListener('change', filterAndSortRows);
    filterYearSelect.addEventListener('change', filterAndSortRows);
    sortSelect.addEventListener('change', filterAndSortRows);

    filterAndSortRows(); // initial filter
  }
});
