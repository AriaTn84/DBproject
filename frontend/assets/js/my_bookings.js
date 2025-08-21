document.addEventListener('DOMContentLoaded', () => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        window.location.href = '../../auth/login/index.html';
        return;
    }

    const bookingsContainer = document.getElementById('bookings-container');

    // --- تابع اصلی برای لغو رزرو ---
    async function cancelBooking(bookingId, cardElement) {
        const isConfirmed = confirm('آیا از لغو این رزرو اطمینان دارید؟');
        if (!isConfirmed) {
            return;
        }

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        };

        // در این Body، نام فیلد به reservation_id تغییر کرده است
        const body = JSON.stringify({
            reservation_id: bookingId,
            confirm: true
        });

        const cancelWithPenaltyURL = 'http://127.0.0.1:8000/api/reservation/cancel-penalty/';
        const cancelReservationURL = 'http://127.0.0.1:8000/api/reservation/cancel/';

        try {
            let response = await fetch(cancelWithPenaltyURL, { method: 'POST', headers, body });
            let data = await response.json();

            if (!response.ok) {
                response = await fetch(cancelReservationURL, { method: 'POST', headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }, body: JSON.stringify({ reservation_id: bookingId }) });
                data = await response.json();
            }

            if (response.ok) {
                alert('رزرو شما با موفقیت لغو شد.');
                const statusSpan = cardElement.querySelector('.status-span');
                statusSpan.textContent = 'کنسل شده توسط مسافر';
                statusSpan.className = 'status-span text-sm font-bold text-red-600';
                cardElement.querySelector('.cancel-btn').remove();
            } else {
                throw new Error(data.error || 'خطای نامشخص در لغو رزرو');
            }
        } catch (error) {
            console.error('Error during cancellation:', error);
            alert(`خطا در هنگام لغو رزرو: ${error.message}`);
        }
    }

    // --- مدیریت کلیک روی دکمه‌های کنسل ---
    bookingsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('cancel-btn')) {
            const bookingId = event.target.getAttribute('data-booking-id');
            const cardElement = event.target.closest('.booking-card');
            cancelBooking(bookingId, cardElement);
        }
    });

    // --- تابع برای رندر کردن کارت‌های رزرو ---
    function renderBookings(bookings) {
        bookingsContainer.innerHTML = '';
        if (bookings.length === 0) {
            bookingsContainer.innerHTML = '<p class="text-center text-gray-500">موردی برای نمایش وجود ندارد.</p>';
            return;
        }

        bookings.sort((a, b) => new Date(b.departure_date) - new Date(a.departure_date));

        bookings.forEach(booking => {
            const card = document.createElement('div');
            card.className = 'booking-card bg-white p-6 rounded-xl shadow-md border border-slate-200';

            let statusText = booking.reservation_status;
            let statusColor = 'text-yellow-600';

            if (statusText === 'Confirmed') {
                statusText = 'تکمیل شده';
                statusColor = 'text-green-600';
            } else if (statusText === 'Cancelled By Passenger') {
                statusText = 'کنسل شده توسط مسافر';
                statusColor = 'text-red-600';
            } else if (statusText === 'Cancelled By Admin') {
                statusText = 'کنسل شده توسط ادمین';
                statusColor = 'text-red-600';
            }

            let cancelButtonHTML = '';
            if (booking.reservation_status === 'Confirmed') {
                 // !!! اشتباه اینجا بود: booking.id به booking.reservation_id تغییر کرد !!!
                cancelButtonHTML = `
                    <div class="mt-4 text-left">
                        <button class="cancel-btn bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" data-booking-id="${booking.reservation_id}">
                            کنسل کردن
                        </button>
                    </div>`;
            }

            card.innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">${booking.departure_city} به ${booking.arrival_city}</h3>
                    <span class="status-span text-sm font-bold ${statusColor}">${statusText}</span>
                </div>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <p><strong>تاریخ حرکت:</strong> ${booking.departure_date}</p>
                    <p><strong>شرکت:</strong> ${booking.company_name}</p>
                    <p><strong>هزینه:</strong> ${booking.cost} تومان</p>
                </div>
                ${cancelButtonHTML}
            `;
            bookingsContainer.appendChild(card);
        });
    }

    // --- تابع برای دریافت لیست رزروها از سرور ---
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

    // --- بارگذاری اولیه اطلاعات ---
    async function loadAllBookings() {
        bookingsContainer.innerHTML = '<p class="text-center text-gray-500">در حال بارگذاری...</p>';
        const bookings = await fetchAllBookings();
        renderBookings(bookings);
    }

    loadAllBookings();
});








// document.addEventListener('DOMContentLoaded', () => {
//     const accessToken = localStorage.getItem('accessToken');
//     if (!accessToken) {
//         window.location.href = '../../auth/login/index.html';
//         return;
//     }
//
//     const bookingsContainer = document.getElementById('bookings-container');
//
//     async function fetchAllBookings() {
//         const response = await fetch(`http://127.0.0.1:8000/api/get-bookings/`, {
//             headers: { 'Authorization': `Bearer ${accessToken}` }
//         });
//         if (!response.ok) {
//             console.error('Failed to fetch bookings');
//             return [];
//         }
//         const data = await response.json();
//         return data.bookings;
//     }
//
//     function renderBookings(bookings) {
//         bookingsContainer.innerHTML = '';
//         if (bookings.length === 0) {
//             bookingsContainer.innerHTML = '<p class="text-center text-gray-500">موردی برای نمایش وجود ندارد.</p>';
//             return;
//         }
//
//         bookings.sort((a, b) => new Date(b.departure_date) - new Date(a.departure_date));
//
//         bookings.forEach(booking => {
//             const card = document.createElement('div');
//             card.className = 'bg-white p-6 rounded-xl shadow-md border border-slate-200';
//
//             let statusText = booking.reservation_status;
//             let statusColor = 'text-yellow-600';
//
//             if (statusText === 'Confirmed') {
//                 statusText = 'تکمیل شده';
//                 statusColor = 'text-green-600';
//             } else if (statusText === 'Cancelled By Passenger') {
//                 statusText = 'کنسل شده توسط مسافر';
//                 statusColor = 'text-red-600';
//             } else if (statusText === 'Cancelled By admin') {
//                 statusText = 'کنسل شده توسط ادمین';
//                 statusColor = 'text-red-600';
//             }
//
//             card.innerHTML = `
//                 <div class="flex justify-between items-center mb-4">
//                     <h3 class="text-lg font-semibold">${booking.departure_city} به ${booking.arrival_city}</h3>
//                     <span class="text-sm font-bold ${statusColor}">${statusText}</span>
//                 </div>
//                 <div class="grid grid-cols-2 gap-4 text-sm">
//                     <p><strong>تاریخ حرکت:</strong> ${booking.departure_date}</p>
//                     <p><strong>شرکت:</strong> ${booking.company_name}</p>
//                     <p><strong>هزینه:</strong> ${booking.cost} تومان</p>
//                 </div>
//             `;
//             bookingsContainer.appendChild(card);
//         });
//     }
//
//     async function loadAllBookings() {
//         bookingsContainer.innerHTML = '<p class="text-center text-gray-500">در حال بارگذاری...</p>';
//         const bookings = await fetchAllBookings();
//         renderBookings(bookings);
//     }
//
//     loadAllBookings();
// });