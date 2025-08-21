document.addEventListener('DOMContentLoaded', function() {
    // ۱. توکن احراز هویت را از حافظه محلی مرورگر برمی‌داریم
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        // اگر توکن وجود نداشت، کاربر را به صفحه لاگین هدایت می‌کنیم
        window.location.href = '../../auth/login/index.html';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const bookingId = urlParams.get('booking_id');
    const bookingIdInput = document.getElementById('booking-id');
    const messageDiv = document.getElementById('message');

    // اگر شناسه‌ی رزرو در URL بود، آن را در فیلد مربوطه قرار می‌دهیم
    if (bookingId) {
        bookingIdInput.value = bookingId;
    }

    document.getElementById('cancel-button').addEventListener('click', function() {
        const bookingIdToCancel = bookingIdInput.value;
        if (!bookingIdToCancel) {
            messageDiv.innerText = 'لطفا شناسه رزرو را وارد کنید.';
            return;
        }

        // ۲. هدر درخواست را با توکن احراز هویت تنظیم می‌کنیم
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        };

        const cancelWithPenaltyURL = 'http://127.0.0.1:8000/api/cancel_with_penalty/';
        const cancelReservationURL = 'http://127.0.0.1:8000/api/cancel_reservation/';

        messageDiv.innerText = 'در حال ارسال درخواست...';

        // ابتدا سعی می‌کنیم با جریمه کنسل کنیم
        fetch(cancelWithPenaltyURL, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ booking_id: bookingIdToCancel })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message && data.message.includes("successfully")) {
                messageDiv.innerText = 'رزرو با موفقیت کنسل شد و جریمه اعمال گردید.';
                messageDiv.style.color = 'green';
            } else {
                // اگر کنسل کردن با جریمه موفقیت‌آمیز نبود، بدون جریمه را امتحان می‌کنیم
                fetch(cancelReservationURL, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ booking_id: bookingIdToCancel })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message && data.message.includes("successfully")) {
                        messageDiv.innerText = 'رزرو با موفقیت و بدون جریمه کنسل شد.';
                        messageDiv.style.color = 'green';
                    } else {
                        messageDiv.innerText = 'خطا در کنسل کردن رزرو: ' + (data.error || 'خطای نامشخص');
                        messageDiv.style.color = 'red';
                    }
                })
                .catch(error => {
                    console.error('Error during cancellation without penalty:', error);
                    messageDiv.innerText = 'یک خطای شبکه در هنگام کنسل کردن رخ داد.';
                    messageDiv.style.color = 'red';
                });
            }
        })
        .catch(error => {
            console.error('Error during cancellation with penalty:', error);
            messageDiv.innerText = 'یک خطای شبکه در هنگام کنسل کردن رخ داد.';
            messageDiv.style.color = 'red';
        });
    });
});