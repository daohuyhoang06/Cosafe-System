function removeNotification() {
  const notification = document.querySelector('.notification');
  if (notification) notification.remove();
}

function showNotification(message) {
  removeNotification();
  const notif = document.createElement('div');
  notif.className = 'notification';
  notif.textContent = message;

  // Tạo nút đóng
  const closeBtn = document.createElement('span');
  closeBtn.className = 'close-btn';
  closeBtn.innerHTML = '&times;';
  closeBtn.onclick = removeNotification;

  notif.appendChild(closeBtn);
  document.body.appendChild(notif);
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function handleValidEmail(email, emailInput) {
  fetch('http://localhost:8000/send-guide-email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email: email }),
  })
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => {
      emailInput.value = '';
      showNotification(data.message || 'Thanks! Check your email for the guide.');
    })
    .catch(err => {
      showNotification('There was a problem sending the guide. Please try again later.');
    });
}

function setupGuideEmailForm(formSelector = '.form-section-bg form', emailInputSelector = '#email') {
  document.addEventListener('DOMContentLoaded', function () {
    const guideForm = document.querySelector(formSelector);
    const emailInput = document.querySelector(emailInputSelector);

    if (!guideForm || !emailInput) return;

    guideForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const emailVal = emailInput.value.trim();

      if (!isValidEmail(emailVal)) {
        showNotification('Please enter a valid email address to get the guide.');
        emailInput.focus();
        return;
      }

      handleValidEmail(emailVal, emailInput);
    });
  });
}