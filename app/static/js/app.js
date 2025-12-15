// app/static/js/app.js
document.addEventListener('DOMContentLoaded', function() {

// 新增：获取CSRF Token（从cookie中，Flask-WTF默认存储在csrf_token cookie）
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrf_token') {
                return value;
            }
        }
        return '';
    }

    // Load data
    document.getElementById('loadData').addEventListener('click', async () => {
        const res = await fetch('/api/client/data');
        const data = await res.json();
        if (data.status === 'success') {
            const list = data.data.map(item => `
                <div class="card mb-2">
                    <div class="card-body">
                        <p>${item.data}</p>
                        <small class="text-muted">Creation time: ${item.created_at}</small>
                        <button class="btn btn-danger btn-sm float-end" data-id="${item.id}">Delete</button>
                    </div>
                </div>
            `).join('');
            document.getElementById('dataList').innerHTML = list;

            // Bind event to delete buttons
            document.querySelectorAll('.btn-danger').forEach(btn => {
                btn.addEventListener('click', async function() {
                    const id = this.getAttribute('data-id');
                    if (confirm('Are you sure to delete this data?')) {
                        const res = await fetch(`/api/client/data/${id}`, { method: 'DELETE' });
                        const result = await res.json();
                        alert(result.message);
                        if (result.status === 'success') document.getElementById('loadData').click();
                    }
                });
            });
        }
    });

    // Add data
    document.getElementById('addData').addEventListener('click', async () => {
        const data = prompt('Please enter sensitive data:');
        if (data) {
            const res = await fetch('/api/client/data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json',
                 'X-CSRFToken': getCsrfToken()
                 },
                body: JSON.stringify({ data })
            });
            const result = await res.json();
            alert(result.message);
            if (result.status === 'success') document.getElementById('loadData').click();
        }
    });
});