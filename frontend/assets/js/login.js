document.addEventListener('DOMContentLoaded', () => {
    const emailStep = document.getElementById('email-step');
    const otpStep = document.getElementById('otp-step');

    const sendOtpForm = document.getElementById('send-otp-form');
    const verifyOtpForm = document.getElementById('verify-otp-form');

    const emailInput = document.getElementById('email');
    const otpInput = document.getElementById('otp');

    const sendOtpBtn = document.getElementById('send-otp-btn');
    const verifyOtpBtn = document.getElementById('verify-otp-btn');

    const messageBox = document.getElementById('message-box');
    const backToEmailBtn = document.getElementById('back-to-email');

    const SEND_OTP_URL = 'http://127.0.0.1:8000/api/log-in/send-otp/';
    const VERIFY_OTP_URL = 'http://127.0.0.1:8000/api/log-in/verify-otp/';

    function showMessage(message, isError = false) {
        messageBox.textContent = message;
        messageBox.className = `mt-4 text-center text-sm p-3 rounded-lg ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    }

    sendOtpForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = emailInput.value;

        sendOtpBtn.disabled = true;
        sendOtpBtn.textContent = 'در حال ارسال...';
        messageBox.className = '';

        try {
            const response = await fetch(SEND_OTP_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'خطایی رخ داد');
            }

            showMessage('کد تایید با موفقیت به ایمیل شما ارسال شد.', false);
            emailStep.classList.add('hidden');
            otpStep.classList.remove('hidden');

        } catch (error) {
            showMessage(error.message, true);
        } finally {
            sendOtpBtn.disabled = false;
            sendOtpBtn.textContent = 'دریافت کد';
        }
    });

    verifyOtpForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = emailInput.value;
        const otp = otpInput.value;

        verifyOtpBtn.disabled = true;
        verifyOtpBtn.textContent = 'در حال بررسی...';
        messageBox.className = '';

        try {
            const response = await fetch(VERIFY_OTP_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, otp: otp })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'کد تایید نامعتبر است');
            }

            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);

            showMessage('ورود با موفقیت انجام شد! در حال انتقال...', false);

            setTimeout(() => {
                window.location.href = '../../home/index.html';
            }, 2000);

        } catch (error) {
            showMessage(error.message, true);
        } finally {
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.textContent = 'تایید و ورود';
        }
    });

    backToEmailBtn.addEventListener('click', (e) => {
        e.preventDefault();
        otpStep.classList.add('hidden');
        emailStep.classList.remove('hidden');
        messageBox.className = '';
        otpInput.value = '';
    });
});
