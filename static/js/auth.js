/**
 * EVI Dashboard - Authentication & Role Authorization Module
 */

const AuthModule = {
    currentUser: null,

    init() {
        this.loadUser();
        this.renderUserWidget();
        this.applyPermissions();
    },

    loadUser() {
        try {
            const saved = localStorage.getItem('evi_user');
            if (saved) {
                this.currentUser = JSON.parse(saved);
            }
        } catch (e) {
            console.error('Error loading saved user:', e);
            this.currentUser = null;
        }
    },

    saveUser(user) {
        this.currentUser = user;
        localStorage.setItem('evi_user', JSON.stringify(user));
        this.renderUserWidget();
        this.applyPermissions();
    },

    logout() {
        this.currentUser = null;
        localStorage.removeItem('evi_user');
        this.renderUserWidget();
        this.applyPermissions();
        if (typeof App !== 'undefined' && App.showToast) {
            App.showToast('Đã đăng xuất thành công!', 'info');
        }
        // Redirect to dashboard
        if (typeof App !== 'undefined' && App.navigateTo) {
            App.navigateTo('dashboard');
        }
    },

    getUser() {
        return this.currentUser;
    },

    getUserRole() {
        return (this.currentUser && this.currentUser.role) ? this.currentUser.role : '';
    },

    isLoggedIn() {
        return !!this.currentUser;
    },

    isAdmin() {
        return this.currentUser && this.currentUser.role === 'admin';
    },

    isCM() {
        return this.currentUser && (this.currentUser.role === 'cm' || this.currentUser.role === 'admin');
    },

    getCMStaffName() {
        if (!this.currentUser) return '';
        if (this.currentUser.role === 'admin') return ''; // Admin sees all
        return this.currentUser.cm_staff_name || '';
    },

    renderUserWidget() {
        const container = document.getElementById('user-widget-container');
        if (!container) return;

        if (this.currentUser) {
            const roleBadge = this.currentUser.role === 'admin' 
                ? '<span class="badge badge-admin">👑 Admin</span>'
                : `<span class="badge badge-cm">📋 CM ${this.currentUser.cm_staff_name || ''}</span>`;

            const notificationBell = this.isAdmin() ? `
                <div class="notification-bell-wrapper" style="position: relative;">
                    <button class="btn" onclick="AuthModule.toggleNotificationDropdown(event);" title="Thông báo hoạt động người dùng" style="height: 38px; width: 38px; padding: 0; display: inline-flex; align-items: center; justify-content: center; position: relative; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.05); color: #fff; border-radius: 8px;">
                        🔔
                        <span id="admin-unread-badge" style="display: none; position: absolute; top: -5px; right: -5px; background: #ef4444; color: #fff; font-size: 10px; font-weight: 800; padding: 2px 5px; border-radius: 10px; min-width: 16px; text-align: center; border: 1.5px solid #0f172a; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">0</span>
                    </button>
                    <!-- Notification Dropdown -->
                    <div id="admin-notification-dropdown" class="notification-dropdown" style="display: none; position: absolute; right: 0; top: 46px; width: 360px; max-height: 450px; background: #0f172a; border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index: 9999; overflow: hidden; backdrop-filter: blur(10px);">
                        <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03);">
                            <div style="font-weight: 700; font-size: 13.5px; color: #f8fafc; display: flex; align-items: center; gap: 6px;">
                                <span>🔔</span> Hoạt Động Người Dùng Khác
                            </div>
                            <button onclick="AuthModule.markNotificationsRead();" style="background: none; border: none; color: #38bdf8; font-size: 11.5px; font-weight: 600; cursor: pointer; padding: 0;">Đánh dấu đã đọc</button>
                        </div>
                        <div id="admin-notification-list" style="max-height: 350px; overflow-y: auto; padding: 0;">
                            <div style="padding: 20px; text-align: center; color: #94a3b8; font-size: 12.5px;">Đang tải thông báo...</div>
                        </div>
                        <div style="padding: 10px; text-align: center; border-top: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.02);">
                            <a href="#audit-logs" onclick="AuthModule.closeNotificationDropdown(); App.navigateTo('audit-logs');" style="color: #60a5fa; font-size: 12px; font-weight: 700; text-decoration: none;">📜 Xem tất cả nhật ký hoạt động (Audit Logs) →</a>
                        </div>
                    </div>
                </div>
            ` : '';

            container.innerHTML = `
                <div style="display: inline-flex; align-items: center; gap: 8px;">
                    ${notificationBell}
                    <div class="user-profile-badge" onclick="AuthModule.showUserMenuModal();" title="Bấm để xem thông tin tài khoản">
                        <div class="user-avatar">${this.currentUser.full_name.charAt(0).toUpperCase()}</div>
                        <div class="user-info-text">
                            <div class="user-name-title">${this.escapeHtml(this.currentUser.full_name)}</div>
                            <div class="user-role-subtitle">${roleBadge}</div>
                        </div>
                    </div>
                    <button class="btn" onclick="AuthModule.logout();" title="Đăng xuất" style="height: 38px; padding: 0 10px; font-size: 12px; border: 1px solid rgba(239,68,68,0.4); background: rgba(239,68,68,0.12); color: #f87171; border-radius: 8px;">
                        🚪 <span style="font-weight: 500;">Thoát</span>
                    </button>
                </div>
            `;

            if (this.isAdmin()) {
                this.loadNotifications();
            }
        } else {
            container.innerHTML = `
                <button class="btn btn-primary" onclick="AuthModule.showLoginModal();" style="height: 38px; padding: 0 16px; font-weight: 600;">
                    🔐 Đăng Nhập CM / Admin
                </button>
            `;
        }
    },

    async loadNotifications() {
        if (!this.isAdmin()) return;
        try {
            const res = await API.get('/admin/notifications', { limit: 15 });
            if (res.success) {
                const badge = document.getElementById('admin-unread-badge');
                if (badge) {
                    if (res.unread_count > 0) {
                        badge.innerText = res.unread_count > 99 ? '99+' : res.unread_count;
                        badge.style.display = 'inline-block';
                    } else {
                        badge.style.display = 'none';
                    }
                }
                this.notificationsCache = res.data || [];
            }
        } catch (e) {
            console.error('Error loading notifications:', e);
        }
    },

    toggleNotificationDropdown(e) {
        if (e) e.stopPropagation();
        const dropdown = document.getElementById('admin-notification-dropdown');
        if (!dropdown) return;

        if (dropdown.style.display === 'none' || !dropdown.style.display) {
            dropdown.style.display = 'block';
            this.renderNotificationsList();
            // Close dropdown when clicking outside
            const closeHandler = (evt) => {
                if (!dropdown.contains(evt.target)) {
                    dropdown.style.display = 'none';
                    document.removeEventListener('click', closeHandler);
                }
            };
            setTimeout(() => document.addEventListener('click', closeHandler), 10);
        } else {
            dropdown.style.display = 'none';
        }
    },

    closeNotificationDropdown() {
        const dropdown = document.getElementById('admin-notification-dropdown');
        if (dropdown) dropdown.style.display = 'none';
    },

    renderNotificationsList() {
        const container = document.getElementById('admin-notification-list');
        if (!container) return;

        const list = this.notificationsCache || [];
        if (list.length === 0) {
            container.innerHTML = `
                <div style="padding: 30px 16px; text-align: center; color: #94a3b8; font-size: 12.5px;">
                    🔕 Chưa có thông báo hoạt động nào từ người dùng khác.
                </div>
            `;
            return;
        }

        container.innerHTML = list.map(item => `
            <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); background: ${!item.is_read_by_admin ? 'rgba(59,130,246,0.08)' : 'transparent'}; display: flex; gap: 10px; align-items: start; transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.04)'" onmouseout="this.style.background='${!item.is_read_by_admin ? 'rgba(59,130,246,0.08)' : 'transparent'}'">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(59,130,246,0.2); color: #60a5fa; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; flex-shrink: 0;">
                    ${(item.user_fullname || 'U').charAt(0).toUpperCase()}
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 12.5px; color: #f8fafc;">${this.escapeHtml(item.user_fullname || item.username)}</span>
                        <span style="font-size: 10.5px; color: #94a3b8;">${item.time_ago || ''}</span>
                    </div>
                    <div style="font-size: 12px; color: #cbd5e1; margin-top: 3px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                        ${this.escapeHtml(item.description)}
                    </div>
                </div>
            </div>
        `).join('');
    },

    async markNotificationsRead() {
        try {
            await API.post('/admin/notifications/mark-read', {});
            const badge = document.getElementById('admin-unread-badge');
            if (badge) badge.style.display = 'none';
            if (this.notificationsCache) {
                this.notificationsCache.forEach(n => n.is_read_by_admin = 1);
                this.renderNotificationsList();
            }
            if (typeof App !== 'undefined' && App.showToast) {
                App.showToast('Đã đánh dấu đã đọc!', 'success');
            }
        } catch (e) {
            console.error('Error marking read:', e);
        }
    },

    applyPermissions() {
        // Toggle Nav Items based on role
        const attNav = document.getElementById('nav-cm-attendance');
        const gradesNav = document.getElementById('nav-cm-grades');
        const usersNav = document.getElementById('nav-users');
        const classesNav = document.getElementById('nav-manage-classes');
        const auditNav = document.getElementById('nav-audit-logs');
        const adminSection = document.getElementById('section-admin');

        if (attNav) attNav.style.display = 'flex';
        if (gradesNav) gradesNav.style.display = 'flex';

        if (this.isAdmin()) {
            if (usersNav) usersNav.style.display = 'flex';
            if (classesNav) classesNav.style.display = 'flex';
            if (auditNav) auditNav.style.display = 'flex';
            if (adminSection) adminSection.style.display = 'block';
        } else {
            if (usersNav) usersNav.style.display = 'none';
            if (classesNav) classesNav.style.display = 'none';
            if (auditNav) auditNav.style.display = 'none';
            if (adminSection) adminSection.style.display = 'none';
        }
    },

    showLoginModal() {
        const modalBody = document.getElementById('modal-body');
        const modalTitle = document.getElementById('modal-title');
        if (!modalBody || !modalTitle) return;

        modalTitle.innerHTML = '🔐 Đăng Nhập Hệ Thống EVI';
        modalBody.innerHTML = `
            <div class="login-form-container" style="max-width: 400px; margin: 0 auto; padding: 10px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 64px; height: 64px; object-fit: contain; margin-bottom: 8px; filter: drop-shadow(0 2px 8px rgba(0,0,0,0.15)); border-radius: 8px;">
                    <h3 style="margin: 0; font-size: 20px; color: var(--text-heading); font-weight: 900;">Trung tâm Anh ngữ Vicare</h3>
                    <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Đăng nhập hệ thống quản lý & chăm sóc học viên</p>
                </div>

                <div id="login-error-msg" class="alert alert-danger" style="display: none; margin-bottom: 15px; font-size: 13px; padding: 10px 14px; border-radius: 8px; background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #f87171;"></div>

                <form id="login-form" onsubmit="AuthModule.handleLoginSubmit(event);">
                    <div class="form-group" style="margin-bottom: 16px;">
                        <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-main);">Tên đăng nhập</label>
                        <input type="text" id="login-username" class="form-control" placeholder="Tên đăng nhập (ví dụ: admin, cm_thucanh)" required style="width: 100%; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main); font-size: 14px;">
                    </div>

                    <div class="form-group" style="margin-bottom: 20px;">
                        <label style="display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-main);">Mật khẩu</label>
                        <input type="password" id="login-password" class="form-control" placeholder="Mật khẩu" required style="width: 100%; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-main); font-size: 14px;">
                    </div>

                    <button type="submit" id="btn-login-submit" class="btn btn-primary" style="width: 100%; padding: 12px; font-size: 15px; font-weight: 600; border-radius: 8px; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);">
                        🚀 Đăng Nhập
                    </button>
                </form>
            </div>
        `;

        if (typeof Dashboard !== 'undefined' && Dashboard.openModal) {
            Dashboard.openModal();
        } else {
            const backdrop = document.getElementById('modal-backdrop');
            if (backdrop) backdrop.classList.add('active');
        }
    },

    async handleLoginSubmit(event) {
        event.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value.trim();
        const errorMsg = document.getElementById('login-error-msg');
        const submitBtn = document.getElementById('btn-login-submit');

        if (!username || !password) return;

        errorMsg.style.display = 'none';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '⏳ Đang đăng nhập...';

        try {
            const res = await API.login(username, password);
            if (res.success && res.user) {
                this.saveUser(res.user);
                if (typeof Dashboard !== 'undefined' && Dashboard.closeModal) {
                    Dashboard.closeModal();
                } else {
                    const backdrop = document.getElementById('modal-backdrop');
                    if (backdrop) backdrop.classList.remove('active');
                }

                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast(`Xin chào ${res.user.full_name}! Đã đăng nhập thành công.`, 'success');
                }

                // If user logged in as CM or Admin, optionally navigate to CM portal
                if (typeof App !== 'undefined' && App.navigateTo) {
                    App.navigateTo('cm-portal');
                }
            } else {
                errorMsg.innerText = res.error || 'Đăng nhập thất bại. Vui lòng kiểm tra lại!';
                errorMsg.style.display = 'block';
            }
        } catch (err) {
            errorMsg.innerText = err.message || 'Lỗi kết nối máy chủ.';
            errorMsg.style.display = 'block';
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '🚀 Đăng Nhập';
        }
    },

    fillLoginForm(username, password) {
        const uInput = document.getElementById('login-username');
        const pInput = document.getElementById('login-password');
        if (uInput) uInput.value = username;
        if (pInput) pInput.value = password;
        const submitBtn = document.getElementById('btn-login-submit');
        if (submitBtn) submitBtn.focus();
    },

    showUserMenuModal() {
        if (!this.currentUser) return;
        const modalBody = document.getElementById('modal-body');
        const modalTitle = document.getElementById('modal-title');
        if (!modalBody || !modalTitle) return;

        modalTitle.innerHTML = '👤 Thông Tin Tài Khoản';
        modalBody.innerHTML = `
            <div style="padding: 10px; max-width: 450px; margin: 0 auto;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div class="user-avatar" style="width: 64px; height: 64px; font-size: 28px; margin: 0 auto 12px;">${this.currentUser.full_name.charAt(0).toUpperCase()}</div>
                    <h3 style="margin: 0; font-size: 20px;">${this.escapeHtml(this.currentUser.full_name)}</h3>
                    <div style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">@${this.escapeHtml(this.currentUser.username)}</div>
                </div>

                <div class="info-card" style="background: var(--bg-card); border-radius: 12px; padding: 16px; border: 1px solid var(--border-color); margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: var(--text-muted);">Vai trò:</span>
                        <strong style="text-transform: uppercase; color: var(--accent-color);">${this.currentUser.role}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: var(--text-muted);">Phụ trách CM:</span>
                        <strong>${this.escapeHtml(this.currentUser.cm_staff_name || 'Tất cả các lớp (Admin)')}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: var(--text-muted);">Email:</span>
                        <span>${this.escapeHtml(this.currentUser.email || 'Chưa cập nhật')}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">Ngày tạo:</span>
                        <span>${this.currentUser.created_at || 'Mặc định'}</span>
                    </div>
                </div>

                <div style="display: flex; gap: 10px;">
                    <button class="btn btn-outline-danger" style="flex: 1; padding: 10px;" onclick="Dashboard.closeModal(); AuthModule.logout();">
                        🚪 Đăng xuất
                    </button>
                    <button class="btn" style="flex: 1; padding: 10px; border: 1px solid var(--border-color);" onclick="Dashboard.closeModal();">
                        Đóng
                    </button>
                </div>
            </div>
        `;

        if (typeof Dashboard !== 'undefined' && Dashboard.openModal) {
            Dashboard.openModal();
        }
    },

    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
};
