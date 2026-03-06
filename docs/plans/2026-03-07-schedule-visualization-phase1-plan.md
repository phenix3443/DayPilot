# Schedule Visualization Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement three view modes (Timeline, List, Card) and view switching for schedule visualization

**Architecture:** Pure HTML/CSS/JS, no frameworks, modular component structure

**Tech Stack:** CSS Grid, Flexbox, vanilla JavaScript

---

## Task 1: Create View Switcher Component

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add view switcher HTML**

Add after line 24 (before `<div id="schedule">`):

```html
<div id="view-controls" style="display:none; margin-top: 20px;">
    <button onclick="switchView('timeline')" id="btn-timeline">时间轴</button>
    <button onclick="switchView('list')" id="btn-list" class="active">列表</button>
    <button onclick="switchView('card')" id="btn-card">卡片</button>
</div>
```

**Step 2: Add CSS for view switcher**

Add to `<style>` section:

```css
#view-controls button { padding: 8px 15px; margin-right: 5px; }
#view-controls button.active { background: #0066cc; color: white; }
```

**Step 3: Test view switcher appears**

Manual test: Open index.html, verify buttons hidden initially

**Step 4: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: add view switcher component"
```

---

## Task 2: Implement List View (Default)

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Update schedule display function**

Replace `generateSchedule` function (lines 66-91) with:

```javascript
let currentView = 'list';
let scheduleData = [];

async function generateSchedule(task) {
    try {
        const res = await fetch(`${API_BASE}/api/schedule`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task, busy_events: [], work_window: ['09:00', '18:00'] })
        });
        const data = await res.json();
        scheduleData = data.blocks;

        document.getElementById('view-controls').style.display = 'block';
        renderSchedule();
    } catch (err) {
        addMessage('生成日程失败: ' + err.message, 'assistant');
    }
}

function renderSchedule() {
    const scheduleDiv = document.getElementById('schedule');
    scheduleDiv.innerHTML = '<h3>生成的日程：</h3>';

    if (scheduleData.length === 0) {
        scheduleDiv.innerHTML += '<p>无法在截止时间前安排任务</p>';
        return;
    }

    if (currentView === 'list') {
        renderListView(scheduleDiv);
    }
}

function renderListView(container) {
    const ul = document.createElement('ul');
    ul.style.listStyle = 'none';
    ul.style.padding = '0';

    scheduleData.forEach(block => {
        const li = document.createElement('li');
        li.className = 'block';
        li.innerHTML = `
            <strong>${block.title}</strong><br>
            ${block.start} - ${block.end} (${block.duration_minutes}分钟)
        `;
        ul.appendChild(li);
    });

    container.appendChild(ul);
}
```

**Step 2: Test list view renders**

Manual test: Input task, verify list view displays

**Step 3: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement list view for schedule"
```

---

## Task 3: Implement Card View

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add card view CSS**

Add to `<style>` section:

```css
.card-container { display: flex; flex-wrap: wrap; gap: 10px; }
.card { background: #f9f9f9; border: 1px solid #ddd; border-radius: 8px;
        padding: 15px; width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.card-title { font-weight: bold; margin-bottom: 8px; }
.card-time { color: #666; font-size: 14px; }
```

**Step 2: Add card view render function**

Add after `renderListView` function:

```javascript
function renderCardView(container) {
    const cardContainer = document.createElement('div');
    cardContainer.className = 'card-container';

    scheduleData.forEach(block => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-title">${block.title}</div>
            <div class="card-time">开始: ${block.start}</div>
            <div class="card-time">结束: ${block.end}</div>
            <div class="card-time">时长: ${block.duration_minutes}分钟</div>
        `;
        cardContainer.appendChild(card);
    });

    container.appendChild(cardContainer);
}
```

**Step 3: Update renderSchedule to support card view**

Modify `renderSchedule` function:

```javascript
if (currentView === 'list') {
    renderListView(scheduleDiv);
} else if (currentView === 'card') {
    renderCardView(scheduleDiv);
}
```

**Step 4: Test card view**

Manual test: Switch to card view, verify cards display

**Step 5: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement card view for schedule"
```

---

## Task 4: Implement Timeline View

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add timeline CSS**

Add to `<style>` section:

```css
.timeline { position: relative; margin-top: 20px; }
.timeline-header { display: grid; grid-template-columns: 80px repeat(24, 1fr);
                   border-bottom: 2px solid #333; padding-bottom: 5px; }
.timeline-hour { text-align: center; font-size: 12px; }
.timeline-row { display: grid; grid-template-columns: 80px repeat(24, 1fr);
                min-height: 60px; border-bottom: 1px solid #eee; position: relative; }
.timeline-date { padding: 10px; font-weight: bold; }
.timeline-block { position: absolute; background: #4CAF50; color: white;
                  padding: 5px; border-radius: 4px; font-size: 12px;
                  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
```

**Step 2: Add timeline render function**

Add after `renderCardView` function:

```javascript
function renderTimelineView(container) {
    const timeline = document.createElement('div');
    timeline.className = 'timeline';

    // Header with hours
    const header = document.createElement('div');
    header.className = 'timeline-header';
    header.innerHTML = '<div></div>';
    for (let h = 0; h < 24; h++) {
        header.innerHTML += `<div class="timeline-hour">${h}:00</div>`;
    }
    timeline.appendChild(header);

    // Group blocks by date
    const blocksByDate = {};
    scheduleData.forEach(block => {
        const date = block.start.split('T')[0];
        if (!blocksByDate[date]) blocksByDate[date] = [];
        blocksByDate[date].push(block);
    });

    // Render each date row
    Object.keys(blocksByDate).sort().forEach(date => {
        const row = document.createElement('div');
        row.className = 'timeline-row';
        row.innerHTML = `<div class="timeline-date">${date}</div>`;

        blocksByDate[date].forEach(block => {
            const startTime = new Date(block.start);
            const endTime = new Date(block.end);
            const startHour = startTime.getHours() + startTime.getMinutes() / 60;
            const duration = (endTime - startTime) / (1000 * 60 * 60);

            const blockDiv = document.createElement('div');
            blockDiv.className = 'timeline-block';
            blockDiv.style.left = `${80 + (startHour / 24) * (100 - 80 / container.offsetWidth * 100)}%`;
            blockDiv.style.width = `${(duration / 24) * (100 - 80 / container.offsetWidth * 100)}%`;
            blockDiv.textContent = block.title;
            blockDiv.title = `${block.start} - ${block.end}`;

            row.appendChild(blockDiv);
        });

        timeline.appendChild(row);
    });

    container.appendChild(timeline);
}
```

**Step 3: Update renderSchedule to support timeline**

Modify `renderSchedule` function:

```javascript
if (currentView === 'list') {
    renderListView(scheduleDiv);
} else if (currentView === 'card') {
    renderCardView(scheduleDiv);
} else if (currentView === 'timeline') {
    renderTimelineView(scheduleDiv);
}
```

**Step 4: Test timeline view**

Manual test: Switch to timeline, verify blocks positioned correctly

**Step 5: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement timeline view for schedule"
```

---

## Task 5: Implement View Switching Logic

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add switchView function**

Add after `renderTimelineView` function:

```javascript
function switchView(view) {
    currentView = view;

    // Update button states
    document.querySelectorAll('#view-controls button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`btn-${view}`).classList.add('active');

    // Re-render schedule
    renderSchedule();
}
```

**Step 2: Test view switching**

Manual test: Click each button, verify view changes

**Step 3: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement view switching functionality"
```

---

## Task 6: Manual End-to-End Testing

**Test Cases:**

1. **List View (Default)**
   - Input: "明天花2小时健身"
   - Expected: List view shows time blocks

2. **Card View**
   - Click "卡片" button
   - Expected: Cards display with all details

3. **Timeline View**
   - Click "时间轴" button
   - Expected: Timeline shows blocks positioned by time

4. **View Switching**
   - Switch between all three views
   - Expected: Smooth transitions, data persists

**Step 1: Start API server**

```bash
cd apps/api
DEEPSEEK_API_KEY=<key> poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 2: Open Web UI**

Open `apps/web/index.html` in browser

**Step 3: Run test cases**

Execute each test case, document results

**Step 4: Fix any issues found**

If bugs discovered, fix and re-test

---

## Completion Criteria

- ✅ Three views implemented (List, Card, Timeline)
- ✅ View switcher functional
- ✅ All views display schedule data correctly
- ✅ Manual tests pass
- ✅ Code committed to git
