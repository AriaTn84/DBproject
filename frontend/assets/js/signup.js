document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    const signupBtn = document.getElementById('signup-btn');
    const messageBox = document.getElementById('message-box');

    const SIGNUP_URL = 'http://127.0.0.1:8000/api/sign-up/';

    function showMessage(message, isError = false) {
        messageBox.textContent = message;
        messageBox.className = `mt-4 text-center text-sm p-3 rounded-lg ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    }

    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userData = {
            first_name: document.getElementById('first_name').value,
            last_name: document.getElementById('last_name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            password: document.getElementById('password').value,
            city_of_residence: document.getElementById('city_of_residence').value,
        };
        signupBtn.disabled = true;
        signupBtn.textContent = 'در حال ثبت نام...';
        messageBox.className = ''; // پاک کردن پیام قبلی

        try {
            const response = await fetch(SIGNUP_URL, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'خطایی در هنگام ثبت نام رخ داد.');
            }

            showMessage('ثبت‌نام با موفقیت انجام شد. در حال انتقال به صفحه ورود...', false);

            setTimeout(() => {
                window.location.href = '../login/index.html';
            }, 2000);

        } catch (error) {
            showMessage(error.message, true);
        } finally {
            signupBtn.disabled = false;
            signupBtn.textContent = 'ثبت نام';
        }
    });
});
