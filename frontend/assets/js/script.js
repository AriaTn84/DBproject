document.addEventListener('DOMContentLoaded', function() {
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
                    throw new Error(`خطای شبکه: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                loadingIndicator.classList.add('hidden');

                if (data.data && data.data.length > 0) {
                    data.data.forEach(ticket => {
                        const ticketCard = createTicketCard(ticket);
                        resultsContainer.appendChild(ticketCard);
                    });
                } else {
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
                        <p>خطایی در ارتباط با سرور رخ داد. لطفاً از فعال بودن سرور و تنظیمات CORS اطمینان حاصل کنید.</p>
                        <p class="text-sm mt-1">${error.message}</p>
                    </div>`;
            });
    });

    function createTicketCard(ticket) {
        const card = document.createElement('div');
        card.className = 'bg-white border border-slate-200 rounded-xl shadow-md p-5 flex flex-col gap-3 hover:shadow-xl hover:border-blue-500 transition-all duration-300 fade-in';

        let icon = '';
        let vehicleColor = '';
        if (ticket.vehicle_type === 'Airplane') {
            icon = '✈️';
            vehicleColor = 'text-sky-500';
        } else if (ticket.vehicle_type === 'Train') {
            icon = '🚆';
            vehicleColor = 'text-emerald-500';
        } else if (ticket.vehicle_type === 'Bus') {
            icon = '🚌';
            vehicleColor = 'text-amber-500';
        }

        card.innerHTML = `
            <div class="flex justify-between items-center">
                <h3 class="text-xl font-bold text-slate-800">${ticket.company_name}</h3>
                <span class="text-2xl ${vehicleColor}">${icon}</span>
            </div>
            <div class="border-t border-slate-200 my-2"></div>
            <div class="grid grid-cols-2 gap-2 text-sm text-slate-600">
                <p><strong>مبدأ:</strong> ${ticket.departure_city}</p>
                <p><strong>مقصد:</strong> ${ticket.arrival_city}</p>
                <p><strong>تاریخ حرکت:</strong> ${ticket.departure_date}</p>
                <p><strong>زمان حرکت:</strong> ${ticket.departure_time.substring(0, 5)}</p>
            </div>
            <div class="mt-auto pt-3 text-center">
                <p class="text-lg font-semibold text-blue-600">${Number(ticket.cost).toLocaleString()} تومان</p>
                <p class="text-xs text-slate-500 mt-1">${ticket.remaining_capacity} صندلی باقی مانده</p>
            </div>
        `;
        return card;
    }
});