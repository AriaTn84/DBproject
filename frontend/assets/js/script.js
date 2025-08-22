document.addEventListener('DOMContentLoaded', function () {

    const loginLink = document.getElementById('login-link');
    const profileLink = document.getElementById('profile-link');
    const logoutLink = document.getElementById('logout-link');
    const accessToken = localStorage.getItem('accessToken');

    if (accessToken) {
        loginLink.classList.add('hidden');
        profileLink.classList.remove('hidden');
        logoutLink.classList.remove('hidden');
    } else {
        loginLink.classList.remove('hidden');
        profileLink.classList.add('hidden');
        logoutLink.classList.add('hidden');
    }

    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        alert('شما با موفقیت خارج شدید.');
        window.location.href = '../auth/login/index.html';
    });


    const searchForm = document.getElementById('search-form');
    const resultsContainer = document.getElementById('results-container');
    const loadingIndicator = document.getElementById('loading');
    const GET_TICKET_DETAILS_URL = 'http://127.0.0.1:8000/api/get-ticket-details/';


    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const params = {
            departure_city: document.getElementById('departure_city').value,
            arrival_city: document.getElementById('arrival_city').value,
            departure_date: document.getElementById('departure_date').value,
            vehicle_type: document.getElementById('vehicle_type').value,
            min__cost: document.getElementById('min_cost').value,
            max_cost: document.getElementById('max_cost').value,
            company_name: document.getElementById('company_name').value,
            departure_time: document.getElementById('departure_time').value,
            travel_class: document.getElementById('travel_class').value,
        };

        const queryParams = new URLSearchParams();
        for (const key in params) {
            if (params[key]) {
                queryParams.append(key, params[key]);
            }
        }

        const apiUrl = `http://127.0.0.1:8000/api/tickets/search/?${queryParams.toString()}`;

        resultsContainer.innerHTML = '';
        loadingIndicator.classList.remove('hidden');

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || `خطای شبکه: ${response.status}`)
                    });
                }
                return response.json();
            })
            .then(data => {
                loadingIndicator.classList.add('hidden');
                const today = new Date();
                today.setHours(0, 0, 0, 0);

                const validTickets = data.data.filter(ticket => {
                    const ticketDate = new Date(ticket.departure_date);
                    return ticketDate >= today;
                });

                if (validTickets.length > 0) {
                    resultsContainer.className = 'flex flex-col gap-4';
                    validTickets.forEach(ticket => {
                        const ticketElement = createTicketCard(ticket);
                        resultsContainer.appendChild(ticketElement);
                    });
                } else {
                    resultsContainer.className = 'grid grid-cols-1';
                    resultsContainer.innerHTML = `
                        <div class="col-span-full text-center bg-amber-100 text-amber-800 p-4 rounded-lg fade-in">
                            <p>متاسفانه برای این جستجو، بلیطی یافت نشد.</p>
                        </div>`;
                }
            })
            .catch(error => {
                loadingIndicator.classList.add('hidden');
                console.error('خطا در ارتباط با سرور:', error);
                resultsContainer.innerHTML = `
                    <div class="col-span-full text-center bg-red-100 text-red-800 p-4 rounded-lg fade-in">
                        <p>خطایی در ارتباط با سرور رخ داد.</p>
                        <p class="text-sm mt-1">${error.message}</p>
                    </div>`;
            });
    });

    function getLeftSection(ticket) {
        return `
        <div class="flex flex-col items-center justify-center gap-2 w-1/5 text-center border-l border-slate-200 dark:border-slate-700 pl-4">
            <p class="text-xl font-bold text-blue-600 dark:text-blue-400">${Number(ticket.cost).toLocaleString()} تومان</p>
            <button 
                class="select-flight-btn w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition-all"
                data-ticket-id="${ticket.ticket_id}"
                data-origin="${ticket.departure_city}"
                data-destination="${ticket.arrival_city}"
                data-price="${ticket.cost}"
                data-vehicle="${ticket.vehicle_type}"
                data-departure-time-full="${ticket.departure_date}T${ticket.departure_time}"
            >
                انتخاب سفر
            </button>
            <p class="text-xs text-slate-500 dark:text-slate-400">${ticket.remaining_capacity} صندلی باقی مانده</p>
        </div>
    `;
    }


    function getMiddleSection(ticket) {
        let vehicleIcon = '❔';
        if (ticket.vehicle_type === 'Airplane') vehicleIcon = '✈️';
        else if (ticket.vehicle_type === 'Train') vehicleIcon = '🚆';
        else if (ticket.vehicle_type === 'Bus') vehicleIcon = '🚌';

        const arrivalTime = ticket.arrival_time ? ticket.arrival_time.substring(0, 5) : '--:--';

        return `
        <div class="flex-grow">
            <div class="flex items-center justify-between">
                <div class="text-right">
                    <p class="text-2xl font-bold font-mono text-slate-800 dark:text-slate-100">${ticket.departure_time.substring(0, 5)}</p>
                    <p class="text-sm text-slate-600 dark:text-slate-400">${ticket.departure_city}</p>
                </div>
                <div class="flex-grow flex items-center mx-4">
                    <div class="w-full border-b-2 border-dotted border-slate-300 dark:border-slate-600 relative">
                        <span class="absolute left-1/2 -translate-x-1/2 -top-3 text-xl">${vehicleIcon}</span>
                    </div>
                </div>
                <div class="text-left">
                    <p class="text-2xl font-bold font-mono text-slate-800 dark:text-slate-100">${arrivalTime}</p>
                    <p class="text-sm text-slate-600 dark:text-slate-400">${ticket.arrival_city}</p>
                </div>
            </div>
            <div class="flex items-center justify-end gap-4 mt-2 text-xs text-blue-600 dark:text-blue-400">
                <a href="#" class="hover:underline flight-details-link" data-ticket-id="${ticket.ticket_id}">اطلاعات سفر</a>
                <a href="#" class="hover:underline refund-rules-link">قوانین استرداد</a>
            </div>
        </div>
    `;
    }


    function getRightSection(ticket) {
        const travelClass = ticket.airplane_class || ticket.train_star || 'استاندارد';
        return `
        <div class="flex flex-col items-center justify-center gap-2 w-1/4">
            <div class="flex items-center gap-3">
                <img src="https://placehold.co/40x40/E03131/FFFFFF?text=${ticket.company_name.charAt(0)}" alt="Company Logo" class="w-10 h-10 rounded-full">
                <span class="font-semibold text-slate-800 dark:text-slate-200">${ticket.company_name}</span>
            </div>
            <div class="flex items-center gap-2 mt-2">
                <span class="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-200 px-2 py-1 rounded-full">سیستمی</span>
                <span class="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-200 px-2 py-1 rounded-full">${travelClass}</span>
            </div>
        </div>
    `;
    }


    async function fetchTicketDetails(ticketId, detailsContainer) {
        detailsContainer.innerHTML = '<p class="text-center text-slate-500 p-4">در حال بارگذاری جزئیات...</p>';
        try {
            const response = await fetch(GET_TICKET_DETAILS_URL, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ticket_id: ticketId})
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'خطا در دریافت جزئیات');
            }

            const result = await response.json();
            const details = result.data;
            const specifics = details.vehicle_type;

            let detailsHTML = '';

            if (specifics.type === 'Airplane') {
                const amenities = specifics.amenities;
                detailsHTML = `
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-2 text-sm">
                        <div><strong class="block text-slate-500 mb-1">شماره پرواز</strong><span class="font-mono">${amenities.flight_number || 'N/A'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">کلاس پرواز</strong><span>${amenities.airplane_class || 'N/A'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">مدل هواپیما</strong><span>${amenities.etc || 'نامشخص'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">ایرلاین</strong><span>${amenities.airline || 'N/A'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">پذیرایی</strong><span>${amenities.catering ? 'پذیرایی دارد' : 'بدون پذیرایی'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">وایفای</strong><span>${amenities.wifi_access ? 'وایفای دارد' : 'بدون وایفای'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">صندلی تخت شو</strong><span>${amenities.flat_wagon ? ' دارد' : 'ندارد'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">فرودگاه مبدا</strong><span>${amenities.departure_airport}</span></div>
                        <div><strong class="block text-slate-500 mb-1">فرودگاه مقصد</strong><span>${amenities.arrival_airport}</span></div>
                    </div>`;
            } else if (specifics.type === 'Train') {
                const amenities = specifics.amenities;
                detailsHTML = `
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-2 text-sm">
                        <div><strong class="block text-slate-500 mb-1">شماره قطار</strong><span class="font-mono">${details.ticket_id}</span></div>
                        <div><strong class="block text-slate-500 mb-1">درجه قطار</strong><span>${amenities.star} ستاره</span></div>
                        <div><strong class="block text-slate-500 mb-1">شماره واگن</strong><span>${amenities.car_number}</span></div>
                        <div><strong class="block text-slate-500 mb-1">پذیرایی</strong><span>${amenities.catering ? 'پذیرایی دارد' : 'بدون پذیرایی'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">وایفای</strong><span>${amenities.wifi_access ? 'وایفای دارد' : 'بدون وایفای'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">واگن تخت دار</strong><span>${amenities.flat_wagon ? ' دارد' : 'ندارد'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">سایر امکانات</strong><span>${amenities.etc}</span></div>
                    </div>`;
            } else if (specifics.type === 'Bus') {
                const amenities = specifics.amenities;
                detailsHTML = `
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-2 text-sm">
                        <div><strong class="block text-slate-500 mb-1">شماره سرویس</strong><span class="font-mono">${details.ticket_id}</span></div>
                        <div><strong class="block text-slate-500 mb-1">نوع اتوبوس</strong><span>${amenities.bus_type}</span></div>
                        <div><strong class="block text-slate-500 mb-1">چیدمان</strong><span>${amenities.seats_row_per_row} صندلی در ردیف</span></div>
                        <div><strong class="block text-slate-500 mb-1">مانیتور شخصی</strong><span>${amenities.personal_monitor ? 'دارد' : 'ندارد'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">پذیرایی</strong><span>${amenities.catering ? 'پذیرایی دارد' : 'بدون پذیرایی'}</span></div>
                        <div><strong class="block text-slate-500 mb-1">سیستم تهویه</strong><span>${amenities.ventilation ? ' دارد' : 'ندارد'}</span></div>
                    </div>`;
            } else {
                detailsHTML = '<p class="text-center text-slate-500">جزئیات بیشتری برای این بلیط یافت نشد.</p>';
            }

            detailsContainer.innerHTML = `
                ${detailsHTML}
                <div class="text-center mt-4">
                    <button class="text-blue-600 text-sm font-semibold close-details-btn">بستن</button>
                </div>
            `;

        } catch (error) {
            detailsContainer.innerHTML = `<p class="text-center text-red-500 p-4">${error.message}</p>`;
        }
    }

    function createTicketCard(ticket) {
        const wrapper = document.createElement('div');
        wrapper.className = 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-md transition-all duration-300 fade-in';

        const mainCard = document.createElement('div');
        mainCard.className = 'p-4 flex items-center justify-between gap-4';
        mainCard.innerHTML = getRightSection(ticket) + getMiddleSection(ticket) + getLeftSection(ticket);

        const detailsSection = document.createElement('div');
        detailsSection.className = 'hidden p-4 border-t border-slate-200 dark:border-slate-700';

        const refundSection = document.createElement('div');
        refundSection.className = 'hidden p-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900';
        refundSection.innerHTML = `
            <div class="text-center mb-4">
                <h4 class="font-semibold text-slate-800 dark:text-slate-200">قوانین استرداد بلیط</h4>
                <p class="text-xs text-slate-500 dark:text-slate-400">درصد جریمه کسر شده بر اساس زمان اعلام کنسلی محاسبه می‌گردد.</p>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
                <div class="p-2">
                    <p class="font-bold text-lg text-red-600 dark:text-red-400">۱۰٪</p>
                    <p class="text-slate-600 dark:text-slate-400">بیشتر از ۷ روز مانده به پرواز</p>
                </div>
                <div class="p-2">
                    <p class="font-bold text-lg text-red-600 dark:text-red-400">۲۰٪</p>
                    <p class="text-slate-600 dark:text-slate-400">از ۷ روز تا ۱ روز مانده به پرواز</p>
                </div>
                <div class="p-2">
                    <p class="font-bold text-lg text-red-600 dark:text-red-400">۳۰٪</p>
                    <p class="text-slate-600 dark:text-slate-400">از ۲۴ ساعت تا ۱۲ ساعت مانده به پرواز</p>
                </div>
                <div class="p-2">
                    <p class="font-bold text-lg text-red-600 dark:text-red-400">۵۰٪</p>
                    <p class="text-slate-600 dark:text-slate-400">کمتر از ۱۲ ساعت مانده به پرواز</p>
                </div>
            </div>
            <div class="text-center mt-4">
                <button class="text-blue-600 dark:text-blue-400 text-sm font-semibold close-refund-btn">بستن</button>
            </div>
        `;


        wrapper.appendChild(mainCard);
        wrapper.appendChild(detailsSection);
        wrapper.appendChild(refundSection);
        const detailsLink = mainCard.querySelector('.flight-details-link');
        const refundLink = mainCard.querySelector('.refund-rules-link');

        detailsLink.addEventListener('click', async (e) => {
            e.preventDefault();
            refundSection.classList.add('hidden');
            const ticketId = e.target.dataset.ticketId;
            const isHidden = detailsSection.classList.contains('hidden');

            if (isHidden) {
                if (!detailsSection.hasAttribute('data-loaded')) {
                    await fetchTicketDetails(ticketId, detailsSection);
                    detailsSection.setAttribute('data-loaded', 'true');
                    detailsSection.querySelector('.close-details-btn').addEventListener('click', (event) => {
                        event.preventDefault();
                        detailsSection.classList.add('hidden');
                        wrapper.classList.remove('shadow-xl');
                    });
                }
            }

            detailsSection.classList.toggle('hidden');
            wrapper.classList.toggle('shadow-xl');
        });

        refundLink.addEventListener('click', (e) => {
            e.preventDefault();
            detailsSection.classList.add('hidden');
            refundSection.classList.toggle('hidden');
            wrapper.classList.toggle('shadow-xl', !refundSection.classList.contains('hidden'));
            refundSection.querySelector('.close-refund-btn').addEventListener('click', (e) => {
                e.preventDefault();
                refundSection.classList.add('hidden');
                wrapper.classList.remove('shadow-xl');
            })
        });

        return wrapper;
    }

    resultsContainer.addEventListener('click', async (event) => {
        const button = event.target.closest('.select-flight-btn');

        if (button) {
            const accessToken = localStorage.getItem('accessToken');
            if (!accessToken) {
                alert('برای رزرو بلیط، لطفاً ابتدا وارد حساب کاربری خود شوید.');
                window.location.href = '../auth/login/index.html';
                return;
            }

            const ticketId = button.dataset.ticketId;
            try {
                const response = await fetch('http://localhost:8000/api/reserve-ticket/', {
                    method: 'POST', headers: {
                        'Content-Type': 'application/json', 'Authorization': `Bearer ${accessToken}`
                    }, body: JSON.stringify({
                        ticket_id: ticketId
                    })
                });

                const resultReserve = await response.json();
                const ticketData = {
                    id: button.dataset.ticketId,
                    origin: button.dataset.origin,
                    destination: button.dataset.destination,
                    price: button.dataset.price,
                    vehicle: button.dataset.vehicle,
                    departureTime: button.dataset.departureTimeFull
                };
                if (response.ok) {
                    alert(`بلیط با موفقیت رزرو شد! شماره رزرو: ${resultReserve.reservation_id}.`);
                    localStorage.setItem('selectedTicket', JSON.stringify(ticketData));
                    localStorage.setItem('resultReserve', JSON.stringify(resultReserve));
                    window.location.href = '../payment/index.html';
                } else {
                    alert(`خطا در رزرو: ${resultReserve.error || 'مشکلی در سرور رخ داده است.'}`);
                }
            } catch (error) {
                console.error('Error reserving ticket:', error);
                alert('امکان برقراری ارتباط با سرور وجود ندارد.');
            }
        }

    });
});