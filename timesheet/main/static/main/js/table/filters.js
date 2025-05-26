document.addEventListener("DOMContentLoaded", function () {
    const applyFiltersButton = document.getElementById('apply-filters-btn');

    if (applyFiltersButton) {
        applyFiltersButton.addEventListener('click', function() {
            const employeeFilter = document.getElementById('employee-filter');
            const startDateInput = document.getElementById('start-date');
            const endDateInput = document.getElementById('end-date');

            let queryParams = new URLSearchParams();

            if (employeeFilter && employeeFilter.value) {
                queryParams.append('employee', employeeFilter.value);
            }
            if (startDateInput && startDateInput.value) {
                queryParams.append('start_date', startDateInput.value);
            }
            if (endDateInput && endDateInput.value) {
                queryParams.append('end_date', endDateInput.value);
            }

            window.location.search = queryParams.toString();
        });
    }
});