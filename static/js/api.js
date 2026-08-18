/**
 * EVI Dashboard - API Client
 * Centralized API communication layer.
 */

const API = {
    baseUrl: '/api',

    /**
     * Generic fetch wrapper with error handling.
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            return await response.json();

        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    /**
     * GET request.
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url);
    },

    /**
     * POST request.
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * PUT request.
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    /**
     * DELETE request.
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    },

    // ============================================================
    // API Methods
    // ============================================================

    /** Dashboard summary */
    getDashboard() {
        return this.get('/dashboard/summary');
    },

    /** Monthly renewal data */
    getRenewalMonthly(month, year) {
        const params = {};
        if (month) params.month = month;
        if (year) params.year = year;
        return this.get('/renewal/monthly', params);
    },

    /** Yearly renewal data */
    getRenewalYearly() {
        return this.get('/renewal/yearly');
    },

    /** Classes list */
    getClasses(filters = {}) {
        return this.get('/classes', filters);
    },

    /** Classes statistics */
    getClassesStats() {
        return this.get('/classes/stats');
    },

    /** Staff ACS scores */
    getStaffACS() {
        return this.get('/staff/acs');
    },

    /** Homework search */
    getHomework(filters = {}) {
        return this.get('/homework', filters);
    },

    /** Grades list/search */
    getGrades(filters = {}) {
        return this.get('/grades', filters);
    },

    /** Consolidated student lookup */
    lookupStudent(query) {
        return this.get('/student/lookup', { query });
    },

    /** Health check */
    getHealth() {
        return this.get('/health');
    },

    /** Sheets list */
    getSheetsList() {
        return this.get('/sheets/list');
    },

    /** Write data back to sheet */
    writeData(sheetName, range, data) {
        return this.post('/data/write', {
            sheet_name: sheetName,
            range: range,
            data: data,
        });
    },

    /** Refresh data from Google Sheets */
    refreshData() {
        return this.post('/data/refresh');
    },

    // ============================================================
    // Auth & Users
    // ============================================================
    login(username, password) {
        return this.post('/auth/login', { username, password });
    },

    getUsers() {
        return this.get('/users');
    },

    createUser(userData) {
        return this.post('/users', userData);
    },

    updateUser(userId, userData) {
        return this.put(`/users/${userId}`, userData);
    },

    deleteUser(userId) {
        return this.delete(`/users/${userId}`);
    },

    // ============================================================
    // CM & Attendance & Grades
    // ============================================================
    getCMClasses(cmStaffName = '') {
        return this.get('/cm/classes', { cm_staff_name: cmStaffName, _t: Date.now() });
    },

    getAttendance(className, date = '') {
        return this.get('/attendance', { class_name: className, date, _t: Date.now() });
    },

    saveAttendance(data) {
        return this.post('/attendance', data);
    },

    saveGrades(gradesList) {
        return this.post('/grades/save', { grades: gradesList });
    },

    // ============================================================
    // Renewals (Tái phí) & Interactions (Nhật ký tương tác)
    // ============================================================
    saveRenewal(renewalData) {
        return this.post('/renewal/save', renewalData);
    },

    getRenewals(params = {}) {
        return this.get('/renewal/list', { ...params, _t: Date.now() });
    },

    recalculateRenewalExpiry() {
        return this.post('/renewals/calculate-expiry');
    },

    getStudentInteractions(studentCode) {
        return this.get(`/renewals/interactions/${encodeURIComponent(studentCode)}`, { _t: Date.now() });
    },

    getAllInteractions(params = {}) {
        return this.get('/interactions/all', { ...params, _t: Date.now() });
    },

    addInteraction(data) {
        return this.post('/interactions/add', data);
    },

    updateInteraction(logId, data) {
        return this.post(`/interactions/update/${logId}`, data);
    },

    getStudents(params = {}) {
        return this.get('/students', { ...params, _t: Date.now() });
    },

    deleteInteraction(logId) {
        return this.post(`/interactions/delete/${logId}`);
    },
};
