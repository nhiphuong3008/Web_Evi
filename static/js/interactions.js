/**
 * EVI Dashboard - Central Parent Interactions Module (Nhật Ký Tương Tác Phụ Huynh)
 * Dynamic Timeline Card View (Phương án 3) & Table View Toggle
 */

const InteractionsModule = {
    currentCm: '',
    currentSearch: '',
    currentMonth: '',
    currentYear: '',
    currentViewMode: 'timeline', // 'timeline' (Phương án 3) or 'table'
    interactionsData: [],

    async render(container) {
        if (!container) container = document.getElementById('page-content');
        if (!container) return;

        container.innerHTML = `
            <div style="padding: 16px; width: 100%; box-sizing: border-box;">
                
                <!-- TOP HEADER -->
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 18px 20px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                    <div>
                        <h2 style="margin: 0 0 4px; font-size: 18px; font-weight: 900; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                            📖 NHẬT KÝ TƯƠNG TÁC PHỤ HUYNH TRUNG TÂM
                        </h2>
                        <div style="font-size: 13px; color: #64748b; font-weight: 500;">
                            Quản lý & lưu trữ tập trung toàn bộ nhật ký chăm sóc phụ huynh (Tự động đồng bộ tới Tái Phí & Hồ sơ HS)
                        </div>
                    </div>

                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <button class="btn btn-primary" onclick="InteractionsModule.openAddModal();" style="padding: 9px 18px; font-size: 13.5px; font-weight: 800; border-radius: 8px; background: #059669; color: #ffffff; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(5,150,105,0.35); display: flex; align-items: center; gap: 6px;">
                            ➕ Thêm Nhật Ký Tương Tác
                        </button>
                    </div>
                </div>

                <!-- FILTERS & VIEW SWITCHER BAR -->
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <label style="font-size: 13px; font-weight: 700; color: #475569;">👤 Lọc CM:</label>
                            <select id="it_filter_cm" onchange="InteractionsModule.handleFilterChange();" style="padding: 7px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700;">
                                <option value="">-- Tất cả CM --</option>
                                ${['NgọcCM', 'AnhPTT', 'AnhNV'].map(c => `<option value="${c}" ${this.currentCm === c ? 'selected' : ''}>${c}</option>`).join('')}
                            </select>
                        </div>

                        <div style="display: flex; align-items: center; gap: 6px;">
                            <label style="font-size: 13px; font-weight: 700; color: #475569;">🔍 Học Sinh / Mã HS:</label>
                            <input type="text" id="it_filter_search" placeholder="Nhập tên hoặc EVIxxx..." onkeyup="if(event.key==='Enter') InteractionsModule.handleFilterChange();" style="padding: 7px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 600; width: 200px;">
                        </div>

                        <div style="display: flex; align-items: center; gap: 6px;">
                            <label style="font-size: 13px; font-weight: 700; color: #475569;">📅 Tháng:</label>
                            <select id="it_filter_month" onchange="InteractionsModule.handleFilterChange();" style="padding: 7px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700;">
                                <option value="">-- Tất cả tháng --</option>
                                ${Array.from({length: 12}, (_, i) => i + 1).map(m => `<option value="${m}" ${this.currentMonth == m ? 'selected' : ''}>Tháng ${m}</option>`).join('')}
                            </select>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <label style="font-size: 13px; font-weight: 700; color: #475569;">🗓️ Năm:</label>
                            <select id="it_filter_year" onchange="InteractionsModule.handleFilterChange();" style="padding: 7px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-weight: 700;">
                                <option value="">-- Tất cả năm --</option>
                                <option value="2026" ${this.currentYear === '2026' ? 'selected' : ''}>Năm 2026</option>
                                <option value="2025" ${this.currentYear === '2025' ? 'selected' : ''}>Năm 2025</option>
                                <option value="2024" ${this.currentYear === '2024' ? 'selected' : ''}>Năm 2024</option>
                                <option value="2023" ${this.currentYear === '2023' ? 'selected' : ''}>Năm 2023</option>
                                <option value="2023-2025" ${this.currentYear === '2023-2025' ? 'selected' : ''}>🗓️ Giai đoạn 2023 - 2025</option>
                            </select>
                        </div>

                        <button class="btn" onclick="InteractionsModule.loadData();" style="padding: 7px 14px; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 8px; font-weight: 700; cursor: pointer; background: #f8fafc;">
                            🔄 Tìm Kiếm
                        </button>
                    </div>

                    <!-- VIEW SWITCHER TOGGLE -->
                    <div style="display: flex; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 3px; gap: 2px;">
                        <button id="it-view-btn-timeline" onclick="InteractionsModule.switchView('timeline');" style="padding: 6px 14px; font-size: 12.5px; font-weight: 800; border: none; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; ${this.currentViewMode === 'timeline' ? 'background: #2563eb; color: #ffffff; box-shadow: 0 2px 6px rgba(37,99,235,0.3);' : 'background: transparent; color: #64748b;'}">
                            📜 Dòng Thời Gian (Timeline)
                        </button>
                        <button id="it-view-btn-table" onclick="InteractionsModule.switchView('table');" style="padding: 6px 14px; font-size: 12.5px; font-weight: 800; border: none; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; ${this.currentViewMode === 'table' ? 'background: #2563eb; color: #ffffff; box-shadow: 0 2px 6px rgba(37,99,235,0.3);' : 'background: transparent; color: #64748b;'}">
                            📊 Bảng Chi Tiết (Table)
                        </button>
                    </div>
                </div>

                <!-- CONTENT VIEW CONTAINER -->
                <div id="it-table-container" style="width: 100%;">
                    <div style="padding: 20px; text-align: center; color: #64748b;">Đang tải danh sách nhật ký tương tác...</div>
                </div>

            </div>

            <!-- MODAL ADD INTERACTION -->
            <div id="it-add-modal" class="modal" onclick="if(event.target===this) InteractionsModule.closeAddModal();" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(4px); z-index: 9999; display: none; align-items: center; justify-content: center; padding: 16px; box-sizing: border-box;">
                <div class="modal-content" style="max-width: 540px; width: 100%; border-radius: 12px; background: #ffffff; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2); overflow: visible; transform: translateY(0); transition: all 0.2s ease;">
                    <div class="modal-header" style="background: #059669; color: #ffffff; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; border-top-left-radius: 12px; border-top-right-radius: 12px;">
                        <h3 style="margin: 0; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                            ➕ Thêm Nhật Ký Tương Tác Phụ Huynh Mới
                        </h3>
                        <span class="modal-close" onclick="InteractionsModule.closeAddModal();" style="color: #ffffff; font-size: 24px; cursor: pointer; line-height: 1;">&times;</span>
                    </div>
                    <div class="modal-body" style="padding: 20px; max-height: 80vh; overflow-y: auto;">
                        <div style="margin-bottom: 14px; position: relative;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">Mã Học Sinh / Tên Học Sinh (*):</label>
                            <input type="text" id="it_input_st_code" placeholder="Gõ tên hoặc mã HS (VD: EVI198, Hưng)..." autocomplete="off" oninput="InteractionsModule.onStudentInput(this.value, 'add');" onfocus="InteractionsModule.onStudentInput(this.value, 'add');" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; box-sizing: border-box;">
                            <input type="hidden" id="it_input_selected_st_code">
                            <input type="hidden" id="it_input_selected_st_name">
                            <input type="hidden" id="it_input_selected_class_name">

                            <!-- Dropdown Autocomplete Suggestions -->
                            <div id="it_add_st_dropdown" style="display: none; position: absolute; top: 100%; left: 0; right: 0; max-height: 230px; overflow-y: auto; background: #ffffff; border: 1.5px solid #059669; border-radius: 8px; box-shadow: 0 12px 28px rgba(0,0,0,0.18); z-index: 10000; margin-top: 4px;"></div>
                        </div>

                        <div style="margin-bottom: 14px;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">📅 Ngày Tương Tác (*):</label>
                            <input type="date" id="it_input_date" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; font-weight: 600; font-family: inherit; color: #0f172a; box-sizing: border-box;">
                        </div>

                        <div style="margin-bottom: 14px;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">CM / Nhân Viên Phụ Trách (*):</label>
                            <select id="it_input_staff" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; font-weight: 600; box-sizing: border-box;">
                                ${['NgọcCM', 'AnhPTT', 'AnhNV'].map(c => `<option value="${c}">${c}</option>`).join('')}
                            </select>
                        </div>

                        <div style="margin-bottom: 18px;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">Nội Dung Chi Tiết Trao Đổi Phụ Huynh (*):</label>
                            <textarea id="it_input_detail" rows="5" placeholder="Nhập chi tiết nội dung cuộc gọi hoặc phản hồi từ phụ huynh..." style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; font-family: inherit; box-sizing: border-box;"></textarea>
                        </div>

                        <div style="display: flex; justify-content: flex-end; gap: 10px;">
                            <button class="btn" onclick="InteractionsModule.closeAddModal();" style="padding: 8px 16px; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 8px; cursor: pointer;">Hủy</button>
                            <button class="btn btn-primary" onclick="InteractionsModule.saveInteraction();" style="padding: 8px 20px; font-size: 13px; font-weight: 800; background: #059669; color: #ffffff; border: none; border-radius: 8px; cursor: pointer;">💾 Lưu Tương Tác</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MODAL EDIT INTERACTION (ADMIN) -->
            <div id="it-edit-modal" class="modal" onclick="if(event.target===this) InteractionsModule.closeEditModal();" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(4px); z-index: 9999; display: none; align-items: center; justify-content: center; padding: 16px; box-sizing: border-box;">
                <div class="modal-content" style="max-width: 540px; width: 100%; border-radius: 12px; background: #ffffff; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2); overflow: visible; transform: translateY(0); transition: all 0.2s ease;">
                    <div class="modal-header" style="background: #2563eb; color: #ffffff; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; border-top-left-radius: 12px; border-top-right-radius: 12px;">
                        <h3 style="margin: 0; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                            ✏️ Chỉnh Sửa Nhật Ký Tương Tác Phụ Huynh
                        </h3>
                        <span class="modal-close" onclick="InteractionsModule.closeEditModal();" style="color: #ffffff; font-size: 24px; cursor: pointer; line-height: 1;">&times;</span>
                    </div>
                    <div class="modal-body" style="padding: 20px; max-height: 80vh; overflow-y: auto;">
                        <input type="hidden" id="it_edit_id">
                        <div style="margin-bottom: 14px; position: relative;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">Mã Học Sinh / Tên Học Sinh (*):</label>
                            <input type="text" id="it_edit_st_code" placeholder="Gõ tên hoặc mã HS..." autocomplete="off" oninput="InteractionsModule.onStudentInput(this.value, 'edit');" onfocus="InteractionsModule.onStudentInput(this.value, 'edit');" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; box-sizing: border-box;">
                            <input type="hidden" id="it_edit_selected_st_code">
                            <input type="hidden" id="it_edit_selected_st_name">
                            <input type="hidden" id="it_edit_selected_class_name">

                            <div id="it_edit_st_dropdown" style="display: none; position: absolute; top: 100%; left: 0; right: 0; max-height: 230px; overflow-y: auto; background: #ffffff; border: 1.5px solid #2563eb; border-radius: 8px; box-shadow: 0 12px 28px rgba(0,0,0,0.18); z-index: 10000; margin-top: 4px;"></div>
                        </div>

                        <div style="margin-bottom: 14px;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">📅 Ngày Tương Tác (*):</label>
                            <input type="date" id="it_edit_date" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; font-weight: 600; font-family: inherit; color: #0f172a; box-sizing: border-box;">
                        </div>

                        <div style="margin-bottom: 14px;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">CM / Nhân Viên Phụ Trách (*):</label>
                            <select id="it_edit_staff" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; font-weight: 600; box-sizing: border-box;">
                                ${['NgọcCM', 'AnhPTT', 'AnhNV'].map(c => `<option value="${c}">${c}</option>`).join('')}
                            </select>
                        </div>

                        <div style="margin-bottom: 18px;">
                            <label style="display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px;">Nội Dung Chi Tiết Trao Đổi Phụ Huynh (*):</label>
                            <textarea id="it_edit_detail" rows="5" style="width: 100%; padding: 9px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 13.5px; font-family: inherit; box-sizing: border-box;"></textarea>
                        </div>

                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <button class="btn" onclick="InteractionsModule.deleteInteractionFromModal();" style="padding: 8px 16px; font-size: 13px; font-weight: 800; background: #dc2626; color: #ffffff; border: none; border-radius: 8px; cursor: pointer;">
                                🗑️ Xóa Nhật Ký
                            </button>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn" onclick="InteractionsModule.closeEditModal();" style="padding: 8px 16px; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 8px;">Hủy</button>
                                <button class="btn btn-primary" onclick="InteractionsModule.updateInteraction();" style="padding: 8px 20px; font-size: 13px; font-weight: 800; background: #2563eb; border: none; border-radius: 8px;">💾 Cập Nhật Nhật Ký</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await this.loadData();
    },

    switchView(mode) {
        this.currentViewMode = mode;
        const btnTimeline = document.getElementById('it-view-btn-timeline');
        const btnTable = document.getElementById('it-view-btn-table');
        if (btnTimeline && btnTable) {
            if (mode === 'timeline') {
                btnTimeline.style.background = '#2563eb';
                btnTimeline.style.color = '#ffffff';
                btnTimeline.style.boxShadow = '0 2px 6px rgba(37,99,235,0.3)';
                btnTable.style.background = 'transparent';
                btnTable.style.color = '#64748b';
                btnTable.style.boxShadow = 'none';
            } else {
                btnTable.style.background = '#2563eb';
                btnTable.style.color = '#ffffff';
                btnTable.style.boxShadow = '0 2px 6px rgba(37,99,235,0.3)';
                btnTimeline.style.background = 'transparent';
                btnTimeline.style.color = '#64748b';
                btnTimeline.style.boxShadow = 'none';
            }
        }
        const container = document.getElementById('it-table-container');
        if (container) this.renderView(container);
    },

    handleFilterChange() {
        this.currentCm = document.getElementById('it_filter_cm')?.value || '';
        this.currentSearch = document.getElementById('it_filter_search')?.value || '';
        this.currentMonth = document.getElementById('it_filter_month')?.value || '';
        this.currentYear = document.getElementById('it_filter_year')?.value || '';
        this.loadData();
    },

    async loadData() {
        const container = document.getElementById('it-table-container');
        if (!container) return;

        try {
            const res = await API.getAllInteractions({
                cm_staff: this.currentCm,
                search: this.currentSearch,
                month: this.currentMonth,
                year: this.currentYear
            });

            if (res.success) {
                this.interactionsData = res.data || [];
                this.renderView(container);
            } else {
                container.innerHTML = `<div style="padding: 20px; color: #ef4444; text-align: center;">Lỗi: ${res.error}</div>`;
            }
        } catch (e) {
            console.error('Error loading interactions:', e);
            container.innerHTML = `<div style="padding: 20px; color: #ef4444; text-align: center;">Lỗi kết nối máy chủ: ${e.message}</div>`;
        }
    },

    renderView(container) {
        if (this.currentViewMode === 'timeline') {
            this.renderTimeline(container);
        } else {
            this.renderTable(container);
        }
    },

    getCmBadgeStyle(cmName) {
        const name = (cmName || '').trim();
        if (name === 'NgọcCM') return { bg: '#8b5cf6', color: '#ffffff', border: '#7c3aed' }; // Purple
        if (name === 'AnhPTT') return { bg: '#059669', color: '#ffffff', border: '#047857' }; // Emerald
        if (name === 'AnhNV') return { bg: '#2563eb', color: '#ffffff', border: '#1d4ed8' }; // Royal Blue
        return { bg: '#64748b', color: '#ffffff', border: '#475569' };
    },

    renderTimeline(container) {
        if (!this.interactionsData || this.interactionsData.length === 0) {
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px;">
                    <div style="font-size: 40px; margin-bottom: 10px;">📜</div>
                    <div style="font-size: 15px; font-weight: 700; color: #1e293b;">Chưa tìm thấy nhật ký tương tác nào</div>
                    <p style="font-size: 13px; color: #94a3b8; margin-top: 6px; margin-bottom: 16px;">Bấm nút "➕ Thêm Nhật Ký Tương Tác" ở trên để tạo ghi nhận chăm sóc mới.</p>
                </div>
            `;
            return;
        }

        const cardsHtml = this.interactionsData.map((r, i) => {
            const cmStyle = this.getCmBadgeStyle(r.staff_name);
            const fullDetail = Utils.escapeHtml(r.interaction_detail || r.note || '—');
            const isLong = fullDetail.length > 240;
            const shortDetail = isLong ? fullDetail.slice(0, 220) + '...' : fullDetail;

            return `
                <div class="timeline-item" style="position: relative; padding-left: 36px; margin-bottom: 20px;">
                    <!-- TIMELINE NODE DOT -->
                    <div style="position: absolute; left: 0; top: 16px; width: 22px; height: 22px; border-radius: 50%; background: ${cmStyle.bg}; border: 3px solid #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 2; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 10px; font-weight: 900;">
                        ✓
                    </div>

                    <!-- TIMELINE CARD -->
                    <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-left: 4px solid ${cmStyle.bg}; border-radius: 12px; padding: 16px 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.03); transition: transform 0.15s ease, box-shadow 0.15s ease;">
                        
                        <!-- CARD HEADER -->
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; border-bottom: 1px dashed #e2e8f0; padding-bottom: 10px; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                                <span style="font-size: 15px; font-weight: 900; color: #0f172a;">
                                    ${Utils.escapeHtml(r.student_name)}
                                </span>
                                ${r.english_name ? `<span style="font-size: 12.5px; color: #64748b; font-weight: 600;">(${Utils.escapeHtml(r.english_name)})</span>` : ''}
                                
                                ${r.student_code ? `<span style="font-size: 11.5px; font-weight: 800; background: #eff6ff; color: #1d4ed8; padding: 2px 8px; border-radius: 6px; border: 1px solid #bfdbfe;">${r.student_code}</span>` : ''}
                                
                                ${r.class_name ? `<span style="font-size: 11.5px; font-weight: 700; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 6px;">${Utils.escapeHtml(r.class_name)}</span>` : ''}
                            </div>

                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 12px; font-weight: 800; background: ${cmStyle.bg}; color: ${cmStyle.color}; padding: 3px 10px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    👤 ${r.staff_name || '—'}
                                </span>
                                <span style="font-size: 12px; color: #64748b; font-weight: 700; background: #f8fafc; padding: 3px 8px; border-radius: 6px; border: 1px solid #e2e8f0;">
                                    🕒 ${r.created_at || '—'}
                                </span>

                                <div style="display: flex; gap: 4px; margin-left: 6px;">
                                    <button onclick="InteractionsModule.openEditModal(${r.id});" title="Sửa ghi nhận" style="padding: 4px 9px; font-size: 12px; font-weight: 700; background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 6px; cursor: pointer;">
                                        ✏️ Sửa
                                    </button>
                                    <button onclick="InteractionsModule.deleteInteraction(${r.id});" title="Xóa ghi nhận" style="padding: 4px 9px; font-size: 12px; font-weight: 700; background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; border-radius: 6px; cursor: pointer;">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- CARD BODY TEXT -->
                        <div style="background: #f8fafc; border-radius: 8px; padding: 12px 14px; border: 1px solid #f1f5f9; font-size: 13.5px; color: #334155; line-height: 1.6; word-break: break-word;">
                            ${isLong ? `
                                <div id="it-detail-short-${r.id}">
                                    ${shortDetail}
                                    <button onclick="document.getElementById('it-detail-short-${r.id}').style.display='none'; document.getElementById('it-detail-full-${r.id}').style.display='block';" style="background: none; border: none; color: #2563eb; font-weight: 800; cursor: pointer; padding: 0 4px; font-size: 12.5px; text-decoration: underline;">
                                        👁️ Xem thêm
                                    </button>
                                </div>
                                <div id="it-detail-full-${r.id}" style="display: none;">
                                    ${fullDetail}
                                    <div style="margin-top: 6px;">
                                        <button onclick="document.getElementById('it-detail-full-${r.id}').style.display='none'; document.getElementById('it-detail-short-${r.id}').style.display='block';" style="background: none; border: none; color: #64748b; font-weight: 700; cursor: pointer; padding: 0; font-size: 12px; text-decoration: underline;">
                                            ▲ Thu gọn
                                        </button>
                                    </div>
                                </div>
                            ` : fullDetail}
                        </div>

                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="timeline-wrapper" style="position: relative; padding: 10px 0 20px 10px; width: 100%; box-sizing: border-box;">
                <!-- VERTICAL TIMELINE LINE -->
                <div style="position: absolute; left: 20px; top: 20px; bottom: 30px; width: 2px; background: #cbd5e1; border-left: 2px dashed #94a3b8; z-index: 1;"></div>
                
                ${cardsHtml}
            </div>
        `;
    },

    renderTable(container) {
        if (!this.interactionsData || this.interactionsData.length === 0) {
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #64748b; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px;">
                    <div style="font-size: 40px; margin-bottom: 10px;">📖</div>
                    <div style="font-size: 15px; font-weight: 700;">Chưa tìm thấy nhật ký tương tác nào</div>
                    <p style="font-size: 13px; color: #94a3b8; margin-top: 6px; margin-bottom: 16px;">Bấm nút "➕ Thêm Nhật Ký Tương Tác" ở trên để tạo ghi nhận chăm sóc mới.</p>
                </div>
            `;
            return;
        }

        const rowsHtml = this.interactionsData.map((r, i) => {
            return `
                <tr style="border-bottom: 1px solid #e2e8f0; background: ${i % 2 === 0 ? '#ffffff' : '#f8fafc'};">
                    <td style="font-weight: 600; color: #64748b; padding: 12px 14px;">#${r.id}</td>
                    <td style="font-size: 12px; color: #64748b; font-weight: 700; white-space: nowrap; padding: 12px 14px;">${r.created_at || '—'}</td>
                    <td style="font-weight: 800; color: #0f172a; padding: 12px 14px;">
                        ${Utils.escapeHtml(r.student_name)}
                        ${r.english_name ? `<span style="font-size: 11.5px; color: #64748b; font-weight: 500;">(${Utils.escapeHtml(r.english_name)})</span>` : ''}
                    </td>
                    <td style="font-size: 12px; font-weight: 700; color: #2563eb; padding: 12px 14px;">${r.student_code || '—'}</td>
                    <td style="font-size: 12.5px; font-weight: 700; color: #475569; padding: 12px 14px;">${r.staff_name || '—'}</td>
                    <td style="font-size: 13px; color: #334155; max-width: 600px; word-break: break-word; line-height: 1.55; padding: 12px 14px;">${Utils.escapeHtml(r.interaction_detail || r.note || '—')}</td>
                    <td style="text-align: center; white-space: nowrap; padding: 12px 14px;">
                        <button class="btn" onclick="InteractionsModule.openEditModal(${r.id});" style="padding: 5px 10px; font-size: 12px; font-weight: 700; background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 6px; cursor: pointer;">
                            ✏️ Sửa
                        </button>
                        <button class="btn" onclick="InteractionsModule.deleteInteraction(${r.id});" style="padding: 5px 10px; font-size: 12px; font-weight: 700; background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; border-radius: 6px; cursor: pointer; margin-left: 4px;">
                            🗑️ Xóa
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        container.innerHTML = `
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
                <div style="overflow-x: auto; width: 100%;">
                    <table class="data-table" style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <thead>
                            <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1; color: #1e293b; text-align: left;">
                                <th style="width: 60px; padding: 12px 14px;">ID</th>
                                <th style="width: 130px; padding: 12px 14px;">Thời Gian</th>
                                <th style="width: 160px; padding: 12px 14px;">Học Sinh</th>
                                <th style="width: 85px; padding: 12px 14px;">Mã HS</th>
                                <th style="width: 100px; padding: 12px 14px;">CM Thực Hiện</th>
                                <th style="padding: 12px 14px;">Nội Dung Chi Tiết Chăm Sóc & Phản Hồi PH</th>
                                <th style="width: 110px; text-align: center; padding: 12px 14px;">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    allStudents: [],

    removeAccents(str) {
        return (str || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
    },

    getCurrentLocalDateIso() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    formatDateForInput(dateStr) {
        if (!dateStr) return this.getCurrentLocalDateIso();
        let d;
        if (dateStr.includes('/')) {
            const parts = dateStr.split(' ');
            const dateParts = parts[0].split('/');
            if (dateParts.length === 3) {
                d = new Date(`${dateParts[2]}-${dateParts[1].padStart(2, '0')}-${dateParts[0].padStart(2, '0')}T00:00:00`);
            }
        } else {
            d = new Date(dateStr.replace(' ', 'T'));
        }
        if (!d || isNaN(d.getTime())) return this.getCurrentLocalDateIso();

        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    async loadAllStudents() {
        if (this.allStudents && this.allStudents.length > 0) return this.allStudents;

        // Priority 1: Link with StudentsModule if student list is already in memory
        if (typeof StudentsModule !== 'undefined' && StudentsModule.studentsData && StudentsModule.studentsData.length > 0) {
            this.allStudents = StudentsModule.studentsData;
            return this.allStudents;
        }

        // Priority 2: Query API.getStudents()
        try {
            const res = await API.getStudents();
            if (res && res.success) {
                this.allStudents = res.data || [];
            }
        } catch (e) {
            console.error('Error prefetching students for autocomplete:', e);
            try {
                const res = await API.get('/students');
                if (res && res.success) {
                    this.allStudents = res.data || [];
                }
            } catch (err) {
                console.error('Fallback error fetching students:', err);
            }
        }
        return this.allStudents;
    },

    async onStudentInput(query, mode = 'add') {
        await this.loadAllStudents();
        const dropdown = document.getElementById(`it_${mode}_st_dropdown`);
        if (!dropdown) return;

        const rawQ = (query || '').trim();
        const normQ = this.removeAccents(rawQ);

        if (normQ.length === 0) {
            const topHtml = (this.allStudents || []).slice(0, 15).map(st => `
                <div onmousedown="InteractionsModule.selectStudent('${st.code || st.student_code || ''}', '${Utils.escapeHtml(st.full_name || st.name || st.student_name || '').replace(/'/g, "\\'")}', '${Utils.escapeHtml(st.class_name || st.original_class || '').replace(/'/g, "\\'")}', '${mode}');"
                     style="padding: 10px 14px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s; font-size: 13px; background: #ffffff;"
                     onmouseover="this.style.background='#f0f9ff';"
                     onmouseout="this.style.background='#ffffff';">
                    <div style="font-weight: 800; color: #0f172a; display: flex; justify-content: space-between; align-items: center;">
                        <span>${Utils.escapeHtml(st.full_name || st.name || st.student_name || '')} ${st.english_name ? `<span style="font-size: 12px; color: #64748b; font-weight: 500;">(${Utils.escapeHtml(st.english_name)})</span>` : ''}</span>
                        <span style="color: #0284c7; font-family: monospace; font-size: 12px; font-weight: 800; background: #e0f2fe; padding: 1px 6px; border-radius: 4px;">${st.code || st.student_code || ''}</span>
                    </div>
                    <div style="font-size: 11.5px; color: #64748b; margin-top: 3px;">🏫 Lớp: <strong>${Utils.escapeHtml(st.class_name || st.original_class || 'Chưa xếp lớp')}</strong></div>
                </div>
            `).join('');

            dropdown.innerHTML = `<div style="padding: 6px 12px; font-size: 11px; font-weight: 800; color: #64748b; background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-transform: uppercase;">💡 Danh sách gợi ý học sinh Center:</div>` + topHtml;
            dropdown.style.display = 'block';
            return;
        }

        const matches = (this.allStudents || []).filter(st => {
            const normName = this.removeAccents(st.full_name || st.name || st.student_name || '');
            const normCode = this.removeAccents(st.code || st.student_code || '');
            const normEn = this.removeAccents(st.english_name || '');
            const normClass = this.removeAccents(st.class_name || st.original_class || '');
            return normName.includes(normQ) || normCode.includes(normQ) || normEn.includes(normQ) || normClass.includes(normQ);
        });

        if (matches.length === 0) {
            dropdown.innerHTML = `<div style="padding: 12px 14px; color: #94a3b8; font-size: 13px; font-weight: 600; text-align: center;">❌ Không tìm thấy học sinh phù hợp với "${Utils.escapeHtml(rawQ)}"</div>`;
            dropdown.style.display = 'block';
            return;
        }

        const itemsHtml = matches.slice(0, 30).map(st => `
            <div onmousedown="InteractionsModule.selectStudent('${st.code || st.student_code || ''}', '${Utils.escapeHtml(st.full_name || st.name || st.student_name || '').replace(/'/g, "\\'")}', '${Utils.escapeHtml(st.class_name || st.original_class || '').replace(/'/g, "\\'")}', '${mode}');"
                 style="padding: 10px 14px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.15s; font-size: 13px; background: #ffffff;"
                 onmouseover="this.style.background='#f0f9ff';"
                 onmouseout="this.style.background='#ffffff';">
                <div style="font-weight: 800; color: #0f172a; display: flex; justify-content: space-between; align-items: center;">
                    <span>${Utils.escapeHtml(st.full_name || st.name || st.student_name || '')} ${st.english_name ? `<span style="font-size: 12px; color: #64748b; font-weight: 500;">(${Utils.escapeHtml(st.english_name)})</span>` : ''}</span>
                    <span style="color: #0284c7; font-family: monospace; font-size: 12px; font-weight: 800; background: #e0f2fe; padding: 1px 6px; border-radius: 4px;">${st.code || st.student_code || ''}</span>
                </div>
                <div style="font-size: 11.5px; color: #64748b; margin-top: 3px;">🏫 Lớp: <strong>${Utils.escapeHtml(st.class_name || st.original_class || 'Chưa xếp lớp')}</strong></div>
            </div>
        `).join('');

        dropdown.innerHTML = itemsHtml;
        dropdown.style.display = 'block';
    },

    selectStudent(code, name, className, mode = 'add') {
        const inputEl = document.getElementById(mode === 'add' ? 'it_input_st_code' : 'it_edit_st_code');
        const selCodeEl = document.getElementById(mode === 'add' ? 'it_input_selected_st_code' : 'it_edit_selected_st_code');
        const selNameEl = document.getElementById(mode === 'add' ? 'it_input_selected_st_name' : 'it_edit_selected_st_name');
        const selClassEl = document.getElementById(mode === 'add' ? 'it_input_selected_class_name' : 'it_edit_selected_class_name');
        const dropdown = document.getElementById(`it_${mode}_st_dropdown`);

        if (inputEl) inputEl.value = `${name} (${code})`;
        if (selCodeEl) selCodeEl.value = code;
        if (selNameEl) selNameEl.value = name;
        if (selClassEl) selClassEl.value = className;
        if (dropdown) dropdown.style.display = 'none';
    },

    async openAddModal() {
        await this.loadAllStudents();
        const modal = document.getElementById('it-add-modal');
        if (modal) modal.style.display = 'flex';

        if (document.getElementById('it_input_date')) {
            document.getElementById('it_input_date').value = this.getCurrentLocalDateIso();
        }
        if (document.getElementById('it_input_st_code')) document.getElementById('it_input_st_code').value = '';
        if (document.getElementById('it_input_selected_st_code')) document.getElementById('it_input_selected_st_code').value = '';
        if (document.getElementById('it_input_selected_st_name')) document.getElementById('it_input_selected_st_name').value = '';
        if (document.getElementById('it_input_selected_class_name')) document.getElementById('it_input_selected_class_name').value = '';
        if (document.getElementById('it_input_detail')) document.getElementById('it_input_detail').value = '';
        if (document.getElementById('it_add_st_dropdown')) document.getElementById('it_add_st_dropdown').style.display = 'none';
    },

    closeAddModal() {
        const modal = document.getElementById('it-add-modal');
        if (modal) modal.style.display = 'none';
        if (document.getElementById('it_add_st_dropdown')) document.getElementById('it_add_st_dropdown').style.display = 'none';
    },

    async openEditModal(id) {
        await this.loadAllStudents();
        const item = this.interactionsData.find(x => x.id === id);
        if (!item) return;

        if (document.getElementById('it_edit_id')) document.getElementById('it_edit_id').value = item.id;
        if (document.getElementById('it_edit_st_code')) {
            const displayVal = item.student_code ? `${item.student_name} (${item.student_code})` : item.student_name;
            document.getElementById('it_edit_st_code').value = displayVal || '';
        }
        if (document.getElementById('it_edit_selected_st_code')) document.getElementById('it_edit_selected_st_code').value = item.student_code || '';
        if (document.getElementById('it_edit_selected_st_name')) document.getElementById('it_edit_selected_st_name').value = item.student_name || '';
        if (document.getElementById('it_edit_selected_class_name')) document.getElementById('it_edit_selected_class_name').value = item.class_name || '';
        if (document.getElementById('it_edit_staff')) document.getElementById('it_edit_staff').value = item.staff_name || 'NgọcCM';
        if (document.getElementById('it_edit_detail')) document.getElementById('it_edit_detail').value = item.interaction_detail || item.note || '';
        if (document.getElementById('it_edit_date')) {
            document.getElementById('it_edit_date').value = this.formatDateForInput(item.created_at);
        }
        if (document.getElementById('it_edit_st_dropdown')) document.getElementById('it_edit_st_dropdown').style.display = 'none';

        const modal = document.getElementById('it-edit-modal');
        if (modal) modal.style.display = 'flex';
    },

    closeEditModal() {
        const modal = document.getElementById('it-edit-modal');
        if (modal) modal.style.display = 'none';
        if (document.getElementById('it_edit_st_dropdown')) document.getElementById('it_edit_st_dropdown').style.display = 'none';
    },

    async saveInteraction() {
        const rawStInput = document.getElementById('it_input_st_code')?.value.trim() || '';
        let stCode = document.getElementById('it_input_selected_st_code')?.value.trim() || '';
        let stName = document.getElementById('it_input_selected_st_name')?.value.trim() || '';
        let className = document.getElementById('it_input_selected_class_name')?.value.trim() || '';
        const staffName = document.getElementById('it_input_staff')?.value;
        const detail = document.getElementById('it_input_detail')?.value.trim();
        const interactionDate = document.getElementById('it_input_date')?.value;

        // Fallback: If user typed text directly without clicking suggestion dropdown item
        if ((!stCode || !stName) && rawStInput) {
            const found = (this.allStudents || []).find(st => 
                (st.code && st.code.toLowerCase() === rawStInput.toLowerCase()) ||
                (st.full_name && st.full_name.toLowerCase() === rawStInput.toLowerCase()) ||
                (st.full_name && this.removeAccents(st.full_name) === this.removeAccents(rawStInput))
            );
            if (found) {
                stCode = found.code;
                stName = found.full_name;
                className = found.class_name || '';
            } else {
                stCode = rawStInput;
                stName = rawStInput;
            }
        }

        if (!rawStInput || !detail) {
            alert('Vui lòng chọn Học Sinh và nhập Nội dung chi tiết tương tác!');
            return;
        }

        try {
            const res = await API.addInteraction({
                student_code: stCode,
                student_name: stName,
                class_name: className,
                staff_name: staffName,
                note: 'Tương tác Phụ huynh',
                detail: detail,
                interaction_date: interactionDate
            });

            if (res.success) {
                alert('✅ Đã lưu nhật ký tương tác thành công! Hệ thống đã tự động cập nhật đồng bộ toàn trung tâm.');
                this.closeAddModal();
                await this.loadData();
            } else {
                alert('Lỗi: ' + res.error);
            }
        } catch (e) {
            console.error('Error saving interaction:', e);
            alert('Lỗi kết nối máy chủ: ' + e.message);
        }
    },

    async updateInteraction() {
        const id = document.getElementById('it_edit_id')?.value;
        const rawStInput = document.getElementById('it_edit_st_code')?.value.trim() || '';
        let stCode = document.getElementById('it_edit_selected_st_code')?.value.trim() || '';
        let stName = document.getElementById('it_edit_selected_st_name')?.value.trim() || '';
        let className = document.getElementById('it_edit_selected_class_name')?.value.trim() || '';
        const staffName = document.getElementById('it_edit_staff')?.value;
        const detail = document.getElementById('it_edit_detail')?.value.trim();
        const interactionDate = document.getElementById('it_edit_date')?.value;

        if ((!stCode || !stName) && rawStInput) {
            const found = (this.allStudents || []).find(st => 
                (st.code && st.code.toLowerCase() === rawStInput.toLowerCase()) ||
                (st.full_name && st.full_name.toLowerCase() === rawStInput.toLowerCase()) ||
                (st.full_name && this.removeAccents(st.full_name) === this.removeAccents(rawStInput))
            );
            if (found) {
                stCode = found.code;
                stName = found.full_name;
                className = found.class_name || '';
            } else {
                stCode = rawStInput;
                stName = rawStInput;
            }
        }

        if (!id || !rawStInput || !detail) {
            alert('Vui lòng nhập đầy đủ nội dung chi tiết tương tác!');
            return;
        }

        try {
            const res = await API.updateInteraction(id, {
                student_code: stCode,
                student_name: stName,
                class_name: className,
                staff_name: staffName,
                note: 'Tương tác Phụ huynh',
                detail: detail,
                interaction_date: interactionDate
            });

            if (res.success) {
                alert(`✅ Đã cập nhật thành công nhật ký tương tác #${id}! Dữ liệu đã đồng bộ toàn hệ thống.`);
                this.closeEditModal();
                await this.loadData();
            } else {
                alert('Lỗi: ' + res.error);
            }
        } catch (e) {
            console.error('Error updating interaction:', e);
            alert('Lỗi kết nối máy chủ: ' + e.message);
        }
    },

    deleteInteractionFromModal() {
        const id = document.getElementById('it_edit_id')?.value;
        if (id) {
            this.deleteInteraction(id);
        }
    },

    async deleteInteraction(id) {
        if (!id) return;
        if (!confirm(`Anh/chị có chắc chắn muốn xóa nhật ký tương tác #${id} không?\n(Thao tác này sẽ xóa vĩnh viễn khỏi CSDL SQLite)`)) return;

        try {
            const res = await API.deleteInteraction(id);
            if (res.success) {
                alert(`✅ Đã xóa thành công nhật ký tương tác #${id}!`);
                this.closeEditModal();
                await this.loadData();
                if (typeof RenewalsModule !== 'undefined' && RenewalsModule.loadData) {
                    RenewalsModule.loadData();
                }
            } else {
                alert('Lỗi: ' + res.error);
            }
        } catch (e) {
            console.error('Error deleting interaction:', e);
            alert('Lỗi kết nối máy chủ: ' + e.message);
        }
    }
};

// Global click listener to hide autocomplete dropdowns when clicking outside
document.addEventListener('click', (e) => {
    const addWrap = document.getElementById('it_add_st_dropdown');
    const editWrap = document.getElementById('it_edit_st_dropdown');
    const addInput = document.getElementById('it_input_st_code');
    const editInput = document.getElementById('it_edit_st_code');

    if (addWrap && addInput && !addWrap.contains(e.target) && e.target !== addInput) {
        addWrap.style.display = 'none';
    }
    if (editWrap && editInput && !editWrap.contains(e.target) && e.target !== editInput) {
        editWrap.style.display = 'none';
    }
});
