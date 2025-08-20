document.addEventListener('DOMContentLoaded', () => {
    const GET_WALLET_URL = 'http://127.0.0.1:8000/api/wallet/get/';
    const CHARGE_WALLET_URL = 'http://127.0.0.1:8000/api/wallet/charge/';

    const walletBalanceEl = document.getElementById('wallet-balance');
    const chargeForm = document.getElementById('charge-wallet-form');
    const amountInput = document.getElementById('amount');
    const chargeBtn = document.getElementById('charge-btn');
    const messageBox = document.getElementById('message-box');

    const accessToken = localStorage.getItem('accessToken');

    if (!accessToken) {
        window.location.href = '../auth/login/index.html';
        return;
    }

    function showMessage(message, isError = false) {
        messageBox.textContent = message;
        messageBox.className = `mt-4 text-center text-sm p-3 rounded-lg ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    }

    async function fetchWalletData() {
        try {
            const response = await fetch(GET_WALLET_URL, {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (!response.ok) {
                throw new Error('خطا در دریافت اطلاعات کیف پول.');
            }

            const result = await response.json();
            const balance = result.data.balance;
            walletBalanceEl.textContent = `${balance} تومان`;

        } catch (error) {
            showMessage(error.message, true);
        }
    }

    chargeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const amount = amountInput.value;

        if (!amount || amount <= 0) {
            showMessage('لطفاً یک مبلغ معتبر وارد کنید.', true);
            return;
        }

        chargeBtn.disabled = true;
        chargeBtn.textContent = 'در حال پردازش...';

        try {
            const response = await fetch(CHARGE_WALLET_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({ amount: Number(amount) })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'خطا در شارژ حساب.');
            }

            showMessage('حساب شما با موفقیت شارژ شد.', false);
            fetchWalletData(); // Refresh balance
            amountInput.value = '';

        } catch (error) {
            showMessage(error.message, true);
        } finally {
            chargeBtn.disabled = false;
            chargeBtn.textContent = 'شارژ حساب';
        }
    });

    fetchWalletData();
});