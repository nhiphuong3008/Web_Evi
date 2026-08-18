/**
 * EVI Dashboard - User Management Module (Admin)
 */

const UsersModule = {
    users: [],

    async init() {
        if (!AuthModule.isAdmin()) {
            this.renderAccessDenied();
            return;
        }
        await this.loadUsers();
    },

    renderAccessDenied() {
        const container = document.getElementById('page-content');
        if (!container) return;

        container.innerHTML = `
            <div class="card" style="text-align: center; padding: 60px 20px; max-width: 500px; margin: 40px auto;">
                <div style="font-size: 50px; margin-bottom: 16px;">⚠️</div>
                <h2 style="margin: 0 0 10px; color: #ef4444;">Truy Cập Bị Từ Chối</h2>
                <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 24px;">
                    Trang Quản lý Người dùng chỉ dành riêng cho tài khoản Quản Trị Viên (Admin).
                </p>
                <button class="btn btn-primary" onclick="AuthModule.showLoginModal();">
                    🔐 Đăng nhập với tài khoản Admin
                </button>
            </div>
        `;
    },

    async loadUsers() {
        const container = document.getElementById('page-content');
        if (!container) return;

        container.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Đang tải danh sách người dùng...</div>
            </div>
        `;

        try {
            const res = await API.getUsers();
            if (res.success) {
                this.users = res.users || [];
                this.renderUserList();
            } else {
                App.showToast(res.error || 'Lỗi lấy danh sách người dùng', 'error');
            }
        } catch (e) {
            console.error('Error loading users:', e);
            App.showToast('Không thể kết nối máy chủ', 'error');
        }
    },

    renderUserList() {
        const container = document.getElementById('page-content');
        if (!container) return;

        const usersTableRows = this.users.map(u => {
            let roleBadge;
            if (u.role === 'admin') {
                roleBadge = '<span class="badge badge-admin">👑 Admin</span>';
            } else if (u.role === 'teacher' || u.role === 'gv') {
                roleBadge = `<span class="badge" style="background: rgba(59,130,246,0.15); color: #3b82f6; border: 1px solid rgba(59,130,246,0.3); font-weight: 700;">🎓 Giáo Viên</span>`;
            } else {
                roleBadge = `<span class="badge badge-cm">📋 CM (${u.cm_staff_name || 'Chưa gán'})</span>`;
            }

            // Cột PHỤ TRÁCH CM: chỉ hiển thị cho CM, Admin hiện "Tất cả lớp", GV hiện "—"
            let cmAssignmentText;
            if (u.role === 'admin') {
                cmAssignmentText = 'Tất cả lớp (Admin)';
            } else if (u.role === 'cm') {
                cmAssignmentText = AuthModule.escapeHtml(u.cm_staff_name || 'Chưa gán');
            } else {
                cmAssignmentText = '—';
            }

            const statusBadge = u.is_active 
                ? '<span class="badge" style="background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3);">🟢 Hoạt động</span>'
                : '<span class="badge" style="background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3);">🔴 Đã khóa</span>';

            return `
                <tr>
                    <td style="font-weight: 600; color: var(--text-muted);">#${u.id}</td>
                    <td>
                        <div style="font-weight: 600; color: var(--text-heading);">${AuthModule.escapeHtml(u.username)}</div>
                        <div style="font-size: 12px; color: var(--text-muted);">${AuthModule.escapeHtml(u.email || '—')}</div>
                    </td>
                    <td style="font-weight: 600;">${AuthModule.escapeHtml(u.full_name)}</td>
                    <td>${roleBadge}</td>
                    <td>${cmAssignmentText}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <div style="display: flex; gap: 6px;">
                            <button class="btn btn-sm" onclick="UsersModule.openUserModal(${u.id});" style="padding: 4px 8px; font-size: 12px; background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3);" title="Chỉnh sửa">
                                ✏️ Sửa
                            </button>
                            ${u.username !== 'admin' ? `
                                <button class="btn btn-sm" onclick="UsersModule.confirmDeleteUser(${u.id}, '${AuthModule.escapeHtml(u.username)}');" style="padding: 4px 8px; font-size: 12px; background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3);" title="Xóa">
                                    🗑️ Xóa
                                </button>
                            ` : ''}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        container.innerHTML = `
            <div class="user-management-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h2 style="margin: 0; font-size: 20px; color: var(--text-heading);">👤 Quản Lý Tài Khoản Người Dùng</h2>
                    <p style="margin: 4px 0 0; font-size: 13px; color: var(--text-muted);">Quản lý tài khoản Admin & phân quyền Class Manager (CM) quản lý lớp</p>
                </div>
                <button class="btn btn-primary" onclick="UsersModule.openUserModal();" style="padding: 10px 18px; font-weight: 600;">
                    ➕ Thêm Tài Khoản Mới
                </button>
            </div>

            <div class="card" style="padding: 0; overflow: hidden; border-radius: 12px;">
                <div class="table-responsive">
                    <table class="data-table" style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: rgba(30,41,59,0.8); text-align: left;">
                                <th style="padding: 12px 16px; width: 60px;">ID</th>
                                <th style="padding: 12px 16px;">Tên Đăng Nhập</th>
                                <th style="padding: 12px 16px;">Họ Và Tên</th>
                                <th style="padding: 12px 16px;">Vai Trò</th>
                                <th style="padding: 12px 16px;">Phụ Trách CM</th>
                                <th style="padding: 12px 16px;">Trạng Thái</th>
                                <th style="padding: 12px 16px; width: 130px;">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${usersTableRows.length > 0 ? usersTableRows : `
                                <tr>
                                    <td colspan="7" style="text-align: center; padding: 40px; color: var(--text-muted);">
                                        Chưa có tài khoản nào trong hệ thống.
                                    </td>
                                </tr>
                            `}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    openUserModal(userId = null) {
        const isEdit = !!userId;
        const user = isEdit ? this.users.find(u => u.id === userId) : null;

        const modalBody = document.getElementById('modal-body');
        const modalTitle = document.getElementById('modal-title');
        if (!modalBody || !modalTitle) return;

        modalTitle.innerHTML = isEdit ? `✏️ Chỉnh Sửa Tài Khoản: ${user ? user.username : ''}` : '➕ Tạo Tài Khoản Mới';

        modalBody.innerHTML = `
            <form id="user-form" onsubmit="UsersModule.handleSaveUser(event, ${userId});" style="max-width: 500px; margin: 0 auto;">
                <div id="user-form-error" class="alert alert-danger" style="display: none; margin-bottom: 15px; font-size: 13px; padding: 10px 14px; border-radius: 8px; background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #f87171;"></div>

                <div class="form-group" style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Tên đăng nhập <span style="color: #ef4444;">*</span></label>
                    <input type="text" id="user-form-username" class="form-control" value="${user ? AuthModule.escapeHtml(user.username) : ''}" ${isEdit ? 'disabled' : 'required'} style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main);">
                </div>

                <div class="form-group" style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Họ và Tên <span style="color: #ef4444;">*</span></label>
                    <input type="text" id="user-form-fullname" class="form-control" value="${user ? AuthModule.escapeHtml(user.full_name) : ''}" required style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main);">
                </div>

                <div class="form-group" style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Email</label>
                    <input type="email" id="user-form-email" class="form-control" value="${user ? AuthModule.escapeHtml(user.email) : ''}" placeholder="email@evi.edu.vn" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main);">
                </div>

                <div class="form-group" style="margin-bottom: 14px;">
                    <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Mật khẩu ${isEdit ? '<span style="font-weight: normal; color: var(--text-muted);">(Để trống nếu giữ nguyên)</span>' : '<span style="color: #ef4444;">*</span>'}</label>
                    <input type="password" id="user-form-password" class="form-control" ${isEdit ? '' : 'required'} placeholder="${isEdit ? 'Nhập mật khẩu mới nếu muốn đổi' : 'Mật khẩu'}" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main);">
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                    <div class="form-group">
                        <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Vai trò</label>
                        <select id="user-form-role" class="form-control" onchange="UsersModule.toggleCmStaffField();" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main);">
                            <option value="cm" ${user && user.role === 'cm' ? 'selected' : ''}>Class Manager (CM)</option>
                            <option value="teacher" ${user && user.role === 'teacher' ? 'selected' : ''}>🎓 Giáo Viên (GV)</option>
                            <option value="admin" ${user && user.role === 'admin' ? 'selected' : ''}>👑 Quản Trị Viên (Admin)</option>
                        </select>
                    </div>

                    <div class="form-group" id="cm-staff-field-wrapper" style="${user && (user.role === 'teacher' || user.role === 'admin') ? 'display: none;' : ''}">
                        <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px;">Bí danh CM phân công lớp</label>
                        <input type="text" id="user-form-cmstaff" class="form-control" value="${user ? AuthModule.escapeHtml(user.cm_staff_name) : ''}" placeholder="VD: AnhPTT, AnhNV, NgọcCM..." style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main);">
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: flex; align-items: center; gap: 8px; font-size: 14px; cursor: pointer;">
                        <input type="checkbox" id="user-form-active" ${!user || user.is_active ? 'checked' : ''} style="width: 18px; height: 18px;">
                        <span>Kích hoạt tài khoản này (Active)</span>
                    </label>
                </div>

                <div style="display: flex; gap: 10px;">
                    <button type="submit" id="btn-save-user" class="btn btn-primary" style="flex: 1; padding: 12px; font-weight: 600;">
                        💾 ${isEdit ? 'Lưu Cập Nhật' : 'Tạo Tài Khoản'}
                    </button>
                    <button type="button" class="btn" onclick="Dashboard.closeModal();" style="padding: 12px; border: 1px solid var(--border-color);">
                        Hủy
                    </button>
                </div>
            </form>
        `;

        if (typeof Dashboard !== 'undefined' && Dashboard.openModal) {
            Dashboard.openModal();
        }
    },

    toggleCmStaffField() {
        const role = document.getElementById('user-form-role')?.value;
        const wrapper = document.getElementById('cm-staff-field-wrapper');
        if (wrapper) {
            wrapper.style.display = (role === 'cm') ? '' : 'none';
        }
    },

    async handleSaveUser(event, userId = null) {
        event.preventDefault();
        const isEdit = !!userId;

        const username = document.getElementById('user-form-username').value.trim();
        const fullName = document.getElementById('user-form-fullname').value.trim();
        const email = document.getElementById('user-form-email').value.trim();
        const password = document.getElementById('user-form-password').value.trim();
        const role = document.getElementById('user-form-role').value;
        const cmStaffName = document.getElementById('user-form-cmstaff').value.trim();
        const isActive = document.getElementById('user-form-active').checked;

        const errorDiv = document.getElementById('user-form-error');
        const saveBtn = document.getElementById('btn-save-user');

        errorDiv.style.display = 'none';
        saveBtn.disabled = true;
        saveBtn.innerText = '⏳ Đang lưu...';

        try {
            let res;
            if (isEdit) {
                const updateData = {
                    full_name: fullName,
                    email: email,
                    role: role,
                    cm_staff_name: cmStaffName,
                    is_active: isActive
                };
                if (password) updateData.password = password;
                res = await API.updateUser(userId, updateData);
            } else {
                res = await API.createUser({
                    username: username,
                    password: password,
                    full_name: fullName,
                    email: email,
                    role: role,
                    cm_staff_name: cmStaffName
                });
            }

            if (res.success) {
                App.showToast(isEdit ? 'Đã cập nhật tài khoản!' : 'Đã tạo tài khoản mới thành công!', 'success');
                if (typeof Dashboard !== 'undefined' && Dashboard.closeModal) {
                    Dashboard.closeModal();
                }
                await this.loadUsers();
            } else {
                errorDiv.innerText = res.error || 'Lưu tài khoản thất bại.';
                errorDiv.style.display = 'block';
            }
        } catch (e) {
            errorDiv.innerText = e.message || 'Lỗi kết nối máy chủ.';
            errorDiv.style.display = 'block';
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerText = isEdit ? '💾 Lưu Cập Nhật' : 'Tạo Tài Khoản';
        }
    },

    async confirmDeleteUser(userId, username) {
        if (!confirm(`Bạn có chắc chắn muốn xóa tài khoản '${username}'? Thao tác này không thể hoàn tác.`)) {
            return;
        }

        try {
            const res = await API.deleteUser(userId);
            if (res.success) {
                App.showToast(`Đã xóa tài khoản '${username}' thành công.`, 'info');
                await this.loadUsers();
            } else {
                App.showToast(res.error || 'Không thể xóa tài khoản', 'error');
            }
        } catch (e) {
            App.showToast(e.message || 'Lỗi khi xóa tài khoản', 'error');
        }
    }
};
