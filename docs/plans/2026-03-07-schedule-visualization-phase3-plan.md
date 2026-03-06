# Schedule Visualization Phase 3 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add advanced interactions - drag to adjust time and edit block fields

**Architecture:** HTML5 Drag and Drop for timeline, edit form in modal, in-memory updates

**Tech Stack:** Vanilla JavaScript, HTML5 Drag API

---

## Task 1: Add Drag-and-Drop to Timeline Blocks

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Make timeline blocks draggable**

In `renderTimelineView`, add draggable attribute to blockDiv:

```javascript
blockDiv.draggable = true;
blockDiv.ondragstart = (e) => handleDragStart(e, globalIndex);
```

**Step 2: Add drag event handlers**

Add after `deleteBlock` function:

```javascript
let draggedBlockIndex = null;

function handleDragStart(e, index) {
    draggedBlockIndex = index;
    e.dataTransfer.effectAllowed = 'move';
}
```

**Step 3: Make timeline rows drop targets**

In `renderTimelineView`, add drop handlers to row:

```javascript
row.ondragover = (e) => e.preventDefault();
row.ondrop = (e) => handleDrop(e, date);
```

**Step 4: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: add drag-and-drop to timeline blocks"
```

---

## Task 2: Implement Drop Handler

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add handleDrop function**

Add after `handleDragStart`:

```javascript
function handleDrop(e, targetDate) {
    e.preventDefault();
    if (draggedBlockIndex === null) return;

    const block = scheduleData[draggedBlockIndex];
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left - 80;
    const hourWidth = (rect.width - 80) / 24;
    const newHour = Math.floor(x / hourWidth);
    
    const oldStart = new Date(block.start);
    const duration = block.duration_minutes;
    const newStart = new Date(targetDate + 'T' + String(newHour).padStart(2, '0') + ':00:00');
    const newEnd = new Date(newStart.getTime() + duration * 60000);
    
    block.start = newStart.toISOString();
    block.end = newEnd.toISOString();
    
    draggedBlockIndex = null;
    renderSchedule();
}
```

**Step 2: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement drop handler for time adjustment"
```

---

## Task 3: Add Edit Form to Modal

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Update showBlockDetails to include edit form**

Replace `showBlockDetails` function:

```javascript
function showBlockDetails(index) {
    selectedBlockIndex = index;
    const block = scheduleData[index];

    document.getElementById('modal-body').innerHTML = `
        <div>
            <label>标题: <input type="text" id="edit-title" value="${block.title}" style="width:100%;padding:5px;"></label>
        </div>
        <div style="margin-top:10px;">
            <label>开始: <input type="datetime-local" id="edit-start" value="${block.start.slice(0,16)}" style="width:100%;padding:5px;"></label>
        </div>
        <div style="margin-top:10px;">
            <label>结束: <input type="datetime-local" id="edit-end" value="${block.end.slice(0,16)}" style="width:100%;padding:5px;"></label>
        </div>
    `;

    document.getElementById('detail-modal').style.display = 'block';
}
```

**Step 2: Update modal buttons**

Modify modal HTML to add Save button:

```html
<div class="modal-actions">
    <button onclick="saveBlock()" class="btn-save">保存</button>
    <button onclick="deleteBlock()" class="btn-delete">删除</button>
    <button onclick="closeModal()" class="btn-close">关闭</button>
</div>
```

**Step 3: Add CSS for save button**

```css
.btn-save { background: #28a745; color: white; padding: 8px 15px; border: none;
            border-radius: 4px; cursor: pointer; margin-right: 10px; }
```

**Step 4: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: add edit form to modal"
```

---

## Task 4: Implement Save Function

**Files:**
- Modify: `apps/web/index.html`

**Step 1: Add saveBlock function**

Add after `deleteBlock`:

```javascript
function saveBlock() {
    if (selectedBlockIndex === null) return;

    const title = document.getElementById('edit-title').value;
    const start = document.getElementById('edit-start').value;
    const end = document.getElementById('edit-end').value;

    const block = scheduleData[selectedBlockIndex];
    block.title = title;
    block.start = new Date(start).toISOString();
    block.end = new Date(end).toISOString();
    block.duration_minutes = Math.round((new Date(end) - new Date(start)) / 60000);

    closeModal();
    renderSchedule();
}
```

**Step 2: Commit**

```bash
git add apps/web/index.html
git commit -m "feat: implement save function for block editing"
```

---

## Completion Criteria

- ✅ Timeline blocks are draggable
- ✅ Drop handler adjusts block time
- ✅ Modal has edit form
- ✅ Save function updates block data
- ✅ All views update after changes
- ✅ Code committed

