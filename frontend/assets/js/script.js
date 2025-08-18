document.addEventListener('DOMContentLoaded', function() {
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

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const params = {
            departure_city: document.getElementById('departure_city').value,
            arrival_city: document.getElementById('arrival_city').value,
            departure_date: document.getElementById('departure_date').value,
            vehicle_type: document.getElementById('vehicle_type').value,
            min_cost: document.getElementById('min_cost').value,
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
                    return response.json().then(err => { throw new Error(err.error || `خطای شبکه: ${response.status}`) });
                }
                return response.json();
            })
            .then(data => {
                loadingIndicator.classList.add('hidden');

                if (data.data && data.data.length > 0) {
                    resultsContainer.className = 'flex flex-col gap-4';
                    data.data.forEach(ticket => {
                        const ticketCard = createTicketCard(ticket);
                        resultsContainer.appendChild(ticketCard);
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

    function createTicketCard(ticket) {
        const card = document.createElement('div');
        card.className = 'bg-white border border-slate-200 rounded-xl shadow-md p-4 flex items-center justify-between gap-4 hover:shadow-lg hover:border-blue-500 transition-all duration-300 fade-in';
        const leftSection = `
            <div class="flex flex-col items-center justify-center gap-2 w-1/5 text-center border-l border-slate-200 pl-4">
                <p class="text-xl font-bold text-blue-600">${Number(ticket.cost).toLocaleString()} تومان</p>
                <button class="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 transition-all">انتخاب پرواز</button>
                <p class="text-xs text-slate-500">${ticket.remaining_capacity} صندلی باقی مانده</p>
            </div>
        `;
        let vehicleIcon = '❔';
        if (ticket.vehicle_type === 'Airplane') {
            vehicleIcon = '✈️';
        } else if (ticket.vehicle_type === 'Train') {
            vehicleIcon = '🚆';
        } else if (ticket.vehicle_type === 'Bus') {
            vehicleIcon = '🚌';
        }

        const arrivalTime = ticket.arrival_time ? ticket.arrival_time.substring(0, 5) : '--:--';
        const middleSection = `
            <div class="flex-grow">
                <div class="flex items-center justify-between">
                    <div class="text-right">
                        <p class="text-2xl font-bold font-mono">${ticket.departure_time.substring(0, 5)}</p>
                        <p class="text-sm text-slate-600">${ticket.departure_city}</p>
                    </div>
                    <div class="flex-grow flex items-center mx-4">
                        <div class="w-full border-b-2 border-dotted border-slate-300 relative">
                            <span class="absolute left-1/2 -translate-x-1/2 -top-3 text-xl">${vehicleIcon}</span>
                        </div>
                    </div>
                    <div class="text-left">
                        <p class="text-2xl font-bold font-mono">${arrivalTime}</p>
                        <p class="text-sm text-slate-600">${ticket.arrival_city}</p>
                    </div>
                </div>
                <div class="flex items-center justify-end gap-4 mt-2 text-xs text-blue-600">
                    <a href="#" class="hover:underline">اطلاعات پرواز</a>
                    <a href="#" class="hover:underline">قوانین استرداد</a>
                </div>
            </div>
        `;

        const travelClass = ticket.airplane_class || ticket.train_star || 'استاندارد';
        const rightSection = `
            <div class="flex flex-col items-center justify-center gap-2 w-1/4">
                <div class="flex items-center gap-3">
                    <img src="https://placehold.co/40x40/E03131/FFFFFF?text=${ticket.company_name.charAt(0)}" alt="Company Logo" class="w-10 h-10 rounded-full">
                    <span class="font-semibold">${ticket.company_name}</span>
                </div>
                <div class="flex items-center gap-2 mt-2">
                    <span class="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full">${travelClass}</span>
                </div>
            </div>
        `;

        card.innerHTML = rightSection + middleSection + leftSection;

        return card;
    }
});
