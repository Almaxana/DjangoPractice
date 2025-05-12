function addNewRow() {
    const tableBody = document.querySelector('#timesheet-table tbody');

    // Создание новой строки таблицы
    const newRow = document.createElement('tr');

    newRow.innerHTML = `
        <td><input type="date" name="new_date" required></td>
        <td><input type="text" name="new_worker" placeholder="ФИО"></td>
        <td><input type="text" name="new_project" placeholder="Проект"></td>
        <td><input type="number" name="new_hours" min="0" step="0.5" required></td>
        <td><input type="text" name="new_comment" placeholder="Комментарий"></td>
        <td>
            <button class="button" onclick="saveRow(this)">
                <i class="fa-solid fa-check"></i>
            </button>
            <button class="button" onclick="removeRow(this)">
                <i class="fas fa-times"></i>
            </button>
        </td>
    `;

    tableBody.appendChild(newRow);
}

function saveRow(button) {
    const row = button.closest('tr');
    const inputs = row.querySelectorAll('input');
    const values = Array.from(inputs).map(input => input.value);

    if (values.some(value => !value)) {
        alert("Пожалуйста, заполните все поля.");
        return;
    }

    row.innerHTML = `
        <td>${values[0]}</td>
        <td>${values[1]}</td>
        <td>${values[2]}</td>
        <td>${values[3]}</td>
        <td>${values[4]}</td>
        <td>
            <button class="button">
                <i class="fa-solid fa-pen"></i>
            </button>
            <button class="button" onclick="removeRow(this)">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
}

function removeRow(button) {
    const row = button.closest('tr');
    row.remove();
}
