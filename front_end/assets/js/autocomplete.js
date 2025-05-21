// assets/js/autocomplete.js

function setupAutocomplete() {
    const searchInput = document.getElementById('textSearchBar');
    const searchForm = document.getElementById('searchForm');

    // Tạo container cho autocomplete
    const autocompleteContainer = document.createElement('div');
    autocompleteContainer.className = 'autocomplete-container';

    // Tạo phần tử hiển thị kết quả gợi ý
    const autocompleteResults = document.createElement('div');
    autocompleteResults.className = 'autocomplete-results';

    // Chèn các phần tử vào DOM
    searchInput.parentNode.insertBefore(autocompleteContainer, searchInput);
    autocompleteContainer.appendChild(searchInput);
    autocompleteContainer.appendChild(autocompleteResults);

    let debounceTimer;

    // Xử lý sự kiện nhập vào ô tìm kiếm
    searchInput.addEventListener('input', function () {
        const query = this.value.trim();

        // Xóa timer debounce cũ
        clearTimeout(debounceTimer);

        // Nếu query rỗng, ẩn kết quả gợi ý
        if (!query) {
            autocompleteResults.classList.remove('show');
            return;
        }

        // Thiết lập debounce để tránh gọi API quá nhiều
        debounceTimer = setTimeout(async () => {
            try {
                // Gọi API search với số lượng kết quả nhỏ
                const response = await fetch('http://localhost:8000/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        keyword: query,
                        page: 1,
                        size: 5, // Chỉ lấy 5 kết quả cho gợi ý
                        sort: 'default'
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();

                // Hiển thị kết quả gợi ý
                renderAutocompleteResults(data, query);
            } catch (error) {
                console.error('Error fetching autocomplete suggestions:', error);
            }
        }, 300); // Đợi 300ms sau khi người dùng ngừng gõ
    });

    // Xử lý khi click ra ngoài để ẩn kết quả gợi ý
    document.addEventListener('click', function (event) {
        if (!autocompleteContainer.contains(event.target)) {
            autocompleteResults.classList.remove('show');
        }
    });

    // Xử lý khi form được submit
    searchForm.addEventListener('submit', function (event) {
        if (!searchInput.value.trim()) {
            event.preventDefault();
        }
    });

    // Xử lý phím tắt
    searchInput.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            // Esc key - ẩn kết quả gợi ý
            autocompleteResults.classList.remove('show');
        } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
            // Phím mũi tên - di chuyển giữa các gợi ý
            event.preventDefault();

            const items = autocompleteResults.querySelectorAll('.autocomplete-item');
            if (items.length === 0) return;

            // Tìm item đang được chọn
            const currentSelected = autocompleteResults.querySelector('.autocomplete-item.selected');
            let nextIndex = 0;

            if (currentSelected) {
                const currentIndex = Array.from(items).indexOf(currentSelected);
                currentSelected.classList.remove('selected');

                if (event.key === 'ArrowDown') {
                    nextIndex = (currentIndex + 1) % items.length;
                } else {
                    nextIndex = (currentIndex - 1 + items.length) % items.length;
                }
            } else if (event.key === 'ArrowUp') {
                nextIndex = items.length - 1;
            }

            // Chọn item mới
            items[nextIndex].classList.add('selected');
            items[nextIndex].scrollIntoView({ block: 'nearest' });
        } else if (event.key === 'Enter') {
            // Enter key - chọn item đang được highlight
            const selectedItem = autocompleteResults.querySelector('.autocomplete-item.selected');
            if (selectedItem && autocompleteResults.classList.contains('show')) {
                event.preventDefault();
                selectedItem.click();
            }
        }
    });

    // Hàm hiển thị kết quả gợi ý
    function renderAutocompleteResults(data, query) {
        autocompleteResults.innerHTML = '';

        // Nếu không có kết quả hoặc có lỗi
        if (!data.products || data.products.length === 0) {
            autocompleteResults.classList.remove('show');
            return;
        }

        // Hiển thị kết quả
        data.products.forEach(product => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';

            // Highlight từ khóa tìm kiếm trong tên sản phẩm
            const highlightedName = highlightMatch(product.name, query);

            // Tạo nội dung cho mỗi item gợi ý
            item.innerHTML = `
        <img src="${product.link_image || 'assets/images/product-placeholder.jpg'}" alt="${product.name}">
        <div class="autocomplete-item-content">
          <div class="autocomplete-item-title">${highlightedName}</div>
          <div class="autocomplete-item-score">Score: ${product.score}</div>
        </div>
      `;

            // Xử lý khi click vào item gợi ý
            item.addEventListener('click', function () {
                searchInput.value = product.name;
                autocompleteResults.classList.remove('show');

                // Chuyển đến trang chi tiết sản phẩm
                window.location.href = `product-detail.html?query=${encodeURIComponent(searchInput.value)}&title=${encodeURIComponent(product.name)}`;
            });

            autocompleteResults.appendChild(item);
        });

        // Hiển thị kết quả gợi ý
        autocompleteResults.classList.add('show');
    }

    // Hàm highlight từ khóa tìm kiếm trong text
    function highlightMatch(text, query) {
        if (!query) return text;

        // Tách query thành các từ riêng biệt
        const queryTerms = query.trim().split(/\s+/);
        let result = text;

        // Highlight từng từ trong query
        queryTerms.forEach(term => {
            if (term.length < 2) return; // Bỏ qua từ quá ngắn

            // Tạo regex để tìm từng từ, không phân biệt hoa thường
            const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
            result = result.replace(regex, '<span class="autocomplete-highlight">$1</span>');
        });

        return result;
    }

    // Hàm escape các ký tự đặc biệt trong regex
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// Thêm CSS cho item được chọn
document.head.insertAdjacentHTML('beforeend', `
  <style>
    .autocomplete-item.selected {
      background-color: #f0f8ff;
    }
    
    .autocomplete-results {
      scrollbar-width: thin;
      scrollbar-color: #ddd #f9f9f9;
    }
    
    .autocomplete-results::-webkit-scrollbar {
      width: 8px;
    }
    
    .autocomplete-results::-webkit-scrollbar-track {
      background: #f9f9f9;
    }
    
    .autocomplete-results::-webkit-scrollbar-thumb {
      background-color: #ddd;
      border-radius: 4px;
    }
  </style>
`);

// Khởi tạo autocomplete khi trang đã tải xong
document.addEventListener('DOMContentLoaded', setupAutocomplete);
