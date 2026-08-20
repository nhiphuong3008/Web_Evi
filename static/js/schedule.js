/**
 * EVI Dashboard - Schedule & Timetable Module
 * Quản lý & Hiển thị Thời khóa biểu ma trận 7 ngày x 2 Ca (MT5 & MT6) & Pop-up Nhật ký bài học theo buổi.
 */

const ScheduleModule = {
    selectedCm: '',
    matrixData: [],
    availableCms: [],

    async init() {
        const user = Auth.getUser();
        if (user && user.cm_staff_name) {
            this.selectedCm = user.cm_staff_name;
        }
    },

    currentZoom: 1.0, // Always default size 100%

    /**
     * Render trang Thời khóa biểu đầy đủ (#schedule) dạng ma trận trực quan gọn gàng.
     */
    async renderPage(container) {
        if (!container) return;

        container.innerHTML = `
            <!-- Top Navigation Control Bar: Clean layout without unused buttons -->
            <div style="background: #ffffff; padding: 14px 24px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <!-- Left: Hamburger icon & Upper-case Black Title -->
                <div style="display: flex; align-items: center; gap: 14px;">
                    <button style="background: none; border: none; font-size: 22px; cursor: pointer; color: #000; display: flex; align-items: center;" title="Menu">☰</button>
                    <h2 style="margin: 0; font-size: 18px; font-weight: 900; color: #000000; text-transform: uppercase; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;">
                        THỜI KHÓA BIỂU CM & GV - TỪNG HÀNG LỚP
                    </h2>
                </div>

                <!-- Center/Right Selector & Action Bar -->
                <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
                    <button class="btn" style="padding: 6px 14px; font-size: 12.5px; font-weight: 800; background: linear-gradient(135deg, #4f46e5, #7c3aed); border: none; border-radius: 8px; color: #ffffff; cursor: pointer; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25); display: flex; align-items: center; gap: 6px;" onclick="ScheduleModule.openHolidayManagerModal();">
                        🌴 Quản Lý Lịch Nghỉ & Lùi Lịch
                    </button>

                    <div style="display: flex; align-items: center; gap: 8px; font-size: 13px;">
                        <label style="font-weight: 800; color: #1e293b;">Chọn CM:</label>
                        <select id="schedule-cm-selector" class="form-control" style="width: auto; padding: 6px 12px; font-size: 12.5px; font-weight: 700; background: #ffffff; border: 1.5px solid #cbd5e1; color: #0f172a;" onchange="ScheduleModule.onCmSelectChange(this.value);">
                            <option value="">-- Tất cả CM --</option>
                        </select>
                    </div>

                    <!-- Zoom Controls (Fixed 100% default) -->
                    <div style="display: flex; align-items: center; gap: 4px; background: #f1f5f9; padding: 4px 10px; border-radius: 8px; border: 1px solid #cbd5e1;">
                        <span style="color: #475569; font-size: 11.5px; font-weight: 700;">🔍 Thu phóng:</span>
                        <button class="btn btn-sm" style="padding: 2px 6px; font-size: 11px; height: 24px;" onclick="ScheduleModule.setZoom(0.8);">80%</button>
                        <button class="btn btn-sm" style="padding: 2px 6px; font-size: 11px; height: 24px;" onclick="ScheduleModule.setZoom(0.9);">90%</button>
                        <button class="btn btn-sm" style="padding: 2px 6px; font-size: 11px; height: 24px; background: #ff7e5f; color: #fff; font-weight: 800;" onclick="ScheduleModule.setZoom(1.0);">100%</button>
                    </div>
                </div>
            </div>

            <!-- Lavender Background Card List Container (Khu vực danh sách thẻ lớp học bo góc lớn 16px, đổ bóng drop shadow) -->
            <div style="background: #faf5ff; border: 2px solid #e9d5ff; border-radius: 16px; padding: 20px; box-shadow: 0 12px 35px rgba(147, 51, 234, 0.08); margin-bottom: 24px;">
                <!-- Matrix Schedule Table Wrapper -->
                <div id="schedule-matrix-wrapper" style="overflow-x: auto; width: 100%;">
                    <div id="schedule-matrix-container" style="transform-origin: top left; transition: transform 0.2s ease;">
                        <div class="loading-spinner"></div>
                    </div>
                </div>
            </div>
        `;

        await this.loadAndRenderMatrix();
        this.applyZoom();
    },

    setZoom(level) {
        this.currentZoom = level;
        this.applyZoom();
    },

    applyZoom() {
        const container = document.getElementById('schedule-matrix-container');
        if (container) {
            container.style.zoom = this.currentZoom;
            if (!('zoom' in container.style)) {
                container.style.transform = `scale(${this.currentZoom})`;
            }
        }
    },

    async loadAndRenderMatrix() {
        const container = document.getElementById('schedule-matrix-container');
        try {
            const res = await fetch(`/api/schedule/matrix?cm_staff_name=${encodeURIComponent(this.selectedCm)}`);
            const json = await res.json();
            if (!json || !json.success) {
                if (container) container.innerHTML = `<div style="color: var(--accent-red); padding: 16px; text-align: center;">Không thể tải thời khóa biểu: ${json ? json.error : 'Lỗi kết nối máy chủ'}. Vui lòng thử lại.</div>`;
                return;
            }

            this.matrixData = json.matrix || [];
            this.availableCms = json.available_cms || [];

            // Populate CM Selector if empty
            const sel = document.getElementById('schedule-cm-selector');
            if (sel && sel.options.length <= 1 && this.availableCms.length > 0) {
                this.availableCms.forEach(cm => {
                    const opt = document.createElement('option');
                    opt.value = cm;
                    opt.textContent = `CM ${cm}`;
                    if (cm.toLowerCase() === this.selectedCm.toLowerCase()) opt.selected = true;
                    sel.appendChild(opt);
                });
            }

            this.renderMatrixTable();
            this.applyZoom();
        } catch (e) {
            console.error("Error loading matrix:", e);
            if (container) container.innerHTML = `<div style="color: var(--accent-red); padding: 16px; text-align: center;">Lỗi tải dữ liệu thời khóa biểu: ${e.message}</div>`;
        }
    },

    onCmSelectChange(cm) {
        this.selectedCm = cm;
        this.loadAndRenderMatrix();
    },

    /**
     * Render Bảng ma trận thời khóa biểu theo cấu trúc Thẻ Nguyên Khối Theo Ngày (Grouped Day Card System).
     */
    renderMatrixTable() {
        const container = document.getElementById('schedule-matrix-container');
        if (!container) return;

        if (this.matrixData.length === 0) {
            container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted);">Chưa có dữ liệu ma trận thời khóa biểu.</div>`;
            return;
        }

        // Group matrix rows by Day
        const daysMap = {};
        this.matrixData.forEach(row => {
            const dayCode = row.day_code || 'Mon';
            if (!daysMap[dayCode]) {
                daysMap[dayCode] = [];
            }
            daysMap[dayCode].push(row);
        });

        let fullCardsHtml = '';

        const renderShiftCells = (s) => {
            if (!s) {
                return `<td colspan="7" style="background: rgba(255,255,255,0.6); text-align: center; color: #94a3b8; font-size: 11px; padding: 8px; border-bottom: 1px solid #e9d5ff;">—</td>`;
            }

            const isCmMatch = this.selectedCm && s.cm_staff && s.cm_staff.toLowerCase().includes(this.selectedCm.toLowerCase());
            const cmBadgeStyle = isCmMatch 
                ? `background: #f59e0b; color: #ffffff; font-weight: 800; border: 1px solid #d97706; padding: 3px 8px; border-radius: 6px; font-size: 11px; box-shadow: 0 2px 6px rgba(245,158,11,0.3);`
                : `background: #ffffff; color: #1e293b; padding: 3px 8px; font-size: 11px; border-radius: 6px; border: 1px solid #cbd5e1; font-weight: 700;`;

            // Distinct badge color per level - Flat high contrast
            let pillBg = 'background: #e0e7ff; color: #3730a3; border: 1px solid #a5b4fc;';
            if (s.class_name.startsWith('Sun')) pillBg = 'background: #ffedd5; color: #c2410c; border: 1px solid #fdba74;';
            if (s.class_name.startsWith('Galax')) pillBg = 'background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe;';
            if (s.class_name.startsWith('Moon')) pillBg = 'background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc;';

            const defaultDriveUrl = (s && s.lesson_plan_url) || "https://drive.google.com/drive/folders/1JBDNHJLPorVjqbEHfHJgObhP9wsEejTz?usp=sharing";
            const isPinned = !!s.is_pinned;
            const lessonBtnLabel = s.current_buoi ? (isPinned ? `📌 Lesson ${s.current_buoi}` : `Lesson ${s.current_buoi}`) : 'Syllabus';
            const cleanUnit = (s.current_unit || '').replace(/\s+/g, ' ').trim();
            const lessonTooltip = s.current_buoi 
                ? `Lesson ${s.current_buoi}/${s.total_lessons || 72}${cleanUnit ? ' - ' + cleanUnit : ''}${isPinned ? ' (Đang ghim thủ công)' : ''}` 
                : 'Bấm để xem chi tiết bài học giáo án';

            return `
                <td style="padding: 7px 8px; border-bottom: 1px solid #e9d5ff; vertical-align: middle;">
                    <span class="badge" style="${pillBg} font-weight: 900; font-size: 12px; padding: 4px 8px; border-radius: 6px;">${s.class_name}</span>
                </td>
                <td style="font-size: 11px; padding: 7px 8px; border-bottom: 1px solid #e9d5ff; max-width: 160px; vertical-align: middle;" title="${lessonTooltip}">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <button class="btn btn-sm" onclick="ScheduleModule.openLessonLogModal('${s.class_name}');" style="padding: 3px 8px; font-size: 11px; background: ${isPinned ? '#fef3c7' : '#ffffff'}; border: 1.5px solid ${isPinned ? '#f59e0b' : '#c084fc'}; color: ${isPinned ? '#b45309' : '#6b21a8'}; font-weight: 800; border-radius: 6px; display: flex; align-items: center; gap: 4px; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.05);" title="${lessonTooltip}">
                            ${isPinned ? '📌' : '📖'} <span style="white-space: nowrap; font-weight: 800;">${lessonBtnLabel}</span>
                        </button>
                        <a href="${defaultDriveUrl}" target="_blank" rel="noopener noreferrer" style="color: #0284c7; text-decoration: none; font-size: 14px; padding: 2px 4px;" title="Mở thư mục Giáo án TEMPLATE trên Google Drive">
                            📂
                        </a>
                    </div>
                </td>
                <td style="padding: 7px 8px; border-bottom: 1px solid #e9d5ff; vertical-align: middle;"><span class="badge" style="background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; font-size: 11.5px; font-weight: 800; padding: 3px 7px; border-radius: 6px;">${s.room || '—'}</span></td>
                <td style="font-size: 12px; padding: 7px 8px; border-bottom: 1px solid #e9d5ff; font-weight: 800; color: #0f172a; max-width: 100px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; vertical-align: middle;" title="${s.teacher || ''}">${s.teacher || '—'}</td>
                <td style="text-align: center; font-size: 13px; padding: 7px 8px; border-bottom: 1px solid #e9d5ff; font-weight: 900; color: #dc2626; vertical-align: middle;">${s.students_count}</td>
                <td style="padding: 7px 8px; border-bottom: 1px solid #e9d5ff; vertical-align: middle;"><span class="badge" style="${cmBadgeStyle}">${s.cm_staff || '—'}</span></td>
                <td style="font-size: 11.5px; padding: 7px 8px; border-bottom: 1px solid #e9d5ff; font-weight: 700; color: #475569; vertical-align: middle;">${s.ta_staff || '—'}</td>
            `;
        };

        // Render each Day Card
        Object.keys(daysMap).forEach(dayCode => {
            const dayRows = daysMap[dayCode];

            let dayTableRowsHtml = '';
            dayRows.forEach(row => {
                const m5 = row.mt5;
                const m6 = row.mt6;
                dayTableRowsHtml += `
                    <tr style="transition: background 0.15s ease;" onmouseenter="this.style.background='#fff0f3';" onmouseleave="this.style.background='transparent';">
                        ${renderShiftCells(m5)}
                        <td style="border-right: 3px solid #cbd5e1; width: 0; padding: 0;"></td>
                        ${renderShiftCells(m6)}
                    </tr>
                `;
            });

            fullCardsHtml += `
                <!-- UNIFIED DAY CARD CONTAINER -->
                <div style="display: flex; margin-bottom: 22px; border-radius: 16px; box-shadow: 0 10px 30px rgba(147, 51, 234, 0.09); border: 2px solid #e9d5ff; background: #faf5ff; overflow: hidden;">
                    
                    <!-- Cột THỨ (Sidebar bên trái): Dải màu cam/hồng tươi sáng, chữ tên Thứ MÀU ĐEN 100%, nổi & đổ bóng nguyên khối -->
                    <div style="width: 85px; min-width: 85px; background: linear-gradient(180deg, #ff7e5f 0%, #ff6b6b 100%); display: flex; align-items: center; justify-content: center; border-right: 2px solid #ea580c; box-shadow: 4px 0 14px rgba(255, 112, 126, 0.35); flex-shrink: 0;">
                        <span style="font-size: 18px; font-weight: 900; color: #000000; letter-spacing: 0.5px; text-transform: uppercase; text-shadow: 0 1px 0 rgba(255,255,255,0.4);">
                            ${dayCode}
                        </span>
                    </div>

                    <!-- Khu vực NỘI DUNG DẠY (Khối Nền To Duy Nhất Tím Nhạt Lavender dịu mắt) -->
                    <div style="flex: 1; overflow-x: auto; background: #faf5ff; padding: 4px 12px 12px 12px;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 12px; min-width: 780px;">
                            <thead>
                                <!-- Row 1: Shift Block Headers -->
                                <tr>
                                    <th colspan="7" style="background: #ff7e5f; color: #ffffff; font-size: 13px; text-align: center; font-weight: 900; padding: 8px; border-radius: 8px 8px 0 0;">
                                        🟧 CA 1: MT5 (17:30 - 19:00)
                                    </th>
                                    <th style="width: 3px; padding: 0; background: #cbd5e1;"></th>
                                    <th colspan="7" style="background: #10b981; color: #ffffff; font-size: 13px; text-align: center; font-weight: 900; padding: 8px; border-radius: 8px 8px 0 0;">
                                        🟩 CA 2: MT6 (19:15 - 20:45)
                                    </th>
                                </tr>
                                <!-- Row 2: Sub Columns -->
                                <tr style="background: #f1f5f9; border-bottom: 2px solid #e9d5ff;">
                                    <th style="min-width: 80px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">CLASSES</th>
                                    <th style="min-width: 95px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">MATERIALS</th>
                                    <th style="min-width: 60px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">ROOMS</th>
                                    <th style="min-width: 85px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">TEACHERS</th>
                                    <th style="min-width: 42px; padding: 6px; text-align: center; color: #1e293b; font-weight: 800;">NO.STU</th>
                                    <th style="min-width: 70px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">CM</th>
                                    <th style="min-width: 50px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">TA</th>

                                    <th style="width: 3px; padding: 0; background: #cbd5e1;"></th>

                                    <th style="min-width: 80px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">CLASSES</th>
                                    <th style="min-width: 95px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">MATERIALS</th>
                                    <th style="min-width: 60px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">ROOMS</th>
                                    <th style="min-width: 85px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">TEACHERS</th>
                                    <th style="min-width: 42px; padding: 6px; text-align: center; color: #1e293b; font-weight: 800;">NO.STU</th>
                                    <th style="min-width: 70px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">CM</th>
                                    <th style="min-width: 50px; padding: 6px 8px; color: #1e293b; font-weight: 800; text-align: left;">TA</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${dayTableRowsHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        });

        container.innerHTML = fullCardsHtml;
    },

    /**
     * Open Pop-up Theo dõi nhật ký bài học theo buổi của 1 lớp học (Right side in mockup).
     */
    async openLessonLogModal(className) {
        const modal = document.getElementById('modal-backdrop');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');

        if (!modal || !modalBody) return;

        modal.style.display = 'flex';
        modalTitle.innerHTML = `📋 POP-UP THEO DÕI NỘI DUNG BÀI HỌC VÀ NHẬT KÝ LỚP`;
        modalBody.innerHTML = `<div class="loading-spinner"></div>`;
        modal.classList.add('active');

        const modalContainer = modal.querySelector('.modal-container');
        if (modalContainer) {
            modalContainer.classList.add('modal-xl');
            modalContainer.style.maxWidth = '1320px';
            modalContainer.style.width = '96vw';
        }

        try {
            const res = await fetch(`/api/schedule/class-detail?class_name=${encodeURIComponent(className)}`);
            const json = await res.json();
            if (!json.success) {
                modalBody.innerHTML = `<div style="color: var(--accent-red); padding: 20px;">Lỗi: ${json.error}</div>`;
                return;
            }

            const { class_name, materials, room, teacher, cm_staff, lessons, lesson_plan_url, total_lessons, detected_course, pinned_lesson_num } = json;
            const driveUrl = lesson_plan_url || "https://drive.google.com/drive/folders/1JBDNHJLPorVjqbEHfHJgObhP9wsEejTz?usp=sharing";

            // Save class name & lessons in module memory for preview modal
            this.currentClassName = className;
            this.currentLessonsList = lessons;
            this.currentPinnedLesson = pinned_lesson_num;

            // Find focus lesson index: Pinned > Today > Last Completed > First lesson
            let targetIndex = -1;
            let targetReason = '';

            if (pinned_lesson_num) {
                targetIndex = lessons.findIndex(l => l.buoi === pinned_lesson_num);
                if (targetIndex !== -1) {
                    targetReason = 'Đã ghim bài học hiện tại';
                }
            }

            if (targetIndex === -1) {
                // Search for Today lesson
                targetIndex = lessons.findIndex(l => l.status_code === 'today');
                if (targetIndex !== -1) {
                    targetReason = 'Hôm nay';
                } else {
                    // Find most recently completed lesson
                    for (let i = lessons.length - 1; i >= 0; i--) {
                        if (lessons[i].status_code === 'completed') {
                            targetIndex = i;
                            targetReason = 'Ngày học kết thúc gần nhất';
                            break;
                        }
                    }
                }
            }

            if (targetIndex === -1) {
                targetIndex = 0;
                targetReason = 'Bài học mới nhất';
            }

            this.currentTargetIndex = targetIndex;
            const targetLesson = lessons[targetIndex];

            let rowsHtml = lessons.map((l, index) => {
                let statusBadge = 'badge-secondary';
                if (l.status_code === 'completed') statusBadge = 'badge-success';
                if (l.status_code === 'today') statusBadge = 'badge-warning';
                if (l.status_code === 'pending') statusBadge = 'badge-info';

                const isTarget = (index === targetIndex);
                const isPinnedThis = l.is_pinned || (pinned_lesson_num === l.buoi);

                return `
                    <tr id="lesson-row-${index}" data-target-scroll="${isTarget ? 'true' : ''}" style="${isTarget ? (isPinnedThis ? 'background: rgba(245, 158, 11, 0.15); font-weight: 700; border: 2px solid #f59e0b;' : 'background: rgba(255, 126, 95, 0.15); font-weight: 700; border: 2px solid #ff7e5f;') : ''}">
                        <td style="text-align: center; font-weight: 800; font-size: 13px; vertical-align: top; padding-top: 10px;">
                            ${isPinnedThis ? '📌 ' : (l.status_code === 'completed' ? '🟢 ' : (l.status_code === 'today' ? '👉 ' : '⚪ '))}${l.buoi}
                            ${isTarget ? `<br><small style="color: ${isPinnedThis ? '#b45309' : '#ff7e5f'}; font-size: 10px; font-weight: 800;">📍(${targetReason})</small>` : ''}
                        </td>
                        <td style="font-weight: 700; color: #4338ca; font-size: 12px; vertical-align: top; padding-top: 10px;">${l.date}</td>
                        <td style="font-size: 12.5px; padding: 10px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <strong style="color: #4f46e5; font-size: 14px;">${AuthModule.escapeHtml(l.lesson_title || ('LESSON ' + l.buoi))}</strong>
                                <span class="badge badge-info" style="font-size: 11px;">${AuthModule.escapeHtml(l.unit_name || '')} ${l.pages ? '(Trang ' + l.pages + ')' : ''}</span>
                            </div>

                            <div style="background: #ffffff; padding: 10px 12px; border-radius: 8px; border: 1.5px solid #cbd5e1; border-left: 4px solid ${isPinnedThis ? '#f59e0b' : '#ff7e5f'}; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                                <div style="color: #0f172a; font-size: 12px; margin-bottom: 6px; line-height: 1.4;">
                                    <strong style="color: #0284c7; display: block; margin-bottom: 2px;">📚 Vocabulary (Từ vựng):</strong>
                                    ${AuthModule.escapeHtml(l.vocabulary || '—').replace(/\n/g, '<br>')}
                                </div>

                                <div style="color: #0f172a; font-size: 12px; margin-bottom: 6px; line-height: 1.4;">
                                    <strong style="color: #059669; display: block; margin-bottom: 2px;">💬 Grammar & Structures (Cấu trúc câu):</strong>
                                    ${AuthModule.escapeHtml(l.grammar || '—').replace(/\n/g, '<br>')}
                                </div>

                                ${l.lesson_target ? `
                                    <div style="color: #475569; font-size: 11.5px; font-style: italic; border-top: 1px dashed #cbd5e1; padding-top: 4px; margin-top: 4px;">
                                        🎯 Target: ${AuthModule.escapeHtml(l.lesson_target)}
                                    </div>
                                ` : ''}
                            </div>
                        </td>
                        <td style="vertical-align: top; padding-top: 10px; width: 225px; min-width: 220px;">
                            <span class="badge ${statusBadge}" style="font-weight: 700;">${l.status_label}</span>
                            <div style="margin-top: 8px; display: flex; gap: 4px; flex-wrap: wrap;">
                                <button class="btn btn-sm" onclick="ScheduleModule.showReportCardModal(${index});" style="padding: 4px 8px; font-size: 11px; background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; border-radius: 6px; font-weight: 700; cursor: pointer;" title="Xem thẻ báo cáo bài học mẫu EVI">
                                    📄 Báo Cáo
                                </button>
                                <button class="btn btn-sm" onclick="ScheduleModule.toggleLessonDelay('${AuthModule.escapeHtml(class_name)}', ${l.buoi});" style="padding: 4px 8px; font-size: 11px; background: ${l.is_delayed ? '#ffe4e6' : '#fef3c7'}; color: ${l.is_delayed ? '#be123c' : '#b45309'}; border: 1px solid ${l.is_delayed ? '#f43f5e' : '#f59e0b'}; border-radius: 6px; font-weight: 700; cursor: pointer;" title="${l.is_delayed ? 'Hủy lùi lịch cho buổi này' : 'Bấm lùi ngày học của buổi này sang buổi kế tiếp nếu bị nghỉ học/hủy buổi'}">
                                    ${l.is_delayed ? '↩️ Hủy Lùi' : '⏪ Lùi Lịch'}
                                </button>
                                <button class="btn btn-sm" onclick="ScheduleModule.advanceLessonProgress('${AuthModule.escapeHtml(class_name)}', ${l.buoi});" style="padding: 4px 8px; font-size: 11px; background: #e0e7ff; color: #4338ca; border: 1px solid #a5b4fc; border-radius: 6px; font-weight: 700; cursor: pointer;" title="Bấm để nhảy bài (đẩy ngày học của bài này và các bài sau lên sớm 1 buổi nếu học nhanh hơn hoặc bỏ qua bài trước)">
                                    ⏩ Nhảy Bài
                                </button>
                            </div>
                        </td>
                        <td style="font-size: 12px; color: #334155; vertical-align: top; padding-top: 10px; font-weight: 600; width: 220px; min-width: 200px;">${l.homework_note}</td>
                    </tr>
                `;
            }).join('');

            modalBody.innerHTML = `
                <div style="padding: 6px;">
                    <!-- Class Header Box -->
                    <div style="background: #ffffff; border: 2px solid #cbd5e1; border-radius: 12px; padding: 16px; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
                            <div>
                                <h2 style="margin: 0; font-size: 19px; color: #1e293b; font-weight: 900;">
                                    LỚP: ${class_name.toUpperCase()} | Giáo trình: ${detected_course || materials}
                                </h2>
                                <div style="font-size: 12px; color: #64748b; margin-top: 2px;">Vị trí lớp: ${materials}</div>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <span class="badge" style="background: #f3e8ff; color: #6b21a8; font-size: 12px; font-weight: 800;">Phòng ${room}</span>
                                <a href="${driveUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="background: #0284c7; color: #fff; text-decoration: none; padding: 5px 12px; font-size: 12px; font-weight: 800; border-radius: 6px; display: inline-flex; align-items: center; gap: 5px; box-shadow: 0 2px 8px rgba(2,132,199,0.3);">
                                    📂 Mở Folder Giáo Án (Drive TEMPLATE)
                                </a>
                            </div>
                        </div>
                        <div style="font-size: 13px; color: #334155; display: flex; gap: 18px; flex-wrap: wrap; font-weight: 600;">
                            <span>👨‍🏫 Giáo viên: <strong style="color: #059669;">${teacher}</strong></span>
                            <span>👩‍💼 CM Phụ trách: <strong style="color: #d97706;">CM ${cm_staff}</strong></span>
                            <span>📋 Tổng số bài học: <strong style="color: #7e22ce;">${total_lessons || lessons.length} bài (100% CSDL)</strong></span>
                        </div>
                    </div>

                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <span>📝 CHI TIẾT NỘI DUNG BÀI HỌC (SYLLABUS)</span>
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <span id="target-location-badge" style="background: ${pinned_lesson_num ? '#fef3c7' : '#ffedd5'}; color: ${pinned_lesson_num ? '#b45309' : '#c2410c'}; border: 1px solid ${pinned_lesson_num ? '#f59e0b' : '#fdba74'}; font-size: 12px; font-weight: 800; padding: 3px 10px; border-radius: 20px; box-shadow: 0 2px 6px rgba(255, 126, 95, 0.2);">
                                ${pinned_lesson_num ? '📌 Đã ghim bài học:' : '📍 Tự động định vị:'} Buổi ${targetLesson ? targetLesson.buoi : ''} (${targetReason})
                            </span>
                            ${pinned_lesson_num ? `
                                <button class="btn btn-sm" onclick="ScheduleModule.jumpToLessonProgress('${AuthModule.escapeHtml(class_name)}', 0);" style="padding: 3px 10px; font-size: 11.5px; background: #fee2e2; color: #b91c1c; border: 1px solid #f87171; border-radius: 20px; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;" title="Hủy ghim và đưa lớp về chế độ tự động tính theo ngày">
                                    🔄 Hủy Ghim (Về Tự Động)
                                </button>
                            ` : ''}
                        </div>
                    </h4>

                    <div id="lesson-log-scroll-wrapper" class="data-table-wrapper" style="max-height: 480px; overflow-y: auto; overflow-x: auto; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px;">
                        <table class="data-table" style="font-size: 12.5px; width: 100%; min-width: 980px;">
                            <thead>
                                <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1;">
                                    <th style="width: 55px; text-align: center; white-space: nowrap;">Buổi</th>
                                    <th style="width: 65px; white-space: nowrap;">Ngày</th>
                                    <th style="min-width: 360px;">Chi Tiết Bài Học (Unit, Từ vựng, Cấu trúc, Target)</th>
                                    <th style="width: 225px; min-width: 220px; white-space: nowrap;">Trạng Thái & Thao Tác</th>
                                    <th style="width: 220px; min-width: 200px;">Bài Tập (GV & CM)</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            setTimeout(() => {
                const targetRow = document.querySelector('[data-target-scroll="true"]');
                if (targetRow) {
                    targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 300);

        } catch (e) {
            modalBody.innerHTML = `<div style="color: var(--accent-red); padding: 20px;">Lỗi tải dữ liệu: ${e.message}</div>`;
        }
    },

    formatCleanText(text) {
        if (!text) return '—';
        const lines = String(text).split('\n');
        const cleanLines = lines.map(line => {
            let trimmed = line.trim();
            if (!trimmed) return '';
            let cleanText = trimmed.replace(/^[-+*•:]\s*/, '');
            if (!cleanText) return AuthModule.escapeHtml(line);
            return `<div style="margin-bottom: 4px; font-weight: 700; line-height: 1.4;">• ${AuthModule.escapeHtml(cleanText)}</div>`;
        });
        return cleanLines.join('');
    },


    exportReportCardPDF() {
        const cardEl = document.getElementById('report-card-canvas');
        if (!cardEl) {
            if (typeof App !== 'undefined' && App.showToast) App.showToast('Không tìm thấy thẻ báo cáo để xuất PDF.', 'error');
            return;
        }

        const lessonTitle = this.currentLessonTitle || 'Bao_Cao_Buoi_Hoc_EVI';
        const cleanFileName = lessonTitle.replace(/[^a-zA-Z0-9_\-]/g, '_') + '.pdf';

        const doExport = () => {
            const opt = {
                margin:       [4, 4, 4, 4],
                filename:     cleanFileName,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2.5, useCORS: true, logging: false },
                jsPDF:        { unit: 'mm', format: 'a5', orientation: 'landscape' }
            };
            html2pdf().set(opt).from(cardEl).save().then(() => {
                if (typeof Dashboard !== 'undefined' && Dashboard.showToast) {
                    Dashboard.showToast('✅ Đã xuất file Báo cáo PDF thành công!');
                }
            }).catch(err => {
                console.error('PDF export error:', err);
                window.print();
            });
        };

        if (typeof html2pdf !== 'undefined') {
            doExport();
        } else {
            if (typeof Dashboard !== 'undefined' && Dashboard.showToast) {
                Dashboard.showToast('⏳ Đang khởi tạo bộ xuất PDF...', 'info');
            }
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js';
            script.onload = () => {
                doExport();
            };
            script.onerror = () => {
                window.print();
            };
            document.head.appendChild(script);
        }
    },

    showReportCardModal(index) {
        if (!this.currentLessonsList || !this.currentLessonsList[index]) return;
        const lesson = this.currentLessonsList[index];
        const targetClassName = this.currentClassName || (this.currentLessonsList[0] ? this.currentLessonsList[0].class_name : '');
        this.currentLessonTitle = lesson.lesson_title || ('LESSON_' + lesson.buoi);

        if (typeof Dashboard !== 'undefined' && Dashboard.pushModalState) {
            Dashboard.pushModalState(() => {
                if (targetClassName) {
                    ScheduleModule.openLessonLogModal(targetClassName);
                }
            });
        }

        const unitClean = AuthModule.escapeHtml(lesson.unit_name || 'UNIT');
        const vocabHtml = this.formatCleanText(lesson.vocabulary);
        const grammarHtml = lesson.grammar ? this.formatCleanText(lesson.grammar) : '';
        const hwClean = AuthModule.escapeHtml(lesson.homework_note || 'Ôn tập từ vựng & cấu trúc bài học');

        const cardHtml = `
            <div style="display: flex; flex-direction: column; align-items: center; gap: 12px; max-width: 600px; margin: 0 auto;">
                
                <!-- 🖼️ CLEAN SIMPLE MINIMALIST EVI REPORT CARD CANVAS FOR 100% CLEAR DISPLAY & SCREENSHOTS -->
                <div id="report-card-canvas" style="position: relative; background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 20px 24px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.06); color: #0f172a;">
                    
                    <!-- Header Logo & Clean Title -->
                    <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 2px solid #2563eb;">
                        <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 44px; height: 44px; object-fit: contain;">
                        <div>
                            <div style="font-size: 18px; font-weight: 900; color: #0432ff; letter-spacing: 0.5px; text-transform: uppercase; line-height: 1.2;">
                                TRUNG TÂM ANH NGỮ VICARE
                            </div>
                            <h2 style="margin: 3px 0 0 0; font-size: 14px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px;">
                                BÁO CÁO NỘI DUNG BUỔI HỌC: <span style="color: #2563eb;">${AuthModule.escapeHtml(lesson.lesson_title || ('LESSON ' + lesson.buoi))}</span>
                            </h2>
                        </div>
                    </div>

                    <!-- Clean Data Table Grid -->
                    <div style="border: 1.5px solid #e2e8f0; border-radius: 8px; overflow: hidden; background: #ffffff;">
                        
                        <!-- Row 1: Units -->
                        <div style="display: flex; border-bottom: 1px solid #e2e8f0;">
                            <div style="width: 130px; min-width: 130px; padding: 10px 14px; background: #f8fafc; font-weight: 800; font-size: 12.5px; border-right: 1px solid #e2e8f0; color: #0f172a; display: flex; flex-direction: column; justify-content: center;">
                                <div>Units</div>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b;">(Bài học)</div>
                            </div>
                            <div style="flex: 1; padding: 10px 14px; font-weight: 700; font-size: 13px; color: #0f172a; background: #ffffff; display: flex; align-items: center;">
                                : ${unitClean} ${lesson.pages ? (' (Trang ' + AuthModule.escapeHtml(lesson.pages) + ')') : ''}
                            </div>
                        </div>

                        <!-- Row 2: Vocabulary -->
                        <div style="display: flex; border-bottom: 1px solid #e2e8f0;">
                            <div style="width: 130px; min-width: 130px; padding: 10px 14px; background: #f8fafc; font-weight: 800; font-size: 12.5px; border-right: 1px solid #e2e8f0; color: #0f172a; display: flex; flex-direction: column; justify-content: center;">
                                <div>Vocabulary</div>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b;">(Từ vựng)</div>
                            </div>
                            <div style="flex: 1; padding: 10px 14px; font-size: 12.5px; font-weight: 600; color: #0f172a; line-height: 1.5; background: #ffffff;">
                                ${vocabHtml}
                            </div>
                        </div>

                        ${lesson.grammar ? `
                        <!-- Row 3: Structures -->
                        <div style="display: flex; border-bottom: 1px solid #e2e8f0;">
                            <div style="width: 130px; min-width: 130px; padding: 10px 14px; background: #f8fafc; font-weight: 800; font-size: 12.5px; border-right: 1px solid #e2e8f0; color: #0f172a; display: flex; flex-direction: column; justify-content: center;">
                                <div>Cấu trúc câu</div>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b;">(Structures)</div>
                            </div>
                            <div style="flex: 1; padding: 10px 14px; font-size: 12.5px; font-weight: 600; color: #0f172a; line-height: 1.5; background: #ffffff;">
                                ${grammarHtml}
                            </div>
                        </div>
                        ` : ''}

                        <!-- Row 4: BTVN -->
                        <div style="display: flex;">
                            <div style="width: 130px; min-width: 130px; padding: 10px 14px; background: #f8fafc; font-weight: 800; font-size: 12.5px; border-right: 1px solid #e2e8f0; color: #0f172a; display: flex; flex-direction: column; justify-content: center;">
                                <div>BTVN</div>
                                <div style="font-size: 11px; font-weight: 600; color: #64748b;">(Homework)</div>
                            </div>
                            <div style="flex: 1; padding: 10px 14px; font-size: 12.5px; font-weight: 700; color: #0f172a; line-height: 1.5; background: #ffffff;">
                                : ${hwClean}
                            </div>
                        </div>
                    </div>

                    <!-- Watermark Footer -->
                    <div style="margin-top: 14px; border-top: 1.5px dashed #cbd5e1; padding-top: 10px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #64748b;">
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <img src="/static/images/logo.jpg" style="width: 14px; height: 14px; object-fit: contain;">
                            <strong>Trung tâm Anh ngữ Vicare</strong>
                        </div>
                        <div>✨ Thiết kế bởi: <strong style="color: #0284c7; font-weight: 800;">Nhi Phương</strong></div>
                    </div>
                </div>

                <!-- Clean Action Bar -->
                <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 6px; width: 100%;">
                    <button class="btn btn-sm" onclick="ScheduleModule.exportReportCardPDF();" style="padding: 8px 24px; background: #2563eb; color: #ffffff; border-radius: 8px; font-weight: 800; border: none; box-shadow: 0 2px 8px rgba(37,99,235,0.25); cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                        📄 Xuất Báo Cáo PDF
                    </button>
                    <button class="btn btn-sm" onclick="Dashboard.closeModal();" style="padding: 8px 24px; background: #475569; color: #ffffff; border-radius: 8px; font-weight: 800; border: none; box-shadow: 0 2px 8px rgba(71,85,105,0.2); cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                        ✕ Đóng Preview
                    </button>
                </div>
            </div>
        `;

        const modal = document.getElementById('modal-backdrop');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');

        if (modal && modalBody) {
            modalTitle.innerHTML = `📄 THẺ BÁO CÁO NỘI DUNG BUỔI HỌC - ANH NGỮ VICARE`;
            modalBody.innerHTML = cardHtml;
            modalBody.style.padding = '10px 14px';
        }
    },

    /**
     * Bật/Tắt Lùi lịch cho 1 buổi học cụ thể của lớp
     */
    async toggleLessonDelay(className, buoi) {
        if (!confirm(`Bạn có chắc chắn muốn lùi ngày học của Lớp ${className} từ Buổi ${buoi} trở đi sang buổi học kế tiếp không?`)) {
            return;
        }
        try {
            const res = await API.post('/schedule/delay-lesson', { class_name: className, lesson_num: buoi });

            if (res && res.success) {
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast('✅ Đã cập nhật điều chỉnh lùi lịch học thành công!', 'success');
                } else {
                    alert('✅ Đã cập nhật điều chỉnh lùi lịch học thành công!');
                }
                // Re-open modal with updated log
                await this.openLessonLogModal(className);

                // Refresh all active timetable views (Dashboard & Schedule page)
                this.refreshActiveScheduleViews();
            } else {
                alert('Lỗi lùi lịch: ' + (res.error || res.message || 'Không thể cập nhật'));
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        }
    },

    /**
     * Nhảy Bài (Đẩy sớm tiến độ bài học lên 1 buổi thực tế)
     */
    async advanceLessonProgress(className, buoi) {
        if (!confirm(`Bạn có chắc chắn muốn nhảy bài, đẩy Buổi ${buoi} và toàn bộ các buổi tiếp theo của Lớp ${className} lên sớm 1 buổi học trong lịch thực tế không?`)) {
            return;
        }
        try {
            const res = await API.post('/schedule/advance-lesson', { class_name: className, lesson_num: buoi });

            if (res && res.success) {
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast(`✅ Đã nhảy bài, đẩy tiến độ Buổi ${buoi} lên sớm 1 buổi thành công!`, 'success');
                } else {
                    alert(`✅ Đã nhảy bài, đẩy tiến độ Buổi ${buoi} lên sớm 1 buổi thành công!`);
                }
                // Re-open modal with updated log
                await this.openLessonLogModal(className);

                // Refresh all active timetable views (Dashboard & Schedule page)
                this.refreshActiveScheduleViews();
            } else {
                alert('Lỗi nhảy bài: ' + (res.error || res.message || 'Không thể cập nhật'));
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        }
    },

    /**
     * Tự động làm mới toàn bộ các bảng Thời khóa biểu đang hiển thị (cả trang Dashboard và trang Thời khóa biểu)
     */
    refreshActiveScheduleViews() {
        // 1. If on full Schedule page:
        const scheduleContainer = document.getElementById('schedule');
        if (scheduleContainer && typeof this.renderPage === 'function') {
            this.renderPage(scheduleContainer);
        }

        // 2. If on Dashboard page:
        const dashboardSchedContainer = document.getElementById('cm-dashboard-schedule-container');
        if (dashboardSchedContainer && typeof this.renderCmDashboardSchedule === 'function') {
            const user = (typeof Auth !== 'undefined') ? Auth.getUser() : null;
            const cmName = this.selectedCm || (user && user.role === 'cm' ? (user.cm_staff_name || user.full_name) : (user && user.cm_staff_name ? user.cm_staff_name : 'AnhNV'));
            this.renderCmDashboardSchedule(dashboardSchedContainer, cmName);
        }
    },

    /**
     * Render CM Dashboard Widget (Gọn gàng siêu nhỏ, thu phóng 85%, giới hạn chiều cao 280px)
     */
    async renderCmDashboardSchedule(container, cmName) {
        if (!container) return;
        this.selectedCm = cmName || '';
        this.currentZoom = 0.85; // Thu nhỏ 85% trên Dashboard cho vừa vặn
        await this.renderPage(container);

        // Giới hạn max-height trên Dashboard và thêm cuộn dọc
        const wrapper = document.getElementById('schedule-matrix-wrapper');
        if (wrapper) {
            wrapper.style.maxHeight = '280px';
            wrapper.style.overflowY = 'auto';
        }
    },

    /**
     * Mở Modal Quản Lý Lịch Nghỉ Lễ & Lùi Lịch
     */
    async openHolidayManagerModal() {
        const modal = document.getElementById('holiday-modal');
        const modalBody = document.getElementById('holiday-modal-body');
        if (!modal || !modalBody) return;

        modal.classList.add('active');
        this.renderHolidayModalContent('declare');
    },

    closeHolidayModal() {
        const modal = document.getElementById('holiday-modal');
        if (modal) modal.classList.remove('active');
    },

    activeHolidayTab: 'declare',

    async renderHolidayModalContent(tabName = 'declare') {
        this.activeHolidayTab = tabName;
        const modalBody = document.getElementById('holiday-modal-body');
        if (!modalBody) return;

        modalBody.innerHTML = `
            <!-- Modal Tabs Header -->
            <div style="display: flex; gap: 10px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; padding-bottom: 10px;">
                <button class="btn" style="padding: 8px 16px; font-weight: 800; border-radius: 8px; font-size: 13px; background: ${tabName === 'declare' ? '#4f46e5' : '#e2e8f0'}; color: ${tabName === 'declare' ? '#fff' : '#475569'}; border: none; cursor: pointer;" onclick="ScheduleModule.renderHolidayModalContent('declare');">
                    🌴 Khai Báo Đợt Nghỉ Mới
                </button>
                <button class="btn" style="padding: 8px 16px; font-weight: 800; border-radius: 8px; font-size: 13px; background: ${tabName === 'history' ? '#4f46e5' : '#e2e8f0'}; color: ${tabName === 'history' ? '#fff' : '#475569'}; border: none; cursor: pointer;" onclick="ScheduleModule.renderHolidayModalContent('history');">
                    📜 Lịch Sử Lùi Lịch & Khôi Phục
                </button>
            </div>

            <div id="holiday-tab-container">
                <div style="text-align: center; padding: 30px; color: #64748b;">Đang tải dữ liệu...</div>
            </div>
        `;

        if (tabName === 'declare') {
            this.renderHolidayDeclareForm();
        } else {
            await this.renderHolidayHistoryTable();
        }
    },

    renderHolidayDeclareForm() {
        const container = document.getElementById('holiday-tab-container');
        if (!container) return;

        const todayStr = new Date().toISOString().split('T')[0];

        // Build dynamic options list for active classes
        let classOptionsHtml = '<option value="ALL">🏢 Toàn Trung Tâm (Tất cả các lớp)</option>';
        let classNames = [];
        if (this.scheduleData && this.scheduleData.data) {
            const classSet = new Set();
            this.scheduleData.data.forEach(row => {
                ['mt5', 'mt6', 'tf5', 'tf6', 'ws5', 'ws6'].forEach(shift => {
                    const cInfo = row[shift];
                    if (cInfo && cInfo.class_name) {
                        classSet.add(cInfo.class_name.trim());
                    }
                });
            });
            classNames = Array.from(classSet).sort();
        }
        if (classNames.length > 0) {
            classNames.forEach(c => {
                classOptionsHtml += `<option value="${AuthModule.escapeHtml(c)}">🏫 Lớp ${AuthModule.escapeHtml(c)}</option>`;
            });
        }

        container.innerHTML = `
            <div style="background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 16px;">
                    <div>
                        <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 6px;">Tên Dịp / Lý Do Nghỉ <span style="color: #ef4444;">*</span></label>
                        <input type="text" id="holiday-title" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" placeholder="Ví dụ: Nghỉ lễ Quốc Khánh 2/9, Nghỉ bão Yagi..." />
                    </div>

                    <div>
                        <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 6px;">Loại Nghỉ</label>
                        <select id="holiday-type" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;">
                            <option value="Nghỉ lễ cố định">🌴 Nghỉ lễ cố định (Tết, 2/9, 30/4...)</option>
                            <option value="Nghỉ đột xuất">⚡ Nghỉ đột xuất (Bão lũ, sự cố...)</option>
                            <option value="Lùi lịch riêng">✏️ Điều chỉnh lùi lịch riêng</option>
                        </select>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 16px;">
                    <div>
                        <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 6px;">Từ Ngày <span style="color: #ef4444;">*</span></label>
                        <input type="date" id="holiday-start-date" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" value="${todayStr}" />
                    </div>

                    <div>
                        <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 6px;">Đến Ngày <span style="color: #ef4444;">*</span></label>
                        <input type="date" id="holiday-end-date" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" value="${todayStr}" />
                    </div>

                    <div>
                        <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 6px;">Phạm Vi Áp Dụng</label>
                        <select id="holiday-scope" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;">
                            ${classOptionsHtml}
                        </select>
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 800; font-size: 13px; color: #1e293b; margin-bottom: 6px;">Ghi Chú Chi Tiết</label>
                    <input type="text" id="holiday-note" class="form-control" style="width: 100%; padding: 8px 12px; font-size: 13px; border-radius: 8px; border: 1.5px solid #cbd5e1;" placeholder="Nhập bổ sung thông tin hoặc lý do nếu cần..." />
                </div>

                <div style="display: flex; gap: 12px; align-items: center;">
                    <button class="btn" style="padding: 10px 20px; font-weight: 800; background: #0284c7; color: #fff; border: none; border-radius: 8px; font-size: 13.5px; cursor: pointer; display: flex; align-items: center; gap: 6px;" onclick="ScheduleModule.previewHolidayShift();">
                        🔍 Xem Trước Tác Động
                    </button>
                    <button class="btn" style="padding: 10px 24px; font-weight: 800; background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; border-radius: 8px; font-size: 13.5px; cursor: pointer; display: flex; align-items: center; gap: 6px;" onclick="ScheduleModule.submitHolidayShift();">
                        🚀 Áp Dụng Lùi Lịch
                    </button>
                </div>
            </div>

            <!-- Preview Results Area -->
            <div id="holiday-preview-container" style="margin-top: 20px; display: none;"></div>
        `;
    },

    async previewHolidayShift() {
        const title = document.getElementById('holiday-title')?.value || '';
        const start_date = document.getElementById('holiday-start-date')?.value || '';
        const end_date = document.getElementById('holiday-end-date')?.value || '';
        const scope = document.getElementById('holiday-scope')?.value || 'ALL';
        const previewBox = document.getElementById('holiday-preview-container');

        if (!start_date || !end_date) {
            alert('Vui lòng chọn Từ Ngày và Đến Ngày!');
            return;
        }

        if (previewBox) {
            previewBox.style.display = 'block';
            previewBox.innerHTML = `<div style="text-align: center; padding: 20px; color: #0284c7; font-weight: 700;">⏳ Đang tính toán xem trước tác động...</div>`;
        }

        try {
            const res = await API.post('/schedule/holiday-shift/preview', {
                start_date: start_date,
                end_date: end_date,
                affected_classes: [scope]
            });

            if (res && res.success) {
                let sampleHtml = (res.sample_students || []).map(st => `
                    <tr>
                        <td style="padding: 6px 10px; font-weight: 700; border-bottom: 1px solid #f1f5f9;">${st.code}</td>
                        <td style="padding: 6px 10px; border-bottom: 1px solid #f1f5f9;">${st.name}</td>
                        <td style="padding: 6px 10px; border-bottom: 1px solid #f1f5f9;">${st.class_name}</td>
                        <td style="padding: 6px 10px; border-bottom: 1px solid #f1f5f9; color: #64748b;">${st.old_expiry_date || 'N/A'}</td>
                        <td style="padding: 6px 10px; border-bottom: 1px solid #f1f5f9; color: #059669; font-weight: 800;">${st.new_expiry_date || 'N/A'}</td>
                    </tr>
                `).join('');

                previewBox.innerHTML = `
                    <div style="background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 12px; padding: 18px;">
                        <h4 style="margin: 0 0 12px 0; color: #166534; font-size: 15px; font-weight: 900; display: flex; align-items: center; gap: 6px;">
                            📊 THỐNG KÊ XEM TRƯỚC TÁC ĐỘNG (${res.holiday_days} ngày nghỉ)
                        </h4>
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 16px;">
                            <div style="background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #dcfce7; text-align: center;">
                                <div style="font-size: 11px; font-weight: 700; color: #15803d; text-transform: uppercase;">Số Lớp Ảnh Hưởng</div>
                                <div style="font-size: 20px; font-weight: 900; color: #166534; margin-top: 4px;">${res.total_classes_affected} lớp</div>
                            </div>
                            <div style="background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #dcfce7; text-align: center;">
                                <div style="font-size: 11px; font-weight: 700; color: #15803d; text-transform: uppercase;">Số Ca Học Bị Hoãn</div>
                                <div style="font-size: 20px; font-weight: 900; color: #2563eb; margin-top: 4px;">${res.total_lessons_affected} ca</div>
                            </div>
                            <div style="background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #dcfce7; text-align: center;">
                                <div style="font-size: 11px; font-weight: 700; color: #15803d; text-transform: uppercase;">Số HS Tự Động Gia Hạn</div>
                                <div style="font-size: 20px; font-weight: 900; color: #7c3aed; margin-top: 4px;">${res.total_students_affected} học sinh</div>
                            </div>
                        </div>

                        <div style="font-size: 13px; font-weight: 800; color: #166534; margin-bottom: 8px;">Mẫu Học Sinh Được Tự Động Dời Ngày Hết Phí (Expiry Date +${res.holiday_days} ngày):</div>
                        <div style="max-height: 180px; overflow-y: auto; background: #ffffff; border-radius: 8px; border: 1px solid #dcfce7;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                                <thead>
                                    <tr style="background: #dcfce7; color: #166534; text-align: left; position: sticky; top: 0;">
                                        <th style="padding: 6px 10px;">Mã HS</th>
                                        <th style="padding: 6px 10px;">Họ Tên</th>
                                        <th style="padding: 6px 10px;">Lớp</th>
                                        <th style="padding: 6px 10px;">Hạn Cũ</th>
                                        <th style="padding: 6px 10px;">Hạn Mới</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${sampleHtml || '<tr><td colspan="5" style="padding: 10px; text-align: center; color: #64748b;">Không có mẫu học sinh</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            } else {
                previewBox.innerHTML = `<div style="color: #ef4444; padding: 12px; font-weight: 700;">Lỗi preview: ${res.error}</div>`;
            }
        } catch (e) {
            if (previewBox) previewBox.innerHTML = `<div style="color: #ef4444; padding: 12px; font-weight: 700;">Lỗi kết nối: ${e.message}</div>`;
        }
    },

    async submitHolidayShift() {
        const title = document.getElementById('holiday-title')?.value || '';
        const holiday_type = document.getElementById('holiday-type')?.value || 'Nghỉ lễ cố định';
        const start_date = document.getElementById('holiday-start-date')?.value || '';
        const end_date = document.getElementById('holiday-end-date')?.value || '';
        const scope = document.getElementById('holiday-scope')?.value || 'ALL';
        const note = document.getElementById('holiday-note')?.value || '';

        if (!title.trim()) {
            alert('Vui lòng nhập Tên Dịp / Lý Do Nghỉ!');
            return;
        }

        if (!start_date || !end_date) {
            alert('Vui lòng chọn Từ Ngày và Đến Ngày!');
            return;
        }

        if (!confirm(`Bạn có chắc chắn muốn áp dụng đợt nghỉ "${title}" từ ${start_date} đến ${end_date}?\nSyllabus và ngày hết phí của học sinh sẽ tự động được tịnh tiến!`)) {
            return;
        }

        try {
            const currentUser = (typeof AuthModule !== 'undefined' && AuthModule.getUser) ? AuthModule.getUser() : null;
            const createdByName = currentUser ? currentUser.full_name : 'Admin';

            const res = await API.post('/schedule/holiday-shift', {
                title: title,
                holiday_type: holiday_type,
                start_date: start_date,
                end_date: end_date,
                affected_classes: [scope],
                note: note,
                created_by: createdByName
            });

            if (res && res.success) {
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast('🎉 ' + res.message, 'success');
                } else {
                    alert('🎉 ' + res.message);
                }
                this.closeHolidayModal();
                // Refresh main schedule page matrix
                const container = document.getElementById('schedule');
                if (container) this.renderPage(container);
            } else {
                alert('Lỗi áp dụng đợt nghỉ: ' + (res.error || res.message));
            }
        } catch (e) {
            alert('Lỗi kết nối server: ' + e.message);
        }
    },

    async renderHolidayHistoryTable() {
        const container = document.getElementById('holiday-tab-container');
        if (!container) return;

        try {
            const res = await API.get('/schedule/holiday-history');
            if (res && res.success) {
                const logs = res.data || [];
                if (logs.length === 0) {
                    container.innerHTML = `
                        <div style="background: #ffffff; border-radius: 12px; padding: 40px; text-align: center; color: #64748b; border: 1px solid #e2e8f0;">
                            <div style="font-size: 36px; margin-bottom: 8px;">🌴</div>
                            <div style="font-weight: 800; font-size: 15px;">Chưa có đợt lùi lịch/nghỉ lễ nào được ghi nhận</div>
                            <div style="font-size: 13px; margin-top: 4px;">Hãy tạo mới đợt nghỉ tại tab "Khai Báo Đợt Nghỉ Mới".</div>
                        </div>
                    `;
                    return;
                }

                let rowsHtml = logs.map(l => {
                    const isActive = (l.status === 'Active');
                    const badgeBg = isActive ? '#dcfce7' : '#f1f5f9';
                    const badgeFg = isActive ? '#15803d' : '#64748b';
                    const badgeText = isActive ? '🟢 Đang áp dụng' : '⚪ Đã hủy';

                    return `
                        <tr>
                            <td style="padding: 10px; font-weight: 800; border-bottom: 1px solid #f1f5f9;">#${l.id}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #f1f5f9;">
                                <div style="font-weight: 800; color: #1e293b;">${l.title}</div>
                                <div style="font-size: 11px; color: #64748b;">${l.holiday_type} ${l.note ? '• ' + l.note : ''}</div>
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #f1f5f9; font-weight: 700; color: #2563eb;">
                                ${l.start_date} ➔ ${l.end_date}
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #f1f5f9;">
                                <span style="font-weight: 800; color: #7c3aed;">${l.affected_students_count} HS</span> / <span style="font-weight: 700; color: #0284c7;">${l.affected_lessons_count} ca</span>
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 11.5px; color: #475569;">
                                ${l.created_by || 'Admin'}<br/>
                                <span style="color: #94a3b8;">${l.created_at}</span>
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #f1f5f9;">
                                <span style="background: ${badgeBg}; color: ${badgeFg}; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800;">${badgeText}</span>
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #f1f5f9; text-align: center;">
                                ${isActive ? `
                                    <button class="btn btn-sm" style="padding: 4px 10px; font-size: 11.5px; background: #ffe4e6; color: #be123c; border: 1px solid #f43f5e; border-radius: 6px; font-weight: 800; cursor: pointer;" onclick="ScheduleModule.cancelHolidayShift(${l.id}, '${AuthModule.escapeHtml(l.title)}');">
                                        ↩️ Hủy Đợt Nghỉ
                                    </button>
                                ` : '<span style="font-size: 11px; color: #94a3b8;">Không khả dụng</span>'}
                            </td>
                        </tr>
                    `;
                }).join('');

                container.innerHTML = `
                    <div style="background: #ffffff; border-radius: 12px; padding: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                            <thead>
                                <tr style="background: #f8fafc; color: #475569; text-align: left; font-weight: 800;">
                                    <th style="padding: 10px;">ID</th>
                                    <th style="padding: 10px;">Tên Dịp / Lý Do</th>
                                    <th style="padding: 10px;">Thời Gian Nghỉ</th>
                                    <th style="padding: 10px;">Tác Động</th>
                                    <th style="padding: 10px;">Người Tạo</th>
                                    <th style="padding: 10px;">Trạng Thái</th>
                                    <th style="padding: 10px; text-align: center;">Thao Tác</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                `;
            } else {
                container.innerHTML = `<div style="color: #ef4444; padding: 20px; text-align: center;">Lỗi tải lịch sử: ${res.error}</div>`;
            }
        } catch (e) {
            container.innerHTML = `<div style="color: #ef4444; padding: 20px; text-align: center;">Lỗi kết nối: ${e.message}</div>`;
        }
    },

            async cancelHolidayShift(holidayId, title) {
        if (!confirm(`Bạn có chắc chắn muốn HỦY đợt nghỉ "${title}" (#${holidayId})?\nHệ thống sẽ khôi phục lại hạn học (Expiry Date) ban đầu của tất cả học sinh bị ảnh hưởng!`)) {
            return;
        }

        try {
            const res = await API.post('/schedule/holiday-shift/cancel', { holiday_id: holidayId });

            if (res && res.success) {
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast('✅ ' + res.message, 'success');
                } else {
                    alert('✅ ' + res.message);
                }
                await this.renderHolidayHistoryTable();
                // Refresh main schedule matrix
                const container = document.getElementById('schedule');
                if (container) this.renderPage(container);
            } else {
                alert('Lỗi hủy đợt nghỉ: ' + (res.error || res.message));
            }
        } catch (e) {
            alert('Lỗi kết nối server: ' + e.message);
        }
    },

    /**
     * Nhảy Bài & Ghim / Hủy ghim bài học hiện tại cho lớp (Option 2)
     */
    async jumpToLessonProgress(className, buoiNum) {
        const isReset = (buoiNum === 0 || !buoiNum);
        const confirmMsg = isReset
            ? `Bạn có chắc chắn muốn hủy ghim bài học và đưa Lớp ${className} trở về chế độ tự động tính theo ngày không?`
            : `Bạn có chắc chắn muốn nhảy bài và ghim Buổi ${buoiNum} làm bài học hiện tại cho Lớp ${className} trên Thời khóa biểu & Dashboard không?`;

        if (!confirm(confirmMsg)) return;

        try {
            const res = await API.post('/schedule/jump-lesson', {
                class_name: className,
                lesson_num: isReset ? null : buoiNum
            });

            if (res && res.success) {
                const msg = (res.jump_res && res.jump_res.message) || (isReset ? '✅ Đã hủy ghim bài học thành công!' : `✅ Đã ghim Buổi ${buoiNum} làm bài học hiện tại thành công!`);
                if (typeof App !== 'undefined' && App.showToast) {
                    App.showToast(msg, 'success');
                } else {
                    alert(msg);
                }

                // Re-open/refresh modal with updated log
                await this.openLessonLogModal(className);

                // Refresh all active timetable views (Dashboard & Schedule page)
                this.refreshActiveScheduleViews();
            } else {
                alert('Lỗi nhảy bài: ' + (res.error || res.message || 'Không thể cập nhật'));
            }
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
        }
    },

    /**
     * Nhảy tiêu điểm tới bài học được chọn
     */
    jumpToLesson(index, buoiNum) {
        if (!this.currentLessonsList || index < 0 || index >= this.currentLessonsList.length) return;

        this.currentTargetIndex = index;
        const targetLesson = this.currentLessonsList[index];
        const buoi = buoiNum || (targetLesson ? targetLesson.buoi : index + 1);

        // Update target badge header
        const badge = document.getElementById('target-location-badge');
        if (badge) {
            badge.innerHTML = `📍 Đã định vị: Buổi ${buoi} (Người dùng chọn thủ công)`;
            badge.style.background = '#e0e7ff';
            badge.style.color = '#3730a3';
            badge.style.borderColor = '#818cf8';
        }

        // Update row styling
        this.currentLessonsList.forEach((_, idx) => {
            const row = document.getElementById(`lesson-row-${idx}`);
            if (row) {
                if (idx === index) {
                    row.style.background = 'rgba(255, 126, 95, 0.15)';
                    row.style.fontWeight = '700';
                    row.style.border = '2px solid #ff7e5f';
                } else {
                    row.style.background = '';
                    row.style.fontWeight = '';
                    row.style.border = '';
                }
            }
        });

        // Scroll into view smoothly
        const targetRow = document.getElementById(`lesson-row-${index}`);
        if (targetRow) {
            targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        if (typeof App !== 'undefined' && App.showToast) {
            App.showToast(`📌 Đã nhảy tới Buổi ${buoi} (${targetLesson ? (targetLesson.lesson_title || 'Lesson ' + buoi) : ''})`, 'info');
        }
    }
};
