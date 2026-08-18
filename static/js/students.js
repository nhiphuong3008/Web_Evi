/**
 * EVI Dashboard - Student Directory & 360-degree Student Profile Module
 * Trang Quản Lý & Hồ Sơ Chi Tiết Học Sinh (Họ tên, Thông tin cá nhân, Học phí, BTVN, Điểm số)
 */

const StudentsModule = {
    studentsData: [],
    currentPage: 1,
    pageSize: 15,
    currentStudent: null,

    /**
     * Render the Student Directory Page.
     */
    async renderStudentsPage(container) {
        container.innerHTML = `
            <div class="search-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div class="search-title">
                    <h2>Danh sách Học sinh</h2>
                    <p class="text-muted">Quản lý hồ sơ 360° học sinh: thông tin cá nhân, phụ huynh, lớp học, số buổi học & điểm số</p>
                </div>
                ${AuthModule.isAdmin() ? `
                    <button class="btn btn-primary" onclick="StudentsModule.openAddStudentModal();" style="padding: 10px 18px; font-weight: 700; font-size: 13.5px; box-shadow: 0 4px 14px rgba(99,102,241,0.35); display: flex; align-items: center; gap: 8px;">
                        ➕ Thêm Học Sinh Mới
                    </button>
                ` : ''}
            </div>

            <!-- Controls Card -->
            <div class="chart-card full-width" style="margin-bottom: 24px;">
                <div class="filter-bar" style="display: grid; grid-template-columns: minmax(180px, 1fr) minmax(180px, 1fr) 2fr auto; gap: 16px; align-items: flex-end;">
                    <div class="filter-group">
                        <label class="filter-label" style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 6px; letter-spacing: 0.5px;">TÌNH TRẠNG HỌC</label>
                        <select id="student-filter-status" class="filter-select" style="width: 100%; font-weight: 700;" onchange="StudentsModule.performSearch()">
                            <option value="">Tất cả học sinh</option>
                            <option value="Đang học">🟢 Đang học</option>
                            <option value="Bảo lưu">🟡 Bảo lưu</option>
                            <option value="Đã nghỉ">🔴 Đã nghỉ</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label class="filter-label" style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 6px; letter-spacing: 0.5px;">LỚP HỌC</label>
                        <select id="student-filter-class" class="filter-select" style="width: 100%;" onchange="StudentsModule.performSearch()">
                            <option value="">Tất cả các Lớp</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label class="filter-label" style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 6px; letter-spacing: 0.5px;">TỪ KHÓA TÌM KIẾM</label>
                        <div class="search-input-wrapper" style="position: relative; width: 100%;">
                            <input type="text" id="student-search-input" class="search-input" style="width: 100%;" placeholder="Nhập Họ tên, Mã EVIxxx, Tên phụ huynh, SĐT..." onkeyup="if(event.key === 'Enter') StudentsModule.performSearch()">
                            <span style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); cursor: pointer;" onclick="StudentsModule.performSearch()">🔍</span>
                        </div>
                    </div>

                    <div>
                        <button class="btn btn-primary" onclick="StudentsModule.performSearch()" style="height: 42px; min-width: 110px;">
                            🔍 Tìm kiếm
                        </button>
                    </div>
                </div>
            </div>

            <!-- Student Results Area -->
            <div id="students-results-area">
                <div class="loading-spinner">Đang tải danh sách học sinh...</div>
            </div>
        `;

        await this.loadData();
    },

    /**
     * Load Students Data from API.
     */
    async loadData() {
        const area = document.getElementById('students-results-area');
        if (!area) return;

        try {
            const status = document.getElementById('student-filter-status')?.value || '';
            const className = document.getElementById('student-filter-class')?.value || '';
            const search = document.getElementById('student-search-input')?.value.trim() || '';

            const res = await API.get(`/students?status=${encodeURIComponent(status)}&class_name=${encodeURIComponent(className)}&search=${encodeURIComponent(search)}`);
            if (res.success) {
                this.studentsData = res.data || [];
                this.updateClassDropdown(res.available_classes);
                this.renderStudentList(1);
            }
        } catch (err) {
            console.error('Error loading students:', err);
            area.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <h3>Không thể tải danh sách học sinh</h3>
                    <p>${err.message}</p>
                </div>
            `;
        }
    },

    /**
     * Perform search.
     */
    performSearch() {
        this.loadData();
    },

    /**
     * Update Class Dropdown.
     */
    updateClassDropdown(classes = []) {
        this.availableClassesList = classes || [];
        const classSelect = document.getElementById('student-filter-class');
        if (classSelect && classSelect.options.length <= 1 && classes.length > 0) {
            classes.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = `Lớp ${c}`;
                classSelect.appendChild(opt);
            });
        }
    },

    /**
     * Render Student List Table with Pagination.
     */
    renderStudentList(page = 1) {
        const area = document.getElementById('students-results-area');
        if (!area) return;

        const data = this.studentsData;
        if (!data || data.length === 0) {
            area.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <h3>Không tìm thấy học sinh phù hợp</h3>
                    <p>Hãy thử tìm kiếm với từ khóa khác hoặc chọn bộ lọc Tất cả học sinh.</p>
                </div>
            `;
            return;
        }

        this.currentPage = page;
        const total = data.length;
        const totalPages = Math.ceil(total / this.pageSize);
        if (this.currentPage > totalPages) this.currentPage = 1;

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const pageData = data.slice(startIndex, startIndex + this.pageSize);

        let tableRows = '';
        pageData.forEach(st => {
            const avatarColor = Utils.getAvatarColor(st.name);
            let statusBadge = '<span class="badge badge-success">🟢 Đang học</span>';
            if (st.status === 'Bảo lưu') {
                statusBadge = '<span class="badge" style="background: rgba(245,158,11,0.2); color: #f59e0b; border: 1px solid rgba(245,158,11,0.4); font-weight: 700;">🟡 Bảo lưu</span>';
            } else if (st.status === 'Đã nghỉ') {
                statusBadge = '<span class="badge badge-danger">🔴 Đã nghỉ</span>';
            }

            let classBadges = '<span style="color: var(--text-muted);">—</span>';
            if (st.class_name) {
                const cList = st.class_name.split(',').map(c => c.trim()).filter(Boolean);
                classBadges = cList.map(c => `<span class="badge badge-info" style="margin-right: 4px; margin-bottom: 2px; display: inline-block;">Lớp ${c}</span>`).join('');
            } else if (st.last_class_name) {
                classBadges = `<span class="badge" style="background: rgba(148,163,184,0.15); color: #94a3b8; font-size: 11px;" title="Lớp học gần nhất trước khi bảo lưu/nghỉ">Lớp cũ: ${st.last_class_name}</span>`;
            }

            tableRows += `
                <tr style="cursor: pointer;" onclick="StudentsModule.openStudentProfile('${st.code}')" title="Click để xem hồ sơ đầy đủ học sinh ${st.name}">
                    <td><span class="badge badge-info" style="font-family: monospace;">${st.code}</span></td>
                    <td>
                        <div class="staff-name">
                            <div class="staff-avatar" style="background: ${avatarColor}">
                                ${Utils.getInitials(st.name)}
                            </div>
                            <div>
                                <strong style="color: var(--text-primary);">${st.name}</strong>
                                ${st.english_name ? `<div style="font-size: 11px; color: var(--text-muted);">${st.english_name}</div>` : ''}
                            </div>
                        </div>
                    </td>
                    <td>${classBadges}</td>
                    <td>${st.phone ? `<span style="font-size: 12px; color: var(--text-secondary);">${st.phone}</span>` : '<span style="color: var(--text-muted);">—</span>'}</td>
                    <td>${st.parent_name || '<span style="color: var(--text-muted);">—</span>'}</td>
                    <td>${st.remaining_sessions !== undefined && st.remaining_sessions !== 0 ? `<strong>${st.remaining_sessions}</strong> buổi` : '<span style="color: var(--text-muted);">—</span>'}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); StudentsModule.openStudentProfile('${st.code}')">
                            📄 Xem hồ sơ ↗
                        </button>
                    </td>
                </tr>
            `;
        });

        const paginationHtml = `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 16px 0; border-top: 1px solid var(--border-color); margin-top: 16px; flex-wrap: wrap; gap: 12px;">
                <div style="font-size: 12px; color: var(--text-muted);">
                    Hiển thị <strong>${startIndex + 1} - ${Math.min(startIndex + this.pageSize, total)}</strong> trên tổng số <strong>${total}</strong> học sinh (Trang ${this.currentPage}/${totalPages})
                </div>
                <div style="display: flex; gap: 6px; align-items: center;">
                    <button class="btn" ${this.currentPage <= 1 ? 'disabled' : ''} onclick="StudentsModule.renderStudentList(${this.currentPage - 1})">
                        ◀ Trang trước
                    </button>
                    <span style="font-size: 12px; font-weight: 600; padding: 0 8px;">Trang ${this.currentPage} / ${totalPages}</span>
                    <button class="btn" ${this.currentPage >= totalPages ? 'disabled' : ''} onclick="StudentsModule.renderStudentList(${this.currentPage + 1})">
                        Trang sau ▶
                    </button>
                </div>
            </div>
        `;

        area.innerHTML = `
            <div class="chart-card full-width">
                <div class="chart-header">
                    <div>
                        <div class="chart-title">👥 Danh Sách Hồ Sơ Học Sinh</div>
                        <div class="chart-subtitle">Tìm thấy ${total} học sinh (Click vào hàng bất kỳ để xem toàn bộ thông tin)</div>
                    </div>
                </div>
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Mã HS</th>
                                <th>Học viên</th>
                                <th>Lớp học</th>
                                <th>SĐT Phụ huynh</th>
                                <th>Tên Phụ huynh</th>
                                <th>Buổi còn lại</th>
                                <th>Tình trạng</th>
                                <th>Hành động</th>
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
     * Open 360-degree Student Profile Modal.
     */
    async openStudentProfile(studentCode) {
        const modal = document.getElementById('student-modal');
        const modalBody = document.getElementById('student-modal-body');
        if (!modal || !modalBody) return;

        modal.classList.add('active');
        modalBody.innerHTML = `
            <div class="loading-container" style="min-height: 300px;">
                <div class="loading-spinner"></div>
                <div class="loading-text">Đang tải hồ sơ 360° học sinh ${studentCode}...</div>
            </div>
        `;

        try {
            const res = await API.get(`/students/${encodeURIComponent(studentCode)}`);
            if (res.success) {
                this.renderProfileModalContent(res.student, res.homework, res.grades, res.summary, res.ai_assessment || {}, res.cm_notes || []);
            } else {
                modalBody.innerHTML = `<div class="empty-state">⚠️ ${res.error || 'Không thể lấy thông tin học sinh'}</div>`;
            }
        } catch (err) {
            console.error('Error getting student detail:', err);
            modalBody.innerHTML = `<div class="empty-state">⚠️ Lỗi: ${err.message}</div>`;
        }
    },

    /**
     * Render Profile Modal Content with Care History, AI Assessment, and Grade History at the bottom.
     */
    renderProfileModalContent(st, homework = [], grades = [], summary = {}, aiAssessment = {}, cmNotes = []) {
        const modalBody = document.getElementById('student-modal-body');
        if (!modalBody) return;

        const avatarColor = Utils.getAvatarColor(st.name);
        const statusBadge = st.status === 'Đang học' ? 'badge-success' : 'badge-danger';

        // 1. CM Care Notes History
        let cmCareRows = '';
        if (cmNotes && cmNotes.length > 0) {
            cmNotes.forEach(c => {
                cmCareRows += `
                    <div style="background: #ffffff; padding: 12px 14px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e2e8f0; border-left: 4px solid #059669; font-size: 13px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px; flex-wrap: wrap; gap: 6px;">
                            <strong style="color: #059669; font-size: 13.5px;">👩‍💼 Phụ trách CM: ${AuthModule.escapeHtml(c.staff_name || 'Class Manager')}</strong>
                            ${c.class_name ? `<span class="badge badge-info">${AuthModule.escapeHtml(c.class_name)}</span>` : ''}
                        </div>
                        <div style="color: #0f172a; line-height: 1.5; font-style: italic; font-weight: 600;">"${AuthModule.escapeHtml(c.note)}"</div>
                    </div>
                `;
            });
        } else {
            cmCareRows = `<div style="text-align: center; color: #64748b; padding: 16px; font-size: 13px; font-weight: 600;">Chưa có nhật ký tương tác chăm sóc ghi nhận</div>`;
        }

        // 2. Group Homework by Class & Sort Reverse-Chronologically (Newest first)
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

        let hwGrouped = {};
        if (homework && homework.length > 0) {
            homework.forEach(h => {
                let cName = (h.phone_class || h.class_name || 'Lớp chưa xác định').trim();
                if (!hwGrouped[cName]) hwGrouped[cName] = [];
                hwGrouped[cName].push(h);
            });
        }

        let hwGroupedMarkup = '';
        const hwClassKeys = Object.keys(hwGrouped);

        if (hwClassKeys.length === 0) {
            hwGroupedMarkup = `<div style="text-align: center; color: #64748b; padding: 16px; font-size: 13px; font-weight: 600;">Chưa có nhật ký BTVN ghi nhận</div>`;
        } else {
            hwClassKeys.forEach(cName => {
                const items = hwGrouped[cName];
                // Sort items in this class reverse-chronologically (newest first)
                items.sort((a, b) => parseDateSortKey(b.date || b.submission_date) - parseDateSortKey(a.date || a.submission_date));

                let rows = '';
                items.forEach(h => {
                    const st = (h.status || '').trim();
                    let sBadge = 'badge-danger';
                    if (st === 'Đã nộp' || st === 'Nộp đúng giờ') sBadge = 'badge-success';
                    else if (st === 'Nộp muộn') sBadge = 'badge-warning';
                    else if (st === 'Không có BTVN' || st === 'Không có BVN' || st === 'Không bài' || st === 'Không có') sBadge = 'badge-secondary';
                    else if (st === 'Nghỉ học' || st === 'Học buổi đầu') sBadge = 'badge-info';

                    rows += `
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="color: #0f172a; font-weight: 700;">${h.date || '—'}</td>
                            <td><span class="badge ${sBadge}">${h.status}</span></td>
                            <td style="color: #0f172a;">${h.score !== undefined && h.score !== '' ? `<strong style="color: #0f172a;">${h.score}</strong> điểm` : '—'}</td>
                        </tr>
                    `;
                });

                hwGroupedMarkup += `
                    <div style="margin-bottom: 16px; background: #f8fafc; padding: 12px 14px; border-radius: 10px; border: 1.5px solid #cbd5e1;">
                        <div style="font-weight: 800; color: #0f172a; margin-bottom: 8px; font-size: 13.5px; display: flex; align-items: center; justify-content: space-between;">
                            <span>📚 BTVN LỚP: <strong style="color: #2563eb; font-size: 14px;">${AuthModule.escapeHtml(cName)}</strong> (${items.length} lượt nộp)</span>
                        </div>
                        <div class="data-table-wrapper" style="max-height: 180px; overflow-y: auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0;">
                            <table class="data-table" style="font-size: 12.5px; width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #f1f5f9; color: #0f172a; font-weight: 800;">
                                        <th style="padding: 8px 12px; color: #0f172a;">Ngày nộp</th>
                                        <th style="padding: 8px 12px; color: #0f172a;">Tình trạng</th>
                                        <th style="padding: 8px 12px; color: #0f172a;">Điểm BTVN</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            });
        }

        // 3. Group Grade Cards & Per-Test Comments by Class
        let gradeGrouped = {};
        if (grades && grades.length > 0) {
            grades.forEach(g => {
                let cName = (g.class_name || 'Lớp chưa xác định').trim();
                if (!gradeGrouped[cName]) gradeGrouped[cName] = [];
                gradeGrouped[cName].push(g);
            });
        }

        let gradeGroupedMarkup = '';
        const gradeClassKeys = Object.keys(gradeGrouped);

        if (gradeClassKeys.length === 0) {
            gradeGroupedMarkup = `<div style="text-align: center; color: #64748b; padding: 20px; font-weight: 600;">Chưa có dữ liệu bài test</div>`;
        } else {
            gradeClassKeys.forEach(cName => {
                const items = gradeGrouped[cName];
                let cards = '';
                items.forEach(g => {
                    const pct = g.max_score ? Math.round((g.total_score / g.max_score) * 100) : 0;
                    const badgeColor = pct >= 80 ? 'badge-success' : (pct >= 65 ? 'badge-info' : 'badge-warning');
                    cards += `
                        <div style="background: #ffffff; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; border: 1.5px solid #cbd5e1; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 6px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">
                                <strong style="color: #0f172a; font-size: 15px; font-weight: 800;">🎯 ${AuthModule.escapeHtml(g.test_name || 'UNIT TEST')}</strong>
                                <span class="badge ${badgeColor}" style="font-size: 13px; padding: 5px 12px; font-weight: 800;">Tổng: ${g.total_score !== null ? g.total_score : '—'} / ${g.max_score || 10} điểm (${pct}%)</span>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; font-size: 12.5px; margin-bottom: 8px;">
                                <div style="background: #f0f9ff; border: 1px solid #bae6fd; padding: 8px 10px; border-radius: 8px; color: #0369a1; font-weight: 700;">🎧 Nghe: <strong style="color: #0f172a; font-size: 13.5px;">${g.listening !== null ? g.listening : '—'}</strong> / 10</div>
                                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 8px 10px; border-radius: 8px; color: #15803d; font-weight: 700;">📖 Đọc-Viết: <strong style="color: #0f172a; font-size: 13.5px;">${g.reading_writing !== null ? g.reading_writing : '—'}</strong> / 12</div>
                                <div style="background: #fffbeb; border: 1px solid #fde68a; padding: 8px 10px; border-radius: 8px; color: #b45309; font-weight: 700;">🗣️ Nói: <strong style="color: #0f172a; font-size: 13.5px;">${g.speaking !== null ? g.speaking : '—'}</strong> / 10</div>
                            </div>
                            ${g.comment ? `
                                <div style="font-size: 13px; color: #0f172a; background: #f8fafc; padding: 10px 14px; border-radius: 8px; border: 1.5px solid #cbd5e1; border-left: 4px solid #2563eb; margin-top: 8px; line-height: 1.5;">
                                    💬 <strong style="color: #1e293b;">GV Nhận xét:</strong> <span style="color: #0f172a; font-weight: 600;">"${AuthModule.escapeHtml(g.comment)}"</span>
                                </div>
                            ` : ''}
                        </div>
                    `;
                });

                gradeGroupedMarkup += `
                    <div style="margin-bottom: 18px; background: #f8fafc; padding: 14px; border-radius: 12px; border: 1.5px solid #cbd5e1;">
                        <div style="font-weight: 800; color: #0f172a; margin-bottom: 10px; font-size: 14px;">
                            🏫 BẢNG ĐIỂM LỚP: <strong style="color: #2563eb;">${AuthModule.escapeHtml(cName)}</strong> (${items.length} bài test)
                        </div>
                        ${cards}
                    </div>
                `;
            });
        }

        let classBadgesModal = 'Chưa xếp lớp';
        if (st.class_name) {
            const cList = st.class_name.split(',').map(c => c.trim()).filter(Boolean);
            classBadgesModal = cList.map(c => `<span class="badge badge-info" style="margin-right: 4px; margin-bottom: 2px; display: inline-block;">Lớp ${c}</span>`).join('');
        }

        modalBody.innerHTML = `
            <!-- Modal Header Profile Bar with Export Buttons -->
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-bottom: 20px; border-bottom: 1.5px solid #e2e8f0; margin-bottom: 20px; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div class="staff-avatar" style="background: ${avatarColor}; width: 60px; height: 60px; font-size: 22px; border-radius: 50%;">
                        ${Utils.getInitials(st.name)}
                    </div>
                    <div>
                        <h2 style="margin: 0; font-size: 22px; color: #0f172a; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                            ${AuthModule.escapeHtml(st.name)}
                            <span class="badge ${statusBadge}">${st.status}</span>
                        </h2>
                        <div style="font-size: 13px; color: #475569; margin-top: 4px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-weight: 600;">
                            <span>Mã HS: <strong style="color: #0284c7; font-family: monospace; font-size: 14px;">${st.code}</strong></span>
                            ${st.english_name ? `<span>• Nickname: <strong style="color: #0f172a;">${AuthModule.escapeHtml(st.english_name)}</strong></span>` : ''}
                            <span>• Các lớp: ${classBadgesModal}</span>
                        </div>
                    </div>
                </div>

                <!-- Export Action Buttons -->
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="downloadStudentReport('${st.code}', 'pdf');" style="background: #2563eb; color: #ffffff; border: none; font-weight: 700;" title="In báo cáo học tập hoặc Lưu file PDF">
                        🖨️ In / File PDF
                    </button>
                    <button class="btn" style="border-color: #cbd5e1; color: #0284c7; background: #f0f9ff; font-weight: 700;" onclick="downloadStudentReport('${st.code}', 'word');" title="Tải xuống Báo cáo Word (.doc)">
                        📝 File Word
                    </button>
                    <button class="btn" style="border-color: #cbd5e1; color: #059669; background: #f0fdf4; font-weight: 700;" onclick="downloadStudentReport('${st.code}', 'excel');" title="Tải xuống Bảng tính Excel (.csv)">
                        📊 File Excel
                    </button>
                </div>
            </div>

            <!-- Profile Details Grid (2 Columns) -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 24px;">
                <!-- Box 1: Personal & Parent Info -->
                <div class="chart-card" style="padding: 16px; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 8px; font-weight: 800;">
                        👤 Thông Tin Cá Nhân & Phụ Huynh
                    </h4>
                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 13px; color: #0f172a;">
                        <div>🎂 <strong>Ngày sinh:</strong> ${st.dob || 'Chưa cập nhật'}</div>
                        <div>👨‍👩‍👧 <strong>Tên phụ huynh:</strong> ${AuthModule.escapeHtml(st.parent_name || 'Chưa cập nhật')}</div>
                        <div>📞 <strong>Số điện thoại:</strong> ${st.phone ? `<a href="tel:${st.phone}" style="color: #0284c7; font-weight: 700;">${st.phone}</a>` : 'Chưa cập nhật'}</div>
                        <div>🏠 <strong>Địa chỉ:</strong> ${AuthModule.escapeHtml(st.address || 'Chưa cập nhật')}</div>
                    </div>
                </div>

                <!-- Box 2: Class & Fee Info -->
                <div class="chart-card" style="padding: 16px; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 8px; font-weight: 800;">
                        🏫 Lớp Học & Học Phí Tái Phí
                    </h4>
                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 13px; color: #0f172a;">
                        <div>📚 <strong>Lớp đang học:</strong> ${classBadgesModal} (${st.schedule || 'N/A'})</div>
                        <div>👨‍🏫 <strong>Giáo viên (GV):</strong> ${AuthModule.escapeHtml(st.teacher || '—')}</div>
                        <div>👩‍💼 <strong>Quản lý (CM / TA):</strong> CM ${AuthModule.escapeHtml(st.cm || '—')} ${st.ta ? `• TA ${AuthModule.escapeHtml(st.ta)}` : ''}</div>
                        <div>💳 <strong>Tổng số buổi đăng ký (Khóa chính):</strong> ${st.total_sessions || 0} buổi (Còn <strong style="color: ${(st.remaining_sessions || 0) <= 0 ? '#dc2626' : '#059669'}; font-size: 14px;">${st.remaining_sessions || 0}</strong> buổi)</div>
                        <div>⏳ <strong>Dự kiến hết phí (Khóa chính):</strong> ${st.expiry_date === 'Đã hết phí' || (st.remaining_sessions || 0) <= 0 ? `<span class="badge badge-danger" style="font-size: 11.5px; padding: 3px 8px;">🔴 Đã hết phí (Hết 0 buổi)</span>` : `<strong style="color: #0284c7;">${st.expiry_date}</strong> ${st.expiry_month ? `(Tháng ${st.expiry_month})` : ''}`}</div>
                        ${st.fee_package_1 ? `<div style="margin-top: 4px; padding: 6px 10px; background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; color: #92400e; font-size: 12px; font-weight: 600;">📙 <strong>Gói bổ trợ / Ngắn hạn:</strong> ${AuthModule.escapeHtml(st.fee_package_1)}</div>` : ''}
                    </div>

                    <!-- ⚡ TÌNH TRẠNG HỌC & LỚP GẦN NHẤT -->
                    ${AuthModule.isAdmin() ? `
                        <div style="background: #f8fafc; padding: 10px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; margin-top: 12px;">
                            <div style="font-weight: 800; color: #0f172a; margin-bottom: 6px; font-size: 12px;">⚡ CẬP NHẬT TÌNH TRẠNG HỌC (ADMIN):</div>
                            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <select id="modal-change-status-select" class="filter-select" style="padding: 5px 10px; font-size: 12.5px; border-radius: 6px; background: #ffffff; color: #0f172a; font-weight: 800; border: 1px solid #cbd5e1;">
                                    <option value="Đang học" ${st.status === 'Đang học' ? 'selected' : ''}>🟢 Đang học</option>
                                    <option value="Bảo lưu" ${st.status === 'Bảo lưu' ? 'selected' : ''}>🟡 Bảo lưu</option>
                                    <option value="Đã nghỉ" ${st.status === 'Đã nghỉ' ? 'selected' : ''}>🔴 Đã nghỉ</option>
                                </select>
                                <button class="btn btn-sm btn-primary" onclick="StudentsModule.updateStudentStatus('${st.code}');" style="padding: 5px 12px; font-size: 12px; font-weight: 800; background: #2563eb; color: #ffffff; border: none;">
                                    💾 Cập nhật
                                </button>
                            </div>
                            ${st.last_class_name ? `<div style="margin-top: 6px; font-size: 11.5px; color: #475569;">🏫 <i>Lớp học gần nhất: <strong style="color: #0f172a;">${AuthModule.escapeHtml(st.last_class_name)}</strong></i></div>` : ''}
                        </div>
                    ` : `
                        <div style="background: #f8fafc; padding: 10px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; margin-top: 12px; font-size: 13px;">
                            <strong>Trạng thái học:</strong> <span class="badge ${statusBadge}">${st.status}</span>
                            ${st.last_class_name ? `<div style="margin-top: 4px; font-size: 11.5px; color: #475569;">🏫 <i>Lớp học gần nhất: <strong style="color: #0f172a;">${AuthModule.escapeHtml(st.last_class_name)}</strong></i></div>` : ''}
                        </div>
                    `}

                    <!-- 🏫 QUẢN LÝ DANH SÁCH LỚP HỌC (TAG LỚP) -->
                    <div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; margin-top: 10px;">
                        <div style="font-weight: 800; color: #0f172a; margin-bottom: 8px; font-size: 12px; display: flex; align-items: center; justify-content: space-between;">
                            <span>🏫 DANH SÁCH LỚP ĐANG HỌC:</span>
                        </div>
                        
                        <!-- Hiển thị các Tag Lớp Đang Học -->
                        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; align-items: center;">
                            ${st.class_name ? st.class_name.split(',').map(c => c.trim()).filter(Boolean).map(c => `
                                <span class="badge" style="background: #f0f9ff; color: #0284c7; border: 1.5px solid #bae6fd; padding: 6px 10px; font-size: 12px; border-radius: 6px; font-weight: 800; display: inline-flex; align-items: center; gap: 6px;">
                                    📚 Lớp ${AuthModule.escapeHtml(c)}
                                    ${AuthModule.isAdmin() ? `
                                        <a onclick="StudentsModule.removeClassFromStudent('${st.code}', '${AuthModule.escapeHtml(c)}');" style="color: #dc2626; font-weight: 900; cursor: pointer; padding: 0 3px; font-size: 13px;" title="Gỡ lớp ${AuthModule.escapeHtml(c)}">✕</a>
                                    ` : ''}
                                </span>
                            `).join('') : '<span style="color: #64748b; font-size: 12px; font-style: italic;">Chưa xếp lớp nào</span>'}
                        </div>

                        ${AuthModule.isAdmin() ? `
                            <!-- Thêm Lớp Học Mới (Admin Only) -->
                            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <select id="modal-add-class-select" class="filter-select" style="padding: 5px 10px; font-size: 12px; border-radius: 6px; background: #ffffff; color: #0f172a; font-weight: 800; border: 1px solid #cbd5e1;">
                                    <option value="">-- Chọn lớp để gán thêm --</option>
                                    ${this.availableClassesList ? this.availableClassesList.map(c => `<option value="${AuthModule.escapeHtml(c)}">Lớp ${AuthModule.escapeHtml(c)}</option>`).join('') : ''}
                                </select>
                                <button class="btn btn-sm" onclick="StudentsModule.addClassToStudent('${st.code}');" style="background: #059669; color: #ffffff; border: none; padding: 5px 12px; font-size: 12px; font-weight: 800; cursor: pointer; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;">
                                    ➕ Thêm Lớp
                                </button>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>

            <!-- SECTION 2: Class Manager History & Daily Checking Logs (Lịch sử Chăm sóc CM) -->
            <div class="chart-card" style="padding: 18px; margin-bottom: 24px; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px;">
                <h4 style="margin: 0 0 14px 0; color: #0f172a; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; font-weight: 800;">
                    <span>💚 LỊCH SỬ CHĂM SÓC & TƯƠNG TÁC PHỤ HUYNH (${cmNotes.length} lượt)</span>
                    <span style="font-size: 11.5px; color: #64748b; font-weight: 400;"><i>Sắp xếp: Mới nhất ở trên, cũ hơn bên dưới</i></span>
                </h4>

                <!-- Khung điền nhật ký chăm sóc thủ công -->
                <div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; margin-bottom: 14px;">
                    <div style="font-weight: 800; color: #059669; font-size: 12.5px; margin-bottom: 8px;">✍️ Ghi Nhận Nhật Ký Chăm Sóc / Lời Dặn Mới:</div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <input type="text" id="modal-care-log-staff" placeholder="CM / Phụ trách..." value="${AuthModule.escapeHtml(st.cm || '')}" style="width: 160px; padding: 6px 10px; border-radius: 6px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 12.5px; font-weight: 600;">
                        <input type="text" id="modal-care-log-note" placeholder="Nhập lời dặn, phản hồi PH, tình trạng học tập..." style="flex: 1; min-width: 250px; padding: 6px 10px; border-radius: 6px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 12.5px; font-weight: 600;" onkeyup="if(event.key==='Enter') StudentsModule.addCareLog('${st.code}');">
                        <button class="btn btn-sm" onclick="StudentsModule.addCareLog('${st.code}');" style="background: #059669; color: #ffffff; border: none; padding: 6px 16px; font-weight: 800; font-size: 12.5px; border-radius: 6px; cursor: pointer;">
                            ➕ Thêm Nhật Ký
                        </button>
                    </div>
                </div>
                <div style="max-height: 220px; overflow-y: auto; padding-right: 4px;">
                    ${cmCareRows}
                </div>
            </div>

            <!-- SECTION 3: Homework History (Nhật ký Bài Về Nhà - Phân nhóm theo lớp) -->
            <div class="chart-card" style="padding: 18px; margin-bottom: 24px; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px;">
                <h4 style="margin: 0 0 14px 0; color: #0f172a; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; font-weight: 800;">
                    <span>📋 NHẬT KÝ BÀI VỀ NHÀ - BTVN (${homework.length} lượt nộp)</span>
                    <span style="font-size: 11.5px; color: #64748b; font-weight: 400;"><i>Tự động phân tách riêng biệt theo từng lớp</i></span>
                </h4>
                <div style="max-height: 380px; overflow-y: auto; padding-right: 4px;">
                    ${hwGroupedMarkup}
                </div>
            </div>

            <!-- SECTION 4: AI Progress Assessment Card -->
            <div class="chart-card" style="padding: 20px; margin-bottom: 24px; border: 1.5px solid #cbd5e1; background: #ffffff; border-radius: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                    <h3 style="margin: 0; color: #0f172a; font-size: 16.5px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                        ✨ ĐÁNH GIÁ TỔNG QUAN QUÁ TRÌNH HỌC TẬP (AI SYNTHESIZED)
                    </h3>
                    <span class="badge badge-success" style="font-size: 12.5px; padding: 5px 12px; font-weight: 800;">Trình độ: ${aiAssessment.level_evaluation || 'Khá'}</span>
                </div>
                <p style="font-size: 14px; color: #0f172a; line-height: 1.6; margin-bottom: 14px; font-weight: 600;">
                    ${aiAssessment.summary || ''}
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; font-size: 13px;">
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px 14px; border-radius: 8px;">
                        <strong style="color: #15803d; display: block; margin-bottom: 6px; font-size: 13.5px;">🌟 Điểm mạnh nổi bật:</strong>
                        <ul style="margin: 0; padding-left: 18px; color: #0f172a; font-weight: 600;">
                            ${(aiAssessment.strengths || []).map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                    <div style="background: #fffbeb; border: 1px solid #fde68a; padding: 12px 14px; border-radius: 8px;">
                        <strong style="color: #b45309; display: block; margin-bottom: 6px; font-size: 13.5px;">🎯 Điểm cần lưu ý & cải thiện:</strong>
                        <ul style="margin: 0; padding-left: 18px; color: #0f172a; font-weight: 600;">
                            ${(aiAssessment.improvements || []).map(i => `<li>${i}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div style="margin-top: 14px; padding: 12px 16px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; font-size: 13px; color: #0284c7; font-weight: 700;">
                    💡 <strong>Khuyến nghị dành cho Phụ huynh:</strong> <span style="color: #0f172a; font-weight: 600;">${aiAssessment.recommendations || ''}</span>
                </div>
            </div>

            <!-- SECTION 5: CHI TIẾT ĐIỂM, LỊCH SỬ ĐIỂM THI & NHẬN XÉT GIÁO VIÊN TỪNG BÀI -->
            <div class="chart-card" style="padding: 20px; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px;">
                <h4 style="margin: 0 0 16px 0; color: #0f172a; border-bottom: 1.5px solid #f1f5f9; padding-bottom: 10px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; font-weight: 800;">
                    <span>💯 CHI TIẾT ĐIỂM THI, LỊCH SỬ ĐIỂM & NHẬN XÉT GIÁO VIÊN TỪNG BÀI</span>
                    <span class="badge badge-info" style="font-weight: 800; font-size: 12px;">Tổng ${grades.length} bài test</span>
                </h4>
                <div style="max-height: 450px; overflow-y: auto; padding-right: 6px;">
                    ${gradeGroupedMarkup}
                </div>
            </div>
        `;
    },

    /**
     * Close Student Modal.
     */
    closeStudentModal() {
        const modal = document.getElementById('student-modal');
        if (modal) modal.classList.remove('active');
    },

    /**
     * Update Student Status (Đang học, Bảo lưu, Đã nghỉ) via API.
     */
    async updateStudentStatus(studentCode) {
        const statusSelect = document.getElementById('modal-change-status-select');
        if (!statusSelect) return;
        const newStatus = statusSelect.value;

        try {
            const res = await API.post(`/students/${encodeURIComponent(studentCode)}/status`, { status: newStatus });
            if (res.success) {
                App.showToast(res.message, 'success');
                // Reload current student profile modal
                this.openStudentProfile(studentCode);
                // Reload background student list
                this.loadData();
            } else {
                App.showToast(res.error || 'Cập nhật tình trạng học thất bại', 'error');
            }
        } catch (err) {
            App.showToast('Lỗi cập nhật: ' + err.message, 'error');
        }
    },

    /**
     * Add a new class tag to student (Dành cho học sinh học 2+ lớp).
     */
    async addClassToStudent(studentCode) {
        const classSelect = document.getElementById('modal-add-class-select');
        if (!classSelect) return;
        const classToAdd = classSelect.value;
        if (!classToAdd) {
            App.showToast('Vui lòng chọn lớp học muốn gán thêm', 'warning');
            return;
        }

        try {
            const res = await API.post(`/students/${encodeURIComponent(studentCode)}/add-class`, { class_name: classToAdd });
            if (res.success) {
                App.showToast(res.message, 'success');
                this.openStudentProfile(studentCode);
                this.loadData();
            } else {
                App.showToast(res.error || 'Thêm lớp thất bại', 'error');
            }
        } catch (err) {
            App.showToast('Lỗi thêm lớp: ' + err.message, 'error');
        }
    },

    /**
     * Remove a class tag from student (Gỡ 1 lớp khỏi danh sách lớp của học sinh).
     */
    async removeClassFromStudent(studentCode, className) {
        if (!confirm(`Bạn có chắc chắn muốn gỡ Lớp ${className} khỏi học sinh này?`)) return;

        try {
            const res = await API.post(`/students/${encodeURIComponent(studentCode)}/remove-class`, { class_name: className });
            if (res.success) {
                App.showToast(res.message, 'success');
                this.openStudentProfile(studentCode);
                this.loadData();
            } else {
                App.showToast(res.error || 'Gỡ lớp thất bại', 'error');
            }
        } catch (err) {
            App.showToast('Lỗi gỡ lớp: ' + err.message, 'error');
        }
    },

    /**
     * Add manual Parent Care Log (Thêm nhật ký tương tác chăm sóc).
     */
    async addCareLog(studentCode) {
        const noteInput = document.getElementById('modal-care-log-note');
        const staffInput = document.getElementById('modal-care-log-staff');
        if (!noteInput) return;

        const note = noteInput.value.trim();
        const staffName = staffInput ? staffInput.value.trim() : '';

        if (!note) {
            App.showToast('Vui lòng nhập nội dung nhật ký chăm sóc', 'warning');
            return;
        }

        try {
            const res = await API.post(`/students/${encodeURIComponent(studentCode)}/care-log`, {
                note: note,
                staff_name: staffName
            });

            if (res.success) {
                App.showToast(res.message, 'success');
                this.openStudentProfile(studentCode);
            } else {
                App.showToast(res.error || 'Thêm nhật ký chăm sóc thất bại', 'error');
            }
        } catch (err) {
            App.showToast('Lỗi thêm nhật ký: ' + err.message, 'error');
        }
    },

    /**
     * Open Modal Add New Student.
     */
    openAddStudentModal() {
        let addModal = document.getElementById('cm-add-student-modal');
        if (!addModal) {
            addModal = document.createElement('div');
            addModal.id = 'cm-add-student-modal';
            addModal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.75); display: none; align-items: center; justify-content: center; z-index: 10000; padding: 20px; backdrop-filter: blur(4px);';
            document.body.appendChild(addModal);
        }

        const classOptions = (this.availableClassesList || []).map(c => `<option value="${AuthModule.escapeHtml(c)}">Lớp ${AuthModule.escapeHtml(c)}</option>`).join('');

        addModal.innerHTML = `
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 16px; width: 100%; max-width: 620px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.15);">
                <div style="padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between;">
                    <h3 style="margin: 0; font-size: 16px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        ➕ THÊM HỌC SINH MỚI THỦ CÔNG
                    </h3>
                    <button onclick="StudentsModule.closeAddStudentModal();" style="background: none; border: none; color: #64748b; font-size: 20px; cursor: pointer; padding: 4px 8px;">✕</button>
                </div>

                <div style="padding: 20px; display: flex; flex-direction: column; gap: 14px; max-height: 75vh; overflow-y: auto; font-size: 13px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Mã Học Sinh (Để trống tự sinh EVIxxx):</label>
                            <input type="text" id="add-st-code" placeholder="Tự sinh hoặc gõ EVI..." style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700;">
                        </div>
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Họ và Tên Học Sinh (*):</label>
                            <input type="text" id="add-st-name" placeholder="Nhập họ và tên đầy đủ..." style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700;">
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Tên Tiếng Anh / Nickname:</label>
                            <input type="text" id="add-st-en-name" placeholder="Ví dụ: Alex, Jenny..." style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 600;">
                        </div>
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Ngày Sinh:</label>
                            <input type="text" id="add-st-dob" placeholder="dd/mm/yyyy..." style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 600;">
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Tên Phụ Huynh:</label>
                            <input type="text" id="add-st-parent" placeholder="Bố/Mẹ..." style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 600;">
                        </div>
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Số Điện Thoại PH (*):</label>
                            <input type="text" id="add-st-phone" placeholder="SĐT liên hệ..." style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 600;">
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Lớp Học Đăng Ký:</label>
                            <select id="add-st-class" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700;">
                                <option value="">-- Chưa xếp lớp --</option>
                                ${classOptions}
                            </select>
                        </div>
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Tình Trạng Học:</label>
                            <select id="add-st-status" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700;">
                                <option value="Đang học">🟢 Đang học</option>
                                <option value="Bảo lưu">🟡 Bảo lưu</option>
                                <option value="Đã nghỉ">🔴 Đã nghỉ</option>
                            </select>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Tổng Số Buổi Đăng Ký:</label>
                            <input type="number" id="add-st-tot-sess" value="48" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700;">
                        </div>
                        <div>
                            <label style="font-weight: 800; color: #0f172a; display: block; margin-bottom: 4px;">Số Buổi Còn Lại:</label>
                            <input type="number" id="add-st-rem-sess" value="48" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700;">
                        </div>
                    </div>
                </div>

                <div style="padding: 14px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: flex-end; gap: 10px;">
                    <button class="btn" onclick="StudentsModule.closeAddStudentModal();" style="padding: 8px 18px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #334155; font-weight: 700; border-radius: 8px;">
                        Hủy bỏ
                    </button>
                    <button class="btn btn-primary" onclick="StudentsModule.submitAddStudent();" style="padding: 8px 22px; font-weight: 800; background: #2563eb; color: #ffffff; border: none; border-radius: 8px; box-shadow: 0 2px 6px rgba(37,99,235,0.3);">
                        💾 Lưu Học Sinh Mới
                    </button>
                </div>
            </div>
        `;
        addModal.style.display = 'flex';
    },

    closeAddStudentModal() {
        const addModal = document.getElementById('cm-add-student-modal');
        if (addModal) addModal.style.display = 'none';
    },

    /**
     * Submit Add New Student.
     */
    async submitAddStudent() {
        const name = document.getElementById('add-st-name')?.value.trim() || '';
        if (!name) {
            App.showToast('Vui lòng nhập Họ và Tên học sinh', 'warning');
            return;
        }

        const payload = {
            code: document.getElementById('add-st-code')?.value.trim() || '',
            name: name,
            english_name: document.getElementById('add-st-en-name')?.value.trim() || '',
            dob: document.getElementById('add-st-dob')?.value.trim() || '',
            parent_name: document.getElementById('add-st-parent')?.value.trim() || '',
            phone: document.getElementById('add-st-phone')?.value.trim() || '',
            class_name: document.getElementById('add-st-class')?.value || '',
            status: document.getElementById('add-st-status')?.value || 'Đang học',
            total_sessions: parseInt(document.getElementById('add-st-tot-sess')?.value || '0'),
            remaining_sessions: parseInt(document.getElementById('add-st-rem-sess')?.value || '0')
        };

        try {
            const res = await API.post('/students/add', payload);
            if (res.success) {
                App.showToast(res.message, 'success');
                this.closeAddStudentModal();
                this.loadData();
            } else {
                App.showToast(res.error || 'Thêm học sinh thất bại', 'error');
            }
        } catch (err) {
            App.showToast('Lỗi hệ thống: ' + err.message, 'error');
        }
    }
};

/**
 * Global Helper Tải xuống báo cáo học tập không bị treo tab hoặc bị popup blocker.
 */
window.downloadStudentReport = function(studentCode, format) {
    const url = `/api/students/${studentCode}/export?format=${format}`;
    if (format === 'pdf') {
        window.open(url, '_blank');
    } else {
        const link = document.createElement('a');
        link.href = url;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        setTimeout(() => {
            if (document.body.contains(link)) {
                document.body.removeChild(link);
            }
        }, 1000);
    }
};
