document.addEventListener('DOMContentLoaded', () => {
    const GET_PROFILE_URL = 'http://127.0.0.1:8000/api/profile/get/';
    const userFullname = document.getElementById('user-fullname');
    const userPhoneDisplay = document.getElementById('user-phone-display');
    const walletBalance = document.getElementById('wallet-balance');
    const userPhone = document.getElementById('user-phone');
    const userEmail = document.getElementById('user-email');
    const logoutLink = document.getElementById('logout-link');
    const personalFullname = document.getElementById('personal-fullname');
    const dateOfBirth = document.getElementById('date-of-birth');

    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        alert('شما با موفقیت خارج شدید.');
        window.location.href = '../auth/login/index.html';
    });

    async function fetchProfileData() {
        const accessToken = localStorage.getItem('accessToken');

        if (!accessToken) {
            window.location.href = '../auth/login/index.html';
            return;
        }

        try {
            const response = await fetch(GET_PROFILE_URL, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                     alert('نشست شما منقضی شده است. لطفاً دوباره وارد شوید.');
                     localStorage.clear();
                     window.location.href = '../auth/login/index.html';
                }
                throw new Error('خطا در دریافت اطلاعات پروفایل');
            }

            const responseData = await response.json();
            const user = responseData.data;

            const fullname = `${user.first_name} ${user.last_name}`;
            userFullname.textContent = fullname;
            userPhoneDisplay.textContent = user.phone;
            userPhone.textContent = user.phone;
            userEmail.textContent = user.email;
            personalFullname.textContent = fullname;
            dateOfBirth.textContent = user.date_of_birth.toString() || '—';
            walletBalance.textContent = user.balance;

        } catch (error) {
            console.error(error);
        }
    }

    fetchProfileData();
});
