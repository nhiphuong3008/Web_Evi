/**
 * EVI Dashboard - Class Manager (CM) Portal
 * Kiểm tra lớp học, Điểm danh & Nhập điểm bài thi.
 */

const CMPortalModule = {
    classes: [],
    selectedClassName: '',
    currentTab: 'classes', // 'classes', 'attendance', 'grades'
    studentsInClass: [],
    attendanceRecords: {},
    gradeRecords: {},

    gradeMode: 'all', // 'all', 'sun', 'moon'

    async init(defaultTab = 'attendance') {
        const cmName = AuthModule.getCMStaffName();
        if (defaultTab === 'grades_sun') {
            this.currentTab = 'grades';
            this.gradeMode = 'sun';
        } else if (defaultTab === 'grades_moon') {
            this.currentTab = 'grades';
            this.gradeMode = 'moon';
        } else {
            this.currentTab = defaultTab;
            this.gradeMode = 'all';
        }

        await this.loadCMClasses(cmName);
        if (this.selectedClassName) {
            await this.loadRosterForClass(this.selectedClassName);
        }
        this.renderPortal();
    },

    async loadCMClasses(cmName = '') {
        try {
            const res = await API.getCMClasses(cmName);
            if (res.success) {
                let rawClasses = res.data || [];
                if (this.gradeMode === 'sun') {
                    rawClasses = rawClasses.filter(c => !(c.class_name || '').toLowerCase().startsWith('moon'));
                } else if (this.gradeMode === 'moon') {
                    rawClasses = rawClasses.filter(c => (c.class_name || '').toLowerCase().startsWith('moon'));
                }

                this.classes = rawClasses;
                if (this.classes.length > 0) {
                    const exists = this.classes.some(c => c.class_name === this.selectedClassName);
                    if (!exists) {
                        this.selectedClassName = this.classes[0].class_name;
                    }
                } else {
                    this.selectedClassName = '';
                }
            }
        } catch (e) {
            console.error('Error loading CM classes:', e);
        }
    },

    async reloadClassesSilently() {
        const cmName = AuthModule.getCMStaffName();
        await this.loadCMClasses(cmName);
        const dropdown = document.getElementById('cm-main-class-dropdown');
        if (dropdown) {
            const classDropdownOptionsHtml = this.classes.map(c => {
                const selected = c.class_name === this.selectedClassName ? 'selected' : '';
                return `<option value="${AuthModule.escapeHtml(c.class_name)}" ${selected}>🏫 ${AuthModule.escapeHtml(c.class_name)} (${c.student_count || 0} HS)</option>`;
            }).join('');
            dropdown.innerHTML = classDropdownOptionsHtml.length > 0 ? classDropdownOptionsHtml : '<option value="">Không tìm thấy lớp học phụ trách</option>';
        }
    },

    async selectClass(className) {
        this.selectedClassName = className;
        await this.loadRosterForClass(className);
        this.renderPortal();
    },

    async switchTab(tabName) {
        this.currentTab = tabName;
        if (this.selectedClassName) {
            await this.loadRosterForClass(this.selectedClassName);
        }
        this.renderPortal();
    },

    async loadRosterForClass(className) {
        if (!className) return;
        try {
            const res = await API.get('/students', { class_name: className, _t: Date.now() });
            if (res.success) {
                this.studentsInClass = res.data || [];
            }
        } catch (e) {
            console.error('Error loading roster:', e);
        }
    },

    renderPortal() {
        const container = document.getElementById('page-content');
        if (!container) return;

        const cmUser = AuthModule.getUser();
        const cmTitle = cmUser 
            ? (cmUser.role === 'admin' ? 'Tất cả các lớp (Quyền Admin)' : `CM ${cmUser.cm_staff_name || cmUser.full_name}`)
            : 'Khách (Chưa đăng nhập)';

        // Class Selector Dropdown Options
        const classDropdownOptionsHtml = this.classes.map(c => {
            const selected = c.class_name === this.selectedClassName ? 'selected' : '';
            return `<option value="${AuthModule.escapeHtml(c.class_name)}" ${selected}>🏫 ${AuthModule.escapeHtml(c.class_name)} (${c.student_count || 0} HS)</option>`;
        }).join('');

        container.innerHTML = `
            <div class="cm-portal-header" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; border-bottom: 1px dashed var(--border-color); padding-bottom: 14px;">
                    <div>
                        <h2 style="margin: 0; font-size: 20px; color: var(--text-heading);">📋 Cổng Quản Lý CM & Điểm Danh</h2>
                        <p style="margin: 4px 0 0; font-size: 13px; color: var(--text-muted);">
                            Phụ trách: <strong style="color: var(--accent-color);">${cmTitle}</strong>
                        </p>
                    </div>

                    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                        ${this.currentTab === 'attendance' ? `
                            <button class="btn" onclick="CMPortalModule.exportClassReport();" style="background: rgba(14,165,233,0.25); color: #38bdf8; border: 1.5px solid #38bdf8; padding: 9px 20px; font-weight: 800; font-size: 13.5px; cursor: pointer; border-radius: 10px; box-shadow: 0 4px 14px rgba(14,165,233,0.3); display: flex; align-items: center; gap: 8px;" title="Xuất báo cáo tổng hợp điểm danh & điểm BTVN của cả lớp">
                                📊 Xuất Báo Cáo (Điểm Danh & BTVN)
                            </button>
                        ` : ''}

                        ${!AuthModule.isLoggedIn() ? `
                            <button class="btn btn-primary" onclick="AuthModule.showLoginModal();" style="padding: 8px 16px;">
                                🔐 Đăng Nhập Để Lưu Điểm Danh / Điểm Thi
                            </button>
                        ` : ''}
                    </div>
                </div>

                <!-- Class Selector Dropdown -->
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px; background: rgba(30,41,59,0.6); padding: 10px 16px; border-radius: 10px; border: 1px solid var(--border-color); flex-wrap: wrap;">
                    <label style="font-size: 13.5px; font-weight: 700; color: #a5b4fc; display: flex; align-items: center; gap: 6px; margin: 0;">
                        🏫 Chọn Lớp Học Phụ Trách:
                    </label>
                    <select id="cm-main-class-dropdown" onchange="CMPortalModule.selectClass(this.value);" style="padding: 7px 14px; border-radius: 8px; border: 1.5px solid #818cf8; background: var(--bg-card); color: var(--text-heading); font-weight: 700; font-size: 13.5px; cursor: pointer; min-width: 240px;">
                        ${classDropdownOptionsHtml.length > 0 ? classDropdownOptionsHtml : '<option value="">Không tìm thấy lớp học phụ trách</option>'}
                    </select>

                    ${AuthModule.isAdmin() ? `
                        <button class="btn btn-sm" onclick="Dashboard.openManageClassesModal();" style="padding: 7px 16px; background: #2563eb; color: #ffffff; font-weight: 800; font-size: 13px; border-radius: 8px; border: none; cursor: pointer; box-shadow: 0 2px 6px rgba(37,99,235,0.3); display: flex; align-items: center; gap: 6px;" title="Thêm Lớp Học Mới Hoặc Quản Lý Lớp (Admin Only)">
                            ➕ Thêm Lớp Mới (Admin)
                        </button>
                    ` : ''}
                </div>

            </div>

            <!-- Tab Content Container -->
            <div id="cm-tab-content"></div>
        `;

        if (this.currentTab === 'classes') {
            this.renderClassRosterTab();
        } else if (this.currentTab === 'attendance') {
            this.renderAttendanceTab();
        } else if (this.currentTab === 'grades') {
            this.renderGradeEntryTab();
        }
    },

    async renderClassRosterTab() {
        const tabContent = document.getElementById('cm-tab-content');
        if (!tabContent) return;

        if (this.selectedClassName) {
            await this.loadRosterForClass(this.selectedClassName);
        }

        const selectedClassObj = this.classes.find(c => c.class_name === this.selectedClassName) || {};

        const rows = this.studentsInClass.map((s, idx) => {
            const rem = s.remaining_sessions || 0;
            let feeBadge = `<span class="badge" style="background: rgba(16,185,129,0.15); color: #10b981;">Còn ${rem} buổi</span>`;
            if (rem <= 5 && rem > 0) {
                feeBadge = `<span class="badge" style="background: rgba(245,158,11,0.15); color: #f59e0b;">Sắp hết (${rem} buổi)</span>`;
            } else if (rem <= 0) {
                feeBadge = `<span class="badge" style="background: rgba(239,68,68,0.15); color: #ef4444;">Hết phí</span>`;
            }

            return `
                <tr>
                    <td style="color: var(--text-muted);">${idx + 1}</td>
                    <td style="font-weight: 600; color: var(--accent-color);">${AuthModule.escapeHtml(s.code)}</td>
                    <td>
                        <div style="font-weight: 600; color: var(--text-heading);">${AuthModule.escapeHtml(s.name)}</div>
                        <div style="font-size: 12px; color: var(--text-muted);">${AuthModule.escapeHtml(s.english_name || '')}</div>
                    </td>
                    <td>${AuthModule.escapeHtml(s.parent_name || '—')}</td>
                    <td>
                        <a href="tel:${AuthModule.escapeHtml(s.phone)}" style="color: #60a5fa; text-decoration: none;">
                            📞 ${AuthModule.escapeHtml(s.phone || '—')}
                        </a>
                    </td>
                    <td>${feeBadge}</td>
                    <td>
                        <button class="btn btn-sm" onclick="StudentsModule.openStudentModal('${s.code}');" style="padding: 4px 8px; font-size: 12px; border: 1px solid var(--border-color);">
                            📋 Xem Hồ Sơ
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        tabContent.innerHTML = `
            <div class="card" style="margin-bottom: 20px; padding: 16px; background: rgba(30,41,59,0.5); border: 1px solid var(--border-color);">
                <div style="display: flex; gap: 20px; flex-wrap: wrap; font-size: 13px;">
                    <div>🏫 <b>Lớp:</b> ${AuthModule.escapeHtml(this.selectedClassName)}</div>
                    <div>👨‍🏫 <b>Giáo viên:</b> ${AuthModule.escapeHtml(selectedClassObj.teacher || '—')}</div>
                    <div>🗓️ <b>Lịch học:</b> ${AuthModule.escapeHtml(selectedClassObj.schedule || '—')}</div>
                    <div>🚪 <b>Phòng:</b> ${AuthModule.escapeHtml(selectedClassObj.room || '—')}</div>
                    <div>👥 <b>Sĩ số:</b> ${this.studentsInClass.length} học sinh</div>
                </div>
            </div>

            <div class="card" style="padding: 0; overflow: hidden; border-radius: 12px;">
                <div class="table-responsive">
                    <table class="data-table" style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: rgba(30,41,59,0.8); text-align: left;">
                                <th style="padding: 12px 16px; width: 40px;">STT</th>
                                <th style="padding: 12px 16px;">Mã HS</th>
                                <th style="padding: 12px 16px;">Họ Và Tên</th>
                                <th style="padding: 12px 16px;">Phụ Huynh</th>
                                <th style="padding: 12px 16px;">SĐT Liên Hệ</th>
                                <th style="padding: 12px 16px;">Số Buổi Còn Lại</th>
                                <th style="padding: 12px 16px; width: 110px;">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.length > 0 ? rows : `
                                <tr>
                                    <td colspan="7" style="text-align: center; padding: 40px; color: var(--text-muted);">
                                        Chưa có thông tin học sinh cho lớp ${AuthModule.escapeHtml(this.selectedClassName)}.
                                    </td>
                                </tr>
                            `}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    allSystemStudents: [],
    addedGuestStudents: [],

    async loadAllSystemStudents() {
        if (this.allSystemStudents && this.allSystemStudents.length > 0) return;
        try {
            const res = await API.get('/students', { search: '' });
            if (res.success) {
                this.allSystemStudents = res.data || [];
            }
        } catch (e) {
            console.error("Error loading system students:", e);
        }
    },

    async renderAttendanceTab() {
        const tabContent = document.getElementById('cm-tab-content');
        if (!tabContent) return;

        const todayStr = new Date().toISOString().split('T')[0];
        const selectedDate = this.selectedAttendanceDate || todayStr;

        await this.loadAllSystemStudents();

        // Ensure roster for selected class is ALWAYS loaded from DB
        if (this.classes && this.classes.length > 0) {
            if (!this.selectedClassName) {
                this.selectedClassName = this.classes[0].class_name;
            }
            await this.loadRosterForClass(this.selectedClassName);
        }

        // Build Class Selector Dropdown Options
        let classSelectOptionsHtml = '';
        if (this.classes && this.classes.length > 0) {
            classSelectOptionsHtml = this.classes.map(c => {
                const isSel = c.class_name === this.selectedClassName ? 'selected' : '';
                return `<option value="${AuthModule.escapeHtml(c.class_name)}" ${isSel}>🏫 ${AuthModule.escapeHtml(c.class_name)} (${c.student_count || 0} HS)</option>`;
            }).join('');
        } else {
            classSelectOptionsHtml = `<option value="">-- Không có lớp --</option>`;
        }

        tabContent.innerHTML = `
            <div class="card" style="margin-bottom: 16px; padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <label style="font-size: 13px; font-weight: 700; color: var(--text-heading);">📅 Chọn Ngày Điểm Danh:</label>
                            <input type="date" id="attendance-date-picker" class="form-control" value="${selectedDate}" onchange="CMPortalModule.handleAttendanceDateChange(this.value);" style="padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main); font-weight: 600;">
                        </div>

                        <div style="display: flex; align-items: center; gap: 8px; background: rgba(129,140,248,0.08); padding: 4px 10px; border-radius: 8px; border: 1px dashed rgba(129,140,248,0.4);">
                            <label style="font-size: 13px; font-weight: 700; color: #a5b4fc;">📝 Tổng Số Câu BVN:</label>
                            <input type="number" id="global-hw-total-questions" class="form-control" placeholder="Mấy câu..." oninput="CMPortalModule.onGlobalHwTotalChange(this.value);" style="width: 70px; padding: 5px 8px; border-radius: 6px; border: 1.5px solid #818cf8; background: var(--bg-card); color: #818cf8; font-weight: 800; font-size: 13px; text-align: center;" title="Nhập tổng số câu bài tập về nhà chung cho cả lớp">
                        </div>
                        
                        <button class="btn btn-sm" onclick="CMPortalModule.markAllAttendance('Có mặt');" style="background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.3); font-weight: 600; padding: 6px 12px;">
                            🟢 Tất cả Có mặt
                        </button>
                    </div>

                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <button class="btn btn-primary" onclick="CMPortalModule.saveAttendance();" style="padding: 9px 20px; font-weight: 700; font-size: 13.5px; box-shadow: 0 4px 12px rgba(99,102,241,0.3);">
                            💾 Lưu Kết Quả Điểm Danh
                        </button>
                    </div>
                </div>

                <!-- Realtime Attendance Summary Bar -->
                <div id="attendance-summary-bar" style="margin-top: 14px; padding-top: 12px; border-top: 1px dashed var(--border-color); display: flex; gap: 12px; flex-wrap: wrap; font-size: 12.5px; font-weight: 600;">
                    <!-- Filled dynamically -->
                </div>
            </div>

            <div class="card" style="padding: 0; overflow: hidden; border-radius: 12px; border: 1px solid var(--border-color);">
                <div class="table-responsive">
                    <table class="data-table" style="width: 100%; border-collapse: collapse; font-size: 12.5px; table-layout: fixed;">
                        <thead>
                            <tr style="background: rgba(30,41,59,0.95); text-align: left; color: var(--text-heading);">
                                <th style="padding: 10px 8px; width: 38px; text-align: center;">STT</th>
                                <th style="padding: 10px 8px; width: 75px;">Mã HS</th>
                                <th style="padding: 10px 8px; width: 145px;">Họ Và Tên</th>
                                <th style="padding: 10px 8px; width: 130px;">Điểm Danh</th>
                                <th style="padding: 10px 8px; width: 125px;">Ghi Chú</th>
                                <th style="padding: 10px 8px; width: 155px;">📝 BVN (Số Câu Đúng)</th>
                                <th style="padding: 10px 8px; width: 135px;">Tình Trạng BVN</th>
                                <th style="padding: 10px 8px;">Nhận Xét Bài Về Nhà</th>
                                <th style="padding: 10px 8px; width: 75px; text-align: center;">Loại</th>
                            </tr>
                        </thead>
                        <tbody id="attendance-table-body">
                            <!-- Filled dynamically -->
                        </tbody>
                    </table>
                </div>

                <!-- Add Guest Student Section with Autocomplete Search -->
                <div style="padding: 14px 16px; background: #f8fafc; border-top: 1.5px solid #cbd5e1; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; border-radius: 0 0 12px 12px;">
                    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; flex: 1;">
                        <span style="font-size: 13px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 6px;">
                            ➕ Bổ sung học sinh từ lớp khác:
                        </span>
                        
                        <div style="position: relative; flex: 1; max-width: 420px; min-width: 280px;">
                            <input type="text" 
                                   id="guest-student-search-input" 
                                   placeholder="🔍 Gõ tên hoặc Mã HS (VD: Đào Đức Nhật Minh hoặc EVI166)..." 
                                   style="width: 100%; padding: 8px 14px; font-size: 13px; font-weight: 700; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; outline: none; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"
                                   oninput="CMPortalModule.filterGuestSuggestions(this.value);"
                                   onfocus="CMPortalModule.filterGuestSuggestions(this.value);"
                                   onblur="setTimeout(() => CMPortalModule.hideGuestSuggestions(), 250);"
                                   onkeyup="if(event.key==='Enter') CMPortalModule.addGuestStudent();"
                                   autocomplete="off">
                            <input type="hidden" id="guest-student-selected-code" value="">

                            <div id="guest-student-suggestions-list" 
                                 style="display: none; position: absolute; bottom: 100%; left: 0; right: 0; max-height: 260px; overflow-y: auto; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 10px; box-shadow: 0 -10px 30px rgba(0,0,0,0.18); z-index: 9999; margin-bottom: 6px;">
                            </div>
                        </div>

                        <button class="btn btn-sm btn-primary" onclick="CMPortalModule.addGuestStudent();" style="padding: 8px 18px; font-size: 12.5px; font-weight: 800; background: #059669; color: #ffffff; border: none; border-radius: 8px; box-shadow: 0 2px 6px rgba(5,150,105,0.25); cursor: pointer;">
                            ➕ Thêm Học Sinh Lớp Khác
                        </button>
                    </div>
                    <small style="color: #64748b; font-size: 12px; font-weight: 600;">💡 Nhập tên/mã để tự động gợi ý, không cần tìm thủ công</small>
                </div>
            </div>
        `;

        await this.loadAttendanceRecords(this.selectedClassName, selectedDate);
    },

    async loadAttendanceRecords(className, dateStr) {
        this.selectedAttendanceDate = dateStr;
        const tbody = document.getElementById('attendance-table-body');
        if (!tbody) return;

        let existingMap = {};
        this.addedGuestStudents = [];

        try {
            const res = await API.getAttendance(className, dateStr);
            if (res.success && res.data) {
                res.data.forEach(r => {
                    existingMap[r.student_name] = r;
                    // If stored record was guest student, add to addedGuestStudents if not in current class
                    if (r.is_guest) {
                        const existsInRoster = this.studentsInClass.some(s => s.name === r.student_name || s.code === r.student_code);
                        if (!existsInRoster) {
                            const sysMatch = this.allSystemStudents.find(st => st.code === r.student_code || st.name === r.student_name);
                            this.addedGuestStudents.push({
                                id: sysMatch ? sysMatch.id : ('guest_' + Math.random().toString(36).substr(2, 5)),
                                code: r.student_code || (sysMatch ? sysMatch.code : 'EVI_GUEST'),
                                name: r.student_name,
                                english_name: sysMatch ? sysMatch.english_name : '',
                                original_class: sysMatch ? sysMatch.class_name : 'Lớp khác',
                                status: r.status,
                                note: r.note,
                                is_guest: true
                            });
                        }
                    }
                });
            }
        } catch (e) {
            console.error('Error fetching attendance:', e);
        }

        this.renderAttendanceTableBody(existingMap);
        this.populateGuestSelectOptions();
    },

    renderAttendanceTableBody(existingMap = {}) {
        const tbody = document.getElementById('attendance-table-body');
        if (!tbody) return;

        let rowsHtml = '';
        let stt = 1;
        let detectedGlobalTot = '';

        // 1. Official Class Students
        this.studentsInClass.forEach(s => {
            const existing = existingMap[s.name] || {};
            if (!detectedGlobalTot && existing.hw_total_questions) {
                detectedGlobalTot = existing.hw_total_questions;
            }
            rowsHtml += this.buildAttendanceRowHtml(stt++, s, existing, false);
        });

        // 2. Added Guest Students from Other Classes
        this.addedGuestStudents.forEach(g => {
            const existing = existingMap[g.name] || {};
            if (!detectedGlobalTot && existing.hw_total_questions) {
                detectedGlobalTot = existing.hw_total_questions;
            }
            rowsHtml += this.buildAttendanceRowHtml(stt++, g, existing, true);
        });

        tbody.innerHTML = rowsHtml.length > 0 ? rowsHtml : `
            <tr>
                <td colspan="9" style="text-align: center; padding: 40px; color: var(--text-muted);">
                    Không có học sinh nào trong lớp. Vui lòng chọn lớp khác hoặc bổ sung học sinh.
                </td>
            </tr>
        `;

        // Set global total input value if detected from records
        const globalTotInput = document.getElementById('global-hw-total-questions');
        if (globalTotInput && detectedGlobalTot) {
            globalTotInput.value = detectedGlobalTot;
        }

        this.updateAttendanceStats();
    },

    buildAttendanceRowHtml(sttIndex, studentObj, existingObj = {}, isGuest = false) {
        const rowId = isGuest ? `guest_${studentObj.code}` : studentObj.id;
        const currentStatus = existingObj.status || (isGuest ? (studentObj.status || 'Có mặt') : 'Có mặt');
        const currentNote = existingObj.note || (isGuest ? (studentObj.note || '') : '');

        const hwTot = (existingObj.hw_total_questions !== undefined && existingObj.hw_total_questions !== null) ? existingObj.hw_total_questions : '';
        const hwCorr = existingObj.hw_correct_answers !== undefined && existingObj.hw_correct_answers !== null ? existingObj.hw_correct_answers : '';
        const hwStatus = existingObj.hw_submission_status || 'Nộp đúng giờ';
        const hwComment = existingObj.hw_comment || '';

        // Pre-calculate score badge if correct answers and total questions exist
        let scoreBadgeHtml = `<span id="hw_badge_${rowId}" style="display: flex; align-items: center;"><span style="color: var(--text-muted); font-size: 11.5px;">(Chưa nhập)</span></span>`;
        if (hwCorr !== '' && hwTot !== '' && !isNaN(parseFloat(hwCorr)) && !isNaN(parseFloat(hwTot)) && parseFloat(hwTot) > 0) {
            const sc = Math.round((parseFloat(hwCorr) / parseFloat(hwTot)) * 100) / 10;
            let color = '#10b981';
            if (sc < 5.0) color = '#ef4444';
            else if (sc < 7.0) color = '#f59e0b';
            scoreBadgeHtml = `<span id="hw_badge_${rowId}" style="display: flex; align-items: center;"><span style="color: ${color}; font-weight: 700; background: rgba(15,23,42,0.8); padding: 2px 6px; border-radius: 4px; border: 1px solid ${color}; font-size: 11.5px;">📊 ${sc.toFixed(1)} / 10đ</span></span>`;
        }

        const guestBadge = isGuest 
            ? `<span class="badge" style="background: rgba(245,158,11,0.2); color: #f59e0b; font-size: 11px;">Học ghép (${AuthModule.escapeHtml(studentObj.original_class || 'Lớp khác')})</span>`
            : `<span class="badge badge-secondary" style="font-size: 11px;">Chính thức</span>`;

        const removeBtnHtml = isGuest
            ? `<button class="btn btn-sm" onclick="CMPortalModule.removeGuestStudent('${studentObj.code}');" style="padding: 2px 6px; font-size: 11px; background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.4);" title="Xóa khỏi danh sách điểm danh">🗑️</button>`
            : `—`;

        return `
            <tr id="att_row_${rowId}" style="${isGuest ? 'background: rgba(245,158,11,0.06);' : ''}">
                <td style="padding: 6px 4px; text-align: center; color: var(--text-muted); font-weight: 600;">${sttIndex}</td>
                <td style="padding: 6px 6px; font-weight: 700; color: var(--accent-color); font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${AuthModule.escapeHtml(studentObj.code || '—')}</td>
                <td style="padding: 6px 6px;">
                    <div style="font-weight: 700; color: var(--text-heading); line-height: 1.2; font-size: 12px;">${AuthModule.escapeHtml(studentObj.name)}</div>
                    ${studentObj.english_name ? `<div style="font-size: 10.5px; color: var(--text-muted); line-height: 1.1;">${AuthModule.escapeHtml(studentObj.english_name)}</div>` : ''}
                </td>
                <td style="padding: 6px 4px;">
                    <select id="att_select_${rowId}" class="form-control att-status-select" onchange="CMPortalModule.onStatusSelectChange('${rowId}');" style="width: 100%; padding: 4px 6px; border-radius: 6px; border: 1.5px solid var(--border-color); background: var(--bg-card); font-weight: 700; font-size: 11.5px; cursor: pointer;">
                        <option value="Có mặt" ${currentStatus === 'Có mặt' ? 'selected' : ''} style="color: #10b981; font-weight: 700;">🟢 Có mặt</option>
                        <option value="Vắng có phép" ${currentStatus === 'Vắng có phép' ? 'selected' : ''} style="color: #f97316; font-weight: 700;">🟠 Vắng có phép</option>
                        <option value="Vắng không phép" ${currentStatus === 'Vắng không phép' || (currentStatus.includes('Vắng') && !currentStatus.includes('phép')) ? 'selected' : ''} style="color: #ef4444; font-weight: 700;">🔴 Vắng không phép</option>
                        <option value="Lý do khác" ${currentStatus === 'Lý do khác' ? 'selected' : ''} style="color: #3b82f6; font-weight: 700;">🔵 Lý do khác</option>
                    </select>
                </td>
                <td style="padding: 6px 4px;">
                    <input type="text" id="note_${rowId}" value="${AuthModule.escapeHtml(currentNote)}" placeholder="Ghi chú..." style="width: 100%; padding: 4px 6px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main); font-size: 11.5px;">
                </td>

                <!-- 📝 BÀI TẬP VỀ NHÀ (CHỈ CẦN NHẬP SỐ CÂU ĐÚNG) -->
                <td style="padding: 6px 4px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <input type="number" id="hw_corr_${rowId}" value="${hwCorr}" min="0" max="100" placeholder="Số đúng" oninput="CMPortalModule.onHwScoreChange('${rowId}');" style="width: 58px; padding: 4px 6px; border-radius: 6px; border: 1.5px solid #818cf8; background: var(--bg-card); color: #818cf8; font-weight: 700; text-align: center; font-size: 12px;" title="Chỉ cần nhập số câu học sinh làm đúng">
                        <input type="hidden" id="hw_tot_${rowId}" value="${hwTot}">
                        ${scoreBadgeHtml}
                    </div>
                </td>

                <td style="padding: 6px 4px;">
                    <select id="hw_status_${rowId}" class="form-control" style="width: 100%; padding: 4px 6px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-card); font-size: 11.5px; color: var(--text-main); font-weight: 600;">
                        <option value="Nộp đúng giờ" ${hwStatus === 'Nộp đúng giờ' ? 'selected' : ''}>✅ Nộp đúng giờ</option>
                        <option value="Nộp muộn" ${hwStatus === 'Nộp muộn' ? 'selected' : ''}>⏳ Nộp muộn</option>
                        <option value="Không làm" ${hwStatus === 'Không làm' ? 'selected' : ''}>❌ Không làm</option>
                        <option value="Nghỉ học" ${hwStatus === 'Nghỉ học' ? 'selected' : ''}>🏖️ Nghỉ học</option>
                        <option value="Học buổi đầu" ${hwStatus === 'Học buổi đầu' ? 'selected' : ''}>🐣 Học buổi đầu</option>
                        <option value="Không có BVN" ${hwStatus === 'Không có BVN' ? 'selected' : ''}>⚪ Không có BVN</option>
                    </select>
                </td>

                <td style="padding: 6px 6px;">
                    <input type="text" id="hw_comment_${rowId}" value="${AuthModule.escapeHtml(hwComment)}" placeholder="Nhận xét bài về nhà..." style="width: 100%; padding: 4px 8px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main); font-size: 11.5px;">
                </td>

                <td style="padding: 6px 4px; text-align: center;">
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 2px;">
                        ${guestBadge}
                        ${removeBtnHtml}
                    </div>
                </td>
            </tr>
        `;
    },

    onGlobalHwTotalChange(globalTotVal) {
        const globalValStr = (globalTotVal || '').toString().trim();
        
        const updateRowTot = (rId) => {
            const hwTotHidden = document.getElementById(`hw_tot_${rId}`);
            if (hwTotHidden) {
                hwTotHidden.value = globalValStr;
            }
            this.onHwScoreChange(rId);
        };

        this.studentsInClass.forEach(s => updateRowTot(s.id));
        this.addedGuestStudents.forEach(g => updateRowTot(`guest_${g.code}`));
    },

    onHwScoreChange(rowId) {
        const totInput = document.getElementById(`hw_tot_${rowId}`);
        const globalTotInput = document.getElementById('global-hw-total-questions');
        const corrInput = document.getElementById(`hw_corr_${rowId}`);
        const badgeSpan = document.getElementById(`hw_badge_${rowId}`);
        if (!corrInput || !badgeSpan) return;

        let totStr = totInput ? totInput.value.trim() : '';
        if (!totStr && globalTotInput) {
            totStr = globalTotInput.value.trim();
        }

        const corrStr = corrInput.value.trim();

        if (corrStr === '' || totStr === '') {
            badgeSpan.innerHTML = `<span style="color: var(--text-muted); font-size: 11.5px;">(Chưa nhập)</span>`;
            return;
        }

        let corr = parseFloat(corrStr);
        let tot = parseFloat(totStr);

        // Validation: Cảnh báo & Giới hạn không cho nhập số câu đúng vượt quá tổng số câu
        if (!isNaN(corr) && !isNaN(tot) && tot > 0) {
            if (corr > tot) {
                App.showToast(`⚠️ Số câu đúng (${corr}) không được vượt quá Tổng số câu (${tot})!`, 'warning');
                corr = tot;
                corrInput.value = tot;
            }

            const score = Math.round((corr / tot) * 100) / 10;
            let color = '#10b981';
            if (score < 5.0) color = '#ef4444';
            else if (score < 7.0) color = '#f59e0b';

            badgeSpan.innerHTML = `<span style="color: ${color}; font-weight: 700; background: rgba(15,23,42,0.8); padding: 2px 6px; border-radius: 4px; border: 1px solid ${color}; font-size: 11.5px;">📊 ${score.toFixed(1)} / 10đ</span>`;
        }
    },

    populateGuestSelectOptions() {
        const hiddenInput = document.getElementById('guest-student-selected-code');
        const searchInput = document.getElementById('guest-student-search-input');
        if (hiddenInput) hiddenInput.value = '';
        if (searchInput && !searchInput.value) {
            searchInput.placeholder = '🔍 Gõ tên hoặc Mã HS (VD: Đào Đức Nhật Minh hoặc EVI166)...';
        }
    },

    filterGuestSuggestions(query) {
        const listDiv = document.getElementById('guest-student-suggestions-list');
        const hiddenInput = document.getElementById('guest-student-selected-code');
        if (!listDiv) return;

        if (hiddenInput) hiddenInput.value = '';

        const existingCodes = new Set([
            ...this.studentsInClass.map(s => s.code),
            ...this.addedGuestStudents.map(g => g.code)
        ]);

        const available = this.allSystemStudents.filter(st => st.code && !existingCodes.has(st.code));

        const removeAccents = (str) => {
            return (str || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
        };

        const rawQ = (query || '').trim();
        const normQ = removeAccents(rawQ);

        let matches = available;
        if (normQ.length > 0) {
            matches = available.filter(st => {
                const normName = removeAccents(st.name);
                const normCode = removeAccents(st.code);
                const normClass = removeAccents(st.class_name);
                return normName.includes(normQ) || normCode.includes(normQ) || normClass.includes(normQ);
            });
        }

        if (matches.length === 0) {
            listDiv.innerHTML = `<div style="padding: 10px 14px; color: #64748b; font-size: 12.5px; font-weight: 600;">❌ Không tìm thấy học sinh phù hợp với "${AuthModule.escapeHtml(rawQ)}"</div>`;
            listDiv.style.display = 'block';
            return;
        }

        const itemsHtml = matches.slice(0, 35).map(st => `
            <div class="guest-suggestion-item" 
                 onmousedown="CMPortalModule.selectGuestStudent('${st.code}', '${AuthModule.escapeHtml(st.name).replace(/'/g, "\\'")}');"
                 style="padding: 10px 14px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s; font-size: 13px; background: #ffffff;"
                 onmouseover="this.style.background='#f0f9ff';"
                 onmouseout="this.style.background='#ffffff';">
                <div style="font-weight: 800; color: #0f172a;">${AuthModule.escapeHtml(st.name)} <span style="color: #0284c7; font-family: monospace;">(${st.code})</span></div>
                <div style="font-size: 11.5px; color: #64748b; margin-top: 2px;">🏫 Lớp hiện tại: <strong>${AuthModule.escapeHtml(st.class_name || 'Chưa xếp lớp')}</strong></div>
            </div>
        `).join('');

        listDiv.innerHTML = itemsHtml;
        listDiv.style.display = 'block';
    },

    selectGuestStudent(code, name) {
        const searchInput = document.getElementById('guest-student-search-input');
        const hiddenInput = document.getElementById('guest-student-selected-code');
        const listDiv = document.getElementById('guest-student-suggestions-list');

        if (searchInput) searchInput.value = `${name} (${code})`;
        if (hiddenInput) hiddenInput.value = code;
        if (listDiv) listDiv.style.display = 'none';
    },

    hideGuestSuggestions() {
        const listDiv = document.getElementById('guest-student-suggestions-list');
        if (listDiv) listDiv.style.display = 'none';
    },

    addGuestStudent() {
        const hiddenInput = document.getElementById('guest-student-selected-code');
        const searchInput = document.getElementById('guest-student-search-input');
        
        let selectedCode = hiddenInput ? hiddenInput.value : '';

        // Fallback: search if user typed text directly without clicking dropdown item
        if (!selectedCode && searchInput && searchInput.value.trim()) {
            const typedVal = searchInput.value.trim().toLowerCase();
            const found = this.allSystemStudents.find(st => 
                (st.code && st.code.toLowerCase() === typedVal) || 
                (st.name && st.name.toLowerCase() === typedVal) ||
                (st.name && st.name.toLowerCase().includes(typedVal))
            );
            if (found) selectedCode = found.code;
        }

        if (!selectedCode) {
            App.showToast('Vui lòng gõ tên/mã học sinh và chọn từ danh sách gợi ý.', 'warning');
            return;
        }

        const studentObj = this.allSystemStudents.find(st => st.code === selectedCode);
        if (!studentObj) return;

        this.addedGuestStudents.push({
            id: studentObj.id,
            code: studentObj.code,
            name: studentObj.name,
            english_name: studentObj.english_name || '',
            original_class: studentObj.class_name || 'Lớp khác',
            status: 'Có mặt',
            note: 'Học ghép lớp khác',
            is_guest: true
        });

        let existingMap = {};
        this.renderAttendanceTableBody(existingMap);
        if (searchInput) searchInput.value = '';
        if (hiddenInput) hiddenInput.value = '';
        this.hideGuestSuggestions();
        App.showToast(`✅ Đã bổ sung học sinh ${studentObj.name} (${studentObj.code}) vào điểm danh!`, 'success');
    },

    removeGuestStudent(studentCode) {
        this.addedGuestStudents = this.addedGuestStudents.filter(g => g.code !== studentCode);
        this.renderAttendanceTableBody();
        this.populateGuestSelectOptions();
        App.showToast('Đã xóa học sinh khỏi danh sách điểm danh.', 'info');
    },

    onStatusSelectChange(rowId) {
        const select = document.getElementById(`att_select_${rowId}`);
        const noteInput = document.getElementById(`note_${rowId}`);
        if (select && noteInput && select.value === 'Lý do khác' && !noteInput.value) {
            noteInput.focus();
            noteInput.placeholder = 'Vui lòng nhập lý do khác...';
        }
        this.updateAttendanceStats();
    },

    updateAttendanceStats() {
        const summaryBar = document.getElementById('attendance-summary-bar');
        if (!summaryBar) return;

        let total = 0, present = 0, absentPerm = 0, absentNoPerm = 0, other = 0;
        const selects = document.querySelectorAll('.att-status-select');

        selects.forEach(s => {
            total++;
            const val = s.value;
            if (val === 'Có mặt') present++;
            else if (val === 'Vắng có phép') absentPerm++;
            else if (val === 'Vắng không phép' || val.includes('Vắng')) absentNoPerm++;
            else other++;
        });

        summaryBar.innerHTML = `
            <span>Sĩ số điểm danh: <strong style="color: var(--text-heading); font-size: 13.5px;">${total} HS</strong></span>
            <span style="color: var(--border-color);">|</span>
            <span style="color: #34d399;">🟢 Có mặt: <strong>${present}</strong></span>
            <span style="color: #f97316;">🟠 Vắng có phép: <strong>${absentPerm}</strong></span>
            <span style="color: #f87171;">🔴 Vắng không phép: <strong>${absentNoPerm}</strong></span>
            <span style="color: #60a5fa;">🔵 Lý do khác: <strong>${other}</strong></span>
        `;
    },

    handleAttendanceDateChange(dateVal) {
        this.loadAttendanceRecords(this.selectedClassName, dateVal);
    },

    markAllAttendance(statusVal) {
        const selects = document.querySelectorAll('.att-status-select');
        selects.forEach(s => {
            s.value = statusVal;
        });
        this.updateAttendanceStats();
        App.showToast(`Đã đặt tất cả học sinh thành '${statusVal}'`, 'info');
    },

    async saveAttendance() {
        if (!AuthModule.isLoggedIn()) {
            App.showToast('Vui lòng đăng nhập tài khoản CM để thực hiện điểm danh.', 'warning');
            AuthModule.showLoginModal();
            return;
        }

        const dateVal = document.getElementById('attendance-date-picker').value;
        if (!dateVal) {
            App.showToast('Vui lòng chọn ngày điểm danh.', 'warning');
            return;
        }

        const records = [];
        const globalTotInput = document.getElementById('global-hw-total-questions');
        const globalTotVal = (globalTotInput && globalTotInput.value.trim() !== '') ? parseInt(globalTotInput.value.trim(), 10) : null;

        // 1. Official Students
        this.studentsInClass.forEach(s => {
            const rowId = s.id;
            const select = document.getElementById(`att_select_${rowId}`);
            const noteInput = document.getElementById(`note_${rowId}`);
            const hwCorrInput = document.getElementById(`hw_corr_${rowId}`);
            const hwTotInput = document.getElementById(`hw_tot_${rowId}`);
            const hwStatusSelect = document.getElementById(`hw_status_${rowId}`);
            const hwCommentInput = document.getElementById(`hw_comment_${rowId}`);

            const rowTotVal = (hwTotInput && hwTotInput.value.trim() !== '') ? parseInt(hwTotInput.value.trim(), 10) : globalTotVal;

            records.push({
                student_code: s.code,
                student_name: s.name,
                status: select ? select.value : 'Có mặt',
                note: noteInput ? noteInput.value.trim() : '',
                is_guest: false,
                hw_correct_answers: hwCorrInput && hwCorrInput.value.trim() !== '' ? parseInt(hwCorrInput.value.trim(), 10) : null,
                hw_total_questions: rowTotVal,
                hw_submission_status: hwStatusSelect ? hwStatusSelect.value : 'Nộp đúng giờ',
                hw_comment: hwCommentInput ? hwCommentInput.value.trim() : ''
            });
        });

        // 2. Added Guest Students
        this.addedGuestStudents.forEach(g => {
            const rowId = `guest_${g.code}`;
            const select = document.getElementById(`att_select_${rowId}`);
            const noteInput = document.getElementById(`note_${rowId}`);
            const hwCorrInput = document.getElementById(`hw_corr_${rowId}`);
            const hwTotInput = document.getElementById(`hw_tot_${rowId}`);
            const hwStatusSelect = document.getElementById(`hw_status_${rowId}`);
            const hwCommentInput = document.getElementById(`hw_comment_${rowId}`);

            const rowTotVal = (hwTotInput && hwTotInput.value.trim() !== '') ? parseInt(hwTotInput.value.trim(), 10) : globalTotVal;

            records.push({
                student_code: g.code,
                student_name: g.name,
                status: select ? select.value : 'Có mặt',
                note: noteInput ? noteInput.value.trim() : '',
                is_guest: true,
                hw_correct_answers: hwCorrInput && hwCorrInput.value.trim() !== '' ? parseInt(hwCorrInput.value.trim(), 10) : null,
                hw_total_questions: hwTotInput && hwTotInput.value.trim() !== '' ? parseInt(hwTotInput.value.trim(), 10) : null,
                hw_submission_status: hwStatusSelect ? hwStatusSelect.value : 'Nộp đúng giờ',
                hw_comment: hwCommentInput ? hwCommentInput.value.trim() : ''
            });
        });

        try {
            const user = AuthModule.getUser();
            const res = await API.saveAttendance({
                class_name: this.selectedClassName,
                date: dateVal,
                records: records,
                created_by: user ? user.username : ''
            });

            if (res.success) {
                App.showToast(`Lưu điểm danh thành công cho lớp ${this.selectedClassName} ngày ${dateVal} (${records.length} HS)!`, 'success');
            } else {
                App.showToast(res.error || 'Lưu điểm danh thất bại', 'error');
            }
        } catch (e) {
            App.showToast(e.message || 'Lỗi lưu điểm danh', 'error');
        }
    },

    async handleAttendanceClassChange(newClassName) {
        if (!newClassName) return;
        this.selectedClassName = newClassName;
        await this.loadRosterForClass(newClassName);
        const datePicker = document.getElementById('attendance-date-picker');
        const selectedDate = datePicker ? datePicker.value : (this.selectedAttendanceDate || new Date().toISOString().split('T')[0]);
        await this.loadAttendanceRecords(newClassName, selectedDate);
        App.showToast(`Đã chuyển điểm danh sang lớp ${newClassName}!`, 'info');
    },

    async handleAttendanceDateChange(dateStr) {
        this.selectedAttendanceDate = dateStr;
        if (this.selectedClassName) {
            await this.loadAttendanceRecords(this.selectedClassName, dateStr);
        }
    },

    async renderGradeEntryTab() {
        const tabContent = document.getElementById('cm-tab-content');
        if (!tabContent) return;

        if (this.selectedClassName) {
            await this.loadRosterForClass(this.selectedClassName);
        }

        const clsLower = (this.selectedClassName || '').toLowerCase();
        const isMoon5 = clsLower.includes('moon 5');
        const isMoon = clsLower.startsWith('moon');

        let defaultTestName = 'Unit 1';
        let testOptionsHtml = '';

        if (isMoon5) {
            defaultTestName = 'Unit 2';
            testOptionsHtml = `
                <option value="Unit 2">Unit 2</option>
                <option value="Unit 3">Unit 3</option>
                <option value="Unit 4">Unit 4</option>
                <option value="Midterm test">Midterm test</option>
            `;
        } else if (isMoon) {
            defaultTestName = 'Unit 1';
            testOptionsHtml = `
                <option value="Unit 1">Unit 1</option>
                <option value="Unit 2">Unit 2</option>
                <option value="Unit 3">Unit 3</option>
                <option value="Unit 4">Unit 4</option>
                <option value="Unit 5">Unit 5</option>
                <option value="Midterm test">Midterm test</option>
                <option value="Unit 6">Unit 6</option>
                <option value="Unit 7">Unit 7</option>
                <option value="Unit 8">Unit 8</option>
                <option value="Unit 9">Unit 9</option>
                <option value="Final test">Final test</option>
            `;
        } else {
            defaultTestName = 'Unit 01';
            testOptionsHtml = `
                <option value="Unit 01">Unit 01</option>
                <option value="Unit 02">Unit 02</option>
                <option value="Unit 03">Unit 03</option>
                <option value="Unit 04">Unit 04</option>
                <option value="Unit 05">Unit 05</option>
                <option value="Unit 06">Unit 06</option>
                <option value="Unit 07">Unit 07</option>
                <option value="Unit 08">Unit 08</option>
                <option value="Unit 09">Unit 09</option>
                <option value="Unit 10">Unit 10</option>
                <option value="Unit 11">Unit 11</option>
                <option value="Unit 12">Unit 12</option>
                <option value="Unit 1-2">Unit 1-2</option>
                <option value="Unit 3-4">Unit 3-4</option>
                <option value="Unit 5-6">Unit 5-6</option>
                <option value="Unit 7-8">Unit 7-8</option>
                <option value="Unit 9-10">Unit 9-10</option>
                <option value="Unit 11-12">Unit 11-12</option>
                <option value="Midterm">Midterm</option>
                <option value="Final">Final</option>
            `;
        }

        const totalConfigHtml = isMoon ? `
            <div style="display: flex; align-items: center; gap: 10px; background: #f8fafc; padding: 8px 14px; border-radius: 8px; border: 1.5px solid #cbd5e1;">
                <span style="font-size: 12.5px; font-weight: 800; color: #1e293b;">⚙️ Tổng số từ vựng bài test (Chung):</span>
                <div style="font-size: 12.5px; font-weight: 700; color: #334155;">📚 Từ vựng: <input type="number" id="tot_vocab_q" value="" placeholder="VD 20" style="width: 65px; padding: 4px 8px; border-radius: 6px; border: 1.5px solid #94a3b8; background: #ffffff; color: #0f172a; text-align: center; font-weight: 800;" oninput="CMPortalModule.recalcAllGradeRowScores();" onkeyup="CMPortalModule.recalcAllGradeRowScores();"></div>
            </div>
        ` : `
            <div style="display: flex; align-items: center; gap: 10px; background: #f8fafc; padding: 8px 14px; border-radius: 8px; border: 1.5px solid #cbd5e1;">
                <span style="font-size: 12.5px; font-weight: 800; color: #1e293b;">⚙️ Tổng số câu (Chung):</span>
                <div style="font-size: 12.5px; font-weight: 700; color: #334155;">🎧 Listening: <input type="number" id="tot_lis_q" value="" placeholder="VD 15" style="width: 60px; padding: 4px 6px; border-radius: 6px; border: 1.5px solid #94a3b8; background: #ffffff; color: #0f172a; text-align: center; font-weight: 800;" oninput="CMPortalModule.recalcAllGradeRowScores();" onkeyup="CMPortalModule.recalcAllGradeRowScores();"></div>
                <div style="font-size: 12.5px; font-weight: 700; color: #334155;">📖 R&W: <input type="number" id="tot_rw_q" value="" placeholder="VD 20" style="width: 60px; padding: 4px 6px; border-radius: 6px; border: 1.5px solid #94a3b8; background: #ffffff; color: #0f172a; text-align: center; font-weight: 800;" oninput="CMPortalModule.recalcAllGradeRowScores();" onkeyup="CMPortalModule.recalcAllGradeRowScores();"></div>
                <div style="font-size: 12.5px; font-weight: 700; color: #334155;">🗣️ Speaking: <input type="number" id="tot_spk_q" value="" placeholder="VD 10" style="width: 60px; padding: 4px 6px; border-radius: 6px; border: 1.5px solid #94a3b8; background: #ffffff; color: #0f172a; text-align: center; font-weight: 800;" oninput="CMPortalModule.recalcAllGradeRowScores();" onkeyup="CMPortalModule.recalcAllGradeRowScores();"></div>
            </div>
        `;

        const tableHeaderHtml = isMoon ? `
            <tr style="background: #f1f5f9; color: #0f172a; text-align: left; font-size: 13px; border-bottom: 2px solid #cbd5e1;">
                <th style="padding: 12px 14px; width: 35px; color: #0f172a; font-weight: 800;">STT</th>
                <th style="padding: 12px 14px; min-width: 170px; color: #0f172a; font-weight: 800;">Họ Và Tên Học Sinh (Hệ Moon)</th>
                <th style="padding: 12px 14px; width: 230px; text-align: center; color: #0f172a; font-weight: 800;">📝 Tích Đánh Giá Chi Tiết Bài Test</th>
                <th style="padding: 12px 14px; min-width: 240px; color: #0f172a; font-weight: 800;">Nhận Xét Bài Thi</th>
                <th style="padding: 12px 14px; width: 140px; text-align: center; color: #0f172a; font-weight: 800;">Mẫu Báo Cáo PDF</th>
            </tr>
        ` : `
            <tr style="background: #f1f5f9; color: #0f172a; text-align: left; font-size: 13px; border-bottom: 2px solid #cbd5e1;">
                <th style="padding: 12px 14px; width: 35px; color: #0f172a; font-weight: 800;">STT</th>
                <th style="padding: 12px 14px; min-width: 160px; color: #0f172a; font-weight: 800;">Họ Và Tên Học Sinh</th>
                <th style="padding: 12px 14px; width: 140px; color: #0f172a; font-weight: 800;">🎧 Listening (Số câu / Điểm)</th>
                <th style="padding: 12px 14px; width: 140px; color: #0f172a; font-weight: 800;">📖 Reading & Writing</th>
                <th style="padding: 12px 14px; width: 140px; color: #0f172a; font-weight: 800;">🗣️ Speaking</th>
                <th style="padding: 12px 14px; min-width: 240px; color: #0f172a; font-weight: 800;">Nhận Xét Bài Thi</th>
                <th style="padding: 12px 14px; width: 130px; text-align: center; color: #0f172a; font-weight: 800;">Mẫu Báo Cáo PDF</th>
            </tr>
        `;

        const todayStr = new Date().toISOString().split('T')[0];

        tabContent.innerHTML = `
            <div class="card" style="margin-bottom: 20px; padding: 16px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                    <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; display: block; margin-bottom: 4px;">💯 BÀI KIỂM TRA / BÀI THI:</label>
                            <select id="grade-test-name-select" class="form-control" onchange="CMPortalModule.handleTestNameChange(this.value);" style="padding: 7px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 13px; font-weight: 800;">
                                ${testOptionsHtml}
                            </select>
                        </div>

                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; display: block; margin-bottom: 4px;">📅 NGÀY KIỂM TRA:</label>
                            <input type="date" id="grade-test-date-picker" value="${todayStr}" style="padding: 6px 10px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 13px; font-weight: 800;">
                        </div>

                        ${totalConfigHtml}
                    </div>

                    <button class="btn btn-primary" onclick="CMPortalModule.saveGrades();" style="padding: 10px 22px; font-weight: 800; background: #2563eb; color: #ffffff; border: none; border-radius: 8px; box-shadow: 0 4px 14px rgba(37,99,235,0.3); cursor: pointer;">
                        💾 Lưu Kết Quả Điểm Thi
                    </button>
                </div>
            </div>

            <div class="card" style="padding: 0; overflow: hidden; border-radius: 12px; border: 1px solid #e2e8f0; background: #ffffff;">
                <div class="table-responsive">
                    <table class="data-table" style="width: 100%; border-collapse: collapse;">
                        <thead>
                            ${tableHeaderHtml}
                        </thead>
                        <tbody id="grade-table-body">
                            <!-- Filled dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        await this.loadGradesForTest(this.selectedClassName, defaultTestName);
    },

    async loadGradesForTest(className, testName) {
        this.selectedTestName = testName;
        const tbody = document.getElementById('grade-table-body');
        if (!tbody) return;

        const isMoon = (className || '').toLowerCase().startsWith('moon');

        let existingGradesMap = {};
        let savedLisMax = null, savedRwMax = null, savedSpkMax = null;
        try {
            const res = await API.getGrades({ class_name: className, test_name: testName });
            if (res.success && res.data) {
                res.data.forEach(g => {
                    existingGradesMap[g.name] = g;
                    if (g.listening_max && !savedLisMax) savedLisMax = g.listening_max;
                    if (g.reading_writing_max && !savedRwMax) savedRwMax = g.reading_writing_max;
                    if (g.speaking_max && !savedSpkMax) savedSpkMax = g.speaking_max;
                });
            }
        } catch (e) {
            console.error('Error loading test grades:', e);
        }

        // Restore saved total max questions to top input fields if present
        const totLisInput = document.getElementById('tot_lis_q');
        const totRwInput = document.getElementById('tot_rw_q');
        const totSpkInput = document.getElementById('tot_spk_q');
        const totVocabInput = document.getElementById('tot_vocab_q');

        if (isMoon) {
            if (totVocabInput && savedRwMax) totVocabInput.value = savedRwMax;
        } else {
            if (totLisInput && savedLisMax) totLisInput.value = savedLisMax;
            if (totRwInput && savedRwMax) totRwInput.value = savedRwMax;
            if (totSpkInput && savedSpkMax) totSpkInput.value = savedSpkMax;
        }

        const rows = this.studentsInClass.map((s, idx) => {
            const eg = existingGradesMap[s.name] || {};
            const lis = eg.listening !== null && eg.listening !== undefined ? eg.listening : '';
            const rw = eg.reading_writing !== null && eg.reading_writing !== undefined ? eg.reading_writing : '';
            const spk = eg.speaking !== null && eg.speaking !== undefined ? eg.speaking : '';
            const cmt = eg.comment || '';

            if (isMoon) {
                return `
                    <tr style="border-bottom: 1px solid #e2e8f0; background: ${idx % 2 === 0 ? '#ffffff' : '#f8fafc'};">
                        <td style="color: #475569; text-align: center; font-weight: 800;">${idx + 1}</td>
                        <td>
                            <div style="font-weight: 800; color: #0f172a; font-size: 14px;">${AuthModule.escapeHtml(s.name)}</div>
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; font-family: monospace;">${AuthModule.escapeHtml(s.code)} ${s.english_name ? `• ${AuthModule.escapeHtml(s.english_name)}` : ''}</div>
                            <input type="hidden" id="vocab_q_${s.id}" value="${rw || lis || 15}">
                            <input type="hidden" id="phonics_${s.id}" value="${spk || 9}">
                        </td>
                        <td style="text-align: center;">
                            <button class="btn btn-sm" onclick="CMPortalModule.openMoonDetailModal('${s.code}', '${AuthModule.escapeHtml(s.name)}', '${s.id}');" style="background: #059669; color: #ffffff; border: none; padding: 7px 16px; font-weight: 800; cursor: pointer; border-radius: 8px; box-shadow: 0 2px 6px rgba(5,150,105,0.25);" title="Mở Cửa Sổ Chấm Tích 3 Mức Độ (Excellent, Satisfactory, Need support) Cho ${AuthModule.escapeHtml(s.name)}">
                                📝 Tích Đánh Giá Chi Tiết (Moon)
                            </button>
                        </td>
                        <td style="min-width: 240px;">
                            ${this.renderCommentFieldHTML(s, cmt, idx)}
                        </td>
                        <td style="text-align: center;">
                            <button class="btn btn-sm" onclick="CMPortalModule.exportStudentUnitTestPdf('${s.code}', '${AuthModule.escapeHtml(s.name)}', '${s.id}');" style="background: #0284c7; color: #ffffff; border: none; padding: 7px 16px; font-size: 12.5px; font-weight: 800; cursor: pointer; border-radius: 8px; box-shadow: 0 2px 6px rgba(2,132,199,0.25);" title="Xuất Báo Cáo PDF Bài Test MOON UNIT TEST cho ${AuthModule.escapeHtml(s.name)}">
                                📄 Báo Cáo PDF
                            </button>
                        </td>
                    </tr>
                `;
            }

            return `
                <tr style="border-bottom: 1px solid #e2e8f0; background: ${idx % 2 === 0 ? '#ffffff' : '#f8fafc'};">
                    <td style="color: #475569; text-align: center; font-weight: 800;">${idx + 1}</td>
                    <td>
                        <div style="font-weight: 800; color: #0f172a; font-size: 14px;">${AuthModule.escapeHtml(s.name)}</div>
                        <div style="font-size: 12px; color: #64748b; font-weight: 600; font-family: monospace;">${AuthModule.escapeHtml(s.code)} ${s.english_name ? `• ${AuthModule.escapeHtml(s.english_name)}` : ''}</div>
                    </td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <input type="number" step="0.5" min="0" id="lis_q_${s.id}" value="${lis}" placeholder="Đúng" style="width: 55px; padding: 5px 6px; border-radius: 6px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 800; text-align: center;" oninput="CMPortalModule.calcRowGrade10('${s.id}');">
                            <span style="font-size: 11.5px; color: #64748b; font-weight: 600;">/ <span id="lbl_tot_lis_${s.id}">—</span></span>
                        </div>
                        <div style="font-size: 11.5px; color: #0f172a; font-weight: 800; margin-top: 3px;" id="score_10_lis_${s.id}">— / 10đ</div>
                    </td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <input type="number" step="0.5" min="0" id="rw_q_${s.id}" value="${rw}" placeholder="Đúng" style="width: 55px; padding: 5px 6px; border-radius: 6px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 800; text-align: center;" oninput="CMPortalModule.calcRowGrade10('${s.id}');">
                            <span style="font-size: 11.5px; color: #64748b; font-weight: 600;">/ <span id="lbl_tot_rw_${s.id}">—</span></span>
                        </div>
                        <div style="font-size: 11.5px; color: #16a34a; font-weight: 800; margin-top: 3px;" id="score_10_rw_${s.id}">— / 10đ</div>
                    </td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <input type="number" step="0.5" min="0" id="spk_q_${s.id}" value="${spk}" placeholder="Đúng" style="width: 55px; padding: 5px 6px; border-radius: 6px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 800; text-align: center;" oninput="CMPortalModule.calcRowGrade10('${s.id}');">
                            <span style="font-size: 11.5px; color: #64748b; font-weight: 600;">/ <span id="lbl_tot_spk_${s.id}">—</span></span>
                        </div>
                        <div style="font-size: 11.5px; color: #d97706; font-weight: 800; margin-top: 3px;" id="score_10_spk_${s.id}">— / 10đ</div>
                    </td>
                    <td style="min-width: 240px;">
                        ${this.renderCommentFieldHTML(s, cmt, idx)}
                    </td>
                    <td style="text-align: center;">
                        <button class="btn btn-sm" onclick="CMPortalModule.exportStudentUnitTestPdf('${s.code}', '${AuthModule.escapeHtml(s.name)}', '${s.id}');" style="background: #0284c7; color: #ffffff; border: none; padding: 7px 16px; font-size: 12.5px; font-weight: 800; cursor: pointer; border-radius: 8px; box-shadow: 0 2px 6px rgba(2,132,199,0.25);" title="Xuất Báo Cáo PDF">
                            📄 Báo Cáo PDF
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = rows.length > 0 ? rows : `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: var(--text-muted);">
                    Không có học sinh trong lớp để nhập điểm.
                </td>
            </tr>
        `;

        // Recalculate row scores on initial load
        this.recalcAllGradeRowScores();
    },

    recalcAllGradeRowScores() {
        const isMoon = (this.selectedClassName || '').toLowerCase().startsWith('moon');
        if (isMoon) {
            const totVocabInput = document.getElementById('tot_vocab_q');
            const totVocab = totVocabInput && totVocabInput.value.trim() !== '' ? parseFloat(totVocabInput.value.trim()) : 0;

            this.studentsInClass.forEach(s => {
                const lblVocab = document.getElementById(`lbl_tot_vocab_${s.id}`);
                if (lblVocab) lblVocab.innerText = totVocab > 0 ? totVocab : '—';
                this.calcRowGrade10(s.id);
            });
            return;
        }

        const totLisInput = document.getElementById('tot_lis_q');
        const totRwInput = document.getElementById('tot_rw_q');
        const totSpkInput = document.getElementById('tot_spk_q');

        const totLis = totLisInput && totLisInput.value.trim() !== '' ? parseFloat(totLisInput.value.trim()) : 0;
        const totRw = totRwInput && totRwInput.value.trim() !== '' ? parseFloat(totRwInput.value.trim()) : 0;
        const totSpk = totSpkInput && totSpkInput.value.trim() !== '' ? parseFloat(totSpkInput.value.trim()) : 0;

        this.studentsInClass.forEach(s => {
            const lblLis = document.getElementById(`lbl_tot_lis_${s.id}`);
            const lblRw = document.getElementById(`lbl_tot_rw_${s.id}`);
            const lblSpk = document.getElementById(`lbl_tot_spk_${s.id}`);

            if (lblLis) lblLis.innerText = totLis > 0 ? totLis : '—';
            if (lblRw) lblRw.innerText = totRw > 0 ? totRw : '—';
            if (lblSpk) lblSpk.innerText = totSpk > 0 ? totSpk : '—';

            this.calcRowGrade10(s.id);
        });
    },

    calcRowGrade10(studentId) {
        const isMoon = (this.selectedClassName || '').toLowerCase().startsWith('moon');
        if (isMoon) {
            const totVocabInput = document.getElementById('tot_vocab_q');
            const totVocab = totVocabInput && totVocabInput.value.trim() !== '' ? parseFloat(totVocabInput.value.trim()) : 0;
            const corrVocabInput = document.getElementById(`vocab_q_${studentId}`);
            const corrVocab = corrVocabInput && corrVocabInput.value.trim() !== '' ? parseFloat(corrVocabInput.value.trim()) : NaN;

            const scoreVocabDiv = document.getElementById(`score_10_vocab_${studentId}`);
            if (scoreVocabDiv) {
                if (!isNaN(corrVocab) && totVocab > 0) {
                    const p10 = ((corrVocab / totVocab) * 10).toFixed(1);
                    scoreVocabDiv.innerText = `${p10} / 10đ (${corrVocab}/${totVocab})`;
                } else scoreVocabDiv.innerText = '— / 10đ';
            }
            return;
        }

        const totLisInput = document.getElementById('tot_lis_q');
        const totRwInput = document.getElementById('tot_rw_q');
        const totSpkInput = document.getElementById('tot_spk_q');

        const totLis = totLisInput && totLisInput.value.trim() !== '' ? parseFloat(totLisInput.value.trim()) : 0;
        const totRw = totRwInput && totRwInput.value.trim() !== '' ? parseFloat(totRwInput.value.trim()) : 0;
        const totSpk = totSpkInput && totSpkInput.value.trim() !== '' ? parseFloat(totSpkInput.value.trim()) : 0;

        const corrLis = parseFloat(document.getElementById(`lis_q_${studentId}`)?.value);
        const corrRw = parseFloat(document.getElementById(`rw_q_${studentId}`)?.value);
        const corrSpk = parseFloat(document.getElementById(`spk_q_${studentId}`)?.value);

        const scoreLisDiv = document.getElementById(`score_10_lis_${studentId}`);
        const scoreRwDiv = document.getElementById(`score_10_rw_${studentId}`);
        const scoreSpkDiv = document.getElementById(`score_10_spk_${studentId}`);

        if (scoreLisDiv) {
            if (!isNaN(corrLis) && totLis > 0) {
                const p10 = ((corrLis / totLis) * 10).toFixed(1);
                scoreLisDiv.innerText = `${p10} / 10đ (${corrLis}/${totLis})`;
            } else scoreLisDiv.innerText = '— / 10đ';
        }

        if (scoreRwDiv) {
            if (!isNaN(corrRw) && totRw > 0) {
                const p10 = ((corrRw / totRw) * 10).toFixed(1);
                scoreRwDiv.innerText = `${p10} / 10đ (${corrRw}/${totRw})`;
            } else scoreRwDiv.innerText = '— / 10đ';
        }

        if (scoreSpkDiv) {
            if (!isNaN(corrSpk) && totSpk > 0) {
                const p10 = ((corrSpk / totSpk) * 10).toFixed(1);
                scoreSpkDiv.innerText = `${p10} / 10đ (${corrSpk}/${totSpk})`;
            } else scoreSpkDiv.innerText = '— / 10đ';
        }
    },

    generateAiCommentForStudent(studentId, studentName) {
        const cmtInput = document.getElementById(`cmt_${studentId}`);
        if (!cmtInput) return;

        const isMoon = (this.selectedClassName || '').toLowerCase().startsWith('moon');
        const userDraftText = cmtInput.value.trim();

        // 🌟 Bộ câu từ khích lệ sư phạm chuẩn ELT (Hoàn toàn tích cực, không chỉ trích hay bịa lỗi sai)
        const praiseVocab = [
            "nắm từ vựng bài học rất chắc chắn và phản xạ từ nhanh nhẹn",
            "ghi nhớ lượng từ mới vô cùng tốt và hiểu rõ nghĩa của từ",
            "rất chăm chỉ học thuộc các thẻ từ vựng và tự tin trả lời"
        ];

        const praisePhonicsSkill = [
            "phát âm âm tiết rõ ràng, đúng trọng âm và ngữ điệu tự nhiên",
            "kỹ năng làm bài tập trung, cẩn thận và tư duy nghe / đọc hiểu nhạy bén",
            "thể hiện phản xạ ngữ âm chính xác và trình bày bài thi rất chỉn chu"
        ];

        const encouragementTail = [
            `Thầy/Cô tin tưởng em ${studentName} sẽ tiếp tục phát huy tinh thần tuyệt vời này ở các bài học tiếp theo!`,
            `Thầy/Cô rất tự hào về sự nỗ lực học tập của em ${studentName} và chúc em luôn giữ vững phong độ!`,
            `Em ${studentName} hãy luôn duy trì niềm yêu thích tiếng Anh và tiếp tục gặt hái nhiều điểm số xuất sắc nhé!`
        ];

        const randomItem = (arr) => arr[Math.floor(Math.random() * arr.length)];

        let finalComment = '';

        if (userDraftText) {
            // 💡 ĐÃ CÓ NỘI DUNG NHẬP TAY: AI lấy ý tưởng của người dùng làm nòng cốt và phát triển đầy đủ các tiêu chí
            let baseIdea = userDraftText.replace(/[.,;!]+$/, '');

            // Phát triển ý nhập tay thành câu nhận xét hoàn chỉnh, chuẩn mực, khích lệ & KHÔNG có lỗi sai
            finalComment = `Thầy/Cô ghi nhận em ${studentName} ${baseIdea}. Em ${randomItem(praisePhonicsSkill)}. ${randomItem(encouragementTail)}`;
        } else {
            // 💡 CHƯA CÓ NỘI DUNG NHẬP TAY: AI tự động khởi tạo nhận xét đầy đủ tiêu chí theo điểm số
            if (isMoon) {
                const totVocab = parseFloat(document.getElementById('tot_vocab_q')?.value || 20);
                const corrVocab = parseFloat(document.getElementById(`vocab_q_${studentId}`)?.value || 0);
                const ratio = totVocab > 0 ? corrVocab / totVocab : 0.8;

                if (ratio >= 0.9) {
                    finalComment = `Thầy/Cô khen ngợi em ${studentName} ${randomItem(praiseVocab)}, ${randomItem(praisePhonicsSkill)}! ${randomItem(encouragementTail)}`;
                } else if (ratio >= 0.7) {
                    finalComment = `Thầy/Cô ghi nhận em ${studentName} nắm từ vựng bài học khá tốt và phản xạ nhanh nhẹn! Em chú ý đọc và phát âm thêm hàng ngày để luôn tự tin đạt kết quả cao nhất nhé.`;
                } else {
                    finalComment = `Thầy/Cô động viên em ${studentName} tiếp tục phát huy tinh thần hăng hái trên lớp và ôn tập thẻ từ vựng đều đặn! Thầy/Cô tin em sẽ có nhiều tiến bộ vượt bậc ở bài kiểm tra tới.`;
                }
            } else {
                const corrLis = parseFloat(document.getElementById(`lis_q_${studentId}`)?.value || 0);
                const totLis = parseFloat(document.getElementById('tot_lis_q')?.value || 15);
                const corrRw = parseFloat(document.getElementById(`rw_q_${studentId}`)?.value || 0);
                const totRw = parseFloat(document.getElementById('tot_rw_q')?.value || 20);

                const pLis = totLis > 0 ? (corrLis / totLis) * 10 : 0;
                const pRw = totRw > 0 ? (corrRw / totRw) * 10 : 0;
                const avg = ((pLis + pRw) / 2);

                if (avg >= 9.0) {
                    finalComment = `Thầy/Cô khen ngợi em ${studentName} làm bài thi rất xuất sắc! Em ${randomItem(praiseVocab)} và ${randomItem(praisePhonicsSkill)}. ${randomItem(encouragementTail)}`;
                } else if (avg >= 7.0) {
                    finalComment = `Thầy/Cô nhận thấy em ${studentName} nắm chắc kiến thức căn bản, ${randomItem(praisePhonicsSkill)}! Em tiếp tục duy trì phong độ và luyện tập thêm các dạng bài nâng cao nhé.`;
                } else if (avg >= 5.0) {
                    finalComment = `Thầy/Cô đánh giá em ${studentName} đã nắm vững các từ vựng nền tảng và luôn nỗ lực trong giờ học! Em dành thêm thời gian luyện đọc và nghe hàng ngày để tự tin bứt phá điểm số nhé.`;
                } else {
                    finalComment = `Thầy/Cô khen ngợi tinh thần đi học đầy đủ và thái độ hợp tác tích cực của em ${studentName}! Thầy/Cô động viên em tiếp tục ôn tập từ vựng đều đặn để gặt hái kết quả tốt hơn ở các bài thi tới.`;
                }
            }
        }

        cmtInput.value = finalComment;
        if (typeof App !== 'undefined' && App.showToast) {
            App.showToast(`✨ AI đã phát triển & hoàn thiện nhận xét cho ${studentName}!`, 'success');
        }
    },

    getMoonSyllabusData(className, testName) {
        // Official Syllabus Mapping for Moon 1 to Moon 6
        const syllabusMap = {
            "Moon 1": {
                "Unit 01": { subtitle: "UNIT 1: CLASSROOM RULES & FRIENDS", vocab: ["Be quiet", "Speak English", "No Fighting", "Sit nicely", "I can", "Mimi", "Dylan", "Mommy", "Daddy", "Boy", "Girl", "Red", "Ferris Wheel"], phonics: ["Letter A - /a/(Apple, Ant, Annie Ant)", "Letter B - /b/(Bear, ball, Benny Bear)"], struct: ["Hello! I'm.....", "Who is it? It's...."] },
                "Unit 02": { subtitle: "UNIT 2: FAMILY", vocab: ["Mommy", "Daddy", "Grandma", "Grandpa", "Brother", "Sister", "Round", "Wheel", "Red", "Yellow", "Orange", "Pink"], phonics: ["Letter C - /k/(Cat, cut, Candy cat)", "Letter D - /d/(Dog, dig, Danny dog)"], struct: ["What colour is it? It's...", "Where is mommy? Here! (point)"] },
                "Unit 03": { subtitle: "UNIT 3: CLASSROOM", vocab: ["Book", "Crayon", "Eraser", "Pencil", "Table", "Chair", "Blue", "Shelf", "Tray"], phonics: ["Letter C - /c/(Cut, Candy, Candy Cat)", "Letter D - /d/(Dog, dig, Danny Dog)"], struct: ["What's is this? It's a...."] },
                "Unit 04": { subtitle: "UNIT 4: MY FACE", vocab: ["Ear", "Eye", "Hair", "Mouth", "Nose", "Teeth", "Hear", "See"], phonics: ["Letter E - /e/(Elephant, egg, Eddie elephant)"], struct: ["I have (a nose).", "I have (two) (eyes)."] },
                "Unit 05": { subtitle: "UNIT 5: CLOTHES", vocab: ["Hat", "Shirt", "Pants", "Shoes", "Socks", "Dress", "Coat", "Blue", "Green", "Purple", "Clean", "Dirty"], phonics: ["Letter I - /i/(Ink, Insect)", "Letter J - /dʒ/(Jam, Juice)"], struct: ["Put on your.....", "Take off your....."] },
                "Midterm test": { subtitle: "MOON 1 MIDTERM TEST REVIEW (UNITS 1 - 3)", vocab: ["Book", "Crayon", "Eraser", "Pencil", "Table", "Chair", "Mommy", "Daddy", "Grandma", "Grandpa", "Brother", "Sister", "Ear", "Eye", "Nose", "Mouth", "Hat", "Shirt", "Pants", "Shoes"], phonics: ["Letter A - /a/ (Apple)", "Letter B - /b/ (Bear)", "Letter C - /k/ (Cat)", "Letter D - /d/ (Dog)", "Letter E - /e/ (Elephant)"], struct: ["What's this? It's a...", "Who is it? It's...", "What colour is it? It's...", "I have (two eyes)."] },
                "Final test": { subtitle: "MOON 1 FINAL TEST REVIEW (UNITS 1 - 5)", vocab: ["Book", "Pencil", "Mommy", "Daddy", "Ear", "Eye", "Hat", "Shirt", "Socks", "Red", "Yellow", "Blue", "Green"], phonics: ["Review Letters A to J"], struct: ["What's this? It's a...", "Put on your...", "I have..."] }
            },
            "Moon 2": {
                "Unit 06": { subtitle: "UNIT 6: TOYS", vocab: ["Ball", "Car", "Teddy", "Doll", "Scooter", "Train", "Classroom", "Playground", "Play", "Work"], phonics: ["Letter I - /i/(Insect, ill, Ian insect)", "Letter J - /j/(Jellyfish, jump, Jane jellyfish)"], struct: ["What toy is it? It's a….", "Where is the (car)? Here!"] },
                "Unit 07": { subtitle: "UNIT 7: FOOD", vocab: ["Apple", "Banana", "Cookie", "Juice", "Sandwich", "Water", "Drink", "Eat"], phonics: ["Letter K - /k/(Kangaroo, kick, Kenny Kangaroo)", "Letter J - /j/(Jellyfish, jump, Jane jellyfish)"], struct: ["What food is it? It's....", "Do you like (bananas)? I like (bananas)."] },
                "Unit 08": { subtitle: "UNIT 8: PETS", vocab: ["Bird", "Cat", "Dog", "Fish", "Mouse", "Rabbit", "Fly", "Swim"], phonics: ["Letter L - /l/(Lion, leg, Larry lion)", "Letter K - /k/(Kangaroo, kick, Kenny Kangaroo)"], struct: ["What animal is it? (It's)....", "Is it a (rabbit)? Yes, it is/ No, it isn't."] },
                "Unit 09": { subtitle: "UNIT 9: BEACH", vocab: ["Crab", "Ocean", "Sand", "Shell", "Bucket", "Shovel", "Land", "Water"], phonics: ["Letter M - /m/(Money, mouth, Mickey monkey)", "Letter L - /l/(Lion, leg, Larry lion)"], struct: ["What's it? (It's)...", "What can you see? (I can see) a shell."] },
                "Midterm test": { subtitle: "MOON 2 MIDTERM TEST REVIEW (UNITS 6 - 7)", vocab: ["Ball", "Car", "Teddy", "Doll", "Scooter", "Train", "Apple", "Banana", "Cookie", "Juice", "Sandwich", "Water"], phonics: ["Letter I - /i/ (Insect)", "Letter J - /j/ (Jellyfish)", "Letter K - /k/ (Kangaroo)", "Letter L - /l/ (Lion)"], struct: ["What toy is it? It's a...", "Do you like (bananas)? I like...", "Where is the (car)? Here!"] },
                "Final test": { subtitle: "MOON 2 FINAL TEST REVIEW (UNITS 6 - 9)", vocab: ["Ball", "Car", "Apple", "Cookie", "Bird", "Cat", "Dog", "Fish", "Crab", "Ocean", "Shell", "Bucket"], phonics: ["Review Letters I to M"], struct: ["Is it a (rabbit)? Yes, it is.", "What can you see? I can see a..."] }
            },
            "Moon 3": {
                "Unit 01": { subtitle: "UNIT 1: HELLO", vocab: ["We are quiet", "We speak English", "We don't fight", "We sit nicely", "We can", "Mommy", "Daddy", "Mimi", "Dylan", "Ferris Wheel", "Ball", "Car", "Doll", "Teddy", "Train", "Scooter"], phonics: ["Letter N - /n/(Nose, Nurse, Nancy Nurse)", "Letter O - /o/(Octopus, on, Oscar Octopus)"], struct: ["Who is this? (This is)....", "Where's the (ball)? Here's the (ball)!"] },
                "Unit 02": { subtitle: "UNIT 2: CLASSROOM", vocab: ["Backpack", "Crayons", "Glue", "Paints", "Paper", "Pencil", "Pencil case", "Scissors", "Cafeteria", "Classroom", "Library", "Playground"], phonics: ["Letter P - /p/(Pen, panda, Penny Panda)", "Letter Q - /k/(Queen, quiet, Queenie Quick)"], struct: ["What do you have? I have...", "Do you have a pencil? Yes/No"] },
                "Unit 03": { subtitle: "UNIT 3: MY BODY", vocab: ["Arms", "Feet", "Hands", "Leg", "Tummy", "fingers", "Toes", "Climb", "Hop", "Jump", "Run"], phonics: ["Letter R - /r/(Rabbit, read, Ricky rabbit)", "Letter S - /s/(Sun, seal, Susie Seal)"], struct: ["What can you do? I can move my (fingers)"] },
                "Unit 04": { subtitle: "UNIT 4: CLOTHES", vocab: ["Coat", "Dress", "Pants", "Shirt", "Shoes", "Skirt", "Socks", "Sweater", "Glove", "Sandals", "Scarf", "T-shirt"], phonics: ["Letter T - /t/(Tiger, teeth, Teddy Tiger)", "Letter U - /u/(Uncle, under, Uncle Utter)"], struct: ["What's this/are these? This is a (skirt). These are (shoes)", "What are you wearing? (I'm wearing) a ..."] },
                "Unit 05": { subtitle: "UNIT 5: HOME", vocab: ["Bathroom", "Bedroom", "Dining room", "Garage", "House", "Kitchen", "Living room", "Yard", "Box", "Closet", "Shelf", "Recycling bin"], phonics: ["Letter V - /v/(Van, Violin)", "Letter W - /w/(Water, Watch)"], struct: ["What room is it? It's....", "Where’s (the box)? In the...."] },
                "Midterm test": { subtitle: "MOON 3 MIDTERM TEST REVIEW (UNITS 1 - 3)", vocab: ["Backpack", "Crayons", "Glue", "Pencil", "Scissors", "Arms", "Feet", "Hands", "Leg", "Tummy", "fingers", "Toes"], phonics: ["Letter N - /n/ (Nose)", "Letter O - /o/ (Octopus)", "Letter P - /p/ (Pen)", "Letter Q - /k/ (Queen)", "Letter R - /r/ (Rabbit)", "Letter S - /s/ (Sun)"], struct: ["What do you have? I have...", "What can you do? I can move my...", "Do you have a pencil?"] },
                "Final test": { subtitle: "MOON 3 FINAL TEST REVIEW (UNITS 1 - 5)", vocab: ["Pencil", "Scissors", "Arms", "Leg", "Coat", "Dress", "Pants", "Kitchen", "Living room", "Bedroom", "Yard"], phonics: ["Review Letters N to W"], struct: ["What are you wearing? I'm wearing...", "Where's the (box)? In the..."] }
            },
            "Moon 4": {
                "Unit 06": { subtitle: "UNIT 6: FOOD", vocab: ["Apples", "Bananas", "Bread", "Carrots", "Cereal", "Eggs", "Ice cream", "Milk", "Pears", "Peas", "Potatoes", "Tomatoes"], phonics: ["Letter V - /v/(Van, victory, Vicky Van)", "Letter W - /w/(Worm, wet, Wendy worm)"], struct: ["What's this? It's…..", "Do you like…? I like/ don't like…."] },
                "Unit 07": { subtitle: "UNIT 7: FARM ANIMALS", vocab: ["Cow", "Duck", "Goat", "Hen", "Horse", "Rooster", "Sheep", "Calf", "Dog", "Puppy", "Foal", "Lamb"], phonics: ["Letter X - /ks/(Fox, box, Felix fox)", "Letter V - /v/(Van, victory, Vicky Van)"], struct: ["What animals is it? Its'….", "There is/are cow(s)."] },
                "Unit 08": { subtitle: "UNIT 8: TRANSPORTATION", vocab: ["Boat", "Bus", "Motorbike", "Plane", "Train", "Truck", "Air", "Road", "Track", "Water", "Bike", "Car"], phonics: ["Letter Y - /y/(Yo-yo, yes, Yester Yo-yo)", "Letter W - /w/(Worm, wet, Wendy worm)"], struct: ["What's it? It's a…..", "Do you want to go by (bus)? Yes/No"] },
                "Unit 09": { subtitle: "UNIT 9: SPACE", vocab: ["Astronaut", "Moon", "Planet", "Rocket", "Star", "Sun", "Day", "Night", "Clouds", "Rainbow", "Sky"], phonics: ["Letter Z - /z/(Zebra, zip, Zeppy Zebra)"], struct: ["What's it? It's a…..", "In the day/night, what can you see?"] },
                "Midterm test": { subtitle: "MOON 4 MIDTERM TEST REVIEW (UNITS 6 - 7)", vocab: ["Apples", "Bananas", "Bread", "Eggs", "Milk", "Cow", "Duck", "Goat", "Hen", "Horse", "Rooster", "Sheep"], phonics: ["Letter V - /v/ (Van)", "Letter W - /w/ (Worm)", "Letter X - /ks/ (Fox)"], struct: ["Do you like...? I like/don't like...", "What animal is it? It's...", "There is/are cow(s)."] },
                "Final test": { subtitle: "MOON 4 FINAL TEST REVIEW (UNITS 6 - 9)", vocab: ["Apples", "Cow", "Duck", "Boat", "Bus", "Motorbike", "Plane", "Astronaut", "Moon", "Planet", "Rocket", "Star"], phonics: ["Review Letters V to Z"], struct: ["Do you want to go by (bus)?", "In the day/night, what can you see?"] }
            },
            "Moon 5": {
                "Unit 02": { subtitle: "UNIT 2: SCHOOL", vocab: ["Colour", "Count", "Draw", "Paint", "Play", "Sing", "Dance", "Jump", "Run", "Think", "Swim", "Walk"], phonics: ["Short vowel a: ham, ram, dam, jam", "Short vowel e: bed, red, leg, egg"], struct: ["What do you do at school? I .... at school.", "Do you want to…? Yes, I do/No, I don't."] },
                "Unit 03": { subtitle: "UNIT 3: THE PARK", vocab: ["Bench", "Flowers", "Grass", "Merry-go-round", "Path", "Pond", "Seesaw", "Slide", "Swing", "Tree", "Leave", "Plants", "Root", "Seed", "Sun", "Water"], phonics: ["Short vowel i: bib, nib, lid, kid", "Short vowel i: lip, rip, hit, sit"], struct: ["There is a (pond).", "There are (trees)."] },
                "Unit 04": { subtitle: "UNIT 4: WILD ANIMALS", vocab: ["Elephant", "Giraffe", "Hippo", "Monkey", "Parrot", "Snake", "Tiger", "Zebra"], phonics: ["Short vowel o: dog, jog, log", "Short vowel o: pot, hot, dot"], struct: ["What's it? It's a…..", "What are those? They're....", "It has (big teeth/big ears/...)."] },
                "Midterm test": { subtitle: "MOON 5 MIDTERM TEST REVIEW (UNITS 2 - 4)", vocab: ["Bench", "Flowers", "Grass", "Elephant", "Giraffe", "Hippo", "Colour", "Count", "Draw"], phonics: ["Short vowels Review"], struct: ["There is a (pond).", "What do you do at school?"] },
                "Final test": { subtitle: "MOON 5 FINAL TEST REVIEW (UNITS 2 - 5)", vocab: ["Bench", "Flowers", "Elephant", "Giraffe", "Colour", "Count", "Draw", "Paint"], phonics: ["Short vowels Review"], struct: ["There is a (pond).", "What do you do at school?"] }
            }
        };

        // Determine Level Key
        let levelKey = "Moon 1";
        const clsLower = (className || "").toLowerCase();
        if (clsLower.includes("moon 2")) levelKey = "Moon 2";
        else if (clsLower.includes("moon 3")) levelKey = "Moon 3";
        else if (clsLower.includes("moon 4")) levelKey = "Moon 4";
        else if (clsLower.includes("moon 5")) levelKey = "Moon 5";
        else if (clsLower.includes("moon 6")) levelKey = "Moon 6";

        // Determine Unit Key
        const tLower = (testName || "").toLowerCase();
        let unitKey = "Unit 01";
        if (tLower.includes("midterm") || tLower.includes("giữa kỳ")) {
            unitKey = "Midterm test";
        } else if (tLower.includes("final") || tLower.includes("cuối kỳ")) {
            unitKey = "Final test";
        } else if (tLower.includes("02") || tLower.includes("2")) unitKey = "Unit 02";
        else if (tLower.includes("03") || tLower.includes("3")) unitKey = "Unit 03";
        else if (tLower.includes("04") || tLower.includes("4")) unitKey = "Unit 04";
        else if (tLower.includes("05") || tLower.includes("5")) unitKey = "Unit 05";
        else if (tLower.includes("06") || tLower.includes("6")) unitKey = "Unit 06";
        else if (tLower.includes("07") || tLower.includes("7")) unitKey = "Unit 07";
        else if (tLower.includes("08") || tLower.includes("8")) unitKey = "Unit 08";
        else if (tLower.includes("09") || tLower.includes("9")) unitKey = "Unit 09";

        const levelData = syllabusMap[levelKey] || syllabusMap["Moon 1"];
        return levelData[unitKey] || levelData["Midterm test"] || levelData["Unit 01"] || syllabusMap["Moon 1"]["Unit 01"];
    },

    renderCommentFieldHTML(s, cmt, idx) {
        const escapedCmt = AuthModule.escapeHtml(cmt || '');
        return `
            <div style="position: relative; width: 100%; min-width: 220px;">
                <div style="display: flex; align-items: center; justify-content: space-between; background: #f8fafc; border: 1.5px solid #cbd5e1; border-bottom: none; border-radius: 6px 6px 0 0; padding: 3px 6px; gap: 4px;">
                    <div style="display: flex; align-items: center; gap: 3px;">
                        <button type="button" onclick="CMPortalModule.formatTextarea('${s.id}', 'bold')" title="In đậm (**văn bản**)" style="padding: 1px 6px; font-size: 11px; font-weight: 900; border: 1px solid #cbd5e1; background: #ffffff; color: #0f172a; border-radius: 4px; cursor: pointer; line-height: 1.2;">B</button>
                        <button type="button" onclick="CMPortalModule.formatTextarea('${s.id}', 'bullet')" title="Thêm gạch đầu dòng (- )" style="padding: 1px 5px; font-size: 11px; font-weight: 700; border: 1px solid #cbd5e1; background: #ffffff; color: #0f172a; border-radius: 4px; cursor: pointer; line-height: 1.2;">• List</button>
                    </div>
                    <button type="button" onclick="CMPortalModule.openRichCommentModal('${s.code}', '${AuthModule.escapeHtml(s.name)}', '${s.id}', ${idx})" title="Mở Cửa Sổ Soạn Nhận Xét Chi Tiết & Chọn Mẫu Nhanh" style="padding: 1px 7px; font-size: 11px; font-weight: 800; border: 1px solid #0284c7; background: #e0f2fe; color: #0369a1; border-radius: 4px; cursor: pointer; display: flex; align-items: center; gap: 3px; line-height: 1.2;">
                        📝 Soạn Chi Tiết
                    </button>
                </div>
                <textarea id="cmt_${s.id}" rows="2" placeholder="Nhận xét bài làm học sinh... (Enter xuống dòng)" oninput="CMPortalModule.autoResizeTextarea(this)" style="width: 100%; min-height: 44px; padding: 5px 8px; border-radius: 0 0 6px 6px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 12.5px; font-weight: 600; font-family: inherit; resize: vertical; box-sizing: border-box; line-height: 1.4;">${escapedCmt}</textarea>
            </div>
        `;
    },

    autoResizeTextarea(textarea) {
        if (!textarea) return;
        textarea.style.height = 'auto';
        textarea.style.height = Math.max(44, textarea.scrollHeight + 2) + 'px';
    },

    formatTextarea(studentId, formatType) {
        const textarea = document.getElementById(`cmt_${studentId}`);
        if (!textarea) return;
        const start = textarea.selectionStart || 0;
        const end = textarea.selectionEnd || 0;
        const val = textarea.value || '';
        const selected = val.substring(start, end);

        if (formatType === 'bold') {
            const replacement = selected ? `**${selected}**` : '**in đậm**';
            textarea.value = val.substring(0, start) + replacement + val.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + 2, start + 2 + (selected ? selected.length : 7));
        } else if (formatType === 'bullet') {
            const prefix = (start > 0 && val[start - 1] !== '\n') ? '\n- ' : '- ';
            const replacement = selected ? selected.split('\n').map(l => l.startsWith('- ') ? l : `- ${l}`).join('\n') : prefix;
            textarea.value = val.substring(0, start) + replacement + val.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + replacement.length, start + replacement.length);
        } else if (formatType === 'italic') {
            const replacement = selected ? `*${selected}*` : '*in nghiêng*';
            textarea.value = val.substring(0, start) + replacement + val.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + 1, start + 1 + (selected ? selected.length : 10));
        }
        this.autoResizeTextarea(textarea);
    },

    openRichCommentModal(studentCode, studentName, studentId, studentIndex) {
        this.currentRichStudentIndex = studentIndex;
        const currentCmt = document.getElementById(`cmt_${studentId}`)?.value || '';

        let modal = document.getElementById('rich-comment-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'rich-comment-modal';
            document.body.appendChild(modal);
        }

        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.background = 'rgba(15, 23, 42, 0.85)';
        modal.style.backdropFilter = 'blur(8px)';
        modal.style.webkitBackdropFilter = 'blur(8px)';
        modal.style.zIndex = '999999';

        const testName = this.selectedTestName || 'Unit 01';
        const className = this.selectedClassName || '';

        const quickTemplates = [
            "🌟 Con tiếp thu bài rất nhanh, làm bài cẩn thận và phát âm chuẩn.",
            "📚 Nắm vững từ vựng & ngữ pháp, làm bài tự tin.",
            "✏️ Cần chú ý ôn lại cấu trúc ngữ pháp và làm bài cẩn thận hơn.",
            "👂 Cần luyện tập thêm kỹ năng Nghe và chú ý âm cuối (ending sounds).",
            "💡 Con phát biểu hăng hái trên lớp, bài kiểm tra đạt kết quả rất xuất sắc!"
        ];

        modal.innerHTML = `
            <div class="modal-content" style="max-width: 820px; width: 94vw; max-height: 90vh; display: flex; flex-direction: column; padding: 22px 26px; border-radius: 16px; border: 2px solid #cbd5e1; background: #ffffff; color: #0f172a; box-shadow: 0 25px 60px rgba(0,0,0,0.35); font-family: 'Montserrat', sans-serif;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; margin-bottom: 14px;">
                    <div>
                        <h3 style="margin: 0; color: #0f172a; font-size: 18px; font-weight: 900; display: flex; align-items: center; gap: 8px;">
                            📝 SOẠN NHẬN XÉT CHI TIẾT BÀI THI
                        </h3>
                        <div style="font-size: 13px; color: #475569; margin-top: 4px; font-weight: 600;">
                            Học sinh: <strong style="color: #0284c7; font-size: 14px;">${AuthModule.escapeHtml(studentName)}</strong> (${studentCode}) | Lớp: <strong style="color: #16a34a; font-size: 14px;">${className}</strong> | Bài Test: <strong style="color: #d97706; font-size: 14px;">${testName}</strong>
                        </div>
                    </div>
                    <button onclick="CMPortalModule.closeRichCommentModal();" style="background: #f1f5f9; border: 1px solid #cbd5e1; color: #475569; width: 32px; height: 32px; border-radius: 50%; font-size: 18px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center;" title="Đóng modal">&times;</button>
                </div>

                <div style="flex: 1; overflow-y: auto; padding-right: 4px; display: flex; flex-direction: column; gap: 14px;">
                    <!-- Quick Templates -->
                    <div>
                        <label style="font-size: 12px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px;">
                            ⚡ Mẫu nhận xét nhanh (bấm 1-click để chèn vào bài viết):
                        </label>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                            ${quickTemplates.map(tpl => `
                                <button type="button" onclick="CMPortalModule.applyQuickTemplate('${studentId}', '${AuthModule.escapeHtml(tpl)}')" style="background: #f0f9ff; border: 1px solid #bae6fd; color: #0369a1; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.15s; text-align: left;" onmouseover="this.style.background='#e0f2fe'" onmouseout="this.style.background='#f0f9ff'">
                                    ${AuthModule.escapeHtml(tpl)}
                                </button>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Format Toolbar & Textarea -->
                    <div>
                        <div style="display: flex; align-items: center; justify-content: space-between; background: #f8fafc; border: 1.5px solid #cbd5e1; border-bottom: none; border-radius: 8px 8px 0 0; padding: 6px 12px;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <button type="button" onclick="CMPortalModule.formatRichModalTextarea('${studentId}', 'bold')" style="padding: 3px 10px; font-size: 12px; font-weight: 900; border: 1px solid #cbd5e1; background: #ffffff; color: #0f172a; border-radius: 4px; cursor: pointer;">B (In đậm)</button>
                                <button type="button" onclick="CMPortalModule.formatRichModalTextarea('${studentId}', 'italic')" style="padding: 3px 10px; font-size: 12px; font-weight: 700; font-style: italic; border: 1px solid #cbd5e1; background: #ffffff; color: #0f172a; border-radius: 4px; cursor: pointer;">I (In nghiêng)</button>
                                <button type="button" onclick="CMPortalModule.formatRichModalTextarea('${studentId}', 'bullet')" style="padding: 3px 10px; font-size: 12px; font-weight: 700; border: 1px solid #cbd5e1; background: #ffffff; color: #0f172a; border-radius: 4px; cursor: pointer;">• Gạch đầu dòng</button>
                            </div>
                            <span style="font-size: 11.5px; color: #64748b; font-weight: 600;">Xuống dòng bằng Enter</span>
                        </div>
                        <textarea id="rich_cmt_input" rows="5" placeholder="Gõ hoặc chọn mẫu nhận xét bài thi cho học sinh..." oninput="CMPortalModule.syncRichModalTextarea('${studentId}')" style="width: 100%; padding: 10px 12px; border-radius: 0 0 8px 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 13.5px; font-weight: 600; font-family: inherit; resize: vertical; box-sizing: border-box; line-height: 1.5;">${AuthModule.escapeHtml(currentCmt)}</textarea>
                    </div>

                    <!-- Live PDF Preview Box -->
                    <div style="border: 1.5px solid #e2e8f0; border-radius: 8px; background: #f8fafc; padding: 12px;">
                        <div style="font-size: 11.5px; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                            <span>👁️ Xem trước nhận xét hiển thị trên File PDF:</span>
                        </div>
                        <div id="rich_cmt_preview" style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px 14px; min-height: 50px; font-size: 13.5px; color: #0f172a; line-height: 1.5;">
                            ${this.renderPreviewHTML(currentCmt)}
                        </div>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 2px solid #f1f5f9; padding-top: 14px; margin-top: 14px;">
                    <button type="button" onclick="CMPortalModule.navigateRichModalStudent(-1)" ${studentIndex === 0 ? 'disabled style="opacity: 0.5; cursor: not-allowed; padding: 8px 16px; border-radius: 8px; border: 1px solid #cbd5e1; background: #f1f5f9; font-weight: 700;"' : 'style="padding: 8px 16px; border-radius: 8px; border: 1px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700; cursor: pointer;"'}>
                        ⬅️ HS Trước
                    </button>
                    <button type="button" onclick="CMPortalModule.closeRichCommentModal()" style="background: #0284c7; color: #ffffff; border: none; padding: 9px 24px; font-size: 13.5px; font-weight: 800; border-radius: 8px; cursor: pointer; box-shadow: 0 2px 8px rgba(2,132,199,0.3);">
                        ✅ Hoàn Tất & Đóng
                    </button>
                    <button type="button" onclick="CMPortalModule.navigateRichModalStudent(1)" ${studentIndex >= (this.studentsInClass ? this.studentsInClass.length - 1 : 0) ? 'disabled style="opacity: 0.5; cursor: not-allowed; padding: 8px 16px; border-radius: 8px; border: 1px solid #cbd5e1; background: #f1f5f9; font-weight: 700;"' : 'style="padding: 8px 16px; border-radius: 8px; border: 1px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700; cursor: pointer;"'}>
                        HS Tiếp ➡️
                    </button>
                </div>
            </div>
        `;

        if (window.Dashboard && typeof window.Dashboard.pushModalState === 'function') {
            window.Dashboard.pushModalState('rich-comment-modal', () => {
                const el = document.getElementById('rich-comment-modal');
                if (el) el.style.display = 'none';
            });
        }
    },

    closeRichCommentModal() {
        const modal = document.getElementById('rich-comment-modal');
        if (modal) modal.style.display = 'none';
        if (window.Dashboard && typeof window.Dashboard.closeModal === 'function') {
            window.Dashboard.closeModal();
        }
    },

    syncRichModalTextarea(studentId) {
        const richInput = document.getElementById('rich_cmt_input');
        const mainInput = document.getElementById(`cmt_${studentId}`);
        if (!richInput) return;
        const val = richInput.value;
        if (mainInput) {
            mainInput.value = val;
            this.autoResizeTextarea(mainInput);
        }
        const preview = document.getElementById('rich_cmt_preview');
        if (preview) {
            preview.innerHTML = this.renderPreviewHTML(val);
        }
    },

    applyQuickTemplate(studentId, tplText) {
        const richInput = document.getElementById('rich_cmt_input');
        if (!richInput) return;
        const curVal = richInput.value.trim();
        richInput.value = curVal ? `${curVal}\n${tplText}` : tplText;
        this.syncRichModalTextarea(studentId);
    },

    formatRichModalTextarea(studentId, formatType) {
        const textarea = document.getElementById('rich_cmt_input');
        if (!textarea) return;
        const start = textarea.selectionStart || 0;
        const end = textarea.selectionEnd || 0;
        const val = textarea.value || '';
        const selected = val.substring(start, end);

        if (formatType === 'bold') {
            const replacement = selected ? `**${selected}**` : '**in đậm**';
            textarea.value = val.substring(0, start) + replacement + val.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + 2, start + 2 + (selected ? selected.length : 7));
        } else if (formatType === 'italic') {
            const replacement = selected ? `*${selected}*` : '*in nghiêng*';
            textarea.value = val.substring(0, start) + replacement + val.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + 1, start + 1 + (selected ? selected.length : 10));
        } else if (formatType === 'bullet') {
            const prefix = (start > 0 && val[start - 1] !== '\n') ? '\n- ' : '- ';
            const replacement = selected ? selected.split('\n').map(l => l.startsWith('- ') ? l : `- ${l}`).join('\n') : prefix;
            textarea.value = val.substring(0, start) + replacement + val.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + replacement.length, start + replacement.length);
        }
        this.syncRichModalTextarea(studentId);
    },

    renderPreviewHTML(rawText) {
        if (!rawText || !rawText.trim()) {
            return '<em style="color: #94a3b8;">(Xem trước hiển thị nhận xét trên giấy PDF...)</em>';
        }
        let html = AuthModule.escapeHtml(rawText);
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        const lines = html.split('\n');
        const formatted = lines.map(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
                return `<div style="padding-left: 10px; margin-top: 3px; display: flex; align-items: flex-start;"><span style="margin-right: 6px; font-weight: bold; color: #0284c7;">•</span><span>${trimmed.substring(2)}</span></div>`;
            }
            return line;
        }).join('<br>');
        return formatted;
    },

    navigateRichModalStudent(offset) {
        if (!this.studentsInClass || this.studentsInClass.length === 0) return;
        const newIdx = (this.currentRichStudentIndex || 0) + offset;
        if (newIdx < 0 || newIdx >= this.studentsInClass.length) return;

        const nextStudent = this.studentsInClass[newIdx];
        if (nextStudent) {
            this.openRichCommentModal(nextStudent.code, nextStudent.name, nextStudent.id, newIdx);
        }
    },

    openMoonDetailModal(studentCode, studentName, studentId) {
        const testName = this.selectedTestName || 'Unit 01';
        const className = this.selectedClassName || '';

        const sylData = this.getMoonSyllabusData(className, testName);
        const vocabItems = sylData.vocab;
        const phonicsItems = sylData.phonics;
        const structItems = sylData.struct;

        let modal = document.getElementById('moon-detail-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'moon-detail-modal';
            document.body.appendChild(modal);
        }

        // Apply mandatory centering styles directly
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.background = 'rgba(15, 23, 42, 0.85)';
        modal.style.backdropFilter = 'blur(8px)';
        modal.style.webkitBackdropFilter = 'blur(8px)';
        modal.style.zIndex = '999999';

        const buildRows = (items, categoryName, categoryBg) => {
            return items.map((item, idx) => `
                <tr style="border-bottom: 1px solid #e2e8f0; background: ${idx % 2 === 0 ? '#ffffff' : '#f8fafc'}; transition: background 0.15s;">
                    ${idx === 0 ? `<td rowspan="${items.length}" style="background: ${categoryBg}; color: #ffffff; font-weight: 800; text-align: center; vertical-align: middle; padding: 12px 10px; font-size: 13.5px; border-right: 2px solid #cbd5e1;">${categoryName}</td>` : ''}
                    <td style="padding: 10px 14px; font-weight: 700; font-size: 13.5px; color: #0f172a; border-right: 1px solid #e2e8f0;">${AuthModule.escapeHtml(item)}</td>
                    <td style="text-align: center; padding: 10px; border-right: 1px solid #e2e8f0;"><input type="radio" name="m_level_${studentId}_${categoryName}_${idx}" value="excellent" style="accent-color: #16a34a; transform: scale(1.35); cursor: pointer;"></td>
                    <td style="text-align: center; padding: 10px; border-right: 1px solid #e2e8f0;"><input type="radio" name="m_level_${studentId}_${categoryName}_${idx}" value="satisfactory" style="accent-color: #d97706; transform: scale(1.35); cursor: pointer;"></td>
                    <td style="text-align: center; padding: 10px;"><input type="radio" name="m_level_${studentId}_${categoryName}_${idx}" value="support" style="accent-color: #dc2626; transform: scale(1.35); cursor: pointer;"></td>
                </tr>
            `).join('');
        };

        modal.innerHTML = `
            <div class="modal-content" style="max-width: 840px; width: 94vw; max-height: 88vh; display: flex; flex-direction: column; padding: 22px 26px; border-radius: 16px; border: 2px solid #cbd5e1; background: #ffffff; color: #0f172a; box-shadow: 0 25px 60px rgba(0,0,0,0.35); animation: fadeIn 0.2s ease-out; font-family: 'Montserrat', sans-serif;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; margin-bottom: 14px;">
                    <div>
                        <h3 style="margin: 0; color: #0f172a; font-size: 19px; font-weight: 900; display: flex; align-items: center; gap: 8px;">
                            📝 BẢNG ĐÁNH GIÁ TỪ VỰNG THỦ CÔNG - MOON UNIT TEST
                        </h3>
                        <div style="font-size: 13px; color: #475569; margin-top: 4px; font-weight: 600;">
                            Học sinh: <strong style="color: #0284c7; font-size: 14px;">${AuthModule.escapeHtml(studentName)}</strong> (${studentCode}) | Lớp: <strong style="color: #16a34a; font-size: 14px;">${className}</strong> | Bài Test: <strong style="color: #d97706; font-size: 14px;">${testName}</strong>
                        </div>
                    </div>
                    <button onclick="CMPortalModule.closeMoonDetailModal();" style="background: #f1f5f9; border: 1px solid #cbd5e1; color: #475569; width: 32px; height: 32px; border-radius: 50%; font-size: 18px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center;" title="Đóng modal">&times;</button>
                </div>

                <div style="flex: 1; overflow-y: auto; padding-right: 4px; margin-bottom: 14px; border: 1.5px solid #cbd5e1; border-radius: 10px; background: #ffffff;">
                    <table class="data-table" style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <thead>
                            <tr style="background: #f8fafc; color: #0f172a; text-align: center; position: sticky; top: 0; z-index: 2; border-bottom: 2px solid #cbd5e1;">
                                <th style="padding: 11px 10px; width: 15%; font-weight: 800; border-right: 1px solid #cbd5e1; color: #0f172a;">Danh mục</th>
                                <th style="padding: 11px 12px; text-align: left; font-weight: 800; border-right: 1px solid #cbd5e1; color: #0f172a;">Nội dung kiểm tra (Content)</th>
                                <th style="padding: 11px 10px; width: 19%; color: #15803d; font-weight: 800; border-right: 1px solid #cbd5e1;">🌟 EXCELLENT (2Đ)</th>
                                <th style="padding: 11px 10px; width: 19%; color: #b45309; font-weight: 800; border-right: 1px solid #cbd5e1;">🟡 SATISFACTORY (1Đ)</th>
                                <th style="padding: 11px 10px; width: 19%; color: #b91c1c; font-weight: 800;">🔴 NEED SUPPORT (0Đ)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${buildRows(vocabItems, 'Vocabulary', '#4d7c0f')}
                            ${buildRows(phonicsItems, 'Phonics', '#c2410c')}
                            ${buildRows(structItems, 'Structures', '#7e22ce')}
                        </tbody>
                    </table>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; background: #f8fafc; padding: 12px 18px; border-radius: 10px; border: 1px solid #e2e8f0;">
                    <div style="font-size: 12.5px; color: #475569; font-weight: 600;">
                        💡 <i>Tích chọn mức độ cho từng từ ➔ Bấm <b>Lưu Đánh Giá</b> để quy đổi điểm & in Báo cáo PDF.</i>
                    </div>
                    <div style="display: flex; gap: 12px;">
                        <button class="btn" onclick="CMPortalModule.closeMoonDetailModal();" style="padding: 8px 20px; font-weight: 700; background: #ffffff; color: #475569; border: 1.5px solid #cbd5e1; border-radius: 8px; cursor: pointer;">Hủy</button>
                        <button class="btn btn-primary" onclick="CMPortalModule.saveMoonDetailEvaluation('${studentId}', ${vocabItems.length + phonicsItems.length + structItems.length});" style="background: #16a34a; color: #ffffff; border: none; padding: 8px 24px; font-weight: 800; border-radius: 8px; box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3); cursor: pointer;">
                            💾 Lưu Đánh Giá
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    closeMoonDetailModal() {
        const modal = document.getElementById('moon-detail-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    },

    saveMoonDetailEvaluation(studentId, totalItemsCount) {
        // Count Excellent & Satisfactory
        const radios = document.querySelectorAll(`input[name^="m_level_${studentId}_"]`);
        let excCount = 0;
        let satCount = 0;

        radios.forEach(r => {
            if (r.checked) {
                if (r.value === 'excellent') excCount++;
                else if (r.value === 'satisfactory') satCount++;
            }
        });

        const totalCorr = excCount + satCount;
        const vocabInput = document.getElementById(`vocab_q_${studentId}`);
        const totVocabInput = document.getElementById('tot_vocab_q');

        if (totVocabInput) totVocabInput.value = totalItemsCount;
        if (vocabInput) {
            vocabInput.value = totalCorr;
            this.calcRowGrade10(studentId);
        }

        this.closeMoonDetailModal();
        App.showToast(`✅ Đã lưu đánh giá chi tiết (${excCount} Xuất sắc, ${satCount} Đạt)!`, 'success');
    },

    exportStudentUnitTestPdf(studentCode, studentName, studentId) {
        const testName = this.selectedTestName || 'Unit 01';
        const className = this.selectedClassName || '';
        const isMoon = className.toLowerCase().startsWith('moon');

        const datePicker = document.getElementById('grade-test-date-picker');
        const examDate = datePicker ? datePicker.value : new Date().toISOString().split('T')[0];

        if (isMoon) {
            const totVocab = parseFloat(document.getElementById('tot_vocab_q')?.value || 17);
            const corrVocab = parseFloat(document.getElementById(`vocab_q_${studentId}`)?.value || 15);
            const phonics = parseFloat(document.getElementById(`phonics_${studentId}`)?.value || 9.0);
            const comment = document.getElementById(`cmt_${studentId}`)?.value || '';

            const url = `/api/students/${studentCode}/test-report-pdf?is_moon=1&test_name=${encodeURIComponent(testName)}&class_name=${encodeURIComponent(className)}&exam_date=${encodeURIComponent(examDate)}&tot_vocab=${totVocab}&corr_vocab=${corrVocab}&phonics=${phonics}&comment=${encodeURIComponent(comment)}`;
            window.open(url, '_blank');
            return;
        }
        
        const totLis = parseFloat(document.getElementById('tot_lis_q')?.value || 0);
        const totRw = parseFloat(document.getElementById('tot_rw_q')?.value || 0);
        const corrLis = parseFloat(document.getElementById(`lis_q_${studentId}`)?.value || 0);
        const corrRw = parseFloat(document.getElementById(`rw_q_${studentId}`)?.value || 0);
        const comment = document.getElementById(`cmt_${studentId}`)?.value || '';

        const url = `/api/students/${studentCode}/test-report-pdf?test_name=${encodeURIComponent(testName)}&class_name=${encodeURIComponent(className)}&exam_date=${encodeURIComponent(examDate)}&tot_lis=${totLis}&tot_rw=${totRw}&corr_lis=${corrLis}&corr_rw=${corrRw}&comment=${encodeURIComponent(comment)}`;
        window.open(url, '_blank');
    },

    handleTestNameChange(testVal) {
        this.loadGradesForTest(this.selectedClassName, testVal);
    },

    async saveGrades() {
        if (!AuthModule.isLoggedIn()) {
            App.showToast('Vui lòng đăng nhập tài khoản để thực hiện nhập điểm.', 'warning');
            AuthModule.showLoginModal();
            return;
        }

        const testName = this.selectedTestName || 'Unit 01';
        const className = this.selectedClassName || '';
        const isMoon = className.toLowerCase().startsWith('moon');
        const gradeList = [];

        const totLisInput = document.getElementById('tot_lis_q');
        const totRwInput = document.getElementById('tot_rw_q');
        const totSpkInput = document.getElementById('tot_spk_q');
        const totVocabInput = document.getElementById('tot_vocab_q');

        const totLisVal = totLisInput ? totLisInput.value.trim() : '';
        const totRwVal = totRwInput ? totRwInput.value.trim() : '';
        const totSpkVal = totSpkInput ? totSpkInput.value.trim() : '';
        const totVocabVal = totVocabInput ? totVocabInput.value.trim() : '';

        this.studentsInClass.forEach(s => {
            if (isMoon) {
                const vocabInput = document.getElementById(`vocab_q_${s.id}`);
                const phonicsInput = document.getElementById(`phonics_${s.id}`);
                const cmtInput = document.getElementById(`cmt_${s.id}`);

                gradeList.push({
                    code: s.code,
                    name: s.name,
                    english_name: s.english_name || '',
                    class_name: className,
                    test_name: testName,
                    listening: '',
                    reading_writing: vocabInput ? vocabInput.value : '',
                    speaking: phonicsInput ? phonicsInput.value : '',
                    reading_writing_max: totVocabVal,
                    comment: cmtInput ? cmtInput.value.trim() : ''
                });
            } else {
                const lisInput = document.getElementById(`lis_q_${s.id}`);
                const rwInput = document.getElementById(`rw_q_${s.id}`);
                const spkInput = document.getElementById(`spk_q_${s.id}`);
                const cmtInput = document.getElementById(`cmt_${s.id}`);

                gradeList.push({
                    code: s.code,
                    name: s.name,
                    english_name: s.english_name || '',
                    class_name: className,
                    test_name: testName,
                    listening: lisInput ? lisInput.value : '',
                    reading_writing: rwInput ? rwInput.value : '',
                    speaking: spkInput ? spkInput.value : '',
                    listening_max: totLisVal,
                    reading_writing_max: totRwVal,
                    speaking_max: totSpkVal,
                    comment: cmtInput ? cmtInput.value.trim() : ''
                });
            }
        });

        try {
            const res = await API.saveGrades(gradeList);
            if (res.success) {
                App.showToast(`Lưu điểm thành công bài '${testName}' cho lớp ${this.selectedClassName}!`, 'success');
            } else {
                App.showToast(res.error || 'Lưu điểm thất bại', 'error');
            }
        } catch (e) {
            App.showToast(e.message || 'Lỗi kết nối máy chủ', 'error');
        }
    },

    exportClassReport() {
        const className = this.selectedClassName || 'Tất cả';
        const datePicker = document.getElementById('attendance-date-picker');
        const dateVal = datePicker ? datePicker.value : (this.selectedAttendanceDate || new Date().toISOString().split('T')[0]);

        const reportData = [];
        let totalCount = 0;
        let presentCount = 0;
        let submittedHwCount = 0;
        let scoreSum = 0;
        let scoredStudentsCount = 0;

        const collectRow = (s, isGuest = false) => {
            totalCount++;
            const rowId = isGuest ? `guest_${s.code}` : s.id;
            const attSelect = document.getElementById(`att_select_${rowId}`);
            const noteInput = document.getElementById(`note_${rowId}`);
            const hwCorrInput = document.getElementById(`hw_corr_${rowId}`);
            const hwTotInput = document.getElementById(`hw_tot_${rowId}`);
            const hwStatusSelect = document.getElementById(`hw_status_${rowId}`);
            const hwCommentInput = document.getElementById(`hw_comment_${rowId}`);

            const attStatus = attSelect ? attSelect.value : 'Có mặt';
            const attNote = noteInput ? noteInput.value.trim() : '';
            const hwCorrStr = hwCorrInput ? hwCorrInput.value.trim() : '';
            const hwTotStr = hwTotInput ? hwTotInput.value.trim() : '';
            const hwStatus = hwStatusSelect ? hwStatusSelect.value : 'Nộp đúng giờ';
            const hwComment = hwCommentInput ? hwCommentInput.value.trim() : '';

            if (attStatus === 'Có mặt') presentCount++;
            if (hwStatus === 'Nộp đúng giờ' || hwStatus === 'Nộp muộn') submittedHwCount++;

            let calcScore = null;
            if (hwCorrStr !== '' && hwTotStr !== '') {
                const cVal = parseFloat(hwCorrStr);
                const tVal = parseFloat(hwTotStr);
                if (!isNaN(cVal) && !isNaN(tVal) && tVal > 0) {
                    calcScore = Math.round((cVal / tVal) * 100) / 10;
                    scoreSum += calcScore;
                    scoredStudentsCount++;
                }
            }

            reportData.push({
                stt: totalCount,
                code: s.code || '—',
                name: s.name || '',
                english_name: s.english_name || '',
                att_status: attStatus,
                att_note: attNote,
                hw_corr: hwCorrStr,
                hw_tot: hwTotStr,
                hw_score: calcScore !== null ? calcScore.toFixed(1) : '—',
                hw_status: hwStatus,
                hw_comment: hwComment,
                is_guest: isGuest
            });
        };

        this.studentsInClass.forEach(s => collectRow(s, false));
        this.addedGuestStudents.forEach(g => collectRow(g, true));

        if (reportData.length === 0) {
            App.showToast('Không có dữ liệu học sinh trong lớp để xuất báo cáo.', 'warning');
            return;
        }

        const avgScoreStr = scoredStudentsCount > 0 ? (Math.round((scoreSum / scoredStudentsCount) * 10) / 10).toFixed(1) : '—';

        let formattedDate = dateVal;
        const dParts = dateVal.split('-');
        if (dParts.length === 3) formattedDate = `${dParts[2]}/${dParts[1]}/${dParts[0]}`;

        this.activeReportContext = {
            className,
            dateVal,
            formattedDate,
            reportData,
            totalCount,
            presentCount,
            submittedHwCount,
            avgScoreStr
        };

        this.showReportModal();
    },

    showReportModal() {
        const ctx = this.activeReportContext;
        if (!ctx) return;

        let modal = document.getElementById('cm-report-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'cm-report-modal';
            modal.style.cssText = 'position: fixed; inset: 0; z-index: 9999; background: rgba(15, 23, 42, 0.55); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.2s ease-out;';
            document.body.appendChild(modal);
        }

        let tableRowsHtml = ctx.reportData.map((r, idx) => {
            let attBadge = '';
            if (r.att_status === 'Có mặt') {
                attBadge = `<span style="display: inline-block; background: #d1fae5; color: #047857; border: 1px solid #6ee7b7; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11.5px;">✓ Có mặt</span>`;
            } else if (r.att_status === 'Vắng có phép') {
                attBadge = `<span style="display: inline-block; background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11.5px;">⚠️ Vắng có phép</span>`;
            } else if (r.att_status === 'Vắng không phép') {
                attBadge = `<span style="display: inline-block; background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11.5px;">❌ Vắng KP</span>`;
            } else {
                attBadge = `<span style="display: inline-block; background: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11.5px;">${AuthModule.escapeHtml(r.att_status)}</span>`;
            }

            let hwBadge = '';
            const hwStr = r.hw_status || '';
            if (hwStr.includes('đúng hạn') || hwStr.includes('Đã nộp') || hwStr.includes('Đúng hạn')) {
                hwBadge = `<span style="display: inline-block; background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; padding: 3px 9px; border-radius: 6px; font-weight: 700; font-size: 11.5px;">${AuthModule.escapeHtml(hwStr)}</span>`;
            } else if (hwStr.includes('muộn')) {
                hwBadge = `<span style="display: inline-block; background: #fffbeb; color: #b45309; border: 1px solid #fde68a; padding: 3px 9px; border-radius: 6px; font-weight: 700; font-size: 11.5px;">${AuthModule.escapeHtml(hwStr)}</span>`;
            } else if (hwStr.includes('Chưa nộp')) {
                hwBadge = `<span style="display: inline-block; background: #fef2f2; color: #b91c1c; border: 1px solid #fca5a5; padding: 3px 9px; border-radius: 6px; font-weight: 700; font-size: 11.5px;">${AuthModule.escapeHtml(hwStr)}</span>`;
            } else {
                hwBadge = `<span style="color: #475569; font-weight: 600; font-size: 11.5px;">${AuthModule.escapeHtml(hwStr || '—')}</span>`;
            }

            const rowBg = r.is_guest 
                ? 'background: #fffbe6; border-left: 3.5px solid #d97706;' 
                : (idx % 2 === 0 ? 'background: #ffffff;' : 'background: #f8fafc;');

            return `
                <tr style="border-bottom: 1px solid #e2e8f0; ${rowBg} transition: background 0.15s ease;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='${r.is_guest ? '#fffbe6' : (idx % 2 === 0 ? '#ffffff' : '#f8fafc')}'">
                    <td style="padding: 11px 8px; text-align: center; color: #64748b; font-weight: 700; font-size: 12px;">${r.stt}</td>
                    <td style="padding: 11px 8px;">
                        <span style="font-weight: 800; color: #0284c7; font-size: 11.5px; background: #e0f2fe; padding: 3px 8px; border-radius: 5px; border: 1px solid #7dd3fc; display: inline-block;">
                            ${AuthModule.escapeHtml(r.code)}
                        </span>
                    </td>
                    <td style="padding: 11px 8px;">
                        <div style="font-weight: 800; color: #0f172a; font-size: 13px;">${AuthModule.escapeHtml(r.name)}</div>
                        ${r.english_name ? `<div style="font-size: 11px; color: #64748b; margin-top: 1px;">(${AuthModule.escapeHtml(r.english_name)})</div>` : ''}
                    </td>
                    <td style="padding: 11px 8px;">
                        ${attBadge}
                        ${r.att_note ? `<div style="font-size: 10.5px; color: #d97706; margin-top: 2px; font-weight: 600;">(${AuthModule.escapeHtml(r.att_note)})</div>` : ''}
                    </td>
                    <td style="padding: 11px 8px; text-align: center;">
                        ${r.hw_score !== '—' ? `<span style="font-weight: 900; color: #047857; background: #d1fae5; padding: 4px 10px; border-radius: 8px; border: 1px solid #6ee7b7; font-size: 13px;">${r.hw_score}đ</span>` : '<span style="color: #94a3b8; font-size: 13px; font-weight: 700;">—</span>'}
                    </td>
                    <td style="padding: 11px 8px;">
                        ${hwBadge}
                    </td>
                    <td style="padding: 11px 8px; color: #334155; font-size: 12.5px; line-height: 1.45; font-weight: 500;">
                        ${r.hw_comment ? AuthModule.escapeHtml(r.hw_comment) : '<span style="color: #94a3b8; font-style: italic;">Chưa có nhận xét</span>'}
                    </td>
                </tr>
            `;
        }).join('');

        modal.innerHTML = `
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 18px; width: 100%; max-width: 1100px; max-height: 92vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);">
                <!-- Header -->
                <div style="padding: 18px 24px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h3 style="margin: 0; font-size: 17px; font-weight: 900; color: #0f172a; display: flex; align-items: center; gap: 10px; letter-spacing: 0.2px;">
                            <span style="font-size: 20px;">📊</span> BÁO CÁO TỔNG HỢP ĐIỂM & NHẬN XÉT BTVN
                        </h3>
                        <div style="font-size: 12.5px; color: #64748b; margin-top: 4px; display: flex; align-items: center; gap: 12px;">
                            <span>🏫 Lớp: <strong style="color: #0284c7; font-weight: 800; background: #e0f2fe; padding: 2px 8px; border-radius: 5px; border: 1px solid #bae6fd;">${AuthModule.escapeHtml(ctx.className)}</strong></span>
                            <span style="color: #cbd5e1;">|</span>
                            <span>📅 Ngày học: <strong style="color: #b45309; font-weight: 800; background: #fef3c7; padding: 2px 8px; border-radius: 5px; border: 1px solid #fde68a;">${ctx.formattedDate}</strong></span>
                        </div>
                    </div>
                    <button onclick="CMPortalModule.closeReportModal();" style="background: #f1f5f9; border: 1px solid #cbd5e1; color: #475569; font-size: 16px; cursor: pointer; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; transition: all 0.2s;" onmouseover="this.style.background='#fee2e2'; this.style.color='#dc2626';" onmouseout="this.style.background='#f1f5f9'; this.style.color='#475569';">✕</button>
                </div>

                <!-- Stat Cards Row -->
                <div style="padding: 14px 24px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
                    <div style="background: #ffffff; border: 1.5px solid #cbd5e1; padding: 10px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px;">👥 Sĩ Số Lớp</div>
                        <div style="font-size: 18px; font-weight: 900; color: #0f172a; margin-top: 2px;">${ctx.totalCount} HS</div>
                    </div>

                    <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 10px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 11px; color: #047857; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px;">🟢 Có Mặt</div>
                        <div style="font-size: 18px; font-weight: 900; color: #047857; margin-top: 2px;">${ctx.presentCount} HS</div>
                    </div>

                    <div style="background: #eff6ff; border: 1.5px solid #bfdbfe; padding: 10px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 11px; color: #1d4ed8; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px;">📝 Nộp BTVN</div>
                        <div style="font-size: 18px; font-weight: 900; color: #1d4ed8; margin-top: 2px;">${ctx.submittedHwCount} / ${ctx.totalCount} HS</div>
                    </div>

                    <div style="background: #fffbeb; border: 1.5px solid #fde68a; padding: 10px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size: 11px; color: #b45309; text-transform: uppercase; font-weight: 800; letter-spacing: 0.5px;">⭐ Điểm TB Cả Lớp</div>
                        <div style="font-size: 18px; font-weight: 900; color: #b45309; margin-top: 2px;">${ctx.avgScoreStr} <span style="font-size: 12px; color: #78350f; font-weight: 600;">/ 10đ</span></div>
                    </div>
                </div>

                <!-- Table Content -->
                <div style="flex: 1; overflow-y: auto; padding: 0;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12.5px; table-layout: fixed;">
                        <thead>
                            <tr style="background: #f8fafc; color: #0f172a; text-align: left; position: sticky; top: 0; z-index: 10; border-bottom: 2px solid #cbd5e1; font-weight: 800; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.5px;">
                                <th style="padding: 12px 8px; width: 42px; text-align: center; color: #475569;">STT</th>
                                <th style="padding: 12px 8px; width: 90px; color: #0284c7;">Mã HS</th>
                                <th style="padding: 12px 8px; width: 175px; color: #0f172a;">Họ Và Tên</th>
                                <th style="padding: 12px 8px; width: 130px; color: #047857;">Điểm Danh</th>
                                <th style="padding: 12px 8px; width: 90px; text-align: center; color: #b45309;">Điểm</th>
                                <th style="padding: 12px 8px; width: 135px; color: #1d4ed8;">Tình Trạng BVN</th>
                                <th style="padding: 12px 8px; color: #334155;">Nhận Xét Bài Về Nhà Học Viên</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRowsHtml}
                        </tbody>
                    </table>
                </div>

                <!-- Footer -->
                <div style="padding: 16px 24px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <button class="btn" onclick="CMPortalModule.exportReportPDF();" style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; border: none; padding: 9px 18px; font-weight: 800; font-size: 12.5px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(16,185,129,0.25);">
                            📄 Tải Báo Cáo PDF
                        </button>
                        <button class="btn" onclick="CMPortalModule.downloadReportCSV();" style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #ffffff; border: none; padding: 9px 18px; font-weight: 800; font-size: 12.5px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(37,99,235,0.25);">
                            📥 Tải File Báo Cáo CSV / Excel
                        </button>
                    </div>
                    <button class="btn" onclick="CMPortalModule.closeReportModal();" style="padding: 9px 22px; font-weight: 800; font-size: 12.5px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #334155; border-radius: 8px; cursor: pointer;">
                        Đóng
                    </button>
                </div>
            </div>
        `;
        modal.style.display = 'flex';
    },

    closeReportModal() {
        const modal = document.getElementById('cm-report-modal');
        if (modal) modal.style.display = 'none';
    },

    exportReportPDF() {
        const ctx = this.activeReportContext;
        if (!ctx) return;

        // Open print-friendly A4 PDF layout window
        const printWindow = window.open('', '_blank', 'width=950,height=800');
        if (!printWindow) {
            App.showToast('Vui lòng cho phép trình duyệt bật Cửa sổ Popup để xuất PDF.', 'warning');
            return;
        }

        const tableRowsPrintHtml = ctx.reportData.map(r => `
            <tr style="border-bottom: 1px solid #e2e8f0; ${r.is_guest ? 'background-color: #fffbe6;' : ''}">
                <td style="padding: 8px 6px; text-align: center; border: 1px solid #cbd5e1; font-weight: 600;">${r.stt}</td>
                <td style="padding: 8px 6px; border: 1px solid #cbd5e1; font-weight: 700; color: #4338ca;">${r.code}</td>
                <td style="padding: 8px 6px; border: 1px solid #cbd5e1;">
                    <strong style="color: #0f172a;">${r.name}</strong>
                    ${r.english_name ? `<br><span style="font-size: 11px; color: #64748b;">(${r.english_name})</span>` : ''}
                </td>
                <td style="padding: 8px 6px; border: 1px solid #cbd5e1; font-weight: 700; color: ${r.att_status === 'Có mặt' ? '#047857' : '#c2410c'};">
                    ${r.att_status} ${r.att_note ? `(${r.att_note})` : ''}
                </td>
                <td style="padding: 8px 6px; text-align: center; border: 1px solid #cbd5e1; font-weight: 800; color: #047857;">
                    ${r.hw_score !== '—' ? `${r.hw_score}đ` : '—'}
                </td>
                <td style="padding: 8px 6px; border: 1px solid #cbd5e1;">${r.hw_status}</td>
                <td style="padding: 8px 6px; border: 1px solid #cbd5e1; line-height: 1.3;">${r.hw_comment || '—'}</td>
            </tr>
        `).join('');

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Báo Cáo Điểm Danh & BTVN - Lớp ${ctx.className}</title>
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">
                <style>
                    body { font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; padding: 25px; margin: 0; }
                    .header { text-align: center; border-bottom: 2.5px solid #4f46e5; padding-bottom: 14px; margin-bottom: 20px; }
                    .header h1 { margin: 0; color: #312e81; font-size: 22px; font-weight: 800; text-transform: uppercase; }
                    .header p { margin: 6px 0 0; color: #475569; font-size: 13px; font-weight: 600; }
                    .stats { display: flex; justify-content: space-between; background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px; font-size: 13px; }
                    table { width: 100%; border-collapse: collapse; font-size: 12px; }
                    th { background-color: #312e81; color: #ffffff; padding: 10px 8px; border: 1px solid #1e1b4b; text-align: left; }
                    @media print {
                        body { padding: 0; }
                        @page { size: A4 landscape; margin: 12mm; }
                    }
                </style>
            </head>
            <body>
                <div class="header" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2.5px solid #312e81; padding-bottom: 12px; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 52px; height: 52px; object-fit: contain;">
                        <div>
                            <h1 style="margin: 0; font-size: 20px; color: #0432ff; font-weight: 900; letter-spacing: 0.5px;">TRUNG TÂM ANH NGỮ VICARE</h1>
                            <p style="margin: 3px 0 0; color: #475569; font-size: 13px; font-weight: 700;">BÁO CÁO ĐIỂM DANH & BÀI TẬP VỀ NHÀ — Lớp: <strong>${ctx.className}</strong> (${ctx.formattedDate})</p>
                        </div>
                    </div>
                </div>
                <div class="stats">
                    <div>Sĩ số: <strong>${ctx.totalCount} học sinh</strong></div>
                    <div>🟢 Có mặt: <strong>${ctx.presentCount} học sinh</strong></div>
                    <div>📝 Hoàn thành BTVN: <strong>${ctx.submittedHwCount} / ${ctx.totalCount} học sinh</strong></div>
                    <div>⭐ Điểm TB Cả Lớp: <strong>${ctx.avgScoreStr} / 10đ</strong></div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 35px; text-align: center;">STT</th>
                            <th style="width: 70px;">Mã HS</th>
                            <th style="width: 160px;">Họ Và Tên</th>
                            <th style="width: 110px;">Điểm Danh</th>
                            <th style="width: 90px; text-align: center;">Điểm</th>
                            <th style="width: 115px;">Tình Trạng BVN</th>
                            <th>Nhận Xét Bài Về Nhà Học Viên</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRowsPrintHtml}
                    </tbody>
                </table>

                <!-- Watermark Footer -->
                <div style="margin-top: 24px; border-top: 1.5px dashed #cbd5e1; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; color: #64748b;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <img src="/static/images/logo.jpg" style="width: 16px; height: 16px; object-fit: contain;">
                        <strong>Trung tâm Anh ngữ Vicare</strong> - Báo cáo điểm danh & BTVN chính thức
                    </div>
                    <div>✨ Thiết kế bởi: <strong style="color: #0284c7; font-weight: 800;">Nhi Phương</strong></div>
                </div>

                <script>
                    window.onload = function() {
                        setTimeout(function() {
                            window.print();
                        }, 400);
                    };
                </script>
            </body>
            </html>
        `);
        printWindow.document.close();
        App.showToast('Đã mở cửa sổ xuất PDF Báo cáo thành công!', 'success');
    },

    downloadReportCSV() {
        const ctx = this.activeReportContext;
        if (!ctx) return;

        let csvContent = "\uFEFF";
        csvContent += "STT,Ma HS,Ho Va Ten,Ten Tieng Anh,Diem Danh,Ghi Chu Vang,So Cau Dung,Tong So Cau,Diem Quy Doi,Tinh Trang BVN,Nhan Xet BVN\n";

        ctx.reportData.forEach(r => {
            const row = [
                r.stt,
                `"${r.code}"`,
                `"${r.name}"`,
                `"${r.english_name}"`,
                `"${r.att_status}"`,
                `"${r.att_note}"`,
                `"${r.hw_corr}"`,
                `"${r.hw_tot}"`,
                `"${r.hw_score}"`,
                `"${r.hw_status}"`,
                `"${r.hw_comment.replace(/"/g, '""')}"`
            ];
            csvContent += row.join(",") + "\n";
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `BaoCao_BTVN_${ctx.className}_${ctx.dateVal}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        App.showToast(`Đã xuất và tải thành công file Báo cáo CSV cho lớp ${ctx.className}!`, 'success');
    },

    openSingleHwModal(rowId) {
        let stName = 'Học sinh';
        const isGuest = rowId.startsWith('guest_');
        const stCode = isGuest ? rowId.replace('guest_', '') : '';
        if (isGuest) {
            const gObj = this.addedGuestStudents.find(g => g.code === stCode);
            if (gObj) stName = gObj.name;
        } else {
            const sObj = this.studentsInClass.find(s => String(s.id) === String(rowId));
            if (sObj) stName = sObj.name;
        }

        const hwTotInput = document.getElementById(`hw_tot_${rowId}`);
        const hwCorrInput = document.getElementById(`hw_corr_${rowId}`);
        const hwStatusInput = document.getElementById(`hw_status_${rowId}`);
        const hwCommentInput = document.getElementById(`hw_comment_${rowId}`);
        const globalTotInput = document.getElementById('global-hw-total-questions');

        let totVal = hwTotInput ? hwTotInput.value.trim() : '';
        if (!totVal && globalTotInput) totVal = globalTotInput.value.trim();
        const corrVal = hwCorrInput ? hwCorrInput.value.trim() : '';
        const statusVal = hwStatusInput ? hwStatusInput.value : 'Nộp đúng giờ';
        const commentVal = hwCommentInput ? hwCommentInput.value : '';

        let modal = document.getElementById('cm-single-hw-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'cm-single-hw-modal';
            modal.style.cssText = 'position: fixed; inset: 0; z-index: 9999; background: rgba(10, 14, 26, 0.85); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.2s ease-out;';
            document.body.appendChild(modal);
        }

        modal.innerHTML = `
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 16px; width: 100%; max-width: 520px; box-shadow: 0 20px 50px rgba(0,0,0,0.15); overflow: hidden;">
                <div style="padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between;">
                    <h3 style="margin: 0; font-size: 15px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        📝 NHẬP BTVN - ${AuthModule.escapeHtml(stName)}
                    </h3>
                    <button onclick="document.getElementById('cm-single-hw-modal').style.display='none';" style="background: none; border: none; color: #64748b; font-size: 18px; cursor: pointer;">✕</button>
                </div>
                <div style="padding: 20px; display: flex; flex-direction: column; gap: 14px;">
                    <div style="display: flex; gap: 12px;">
                        <div style="flex: 1;">
                            <label style="font-size: 12px; font-weight: 800; color: #0f172a; margin-bottom: 4px; display: block;">📝 Tổng Số Câu BVN:</label>
                            <input type="number" id="modal_hw_tot_${rowId}" value="${totVal}" placeholder="VD: 20" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 700;">
                        </div>
                        <div style="flex: 1;">
                            <label style="font-size: 12px; font-weight: 800; color: #059669; margin-bottom: 4px; display: block;">✅ Số Câu Đúng:</label>
                            <input type="number" id="modal_hw_corr_${rowId}" value="${corrVal}" placeholder="VD: 18" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #10b981; background: #ffffff; color: #059669; font-weight: 800;">
                        </div>
                    </div>
                    <div>
                        <label style="font-size: 12px; font-weight: 800; color: #0f172a; margin-bottom: 4px; display: block;">📌 Tình Trạng Nộp BTVN:</label>
                        <select id="modal_hw_status_${rowId}" class="form-control" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-weight: 600;">
                            <option value="Nộp đúng giờ" ${statusVal === 'Nộp đúng giờ' ? 'selected' : ''}>✅ Nộp đúng giờ</option>
                            <option value="Nộp muộn" ${statusVal === 'Nộp muộn' ? 'selected' : ''}>⏳ Nộp muộn</option>
                            <option value="Không làm" ${statusVal === 'Không làm' ? 'selected' : ''}>❌ Không làm</option>
                            <option value="Nghỉ học" ${statusVal === 'Nghỉ học' ? 'selected' : ''}>🏖️ Nghỉ học</option>
                            <option value="Học buổi đầu" ${statusVal === 'Học buổi đầu' ? 'selected' : ''}>🐣 Học buổi đầu</option>
                            <option value="Không có BVN" ${statusVal === 'Không có BVN' ? 'selected' : ''}>⚪ Không có BVN</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 12px; font-weight: 800; color: #0f172a; margin-bottom: 4px; display: block;">💬 Nhận Xét Bài Về Nhà:</label>
                        <textarea id="modal_hw_comment_${rowId}" rows="3" placeholder="Nhập nhận xét ưu/nhược điểm bài làm..." style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; font-size: 12.5px; font-weight: 600; font-family: inherit;">${AuthModule.escapeHtml(commentVal)}</textarea>
                    </div>
                </div>
                <div style="padding: 14px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 10px;">
                    <button class="btn" onclick="document.getElementById('cm-single-hw-modal').style.display='none';" style="padding: 8px 18px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #334155; font-weight: 700; border-radius: 8px;">Hủy</button>
                    <button class="btn btn-primary" onclick="CMPortalModule.saveSingleHwModal('${rowId}');" style="padding: 8px 22px; font-weight: 800; background: #2563eb; color: #ffffff; border: none; border-radius: 8px; box-shadow: 0 2px 6px rgba(37,99,235,0.3);">💾 Lưu BTVN</button>
                </div>
            </div>
        `;
        modal.style.display = 'flex';
    },

    saveSingleHwModal(rowId) {
        const modalTot = document.getElementById(`modal_hw_tot_${rowId}`);
        const modalCorr = document.getElementById(`modal_hw_corr_${rowId}`);
        const modalStatus = document.getElementById(`modal_hw_status_${rowId}`);
        const modalComment = document.getElementById(`modal_hw_comment_${rowId}`);

        let totVal = modalTot ? modalTot.value.trim() : '';
        let corrVal = modalCorr ? modalCorr.value.trim() : '';

        if (corrVal !== '' && totVal !== '') {
            const cNum = parseFloat(corrVal);
            const tNum = parseFloat(totVal);
            if (!isNaN(cNum) && !isNaN(tNum) && tNum > 0 && cNum > tNum) {
                App.showToast(`⚠️ Số câu đúng (${cNum}) không được vượt quá Tổng số câu (${tNum})!`, 'warning');
                corrVal = String(tNum);
            }
        }

        const hwTotHidden = document.getElementById(`hw_tot_${rowId}`);
        const hwCorrHidden = document.getElementById(`hw_corr_${rowId}`);
        const hwStatusHidden = document.getElementById(`hw_status_${rowId}`);
        const hwCommentHidden = document.getElementById(`hw_comment_${rowId}`);

        if (hwTotHidden) hwTotHidden.value = totVal;
        if (hwCorrHidden) hwCorrHidden.value = corrVal;
        if (hwStatusHidden) hwStatusHidden.value = modalStatus ? modalStatus.value : 'Nộp đúng giờ';
        if (hwCommentHidden) hwCommentHidden.value = modalComment ? modalComment.value.trim() : '';

        document.getElementById('cm-single-hw-modal').style.display = 'none';

        const existingMap = {};
        const collectState = (rId, name) => {
            const hwT = document.getElementById(`hw_tot_${rId}`);
            const hwC = document.getElementById(`hw_corr_${rId}`);
            const hwS = document.getElementById(`hw_status_${rId}`);
            const hwCm = document.getElementById(`hw_comment_${rId}`);
            const attS = document.getElementById(`att_select_${rId}`);
            const attN = document.getElementById(`note_${rId}`);

            existingMap[name] = {
                hw_total_questions: hwT ? hwT.value : '',
                hw_correct_answers: hwC ? hwC.value : '',
                hw_submission_status: hwS ? hwS.value : 'Nộp đúng giờ',
                hw_comment: hwCm ? hwCm.value : '',
                status: attS ? attS.value : 'Có mặt',
                note: attN ? attN.value : ''
            };
        };

        this.studentsInClass.forEach(s => collectState(s.id, s.name));
        this.addedGuestStudents.forEach(g => collectState(`guest_${g.code}`, g.name));
        this.renderAttendanceTableBody(existingMap);

        App.showToast('Đã lưu thông tin BTVN cho học sinh!', 'success');
    },

    openBatchHwModal() {
        let modal = document.getElementById('cm-batch-hw-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'cm-batch-hw-modal';
            modal.style.cssText = 'position: fixed; inset: 0; z-index: 9999; background: rgba(10, 14, 26, 0.85); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.2s ease-out;';
            document.body.appendChild(modal);
        }

        const globalTotInput = document.getElementById('global-hw-total-questions');
        const currentGlobalTot = globalTotInput ? globalTotInput.value : '';

        let allRowsHtml = '';
        let stt = 1;

        const makeRow = (s, isGuest = false) => {
            const rId = isGuest ? `guest_${s.code}` : s.id;
            const hwTotH = document.getElementById(`hw_tot_${rId}`);
            const hwCorrH = document.getElementById(`hw_corr_${rId}`);
            const hwStatH = document.getElementById(`hw_status_${rId}`);
            const hwCommH = document.getElementById(`hw_comment_${rId}`);

            const cVal = hwCorrH ? hwCorrH.value : '';
            const sVal = hwStatH ? hwStatH.value : 'Nộp đúng giờ';
            const cmVal = hwCommH ? hwCommH.value : '';

            return `
                <tr style="border-bottom: 1px solid var(--border-color); ${isGuest ? 'background: rgba(245,158,11,0.05);' : ''}">
                    <td style="padding: 8px; text-align: center; color: var(--text-muted); font-weight: 600;">${stt++}</td>
                    <td style="padding: 8px; font-weight: 700; color: var(--accent-color); font-size: 11.5px;">${AuthModule.escapeHtml(s.code || '—')}</td>
                    <td style="padding: 8px;">
                        <div style="font-weight: 700; color: var(--text-heading); font-size: 12px;">${AuthModule.escapeHtml(s.name)}</div>
                    </td>
                    <td style="padding: 8px; text-align: center;">
                        <input type="number" id="batch_corr_${rId}" value="${cVal}" min="0" placeholder="Số câu đúng" style="width: 80px; padding: 6px; border-radius: 6px; border: 1.5px solid #10b981; background: var(--bg-card); color: #10b981; font-weight: 800; text-align: center; font-size: 12px;">
                    </td>
                    <td style="padding: 8px;">
                        <select id="batch_status_${rId}" class="form-control" style="width: 100%; padding: 6px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-card); font-size: 11.5px;">
                            <option value="Nộp đúng giờ" ${sVal === 'Nộp đúng giờ' ? 'selected' : ''}>✅ Nộp đúng giờ</option>
                            <option value="Nộp muộn" ${sVal === 'Nộp muộn' ? 'selected' : ''}>⏳ Nộp muộn</option>
                            <option value="Không làm" ${sVal === 'Không làm' ? 'selected' : ''}>❌ Không làm</option>
                            <option value="Nghỉ học" ${sVal === 'Nghỉ học' ? 'selected' : ''}>🏖️ Nghỉ học</option>
                            <option value="Học buổi đầu" ${sVal === 'Học buổi đầu' ? 'selected' : ''}>🐣 Học buổi đầu</option>
                            <option value="Không có BVN" ${sVal === 'Không có BVN' ? 'selected' : ''}>⚪ Không có BVN</option>
                        </select>
                    </td>
                    <td style="padding: 8px;">
                        <input type="text" id="batch_comm_${rId}" value="${AuthModule.escapeHtml(cmVal)}" placeholder="Nhận xét BTVN..." style="width: 100%; padding: 6px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main); font-size: 11.5px;">
                    </td>
                </tr>
            `;
        };

        this.studentsInClass.forEach(s => allRowsHtml += makeRow(s, false));
        this.addedGuestStudents.forEach(g => allRowsHtml += makeRow(g, true));

        modal.innerHTML = `
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 16px; width: 100%; max-width: 900px; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.15);">
                <div style="padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <h3 style="margin: 0; font-size: 16px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                            📝 NHẬP ĐIỂM & NHẬN XÉT BTVN HÀNG LOẠT - ${AuthModule.escapeHtml(this.selectedClassName)}
                        </h3>
                        <div style="font-size: 12px; color: #475569; margin-top: 2px; font-weight: 700;">
                            Tổng Số Câu BVN Cả Lớp: <input type="number" id="batch_global_tot" value="${currentGlobalTot}" placeholder="VD: 20" style="width: 65px; padding: 2px 6px; border-radius: 6px; border: 1.5px solid #2563eb; background: #ffffff; color: #1d4ed8; font-weight: 800; text-align: center; font-size: 12px;"> câu
                        </div>
                    </div>
                    <button onclick="document.getElementById('cm-batch-hw-modal').style.display='none';" style="background: none; border: none; color: #64748b; font-size: 20px; cursor: pointer;">✕</button>
                </div>

                <div style="flex: 1; overflow-y: auto; padding: 0;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; table-layout: fixed;">
                        <thead>
                            <tr style="background: #f1f5f9; text-align: left; position: sticky; top: 0; z-index: 10; color: #0f172a; border-bottom: 1.5px solid #cbd5e1;">
                                <th style="padding: 10px 8px; width: 38px; text-align: center; font-weight: 800;">STT</th>
                                <th style="padding: 10px 8px; width: 75px; font-weight: 800;">Mã HS</th>
                                <th style="padding: 10px 8px; width: 160px; font-weight: 800;">Họ Và Tên</th>
                                <th style="padding: 10px 8px; width: 110px; text-align: center; font-weight: 800;">Số Câu Đúng</th>
                                <th style="padding: 10px 8px; width: 140px; font-weight: 800;">Tình Trạng Nộp</th>
                                <th style="padding: 10px 8px; font-weight: 800;">Nhận Xét Bài Về Nhà Học Viên</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${allRowsHtml}
                        </tbody>
                    </table>
                </div>

                <div style="padding: 14px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: flex-end; gap: 10px;">
                    <button class="btn" onclick="document.getElementById('cm-batch-hw-modal').style.display='none';" style="padding: 8px 18px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #334155; font-weight: 700; border-radius: 8px;">Hủy</button>
                    <button class="btn btn-primary" onclick="CMPortalModule.saveBatchHwModal();" style="padding: 8px 22px; font-weight: 800; background: #2563eb; color: #ffffff; border: none; border-radius: 8px; box-shadow: 0 2px 6px rgba(37,99,235,0.3);">💾 Lưu Toàn Bộ BTVN</button>
                </div>
            </div>
        `;
        modal.style.display = 'flex';
    },

    saveBatchHwModal() {
        const batchTotInput = document.getElementById('batch_global_tot');
        const batchTotStr = batchTotInput ? batchTotInput.value.trim() : '';
        const globalTotInput = document.getElementById('global-hw-total-questions');
        if (globalTotInput) globalTotInput.value = batchTotStr;

        const totNum = parseFloat(batchTotStr);

        const updateRowFromBatch = (rId) => {
            const cInput = document.getElementById(`batch_corr_${rId}`);
            const sSelect = document.getElementById(`batch_status_${rId}`);
            const cmInput = document.getElementById(`batch_comm_${rId}`);

            if (!cInput) return;

            let corrStr = cInput.value.trim();
            if (corrStr !== '' && !isNaN(totNum) && totNum > 0) {
                let corrVal = parseFloat(corrStr);
                if (corrVal > totNum) {
                    App.showToast(`⚠️ Số câu đúng (${corrVal}) không được vượt quá Tổng số câu (${totNum})!`, 'warning');
                    corrVal = totNum;
                    corrStr = String(totNum);
                }
            }

            const hwT = document.getElementById(`hw_tot_${rId}`);
            const hwC = document.getElementById(`hw_corr_${rId}`);
            const hwS = document.getElementById(`hw_status_${rId}`);
            const hwCm = document.getElementById(`hw_comment_${rId}`);

            if (hwT) hwT.value = batchTotStr;
            if (hwC) hwC.value = corrStr;
            if (hwS) hwS.value = sSelect ? sSelect.value : 'Nộp đúng giờ';
            if (hwCm) hwCm.value = cmInput ? cmInput.value.trim() : '';
        };

        this.studentsInClass.forEach(s => updateRowFromBatch(s.id));
        this.addedGuestStudents.forEach(g => updateRowFromBatch(`guest_${g.code}`));

        document.getElementById('cm-batch-hw-modal').style.display = 'none';

        const existingMap = {};
        const collectState = (rId, name) => {
            const hwT = document.getElementById(`hw_tot_${rId}`);
            const hwC = document.getElementById(`hw_corr_${rId}`);
            const hwS = document.getElementById(`hw_status_${rId}`);
            const hwCm = document.getElementById(`hw_comment_${rId}`);
            const attS = document.getElementById(`att_select_${rId}`);
            const attN = document.getElementById(`note_${rId}`);

            existingMap[name] = {
                hw_total_questions: hwT ? hwT.value : '',
                hw_correct_answers: hwC ? hwC.value : '',
                hw_submission_status: hwS ? hwS.value : 'Nộp đúng giờ',
                hw_comment: hwCm ? hwCm.value : '',
                status: attS ? attS.value : 'Có mặt',
                note: attN ? attN.value : ''
            };
        };

        this.studentsInClass.forEach(s => collectState(s.id, s.name));
        this.addedGuestStudents.forEach(g => collectState(`guest_${g.code}`, g.name));
        this.renderAttendanceTableBody(existingMap);

        App.showToast('Đã cập nhật BTVN thành công cho toàn bộ lớp!', 'success');
    }
};
