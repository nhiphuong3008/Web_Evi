/**
 * EVI Dashboard - CRM Renewals Management Module (Quản Lý Tái Phí & Chồng Phí CRM)
 * Hỗ trợ 3 Tab: Kanban Board Pipeline 5 giai đoạn, Bảng danh sách chi tiết & Xuất PDF, Dashboard Analytics KPI.
 */

const RenewalsModule = {
    currentTab: 'kanban', // 'kanban', 'table', 'kpi'
    currentMonth: 8,
    currentYear: 2026,
    currentCm: '',
    pipelineData: null,
    renewalsData: [],

    async render(container) {
        if (!container) container = document.getElementById('page-content');
        if (!container) return;

        const currentM = new Date().getMonth() + 1;
        const currentY = new Date().getFullYear();
        if (!this.currentMonth) this.currentMonth = currentM > 7 ? currentM : 8;
        if (!this.currentYear) this.currentYear = currentY;

        container.innerHTML = `
            <div style="padding: 10px; max-width: 1400px; margin: 0 auto;">
                
                <!-- TOP HEADER & CONTROLS -->
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 18px 20px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                    <div>
                        <h2 style="margin: 0 0 4px; font-size: 18px; font-weight: 900; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                            💳 CRM QUẢN LÝ TÁI PHÍ & CHỒNG PHÍ
                        </h2>
                        <div style="font-size: 13px; color: #64748b; font-weight: 500;">
                            Pipeline 5 giai đoạn, tự động gỡ ca Chồng Phí khỏi danh sách đến hạn tháng cũ & KPI Real-time
                        </div>
                    </div>

                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        ${(typeof AuthModule !== 'undefined' && AuthModule.isAdmin()) ? `
                            <button class="btn" onclick="RenewalsModule.recalculateExpiry();" style="padding: 9px 16px; font-size: 13px; font-weight: 800; border-radius: 8px; background: #f8fafc; color: #0f172a; border: 1.5px solid #cbd5e1; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                                🔄 Tính Lại Hạn Hết Phí
                            </button>
                        ` : ''}
                        <button class="btn" onclick="RenewalsModule.exportPDFReport();" style="padding: 9px 16px; font-size: 13px; font-weight: 800; border-radius: 8px; background: #059669; color: #ffffff; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(5,150,105,0.35); display: flex; align-items: center; gap: 6px;">
                            📄 Xuất Báo Cáo PDF
                        </button>
                        ${(typeof AuthModule !== 'undefined' && AuthModule.isAdmin()) ? `
                            <button class="btn btn-primary" onclick="RenewalsModule.openPaymentModal();" style="padding: 9px 18px; font-size: 13.5px; font-weight: 800; border-radius: 8px; background: linear-gradient(135deg, #4f46e5, #3730a3); color: #ffffff; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(79,70,229,0.35); display: flex; align-items: center; gap: 6px;">
                                💰 Nhập Đóng Phí / Chồng Phí Mới
                            </button>
                        ` : ''}
                    </div>
                </div>

                <!-- TABS & FILTERS BAR -->
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                    <!-- Sub Tabs Buttons -->
                    <div style="display: flex; gap: 8px; border-bottom: 2px solid transparent;">
                        <button id="rn-tab-kanban" class="btn" onclick="RenewalsModule.switchTab('kanban');" style="padding: 8px 16px; font-weight: 800; font-size: 13px; border-radius: 8px; background: ${this.currentTab === 'kanban' ? '#4f46e5' : '#e2e8f0'}; color: ${this.currentTab === 'kanban' ? '#ffffff' : '#475569'}; border: none; cursor: pointer;">
                            📊 Pipeline Kanban (5 Giai đoạn)
                        </button>
                        <button id="rn-tab-table" class="btn" onclick="RenewalsModule.switchTab('table');" style="padding: 8px 16px; font-weight: 800; font-size: 13px; border-radius: 8px; background: ${this.currentTab === 'table' ? '#4f46e5' : '#e2e8f0'}; color: ${this.currentTab === 'table' ? '#ffffff' : '#475569'}; border: none; cursor: pointer;">
                            📋 Bảng Danh Sách Chi Tiết
                        </button>
                        <button id="rn-tab-kpi" class="btn" onclick="RenewalsModule.switchTab('kpi');" style="padding: 8px 16px; font-weight: 800; font-size: 13px; border-radius: 8px; background: ${this.currentTab === 'kpi' ? '#4f46e5' : '#e2e8f0'}; color: ${this.currentTab === 'kpi' ? '#ffffff' : '#475569'}; border: none; cursor: pointer;">
                            📈 KPI & CM Leaderboard
                        </button>
                    </div>

                    <!-- Dropdown Filters -->
                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <label style="font-size: 13px; font-weight: 700; color: #475569;">📅 Tháng:</label>
                            <select id="rn_filter_month" onchange="RenewalsModule.handleFilterChange();" style="padding: 6px 10px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700;">
                                ${Array.from({length: 12}, (_, i) => i + 1).map(m => `<option value="${m}" ${this.currentMonth === m ? 'selected' : ''}>Tháng ${m}</option>`).join('')}
                            </select>
                        </div>

                        <div style="display: flex; align-items: center; gap: 6px;">
                            <label style="font-size: 13px; font-weight: 700; color: #475569;">Năm:</label>
                            <select id="rn_filter_year" onchange="RenewalsModule.handleFilterChange();" style="padding: 6px 10px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700;">
                                <option value="2025" ${this.currentYear === 2025 ? 'selected' : ''}>2025</option>
                                <option value="2026" ${this.currentYear === 2026 ? 'selected' : ''}>2026</option>
                                <option value="2027" ${this.currentYear === 2027 ? 'selected' : ''}>2027</option>
                            </select>
                        </div>

                        <div style="display: flex; align-items: center; gap: 6px;">
                            <label style="font-size: 13px; font-weight: 700; color: #475569;">👤 CM:</label>
                            <select id="rn_filter_cm" onchange="RenewalsModule.handleFilterChange();" style="padding: 6px 10px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700;">
                                <option value="">-- Tất cả CM --</option>
                                ${['NgọcCM', 'AnhPTT', 'AnhNV'].map(c => `<option value="${c}" ${this.currentCm === c ? 'selected' : ''}>${c}</option>`).join('')}
                            </select>
                        </div>

                        <button class="btn" onclick="RenewalsModule.loadData();" style="padding: 6px 12px; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 8px; font-weight: 700;">
                            🔄 Tải lại
                        </button>
                    </div>
                </div>

                <!-- KPI STATS CARDS -->
                <div id="rn-kpi-cards-container" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin-bottom: 20px;">
                    <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 10px; padding: 12px; text-align: center;">
                        <div style="font-size: 11.5px; font-weight: 800; color: #64748b; text-transform: uppercase;">📋 ĐẾN HẠN THÁNG</div>
                        <div id="rn_stat_due" style="font-size: 22px; font-weight: 900; color: #0f172a; margin-top: 4px;">0</div>
                    </div>

                    <div style="background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 10px; padding: 12px; text-align: center;">
                        <div style="font-size: 11.5px; font-weight: 800; color: #15803d; text-transform: uppercase;">🟢 TÁI PHÍ ĐÚNG HẠN</div>
                        <div id="rn_stat_success" style="font-size: 22px; font-weight: 900; color: #16a34a; margin-top: 4px;">0</div>
                    </div>

                    <div style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 10px; padding: 12px; text-align: center;">
                        <div style="font-size: 11.5px; font-weight: 800; color: #1d4ed8; text-transform: uppercase;">🔵 CHỒNG PHÍ SỚM</div>
                        <div id="rn_stat_stacked" style="font-size: 22px; font-weight: 900; color: #2563eb; margin-top: 4px;">0</div>
                    </div>

                    <div style="background: #fff1f2; border: 1.5px solid #fecdd3; border-radius: 10px; padding: 12px; text-align: center;">
                        <div style="font-size: 11.5px; font-weight: 800; color: #be123c; text-transform: uppercase;">🔴 FAIL TÁI PHÍ</div>
                        <div id="rn_stat_failed" style="font-size: 22px; font-weight: 900; color: #dc2626; margin-top: 4px;">0</div>
                    </div>

                    <div style="background: #f5f3ff; border: 1.5px solid #ddd6fe; border-radius: 10px; padding: 12px; text-align: center;">
                        <div style="font-size: 11.5px; font-weight: 800; color: #6d28d9; text-transform: uppercase;">📈 TỈ LỆ TÁI PHÍ REALTIME</div>
                        <div id="rn_stat_rate" style="font-size: 22px; font-weight: 900; color: #7c3aed; margin-top: 4px;">0.0%</div>
                    </div>
                </div>

                <!-- DYNAMIC TAB CONTENT CONTAINER -->
                <div id="rn-tab-content-area">
                    <div style="padding: 30px; text-align: center; color: #64748b;">Đang tải dữ liệu CRM...</div>
                </div>

            </div>

            <!-- PAYMENT TRANSACTION MODAL -->
            <div id="rn-payment-modal" class="modal" style="display: none;">
                <div class="modal-content" style="max-width: 500px; border-radius: 12px;">
                    <div class="modal-header" style="background: #4f46e5; color: #ffffff; border-radius: 12px 12px 0 0; padding: 14px 18px;">
                        <h3 style="margin: 0; font-size: 15.5px; font-weight: 800;">
                            💰 Ghi Nhận Thu Tiền Tái Phí / Chồng Phí
                        </h3>
                        <span class="modal-close" onclick="RenewalsModule.closePaymentModal();" style="color: #ffffff; font-size: 22px; cursor: pointer;">&times;</span>
                    </div>
                    <div class="modal-body" style="padding: 20px;">
                        <div style="margin-bottom: 14px;">
                            <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 4px;">Mã / Họ Tên Học Sinh <span style="color: #ef4444;">*</span></label>
                            <input type="text" id="rn-pm-student-code" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" placeholder="Ví dụ: EVI048 hoặc Phạm Hoàng Anh..." />
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                            <div>
                                <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 4px;">Loại Giao Dịch</label>
                                <select id="rn-pm-is-early" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;">
                                    <option value="0">🟢 Tái phí đúng hạn</option>
                                    <option value="1">🔵 Chồng phí sớm (Early)</option>
                                </select>
                            </div>
                            <div>
                                <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 4px;">Số Buổi Mua Thêm</label>
                                <input type="number" id="rn-pm-sessions" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" value="72" />
                            </div>
                        </div>

                        <div style="margin-bottom: 14px;">
                            <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 4px;">Số Tiền Thực Thu (VNĐ)</label>
                            <input type="number" id="rn-pm-amount" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" placeholder="7200000" value="7200000" />
                        </div>

                        <div style="margin-bottom: 20px;">
                            <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 4px;">Ghi Chú Giao Dịch</label>
                            <input type="text" id="rn-pm-notes" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" placeholder="Nhập thêm ghi chú thu tiền..." />
                        </div>

                        <div style="display: flex; justify-content: flex-end; gap: 10px;">
                            <button class="btn" onclick="RenewalsModule.closePaymentModal();" style="padding: 8px 16px; border: 1px solid #cbd5e1; border-radius: 8px; font-weight: 700;">Hủy</button>
                            <button class="btn btn-primary" onclick="RenewalsModule.submitPaymentTransaction();" style="padding: 8px 20px; background: #4f46e5; color: #fff; border: none; border-radius: 8px; font-weight: 800;">🚀 Xác Nhận Thu Tiền</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MODAL TIMELINE READ-ONLY -->
            <div id="rn-timeline-modal" class="modal" style="display: none;">
                <div class="modal-content" style="max-width: 600px; border-radius: 12px;">
                    <div class="modal-header" style="background: #0284c7; color: #ffffff; border-radius: 12px 12px 0 0; padding: 14px 18px;">
                        <h3 id="rn-timeline-title" style="margin: 0; font-size: 15.5px; font-weight: 800;">
                            📖 Nhật Ký Chăm Sóc & Tương Tác Phụ Huynh
                        </h3>
                        <span class="modal-close" onclick="RenewalsModule.closeTimelineModal();" style="color: #ffffff; font-size: 22px; cursor: pointer;">&times;</span>
                    </div>
                    <div class="modal-body" style="padding: 20px; max-height: 480px; overflow-y: auto;" id="rn-timeline-body">
                        <div style="text-align: center; color: #64748b; padding: 20px;">Đang tải nhật ký...</div>
                    </div>
                </div>
            </div>

            <!-- FLOATING DRAGGABLE MODAL CHUYỂN GIAI ĐOẠN TÁI PHÍ -->
            <div id="rn-stage-modal" style="display: none; position: fixed; top: 120px; right: 40px; z-index: 10000; width: 420px; border-radius: 16px; overflow: hidden; background: #ffffff; box-shadow: 0 20px 40px rgba(0,0,0,0.25), 0 0 0 1px rgba(0,0,0,0.08); font-family: inherit;">
                <div id="rn-stage-modal-header" style="background: linear-gradient(135deg, #1e293b, #0f172a); color: #ffffff; padding: 12px 16px; cursor: move; user-select: none; display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 800; font-size: 13.5px; display: flex; align-items: center; gap: 6px;">
                        <span style="font-size: 15px;">🔄</span> CHUYỂN GIAI ĐOẠN TÁI PHÍ
                        <span style="font-size: 10.5px; background: rgba(255,255,255,0.15); padding: 2px 6px; border-radius: 4px; font-weight: 600; color: #cbd5e1;">Kéo rê di chuyển</span>
                    </div>
                    <button onclick="RenewalsModule.closeStageModal();" style="background: none; border: none; color: #94a3b8; font-size: 20px; font-weight: 700; cursor: pointer; line-height: 1; padding: 0 4px;" onmouseover="this.style.color='#ffffff'" onmouseout="this.style.color='#94a3b8'">&times;</button>
                </div>

                <div style="padding: 16px; background: #ffffff;">
                    <input type="hidden" id="rn-stage-sub-id" value="" />
                    <input type="hidden" id="rn-stage-student-code" value="" />
                    
                    <!-- Student Detailed Info Card -->
                    <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; margin-bottom: 12px;">
                        <div style="font-size: 13.5px; font-weight: 800; color: #0f172a;" id="rn-stage-student-info">Học sinh: —</div>
                        <div style="font-size: 11.5px; color: #475569; margin-top: 6px; display: flex; flex-wrap: wrap; gap: 10px;" id="rn-stage-extra-info">
                            <!-- Class, CM, Expiry filled dynamically -->
                        </div>
                    </div>

                    <!-- Dropdown choice -->
                    <div style="margin-bottom: 10px;">
                        <label style="display: block; font-weight: 800; font-size: 12px; color: #334155; margin-bottom: 4px;">
                            🎯 Chọn Giai Đoạn CRM Muốn Chuyển Sang (*):
                        </label>
                        <select id="rn-stage-select" onchange="RenewalsModule.updateStagePreviewBanner();" style="width: 100%; padding: 8px 10px; font-size: 12.5px; font-weight: 700; border-radius: 8px; border: 1.5px solid #cbd5e1; background: #ffffff; color: #0f172a; cursor: pointer; outline: none;">
                            <option value="D-30">1. Sắp Đến Hạn (D-30)</option>
                            <option value="Contacted">2. Đã Liên Hệ & Tư Vấn (Contacted)</option>
                            <option value="Committed">3. Cam Kết Đóng Phí (Committed)</option>
                            <option value="At-Risk">4. Do Dự / Nguy Cơ Nghỉ (At-Risk)</option>
                            <option value="Success">5. Thành Công (Tái Phí / Chồng Phí)</option>
                            <option value="Failed">6. Thất Bại (Failed / Churned)</option>
                        </select>
                    </div>

                    <!-- Dynamic Stage Transition Banner Preview -->
                    <div id="rn-stage-preview-banner" style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 7px 10px; font-size: 11.5px; font-weight: 700; color: #1d4ed8; margin-bottom: 12px; text-align: center;">
                        🔄 Chuyển sang bước: Đã Liên Hệ
                    </div>

                    <!-- Optional Note Input -->
                    <div style="margin-bottom: 14px;">
                        <label style="display: block; font-weight: 800; font-size: 12px; color: #334155; margin-bottom: 4px;">
                            📝 Ghi Chú Chăm Sóc Nhanh <span style="font-weight: 500; color: #94a3b8;">(Tùy chọn)</span>:
                        </label>
                        <input type="text" id="rn-stage-note" placeholder="Nhập nhanh ghi chú cuộc gọi / lý do chuyển bước..." style="width: 100%; padding: 8px 10px; font-size: 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; box-sizing: border-box; outline: none; font-family: inherit;">
                    </div>

                    <!-- Action Buttons -->
                    <div style="display: flex; justify-content: flex-end; gap: 8px;">
                        <button type="button" onclick="RenewalsModule.closeStageModal();" style="padding: 7px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 12px; font-weight: 700; background: #f8fafc; color: #475569; cursor: pointer;">
                            Hủy
                        </button>
                        <button type="button" onclick="RenewalsModule.submitStageChange();" style="padding: 7px 16px; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #ffffff; border: none; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer; box-shadow: 0 4px 12px rgba(37,99,235,0.25);">
                            🚀 Xác Nhận Chuyển Bước
                        </button>
                    </div>
                </div>
            </div>
        `;

        await this.loadData();
    },

    switchTab(tabName) {
        this.currentTab = tabName;
        ['kanban', 'table', 'kpi'].forEach(t => {
            const btn = document.getElementById(`rn-tab-${t}`);
            if (btn) {
                btn.style.background = (t === tabName) ? '#4f46e5' : '#e2e8f0';
                btn.style.color = (t === tabName) ? '#ffffff' : '#475569';
            }
        });

        this.renderTabContent();
    },

    handleFilterChange() {
        this.currentMonth = parseInt(document.getElementById('rn_filter_month')?.value || 8);
        this.currentYear = parseInt(document.getElementById('rn_filter_year')?.value || 2026);
        this.currentCm = document.getElementById('rn_filter_cm')?.value || '';
        this.loadData();
    },

    async loadData() {
        const area = document.getElementById('rn-tab-content-area');
        if (!area) return;

        try {
            const res = await API.request(`/crm/renewals/pipeline?month=${this.currentMonth}&year=${this.currentYear}&cm_staff=${encodeURIComponent(this.currentCm)}`);

            if (res && res.success) {
                this.pipelineData = res;
                const kpi = res.kpi || {};

                // Update Stats KPI Cards
                if (document.getElementById('rn_stat_due')) document.getElementById('rn_stat_due').innerText = kpi.total_due || 0;
                if (document.getElementById('rn_stat_success')) document.getElementById('rn_stat_success').innerText = kpi.standard_renewed || 0;
                if (document.getElementById('rn_stat_stacked')) document.getElementById('rn_stat_stacked').innerText = kpi.early_renewed || 0;
                if (document.getElementById('rn_stat_failed')) document.getElementById('rn_stat_failed').innerText = kpi.failed_count || 0;
                if (document.getElementById('rn_stat_rate')) document.getElementById('rn_stat_rate').innerText = `${kpi.renew_rate || 0}%`;

                this.renderTabContent();
            } else {
                area.innerHTML = `<div style="padding: 20px; color: #ef4444; text-align: center;">Lỗi tải CRM pipeline: ${res ? res.error : 'Không có phản hồi'}</div>`;
            }
        } catch (e) {
            console.error('Error loading CRM renewals:', e);
            area.innerHTML = `<div style="padding: 20px; color: #ef4444; text-align: center;">Lỗi kết nối máy chủ: ${e.message}</div>`;
        }
    },

    renderTabContent() {
        const area = document.getElementById('rn-tab-content-area');
        if (!area) return;

        if (this.currentTab === 'kanban') {
            this.renderKanbanBoard(area);
        } else if (this.currentTab === 'table') {
            this.renderListViewTable(area);
        } else if (this.currentTab === 'kpi') {
            this.renderKpiLeaderboard(area);
        }
    },

    renderKanbanBoard(container) {
        if (!this.pipelineData || !this.pipelineData.kanban) {
            container.innerHTML = `<div style="padding: 30px; text-align: center; color: #64748b;">Chưa có dữ liệu Kanban Pipeline</div>`;
            return;
        }

        const kb = this.pipelineData.kanban;

        const stagesConfig = [
            { id: 'd30', title: '🕒 1. Sắp Đến Hạn (D-30)', bg: '#f8fafc', border: '#cbd5e1', text: '#334155', list: kb.d30 || [] },
            { id: 'contacted', title: '📞 2. Đã Liên Hệ & Tư Vấn', bg: '#eff6ff', border: '#bfdbfe', text: '#1d4ed8', list: kb.contacted || [] },
            { id: 'committed', title: '🤝 3. Cam Kết Đóng Phí', bg: '#fefce8', border: '#fef08a', text: '#a16207', list: kb.committed || [] },
            { id: 'at_risk', title: '⚠️ 4. Do Dự / Nguy Cơ Nghỉ', bg: '#fff1f2', border: '#fecdd3', text: '#be123c', list: kb.at_risk || [] },
            { id: 'completed', title: '🏆 5. Kết Quả Hoàn Thành', bg: '#f0fdf4', border: '#bbf7d0', text: '#15803d', list: kb.completed || [] }
        ];

        let colsHtml = stagesConfig.map(col => {
            let cardsHtml = col.list.map(st => {
                let badgeClass = 'badge-warning';
                let isSuccess = st.renewal_status === 'Early_Renewed' || st.renewal_status === 'Renewed' || st.pipeline_stage === 'Success';
                let isFailed = st.renewal_status === 'Failed' || st.pipeline_stage === 'Failed';

                if (isSuccess) badgeClass = 'badge-success';
                if (isFailed) badgeClass = 'badge-danger';

                return `
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); position: relative;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                            <div style="font-weight: 800; font-size: 13.5px; color: #0f172a;">
                                ${AuthModule.escapeHtml(st.student_name)}
                                ${st.english_name ? `<span style="font-size: 11px; color: #64748b; font-weight: 600;">(${AuthModule.escapeHtml(st.english_name)})</span>` : ''}
                            </div>
                            <span class="badge ${badgeClass}" style="font-size: 10.5px;">${st.renewal_status || st.pipeline_stage}</span>
                        </div>

                        <div style="font-size: 11.5px; color: #475569; margin-bottom: 4px;">
                            <span>Mã: <strong style="color: #2563eb;">${st.student_code}</strong></span> | 
                            <span>Lớp: <strong>${st.class_name || 'N/A'}</strong></span>
                        </div>

                        <div style="font-size: 11.5px; color: #64748b; margin-bottom: 8px;">
                            📅 Hạn hết phí: <strong style="color: #059669;">${st.current_end_date || st.original_end_date}</strong><br/>
                            👤 CM: <strong>${st.cm_staff || 'Chưa phân công'}</strong>
                        </div>

                        <!-- Action Buttons -->
                        <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap; border-top: 1px solid #f1f5f9; padding-top: 8px; margin-top: 6px;">
                            <button onclick="RenewalsModule.openInteractionTimeline('${st.student_code}', '${AuthModule.escapeHtml(st.student_name)}');" style="padding: 3px 8px; font-size: 10.5px; font-weight: 700; background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; border-radius: 5px; cursor: pointer;">
                                💬 Nhật Ký
                            </button>
                            <button onclick="RenewalsModule.quickMoveStage(${st.id}, '${col.id}', '${AuthModule.escapeHtml(st.student_name).replace(/'/g, "\\'")}', '${st.student_code}');" style="padding: 3px 8px; font-size: 10.5px; font-weight: 700; background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; border-radius: 5px; cursor: pointer;">
                                ➡️ Chuyển Bước
                            </button>
                            ${(typeof AuthModule !== 'undefined' && AuthModule.isAdmin() && !isSuccess) ? `
                                <button onclick="RenewalsModule.openPaymentModal('${st.student_code}');" style="padding: 3px 8px; font-size: 10.5px; font-weight: 800; background: #dcfce7; color: #15803d; border: 1px solid #86efac; border-radius: 5px; cursor: pointer;">
                                    💰 Thu Tiền
                                </button>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');

            return `
                <div style="background: ${col.bg}; border: 1.5px solid ${col.border}; border-radius: 12px; padding: 12px; min-width: 260px; flex: 1; display: flex; flex-direction: column;">
                    <div style="font-weight: 900; font-size: 13px; color: ${col.text}; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <span>${col.title}</span>
                        <span style="background: #ffffff; padding: 2px 8px; border-radius: 12px; font-size: 12px; border: 1px solid ${col.border}; font-weight: 800;">${col.list.length}</span>
                    </div>
                    <div style="flex: 1; min-height: 350px; max-height: 600px; overflow-y: auto;">
                        ${cardsHtml || `<div style="text-align: center; padding: 30px; color: #94a3b8; font-size: 12px;">Không có học sinh trong giai đoạn này</div>`}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div style="display: flex; gap: 14px; overflow-x: auto; padding-bottom: 14px;">
                ${colsHtml}
            </div>
        `;
    },

    renderListViewTable(container) {
        const allList = [];
        if (this.pipelineData && this.pipelineData.kanban) {
            Object.values(this.pipelineData.kanban).forEach(arr => allList.push(...arr));
        }

        if (allList.length === 0) {
            container.innerHTML = `
                <div style="background: #ffffff; border-radius: 12px; padding: 40px; text-align: center; color: #64748b; border: 1px solid #e2e8f0;">
                    <div style="font-size: 36px; margin-bottom: 8px;">📋</div>
                    <div style="font-weight: 800; font-size: 15px;">Chưa có dữ liệu danh sách tái phí cho Tháng ${this.currentMonth}/${this.currentYear}</div>
                </div>
            `;
            return;
        }

        let rowsHtml = allList.map((st, i) => `
            <tr style="border-bottom: 1px solid #e2e8f0; background: ${i % 2 === 0 ? '#ffffff' : '#f8fafc'};">
                <td style="padding: 10px; font-weight: 800; color: #64748b;">#${st.id}</td>
                <td style="padding: 10px; font-weight: 800; color: #0f172a;">${AuthModule.escapeHtml(st.student_name)}</td>
                <td style="padding: 10px; font-weight: 700; color: #2563eb;">${st.student_code}</td>
                <td style="padding: 10px; font-weight: 700; color: #334155;">${st.class_name || '—'}</td>
                <td style="padding: 10px; font-weight: 700; color: #475569;">${st.cm_staff || '—'}</td>
                <td style="padding: 10px; font-weight: 800; color: #059669;">${st.current_end_date || st.original_end_date || '—'}</td>
                <td style="padding: 10px;"><span class="badge badge-info" style="font-size: 11px;">${st.pipeline_stage}</span></td>
                <td style="padding: 10px; text-align: center;">
                    <div style="display: flex; gap: 4px; justify-content: center; align-items: center;">
                        <button onclick="RenewalsModule.quickMoveStage(${st.id}, '${st.pipeline_stage}', '${AuthModule.escapeHtml(st.student_name).replace(/'/g, "\\'")}', '${st.student_code}');" style="padding: 4px 8px; font-size: 11px; font-weight: 700; background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; border-radius: 5px; cursor: pointer;">
                            ➡️ Chuyển Bước
                        </button>
                        <button onclick="RenewalsModule.openInteractionTimeline('${st.student_code}', '${AuthModule.escapeHtml(st.student_name)}');" style="padding: 4px 8px; font-size: 11px; font-weight: 700; background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; border-radius: 5px; cursor: pointer;">
                            💬 Care Log
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div style="background: #ffffff; border-radius: 12px; padding: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="background: #f8fafc; color: #475569; text-align: left; font-weight: 800;">
                            <th style="padding: 10px;">ID</th>
                            <th style="padding: 10px;">Học Sinh</th>
                            <th style="padding: 10px;">Mã HS</th>
                            <th style="padding: 10px;">Lớp</th>
                            <th style="padding: 10px;">CM Phụ Trách</th>
                            <th style="padding: 10px;">Hạn Hết Phí (Thực Tế)</th>
                            <th style="padding: 10px;">Giai Đoạn CRM</th>
                            <th style="padding: 10px; text-align: center;">Thao Tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        `;
    },

    renderKpiLeaderboard(container) {
        if (!this.pipelineData) return;
        const kpi = this.pipelineData.kpi || {};
        const cmBoard = this.pipelineData.cm_leaderboard || [];

        let rowsHtml = cmBoard.map(c => `
            <tr>
                <td style="padding: 10px; font-weight: 800; color: #0f172a; border-bottom: 1px solid #f1f5f9;">👤 ${c.cm_name}</td>
                <td style="padding: 10px; font-weight: 800; color: #2563eb; border-bottom: 1px solid #f1f5f9;">${c.due} HS</td>
                <td style="padding: 10px; font-weight: 800; color: #16a34a; border-bottom: 1px solid #f1f5f9;">${c.success} HS</td>
                <td style="padding: 10px; font-weight: 800; color: #dc2626; border-bottom: 1px solid #f1f5f9;">${c.failed} HS</td>
                <td style="padding: 10px; font-weight: 900; color: #7c3aed; border-bottom: 1px solid #f1f5f9;">${c.rate}%</td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px;">
                <div style="background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                    <h3 style="margin: 0 0 14px 0; font-size: 16px; font-weight: 900; color: #0f172a;">📊 TỔNG QUAN KPI THÁNG ${this.currentMonth}/${this.currentYear}</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1;">
                            <div style="font-size: 11px; font-weight: 700; color: #64748b;">DOANH SỐ TÁI PHÍ</div>
                            <div style="font-size: 18px; font-weight: 900; color: #059669; margin-top: 4px;">${(kpi.total_revenue || 0).toLocaleString('vi-VN')} VNĐ</div>
                        </div>
                        <div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1;">
                            <div style="font-size: 11px; font-weight: 700; color: #64748b;">TỶ LỆ TÁI PHÍ CHUẨN</div>
                            <div style="font-size: 18px; font-weight: 900; color: #7c3aed; margin-top: 4px;">${kpi.renew_rate || 0}%</div>
                        </div>
                    </div>
                </div>

                <div style="background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                    <h3 style="margin: 0 0 14px 0; font-size: 16px; font-weight: 900; color: #0f172a;">🏆 BẢNG XẾP HẠNG CM TÁI PHÍ</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <thead>
                            <tr style="background: #f8fafc; color: #475569; text-align: left; font-weight: 800;">
                                <th style="padding: 10px;">CM</th>
                                <th style="padding: 10px;">Đến Hạn</th>
                                <th style="padding: 10px;">Thành Công</th>
                                <th style="padding: 10px;">Fail</th>
                                <th style="padding: 10px;">Tỷ Lệ %</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml || '<tr><td colspan="5" style="padding: 10px; text-align: center;">Chưa có dữ liệu</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    makeDraggable(element, handle) {
        if (!element || !handle) return;
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        handle.onmousedown = (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'BUTTON') return;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = () => {
                document.onmouseup = null;
                document.onmousemove = null;
            };
            document.onmousemove = (e2) => {
                e2.preventDefault();
                pos1 = pos3 - e2.clientX;
                pos2 = pos4 - e2.clientY;
                pos3 = e2.clientX;
                pos4 = e2.clientY;
                element.style.top = Math.max(10, (element.offsetTop - pos2)) + "px";
                element.style.left = Math.max(10, (element.offsetLeft - pos1)) + "px";
                element.style.right = "auto";
                element.style.bottom = "auto";
            };
        };
    },

    quickMoveStage(subId, currentStageId, passedName = '', passedCode = '') {
        const modal = document.getElementById('rn-stage-modal');
        const header = document.getElementById('rn-stage-modal-header');
        const subIdInput = document.getElementById('rn-stage-sub-id');
        const codeInput = document.getElementById('rn-stage-student-code');
        const infoDiv = document.getElementById('rn-stage-student-info');
        const extraDiv = document.getElementById('rn-stage-extra-info');
        const selectElem = document.getElementById('rn-stage-select');
        const noteElem = document.getElementById('rn-stage-note');

        if (!modal) {
            console.error("Modal #rn-stage-modal not found!");
            return;
        }

        // Find student object from pipelineData master list
        let stObj = null;
        if (this.pipelineData && this.pipelineData.kanban) {
            for (const list of Object.values(this.pipelineData.kanban)) {
                const found = list.find(x => x.id === subId || x.subscription_id === subId || (passedCode && x.student_code === passedCode));
                if (found) {
                    stObj = found;
                    break;
                }
            }
        }

        const studentName = stObj ? stObj.student_name : (passedName || 'Học sinh');
        const studentCode = stObj ? stObj.student_code : (passedCode || '');
        const className = stObj ? (stObj.class_name || '—') : '—';
        const cmStaff = stObj ? (stObj.cm_staff || 'Chưa phân công') : '—';
        const expiryDate = stObj ? (stObj.current_end_date || stObj.original_end_date || '—') : '—';
        const curStage = stObj ? (stObj.pipeline_stage || currentStageId || 'D-30') : (currentStageId || 'D-30');

        if (subIdInput) subIdInput.value = subId;
        if (codeInput) codeInput.value = studentCode;

        if (infoDiv) {
            infoDiv.innerHTML = `👤 Học sinh: <strong style="color: #2563eb; font-size: 14px;">${AuthModule.escapeHtml(studentName)}</strong> ${studentCode ? `<span style="background: #eff6ff; color: #1d4ed8; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 800; border: 1px solid #bfdbfe; margin-left: 4px;">${studentCode}</span>` : ''}`;
        }
        if (extraDiv) {
            extraDiv.innerHTML = `
                <span>🏫 Lớp: <strong>${AuthModule.escapeHtml(className)}</strong></span>
                <span>👤 CM: <strong>${AuthModule.escapeHtml(cmStaff)}</strong></span>
                <span>📅 Hạn hết phí: <strong style="color: #059669;">${expiryDate}</strong></span>
                <span>📌 Hiện tại: <span class="badge badge-info" style="font-size: 10.5px;">${curStage}</span></span>
            `;
        }

        const nextStageMap = {
            'd30': 'Contacted', 'D-30': 'Contacted',
            'contacted': 'Committed', 'Contacted': 'Committed',
            'committed': 'At-Risk', 'Committed': 'At-Risk',
            'at_risk': 'Failed', 'At-Risk': 'Failed'
        };
        const defaultTarget = nextStageMap[curStage] || 'Contacted';
        if (selectElem) selectElem.value = defaultTarget;
        if (noteElem) noteElem.value = '';

        this.updateStagePreviewBanner(curStage);
        this.makeDraggable(modal, header);

        // Reset default position
        modal.style.top = '120px';
        modal.style.right = '40px';
        modal.style.left = 'auto';
        modal.style.display = 'block';
    },

    updateStagePreviewBanner(forcedCurrentStage = null) {
        const selectElem = document.getElementById('rn-stage-select');
        const bannerElem = document.getElementById('rn-stage-preview-banner');
        if (!bannerElem || !selectElem) return;

        const stageLabels = {
            'D-30': 'Sắp Đến Hạn (D-30)',
            'Contacted': 'Đã Liên Hệ & Tư Vấn',
            'Committed': 'Cam Kết Đóng Phí',
            'At-Risk': 'Do Dự / Nguy Cơ Nghỉ',
            'Success': 'Thành Công (Tái Phí / Chồng Phí)',
            'Failed': 'Thất Bại / Churned'
        };

        const targetVal = selectElem.value;
        const targetLabel = stageLabels[targetVal] || targetVal;

        bannerElem.innerHTML = `🔄 Chuyển sang bước: <strong style="color: #1d4ed8; font-size: 12.5px;">${targetLabel}</strong>`;
    },

    closeStageModal() {
        const modal = document.getElementById('rn-stage-modal');
        if (modal) modal.style.display = 'none';
    },

    async submitStageChange() {
        const subId = document.getElementById('rn-stage-sub-id')?.value;
        const targetStage = document.getElementById('rn-stage-select')?.value;
        const note = document.getElementById('rn-stage-note')?.value || '';

        if (!subId || !targetStage) {
            alert('Vui lòng chọn giai đoạn chuyển hợp lệ!');
            return;
        }

        try {
            const res = await API.post('/crm/renewals/stage', {
                subscription_id: subId,
                stage: targetStage,
                note: note
            });

            if (res && res.success) {
                this.closeStageModal();
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast('✅ ' + res.message, 'success');
                } else {
                    alert('✅ ' + res.message);
                }
                await this.loadData();
            } else {
                alert('Lỗi chuyển giai đoạn: ' + (res ? res.error : 'Không thể cập nhật'));
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        }
    },

    openPaymentModal(stCode = '') {
        if (typeof AuthModule !== 'undefined' && !AuthModule.isAdmin()) {
            alert('Chỉ tài khoản Quản trị viên (Admin) mới có quyền thực hiện chức năng Nhập Đóng Phí!');
            return;
        }
        const modal = document.getElementById('rn-payment-modal');
        const codeInput = document.getElementById('rn-pm-student-code');
        if (modal) {
            modal.style.display = 'flex';
            if (codeInput && stCode) codeInput.value = stCode;
        }
    },

    closePaymentModal() {
        const modal = document.getElementById('rn-payment-modal');
        if (modal) modal.style.display = 'none';
    },

    async submitPaymentTransaction() {
        const student_code = document.getElementById('rn-pm-student-code')?.value || '';
        const is_early_renewal = document.getElementById('rn-pm-is-early')?.value || '0';
        const package_sessions = document.getElementById('rn-pm-sessions')?.value || '72';
        const amount = document.getElementById('rn-pm-amount')?.value || '7200000';
        const notes = document.getElementById('rn-pm-notes')?.value || '';

        if (!student_code.trim()) {
            alert('Vui lòng nhập Mã hoặc Họ tên học sinh!');
            return;
        }

        try {
            const currentUser = (typeof AuthModule !== 'undefined' && AuthModule.getUser) ? AuthModule.getUser() : null;
            const created_by = currentUser ? currentUser.full_name : 'Admin';

            const res = await API.post('/crm/renewals/transaction', {
                student_code: student_code.trim(),
                is_early_renewal: parseInt(is_early_renewal),
                package_sessions: parseInt(package_sessions),
                amount: parseFloat(amount),
                notes: notes,
                created_by: created_by
            });

            if (res && res.success) {
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast('🎉 ' + res.message, 'success');
                } else {
                    alert('🎉 ' + res.message);
                }
                this.closePaymentModal();
                await this.loadData();
            } else {
                alert('Lỗi ghi nhận đóng phí: ' + (res ? res.error : 'Không thể lưu'));
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        }
    },

    async openInteractionTimeline(studentCode, studentName) {
        const modal = document.getElementById('rn-timeline-modal');
        const titleEl = document.getElementById('rn-timeline-title');
        const bodyEl = document.getElementById('rn-timeline-body');

        if (titleEl) titleEl.innerText = `📖 Nhật Ký Chăm Sóc & Tương Tác - ${studentName} (${studentCode || ''})`;
        if (bodyEl) bodyEl.innerHTML = `<div style="text-align: center; color: #64748b; padding: 20px;">Đang đọc nhật ký tương tác...</div>`;
        if (modal) modal.style.display = 'flex';

        try {
            const key = studentCode || studentName;
            const res = await API.getStudentInteractions(key);
            if (res && res.success) {
                const logs = res.timeline || [];
                if (logs.length === 0) {
                    bodyEl.innerHTML = `
                        <div style="text-align: center; color: #64748b; padding: 30px;">
                            <div style="font-size: 32px; margin-bottom: 8px;">💬</div>
                            <div style="font-weight: 700;">Chưa có lịch sử chăm sóc phụ huynh nào cho học sinh này</div>
                        </div>
                    `;
                    return;
                }

                let html = `<div style="position: relative; padding-left: 20px; border-left: 2px solid #cbd5e1; margin-left: 10px;">`;
                logs.forEach(item => {
                    html += `
                        <div style="position: relative; margin-bottom: 16px;">
                            <div style="position: absolute; left: -26px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background: #0284c7; border: 2px solid #ffffff;"></div>
                            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <span style="font-size: 12px; font-weight: 800; color: #0f172a;">👤 ${AuthModule.escapeHtml(item.staff_name || 'Admin')}</span>
                                    <span style="font-size: 11px; color: #64748b;">🕒 ${item.created_at || '—'}</span>
                                </div>
                                <div style="font-size: 12.5px; color: #334155;">${AuthModule.escapeHtml(item.detail || item.note || '')}</div>
                            </div>
                        </div>
                    `;
                });
                html += `</div>`;
                bodyEl.innerHTML = html;
            } else {
                bodyEl.innerHTML = `<div style="color: #ef4444; text-align: center; padding: 20px;">Lỗi: ${res.error}</div>`;
            }
        } catch (e) {
            bodyEl.innerHTML = `<div style="color: #ef4444; text-align: center; padding: 20px;">Lỗi kết nối: ${e.message}</div>`;
        }
    },

    closeTimelineModal() {
        const modal = document.getElementById('rn-timeline-modal');
        if (modal) modal.style.display = 'none';
    },

    async recalculateExpiry() {
        if (typeof AuthModule !== 'undefined' && !AuthModule.isAdmin()) {
            alert('Chỉ tài khoản Quản trị viên (Admin) mới có quyền Tính Lại Hạn Hết Phí!');
            return;
        }
        if (!confirm('Anh/chị có chắc muốn tính toán lại Hạn Hết Phí Dự Kiến cho tất cả lượt tái phí không?')) return;
        try {
            const res = await API.recalculateRenewalExpiry();
            if (res.success) {
                alert(`✅ Đã tính toán lại thành công cho ${res.updated} bản ghi học sinh!`);
                await this.loadData();
            } else {
                alert('Lỗi: ' + res.error);
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        }
    },

    exportPDFReport() {
        const url = `/api/renewals/report-pdf?month=${this.currentMonth}&year=${this.currentYear}&cm_staff=${encodeURIComponent(this.currentCm)}`;
        window.open(url, '_blank');
    }
};
