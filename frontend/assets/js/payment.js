document.addEventListener('DOMContentLoaded', () => {

    const PROFILE_API_URL = 'http://127.0.0.1:8000/api/profile/get/';
    const PAYMENT_API_URL = 'http://127.0.0.1:8000/api/payment/pay/';

    const ticketDetailsContainer = document.getElementById('ticket-details');
    const totalPriceEl = document.getElementById('total-price');
    const payButton = document.getElementById('pay-button');
    const messageBox = document.getElementById('message-box');
    const firstNameEl = document.getElementById('passenger-first-name');
    const lastNameEl = document.getElementById('passenger-last-name');

    let userInfo = {};

    const accessToken = localStorage.getItem('accessToken');
    const ticketDataString = localStorage.getItem('selectedTicket');
    const reserveDataString = localStorage.getItem('resultReserve');
    if (!accessToken) {
        alert('برای ادامه باید ابتدا وارد حساب کاربری خود شوید.');
        window.location.href = '../auth/login/index.html';
        return;
    }

    if (!ticketDataString) {
        ticketDetailsContainer.innerHTML = '<p class="text-red-500">خطا: هیچ بلیطی برای پرداخت انتخاب نشده است.</p>';
        payButton.disabled = true;
        return;
    }

    if (!reserveDataString) {
        ticketDetailsContainer.innerHTML = '<p class="text-red-500">خطا: هیچ رزروی است.</p>';
        payButton.disabled = true;
        return;
    }

    const ticket = JSON.parse(ticketDataString);
    const reserve = JSON.parse(reserveDataString)

    async function fetchAndDisplayUserInfo() {
        try {
            const response = await fetch(PROFILE_API_URL, {
                headers: {'Authorization': `Bearer ${accessToken}`}
            });
            if (!response.ok) throw new Error('خطا در دریافت اطلاعات کاربر.');

            const result = await response.json();
            userInfo = result.data;

            firstNameEl.textContent = userInfo.first_name || 'نامشخص';
            lastNameEl.textContent = userInfo.last_name || 'نامشخص';
        } catch (error) {
            showMessage(error.message, true);
            firstNameEl.textContent = 'خطا';
            lastNameEl.textContent = 'خطا';
        }
    }

    function displayTicketInfo() {
        ticketDetailsContainer.innerHTML = `
            <div class="flex justify-between py-2"><span class="text-slate-500">نوع سفر:</span><span class="font-semibold">${ticket.vehicle}</span></div>
            <div class="flex justify-between py-2"><span class="text-slate-500">مبدا:</span><span class="font-semibold">${ticket.origin}</span></div>
            <div class="flex justify-between py-2"><span class="text-slate-500">مقصد:</span><span class="font-semibold">${ticket.destination}</span></div>
            <div class="flex justify-between py-2"><span class="text-slate-500">تاریخ حرکت:</span><span class="font-semibold">${new Date(ticket.departureTime).toLocaleDateString('fa-IR')}</span></div>
        `;
        totalPriceEl.textContent = `${Number(ticket.price).toLocaleString('fa-IR')} تومان`;
    }

    function showMessage(message, isError = false) {
        messageBox.textContent = message;
        messageBox.className = `mt-4 text-center text-sm p-3 rounded-lg ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    }

    payButton.addEventListener('click', async () => {
        if (!userInfo.first_name || !userInfo.last_name) {
            showMessage('اطلاعات کاربر بارگذاری نشده است. لطفاً صفحه را رفرش کنید.', true);
            return;
        }

        payButton.disabled = true;
        payButton.textContent = 'در حال پردازش...';

        try {
            const reservationId = reserve.reservation_id;
            const paymentResponse = await fetch(PAYMENT_API_URL, {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}`},
                body: JSON.stringify({
                    reservation_id: parseInt(reservationId)
                }),
            });
            const paymentResult = await paymentResponse.json();
            if (!paymentResponse.ok) throw new Error(paymentResult.error || 'پرداخت با خطا مواجه شد.');

            showMessage('پرداخت با موفقیت انجام شد! بلیط شما صادر گردید.', false);
            payButton.textContent = 'خرید شما نهایی شد';
            payButton.classList.remove('bg-green-600', 'hover:bg-green-700');
            payButton.classList.add('bg-gray-400');
            localStorage.removeItem('selectedTicket');
            localStorage.removeItem('resultReserve')

        } catch (error) {
            showMessage(error.message, true);
            payButton.disabled = false;
            payButton.textContent = 'پرداخت نهایی با کیف پول';
        }
    });
    displayTicketInfo();
    fetchAndDisplayUserInfo();
});