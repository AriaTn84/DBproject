document.addEventListener('DOMContentLoaded', () => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        window.location.href = '../../auth/login/index.html';
        return;
    }

    const bookingsContainer = document.getElementById('bookings-container');

    async function fetchAllBookings() {
        const response = await fetch(`http://127.0.0.1:8000/api/get-bookings/`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        if (!response.ok) {
            console.error('Failed to fetch bookings');
            return [];
        }
        const data = await response.json();
        return data.bookings;
    }

    function renderBookings(bookings) {
        bookingsContainer.innerHTML = '';
        if (bookings.length === 0) {
            bookingsContainer.innerHTML = '<p class="text-center text-gray-500">موردی برای نمایش وجود ندارد.</p>';
            return;
        }

        bookings.sort((a, b) => new Date(b.departure_date) - new Date(a.departure_date));

        bookings.forEach(booking => {
            const card = document.createElement('div');
            card.className = 'bg-white p-6 rounded-xl shadow-md border border-slate-200';

            let statusText = booking.reservation_status;
            let statusColor = 'text-yellow-600';

            if (statusText === 'Confirmed') {
                statusText = 'تکمیل شده';
                statusColor = 'text-green-600';
            } else if (statusText === 'Cancelled By Passenger') {
                statusText = 'کنسل شده توسط مسافر';
                statusColor = 'text-red-600';
            } else if (statusText === 'Cancelled By admin') {
                statusText = 'کنسل شده توسط ادمین';
                statusColor = 'text-red-600';
            }

            card.innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">${booking.departure_city} به ${booking.arrival_city}</h3>
                    <span class="text-sm font-bold ${statusColor}">${statusText}</span>
                </div>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <p><strong>تاریخ حرکت:</strong> ${booking.departure_date}</p>
                    <p><strong>شرکت:</strong> ${booking.company_name}</p>
                    <p><strong>هزینه:</strong> ${booking.cost} تومان</p>
                </div>
            `;
            bookingsContainer.appendChild(card);
        });
    }

    async function loadAllBookings() {
        bookingsContainer.innerHTML = '<p class="text-center text-gray-500">در حال بارگذاری...</p>';
        const bookings = await fetchAllBookings();
        renderBookings(bookings);
    }

    loadAllBookings();
});