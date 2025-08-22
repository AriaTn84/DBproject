document.addEventListener('DOMContentLoaded', function() {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        window.location.href = '../../auth/login/index.html';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const bookingId = urlParams.get('booking_id');
    const bookingIdInput = document.getElementById('booking-id');
    const messageDiv = document.getElementById('message');

    if (bookingId) {
        bookingIdInput.value = bookingId;
    }

    document.getElementById('cancel-button').addEventListener('click', function() {
        const bookingIdToCancel = bookingIdInput.value;
        if (!bookingIdToCancel) {
            messageDiv.innerText = 'لطفا شناسه رزرو را وارد کنید.';
            return;
        }

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        };

        const cancelWithPenaltyURL = 'http://127.0.0.1:8000/api/cancel_with_penalty/';
        const cancelReservationURL = 'http://127.0.0.1:8000/api/cancel_reservation/';

        messageDiv.innerText = 'در حال ارسال درخواست...';

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