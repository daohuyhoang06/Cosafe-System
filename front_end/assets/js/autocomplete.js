document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('textSearchBar');
  if (!input) return;

  let suggestionsBox = document.getElementById('global-autocomplete-suggestions');

  // Tạo suggestion box ngoài body nếu chưa có
  if (!suggestionsBox) {
    suggestionsBox = document.createElement('div');
    suggestionsBox.id = 'global-autocomplete-suggestions';
    suggestionsBox.className = 'autocomplete-suggestions';
    suggestionsBox.style.display = 'none';
    suggestionsBox.style.position = 'absolute';
    suggestionsBox.style.zIndex = '10099';
    document.body.appendChild(suggestionsBox);
  }

  let debounceTimeout = null;
  let lastValue = "";

  function positionSuggestionBox() {
    const rect = input.getBoundingClientRect();
    suggestionsBox.style.left = rect.left + window.scrollX + 'px';
    suggestionsBox.style.top = rect.bottom + window.scrollY + 'px';
    suggestionsBox.style.width = rect.width + 'px';
  }

  // Hiện autocomplete khi focus lại nếu có giá trị
  input.addEventListener('focus', () => {
    if (input.value.trim()) {
      positionSuggestionBox();
      suggestionsBox.style.display = 'block';
    }
  });

  input.addEventListener('input', function () {
    const value = this.value.trim();
    if (value === lastValue) return;
    lastValue = value;
    if (debounceTimeout) clearTimeout(debounceTimeout);
    if (!value) {
      suggestionsBox.innerHTML = "";
      suggestionsBox.style.display = "none";
      return;
    }
    debounceTimeout = setTimeout(() => {
      fetch('http://127.0.0.1:8000/autocomplete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: value, size: 10 })
      })
        .then(res => res.json())
        .then(data => {
          positionSuggestionBox();
          if (!data.products || data.products.length === 0) {
            suggestionsBox.innerHTML = '<div class="no-suggestion">No suggestions found.</div>';
            suggestionsBox.style.display = 'block';
            return;
          }
          suggestionsBox.innerHTML = data.products.map(product => `
            <div class="suggestion-item" tabindex="0">
              <img src="${product.link_image || 'assets/images/product-placeholder.jpg'}" class="suggestion-img" alt="">
              <span>${product.name}</span>
            </div>
          `).join('');
          suggestionsBox.style.display = 'block';

          suggestionsBox.querySelectorAll('.suggestion-item').forEach((item, idx) => {
            // Dùng cả mousedown lẫn touchstart (cho mobile)
            const selectSuggestion = (e) => {
              e.preventDefault();
              input.value = data.products[idx].name;
              suggestionsBox.style.display = 'none';
              document.getElementById('searchForm').submit();
            };
            item.addEventListener('mousedown', selectSuggestion);
            item.addEventListener('touchstart', selectSuggestion);
          });
        })
        .catch(() => {
          positionSuggestionBox();
          suggestionsBox.innerHTML = '<div class="no-suggestion">Error loading suggestions.</div>';
          suggestionsBox.style.display = 'block';
        });
    }, 250);
  });

  // reposition khi window resize/scroll
  window.addEventListener('resize', positionSuggestionBox);
  window.addEventListener('scroll', positionSuggestionBox, true);

  // Đóng khi click ngoài
  document.addEventListener('mousedown', function (e) {
    if (!suggestionsBox.contains(e.target) && e.target !== input) {
      suggestionsBox.style.display = 'none';
    }
  });

  // Đóng khi bấm Escape
  input.addEventListener('keydown', function (e) {
    if (e.key === "Escape") {
      suggestionsBox.style.display = 'none';
    }
  });

  // Đóng khi input mất focus
  input.addEventListener('blur', function () {
    setTimeout(() => {
      suggestionsBox.style.display = 'none';
    }, 150);
  });
});