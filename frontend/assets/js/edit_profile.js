document.addEventListener('DOMContentLoaded', () => {

    const GET_PROFILE_URL = 'http://127.0.0.1:8000/api/profile/get/';
    const UPDATE_PROFILE_URL = 'http://127.0.0.1:8000/api/profile/update-user/';

    const editProfileForm = document.getElementById('edit-profile-form');
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');
    const phoneInput = document.getElementById('phone');
    const cityInput = document.getElementById('city_of_residence');
    const dobInput = document.getElementById('date_of_birth');
    const updateBtn = document.getElementById('update-btn');
    const messageBox = document.getElementById('message-box');

    function showMessage(message, isError = false) {
        messageBox.textContent = message;
        messageBox.className = `mt-4 text-center text-sm p-3 rounded-lg ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    }

    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        window.location.href = '../../auth/login/index.html';
        return;
    }

    async function populateProfileData() {
        try {
            const response = await fetch(GET_PROFILE_URL, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!response.ok) {
                throw new Error('خطا در دریافت اطلاعات. لطفاً دوباره وارد شوید.');
            }

            const result = await response.json();
            const user = result.data;

            firstNameInput.value = user.first_name || '';
            lastNameInput.value = user.last_name || '';
            phoneInput.value = user.phone || '';
            cityInput.value = user.city_of_residence || '';
            dobInput.value = user.date_of_birth || '';

        } catch (error) {
            showMessage(error.message, true);
             setTimeout(() => {
                localStorage.clear();
                window.location.href = '../../auth/login/index.html';
            }, 2000);
        }
    }

    editProfileForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const updatedData = {
            first_name: firstNameInput.value,
            last_name: lastNameInput.value,
            phone: phoneInput.value,
            city_of_residence: cityInput.value,
            date_of_birth: dobInput.value,
        };

        updateBtn.disabled = true;
        updateBtn.textContent = 'در حال ذخیره...';
        messageBox.className = '';

        try {
            const response = await fetch(UPDATE_PROFILE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify(updatedData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'خطا در به‌روزرسانی اطلاعات.');
            }

            showMessage('اطلاعات با موفقیت ذخیره شد!', false);

            setTimeout(() => {
                window.location.href = '../my_profile/index.html';
            }, 2000);

        } catch (error) {
            showMessage(error.message, true);
        } finally {
            updateBtn.disabled = false;
            updateBtn.textContent = 'ذخیره تغییرات';
        }
    });

    populateProfileData();
});