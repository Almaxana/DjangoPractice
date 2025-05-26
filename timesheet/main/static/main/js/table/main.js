import { initializeTimesheetCrud } from './crud.js';
import './filters.js';

document.addEventListener("DOMContentLoaded", function () {
    const projectsData = window.projectsData;
    const csrfToken = window.csrfToken;
    const addEntryUrl = window.addEntryUrl;
    const currentUserUsername = window.currentUserUsername;
    const deleteEntryUrlTemplate = window.deleteEntryUrlTemplate;
    const updateEntryUrlTemplate = window.updateEntryUrlTemplate;

    initializeTimesheetCrud(projectsData, csrfToken, addEntryUrl, currentUserUsername, deleteEntryUrlTemplate, updateEntryUrlTemplate);
});