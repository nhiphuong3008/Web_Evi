/**
 * EVI Dashboard - Homework & Grades Search Module
 * Tra cứu BTVN và Điểm số học sinh.
 */

const SearchModule = {
    // Current state
    activeTab: 'homework', // 'homework' or 'grades'
    homeworkData: [],
    gradesData: [],
    availableClasses: [],
    activeClasses: [],
    archivedClasses: [],
    showArchivedClasses: false,
    selectedGradeIds: new Set(),
    currentGradesData: [],

    /**
     * Render the Homework Search Page.
     */
    async renderHomework(container) {
        this.activeTab = 'homework';
        await this.renderMainLayout(container);
    },

    /**
     * Render the Grades Search Page.
     */
    async renderGrades(container) {
        this.activeTab = 'grades';
        await this.renderMainLayout(container);
    },

    /**
     * Render main search layout with tabs and search filters.
     */
    async renderMainLayout(container) {
        container.innerHTML = `
            <!-- Page Tabs & Search Bar Header -->
            <div class="chart-card full-width" style="margin-bottom: 24px;">
                <div class="section-header" style="flex-wrap: wrap; gap: 16px;">
                    <!-- Navigation Tabs -->
                    <div style="display: flex; gap: 8px;">
                        <button class="btn ${this.activeTab === 'homework' ? 'btn-primary' : ''}" id="tab-btn-homework" onclick="SearchModule.switchTab('homework')">
                            <span class="btn-icon">📝</span>
                            Tra cứu Bài về nhà
                        </button>
                        <button class="btn ${this.activeTab === 'grades' ? 'btn-primary' : ''}" id="tab-btn-grades" onclick="SearchModule.switchTab('grades')">
                            <span class="btn-icon">💯</span>
                            Tra cứu Điểm số
                        </button>
                    </div>

                    <!-- Search Input Box -->
                    <div style="display: flex; gap: 10px; flex: 1; min-width: 280px; max-width: 500px;">
                        <div style="position: relative; width: 100%;">
                            <input type="text" id="search-input" class="search-input" 
                                placeholder="${this.activeTab === 'homework' ? 'Nhập Tên hoặc Mã học viên (VD: EVI232, Phạm Minh Vũ)...' : 'Nhập Tên hoặc Tên tiếng Anh (VD: Minh Quân, Ronald)...'}" 
                                onkeyup="if(event.key==='Enter') SearchModule.performSearch()">
                            <span style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); cursor: pointer;" onclick="SearchModule.performSearch()">🔍</span>
                        </div>
                        <button class="btn btn-primary" onclick="SearchModule.performSearch()">Tìm kiếm</button>
                    </div>
                </div>

                <!-- Secondary Filters -->
                <div id="filter-bar" style="display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; align-items: center; border-top: 1px solid var(--border-color); padding-top: 16px;">
                    <!-- Filters dynamically rendered based on active tab -->
                </div>
            </div>

            <!-- Content Area -->
            <div id="search-results-area">
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Đang tải dữ liệu...</div>
                </div>
            </div>
        `;

        this.renderFilters();
        await this.loadData();
    },

    /**
     * Render filter controls based on current active tab.
     */
    renderFilters() {
        const filterBar = document.getElementById('filter-bar');
        if (!filterBar) return;

        if (this.activeTab === 'homework') {
            filterBar.innerHTML = `
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <label style="font-size: 12px; font-weight: 700; color: var(--text-muted);">TÌNH TRẠNG:</label>
                        <select id="filter-status" class="filter-select" onchange="SearchModule.performSearch()">
                            <option value="">Tất cả tình trạng BTVN</option>
                            <option value="Chưa nộp BTVN">⚠️ Chưa nộp BTVN</option>
                            <option value="Nộp muộn">⏱️ Nộp muộn</option>
                            <option value="Đã nộp">✅ Đã nộp</option>
                            <option value="Không có BTVN">⚪ Không có BTVN</option>
                            <option value="Nghỉ học">🏖️ Nghỉ học</option>
                            <option value="Học buổi đầu">🐣 Học buổi đầu</option>
                        </select>
                    </div>

                    <div style="display: flex; align-items: center; gap: 6px;">
                        <label style="font-size: 12px; font-weight: 700; color: var(--text-muted);">LỚP HỌC:</label>
                        <select id="filter-class" class="filter-select" onchange="SearchModule.performSearch()" style="min-width: 200px;">
                            <option value="">Tất cả các Lớp</option>
                        </select>
                    </div>

                    <div style="display: flex; align-items: center; gap: 6px;">
                        <label style="font-size: 12px; font-weight: 700; color: var(--text-muted);">📅 TỪ NGÀY:</label>
                        <input type="date" id="filter-start-date" class="filter-select" onchange="SearchModule.performSearch()" style="padding: 5px 8px; border-radius: 6px;">
                    </div>

                    <div style="display: flex; align-items: center; gap: 6px;">
                        <label style="font-size: 12px; font-weight: 700; color: var(--text-muted);">ĐẾN NGÀY:</label>
                        <input type="date" id="filter-end-date" class="filter-select" onchange="SearchModule.performSearch()" style="padding: 5px 8px; border-radius: 6px;">
                    </div>

                    <button class="btn" style="margin-left: auto;" onclick="SearchModule.resetFilters()">🔄 Làm mới bộ lọc</button>
                </div>
            `;
        } else {
            filterBar.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">LỌC THEO LỚP HỌC:</div>
                    <select id="filter-class" class="filter-select" onchange="SearchModule.performSearch()">
                        <option value="">Tất cả các Lớp</option>
                    </select>

                    <div style="font-size: 12px; color: var(--text-muted); font-weight: 600; margin-left: 12px;">LỌC THEO UNIT / BÀI TEST:</div>
                    <select id="filter-test" class="filter-select" onchange="SearchModule.performSearch()">
                        <option value="">Tất cả các Unit</option>
                    </select>

                    <label style="display: flex; align-items: center; gap: 5px; margin-left: 12px; font-size: 12px; color: var(--text-muted); cursor: pointer; user-select: none;">
                        <input type="checkbox" id="toggle-archived" ${this.showArchivedClasses ? 'checked' : ''}
                            onchange="SearchModule.toggleArchivedClasses()" 
                            style="accent-color: #6366f1; cursor: pointer;">
                        Hiện lớp cũ
                    </label>
                </div>
                <button class="btn" style="margin-left: auto;" onclick="SearchModule.resetFilters()">Làm mới bộ lọc</button>
            `;
        }
    },

    /**
     * Switch between Homework and Grades tabs.
     */
    switchTab(tab) {
        this.activeTab = tab;

        const hwBtn = document.getElementById('tab-btn-homework');
        const grBtn = document.getElementById('tab-btn-grades');
        if (hwBtn) hwBtn.className = `btn ${tab === 'homework' ? 'btn-primary' : ''}`;
        if (grBtn) grBtn.className = `btn ${tab === 'grades' ? 'btn-primary' : ''}`;

        this.renderFilters();
        this.loadData();

        window.location.hash = `#${tab === 'homework' ? 'homework' : 'grades'}`;
    },

    /**
     * Load data for current active tab.
     */
    async loadData() {
        const resultsArea = document.getElementById('search-results-area');
        if (!resultsArea) return;

        try {
            if (this.activeTab === 'homework') {
                const cmStaff = (typeof AuthModule !== 'undefined' && AuthModule.getCMStaffName) ? AuthModule.getCMStaffName() : '';
                const userRole = (typeof AuthModule !== 'undefined' && AuthModule.getUserRole) ? AuthModule.getUserRole() : '';

                const res = await API.getHomework({ cm_staff: cmStaff, user_role: userRole });
                if (res.success) {
                    this.homeworkData = res.data;
                    this.updateHomeworkClassDropdown(res.available_classes || [], res.cm_assigned_classes || []);
                    this.renderHomeworkResults(res.data, '', 1, res.summary);
                }
            } else {
                const res = await API.getGrades();
                if (res.success) {
                    this.gradesData = res.data;
                    this.activeClasses = res.active_classes || [];
                    this.archivedClasses = res.archived_classes || [];
                    this.updateClassAndTestDropdowns(res.active_classes || [], res.archived_classes || [], res.available_tests);
                    this.renderGradesResults(res.data);
                }
            }
        } catch (err) {
            resultsArea.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <h3>Không thể lấy dữ liệu</h3>
                    <p>${err.message}</p>
                </div>
            `;
        }
    },

    /**
     * Populate class selection dropdown for Grades tab.
     */
    populateClassDropdown() {
        const select = document.getElementById('filter-class');
        if (!select) return;

        let options = '<option value="">Tất cả các Lớp</option>';
        this.availableClasses.forEach(cls => {
            options += `<option value="${cls}">${cls}</option>`;
        });
        select.innerHTML = options;
    },

    /**
     * Perform search & filtering.
     */
    async performSearch() {
        const searchInput = document.getElementById('search-input');
        const query = searchInput ? searchInput.value.trim() : '';

        const resultsArea = document.getElementById('search-results-area');
        if (resultsArea) {
            resultsArea.innerHTML = `
                <div class="loading-container" style="min-height: 200px;">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Đang tìm kiếm...</div>
                </div>
            `;
        }

        try {
            if (this.activeTab === 'homework') {
                const statusSelect = document.getElementById('filter-status');
                const status = statusSelect ? statusSelect.value : '';
                const classSelect = document.getElementById('filter-class');
                const selectedClass = classSelect ? classSelect.value : '';
                const startDateInput = document.getElementById('filter-start-date');
                const startDate = startDateInput ? startDateInput.value : '';
                const endDateInput = document.getElementById('filter-end-date');
                const endDate = endDateInput ? endDateInput.value : '';
                const cmStaff = (typeof AuthModule !== 'undefined' && AuthModule.getCMStaffName) ? AuthModule.getCMStaffName() : '';
                const userRole = (typeof AuthModule !== 'undefined' && AuthModule.getUserRole) ? AuthModule.getUserRole() : '';

                const res = await API.getHomework({
                    search: query,
                    status: status,
                    class_name: selectedClass,
                    start_date: startDate,
                    end_date: endDate,
                    cm_staff: cmStaff,
                    user_role: userRole
                });
                if (res.success) {
                    this.homeworkData = res.data || [];
                    this.updateHomeworkClassDropdown(res.available_classes || [], res.cm_assigned_classes || []);
                    this.renderHomeworkResults(this.homeworkData, query, 1, res.summary);
                }
            } else {
                const classSelect = document.getElementById('filter-class');
                const selectedClass = classSelect ? classSelect.value : '';
                const testSelect = document.getElementById('filter-test');
                const selectedTest = testSelect ? testSelect.value : '';

                const res = await API.getGrades({ search: query, class_name: selectedClass, test_name: selectedTest, active_only: !this.showArchivedClasses });
                if (res.success) {
                    this.activeClasses = res.active_classes || [];
                    this.archivedClasses = res.archived_classes || [];
                    this.updateClassAndTestDropdowns(res.active_classes || [], res.archived_classes || [], res.available_tests);
                    this.renderGradesResults(res.data, query);
                }
            }
        } catch (err) {
            console.error('Search error:', err);
        }
    },

    /**
     * Populate class and test dropdown options dynamically.
     * Sử dụng optgroup để phân nhóm "Lớp đang học" và "Lớp cũ".
     */
    updateClassAndTestDropdowns(activeClasses = [], archivedClasses = [], tests = []) {
        const classSelect = document.getElementById('filter-class');
        if (classSelect) {
            const currentVal = classSelect.value;
            classSelect.innerHTML = '<option value="">Tất cả các Lớp</option>';

            // Active classes optgroup
            if (activeClasses.length > 0) {
                const activeGroup = document.createElement('optgroup');
                activeGroup.label = `🟢 Lớp đang học (${activeClasses.length})`;
                activeClasses.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c;
                    opt.textContent = `Lớp ${c}`;
                    if (c === currentVal) opt.selected = true;
                    activeGroup.appendChild(opt);
                });
                classSelect.appendChild(activeGroup);
            }

            // Archived classes optgroup (only if showArchivedClasses is true)
            if (this.showArchivedClasses && archivedClasses.length > 0) {
                const archivedGroup = document.createElement('optgroup');
                archivedGroup.label = `📁 Lớp cũ (${archivedClasses.length})`;
                archivedClasses.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c;
                    opt.textContent = `Lớp ${c}`;
                    opt.style.color = '#9ca3af';
                    if (c === currentVal) opt.selected = true;
                    archivedGroup.appendChild(opt);
                });
                classSelect.appendChild(archivedGroup);
            }
        }

        const testSelect = document.getElementById('filter-test');
        if (testSelect) {
            const currentVal = testSelect.value;
            testSelect.innerHTML = '<option value="">Tất cả các Unit</option>';
            tests.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                if (t === currentVal) opt.selected = true;
                testSelect.appendChild(opt);
            });
        }
    },

    /**
     * Toggle showing archived (old) classes.
     */
    toggleArchivedClasses() {
        this.showArchivedClasses = !this.showArchivedClasses;
        this.updateClassAndTestDropdowns(this.activeClasses, this.archivedClasses, []);
        // Re-populate tests from last search
        const testSelect = document.getElementById('filter-test');
        if (testSelect) {
            // Tests are already populated, just refresh class dropdown
        }
        this.performSearch();
    },

    /**
     * Reset search and filters.
     */
    resetFilters() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = '';

        const statusSelect = document.getElementById('filter-status');
        if (statusSelect) statusSelect.value = '';

        const classSelect = document.getElementById('filter-class');
        if (classSelect) classSelect.value = '';

        const startDateInput = document.getElementById('filter-start-date');
        if (startDateInput) startDateInput.value = '';

        const endDateInput = document.getElementById('filter-end-date');
        if (endDateInput) endDateInput.value = '';

        const testSelect = document.getElementById('filter-test');
        if (testSelect) testSelect.value = '';

        this.performSearch();
    },

    /**
     * Populate class dropdown for Homework tab with Option A CM grouping.
     */
    updateHomeworkClassDropdown(availableClasses = [], cmAssignedClasses = []) {
        const classSelect = document.getElementById('filter-class');
        if (!classSelect) return;

        const currentVal = classSelect.value;
        let html = '<option value="">Tất cả các Lớp</option>';

        if (cmAssignedClasses && cmAssignedClasses.length > 0) {
            html += `<optgroup label="⭐ Lớp phụ trách (${cmAssignedClasses.length})">`;
            cmAssignedClasses.forEach(cls => {
                const escaped = AuthModule.escapeHtml(cls);
                html += `<option value="${escaped}" ${cls === currentVal ? 'selected' : ''}>🏫 ${escaped}</option>`;
            });
            html += `</optgroup>`;

            const otherClasses = availableClasses.filter(c => !cmAssignedClasses.includes(c));
            if (otherClasses.length > 0) {
                html += `<optgroup label="🌐 Lớp học khác (${otherClasses.length})">`;
                otherClasses.forEach(cls => {
                    const escaped = AuthModule.escapeHtml(cls);
                    html += `<option value="${escaped}" ${cls === currentVal ? 'selected' : ''}>🏫 ${escaped}</option>`;
                });
                html += `</optgroup>`;
            }
        } else {
            availableClasses.forEach(cls => {
                const escaped = AuthModule.escapeHtml(cls);
                html += `<option value="${escaped}" ${cls === currentVal ? 'selected' : ''}>🏫 ${escaped}</option>`;
            });
        }

        classSelect.innerHTML = html;
    },

    /**
     * Filter homework list when user clicks on any of the 4 summary KPI cards.
     */
    filterByStatus(status) {
        const select = document.getElementById('filter-status');
        if (select) {
            select.value = status;
        }
        this.performSearch();
    },

    // Pagination state
    homeworkPage: 1,
    homeworkPageSize: 25,

    /**
     * Render Homework Results table with pagination and summary cards.
     */
    renderHomeworkResults(data, query = '', page = 1, customSummary = null) {
        const container = document.getElementById('search-results-area');
        if (!container) return;

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <h3>Không tìm thấy kết quả BTVN phù hợp</h3>
                    <p>Hãy thử điều chỉnh bộ lọc lớp học, khoảng ngày hoặc từ khóa tìm kiếm khác.</p>
                </div>
            `;
            return;
        }

        // Sort reverse-chronologically (newest date first)
        const parseDateSortKey = (dateStr) => {
            if (!dateStr) return 0;
            dateStr = String(dateStr).trim();
            if (dateStr.includes('/')) {
                const parts = dateStr.split('/');
                if (parts.length === 3) {
                    return new Date(parseInt(parts[2], 10), parseInt(parts[1], 10) - 1, parseInt(parts[0], 10)).getTime();
                }
            }
            if (dateStr.includes('-')) {
                const parts = dateStr.split('-');
                if (parts.length === 3) {
                    return new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10)).getTime();
                }
            }
            const parsed = Date.parse(dateStr);
            return isNaN(parsed) ? 0 : parsed;
        };

        data.sort((a, b) => parseDateSortKey(b.date || b.submission_date) - parseDateSortKey(a.date || a.submission_date));

        this.homeworkPage = page;
        const total = customSummary ? customSummary.total : data.length;
        const totalPages = Math.ceil(data.length / this.homeworkPageSize);
        if (this.homeworkPage > totalPages) this.homeworkPage = 1;

        const startIndex = (this.homeworkPage - 1) * this.homeworkPageSize;
        const pageData = data.slice(startIndex, startIndex + this.homeworkPageSize);

        // Summary stats
        const missing = customSummary ? customSummary.missing : data.filter(d => d.status === 'Chưa nộp BTVN').length;
        const late = customSummary ? customSummary.late : data.filter(d => d.status === 'Nộp muộn').length;
        const submitted = customSummary ? customSummary.submitted : data.filter(d => d.status === 'Đã nộp').length;

        let tableRows = '';
        pageData.forEach(item => {
            let statusBadge = 'badge-danger';
            const st = (item.status || '').trim();
            if (st === 'Đã nộp' || st === 'Nộp đúng giờ') statusBadge = 'badge-success';
            else if (st === 'Nộp muộn') statusBadge = 'badge-warning';
            else if (st === 'Không có BTVN' || st === 'Không có BVN' || st === 'Không bài' || st === 'Không có') statusBadge = 'badge-secondary';
            else if (st === 'Nghỉ học' || st === 'Học buổi đầu') statusBadge = 'badge-info';

            const displayName = item.name || item.english_name || 'Học viên';
            const avatarColor = Utils.getAvatarColor(displayName);

            tableRows += `
                <tr>
                    <td><span class="badge badge-info" style="font-family: monospace; font-size: 12px;">${item.code || '—'}</span></td>
                    <td>
                        <div class="staff-name">
                            <div class="staff-avatar" style="background: ${avatarColor}">
                                ${Utils.getInitials(displayName)}
                            </div>
                            <div>
                                <strong style="color: var(--text-primary);">${displayName}</strong>
                                ${item.english_name && item.english_name !== displayName ? `<div style="font-size: 11px; color: var(--text-muted);">${item.english_name}</div>` : ''}
                            </div>
                        </div>
                    </td>
                    <td>${item.phone_class || item.class_name || '—'}</td>
                    <td><span class="badge ${statusBadge}">${item.status || 'Chưa nộp BTVN'}</span></td>
                    <td>${item.date ? `<span style="font-size: 12px; color: var(--text-secondary);">${item.date}</span>` : '<span style="color: var(--text-muted);">—</span>'}</td>
                </tr>
            `;
        });

        // Pagination Controls
        const paginationHtml = `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px 0; border-top: 1px solid var(--border-color); margin-top: 16px; flex-wrap: wrap; gap: 12px;">
                <div style="font-size: 12px; color: var(--text-muted);">
                    Hiển thị <strong>${startIndex + 1} - ${Math.min(startIndex + this.homeworkPageSize, total)}</strong> trên tổng số <strong>${total}</strong> bản ghi (Trang ${this.homeworkPage}/${totalPages})
                </div>
                <div style="display: flex; gap: 6px; align-items: center;">
                    <button class="btn" ${this.homeworkPage <= 1 ? 'disabled' : ''} onclick="SearchModule.changeHomeworkPage(${this.homeworkPage - 1})">
                        ◀ Trang trước
                    </button>
                    <span style="font-size: 12px; font-weight: 600; padding: 0 8px;">Trang ${this.homeworkPage} / ${totalPages}</span>
                    <button class="btn" ${this.homeworkPage >= totalPages ? 'disabled' : ''} onclick="SearchModule.changeHomeworkPage(${this.homeworkPage + 1})">
                        Trang sau ▶
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = `
            <!-- Summary Stats (Clickable filters) -->
            <div class="kpi-grid" style="margin-bottom: 20px;">
                <div class="kpi-card accent-purple" onclick="SearchModule.filterByStatus('')" title="Click để xem tất cả">
                    <div class="kpi-header">
                        <div class="kpi-icon purple">📋</div>
                        <div class="kpi-label">Tổng số lượt tra cứu</div>
                    </div>
                    <div class="kpi-value">${total}</div>
                    <div class="kpi-change neutral">Click xem tất cả ↗</div>
                </div>
                <div class="kpi-card accent-amber" onclick="SearchModule.filterByStatus('Chưa nộp BTVN')" title="Click để lọc học sinh chưa nộp BTVN">
                    <div class="kpi-header">
                        <div class="kpi-icon amber">⚠️</div>
                        <div class="kpi-label">Thiếu / Chưa nộp BTVN</div>
                    </div>
                    <div class="kpi-value" style="color: #f87171;">${missing}</div>
                    <div class="kpi-change negative">Click lọc danh sách ↗</div>
                </div>
                <div class="kpi-card accent-blue" onclick="SearchModule.filterByStatus('Nộp muộn')" title="Click để lọc học sinh nộp muộn">
                    <div class="kpi-header">
                        <div class="kpi-icon blue">⏱️</div>
                        <div class="kpi-label">Nộp muộn</div>
                    </div>
                    <div class="kpi-value" style="color: #fbbf24;">${late}</div>
                    <div class="kpi-change neutral">Click lọc danh sách ↗</div>
                </div>
                <div class="kpi-card accent-green" onclick="SearchModule.filterByStatus('Đã nộp')" title="Click để lọc học sinh đã nộp bài">
                    <div class="kpi-header">
                        <div class="kpi-icon green">✅</div>
                        <div class="kpi-label">Hoàn thành đúng giờ</div>
                    </div>
                    <div class="kpi-value" style="color: #34d399;">${submitted}</div>
                    <div class="kpi-change positive">Click lọc danh sách ↗</div>
                </div>
            </div>

            <!-- Table -->
            <div class="chart-card full-width">
                <div class="chart-header">
                    <div>
                        <div class="chart-title">📝 Danh Sách Học Sinh & Tình Trạng BTVN</div>
                        <div class="chart-subtitle">Hiển thị ${total} kết quả ${query ? `cho từ khóa "${query}"` : ''}</div>
                    </div>
                </div>
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Mã học viên</th>
                                <th>Học viên</th>
                                <th>Lớp học / SĐT</th>
                                <th>Tình trạng BTVN</th>
                                <th>Ngày nhập / Ghi nhận</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows}
                        </tbody>
                    </table>
                </div>
                ${paginationHtml}
            </div>
        `;
    },

    /**
     * Render Grades Search Page.
     */
    renderGradesPage(container) {
        container.innerHTML = `
            <div class="search-header">
                <div class="search-title">
                    <h2>Tra cứu Điểm số</h2>
                    <p class="text-muted">Bảng điểm và đánh giá kỹ năng học sinh theo từng Unit / Bài Test</p>
                </div>
            </div>

            <!-- Controls -->
            <div class="search-controls-card glass-panel" style="margin-bottom: 24px; padding: 20px;">
                <div class="search-tab-bar" style="margin-bottom: 20px; display: flex; gap: 12px; align-items: center;">
                    <button class="tab-btn" onclick="SearchModule.switchTab('homework')">
                        📋 Tra cứu Bài về nhà
                    </button>
                    <button class="tab-btn active" onclick="SearchModule.switchTab('grades')">
                        💯 Tra cứu Điểm số
                    </button>
                </div>

                <div style="display: grid; grid-template-columns: minmax(200px, 1fr) minmax(200px, 1fr) 2fr auto; gap: 12px; align-items: center;">
                    <div>
                        <label style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 4px;">Lớp học</label>
                        <select id="filter-class" class="form-control" onchange="SearchModule.performSearch()">
                            <option value="">Tất cả các Lớp</option>
                        </select>
                    </div>

                    <div>
                        <label style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 4px;">Bài Test / Unit</label>
                        <select id="filter-test" class="form-control" onchange="SearchModule.performSearch()">
                            <option value="">Tất cả các Unit</option>
                        </select>
                    </div>

                    <div>
                        <label style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 4px;">Từ khóa tìm kiếm</label>
                        <div class="search-input-wrapper" style="position: relative;">
                            <input type="text" id="search-input" class="form-control" placeholder="Nhập Tên hoặc Tên tiếng Anh (VD: Minh Quân, Ronald)..." onkeyup="if(event.key === 'Enter') SearchModule.performSearch()">
                            <span class="search-icon" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%);">🔍</span>
                        </div>
                    </div>

                    <div style="align-self: end;">
                        <button class="btn btn-primary" onclick="SearchModule.performSearch()" style="height: 42px;">
                            Tìm kiếm
                        </button>
                    </div>
                </div>
            </div>

            <!-- Results -->
            <div id="search-results-area">
                <div class="loading-spinner">Đang tải bảng điểm...</div>
            </div>
        `;
    },

    /**
     * Toggle "Chọn tất cả" checkbox for grades.
     */
    toggleSelectAllGrades(isCheck) {
        if (!this.currentGradesData || this.currentGradesData.length === 0) return;

        if (isCheck) {
            this.currentGradesData.forEach(item => {
                const id = item.id || `${item.code}_${item.test_name}`;
                this.selectedGradeIds.add(id);
            });
        } else {
            this.selectedGradeIds.clear();
        }

        // Update card checkboxes and styles
        this.currentGradesData.forEach(item => {
            const id = item.id || `${item.code}_${item.test_name}`;
            const cb = document.getElementById(`grade-cb-${id}`);
            const card = document.getElementById(`grade-card-${id}`);
            if (cb) cb.checked = isCheck;
            if (card) {
                if (isCheck) {
                    card.style.border = '2px solid #6366f1';
                    card.style.background = 'rgba(99, 102, 241, 0.06)';
                } else {
                    card.style.border = '1px solid var(--border-color)';
                    card.style.background = '';
                }
            }
        });

        this.updateSelectedGradeCountUI();
    },

    /**
     * Toggle selection of an individual student grade card.
     */
    toggleGradeItemSelection(itemId, isCheck) {
        if (isCheck) {
            this.selectedGradeIds.add(itemId);
        } else {
            this.selectedGradeIds.delete(itemId);
        }

        const card = document.getElementById(`grade-card-${itemId}`);
        if (card) {
            if (isCheck) {
                card.style.border = '2px solid #6366f1';
                card.style.background = 'rgba(99, 102, 241, 0.06)';
            } else {
                card.style.border = '1px solid var(--border-color)';
                card.style.background = '';
            }
        }

        // Update select all checkbox state
        const selectAllCb = document.getElementById('select-all-grades-cb');
        if (selectAllCb && this.currentGradesData) {
            const allChecked = this.currentGradesData.every(item => {
                const id = item.id || `${item.code}_${item.test_name}`;
                return this.selectedGradeIds.has(id);
            });
            selectAllCb.checked = allChecked;
        }

        this.updateSelectedGradeCountUI();
    },

    /**
     * Update selected count UI text.
     */
    updateSelectedGradeCountUI() {
        const countSpan = document.getElementById('selected-count');
        const exportBtn = document.getElementById('btn-export-grades-excel');
        const exportPdfBtn = document.getElementById('btn-export-grades-pdf');
        const selCount = this.selectedGradeIds ? this.selectedGradeIds.size : 0;

        if (countSpan) countSpan.textContent = selCount;

        const countText = selCount > 0 ? `(${selCount})` : '(Tất cả)';
        if (exportBtn) exportBtn.innerHTML = `📊 Xuất Excel / CSV ${countText}`;
        if (exportPdfBtn) exportPdfBtn.innerHTML = `📄 In Báo Cáo PDF ${countText}`;
    },

    /**
     * Helper to clean string for safe PDF filenames.
     */
    cleanPdfFilename(str) {
        if (!str) return '';
        return str.normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/đ/g, 'd').replace(/Đ/g, 'D')
            .replace(/[^a-zA-Z0-9]/g, '_')
            .replace(/_+/g, '_')
            .strip ? str.trim() : str;
    },

    /**
     * Export PDF report for a single student item.
     * Sets document <title> to "Bao_Cao_Diem_So_[TenHocSinh]_[TenBaiTest]"
     * so browser automatically names the saved PDF file accordingly.
     */
    exportSingleStudentPdf(itemId) {
        if (!this.currentGradesData) return;

        const item = this.currentGradesData.find(i => {
            const id = i.id || `${i.code}_${i.test_name}`;
            return id === itemId || i.id === itemId;
        });

        if (!item) {
            alert('Không tìm thấy thông tin học sinh.');
            return;
        }

        const displayName = item.name || item.english_name || 'Hoc_Sinh';
        const testName = item.test_name || 'Unit_Test';
        const className = item.class_name || '';

        // Generate clean title string for PDF filename
        const cleanName = displayName.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
        const cleanTest = testName.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
        const pdfTitle = `Bao_Cao_Diem_So_${cleanName}_${cleanTest}`;

        const printWin = window.open('', '_blank');
        if (!printWin) {
            alert('Vui lòng cho phép Pop-up trình duyệt để xem Báo Cáo PDF.');
            return;
        }

        const listen = item.listening !== null && item.listening !== undefined ? item.listening : '—';
        const listenMax = item.listening_max || 10;
        const read = item.reading_writing !== null && item.reading_writing !== undefined ? item.reading_writing : '—';
        const readMax = item.reading_writing_max || 12;
        const speak = item.speaking !== null && item.speaking !== undefined ? item.speaking : '—';
        const speakMax = item.speaking_max || 10;

        const total = item.total_score !== null && item.total_score !== undefined ? item.total_score : '—';
        const maxScore = item.max_score || 22;
        const pct = (item.total_score !== null && maxScore > 0) ? Math.round((item.total_score / maxScore) * 100) : 0;

        printWin.document.write(`
            <!DOCTYPE html>
            <html lang="vi">
            <head>
                <meta charset="UTF-8">
                <title>${pdfTitle}</title>
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">
                <style>
                    body { font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f1f5f9; padding: 24px; color: #0f172a; }
                    .report-container { max-width: 850px; margin: 0 auto; background: #ffffff; padding: 36px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }
                    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #6366f1; padding-bottom: 20px; margin-bottom: 28px; }
                    .title { font-size: 22px; font-weight: 800; color: #1e1b4b; }
                    .subtitle { font-size: 13px; color: #64748b; margin-top: 4px; }
                    @media print {
                        body { background: #ffffff; padding: 0; }
                        .report-container { box-shadow: none; padding: 0; }
                        .no-print { display: none !important; }
                    }
                </style>
            </head>
            <body>
                <div class="report-container">
                    <div class="header" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #6366f1; padding-bottom: 12px; margin-bottom: 16px;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 48px; height: 48px; object-fit: contain;">
                            <div>
                                <div class="title" style="color: #0432ff; font-weight: 900; font-size: 20px; text-transform: uppercase;">TRUNG TÂM ANH NGỮ VICARE</div>
                                <div class="subtitle">BÁO CÁO KẾT QUẢ ĐIỂM SỐ & NHẬN XÉT HỌC TẬP TỔNG HỢP</div>
                            </div>
                        </div>
                        <button class="no-print" onclick="window.print()" style="background: #6366f1; color: #ffffff; border: none; padding: 10px 22px; border-radius: 8px; font-weight: 800; cursor: pointer; font-size: 14px; box-shadow: 0 4px 12px rgba(99,102,241,0.3);">
                            🖨️ In / Lưu PDF (${displayName})
                        </button>
                    </div>

                    <div style="border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 24px; background: #ffffff;">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #6366f1; padding-bottom: 14px; margin-bottom: 20px;">
                            <div>
                                <h3 style="margin: 0; font-size: 20px; color: #1e1b4b; font-weight: 800;">
                                    ${displayName} ${item.english_name ? `(${item.english_name})` : ''}
                                </h3>
                                <div style="font-size: 13.5px; color: #64748b; margin-top: 5px;">
                                    Mã HS: <strong>${item.code || '—'}</strong> | Lớp: <strong>${item.class_name || '—'}</strong> | Giáo trình: <strong>${item.course || '—'}</strong>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 15px; font-weight: 800; background: #EEF2FF; color: #4F46E5; padding: 8px 18px; border-radius: 20px; border: 1px solid #C7D2FE;">
                                    🎯 ${testName}: ${total} / ${maxScore} điểm (${pct}%)
                                </div>
                            </div>
                        </div>

                        <!-- Scores Table -->
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: 14px;">
                            <thead>
                                <tr style="background: #f8fafc; text-align: center;">
                                    <th style="padding: 10px; border: 1px solid #cbd5e1;">🎧 Kỹ năng Nghe</th>
                                    <th style="padding: 10px; border: 1px solid #cbd5e1;">📖 Kỹ năng Đọc - Viết</th>
                                    <th style="padding: 10px; border: 1px solid #cbd5e1;">🗣️ Kỹ năng Nói</th>
                                    <th style="padding: 10px; border: 1px solid #cbd5e1;">🏆 Điểm Tổng Kết</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="text-align: center; font-weight: 700;">
                                    <td style="padding: 12px; border: 1px solid #cbd5e1; color: #4f46e5; font-size: 17px;">${listen} / ${listenMax}</td>
                                    <td style="padding: 12px; border: 1px solid #cbd5e1; color: #059669; font-size: 17px;">${read} / ${readMax}</td>
                                    <td style="padding: 12px; border: 1px solid #cbd5e1; color: #d97706; font-size: 17px;">${speak} / ${speakMax}</td>
                                    <td style="padding: 12px; border: 1px solid #cbd5e1; color: #1e1b4b; font-size: 18px; background: #faf5ff;">${total} / ${maxScore}</td>
                                </tr>
                            </tbody>
                        </table>

                        ${item.comment ? `
                            <div style="background: #f8fafc; border-left: 4px solid #6366f1; padding: 16px 18px; border-radius: 0 8px 8px 0; font-size: 13.5px; color: #334155; line-height: 1.6; white-space: pre-line;">
                                <strong style="color: #4338ca; font-size: 14px;">💬 Nhận xét chi tiết của Giáo viên:</strong><br>${item.comment}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </body>
            </html>
        `);
        printWin.document.close();
    },

    /**
     * Export selected or all visible student grades (Excel CSV or Printable PDF).
     */
    exportGradesReport(format = 'excel') {
        if (!this.currentGradesData || this.currentGradesData.length === 0) {
            alert('Không có dữ liệu điểm số để xuất báo cáo.');
            return;
        }

        // Determine which items to export
        let itemsToExport = [];
        if (this.selectedGradeIds && this.selectedGradeIds.size > 0) {
            itemsToExport = this.currentGradesData.filter(item => {
                const id = item.id || `${item.code}_${item.test_name}`;
                return this.selectedGradeIds.has(id);
            });
        } else {
            itemsToExport = [...this.currentGradesData];
        }

        if (itemsToExport.length === 0) {
            alert('Vui lòng chọn ít nhất một học sinh để xuất báo cáo.');
            return;
        }

        // If only 1 student is selected and PDF requested, open single student PDF window directly
        if (format === 'pdf' && itemsToExport.length === 1) {
            const singleId = itemsToExport[0].id || `${itemsToExport[0].code}_${itemsToExport[0].test_name}`;
            this.exportSingleStudentPdf(singleId);
            return;
        }

        if (format === 'excel') {
            // Generate Excel/CSV file download
            let csv = '\ufeff'; // UTF-8 BOM for Excel
            csv += "STT,Mã Học Sinh,Họ và Tên Học Sinh,Tên Tiếng Anh,Lớp Học,Giáo Trình,Bài Kiểm Tra,Nghe (Listening /10),Đọc - Viết (R&W /12),Nói (Speaking /10),Tổng Điểm,Tỷ Lệ (%),Nhận Xét Của Giáo Viên\n";

            itemsToExport.forEach((item, idx) => {
                const stt = idx + 1;
                const code = (item.code || '').replace(/"/g, '""');
                const name = (item.name || '').replace(/"/g, '""');
                const enName = (item.english_name || '').replace(/"/g, '""');
                const cls = (item.class_name || '').replace(/"/g, '""');
                const course = (item.course || '').replace(/"/g, '""');
                const test = (item.test_name || '').replace(/"/g, '""');

                const listen = item.listening !== null && item.listening !== undefined ? item.listening : '';
                const read = item.reading_writing !== null && item.reading_writing !== undefined ? item.reading_writing : '';
                const speak = item.speaking !== null && item.speaking !== undefined ? item.speaking : '';
                const total = item.total_score !== null && item.total_score !== undefined ? item.total_score : '';

                const maxScore = item.max_score || 22;
                const pct = (total !== '' && maxScore > 0) ? Math.round((total / maxScore) * 100) + '%' : '';
                const cmt = (item.comment || '').replace(/"/g, '""').replace(/\n/g, ' ');

                csv += `${stt},"${code}","${name}","${enName}","${cls}","${course}","${test}",${listen},${read},${speak},${total},"${pct}","${cmt}"\n`;
            });

            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            const dateStr = new Date().toISOString().slice(0, 10);
            link.setAttribute('href', url);
            link.setAttribute('download', `Bao_Cao_Diem_So_EVI_${dateStr}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

        } else if (format === 'pdf') {
            // Multiple students export mode
            const printWin = window.open('', '_blank');
            if (!printWin) {
                alert('Vui lòng cho phép Pop-up trình duyệt để xem Báo Cáo PDF.');
                return;
            }

            const firstCls = itemsToExport[0]?.class_name || '';
            const firstTest = itemsToExport[0]?.test_name || '';
            const cleanCls = firstCls.replace(/[^a-zA-Z0-9]/g, '_');
            const cleanTest = firstTest.replace(/[^a-zA-Z0-9]/g, '_');
            const mainPdfTitle = `Bao_Cao_Diem_So_${itemsToExport.length}_Hoc_Sinh_${cleanCls}_${cleanTest}`;

            let printRowsHtml = '';
            itemsToExport.forEach((item, idx) => {
                const itemId = item.id || `${item.code}_${item.test_name}`;
                const displayName = item.name || item.english_name || 'Học viên';
                const cleanName = displayName.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
                const cleanItemTest = (item.test_name || 'Test').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
                const singleTitle = `Bao_Cao_Diem_So_${cleanName}_${cleanItemTest}`;

                const listen = item.listening !== null && item.listening !== undefined ? item.listening : '—';
                const listenMax = item.listening_max || 10;
                const read = item.reading_writing !== null && item.reading_writing !== undefined ? item.reading_writing : '—';
                const readMax = item.reading_writing_max || 12;
                const speak = item.speaking !== null && item.speaking !== undefined ? item.speaking : '—';
                const speakMax = item.speaking_max || 10;

                const total = item.total_score !== null && item.total_score !== undefined ? item.total_score : '—';
                const maxScore = item.max_score || 22;
                const pct = (item.total_score !== null && maxScore > 0) ? Math.round((item.total_score / maxScore) * 100) : 0;

                printRowsHtml += `
                    <div style="page-break-inside: avoid; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 24px; background: #ffffff;">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #6366f1; padding-bottom: 12px; margin-bottom: 16px;">
                            <div>
                                <h3 style="margin: 0; font-size: 18px; color: #1e1b4b; font-weight: 800;">
                                    ${idx + 1}. ${displayName} ${item.english_name ? `(${item.english_name})` : ''}
                                </h3>
                                <div style="font-size: 13px; color: #64748b; margin-top: 4px;">
                                    Mã HS: <strong>${item.code || '—'}</strong> | Lớp: <strong>${item.class_name || '—'}</strong> | Giáo trình: <strong>${item.course || '—'}</strong>
                                </div>
                            </div>
                            <div style="text-align: right; display: flex; align-items: center; gap: 8px;">
                                <div style="font-size: 14px; font-weight: 800; background: #EEF2FF; color: #4F46E5; padding: 6px 16px; border-radius: 20px; border: 1px solid #C7D2FE;">
                                    🎯 ${item.test_name || 'UNIT TEST'}: ${total} / ${maxScore} điểm (${pct}%)
                                </div>
                            </div>
                        </div>

                        <!-- Scores Table -->
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 14px; font-size: 13.5px;">
                            <thead>
                                <tr style="background: #f8fafc; text-align: center;">
                                    <th style="padding: 8px; border: 1px solid #cbd5e1;">🎧 Kỹ năng Nghe</th>
                                    <th style="padding: 8px; border: 1px solid #cbd5e1;">📖 Kỹ năng Đọc - Viết</th>
                                    <th style="padding: 8px; border: 1px solid #cbd5e1;">🗣️ Kỹ năng Nói</th>
                                    <th style="padding: 8px; border: 1px solid #cbd5e1;">🏆 Điểm Tổng Kết</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="text-align: center; font-weight: 700;">
                                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #4f46e5; font-size: 16px;">${listen} / ${listenMax}</td>
                                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #059669; font-size: 16px;">${read} / ${readMax}</td>
                                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #d97706; font-size: 16px;">${speak} / ${speakMax}</td>
                                    <td style="padding: 10px; border: 1px solid #cbd5e1; color: #1e1b4b; font-size: 17px; background: #faf5ff;">${total} / ${maxScore}</td>
                                </tr>
                            </tbody>
                        </table>

                        ${item.comment ? `
                            <div style="background: #f8fafc; border-left: 4px solid #6366f1; padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 13px; color: #334155; line-height: 1.5; white-space: pre-line;">
                                <strong style="color: #4338ca;">💬 Nhận xét chi tiết của Giáo viên:</strong><br>${item.comment}
                            </div>
                        ` : ''}
                    </div>
                `;
            });

            printWin.document.write(`
                <!DOCTYPE html>
                <html lang="vi">
                <head>
                    <meta charset="UTF-8">
                    <title>${mainPdfTitle}</title>
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">
                    <style>
                        body { font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f1f5f9; padding: 24px; color: #0f172a; }
                        .report-container { max-width: 900px; margin: 0 auto; background: #ffffff; padding: 36px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }
                        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #6366f1; padding-bottom: 20px; margin-bottom: 28px; }
                        .title { font-size: 22px; font-weight: 800; color: #1e1b4b; }
                        .subtitle { font-size: 13px; color: #64748b; margin-top: 4px; }
                        @media print {
                            body { background: #ffffff; padding: 0; }
                            .report-container { box-shadow: none; padding: 0; }
                            .no-print { display: none !important; }
                        }
                    </style>
                </head>
                <body>
                    <div class="report-container">
                        <div class="header" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #6366f1; padding-bottom: 12px; margin-bottom: 16px;">
                            <div style="display: flex; align-items: center; gap: 14px;">
                                <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 48px; height: 48px; object-fit: contain;">
                                <div>
                                    <div class="title" style="color: #0432ff; font-weight: 900; font-size: 20px; text-transform: uppercase;">TRUNG TÂM ANH NGỮ VICARE</div>
                                    <div class="subtitle">BÁO CÁO KẾT QUẢ ĐIỂM SỐ & NHẬN XÉT HỌC TẬP TỔNG HỢP (${itemsToExport.length} HỌC SINH)</div>
                                </div>
                            </div>
                            <button class="no-print" onclick="window.print()" style="background: #6366f1; color: #ffffff; border: none; padding: 10px 22px; border-radius: 8px; font-weight: 800; cursor: pointer; font-size: 14px;">
                                🖨️ In Gộp Tất Cả / Lưu PDF
                            </button>
                        </div>
                        ${printRowsHtml}
                        
                        <!-- Watermark Footer -->
                        <div style="margin-top: 24px; border-top: 1.5px dashed #cbd5e1; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; color: #64748b;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <img src="/static/images/logo.jpg" style="width: 16px; height: 16px; object-fit: contain;">
                                <strong>Trung tâm Anh ngữ Vicare</strong> - Hệ thống báo cáo điểm số chính thức
                            </div>
                            <div>✨ Thiết kế bởi: <strong style="color: #0284c7; font-weight: 800;">Nhi Phương</strong></div>
                        </div>
                    </div>
                </body>
                </html>
            `);
            printWin.document.close();
        }
    },

    /**
     * Render Grades Results.
     */
    renderGradesResults(data, query = '') {
        const container = document.getElementById('search-results-area');
        if (!container) return;

        this.currentGradesData = data || [];

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <h3>Không tìm thấy dữ liệu điểm số</h3>
                    <p>Hãy thử tìm kiếm theo Tên hoặc chọn Lớp / Unit khác.</p>
                </div>
            `;
            return;
        }

        // Check if all currently rendered items are selected
        const allSelected = data.length > 0 && data.every(item => {
            const id = item.id || `${item.code}_${item.test_name}`;
            return this.selectedGradeIds.has(id);
        });

        const selectedCount = data.filter(item => {
            const id = item.id || `${item.code}_${item.test_name}`;
            return this.selectedGradeIds.has(id);
        }).length;

        let cardsHtml = '';
        data.forEach(item => {
            const id = item.id || `${item.code}_${item.test_name}`;
            const isSelected = this.selectedGradeIds.has(id);
            const displayName = item.name || item.english_name || 'Học viên';
            const avatarColor = Utils.getAvatarColor(displayName);

            const listen = item.listening !== null && item.listening !== undefined ? item.listening : null;
            const listenMax = item.listening_max || 10;
            const read = item.reading_writing !== null && item.reading_writing !== undefined ? item.reading_writing : null;
            const readMax = item.reading_writing_max || 12;
            const speak = item.speaking !== null && item.speaking !== undefined ? item.speaking : null;
            const speakMax = item.speaking_max || 10;

            const total = item.total_score || 0;
            const maxScore = item.max_score || 22;
            const pct = maxScore > 0 ? Math.round((total / maxScore) * 100) : 0;

            cardsHtml += `
                <div class="chart-card glass-panel" id="grade-card-${id}" style="padding: 20px; margin-bottom: 16px; transition: all 0.2s ease; ${isSelected ? 'border: 2px solid #6366f1; background: rgba(99, 102, 241, 0.06);' : ''}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <!-- Checkbox cho từng học sinh -->
                            <input type="checkbox" id="grade-cb-${id}" ${isSelected ? 'checked' : ''} onchange="SearchModule.toggleGradeItemSelection(${item.id ? item.id : `'${id}'`}, this.checked)" style="width: 20px; height: 20px; accent-color: #6366f1; cursor: pointer; flex-shrink: 0;" title="Chọn học sinh này">

                            <div class="staff-avatar" style="background: ${avatarColor}; width: 44px; height: 44px; font-size: 16px;">
                                ${Utils.getInitials(displayName)}
                            </div>
                            <div>
                                <h3 style="margin: 0; font-size: 17px; color: var(--text-primary); font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    ${displayName}
                                    <span class="badge badge-info" style="font-size: 11px; font-weight: 600; font-family: sans-serif;">🎯 ${item.test_name || 'UNIT TEST'}</span>
                                </h3>
                                <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">
                                    ${item.english_name ? `English Name: <strong>${item.english_name}</strong> • ` : ''}
                                    Lớp: <strong>${item.class_name || '—'}</strong>
                                    ${item.course ? ` • Giáo trình: <strong>${item.course}</strong>` : ''}
                                </div>
                            </div>
                        </div>

                        <div style="text-align: right; display: flex; align-items: center; gap: 10px;">
                            <button class="btn btn-sm" onclick="SearchModule.exportSingleStudentPdf(${item.id ? item.id : `'${id}'`})" style="background: rgba(99, 102, 241, 0.12); color: var(--accent-primary-light); border: 1px solid rgba(99, 102, 241, 0.3); padding: 6px 12px; border-radius: 16px; font-size: 12px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; transition: all 0.2s;" title="Xuất Báo Cáo PDF riêng cho ${displayName}">
                                📄 In PDF
                            </button>
                            <div style="font-size: 15px; font-weight: 700; color: ${pct >= 80 ? '#34d399' : pct >= 60 ? '#fbbf24' : '#f87171'}; background: var(--bg-surface-elevated); padding: 6px 14px; border-radius: 20px; border: 1px solid var(--border-color);">
                                Tổng: ${total} / ${maxScore} điểm (${pct}%)
                            </div>
                        </div>
                    </div>

                    <!-- Skills Row -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; background: rgba(0,0,0,0.15); padding: 14px; border-radius: 12px;">
                        <div>
                            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; margin-bottom: 4px;">
                                🎧 Kỹ năng Nghe
                            </div>
                            <div style="font-size: 18px; font-weight: 700; color: var(--text-primary);">
                                ${listen !== null ? `<strong>${listen}</strong> <span style="font-size: 12px; color: var(--text-muted);">/ ${listenMax}</span>` : '<span style="font-size: 13px; color: var(--text-muted);">Đang cập nhật</span>'}
                            </div>
                            ${listen !== null ? `<div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 6px; overflow: hidden;"><div style="width: ${Math.min(100, Math.round(listen/listenMax*100))}%; height: 100%; background: #6366f1;"></div></div>` : ''}
                        </div>

                        <div>
                            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; margin-bottom: 4px;">
                                📖 Kỹ năng Đọc - Viết
                            </div>
                            <div style="font-size: 18px; font-weight: 700; color: var(--text-primary);">
                                ${read !== null ? `<strong>${read}</strong> <span style="font-size: 12px; color: var(--text-muted);">/ ${readMax}</span>` : '<span style="font-size: 13px; color: var(--text-muted);">Đang cập nhật</span>'}
                            </div>
                            ${read !== null ? `<div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 6px; overflow: hidden;"><div style="width: ${Math.min(100, Math.round(read/readMax*100))}%; height: 100%; background: #10b981;"></div></div>` : ''}
                        </div>

                        <div>
                            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; margin-bottom: 4px;">
                                🗣️ Kỹ năng Nói
                            </div>
                            <div style="font-size: 18px; font-weight: 700; color: var(--text-primary);">
                                ${speak !== null ? `<strong>${speak}</strong> <span style="font-size: 12px; color: var(--text-muted);">/ ${speakMax}</span>` : '<span style="font-size: 13px; color: var(--text-muted);">Đang cập nhật</span>'}
                            </div>
                            ${speak !== null ? `<div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 6px; overflow: hidden;"><div style="width: ${Math.min(100, Math.round(speak/speakMax*100))}%; height: 100%; background: #f59e0b;"></div></div>` : ''}
                        </div>
                    </div>

                    ${item.comment ? `
                        <div style="margin-top: 14px; padding: 12px 14px; background: rgba(99, 102, 241, 0.08); border-left: 3px solid var(--accent-primary); border-radius: 0 8px 8px 0; font-size: 13px; color: var(--text-secondary); line-height: 1.5; white-space: pre-line;">
                            <strong style="color: var(--accent-primary-light);">💬 Nhận xét của Giáo viên:</strong><br>${item.comment}
                        </div>
                    ` : ''}
                </div>
            `;
        });

        const countText = selectedCount > 0 ? `(${selectedCount})` : '(Tất cả)';

        container.innerHTML = `
            <!-- Results Bar with Selection Controls and Export Buttons -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; background: var(--bg-surface-elevated, rgba(255,255,255,0.04)); padding: 12px 18px; border-radius: 12px; border: 1px solid var(--border-color, rgba(255,255,255,0.1));">
                <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                    <div style="font-size: 14px; color: var(--text-secondary);">
                        Hiển thị <strong>${data.length}</strong> bài test / điểm số học sinh ${query ? `cho từ khóa "${query}"` : ''}
                    </div>

                    <label style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 13.5px; cursor: pointer; user-select: none; color: var(--text-primary); background: rgba(99, 102, 241, 0.12); padding: 6px 14px; border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.3);">
                        <input type="checkbox" id="select-all-grades-cb" onchange="SearchModule.toggleSelectAllGrades(this.checked)" ${allSelected ? 'checked' : ''} style="width: 18px; height: 18px; accent-color: #6366f1; cursor: pointer;">
                        <span>Chọn tất cả</span>
                    </label>

                    <span class="badge badge-info" id="selected-count-badge" style="font-size: 12px; font-weight: 700; padding: 6px 12px; border-radius: 8px;">
                        Đã chọn: <strong id="selected-count">${selectedCount}</strong> / ${data.length}
                    </span>
                </div>

                <div style="display: flex; gap: 10px; align-items: center;">
                    <button class="btn btn-sm" id="btn-export-grades-excel" onclick="SearchModule.exportGradesReport('excel')" style="background: #10b981; color: #ffffff; border: none; font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 8px; box-shadow: 0 3px 10px rgba(16,185,129,0.3); cursor: pointer;" title="Xuất file Excel / CSV các học sinh đã chọn">
                        📊 Xuất Excel / CSV ${countText}
                    </button>
                    <button class="btn btn-sm" id="btn-export-grades-pdf" onclick="SearchModule.exportGradesReport('pdf')" style="background: #6366f1; color: #ffffff; border: none; font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 8px; box-shadow: 0 3px 10px rgba(99,102,241,0.3); cursor: pointer;" title="Mở trang in Báo Cáo Học Tập PDF">
                        📄 In Báo Cáo PDF ${countText}
                    </button>
                </div>
            </div>

            ${cardsHtml}
        `;
    }
};

// CSS styles helper for search inputs and dropdowns
const searchStyles = document.createElement('style');
searchStyles.textContent = `
    .search-input {
        width: 100%;
        padding: 9px 36px 9px 14px;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm);
        background: var(--bg-secondary);
        color: var(--text-primary);
        font-family: inherit;
        font-size: 13px;
        outline: none;
        transition: border-color var(--transition-fast);
    }
    .search-input:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    .filter-select {
        padding: 8px 12px;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm);
        background: var(--bg-secondary);
        color: var(--text-primary);
        font-family: inherit;
        font-size: 12px;
        outline: none;
        cursor: pointer;
    }
    .filter-select:focus {
        border-color: var(--accent-primary);
    }
`;
document.head.appendChild(searchStyles);
