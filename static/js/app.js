/**
 * EVI Dashboard - SPA Router & Core Application
 * Hash-based routing, page management, sidebar navigation.
 */

const App = {
    currentPage: null,
    pages: {},
    isConnected: false,

    /**
     * Initialize the application.
     */
    async init() {
        console.log('🏫 Trung tâm Anh ngữ Vicare initializing...');

        // Initialize Auth module
        if (typeof AuthModule !== 'undefined') {
            AuthModule.init();
        }

        // Check health / connection status
        await this.checkConnection();

        // Setup routing
        this.setupRouter();

        // Setup sidebar interactions
        this.setupSidebar();

        // Navigate to initial page
        this.navigate(window.location.hash || '#dashboard');

        // Periodic Admin notification check (every 25 seconds)
        setInterval(() => {
            if (typeof AuthModule !== 'undefined' && AuthModule.isAdmin()) {
                AuthModule.loadNotifications();
            }
        }, 25000);

        console.log('✅ Trung tâm Anh ngữ Vicare system ready!');
    },

    /**
     * Check API connection status.
     */
    async checkConnection() {
        try {
            const health = await API.getHealth();
            this.isConnected = true;
            this.updateConnectionStatus(health);
        } catch (e) {
            console.warn('API not reachable:', e);
            this.isConnected = false;
            this.updateConnectionStatus({ status: 'error', mode: 'offline' });
        }
    },

    /**
     * Update connection indicator in sidebar.
     */
    updateConnectionStatus(health) {
        const dot = document.getElementById('status-dot');
        const text = document.getElementById('status-text');

        if (!dot || !text) return;

        if (health && (health.status === 'ok' || health.mode === 'live')) {
            dot.className = 'status-dot connected';
            text.textContent = 'CSDL: Đã kết nối (Go-Live 24/7)';
        } else {
            dot.className = 'status-dot error';
            text.textContent = 'Mất kết nối CSDL';
        }
    },

    /**
     * Setup hash-based routing.
     */
    setupRouter() {
        window.addEventListener('hashchange', () => {
            this.navigate(window.location.hash);
        });
    },

    /**
     * Navigate to a page.
     */
    navigate(hash) {
        const page = hash.replace('#', '') || 'dashboard';

        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });

        // Load page content
        this.loadPage(page);
    },

    /**
     * Load page content into main area.
     */
    async loadPage(page) {
        const content = document.getElementById('page-content');
        const pageTitle = document.getElementById('page-title');
        const pageSubtitle = document.getElementById('page-subtitle');

        if (!content) return;

        // Show loading
        content.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Đang tải dữ liệu...</div>
            </div>
        `;

        const titles = {
            'dashboard': { title: 'Dashboard', subtitle: 'Tổng quan hoạt động trung tâm' },
            'cm-attendance': { title: 'Điểm Danh Hàng Ngày', subtitle: 'Thực hiện điểm danh và ghi chú học tập theo ngày cho học sinh' },
            'cm-grades-sun': { title: 'Nhập Điểm Thi Sun & Galax', subtitle: 'Nhập điểm 3 kỹ năng Listening, Reading & Writing, Speaking' },
            'cm-grades-moon': { title: 'Nhập Điểm Thi Trình Độ Moon', subtitle: 'Tích đánh giá từ vựng, ngữ âm & nhận xét bài test Moon' },
            'cm-grades': { title: 'Nhập Điểm Thi Sun & Galax', subtitle: 'Nhập điểm 3 kỹ năng Listening, Reading & Writing, Speaking' },
            'cm-portal': { title: 'Cổng Quản Lý CM & Điểm Danh', subtitle: 'Kiểm tra thông tin lớp, Điểm danh hàng ngày & Nhập điểm thi' },
            'users': { title: 'Quản Lý Tài Khoản Người Dùng', subtitle: 'Phân quyền tài khoản Admin và Class Manager' },
            'homework': { title: 'Tra cứu Bài về nhà', subtitle: 'Theo dõi tình trạng nộp BTVN của học sinh' },
            'grades': { title: 'Tra cứu Điểm số', subtitle: 'Bảng điểm và đánh giá kỹ năng học sinh theo lớp' },
            'students': { title: 'Danh sách Học sinh', subtitle: 'Quản lý thông tin học sinh' },
            'renewals': { title: 'Quản Lý Tái Phí Học Sinh', subtitle: 'Theo dõi, thêm mới & cập nhật trạng thái nộp tái phí trung tâm' },
            'interactions': { title: 'Nhật Ký Tương Tác Phụ Huynh', subtitle: 'Quản lý & lưu trữ tập trung lịch sử chăm sóc phụ huynh toàn trung tâm' },
            'schedule': { title: 'Thời Khóa Biểu Lớp Học', subtitle: 'Thời khóa biểu chi tiết các ca học, phòng học, GV và CM' },
            'manage-classes': { title: 'Quản Lý Lớp Học & Thêm Lớp Mới', subtitle: 'Tạo lớp mới, cập nhật ca học, lịch học, ngày bắt đầu và quản lý trạng thái lớp (Admin Only)' },
            'audit-logs': { title: 'Nhật Ký Hoạt Động & Audit Trail', subtitle: 'Theo dõi 100% lịch sử thao tác, điểm danh, tái phí và thông báo của các người dùng khác (Admin Only)' },
        };

        const info = titles[page] || { title: 'Trang không tìm thấy', subtitle: '' };
        if (pageTitle) pageTitle.textContent = info.title;
        if (pageSubtitle) pageSubtitle.textContent = info.subtitle;

        this.currentPage = page;

        try {
            switch (page) {
                case 'dashboard':
                    await Dashboard.render(content);
                    break;
                case 'cm-attendance':
                    if (typeof CMPortalModule !== 'undefined') {
                        await CMPortalModule.init('attendance');
                    }
                    break;
                case 'cm-grades-sun':
                    if (typeof CMPortalModule !== 'undefined') {
                        await CMPortalModule.init('grades_sun');
                    }
                    break;
                case 'cm-grades-moon':
                    if (typeof CMPortalModule !== 'undefined') {
                        await CMPortalModule.init('grades_moon');
                    }
                    break;
                case 'cm-grades':
                    if (typeof CMPortalModule !== 'undefined') {
                        await CMPortalModule.init('grades_sun');
                    }
                    break;
                case 'cm-portal':
                    if (typeof CMPortalModule !== 'undefined') {
                        await CMPortalModule.init('classes');
                    }
                    break;
                case 'schedule':
                    if (typeof ScheduleModule !== 'undefined') {
                        await ScheduleModule.renderPage(content);
                    }
                    break;
                case 'users':
                    if (typeof UsersModule !== 'undefined') {
                        await UsersModule.init();
                    }
                    break;
                case 'manage-classes':
                    if (typeof Dashboard !== 'undefined' && Dashboard.renderManageClassesPage) {
                        await Dashboard.renderManageClassesPage(content);
                    }
                    break;
                case 'audit-logs':
                    if (typeof AuditLogsModule !== 'undefined') {
                        await AuditLogsModule.render(content);
                    }
                    break;
                case 'homework':
                    await SearchModule.renderHomework(content);
                    break;
                case 'grades':
                    await SearchModule.renderGrades(content);
                    break;
                case 'students':
                    if (typeof StudentsModule !== 'undefined') {
                        await StudentsModule.renderStudentsPage(content);
                    } else {
                        this.renderComingSoon(content, page, info.title);
                    }
                    break;
                case 'renewals':
                case 'renewal':
                    if (typeof RenewalsModule !== 'undefined') {
                        await RenewalsModule.render(content);
                    } else {
                        this.renderComingSoon(content, page, info.title);
                    }
                    break;
                case 'interactions':
                case 'interaction':
                    if (typeof InteractionsModule !== 'undefined') {
                        await InteractionsModule.render(content);
                    } else {
                        this.renderComingSoon(content, page, info.title);
                    }
                    break;
                case 'classes':
                case 'staff':
                case 'settings':
                    this.renderComingSoon(content, page, info.title);
                    break;
                default:
                    this.render404(content);
            }
        } catch (error) {
            console.error(`Error loading page ${page}:`, error);
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <h3>Lỗi tải trang</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    },

    /**
     * Render coming soon placeholder.
     */
    renderComingSoon(container, page, title) {
        const icons = {
            'renewal': '📝',
            'classes': '🏫',
            'staff': '👥',
            'students': '📖',
            'settings': '⚙️',
        };

        container.innerHTML = `
            <div class="coming-soon-page">
                <div class="coming-soon-icon">${icons[page] || '🚧'}</div>
                <h2 class="coming-soon-title">${title}</h2>
                <p class="coming-soon-desc">
                    Tính năng này đang được phát triển và sẽ sớm ra mắt.
                    Hiện tại bạn có thể xem tổng quan tại Dashboard.
                </p>
                <button class="btn btn-primary" onclick="window.location.hash='#dashboard'">
                    <span class="btn-icon">📊</span>
                    Về Dashboard
                </button>
            </div>
        `;
    },

    /**
     * Render 404 page.
     */
    render404(container) {
        container.innerHTML = `
            <div class="coming-soon-page">
                <div class="coming-soon-icon">🔍</div>
                <h2 class="coming-soon-title">Không tìm thấy trang</h2>
                <p class="coming-soon-desc">Trang bạn tìm kiếm không tồn tại.</p>
                <button class="btn btn-primary" onclick="window.location.hash='#dashboard'">
                    <span class="btn-icon">🏠</span>
                    Về Dashboard
                </button>
            </div>
        `;
    },

    /**
     * Setup sidebar interactions.
     */
    setupSidebar() {
        // Nav items click
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (item.classList.contains('disabled')) {
                    e.preventDefault();
                    return;
                }
                const page = item.dataset.page;
                if (page) {
                    window.location.hash = `#${page}`;
                    this.closeMobileSidebar();
                }
            });
        });

        // Mobile toggle
        const toggle = document.getElementById('mobile-menu-toggle');
        const overlay = document.getElementById('sidebar-overlay');

        if (toggle) {
            toggle.addEventListener('click', () => this.toggleMobileSidebar());
        }
        if (overlay) {
            overlay.addEventListener('click', () => this.closeMobileSidebar());
        }
    },

    /**
     * Handle Refresh Button click - Triggers Incremental Sheet -> DB Sync and reloads active page.
     */
    async handleRefreshButton() {
        const btn = document.getElementById('btn-refresh');
        const icon = document.getElementById('refresh-icon');
        const label = document.getElementById('refresh-label');

        if (btn) btn.disabled = true;
        if (icon) icon.style.display = 'inline-block';
        if (icon) icon.style.animation = 'spin 0.8s linear infinite';
        if (label) label.textContent = 'Đang quét & nạp DB...';

        try {
            const res = await API.refreshData();
            if (res.success) {
                console.log('✅ Incremental sync completed:', res.message);
                if (typeof Dashboard !== 'undefined') Dashboard.destroyCharts();

                // Reload current active page with fresh DB data
                if (this.currentPage === 'homework' || this.currentPage === 'grades') {
                    if (typeof SearchModule !== 'undefined') await SearchModule.loadData();
                } else {
                    await this.loadPage(this.currentPage || 'dashboard');
                }

                if (label) label.textContent = 'Đã cập nhật!';
                setTimeout(() => {
                    if (label) label.textContent = 'Làm mới';
                }, 2000);
            } else {
                alert('⚠️ Không thể đồng bộ: ' + (res.error || 'Lỗi kết nối'));
                if (label) label.textContent = 'Làm mới';
            }
        } catch (err) {
            console.error('Refresh error:', err);
            alert('⚠️ Lỗi khi đồng bộ dữ liệu: ' + err.message);
            if (label) label.textContent = 'Làm mới';
        } finally {
            if (btn) btn.disabled = false;
            if (icon) icon.style.animation = 'none';
        }
    },

    toggleMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        if (sidebar) sidebar.classList.toggle('open');
        if (overlay) overlay.classList.toggle('active');
    },

    closeMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
    },

    showToast(message, type = 'info') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; pointer-events: none;';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const colors = {
            success: 'background: rgba(16,185,129,0.95); color: #fff; border-left: 4px solid #059669;',
            error: 'background: rgba(239,68,68,0.95); color: #fff; border-left: 4px solid #dc2626;',
            warning: 'background: rgba(245,158,11,0.95); color: #fff; border-left: 4px solid #d97706;',
            info: 'background: rgba(99,102,241,0.95); color: #fff; border-left: 4px solid #4f46e5;'
        };

        toast.style.cssText = `padding: 12px 18px; border-radius: 8px; font-size: 13px; font-weight: 500; shadow: 0 10px 15px -3px rgba(0,0,0,0.3); backdrop-filter: blur(8px); transition: all 0.3s ease; opacity: 0; transform: translateY(10px); pointer-events: auto; max-width: 380px; ${colors[type] || colors.info}`;
        toast.innerHTML = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },
};

// ============================================================
// Utility Functions
// ============================================================

const Utils = {
    /**
     * Escape HTML special characters.
     */
    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    },

    /**
     * Format number with locale (Vietnamese).
     */
    formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return num.toLocaleString('vi-VN');
    },

    /**
     * Format percentage.
     */
    formatPercent(num) {
        if (num === null || num === undefined) return '0%';
        return num.toFixed(1).replace('.', ',') + '%';
    },

    /**
     * Get rate color class based on percentage.
     */
    getRateColor(rate) {
        if (rate >= 80) return '#34d399'; // green
        if (rate >= 50) return '#fbbf24'; // amber
        return '#f87171'; // red
    },

    /**
     * Get rate badge class.
     */
    getRateBadge(rate) {
        if (rate >= 80) return 'badge-success';
        if (rate >= 50) return 'badge-warning';
        return 'badge-danger';
    },

    /**
     * Get progress bar color class.
     */
    getProgressColor(rate) {
        if (rate >= 80) return 'green';
        if (rate >= 50) return 'amber';
        return 'red';
    },

    /**
     * Generate avatar color from name.
     */
    getAvatarColor(name) {
        if (!name || typeof name !== 'string') return '#6366f1';
        const colors = [
            '#6366f1', '#8b5cf6', '#06b6d4', '#10b981',
            '#f59e0b', '#ef4444', '#ec4899', '#14b8a6',
        ];
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return colors[Math.abs(hash) % colors.length];
    },

    /**
     * Get initials from name.
     */
    getInitials(name) {
        if (!name || typeof name !== 'string') return '?';
        const parts = name.trim().split(/[\s]+/);
        if (parts.length === 0 || !parts[0]) return '?';
        if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    },

    /**
     * Month name in Vietnamese.
     */
    monthName(month) {
        return `Tháng ${month}`;
    },

    /**
     * Animate number counting up.
     */
    animateNumber(element, target, duration = 1000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Utils.formatNumber(Math.round(current));
        }, 16);
    },
};

// ============================================================
// Initialize when DOM ready
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
