/**
 * EVI Dashboard - Dashboard Module
 * Main dashboard page with KPI cards, charts, and data tables.
 */

const Dashboard = {
    charts: {},
    data: null,

    /**
     * Render the dashboard page.
     */
    async render(container) {
        // Fetch data
        try {
            const response = await API.getDashboard();
            if (!response.success) throw new Error(response.error);
            this.data = response.data;
        } catch (error) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <h3>Không thể tải dữ liệu</h3>
                    <p>${error.message}</p>
                </div>
            `;
            return;
        }

        const { kpi, renewal_monthly, classes, acs_stats } = this.data;

        // Build HTML
        container.innerHTML = `
            ${!App.isConnected ? `
                <div class="demo-banner">
                    <span class="demo-banner-icon">⚠️</span>
                    <span>Đang chạy ở <strong>chế độ Demo</strong> với dữ liệu mẫu. Cấu hình Google Sheets credentials để kết nối dữ liệu thực.</span>
                </div>
            ` : ''}

            <!-- CM Schedule Timetable Widget (Đưa lên đầu cho CM kiểm tra) -->
            <div id="cm-dashboard-schedule-container"></div>

            <!-- Admin Activity Feed Widget (Chỉ dành cho Admin) -->
            <div id="admin-dashboard-activity-container"></div>

            <!-- KPI Cards -->
            <div class="kpi-grid">
                ${this.renderKPICard('👥', 'Tổng Học Sinh', kpi.total_students, 'active', 'purple', 'accent-purple', 'students')}
                ${this.renderKPICard('📊', 'Tỉ Lệ Tái Phí', Utils.formatPercent(kpi.latest_renewal_rate), `T${kpi.latest_renewal_month}/${kpi.latest_renewal_year}`, 'blue', 'accent-blue', 'renewal')}
                ${this.renderKPICard('🏫', 'Lớp Đang Hoạt Động', kpi.active_classes, 'lớp đang hoạt động', 'green', 'accent-green', 'classes')}
                ${this.renderKPICard('⭐', 'ACS Trung Bình', kpi.avg_acs.toFixed(2), 'điểm', 'amber', 'accent-amber', 'acs')}
            </div>

            <!-- Charts Row 1 -->
            <div class="charts-grid">
                <!-- Renewal Trend Chart -->
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">📈 Tỉ Lệ Tái Phí Theo Tháng</div>
                            <div class="chart-subtitle">Xu hướng tái phí qua các tháng</div>
                        </div>
                    </div>
                    <div class="chart-body">
                        <canvas id="chart-renewal-trend"></canvas>
                    </div>
                </div>

                <!-- Renewal Staff Chart -->
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">👥 Tái Phí Theo Nhân Viên</div>
                            <div class="chart-subtitle" id="staff-renewal-subtitle">So sánh hiệu suất CM tháng gần nhất</div>
                        </div>
                    </div>
                    <div class="chart-body">
                        <canvas id="chart-staff-renewal"></canvas>
                    </div>
                </div>
            </div>

            <!-- Charts Row 2 -->
            <div class="charts-grid">
                <!-- Students by Schedule -->
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">📅 Phân Bổ Theo Ca Học</div>
                            <div class="chart-subtitle">Số học sinh theo ca (MT/TF/WS)</div>
                        </div>
                    </div>
                    <div class="chart-body">
                        <canvas id="chart-schedule-dist"></canvas>
                    </div>
                </div>

                <!-- ACS Score -->
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">⭐ Điểm ACS Nhân Viên</div>
                            <div class="chart-subtitle">Đánh giá chất lượng dịch vụ</div>
                        </div>
                    </div>
                    <div class="chart-body">
                        <canvas id="chart-acs-score"></canvas>
                    </div>
                </div>
            </div>



            <!-- Class List Table -->
            <div class="chart-card full-width">
                <div class="chart-header">
                    <div>
                        <div class="chart-title">🏫 Tổng Quan Lớp Học</div>
                        <div class="chart-subtitle">Danh sách lớp học đang hoạt động</div>
                    </div>
                </div>
                <div class="data-table-wrapper">
                    <table class="data-table" id="class-list-table">
                        <thead>
                            <tr>
                                <th>Lớp</th>
                                <th>Ca học</th>
                                <th>Phòng</th>
                                <th>Giáo viên</th>
                                <th>CM</th>
                                <th>TA</th>
                                <th>Học sinh</th>
                            </tr>
                        </thead>
                        <tbody id="class-table-body"></tbody>
                    </table>
                </div>
            </div>
        `;

        // Render components
        this.renderClassTable(classes);

        // Render CM Schedule Widget at the top of Dashboard
        if (typeof ScheduleModule !== 'undefined') {
            const user = (typeof Auth !== 'undefined') ? Auth.getUser() : null;
            const cmName = (user && user.role === 'cm') ? (user.cm_staff_name || user.full_name) : (user && user.cm_staff_name ? user.cm_staff_name : 'AnhNV');
            const schedContainer = document.getElementById('cm-dashboard-schedule-container');
            if (schedContainer) {
                ScheduleModule.renderCmDashboardSchedule(schedContainer, cmName);
            }
        }

        // Render Admin Activity Feed Widget if Admin
        this.renderAdminActivityFeedWidget();

        // Initialize charts after DOM is ready
        requestAnimationFrame(() => {
            this.initCharts(renewal_monthly, classes, acs_stats);
        });
    },

    async renderAdminActivityFeedWidget() {
        if (typeof AuthModule === 'undefined' || !AuthModule.isAdmin()) return;
        const container = document.getElementById('admin-dashboard-activity-container');
        if (!container) return;

        try {
            const res = await API.get('/admin/notifications', { limit: 5 });
            if (!res.success || !res.data || res.data.length === 0) return;

            const itemsHtml = res.data.map(item => `
                <div style="padding: 10px 14px; background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0;">
                        <span style="font-size: 16px;">⚡</span>
                        <div style="min-width: 0;">
                            <span style="font-weight: 800; color: #0f172a; font-size: 12.5px;">${AuthModule.escapeHtml(item.user_fullname || item.username)}</span>:
                            <span style="color: #334155; font-size: 12.5px; font-weight: 500;">${AuthModule.escapeHtml(item.description)}</span>
                        </div>
                    </div>
                    <span style="font-size: 11px; color: #64748b; white-space: nowrap; font-weight: 600;">⏱️ ${item.time_ago || ''}</span>
                </div>
            `).join('');

            container.innerHTML = `
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 16px 18px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="font-size: 14px; font-weight: 800; color: #1d4ed8; display: flex; align-items: center; gap: 6px;">
                            <span>🔔</span> Hoạt Động Mới Nhất Của Nhân Viên
                        </div>
                        <a href="#audit-logs" onclick="App.navigateTo('audit-logs');" style="font-size: 12px; color: #2563eb; font-weight: 700; text-decoration: none;">Xem tất cả →</a>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        ${itemsHtml}
                    </div>
                </div>
            `;
        } catch (e) {
            console.error('Error rendering admin activity feed widget:', e);
        }
    },

    /**
     * Render a KPI card with click popup support.
     */
    renderKPICard(icon, label, value, subtitle, colorClass, accentClass, kpiType = '') {
        return `
            <div class="kpi-card ${accentClass} animate-in" onclick="Dashboard.openKPIDetail('${kpiType}')">
                <div class="kpi-header">
                    <div class="kpi-icon ${colorClass}">${icon}</div>
                    <div class="kpi-label">${label}</div>
                </div>
                <div class="kpi-value">${value}</div>
                <div class="kpi-change neutral">
                    ${subtitle}
                </div>
            </div>
        `;
    },

    /**
     * Open Modal popup with detailed breakdown when a KPI card is clicked.
     */
    openKPIDetail(type) {
        const backdrop = document.getElementById('modal-backdrop');
        const titleEl = document.getElementById('modal-title');
        const bodyEl = document.getElementById('modal-body');

        if (!backdrop || !titleEl || !bodyEl || !this.data) return;

        const { kpi, renewal_monthly, classes, acs_stats } = this.data;

        if (type === 'students') {
            titleEl.innerHTML = `👥 Chi Tiết Danh Sách Học Sinh (Tổng: ${kpi.total_students} HS active)`;

            const activeClasses = classes.filter(c => (c.students || c.student_count || c.students_count || 0) > 0);
            let classRows = '';
            activeClasses.forEach(c => {
                const cName = c.class_name || c.name || '';
                const cStudents = c.students || c.student_count || c.students_count || 0;
                const cSchedule = c.schedule || c.shift_code || '—';
                const cCM = c.cm_staff || c.cm || '—';
                const color = Utils.getAvatarColor(cName);
                classRows += `
                    <tr>
                        <td>
                            <div class="staff-name">
                                <div class="staff-avatar" style="background: ${color}">${Utils.getInitials(cName)}</div>
                                <strong>${cName}</strong>
                            </div>
                        </td>
                        <td><span class="badge badge-info">${cSchedule}</span></td>
                        <td>${c.room || '—'}</td>
                        <td>${c.teacher || '—'}</td>
                        <td>${cCM}</td>
                        <td><strong>${cStudents} HS</strong></td>
                    </tr>
                `;
            });

            bodyEl.innerHTML = `
                <div style="margin-bottom: 16px; color: var(--text-secondary); font-size: 13px;">
                    Tổng số <strong>${kpi.total_students} học sinh</strong> đang theo học trên <strong>${activeClasses.length} lớp active</strong>:
                </div>
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Lớp học</th>
                                <th>Ca học</th>
                                <th>Phòng</th>
                                <th>Giáo viên</th>
                                <th>CM Phụ trách</th>
                                <th>Số lượng HS</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${classRows}
                        </tbody>
                    </table>
                </div>
            `;
        } else if (type === 'renewal') {
            const targetMonth = kpi.latest_renewal_month;
            const targetYear = kpi.latest_renewal_year;
            
            titleEl.innerHTML = `📊 Chi Tiết Tỉ Lệ Tái Phí Tháng ${targetMonth}/${targetYear}`;
            
            const targetRec = renewal_monthly.find(r => r.month === targetMonth && r.year === targetYear) || (renewal_monthly.length ? renewal_monthly[renewal_monthly.length - 1] : null);
            let rows = '';

            if (targetRec && targetRec.staff) {
                targetRec.staff.forEach(s => {
                    const badgeClass = Utils.getRateBadge(s.rate);
                    rows += `
                        <tr>
                            <td><strong>${s.name}</strong></td>
                            <td>${s.due}</td>
                            <td><span style="color: #34d399; font-weight: 600;">${s.success}</span></td>
                            <td><span style="color: #fbbf24;">${s.pending}</span></td>
                            <td><span style="color: #f87171;">${s.failed}</span></td>
                            <td><span class="badge ${badgeClass}">${Utils.formatPercent(s.rate)}</span></td>
                        </tr>
                    `;
                });
            }

            bodyEl.innerHTML = `
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Nhân viên (CM)</th>
                                <th>Học sinh đến hạn</th>
                                <th>Tái phí thành công</th>
                                <th>Chờ nộp phí</th>
                                <th>Không tái phí</th>
                                <th>Tỉ lệ tái phí</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                </div>
            `;
        } else if (type === 'classes') {
            titleEl.innerHTML = `🏫 Danh Sách ${kpi.active_classes} Lớp Học Đang Hoạt Động`;

            const activeClasses = classes.filter(c => (c.students || c.student_count || c.students_count || 0) > 0 && (c.schedule || c.shift_code));
            let classRows = '';
            activeClasses.forEach(c => {
                const cName = c.class_name || c.name || '';
                const cSched = c.schedule || c.shift_code || '—';
                const cCM = c.cm_staff || c.cm || '—';
                const cTA = c.ta_staff || c.ta || '—';
                const cStudents = c.students || c.student_count || c.students_count || 0;
                classRows += `
                    <tr>
                        <td><strong style="color: var(--text-primary);">${cName}</strong></td>
                        <td><span class="badge badge-success">${cSched}</span></td>
                        <td>${c.room || '—'}</td>
                        <td>${c.teacher || 'Chưa xếp'}</td>
                        <td>${cCM}</td>
                        <td>${cTA}</td>
                        <td><strong style="color: var(--text-accent);">${cStudents} HS</strong></td>
                    </tr>
                `;
            });

            bodyEl.innerHTML = `
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Tên lớp</th>
                                <th>Ca học</th>
                                <th>Phòng học</th>
                                <th>Giáo viên</th>
                                <th>CM</th>
                                <th>TA (Trợ giảng)</th>
                                <th>Số HS Active</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${classRows}
                        </tbody>
                    </table>
                </div>
            `;
        } else if (type === 'acs') {
            titleEl.innerHTML = `⭐ Bảng Điểm ACS Đánh Giá Nhân Viên (TB: ${acs_stats.average || 7.58} điểm)`;

            let staffRows = '';
            if (acs_stats.staff) {
                acs_stats.staff.forEach(s => {
                    let rating = 'Khá';
                    let ratingBadge = 'badge-warning';
                    if (s.score >= 8.5) { rating = 'Xuất sắc'; ratingBadge = 'badge-success'; }
                    else if (s.score >= 7.5) { rating = 'Tốt'; ratingBadge = 'badge-info'; }

                    staffRows += `
                        <tr>
                            <td>
                                <div class="staff-name">
                                    <div class="staff-avatar" style="background: ${Utils.getAvatarColor(s.name)}">${Utils.getInitials(s.name)}</div>
                                    <strong>${s.name}</strong>
                                </div>
                            </td>
                            <td><strong style="font-size: 16px; color: var(--text-primary);">${s.score.toFixed(2)} / 10</strong></td>
                            <td><span class="badge ${ratingBadge}">${rating}</span></td>
                            <td>
                                <div class="rate-bar" style="width: 120px; height: 8px;">
                                    <div class="rate-fill green" style="width: ${(s.score / 10) * 100}%;"></div>
                                </div>
                            </td>
                        </tr>
                    `;
                });
            }

            bodyEl.innerHTML = `
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Nhân viên (CM)</th>
                                <th>Điểm ACS</th>
                                <th>Đánh giá chất lượng</th>
                                <th>Biểu đồ điểm</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${staffRows}
                        </tbody>
                    </table>
                </div>
            `;
        }

        if (backdrop) {
            backdrop.style.display = 'flex';
            backdrop.classList.add('active');
        }
    },

    modalStack: [],

    /**
     * Push current active modal state onto stack before opening a sub-modal/preview.
     */
    pushModalState(onRestore = null) {
        const backdrop = document.getElementById('modal-backdrop');
        const titleEl = document.getElementById('modal-title');
        const bodyEl = document.getElementById('modal-body');

        if (backdrop && backdrop.classList.contains('active') && titleEl && bodyEl) {
            if (!this.modalStack) this.modalStack = [];
            this.modalStack.push({
                title: titleEl.innerHTML,
                body: bodyEl.innerHTML,
                scrollTop: bodyEl.scrollTop || 0,
                onRestore: onRestore
            });
        }
    },

    /**
     * Close Modal popup incrementally (pops from modalStack if parent modal exists, otherwise hides backdrop).
     */
    closeModal() {
        const backdrop = document.getElementById('modal-backdrop');
        if (this.modalStack && this.modalStack.length > 0) {
            const prevState = this.modalStack.pop();
            if (prevState) {
                if (prevState.onRestore) {
                    prevState.onRestore();
                } else {
                    const titleEl = document.getElementById('modal-title');
                    const bodyEl = document.getElementById('modal-body');
                    if (titleEl && bodyEl) {
                        titleEl.innerHTML = prevState.title;
                        bodyEl.innerHTML = prevState.body;
                        if (prevState.scrollTop) {
                            bodyEl.scrollTop = prevState.scrollTop;
                        }
                    }
                }
                if (backdrop) {
                    backdrop.style.display = 'flex';
                    backdrop.classList.add('active');
                }
                return;
            }
        }

        // If stack is empty, reset stack and hide backdrop
        this.modalStack = [];
        if (backdrop) {
            backdrop.style.display = '';
            backdrop.classList.remove('active');
            const container = backdrop.querySelector('.modal-container');
            if (container) {
                container.classList.remove('modal-xl');
                container.style.maxWidth = '';
                container.style.width = '';
            }
        }
    },

    /**
     * Force close all modals completely back to main page.
     */
    closeAllModals() {
        this.modalStack = [];
        const backdrop = document.getElementById('modal-backdrop');
        if (backdrop) {
            backdrop.classList.remove('active');
            const container = backdrop.querySelector('.modal-container');
            if (container) {
                container.classList.remove('modal-xl');
                container.style.maxWidth = '';
                container.style.width = '';
            }
        }
        const studentModal = document.getElementById('student-modal');
        if (studentModal) studentModal.classList.remove('active');
    },

    /**
     * Render renewal detail table with Month Selector.
     */
    renderRenewalTable(renewalData, selectedMonth = null, selectedYear = null) {
        const tbody = document.getElementById('renewal-table-body');
        const subtitle = document.getElementById('renewal-table-subtitle');
        const monthSelect = document.getElementById('renewal-month-select');
        if (!tbody || !renewalData || !renewalData.length) return;

        // Determine target record
        let targetRec = null;
        if (selectedMonth && selectedYear) {
            targetRec = renewalData.find(r => r.month === parseInt(selectedMonth) && r.year === parseInt(selectedYear));
        }

        if (!targetRec) {
            const { kpi } = this.data || {};
            if (kpi && kpi.latest_renewal_month) {
                targetRec = renewalData.find(r => r.month === kpi.latest_renewal_month && r.year === kpi.latest_renewal_year);
            }
        }

        if (!targetRec) {
            targetRec = renewalData[renewalData.length - 1];
        }

        // Populate select options
        if (monthSelect) {
            let optionsHTML = '';
            renewalData.forEach(r => {
                const key = `${r.month}-${r.year}`;
                const isSelected = targetRec && r.month === targetRec.month && r.year === targetRec.year ? 'selected' : '';
                optionsHTML += `<option value="${key}" ${isSelected}>Tháng ${r.month}/${r.year}</option>`;
            });
            monthSelect.innerHTML = optionsHTML;
        }

        if (subtitle && targetRec) {
            subtitle.textContent = `Báo cáo tái phí Tháng ${targetRec.month}/${targetRec.year}`;
        }

        let html = '';

        if (targetRec && targetRec.staff) {
            targetRec.staff.forEach(staff => {
                const color = Utils.getAvatarColor(staff.name);
                const badgeClass = Utils.getRateBadge(staff.rate);
                const progressColor = Utils.getProgressColor(staff.rate);

                html += `
                    <tr>
                        <td>
                            <div class="staff-name">
                                <div class="staff-avatar" style="background: ${color}">
                                    ${Utils.getInitials(staff.name)}
                                </div>
                                ${staff.name}
                            </div>
                        </td>
                        <td>${staff.due}</td>
                        <td><span style="color: #10b981; font-weight: 600">${staff.success}</span></td>
                        <td><span style="color: #2563eb; font-weight: 600">${staff.stacked || 0}</span></td>
                        <td><span style="color: #f59e0b">${staff.pending}</span></td>
                        <td><span style="color: #ef4444">${staff.failed}</span></td>
                        <td><span class="badge ${badgeClass}">${Utils.formatPercent(staff.rate)}</span></td>
                        <td>
                            <div class="rate-display">
                                <div class="rate-bar">
                                    <div class="rate-fill ${progressColor}" style="width: ${staff.rate}%"></div>
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            });

            // Total row
            if (targetRec.total) {
                const t = targetRec.total;
                html += `
                    <tr class="row-total">
                        <td><strong>📊 Tổng cộng</strong></td>
                        <td><strong>${t.due}</strong></td>
                        <td><strong style="color: #10b981">${t.success}</strong></td>
                        <td><strong style="color: #2563eb">${t.stacked || 0}</strong></td>
                        <td><strong style="color: #f59e0b">${t.pending}</strong></td>
                        <td><strong style="color: #ef4444">${t.failed}</strong></td>
                        <td><span class="badge ${Utils.getRateBadge(t.rate)}">${Utils.formatPercent(t.rate)}</span></td>
                        <td>
                            <div class="rate-display">
                                <div class="rate-bar">
                                    <div class="rate-fill ${Utils.getProgressColor(t.rate)}" style="width: ${t.rate}%"></div>
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            }
        }

        tbody.innerHTML = html;
    },

    handleRenewalMonthChange(val) {
        if (!val || !this.data || !this.data.renewal_monthly) return;
        const parts = val.split('-');
        if (parts.length === 2) {
            const m = parseInt(parts[0]);
            const y = parseInt(parts[1]);
            this.renderRenewalTable(this.data.renewal_monthly, m, y);
            this.createStaffRenewalChart(this.data.renewal_monthly, m, y);
        }
    },

    /**
     * Render class list table.
     */
    renderClassTable(classes) {
        const tbody = document.getElementById('class-table-body');
        if (!tbody || !classes || !classes.length) return;

        // Filter active classes
        const activeClasses = classes.filter(c => (c.schedule || c.shift_code) && (c.students || c.student_count || c.students_count || 0) > 0);

        let html = '';
        activeClasses.forEach(cls => {
            const clsName = cls.class_name || cls.name || '';
            const schedStr = cls.schedule || cls.shift_code || '—';
            const cmName = cls.cm_staff || cls.cm || '';
            const taName = cls.ta_staff || cls.ta || '';
            const stNum = cls.students || cls.student_count || cls.students_count || 0;
            const cmColor = cmName ? Utils.getAvatarColor(cmName) : '#64748b';

            // Schedule badge color
            const scheduleColors = {
                'MT5': 'badge-info', 'MT6': 'badge-info',
                'TF5': 'badge-success', 'TF6': 'badge-success',
                'WS5': 'badge-warning', 'WS6': 'badge-warning',
            };

            html += `
                <tr>
                    <td><strong style="color: var(--text-primary)">${clsName}</strong></td>
                    <td><span class="badge ${scheduleColors[schedStr] || 'badge-neutral'}">${schedStr}</span></td>
                    <td>${cls.room || '—'}</td>
                    <td>${cls.teacher || '—'}</td>
                    <td>
                        ${cmName ? `
                            <div class="staff-name">
                                <div class="staff-avatar" style="background: ${cmColor}; width: 22px; height: 22px; font-size: 9px;">
                                    ${Utils.getInitials(cmName)}
                                </div>
                                ${cmName}
                            </div>
                        ` : '—'}
                    </td>
                    <td>${taName || '—'}</td>
                    <td><strong>${stNum}</strong></td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    },

    /**
     * Initialize all charts using Chart.js.
     */
    initCharts(renewalData, classes, acsStats) {
        this.createRenewalTrendChart(renewalData);
        this.createStaffRenewalChart(renewalData);
        this.createScheduleDistChart(classes);
        this.createACSChart(acsStats);
    },

    /**
     * Chart: Renewal trend over months.
     */
    createRenewalTrendChart(renewalData) {
        const ctx = document.getElementById('chart-renewal-trend');
        if (!ctx) return;

        const labels = renewalData.map(r => `T${r.month}/${r.year.toString().slice(-2)}`);
        const rates = renewalData.map(r => r.total ? r.total.rate : 0);
        const due = renewalData.map(r => r.total ? r.total.due : 0);
        const success = renewalData.map(r => r.total ? r.total.success : 0);

        this.charts.renewalTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Tỉ lệ tái phí (%)',
                        data: rates,
                        borderColor: '#818cf8',
                        backgroundColor: 'rgba(129, 140, 248, 0.1)',
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#818cf8',
                        pointBorderColor: '#0a0e1a',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Đến hạn',
                        data: due,
                        borderColor: 'rgba(148, 163, 184, 0.5)',
                        backgroundColor: 'rgba(148, 163, 184, 0.05)',
                        borderWidth: 1.5,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: '#94a3b8',
                        yAxisID: 'y1',
                    },
                    {
                        label: 'Thành công',
                        data: success,
                        borderColor: '#34d399',
                        backgroundColor: 'rgba(52, 211, 153, 0.05)',
                        borderWidth: 1.5,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: '#34d399',
                        yAxisID: 'y1',
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11, family: 'Inter' },
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 16,
                        },
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: { size: 12, weight: '600', family: 'Inter' },
                        bodyFont: { size: 11, family: 'Inter' },
                    },
                },
                scales: {
                    x: {
                        ticks: { color: '#64748b', font: { size: 11, family: 'Inter' } },
                        grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    },
                    y: {
                        position: 'left',
                        ticks: {
                            color: '#818cf8',
                            font: { size: 11, family: 'Inter' },
                            callback: v => v + '%',
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.03)' },
                        min: 0,
                        max: 100,
                    },
                    y1: {
                        position: 'right',
                        ticks: {
                            color: '#64748b',
                            font: { size: 11, family: 'Inter' },
                        },
                        grid: { display: false },
                        min: 0,
                    },
                },
            },
        });
    },

    /**
     * Chart: Staff renewal comparison (latest month).
     */
    createStaffRenewalChart(renewalData, selectedMonth = null, selectedYear = null) {
        const ctx = document.getElementById('chart-staff-renewal');
        const subtitleEl = document.getElementById('staff-renewal-subtitle');
        if (!ctx || !renewalData || !renewalData.length) return;

        let targetRec = null;
        if (selectedMonth && selectedYear) {
            targetRec = renewalData.find(r => r.month === parseInt(selectedMonth) && r.year === parseInt(selectedYear));
        }
        if (!targetRec) {
            const { kpi } = this.data || {};
            if (kpi && kpi.latest_renewal_month && kpi.latest_renewal_year) {
                targetRec = renewalData.find(r => r.month === kpi.latest_renewal_month && r.year === kpi.latest_renewal_year);
            }
        }
        if (!targetRec) {
            targetRec = renewalData[renewalData.length - 1];
        }

        if (subtitleEl && targetRec) {
            subtitleEl.textContent = `So sánh hiệu suất CM (Tháng ${targetRec.month}/${targetRec.year})`;
        }

        const labels = targetRec.staff.map(s => s.name);
        const success = targetRec.staff.map(s => s.success || 0);
        const stacked = targetRec.staff.map(s => s.stacked || 0);
        const pending = targetRec.staff.map(s => s.pending || 0);
        const failed = targetRec.staff.map(s => s.failed || 0);

        if (this.charts.staffRenewal) {
            this.charts.staffRenewal.destroy();
        }

        this.charts.staffRenewal = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Thành công',
                        data: success,
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderRadius: 4,
                        borderSkipped: false,
                    },
                    {
                        label: 'Chồng phí',
                        data: stacked,
                        backgroundColor: 'rgba(37, 99, 235, 0.8)',
                        borderRadius: 4,
                        borderSkipped: false,
                    },
                    {
                        label: 'Chờ xử lý',
                        data: pending,
                        backgroundColor: 'rgba(245, 158, 11, 0.8)',
                        borderRadius: 4,
                        borderSkipped: false,
                    },
                    {
                        label: 'Thất bại',
                        data: failed,
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderRadius: 4,
                        borderSkipped: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11, family: 'Inter' },
                            usePointStyle: true,
                            pointStyle: 'rectRounded',
                            padding: 16,
                        },
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                    },
                },
                scales: {
                    x: {
                        stacked: true,
                        ticks: { color: '#94a3b8', font: { size: 11, family: 'Inter' } },
                        grid: { display: false },
                    },
                    y: {
                        stacked: true,
                        ticks: { color: '#64748b', font: { size: 11, family: 'Inter' } },
                        grid: { color: 'rgba(255, 255, 255, 0.03)' },
                        beginAtZero: true,
                    },
                },
            },
        });
    },

    /**
     * Chart: Students distribution by schedule.
     */
    createScheduleDistChart(classes) {
        const ctx = document.getElementById('chart-schedule-dist');
        if (!ctx) return;

        // Group by schedule prefix
        const groups = {};
        classes.filter(c => (c.schedule || c.shift_code) && (c.students || c.student_count || c.students_count || 0) > 0).forEach(c => {
            const schedStr = (c.schedule || c.shift_code || '').toUpperCase().trim();
            let prefix = 'KHÁC';
            if (schedStr.startsWith('MT')) prefix = 'MT';
            else if (schedStr.startsWith('TF')) prefix = 'TF';
            else if (schedStr.startsWith('WS')) prefix = 'WS';
            else if (schedStr.includes('KỸ') || schedStr.includes('KN') || schedStr.includes('SKILL') || schedStr.includes('SPEAKING')) prefix = 'KN';

            const stVal = c.students || c.student_count || c.students_count || 0;
            if (!groups[prefix]) groups[prefix] = 0;
            groups[prefix] += stVal;
        });

        const scheduleNames = {
            'MT': 'Thứ 2-4 (MT)',
            'TF': 'Thứ 3-5 (TF)',
            'WS': 'Thứ 4-7 (WS)',
            'KN': 'Khóa Kỹ Năng',
            'KHÁC': 'Ca khác'
        };

        const labels = Object.keys(groups).map(k => scheduleNames[k] || k);
        const data = Object.values(groups);
        const colorPalette = {
            'MT': { bg: 'rgba(99, 102, 241, 0.8)', border: '#6366f1' },
            'TF': { bg: 'rgba(16, 185, 129, 0.8)', border: '#10b981' },
            'WS': { bg: 'rgba(245, 158, 11, 0.8)', border: '#f59e0b' },
            'KN': { bg: 'rgba(168, 85, 247, 0.8)', border: '#a855f7' },
            'KHÁC': { bg: 'rgba(148, 163, 184, 0.8)', border: '#94a3b8' }
        };

        const colors = Object.keys(groups).map(k => (colorPalette[k] || colorPalette['KHÁC']).bg);
        const borderColors = Object.keys(groups).map(k => (colorPalette[k] || colorPalette['KHÁC']).border);

        this.charts.scheduleDist = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: colors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    hoverOffset: 8,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 1.5,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11, family: 'Inter' },
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 20,
                        },
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((context.raw / total) * 100).toFixed(1);
                                return ` ${context.label}: ${context.raw} HS (${pct}%)`;
                            },
                        },
                    },
                },
            },
        });
    },

    /**
     * Chart: ACS scores by staff.
     */
    createACSChart(acsStats) {
        const ctx = document.getElementById('chart-acs-score');
        if (!ctx || !acsStats.staff) return;

        const labels = acsStats.staff.map(s => s.name);
        const scores = acsStats.staff.map(s => s.score);
        const avg = acsStats.average;

        // Color bars based on score
        const bgColors = scores.map(s => {
            if (s >= 8) return 'rgba(52, 211, 153, 0.8)';
            if (s >= 7) return 'rgba(251, 191, 36, 0.8)';
            return 'rgba(248, 113, 113, 0.8)';
        });

        const borderColors = scores.map(s => {
            if (s >= 8) return '#10b981';
            if (s >= 7) return '#f59e0b';
            return '#ef4444';
        });

        this.charts.acsScore = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Điểm ACS',
                        data: scores,
                        backgroundColor: bgColors,
                        borderColor: borderColors,
                        borderWidth: 1.5,
                        borderRadius: 6,
                        borderSkipped: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 1.5,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                        callbacks: {
                            label: (context) => ` Điểm: ${context.raw.toFixed(2)} / 10`,
                        },
                    },
                    // Average line annotation
                    annotation: {
                        annotations: {
                            avgLine: {
                                type: 'line',
                                xMin: avg,
                                xMax: avg,
                                borderColor: 'rgba(129, 140, 248, 0.6)',
                                borderWidth: 2,
                                borderDash: [6, 4],
                                label: {
                                    display: true,
                                    content: `TB: ${avg.toFixed(2)}`,
                                    color: '#818cf8',
                                    font: { size: 11, family: 'Inter' },
                                    position: 'start',
                                },
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { color: '#64748b', font: { size: 11, family: 'Inter' } },
                        grid: { color: 'rgba(255, 255, 255, 0.03)' },
                        min: 0,
                        max: 10,
                    },
                    y: {
                        ticks: { color: '#94a3b8', font: { size: 12, family: 'Inter', weight: '500' } },
                        grid: { display: false },
                    },
                },
            },
        });
    },

    /**
     * Destroy all charts (cleanup).
     */
    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    },

    async renderManageClassesPage(targetContainer) {
        let isModal = false;
        let container = targetContainer;

        if (!container) {
            isModal = true;
            const modalBody = document.getElementById('modal-body');
            const modalTitle = document.getElementById('modal-title');
            if (!modalBody || !modalTitle) return;
            modalTitle.innerHTML = `🏫 QUẢN LÝ LỚP HỌC & THÊM LỚP MỚI`;
            modalBody.innerHTML = `<div class="loading-spinner"></div>`;
            if (typeof Dashboard.openModal === 'function') Dashboard.openModal();
            container = modalBody;
        }

        try {
            const res = await fetch('/api/cm/classes?include_ended=true');
            const json = await res.json();
            const classesList = (json.success ? json.data : []) || [];

            if (!this.classesMap) this.classesMap = {};
            classesList.forEach(c => {
                if (c && c.class_name) {
                    this.classesMap[c.class_name.trim()] = c;
                }
            });

            const activeClasses = classesList.filter(c => (c.status || 'Đang hoạt động') === 'Đang hoạt động');
            const endedClasses = classesList.filter(c => (c.status || 'Đang hoạt động') !== 'Đang hoạt động');

            // Fetch dynamic staff list from CSDL
            let staffRes = { cms: [], teachers: [] };
            try {
                const sRes = await fetch('/api/staff/list');
                staffRes = await sRes.json();
            } catch (e) {
                console.error('Error fetching dynamic staff list:', e);
            }

            const teachersList = (staffRes.teachers && staffRes.teachers.length > 0) ? staffRes.teachers : [];
            const cmsList = (staffRes.cms && staffRes.cms.length > 0) ? staffRes.cms : [];
            const roomsList = json.available_rooms || ['Mercury', 'Venus', 'Jupiter', 'Mars', 'Saturn', 'Uranus', 'Neptune'];

            const teachersOptionsHtml = teachersList.map(t => `<option value="${t}">${t}</option>`).join('');
            const cmsOptionsHtml = cmsList.map(c => `<option value="${c}">${c}</option>`).join('');
            const roomsOptionsHtml = roomsList.map(r => `<option value="${r}">${r}</option>`).join('');

            const makeTableRows = (list, isEndedSection) => {
                if (list.length === 0) {
                    return `<tr><td colspan="8" style="text-align:center; padding: 18px; color: #94a3b8; font-weight: 600;">${isEndedSection ? 'Chưa có lớp nào trong mục đã kết thúc' : 'Không có lớp đang hoạt động'}</td></tr>`;
                }
                return list.map((c, i) => {
                    const currentStatus = c.status || 'Đang hoạt động';
                    const isEnded = currentStatus === 'Đã kết thúc' || currentStatus === 'Không hoạt động';
                    const safeClassName = encodeURIComponent(c.class_name).replace(/'/g, "%27");

                    return `
                        <tr style="border-bottom: 1px solid #cbd5e1; background: ${i % 2 === 0 ? '#ffffff' : '#f8fafc'};">
                            <td style="font-weight: 800; color: #0f172a;">${c.class_name}</td>
                            <td><span class="badge" style="background: #e0e7ff; color: #3730a3;">${c.curriculum || (c.class_name.startsWith('Moon') ? 'Moon' : (c.class_name.startsWith('Sun') ? 'Sun' : 'Galax'))}</span></td>
                            <td style="font-size: 12px; color: #475569;">${c.schedule || c.shift_code || '—'}</td>
                            <td style="font-size: 12px; color: #475569;">${c.start_date || '—'}</td>
                            <td style="font-size: 12px; color: #0f172a;"><strong>GV:</strong> ${c.teacher || '—'} <br><strong>CM:</strong> ${c.cm_staff || '—'}</td>
                            <td style="text-align: center; font-weight: 800; color: ${c.student_count > 0 ? '#16a34a' : '#94a3b8'};">${c.student_count || 0} HS</td>
                            <td style="text-align: center;">
                                <span class="badge" style="padding: 4px 8px; font-weight: 800; ${isEnded ? 'background: #ffe4e6; color: #be123c; border: 1px solid #fda4af;' : 'background: #dcfce7; color: #15803d; border: 1px solid #86efac;'}">
                                    ${currentStatus}
                                </span>
                            </td>
                            <td style="text-align: center; white-space: nowrap;">
                                <button class="btn btn-sm" onclick="Dashboard.openEditClassModalByName('${safeClassName}');" style="background: #0284c7; color: #ffffff; padding: 5px 10px; font-size: 12px; font-weight: 800; border-radius: 6px; border: none; cursor: pointer; margin-right: 4px; box-shadow: 0 2px 6px rgba(2,132,199,0.3);">
                                    ✏️ Sửa Lớp
                                </button>
                                ${isEnded ? `
                                    <button class="btn btn-sm" onclick="Dashboard.toggleAdminClassStatus('${c.class_name}', 'Đang hoạt động');" style="background: #16a34a; color: #ffffff; padding: 5px 12px; font-size: 12px; font-weight: 800; border-radius: 6px; border: none; cursor: pointer; box-shadow: 0 2px 6px rgba(22,163,74,0.3);">
                                        🟢 Mở Lại Lớp
                                    </button>
                                ` : `
                                    <button class="btn btn-sm" onclick="Dashboard.toggleAdminClassStatus('${c.class_name}', 'Đã kết thúc');" style="background: #dc2626; color: #ffffff; padding: 5px 12px; font-size: 12px; font-weight: 800; border-radius: 6px; border: none; cursor: pointer; box-shadow: 0 2px 6px rgba(220,38,38,0.3);">
                                        🔴 Kết Thúc Lớp
                                    </button>
                                `}
                            </td>
                        </tr>
                    `;
                }).join('');
            };

            container.innerHTML = `
                <div style="padding: 10px; max-width: 1000px; margin: 0 auto;">
                    
                    <!-- FORM THÊM LỚP MỚI -->
                    <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
                        <h3 style="margin-top: 0; margin-bottom: 16px; font-size: 16px; font-weight: 900; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                            ➕ THÊM LỚP HỌC MỚI VÀO CSDL (ADMIN ONLY)
                        </h3>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 16px;">
                            <div>
                                <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Tên Lớp Mới (*):</label>
                                <input type="text" id="admin_new_class_name" placeholder="Ví dụ: Galax 3.3, Sun 2.5, Moon 4.3" style="width: 100%; padding: 8px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                            </div>

                            <div>
                                <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Chương Trình Học (*):</label>
                                <select id="admin_new_class_curriculum" style="width: 100%; padding: 8px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                    <option value="Galax">Galax</option>
                                    <option value="Sun">Sun</option>
                                    <option value="Moon">Moon</option>
                                </select>
                            </div>

                            <div class="shift-picker-card" style="grid-column: 1 / -1; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <label style="font-size: 13px; font-weight: 800; color: #1e293b;">📅 Ca Học & Thứ (*):</label>
                                    <span id="admin_new_class_shift_preview" style="font-size: 12px; font-weight: 800; background: #eff6ff; color: #1d4ed8; padding: 3px 10px; border-radius: 6px; border: 1px solid #bfdbfe;">
                                        Mã ca: Chưa chọn
                                    </span>
                                </div>
                                
                                <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
                                    <span style="font-size: 12px; font-weight: 700; color: #64748b; margin-right: 4px;">Chọn thứ:</span>
                                    <button type="button" class="day-btn-admin_new_class" data-day="T2" onclick="Dashboard.toggleDayBtn(this, 'admin_new_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T2</button>
                                    <button type="button" class="day-btn-admin_new_class" data-day="T3" onclick="Dashboard.toggleDayBtn(this, 'admin_new_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T3</button>
                                    <button type="button" class="day-btn-admin_new_class" data-day="T4" onclick="Dashboard.toggleDayBtn(this, 'admin_new_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T4</button>
                                    <button type="button" class="day-btn-admin_new_class" data-day="T5" onclick="Dashboard.toggleDayBtn(this, 'admin_new_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T5</button>
                                    <button type="button" class="day-btn-admin_new_class" data-day="T6" onclick="Dashboard.toggleDayBtn(this, 'admin_new_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T6</button>
                                    <button type="button" class="day-btn-admin_new_class" data-day="T7" onclick="Dashboard.toggleDayBtn(this, 'admin_new_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T7</button>
                                    <button type="button" class="day-btn-admin_new_class" data-day="CN" onclick="Dashboard.toggleDayBtn(this, 'admin_new_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">CN</button>
                                </div>

                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                    <div>
                                        <label style="font-size: 11.5px; font-weight: 700; color: #475569; display: block; margin-bottom: 3px;">Chọn Ca học:</label>
                                        <select id="admin_new_class_shift_time" onchange="Dashboard.updateShiftPreview('admin_new_class');" style="width: 100%; padding: 7px 10px; font-size: 12.5px; font-weight: 700; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a;">
                                            <option value="5">Ca 5 (17:30 - 19:00)</option>
                                            <option value="6">Ca 6 (19:15 - 20:45)</option>
                                            <option value="1">Ca 1 (08:00 - 09:30)</option>
                                            <option value="2">Ca 2 (09:45 - 11:15)</option>
                                            <option value="3">Ca 3 (14:00 - 15:30)</option>
                                            <option value="4">Ca 4 (15:45 - 17:15)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label style="font-size: 11.5px; font-weight: 700; color: #475569; display: block; margin-bottom: 3px;">Hoặc nhập mã ca tùy chỉnh:</label>
                                        <input type="text" id="admin_new_class_schedule_custom" oninput="Dashboard.updateShiftPreview('admin_new_class');" placeholder="Ví dụ: MT5, W5, T2/T5..." style="width: 100%; padding: 7px 10px; font-size: 12.5px; font-weight: 700; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a;" />
                                    </div>
                                </div>
                                <input type="hidden" id="admin_new_class_schedule" value="">
                            </div>

                            <div>
                                <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Ngày Bắt Đầu:</label>
                                <input type="date" id="admin_new_class_start_date" style="width: 100%; padding: 7px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                            </div>

                            <div>
                                <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Giáo Viên (GV):</label>
                                <select id="admin_new_class_teacher" style="width: 100%; padding: 8px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                    <option value="">-- Chọn Giáo Viên --</option>
                                    ${teachersOptionsHtml}
                                </select>
                            </div>

                            <div>
                                <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Phụ Trách (CM):</label>
                                <select id="admin_new_class_cm" style="width: 100%; padding: 8px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                    <option value="">-- Chọn CM Phụ Trách --</option>
                                    ${cmsOptionsHtml}
                                </select>
                            </div>

                            <div>
                                <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Phòng Học:</label>
                                <select id="admin_new_class_room" style="width: 100%; padding: 8px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                    <option value="">-- Chọn Phòng Học --</option>
                                    ${roomsOptionsHtml}
                                </select>
                            </div>
                        </div>

                        <div style="text-align: right;">
                            <button class="btn btn-primary" onclick="Dashboard.submitNewClassForm(this);" style="padding: 10px 28px; font-size: 14px; font-weight: 800; background: #2563eb; color: #ffffff; border-radius: 8px; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(37,99,235,0.35);">
                                💾 Thêm Lớp Mới Vào CSDL
                            </button>
                        </div>
                    </div>

                    <!-- BẢNG DANH SÁCH LỚP HỌC ĐANG HOẠT ĐỘNG -->
                    <h3 style="margin-top: 0; margin-bottom: 14px; font-size: 16px; font-weight: 900; color: #0f172a; display: flex; align-align: center; gap: 8px;">
                        🟢 DANH SÁCH LỚP HỌC ĐANG HOẠT ĐỘNG (${activeClasses.length} LỚP)
                    </h3>
                    <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 30px;">
                        <table class="data-table" style="width: 100%; font-size: 13px;">
                            <thead>
                                <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
                                    <th>Tên Lớp</th>
                                    <th>Chương Trình</th>
                                    <th>Ca Học / Lịch</th>
                                    <th>Ngày Bắt Đầu</th>
                                    <th>GV / CM</th>
                                    <th style="text-align: center;">Số HS</th>
                                    <th style="text-align: center;">Trạng Thái</th>
                                    <th style="text-align: center;">Thao Tác</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${makeTableRows(activeClasses, false)}
                            </tbody>
                        </table>
                    </div>

                    <!-- KHU VỰC CÁC LỚP ĐÃ KẾT THÚC / KHÔNG HOẠT ĐỘNG -->
                    <h3 style="margin-top: 0; margin-bottom: 14px; font-size: 16px; font-weight: 900; color: #be123c; display: flex; align-items: center; gap: 8px;">
                        🔴 KHU VỰC LỚP ĐÃ KẾT THÚC / KHÔNG HOẠT ĐỘNG (${endedClasses.length} LỚP)
                    </h3>
                    <div style="background: #fff5f5; border: 1.5px solid #fecdd3; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
                        <table class="data-table" style="width: 100%; font-size: 13px;">
                            <thead>
                                <tr style="background: #ffe4e6; border-bottom: 2px solid #fecdd3; color: #881337;">
                                    <th>Tên Lớp</th>
                                    <th>Chương Trình</th>
                                    <th>Ca Học / Lịch</th>
                                    <th>Ngày Bắt Đầu</th>
                                    <th>GV / CM</th>
                                    <th style="text-align: center;">Số HS</th>
                                    <th style="text-align: center;">Trạng Thái</th>
                                    <th style="text-align: center;">Thao Tác</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${makeTableRows(endedClasses, true)}
                            </tbody>
                        </table>
                    </div>

                </div>
            `;
        } catch (e) {
            container.innerHTML = `<div style="color: var(--accent-red); padding: 20px;">Lỗi tải dữ liệu lớp học: ${e.message}</div>`;
        }
    },

    openManageClassesModal() {
        this.renderManageClassesPage(null);
    },

    async submitNewClassForm(btnElement) {
        const root = btnElement ? (btnElement.closest('.modal-body') || btnElement.closest('#page-content') || document) : document;
        const className = (root.querySelector('#admin_new_class_name')?.value || '').trim();
        const curriculum = root.querySelector('#admin_new_class_curriculum')?.value || 'Galax';
        const schedule = (root.querySelector('#admin_new_class_schedule')?.value || '').trim();
        const startDate = root.querySelector('#admin_new_class_start_date')?.value || '';
        const teacher = (root.querySelector('#admin_new_class_teacher')?.value || '').trim();
        const cmStaff = (root.querySelector('#admin_new_class_cm')?.value || '').trim();
        const room = (root.querySelector('#admin_new_class_room')?.value || '').trim();

        if (!className) {
            if (typeof App !== 'undefined' && App.showToast) App.showToast('Vui lòng nhập Tên Lớp Mới!', 'error');
            return;
        }

        try {
            const res = await fetch('/api/classes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    class_name: className,
                    curriculum: curriculum,
                    schedule: schedule,
                    shift_code: schedule,
                    start_date: startDate,
                    teacher: teacher,
                    cm_staff: cmStaff,
                    room: room,
                    status: 'Đang hoạt động'
                })
            });
            const json = await res.json();
            if (json.success) {
                if (typeof App !== 'undefined' && App.showToast) App.showToast(`🎉 Đã thêm thành công lớp mới ${className}!`, 'success');
                const pageContent = document.getElementById('page-content');
                const modalBody = document.getElementById('modal-body');

                if (pageContent && pageContent.querySelector('#admin_new_class_name')) {
                    this.renderManageClassesPage(pageContent);
                } else if (modalBody && modalBody.querySelector('#admin_new_class_name')) {
                    this.openManageClassesModal();
                }

                if (typeof CMPortalModule !== 'undefined' && CMPortalModule.reloadClassesSilently) {
                    CMPortalModule.reloadClassesSilently();
                }
            } else {
                if (typeof App !== 'undefined' && App.showToast) App.showToast(`Lỗi: ${json.error}`, 'error');
            }
        } catch (e) {
            if (typeof App !== 'undefined' && App.showToast) App.showToast(`Lỗi kết nối: ${e.message}`, 'error');
        }
    },

    openEditClassModalByName(encodedClassName) {
        const className = decodeURIComponent(encodedClassName);
        const c = (this.classesMap && this.classesMap[className]) || { class_name: className };
        this.openEditClassModal(c);
    },

    async openEditClassModal(classJsonStrOrObj) {
        let c = {};
        if (typeof classJsonStrOrObj === 'object' && classJsonStrOrObj !== null) {
            c = classJsonStrOrObj;
        } else if (typeof classJsonStrOrObj === 'string') {
            try {
                c = JSON.parse(decodeURIComponent(classJsonStrOrObj));
            } catch (e) {
                const className = decodeURIComponent(classJsonStrOrObj);
                c = (this.classesMap && this.classesMap[className]) || { class_name: className };
            }
        }

        const modal = document.getElementById('modal-backdrop') || document.getElementById('modal');
        const titleEl = document.getElementById('modal-title');
        const bodyEl = document.getElementById('modal-body');

        if (titleEl) titleEl.innerText = `✏️ Chỉnh Sửa Thông Tin Lớp Học: ${c.class_name || ''}`;
        
        // Fetch dynamic staff list from CSDL
        let staffRes = { cms: [], teachers: [] };
        try {
            const sRes = await fetch('/api/staff/list');
            staffRes = await sRes.json();
        } catch (e) {
            console.error('Error fetching dynamic staff list:', e);
        }

        const cmsList = (staffRes.cms && staffRes.cms.length > 0) ? staffRes.cms : [];
        const teachersList = (staffRes.teachers && staffRes.teachers.length > 0) ? staffRes.teachers : [];
        const roomsList = ['Mercury', 'Venus', 'Jupiter', 'Mars', 'Saturn', 'Uranus', 'Neptune'];

        if (c.teacher && !teachersList.includes(c.teacher)) teachersList.push(c.teacher);
        if (c.cm_staff && !cmsList.includes(c.cm_staff)) cmsList.push(c.cm_staff);

        const tOptions = teachersList.map(t => `<option value="${t}" ${c.teacher === t ? 'selected' : ''}>${t}</option>`).join('');
        const cmOptions = cmsList.map(cm => `<option value="${cm}" ${c.cm_staff === cm ? 'selected' : ''}>${cm}</option>`).join('');
        const rOptions = roomsList.map(rm => `<option value="${rm}" ${c.room === rm ? 'selected' : ''}>${rm}</option>`).join('');

        if (bodyEl) {
            bodyEl.innerHTML = `
                <div style="padding: 10px;">
                    <input type="hidden" id="edit_original_class_name" value="${c.class_name || ''}" />

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;">
                        <div>
                            <label style="font-weight: 800; font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">Tên Lớp Học:</label>
                            <input type="text" id="edit_class_name" value="${c.class_name || ''}" class="form-control" style="width: 100%; padding: 8px 12px; font-weight: 700;" />
                        </div>
                        <div>
                            <label style="font-weight: 800; font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">Chương Trình Học:</label>
                            <select id="edit_class_curriculum" class="form-control" style="width: 100%; padding: 8px 12px; font-weight: 700;">
                                <option value="Galax" ${c.curriculum === 'Galax' ? 'selected' : ''}>Galax</option>
                                <option value="Sun" ${c.curriculum === 'Sun' ? 'selected' : ''}>Sun</option>
                                <option value="Moon" ${c.curriculum === 'Moon' ? 'selected' : ''}>Moon</option>
                            </select>
                        </div>
                    </div>

                    <div class="shift-picker-card" style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 14px 16px; margin-bottom: 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <label style="font-size: 13px; font-weight: 800; color: #1e293b;">📅 Ca Học & Thứ (*):</label>
                            <span id="edit_class_shift_preview" style="font-size: 12px; font-weight: 800; background: #eff6ff; color: #1d4ed8; padding: 3px 10px; border-radius: 6px; border: 1px solid #bfdbfe;">
                                Mã ca: ${c.schedule || c.shift_code || 'Chưa chọn'}
                            </span>
                        </div>
                        
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
                            <span style="font-size: 12px; font-weight: 700; color: #64748b; margin-right: 4px;">Chọn thứ:</span>
                            <button type="button" class="day-btn-edit_class" data-day="T2" onclick="Dashboard.toggleDayBtn(this, 'edit_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T2</button>
                            <button type="button" class="day-btn-edit_class" data-day="T3" onclick="Dashboard.toggleDayBtn(this, 'edit_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T3</button>
                            <button type="button" class="day-btn-edit_class" data-day="T4" onclick="Dashboard.toggleDayBtn(this, 'edit_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T4</button>
                            <button type="button" class="day-btn-edit_class" data-day="T5" onclick="Dashboard.toggleDayBtn(this, 'edit_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T5</button>
                            <button type="button" class="day-btn-edit_class" data-day="T6" onclick="Dashboard.toggleDayBtn(this, 'edit_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T6</button>
                            <button type="button" class="day-btn-edit_class" data-day="T7" onclick="Dashboard.toggleDayBtn(this, 'edit_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">T7</button>
                            <button type="button" class="day-btn-edit_class" data-day="CN" onclick="Dashboard.toggleDayBtn(this, 'edit_class');" style="width: 36px; height: 36px; border-radius: 50%; font-size: 12px; font-weight: 800; border: 1.5px solid #cbd5e1; background: #ffffff; color: #334155; cursor: pointer; transition: all 0.2s;">CN</button>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div>
                                <label style="font-size: 11.5px; font-weight: 700; color: #475569; display: block; margin-bottom: 3px;">Chọn Ca học:</label>
                                <select id="edit_class_shift_time" onchange="Dashboard.updateShiftPreview('edit_class');" style="width: 100%; padding: 7px 10px; font-size: 12.5px; font-weight: 700; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a;">
                                    <option value="5">Ca 5 (17:30 - 19:00)</option>
                                    <option value="6">Ca 6 (19:15 - 20:45)</option>
                                    <option value="1">Ca 1 (08:00 - 09:30)</option>
                                    <option value="2">Ca 2 (09:45 - 11:15)</option>
                                    <option value="3">Ca 3 (14:00 - 15:30)</option>
                                    <option value="4">Ca 4 (15:45 - 17:15)</option>
                                </select>
                            </div>
                            <div>
                                <label style="font-size: 11.5px; font-weight: 700; color: #475569; display: block; margin-bottom: 3px;">Hoặc nhập mã ca tùy chỉnh:</label>
                                <input type="text" id="edit_class_schedule_custom" value="${c.schedule || c.shift_code || ''}" oninput="Dashboard.updateShiftPreview('edit_class');" placeholder="Ví dụ: MT5, W5, T2/T5..." style="width: 100%; padding: 7px 10px; font-size: 12.5px; font-weight: 700; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a;" />
                            </div>
                        </div>
                        <input type="hidden" id="edit_class_schedule" value="${c.schedule || c.shift_code || ''}">
                    </div>

                    <div style="margin-bottom: 14px;">
                        <label style="font-weight: 800; font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">Ngày Bắt Đầu:</label>
                        <input type="text" id="edit_class_start_date" value="${c.start_date || ''}" class="form-control" style="width: 100%; padding: 8px 12px; font-weight: 700;" />
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;">
                        <div>
                            <label style="font-weight: 800; font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">Giáo Viên (GV):</label>
                            <select id="edit_class_teacher" class="form-control" style="width: 100%; padding: 8px 12px; font-weight: 700;">
                                <option value="">-- Chọn GV --</option>
                                ${tOptions}
                            </select>
                        </div>
                        <div>
                            <label style="font-weight: 800; font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">Phụ Trách (CM):</label>
                            <select id="edit_class_cm" class="form-control" style="width: 100%; padding: 8px 12px; font-weight: 700;">
                                <option value="">-- Chọn CM --</option>
                                ${cmOptions}
                            </select>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px;">
                        <div>
                            <label style="font-weight: 800; font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">Phòng Học:</label>
                            <select id="edit_class_room" class="form-control" style="width: 100%; padding: 8px 12px; font-weight: 700;">
                                <option value="">-- Chọn Phòng --</option>
                                ${rOptions}
                            </select>
                        </div>
                        <div>
                            <label style="font-weight: 800; font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">Trạng Thái Lớp:</label>
                            <select id="edit_class_status" class="form-control" style="width: 100%; padding: 8px 12px; font-weight: 700;">
                                <option value="Đang hoạt động" ${c.status === 'Đang hoạt động' ? 'selected' : ''}>🟢 Đang hoạt động</option>
                                <option value="Đã kết thúc" ${c.status === 'Đã kết thúc' ? 'selected' : ''}>🔴 Đã kết thúc</option>
                            </select>
                        </div>
                    </div>

                    <div style="display: flex; justify-content: flex-end; gap: 10px;">
                        <button class="btn" onclick="Dashboard.cancelEditClass();" style="padding: 8px 16px; border: 1px solid #cbd5e1; border-radius: 8px; font-weight: 700;">Hủy</button>
                        <button class="btn btn-primary" onclick="Dashboard.submitEditClassForm(this);" style="padding: 8px 22px; background: #0284c7; color: #ffffff; border: none; border-radius: 8px; font-weight: 800;">🚀 Lược Sử Cập Nhật Lớp</button>
                    </div>
                </div>
            `;
        }

        if (modal) {
            modal.classList.add('active');
            modal.style.display = 'flex';
            setTimeout(() => {
                this.initShiftPicker('edit_class', c.schedule || c.shift_code || '');
            }, 50);
        }
    },

    cancelEditClass() {
        const modal = document.getElementById('modal-backdrop') || document.getElementById('modal');
        if (modal) {
            modal.classList.remove('active');
            modal.style.display = 'none';
        }
        const pageContent = document.getElementById('page-content');
        if (pageContent && pageContent.querySelector('#admin_new_class_name')) {
            this.renderManageClassesPage(pageContent);
        } else {
            this.renderManageClassesPage(null);
        }
    },

    toggleDayBtn(btn, prefix) {
        if (btn.classList.contains('active')) {
            btn.classList.remove('active');
            btn.style.background = '#ffffff';
            btn.style.color = '#334155';
            btn.style.border = '1.5px solid #cbd5e1';
            btn.style.boxShadow = 'none';
        } else {
            btn.classList.add('active');
            btn.style.background = 'linear-gradient(135deg, #2563eb, #1d4ed8)';
            btn.style.color = '#ffffff';
            btn.style.border = 'none';
            btn.style.boxShadow = '0 4px 10px rgba(37,99,235,0.3)';
        }
        this.updateShiftPreview(prefix);
    },

    updateShiftPreview(prefix) {
        const root = document.querySelector(`.day-btn-${prefix}`)?.closest('div.shift-picker-card') || document;
        const activeBtns = Array.from(root.querySelectorAll(`.day-btn-${prefix}.active`));
        const activeDays = activeBtns.map(b => b.getAttribute('data-day'));
        const shiftTime = root.querySelector(`#${prefix}_shift_time`)?.value || '5';
        const customInput = root.querySelector(`#${prefix}_schedule_custom`);
        const hiddenInput = root.querySelector(`#${prefix}_schedule`);
        const previewSpan = root.querySelector(`#${prefix}_shift_preview`);

        let generatedCode = '';

        if (activeDays.length === 2 && activeDays.includes('T2') && activeDays.includes('T5')) {
            generatedCode = 'MT' + shiftTime;
        } else if (activeDays.length === 2 && activeDays.includes('T3') && activeDays.includes('T6')) {
            generatedCode = 'TF' + shiftTime;
        } else if (activeDays.length === 2 && activeDays.includes('T4') && activeDays.includes('T7')) {
            generatedCode = 'WS' + shiftTime;
        } else if (activeDays.length === 2 && activeDays.includes('T7') && activeDays.includes('CN')) {
            generatedCode = 'SS' + shiftTime;
        } else if (activeDays.length === 1 && activeDays[0] === 'T4') {
            generatedCode = 'W' + shiftTime; // e.g. W5 for Wed
        } else if (activeDays.length === 1 && activeDays[0] === 'T2') {
            generatedCode = 'M' + shiftTime; // e.g. M5 for Mon
        } else if (activeDays.length === 1 && activeDays[0] === 'T3') {
            generatedCode = 'T' + shiftTime; // e.g. T5 for Tue
        } else if (activeDays.length === 1 && activeDays[0] === 'T5') {
            generatedCode = 'Th' + shiftTime; // e.g. Th5 for Thu
        } else if (activeDays.length === 1 && activeDays[0] === 'T6') {
            generatedCode = 'F' + shiftTime; // e.g. F5 for Fri
        } else if (activeDays.length === 1 && activeDays[0] === 'T7') {
            generatedCode = 'Sat' + shiftTime; // e.g. Sat5 for Sat
        } else if (activeDays.length === 1 && activeDays[0] === 'CN') {
            generatedCode = 'Sun' + shiftTime; // e.g. Sun5 for Sun
        } else if (activeDays.length > 0) {
            generatedCode = activeDays.join('/') + ` (Ca ${shiftTime})`;
        }

        const customVal = (customInput?.value || '').trim();
        const finalCode = customVal || generatedCode;

        if (hiddenInput) hiddenInput.value = finalCode;
        if (previewSpan) previewSpan.innerHTML = `Mã ca: <strong>${finalCode || 'Chưa chọn'}</strong>`;
    },

    initShiftPicker(prefix, initialValue = '') {
        const val = (initialValue || '').trim().toUpperCase();
        const root = document.querySelector(`.day-btn-${prefix}`)?.closest('div.shift-picker-card') || document;
        const btns = root.querySelectorAll(`.day-btn-${prefix}`);

        if (!val) return;

        const daysToActivate = new Set();
        if (val.includes('MT') || val.includes('T2-T5') || val.includes('T2/T5')) { daysToActivate.add('T2'); daysToActivate.add('T5'); }
        else if (val.includes('TF') || val.includes('T3-T6') || val.includes('T3/T6')) { daysToActivate.add('T3'); daysToActivate.add('T6'); }
        else if (val.includes('WS') || val.includes('T4-T7') || val.includes('T4/T7')) { daysToActivate.add('T4'); daysToActivate.add('T7'); }
        else if (val.includes('SS') || val.includes('T7-CN') || val.includes('T7/CN')) { daysToActivate.add('T7'); daysToActivate.add('CN'); }
        else if (val.startsWith('W') || val.includes('T4')) { daysToActivate.add('T4'); }
        else if (val.startsWith('M') || val.includes('T2')) { daysToActivate.add('T2'); }
        else if (val.startsWith('TH') || val.includes('T5')) { daysToActivate.add('T5'); }
        else if (val.startsWith('T') || val.includes('T3')) { daysToActivate.add('T3'); }
        else if (val.startsWith('F') || val.includes('T6')) { daysToActivate.add('T6'); }
        else if (val.startsWith('SAT') || val.includes('T7')) { daysToActivate.add('T7'); }
        else if (val.startsWith('SUN') || val.includes('CN')) { daysToActivate.add('CN'); }

        btns.forEach(btn => {
            const day = btn.getAttribute('data-day');
            if (daysToActivate.has(day)) {
                btn.classList.add('active');
                btn.style.background = 'linear-gradient(135deg, #2563eb, #1d4ed8)';
                btn.style.color = '#ffffff';
                btn.style.border = 'none';
                btn.style.boxShadow = '0 4px 10px rgba(37,99,235,0.3)';
            }
        });

        // Set shift time if ending with digit
        const lastChar = val.slice(-1);
        const shiftSelect = root.querySelector(`#${prefix}_shift_time`);
        if (shiftSelect && ['1','2','3','4','5','6'].includes(lastChar)) {
            shiftSelect.value = lastChar;
        }

        this.updateShiftPreview(prefix);
    },

    async submitEditClassForm(btnElement) {
        const root = btnElement ? (btnElement.closest('.modal-body') || document) : document;
        const original_class_name = root.querySelector('#edit_original_class_name')?.value || '';
        const class_name = (root.querySelector('#edit_class_name')?.value || '').trim();
        const curriculum = root.querySelector('#edit_class_curriculum')?.value || 'Galax';
        const schedule = (root.querySelector('#edit_class_schedule')?.value || '').trim();
        const start_date = root.querySelector('#edit_class_start_date')?.value || '';
        const teacher = (root.querySelector('#edit_class_teacher')?.value || '').trim();
        const cm_staff = (root.querySelector('#edit_class_cm')?.value || '').trim();
        const room = (root.querySelector('#edit_class_room')?.value || '').trim();
        const status = root.querySelector('#edit_class_status')?.value || 'Đang hoạt động';

        if (!class_name) {
            alert('Tên lớp không được để trống!');
            return;
        }

        try {
            const res = await fetch('/api/classes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    original_class_name: original_class_name,
                    class_name: class_name,
                    curriculum: curriculum,
                    schedule: schedule,
                    shift_code: schedule,
                    start_date: start_date,
                    teacher: teacher,
                    cm_staff: cm_staff,
                    room: room,
                    status: status
                })
            });
            const json = await res.json();
            if (json.success) {
                const modal = document.getElementById('modal-backdrop') || document.getElementById('modal');
                if (modal) {
                    modal.classList.remove('active');
                    modal.style.display = 'none';
                }
                if (typeof App !== 'undefined' && App.showToast) App.showToast(`✅ ${json.message || 'Đã cập nhật lớp thành công!'}`, 'success');
                const pageContent = document.getElementById('page-content');
                if (pageContent && pageContent.querySelector('#admin_new_class_name')) {
                    this.renderManageClassesPage(pageContent);
                } else {
                    this.renderManageClassesPage(null);
                }
            } else {
                alert('Lỗi cập nhật: ' + json.error);
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        }
    },

    async toggleAdminClassStatus(className, status) {
        try {
            const res = await fetch('/api/classes/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ class_name: className, status: status })
            });
            const json = await res.json();
            if (json.success) {
                if (typeof App !== 'undefined' && App.showToast) App.showToast(`Đã chuyển lớp ${className} sang trạng thái '${status}'!`, 'info');
                const pageContent = document.getElementById('page-content');
                const modalBody = document.getElementById('modal-body');

                if (pageContent && pageContent.querySelector('#admin_new_class_name')) {
                    this.renderManageClassesPage(pageContent);
                } else if (modalBody && modalBody.querySelector('#admin_new_class_name')) {
                    this.openManageClassesModal();
                }

                if (typeof CMPortalModule !== 'undefined' && CMPortalModule.reloadClassesSilently) {
                    CMPortalModule.reloadClassesSilently();
                }
            } else {
                if (typeof App !== 'undefined' && App.showToast) App.showToast(`Lỗi: ${json.error}`, 'error');
            }
        } catch (e) {
            if (typeof App !== 'undefined' && App.showToast) App.showToast(`Lỗi kết nối: ${e.message}`, 'error');
        }
    },

    async openAddRenewalModal(prefillData = null) {
        const modalBody = document.getElementById('modal-body');
        if (!modalBody) return;

        let studentsList = [];
        try {
            const stRes = await API.get('/students');
            if (stRes.success) studentsList = stRes.data || [];
        } catch (e) { console.error('Error fetching students for renewal modal:', e); }

        const cmsOptions = ['NgọcCM', 'AnhPTT', 'AnhNV'];
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();

        const selectedMonth = prefillData ? prefillData.month : (document.getElementById('renewal-month-select')?.value?.split('-')[0] || currentMonth);
        const selectedYear = prefillData ? prefillData.year : (document.getElementById('renewal-month-select')?.value?.split('-')[1] || currentYear);

        modalBody.innerHTML = `
            <div style="padding: 10px; max-width: 580px; margin: 0 auto;">
                <h3 style="margin-top: 0; margin-bottom: 16px; font-size: 17px; font-weight: 900; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                    📋 ${prefillData ? 'CHỈNH SỬA LƯỢT TÁI PHÍ' : 'THÊM LƯỢT TÁI PHÍ HỌC SINH MỚI'}
                </h3>

                <form id="renewal-form" onsubmit="Dashboard.submitRenewalForm(event, ${prefillData ? prefillData.id : 'null'});">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Họ và Tên Học Sinh (*):</label>
                            <input type="text" id="rn_student_name" list="rn_students_datalist" placeholder="Nhập hoặc chọn học sinh..." value="${prefillData ? Utils.escapeHtml(prefillData.student_name) : ''}" required onchange="Dashboard.autoFillStudentRenewalInfo(this.value);" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                            <datalist id="rn_students_datalist">
                                ${studentsList.map(s => `<option value="${Utils.escapeHtml(s.full_name)}">${s.code || ''} - ${s.class_name || ''}</option>`).join('')}
                            </datalist>
                        </div>

                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Mã Học Sinh (EVIxxx):</label>
                            <input type="text" id="rn_student_code" placeholder="Mã HS..." value="${prefillData ? Utils.escapeHtml(prefillData.student_code) : ''}" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Lớp Học Hiện Tại:</label>
                            <input type="text" id="rn_class_name" placeholder="Tên lớp..." value="${prefillData ? Utils.escapeHtml(prefillData.class_name) : ''}" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                        </div>

                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">CM Phụ Trách (*):</label>
                            <select id="rn_cm_staff" required style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                ${cmsOptions.map(c => `<option value="${c}" ${prefillData && prefillData.cm_staff === c ? 'selected' : ''}>${c}</option>`).join('')}
                            </select>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr 1.2fr; gap: 12px; margin-bottom: 12px;">
                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Tháng Tái Phí (*):</label>
                            <select id="rn_month" required style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                ${Array.from({length: 12}, (_, i) => i + 1).map(m => `<option value="${m}" ${parseInt(selectedMonth) === m ? 'selected' : ''}>Tháng ${m}</option>`).join('')}
                            </select>
                        </div>

                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Năm (*):</label>
                            <select id="rn_year" required style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                <option value="2025" ${parseInt(selectedYear) === 2025 ? 'selected' : ''}>2025</option>
                                <option value="2026" ${parseInt(selectedYear) === 2026 ? 'selected' : ''}>2026</option>
                                <option value="2027" ${parseInt(selectedYear) === 2027 ? 'selected' : ''}>2027</option>
                            </select>
                        </div>

                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Trạng Thái Tái Phí (*):</label>
                            <select id="rn_status" required style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                                <option value="success" ${prefillData && prefillData.status === 'success' ? 'selected' : ''}>🟢 Thành Công (Đúng hạn)</option>
                                <option value="stacked" ${prefillData && prefillData.status === 'stacked' ? 'selected' : ''}>🔵 Chồng Phí (Nộp trước hạn)</option>
                                <option value="pending" ${!prefillData || prefillData.status === 'pending' ? 'selected' : ''}>🟡 Chờ Xử Lý (Đang đôn đốc)</option>
                                <option value="failed" ${prefillData && prefillData.status === 'failed' ? 'selected' : ''}>🔴 Thất Bại (Không tái phí)</option>
                            </select>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 12px; margin-bottom: 12px;">
                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Gói Phí Tái Phí (Ghi chú gói):</label>
                            <input type="text" id="rn_fee_package" placeholder="Ví dụ: 15,000,000đ (6 tháng)" value="${prefillData ? Utils.escapeHtml(prefillData.fee_package) : ''}" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                        </div>

                        <div>
                            <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Hạn Hết Phí Dự Kiến:</label>
                            <input type="text" id="rn_expected_expiry_date" placeholder="Ví dụ: 18/01/2028 hoặc DD/MM/YYYY" value="${prefillData ? Utils.escapeHtml(prefillData.expected_expiry_date || prefillData.due_date || '') : ''}" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700; background: #ffffff; color: #0f172a;">
                        </div>
                    </div>

                    <div style="margin-bottom: 18px;">
                        <label style="font-size: 12.5px; font-weight: 800; color: #334155; margin-bottom: 4px; display: block;">Ghi Chú Trao Đổi Phụ Huynh / Chi Tiết:</label>
                        <textarea id="rn_notes" rows="3" placeholder="Nhập ghi chú tình trạng chăm sóc tái phí..." style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; background: #ffffff; color: #0f172a;">${prefillData ? Utils.escapeHtml(prefillData.notes) : ''}</textarea>
                    </div>

                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button type="button" class="btn" onclick="Dashboard.closeModal();" style="padding: 10px 20px; border: 1px solid #cbd5e1; border-radius: 8px; font-weight: 700;">Hủy</button>
                        <button type="submit" id="btn-submit-renewal" class="btn btn-primary" style="padding: 10px 28px; font-size: 14px; font-weight: 800; background: #2563eb; color: #ffffff; border-radius: 8px; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(37,99,235,0.35);">
                            💾 Lưu Lượt Tái Phí
                        </button>
                    </div>
                </form>
            </div>
        `;

        this.openModal();
    },

    async autoFillStudentRenewalInfo(nameVal) {
        if (!nameVal) return;
        try {
            const res = await API.get('/students', { search: nameVal });
            if (res.success && res.data && res.data.length > 0) {
                const match = res.data.find(s => s.full_name.toLowerCase() === nameVal.toLowerCase()) || res.data[0];
                if (match) {
                    if (document.getElementById('rn_student_code')) document.getElementById('rn_student_code').value = match.code || '';
                    if (document.getElementById('rn_class_name')) document.getElementById('rn_class_name').value = match.class_name || '';
                    if (document.getElementById('rn_cm_staff') && match.cm_staff) document.getElementById('rn_cm_staff').value = match.cm_staff;
                    if (document.getElementById('rn_expected_expiry_date') && match.expiry_date) document.getElementById('rn_expected_expiry_date').value = match.expiry_date;
                }
            }
        } catch (e) { console.error('Error auto filling student info:', e); }
    },

    async submitRenewalForm(event, renewalId = null) {
        event.preventDefault();

        const studentName = (document.getElementById('rn_student_name')?.value || '').trim();
        const studentCode = (document.getElementById('rn_student_code')?.value || '').trim();
        const className = (document.getElementById('rn_class_name')?.value || '').trim();
        const cmStaff = (document.getElementById('rn_cm_staff')?.value || '').trim();
        const month = parseInt(document.getElementById('rn_month')?.value || 8);
        const year = parseInt(document.getElementById('rn_year')?.value || 2026);
        const status = (document.getElementById('rn_status')?.value || 'pending').trim();
        const feePackage = (document.getElementById('rn_fee_package')?.value || '').trim();
        const expectedExpiryDate = (document.getElementById('rn_expected_expiry_date')?.value || '').trim();
        const notes = (document.getElementById('rn_notes')?.value || '').trim();

        if (!studentName) {
            if (typeof App !== 'undefined' && App.showToast) App.showToast('Vui lòng nhập tên học sinh!', 'error');
            return;
        }

        const submitBtn = document.getElementById('btn-submit-renewal');
        if (submitBtn) { submitBtn.disabled = true; submitBtn.innerText = '⏳ Đang lưu...'; }

        try {
            const res = await API.saveRenewal({
                id: renewalId,
                student_name: studentName,
                student_code: studentCode,
                class_name: className,
                cm_staff: cmStaff,
                month: month,
                year: year,
                status: status,
                fee_package: feePackage,
                expected_expiry_date: expectedExpiryDate,
                due_date: expectedExpiryDate,
                notes: notes
            });

            if (res.success) {
                if (typeof App !== 'undefined' && App.showToast) App.showToast(res.message || 'Lưu tái phí thành công!', 'success');
                this.closeModal();

                if (typeof RenewalsModule !== 'undefined' && RenewalsModule.loadData) {
                    RenewalsModule.loadData();
                }

                const summaryRes = await API.getDashboard();
                if (summaryRes.success) {
                    this.data = summaryRes.data;
                    this.renderRenewalTable(this.data.renewal_monthly, month, year);
                    if (this.charts && this.charts.renewalTrend) this.createRenewalTrendChart(this.data.renewal_monthly);
                    if (this.charts && this.charts.staffRenewal) this.createStaffRenewalChart(this.data.renewal_monthly);
                }
            } else {
                if (typeof App !== 'undefined' && App.showToast) App.showToast(`Lỗi: ${res.error}`, 'error');
            }
        } catch (e) {
            if (typeof App !== 'undefined' && App.showToast) App.showToast(`Lỗi kết nối: ${e.message}`, 'error');
        } finally {
            if (submitBtn) { submitBtn.disabled = false; submitBtn.innerText = '💾 Lưu Lượt Tái Phí'; }
        }
    },
};
