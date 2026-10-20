// Students Page Functionality

const API_BASE = '/auth/students';

document.addEventListener('DOMContentLoaded', async () => {
    const studentTableBody = document.querySelector('#studentTable tbody');
    const searchInput = document.getElementById('searchInput');
    const addStudentBtn = document.getElementById('addStudentBtn');
    const studentModal = document.getElementById('studentModal');
    const closeModal = document.getElementById('closeModal');
    const studentForm = document.getElementById('studentForm');
    const modalTitle = document.getElementById('modalTitle');
    const logoutLink = document.getElementById('logoutLink');

    let students = [];
    let editingStudentId = null;

    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            logout('admin-login.html');
        });
    }

    if (!(await requireRole('admin', 'admin-login.html'))) return;

    async function fetchStudents() {
        try {
            const res = await apiFetch(API_BASE);
            if (!res.ok) throw new Error('HTTP ' + res.status);
            students = await res.json();
            renderTable(students);
        } catch (err) {
            studentTableBody.innerHTML = '<tr><td colspan="5">Failed to load students.</td></tr>';
        }
    }

    function renderTable(data) {
        studentTableBody.innerHTML = '';
        if (!data || data.length === 0) {
            studentTableBody.innerHTML = '<tr><td colspan="5">No students found.</td></tr>';
            return;
        }
        data.forEach(student => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${escapeHtml(student.name)}</td>
                <td>${escapeHtml(student.email)}</td>
                <td>${escapeHtml(student.phone || '')}</td>
                <td>${escapeHtml(student.room || '')}</td>
                <td>
                    <button class="action-btn action-view" data-id="${Number(student.id)}">View</button>
                    <button class="action-btn action-edit" data-id="${Number(student.id)}">Edit</button>
                    <button class="action-btn action-delete" data-id="${Number(student.id)}">Delete</button>
                </td>
            `;
            studentTableBody.appendChild(row);
        });
    }

    function filterStudents() {
        const query = searchInput.value.toLowerCase();
        const filtered = students.filter(s =>
            (s.name && s.name.toLowerCase().includes(query)) ||
            (s.email && s.email.toLowerCase().includes(query)) ||
            (s.room && s.room.toLowerCase().includes(query))
        );
        renderTable(filtered);
    }

    searchInput.addEventListener('input', filterStudents);

    addStudentBtn.addEventListener('click', () => {
        editingStudentId = null;
        modalTitle.textContent = 'Add Student';
        studentForm.reset();
        studentModal.style.display = 'block';
    });

    closeModal.addEventListener('click', () => {
        studentModal.style.display = 'none';
    });

    window.onclick = function(event) {
        if (event.target === studentModal) {
            studentModal.style.display = 'none';
        }
    };

    studentTableBody.addEventListener('click', async (e) => {
        if (e.target.classList.contains('action-edit')) {
            const id = Number(e.target.dataset.id);
            const student = students.find(s => s.id === id);
            if (student) {
                editingStudentId = id;
                modalTitle.textContent = 'Edit Student';
                document.getElementById('studentId').value = student.id;
                document.getElementById('studentName').value = student.name;
                document.getElementById('studentEmail').value = student.email;
                document.getElementById('studentPhone').value = student.phone || '';
                document.getElementById('studentRoom').value = student.room || '';
                studentModal.style.display = 'block';
            }
        } else if (e.target.classList.contains('action-delete')) {
            const id = Number(e.target.dataset.id);
            if (confirm('Are you sure you want to delete this student?')) {
                const res = await apiFetch(`${API_BASE}/${id}`, { method: 'DELETE' });
                if (!res.ok) {
                    const data = await readJson(res);
                    alert(data.error || 'Failed to delete student.');
                }
                await fetchStudents();
                filterStudents();
            }
        } else if (e.target.classList.contains('action-view')) {
            const id = Number(e.target.dataset.id);
            const student = students.find(s => s.id === id);
            if (student) {
                alert(`Student ID: ${student.id}\nName: ${student.name}\nEmail: ${student.email}\nPhone: ${student.phone || ''}\nRoom: ${student.room || ''}`);
            }
        }
    });

    studentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('studentName').value.trim();
        const email = document.getElementById('studentEmail').value.trim();
        const phone = document.getElementById('studentPhone').value.trim();
        const room = document.getElementById('studentRoom').value.trim();
        let res;
        try {
            if (editingStudentId) {
                // Edit existing
                res = await apiFetch(`${API_BASE}/${editingStudentId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, phone, room })
                });
            } else {
                // Add new
                res = await apiFetch(API_BASE, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, phone, room })
                });
            }
        } catch (err) {
            alert('Could not reach the server. Please try again.');
            return;
        }
        const data = await readJson(res);
        if (!res.ok) {
            alert(data.error || data.message || 'Failed to save student.');
            return;
        }
        if (data.temporary_password) {
            alert(`Student added.\n\nTemporary password: ${data.temporary_password}\n\n` +
                  'Share it with the student securely. It will not be shown again.');
        }
        studentModal.style.display = 'none';
        await fetchStudents();
        filterStudents();
    });

    // Initial render
    fetchStudents();
});
