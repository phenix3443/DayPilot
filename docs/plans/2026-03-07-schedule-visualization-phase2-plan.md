# Schedule Visualization Phase 2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add basic interactions - click to view details and delete time blocks

**Architecture:** Modal popup for details, confirmation dialog for delete, in-memory data updates

**Tech Stack:** Vanilla JavaScript, CSS for modal styling

---

## Task 1: Create Modal Component

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add modal HTML**

Add before closing `</body>` tag:

```html
<div id="detail-modal" style="display:none;">
    <div class="modal-overlay" onclick="closeModal()"></div>
    <div class="modal-content">
        <h3>时间块详情</h3>
        <div id="modal-body"></div>
        <div class="modal-actions">
            <button onclick="deleteBlock()" class="btn-delete">删除</button>
            <button onclick="closeModal()" class="btn-close">关闭</button>
        </div>
    </div>
</div>
```

**Step 2: Add modal CSS**

Add to `<style>` section:

```css
#detail-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1000; }
.modal-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                 background: rgba(0,0,0,0.5); }
.modal-content { position: relative; background: white; margin: 100px auto;
                 padding: 20px; width: 400px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
.modal-actions { margin-top: 20px; text-align: right; }
.btn-delete { background: #dc3545; color: white; padding: 8px 15px; border: none;
              border-radius: 4px; cursor: pointer; margin-right: 10px; }
.btn-close { background: #6c757d; color: white; padding: 8px 15px; border: none;
             border-radius: 4px; cursor: pointer; }
```

**Step 3: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: add modal component for block details"
```

---

## Task 2: Add Click Handlers to Blocks

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add global variable for selected block**

Add after `let scheduleData = [];`:

```javascript
let selectedBlockIndex = null;
```

**Step 2: Update renderListView to add click handlers**

In the forEach loop, add index parameter and modify li creation:

```javascript
scheduleData.forEach((block, index) => {
    const li = document.createElement('li');
    li.className = 'block';
    li.style.cursor = 'pointer';
    li.onclick = () => showBlockDetails(index);
    li.innerHTML = `
        <strong>${block.title}</strong><br>
        ${block.start} - ${block.end} (${block.duration_minutes}分钟)
    `;
    ul.appendChild(li);
});
```

**Step 3: Update renderCardView to add click handlers**

In the forEach loop, add index parameter and modify card creation:

```javascript
scheduleData.forEach((block, index) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.cursor = 'pointer';
    card.onclick = () => showBlockDetails(index);
    card.innerHTML = `
        <div class="card-title">${block.title}</div>
        <div class="card-time">开始: ${block.start}</div>
        <div class="card-time">结束: ${block.end}</div>
        <div class="card-time">时长: ${block.duration_minutes}分钟</div>
    `;
    cardContainer.appendChild(card);
});
```

**Step 4: Update renderTimelineView to add click handlers**

In the blocksByDate forEach loop, add index tracking and modify blockDiv creation:

```javascript
blocksByDate[date].forEach((block, idx) => {
    const globalIndex = scheduleData.indexOf(block);
    const startTime = new Date(block.start);
    const endTime = new Date(block.end);
    const startHour = startTime.getHours() + startTime.getMinutes() / 60;
    const duration = (endTime - startTime) / (1000 * 60 * 60);

    const blockDiv = document.createElement('div');
    blockDiv.className = 'timeline-block';
    blockDiv.style.cursor = 'pointer';
    blockDiv.onclick = () => showBlockDetails(globalIndex);
    const gridColumnStart = 2 + Math.floor(startHour);
    const gridColumnEnd = gridColumnStart + Math.ceil(duration);
    blockDiv.style.gridColumn = `${gridColumnStart} / ${gridColumnEnd}`;
    blockDiv.textContent = block.title;
    blockDiv.title = `${block.start} - ${block.end}`;

    row.appendChild(blockDiv);
});
```

**Step 5: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: add click handlers to schedule blocks"
```

---


## Task 3: Implement Modal Functions

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add showBlockDetails function**

Add after `switchView` function:

```javascript
function showBlockDetails(index) {
    selectedBlockIndex = index;
    const block = scheduleData[index];

    document.getElementById('modal-body').innerHTML = `
        <p><strong>标题:</strong> ${block.title}</p>
        <p><strong>开始:</strong> ${block.start}</p>
        <p><strong>结束:</strong> ${block.end}</p>
        <p><strong>时长:</strong> ${block.duration_minutes}分钟</p>
    `;

    document.getElementById('detail-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('detail-modal').style.display = 'none';
    selectedBlockIndex = null;
}
```

**Step 2: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement modal display functions"
```

---

## Task 4: Implement Delete Functionality

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add deleteBlock function**

Add after `closeModal` function:

```javascript
function deleteBlock() {
    if (selectedBlockIndex === null) return;

    if (confirm('确定要删除这个时间块吗？')) {
        scheduleData.splice(selectedBlockIndex, 1);
        closeModal();
        renderSchedule();
    }
}
```

**Step 2: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement delete block functionality"
```

---

## Completion Criteria

- ✅ Modal component created
- ✅ Click handlers in all views
- ✅ Modal displays details
- ✅ Delete with confirmation works
- ✅ Code committed

