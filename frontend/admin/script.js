/* JavaScript (scripts.js) */
document.getElementById('booking-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Room booked successfully!');
});

document.addEventListener('DOMContentLoaded', function() {
    const userTable = document.querySelector('#user-list tbody');
    if (userTable) {
        userTable.innerHTML = `
            <tr>
                <td>John Doe</td>
                <td>john@example.com</td>
                <td>Single</td>
                <td><button onclick="removeUser(this)">Remove</button></td>
            </tr>`;
    }
});

function removeUser(button) {
    button.parentElement.parentElement.remove();
    alert('User removed');
}
