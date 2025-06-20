function getDateRangeArray(start, end) {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const dates = [];

    while (startDate <= endDate) {
        dates.push(startDate.toISOString().split('T')[0]);
        startDate.setDate(startDate.getDate() + 1);
    }

    return dates;
}

export function initializeTimesheetCrud(projectsData, csrfToken, addEntryUrl, currentUserUsername, deleteEntryUrlTemplate, updateEntryUrlTemplate) {
    const addButton = document.getElementById("add-row-btn");
    const tableBody = document.querySelector("#timesheet-table tbody");

    function showNoRecordsMessage() {
        if (tableBody.rows.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6"><p style="text-align: center; padding: 10px;">Пока нет записей</p></td></tr>';
        }
    }

    function removeNoRecordsMessage() {
        const noRecordsRow = tableBody.querySelector('td > p');
        if (noRecordsRow) {
            const parentRow = noRecordsRow.closest('tr');
            if(parentRow) parentRow.remove();
        }
    }

    function handleDeleteClick() {
        const row = this.closest('tr');
        const entryId = row.dataset.id;

        if (entryId && confirm('Вы уверены, что хотите удалить эту запись?')) {
            const deleteUrl = deleteEntryUrlTemplate.replace('0', entryId);

            fetch(deleteUrl, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.error || `Ошибка сервера: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    row.remove();
                    showNoRecordsMessage();
                } else {
                    alert('Ошибка удаления: ' + (data.error || 'Неизвестная ошибка.'));
                }
            })
            .catch(error => {
                console.error("Delete error:", error);
                alert("Произошла ошибка при удалении записи: " + error.message);
            });
        }
    }

    function handleEditClick() {
        const row = this.closest('tr');
        if (row.classList.contains('editing')) return;

        row.classList.add('editing');
        const cells = Array.from(row.querySelectorAll('td'));
        const entryId = row.dataset.id;

        const originalValues = {
            date: cells[0].textContent.trim(),
            project: cells[2].textContent.trim(),
            hours: cells[3].textContent.trim(),
            comment: cells[4].textContent.trim(),
            actions: cells[6].innerHTML
        };

        const currentProject = projectsData.find(p => p.name === originalValues.project);
        const currentProjectId = currentProject ? currentProject.id : "";

        let projectOptionsHTML = '<option value="">Выберите проект</option>';
        projectsData.forEach(project => {
            projectOptionsHTML += `<option value="${project.id}" ${project.id == currentProjectId ? 'selected' : ''}>${project.name}</option>`;
        });

        cells[0].innerHTML = `<input type="date" name="edit-date" value="${originalValues.date}" class="form-control form-control-sm">`;
        cells[2].innerHTML = `<select name="edit-project" class="form-control form-control-sm">${projectOptionsHTML}</select>`;
        cells[3].innerHTML = `<input type="number" name="edit-hours" value="${originalValues.hours}" min="0" step="0.5" class="form-control form-control-sm">`;
        cells[4].innerHTML = `<input type="text" name="edit-comment" value="${originalValues.comment}" class="form-control form-control-sm">`;
        cells[6].innerHTML = `
            <button class="button save-edit-btn" title="Сохранить"><i class="fas fa-check"></i></button>
            <button class="button cancel-edit-btn" title="Отмена"><i class="fas fa-times"></i></button>
        `;

        row.querySelector('.save-edit-btn').addEventListener('click', function() {
            const updatedData = {
                date: row.querySelector('[name="edit-date"]').value,
                project_id: row.querySelector('[name="edit-project"]').value,
                hours_number: row.querySelector('[name="edit-hours"]').value,
                comment: row.querySelector('[name="edit-comment"]').value,
            };

            if (!updatedData.date) { alert("Пожалуйста, выберите дату."); return; }
            if (!updatedData.project_id) { alert("Пожалуйста, выберите проект."); return; }
            if (updatedData.hours_number === "" || parseFloat(updatedData.hours_number) < 0) {
                alert("Пожалуйста, введите корректное количество часов (не отрицательное).");
                return;
            }

            const updateUrl = updateEntryUrlTemplate.replace('0', entryId);

            fetch(updateUrl, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(updatedData)
            })
            .then(response => {
                if (!response.ok) {
                     return response.json().then(errData => {
                        throw new Error(errData.error || `Ошибка сервера: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.entry) {
                    cells[0].textContent = data.entry.date;
                    cells[1].textContent = data.entry.worker_username;
                    cells[2].textContent = data.entry.project_name;
                    cells[3].textContent = data.entry.hours_number;
                    cells[4].textContent = data.entry.comment;
                    cells[5].textContent = data.entry.approval_status;
                    cells[6].innerHTML = originalValues.actions;

                    row.classList.remove('editing');
                    row.querySelector('.edit-row-btn').addEventListener('click', handleEditClick);
                    row.querySelector('.delete-row-btn').addEventListener('click', handleDeleteClick);
                } else {
                    alert('Ошибка обновления: ' + (data.error || 'Неизвестная ошибка.'));
                }
            })
            .catch(error => {
                console.error("Update error:", error);
                alert("Произошла ошибка при обновлении записи: " + error.message);
            });
        });

        row.querySelector('.cancel-edit-btn').addEventListener('click', function() {
            cells[0].textContent = originalValues.date;
            cells[2].textContent = originalValues.project;
            cells[3].textContent = originalValues.hours;
            cells[4].textContent = originalValues.comment;
            cells[6].innerHTML = originalValues.actions;

            row.classList.remove('editing');
            row.querySelector('.edit-row-btn').addEventListener('click', handleEditClick);
            row.querySelector('.delete-row-btn').addEventListener('click', handleDeleteClick);
        });
    }

    if (addButton) {
        addButton.addEventListener("click", function () {
            if (tableBody.querySelector('tr.new-entry-row')) {
                alert("Пожалуйста, сначала сохраните или отмените текущую новую запись.");
                return;
            }

            const newRow = tableBody.insertRow(0);
            newRow.classList.add('new-entry-row');

            let projectOptionsHTML = '<option value="">Выберите проект</option>';
            projectsData.forEach(project => {
                projectOptionsHTML += `<option value="${project.id}">${project.name}</option>`;
            });

            const today = new Date().toISOString().split('T')[0];

            newRow.innerHTML = `
                <td style="min-width: 180px;">
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <label style="white-space: nowrap;">с</label>
                            <input type="date" name="start_date" value="${today}" class="form-control form-control-sm" style="flex: 1;">
                        </div>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <label style="white-space: nowrap;">по</label>
                            <input type="date" name="end_date" value="${today}" class="form-control form-control-sm" style="flex: 1;">
                        </div>
                    </div>
                </td>
                <td>${currentUserUsername}</td>
                <td>
                    <select name="project" style="width:100%">
                        ${projectOptionsHTML}
                    </select>
                </td>
                <td><input type="number" name="hours_number" min="0" step="0.5" style="width:100%"/></td>
                <td><input type="text" name="comment" style="width:100%"/>
                <td>pending</td>
                <td>
                    <button class="save-row button" title="Сохранить"><i class="fas fa-check"></i></button>
                    <button class="cancel-row button" title="Отменить"><i class="fas fa-times"></i></button>
                </td>
            `;

            removeNoRecordsMessage();

            newRow.querySelector(".cancel-row").addEventListener("click", () => {
                newRow.remove();
                showNoRecordsMessage();
            });

            newRow.querySelector(".save-row").addEventListener("click", () => {
                const startDateInput = newRow.querySelector('[name="start_date"]');
                const endDateInput = newRow.querySelector('[name="end_date"]');
                const projectSelect = newRow.querySelector('[name="project"]');
                const hoursInput = newRow.querySelector('[name="hours_number"]');
                const commentInput = newRow.querySelector('[name="comment"]');

                const startDate = startDateInput.value;
                const endDate = endDateInput.value;
                const projectId = projectSelect.value;
                const hours = hoursInput.value;
                const comment = commentInput.value;

                if (!startDate || !endDate) { alert("Пожалуйста, выберите обе даты."); return; }
                if (startDate > endDate) { alert("Начальная дата не может быть позже конечной."); return; }
                if (!projectId) { alert("Пожалуйста, выберите проект."); projectSelect.focus(); return; }
                if (hours === "" || parseFloat(hours) < 0) { alert("Пожалуйста, введите корректное количество часов (не отрицательное)."); hoursInput.focus(); return; }

                const dates = getDateRangeArray(startDate, endDate);
                const promises = dates.map(date => {
                    return fetch(addEntryUrl, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken,
                        },
                        body: JSON.stringify({
                            date: date,
                            project_id: projectId,
                            hours_number: hours,
                            comment: comment,
                        }),
                    });
                });

                Promise.all(promises)
                    .then(responses => Promise.all(responses.map(res => {
                        if (!res.ok) {
                            return res.json().then(err => {
                                throw new Error(err.error || `Ошибка сервера: ${res.status}`);
                            });
                        }
                        return res.json();
                    })))
                    .then(results => {
                        if (results.every(r => r.success)) {
                            location.reload();
                        } else {
                            const errors = results.filter(r => !r.success).map(r => r.error).join(", ");
                            alert("Некоторые записи не добавлены: " + errors);
                        }
                    })
                    .catch(error => {
                        console.error("Ошибка при отправке:", error);
                        alert("Произошла ошибка при добавлении записей: " + error.message);
                    });
            });
        });
    }

    document.querySelectorAll('.delete-row-btn').forEach(button => {
        button.addEventListener('click', handleDeleteClick);
    });

    document.querySelectorAll('.edit-row-btn').forEach(button => {
        button.addEventListener('click', handleEditClick);
    });

    document.querySelectorAll('.approve-btn').forEach(button => {
        button.addEventListener('click', () => updateApprovalStatus(button.dataset.id, 'approved'));
    });

    document.querySelectorAll('.reject-btn').forEach(button => {
        button.addEventListener('click', () => updateApprovalStatus(button.dataset.id, 'rejected'));
    });

    function updateApprovalStatus(entryId, status) {
        fetch(updateEntryUrlTemplate.replace("0", entryId), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                approval_status: status
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка при обновлении статуса: ' + (data.error || data.errors));
            }
        })
        .catch(err => {
            console.error("Ошибка:", err);
            alert("Ошибка сети: " + err.message);
        });
    }

}