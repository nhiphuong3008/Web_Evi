/**
 * EVI Dashboard - Admin Audit Logs & Activity Notifications Module
 * Trình quản lý Nhật ký hoạt động & Thông báo thời gian thực dành cho Admin.
 */

const AuditLogsModule = {
    logsData: [],
    totalLogs: 0,
    currentPage: 1,
    pageSize: 20,
    filters: {
        username: '',
        action_type: '',
        target_module: '',
        search: ''
    },

    /**
     * Render trang Nhật ký hoạt động dành cho Admin
     */
    async render(container) {
        if (!AuthModule.isAdmin()) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 40px; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 12px;">🔒</div>
                    <h3 style="color: #f87171;">Quyền Truy Cập Bị Hạn Chế</h3>
                    <p style="color: #94a3b8;">Trang Nhật Ký Hoạt Động chỉ dành riêng cho tài khoản Quản trị viên (Admin).</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="audit-logs-page" style="padding-bottom: 30px;">
                <!-- Header Stats Cards -->
                <div class="kpi-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px;">
                    <div class="kpi-card" style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="font-size: 24px;">📊</span>
                            <span class="badge" style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-weight: 700;">Tổng thao tác</span>
                        </div>
                        <div id="stat-total-logs" style="font-size: 28px; font-weight: 900; color: #0f172a; margin-top: 12px;">...</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px; font-weight: 600;">Tất cả vết ghi trong CSDL</div>
                    </div>

                    <div class="kpi-card" style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="font-size: 24px;">📋</span>
                            <span class="badge" style="background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; font-weight: 700;">Hoạt động CM</span>
                        </div>
                        <div id="stat-cm-logs" style="font-size: 28px; font-weight: 900; color: #0f172a; margin-top: 12px;">...</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px; font-weight: 600;">Thao tác từ Class Managers</div>
                    </div>

                    <div class="kpi-card" style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="font-size: 24px;">👑</span>
                            <span class="badge" style="background: #fef9c3; color: #a16207; border: 1px solid #fef08a; font-weight: 700;">Tác vụ Admin</span>
                        </div>
                        <div id="stat-admin-logs" style="font-size: 28px; font-weight: 900; color: #0f172a; margin-top: 12px;">...</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px; font-weight: 600;">Thao tác từ Quản trị viên</div>
                    </div>

                    <div class="kpi-card" style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="font-size: 24px;">✏️</span>
                            <span class="badge" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; font-weight: 700;">Chỉnh sửa & Xóa</span>
                        </div>
                        <div id="stat-mod-logs" style="font-size: 28px; font-weight: 900; color: #0f172a; margin-top: 12px;">...</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px; font-weight: 600;">Thao tác làm thay đổi dữ liệu</div>
                    </div>
                </div>

                <!-- Control & Filter Bar -->
                <div class="card" style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 18px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                    <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center; justify-content: space-between;">
                        <!-- Filter Group -->
                        <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center; flex: 1;">
                            <input type="text" id="audit-search-input" placeholder="🔍 Tìm kiếm theo tên user, mã HS, nội dung..." 
                                   value="${AuthModule.escapeHtml(this.filters.search)}"
                                   onkeyup="if(event.key==='Enter') AuditLogsModule.handleSearch();"
                                   style="min-width: 240px; height: 38px; padding: 0 14px; background: #f8fafc; border: 1.5px solid #cbd5e1; color: #0f172a; border-radius: 8px; font-size: 13px; font-weight: 600;">

                            <select id="audit-filter-action" onchange="AuditLogsModule.handleFilterChange();" style="height: 38px; padding: 0 12px; background: #f8fafc; border: 1.5px solid #cbd5e1; color: #0f172a; border-radius: 8px; font-size: 13px; font-weight: 600;">
                                <option value="">-- Tất cả loại thao tác --</option>
                                <option value="ATTENDANCE" ${this.filters.action_type === 'ATTENDANCE' ? 'selected' : ''}>✅ Điểm danh</option>
                                <option value="GRADE" ${this.filters.action_type === 'GRADE' ? 'selected' : ''}>💯 Nhập điểm thi</option>
                                <option value="RENEWAL_STAGE" ${this.filters.action_type === 'RENEWAL_STAGE' ? 'selected' : ''}>💳 CRM Tái phí (Bước)</option>
                                <option value="RENEWAL_PAYMENT" ${this.filters.action_type === 'RENEWAL_PAYMENT' ? 'selected' : ''}>💰 Đóng tiền tái phí</option>
                                <option value="INTERACTION" ${this.filters.action_type === 'INTERACTION' ? 'selected' : ''}>📖 Nhật ký chăm sóc PH</option>
                                <option value="CLASS_EDIT" ${this.filters.action_type === 'CLASS_EDIT' ? 'selected' : ''}>🏫 Sửa / Thêm lớp</option>
                                <option value="UPDATE" ${this.filters.action_type === 'UPDATE' ? 'selected' : ''}>✏️ Chỉnh sửa bản ghi</option>
                                <option value="DELETE" ${this.filters.action_type === 'DELETE' ? 'selected' : ''}>🗑️ Xóa bản ghi</option>
                            </select>

                            <select id="audit-filter-module" onchange="AuditLogsModule.handleFilterChange();" style="height: 38px; padding: 0 12px; background: #f8fafc; border: 1.5px solid #cbd5e1; color: #0f172a; border-radius: 8px; font-size: 13px; font-weight: 600;">
                                <option value="">-- Tất cả Module --</option>
                                <option value="ATTENDANCE" ${this.filters.target_module === 'ATTENDANCE' ? 'selected' : ''}>Điểm Danh</option>
                                <option value="GRADE" ${this.filters.target_module === 'GRADE' ? 'selected' : ''}>Điểm Thi</option>
                                <option value="RENEWAL" ${this.filters.target_module === 'RENEWAL' ? 'selected' : ''}>Quản Lý Tái Phí</option>
                                <option value="INTERACTION" ${this.filters.target_module === 'INTERACTION' ? 'selected' : ''}>Nhật Ký Tương Tác</option>
                                <option value="CLASS" ${this.filters.target_module === 'CLASS' ? 'selected' : ''}>Lớp Học</option>
                                <option value="STUDENT" ${this.filters.target_module === 'STUDENT' ? 'selected' : ''}>Học Sinh</option>
                            </select>

                            <button class="btn btn-primary" onclick="AuditLogsModule.handleSearch();" style="height: 38px; padding: 0 16px; font-size: 13px; font-weight: 700; background: linear-gradient(135deg, #2563eb, #1d4ed8);">
                                🔍 Lọc
                            </button>
                            <button class="btn" onclick="AuditLogsModule.resetFilters();" style="height: 38px; padding: 0 14px; font-size: 13px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #475569; font-weight: 600;">
                                🧹 Đặt lại
                            </button>
                        </div>

                        <!-- Actions Group -->
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <button class="btn" onclick="AuditLogsModule.markAllAsRead();" style="height: 38px; padding: 0 14px; font-size: 12.5px; background: #ecfdf5; border: 1.5px solid #a7f3d0; color: #047857; font-weight: 700;" title="Đánh dấu tất cả thông báo là đã đọc">
                                ✅ Đã đọc tất cả
                            </button>
                            <button class="btn" onclick="AuditLogsModule.loadLogs();" style="height: 38px; padding: 0 14px; font-size: 12.5px; background: #eff6ff; border: 1.5px solid #bfdbfe; color: #1d4ed8; font-weight: 700;" title="Tải lại dữ liệu">
                                🔄 Tải lại
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Logs Table Card -->
                <div class="card" style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 14px; padding: 0; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
                    <div style="padding: 16px 20px; border-bottom: 2px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc;">
                        <div style="font-size: 15px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                            <span>📜</span> Bảng Chi Tiết Nhật Ký Thao Tác Người Dùng
                        </div>
                        <div id="audit-records-count" style="font-size: 12.5px; color: #64748b; font-weight: 700;">Đang tải...</div>
                    </div>

                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
                            <thead>
                                <tr style="background: #f1f5f9; color: #334155; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #cbd5e1; font-weight: 800;">
                                    <th style="padding: 12px 16px; width: 140px;">Thời Gian</th>
                                    <th style="padding: 12px 16px; width: 160px;">Người Thực Hiện</th>
                                    <th style="padding: 12px 16px; width: 130px;">Phân Loại</th>
                                    <th style="padding: 12px 16px; width: 120px;">Module</th>
                                    <th style="padding: 12px 16px; width: 120px;">Đối Tượng</th>
                                    <th style="padding: 12px 16px;">Nội Dung Chi Tiết Thao Tác</th>
                                </tr>
                            </thead>
                            <tbody id="audit-logs-tbody">
                                <tr>
                                    <td colspan="6" style="text-align: center; padding: 40px; color: #64748b;">
                                        <div class="loading-spinner" style="margin: 0 auto 10px;"></div>
                                        Đang truy vấn lịch sử hoạt động...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Pagination Footer -->
                    <div style="padding: 14px 20px; border-top: 1.5px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; background: #f8fafc;">
                        <div id="audit-pagination-info" style="font-size: 12.5px; color: #475569; font-weight: 600;">Trang 1 / 1</div>
                        <div style="display: flex; gap: 6px;" id="audit-pagination-btns">
                            <button class="btn btn-sm" onclick="AuditLogsModule.changePage(-1);" id="btn-prev-page" style="padding: 6px 14px; font-size: 12px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #334155; font-weight: 700;">◄ Trang trước</button>
                            <button class="btn btn-sm" onclick="AuditLogsModule.changePage(1);" id="btn-next-page" style="padding: 6px 14px; font-size: 12px; background: #ffffff; border: 1.5px solid #cbd5e1; color: #334155; font-weight: 700;">Trang sau ►</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await this.loadLogs();
    },

    /**
     * Load data from API
     */
    async loadLogs() {
        try {
            const tbody = document.getElementById('audit-logs-tbody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 30px; color: #94a3b8;">
                            <div class="loading-spinner" style="margin: 0 auto 10px;"></div>
                            Đang tải lịch sử hoạt động...
                        </td>
                    </tr>
                `;
            }

            const offset = (this.currentPage - 1) * this.pageSize;
            const params = {
                limit: this.pageSize,
                offset: offset
            };

            if (this.filters.username) params.username = this.filters.username;
            if (this.filters.action_type) params.action_type = this.filters.action_type;
            if (this.filters.target_module) params.target_module = this.filters.target_module;
            if (this.filters.search) params.search = this.filters.search;

            const res = await API.get('/admin/audit-logs', params);

            if (!res.success) {
                throw new Error(res.error || 'Không thể tải nhật ký');
            }

            this.logsData = res.data || [];
            this.totalLogs = res.total || 0;

            // Update stats
            document.getElementById('stat-total-logs').innerText = (res.total || 0).toLocaleString('vi-VN');
            document.getElementById('stat-cm-logs').innerText = (res.cm_actions_count || 0).toLocaleString('vi-VN');
            document.getElementById('stat-admin-logs').innerText = (res.admin_actions_count || 0).toLocaleString('vi-VN');
            document.getElementById('stat-mod-logs').innerText = (res.modification_count || 0).toLocaleString('vi-VN');

            document.getElementById('audit-records-count').innerText = `Hiển thị ${this.logsData.length} / Tổng ${this.totalLogs} vết ghi`;

            this.renderTable();
            this.renderPagination();

        } catch (e) {
            console.error('Error loading audit logs:', e);
            const tbody = document.getElementById('audit-logs-tbody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 30px; color: #f87171;">
                            ⚠️ Lỗi tải dữ liệu: ${AuthModule.escapeHtml(e.message)}
                        </td>
                    </tr>
                `;
            }
        }
    },

    renderTable() {
        const tbody = document.getElementById('audit-logs-tbody');
        if (!tbody) return;

        if (this.logsData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 60px 40px; color: #64748b;">
                        <div style="font-size: 40px; margin-bottom: 12px;">📭</div>
                        <div style="font-size: 15px; font-weight: 700; color: #334155; margin-bottom: 6px;">Chưa có hoạt động nào được ghi nhận</div>
                        <div style="font-size: 13px; color: #94a3b8;">Nhật ký sẽ tự động ghi lại khi người dùng thực hiện các thao tác trên hệ thống (điểm danh, nhập điểm, chăm sóc PH...)</div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.logsData.map(item => {
            const roleBadge = item.user_role === 'admin' 
                ? '<span class="badge" style="background: #fef3c7; color: #92400e; border: 1px solid #fde68a; font-size: 10.5px; font-weight: 700;">👑 Admin</span>'
                : '<span class="badge" style="background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; font-size: 10.5px; font-weight: 700;">📋 CM</span>';

            const actionBadge = this.getActionBadge(item.action_type);
            const moduleBadge = this.getModuleBadge(item.target_module);

            const isNew = !item.is_read_by_admin ? '<span style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; margin-right: 6px;" title="Thông báo chưa đọc"></span>' : '';

            return `
                <tr style="border-bottom: 1px solid #e2e8f0; transition: background 0.15s ease;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
                    <td style="padding: 12px 16px; color: #1e293b; white-space: nowrap;">
                        ${isNew}
                        <div style="font-weight: 700; font-size: 12.5px; color: #0f172a;">${item.created_at || ''}</div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 2px; font-weight: 600;">⏱️ ${item.time_ago || ''}</div>
                    </td>
                    <td style="padding: 12px 16px;">
                        <div style="font-weight: 800; color: #0f172a; font-size: 13px;">${AuthModule.escapeHtml(item.user_fullname)}</div>
                        <div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
                            <span style="font-size: 11px; color: #64748b; font-weight: 600;">@${AuthModule.escapeHtml(item.username)}</span>
                            ${roleBadge}
                        </div>
                    </td>
                    <td style="padding: 12px 16px;">${actionBadge}</td>
                    <td style="padding: 12px 16px;">${moduleBadge}</td>
                    <td style="padding: 12px 16px; font-weight: 800; color: #0284c7;">
                        ${AuthModule.escapeHtml(item.target_id || '—')}
                    </td>
                    <td style="padding: 12px 16px; color: #334155; line-height: 1.5; font-size: 13px; font-weight: 500;">
                        ${AuthModule.escapeHtml(item.description)}
                    </td>
                </tr>
            `;
        }).join('');
    },

    getActionBadge(actionType) {
        switch (actionType) {
            case 'ATTENDANCE':
                return '<span class="badge" style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; font-weight: 700;">✅ Điểm danh</span>';
            case 'GRADE':
                return '<span class="badge" style="background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; font-weight: 700;">💯 Điểm thi</span>';
            case 'RENEWAL_STAGE':
                return '<span class="badge" style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-weight: 700;">💳 Đổi bước CRM</span>';
            case 'RENEWAL_PAYMENT':
                return '<span class="badge" style="background: #fef9c3; color: #a16207; border: 1px solid #fef08a; font-weight: 700;">💰 Thu học phí</span>';
            case 'INTERACTION':
                return '<span class="badge" style="background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; font-weight: 700;">📖 Care PH</span>';
            case 'CLASS_EDIT':
                return '<span class="badge" style="background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; font-weight: 700;">🏫 Sửa Lớp</span>';
            case 'CREATE':
                return '<span class="badge" style="background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; font-weight: 700;">➕ Thêm mới</span>';
            case 'UPDATE':
                return '<span class="badge" style="background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; font-weight: 700;">✏️ Chỉnh sửa</span>';
            case 'DELETE':
                return '<span class="badge" style="background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; font-weight: 700;">🗑️ Xóa bản ghi</span>';
            default:
                return `<span class="badge" style="background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; font-weight: 700;">${AuthModule.escapeHtml(actionType)}</span>`;
        }
    },

    getModuleBadge(moduleName) {
        switch (moduleName) {
            case 'ATTENDANCE':
                return '<span style="color: #047857; font-weight: 700;">Điểm danh</span>';
            case 'GRADE':
                return '<span style="color: #7e22ce; font-weight: 700;">Bảng điểm</span>';
            case 'RENEWAL':
                return '<span style="color: #b45309; font-weight: 700;">Tái phí CRM</span>';
            case 'INTERACTION':
                return '<span style="color: #0284c7; font-weight: 700;">Tương tác PH</span>';
            case 'CLASS':
                return '<span style="color: #c2410c; font-weight: 700;">Lớp học</span>';
            case 'STUDENT':
                return '<span style="color: #6d28d9; font-weight: 700;">Học sinh</span>';
            case 'USER':
                return '<span style="color: #be185d; font-weight: 700;">User Hệ thống</span>';
            default:
                return `<span style="color: #64748b; font-weight: 600;">${AuthModule.escapeHtml(moduleName)}</span>`;
        }
    },

    renderPagination() {
        const totalPages = Math.ceil(this.totalLogs / this.pageSize) || 1;
        document.getElementById('audit-pagination-info').innerText = `Trang ${this.currentPage} / ${totalPages} (Tổng ${this.totalLogs} vết ghi)`;

        const btnPrev = document.getElementById('btn-prev-page');
        const btnNext = document.getElementById('btn-next-page');

        if (btnPrev) btnPrev.disabled = (this.currentPage <= 1);
        if (btnNext) btnNext.disabled = (this.currentPage >= totalPages);
    },

    changePage(delta) {
        const totalPages = Math.ceil(this.totalLogs / this.pageSize) || 1;
        const newPage = this.currentPage + delta;
        if (newPage >= 1 && newPage <= totalPages) {
            this.currentPage = newPage;
            this.loadLogs();
        }
    },

    handleSearch() {
        const input = document.getElementById('audit-search-input');
        if (input) {
            this.filters.search = input.value.trim();
            this.currentPage = 1;
            this.loadLogs();
        }
    },

    handleFilterChange() {
        const actSelect = document.getElementById('audit-filter-action');
        const modSelect = document.getElementById('audit-filter-module');
        if (actSelect) this.filters.action_type = actSelect.value;
        if (modSelect) this.filters.target_module = modSelect.value;
        this.currentPage = 1;
        this.loadLogs();
    },

    resetFilters() {
        this.filters = { username: '', action_type: '', target_module: '', search: '' };
        this.currentPage = 1;

        const sInput = document.getElementById('audit-search-input');
        const actSelect = document.getElementById('audit-filter-action');
        const modSelect = document.getElementById('audit-filter-module');

        if (sInput) sInput.value = '';
        if (actSelect) actSelect.value = '';
        if (modSelect) modSelect.value = '';

        this.loadLogs();
    },

    async markAllAsRead() {
        try {
            const res = await API.post('/admin/notifications/mark-read', {});
            if (res.success) {
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast('Đã đánh dấu tất cả thông báo là đã đọc!', 'success');
                }
                if (typeof AuthModule !== 'undefined' && AuthModule.loadNotifications) {
                    AuthModule.loadNotifications();
                }
                this.loadLogs();
            }
        } catch (e) {
            console.error('Error marking notifications read:', e);
        }
    }
};
