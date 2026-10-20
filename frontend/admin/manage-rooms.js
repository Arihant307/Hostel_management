document.addEventListener("DOMContentLoaded", async function () {
    const roomList = document.getElementById("room-list");

    function openAddRoomModal() {
        document.getElementById("addRoomModal").style.display = "block";
    }

    function closeAddRoomModal() {
        document.getElementById("addRoomModal").style.display = "none";
    }

    window.openAddRoomModal = openAddRoomModal;
    window.closeAddRoomModal = closeAddRoomModal;

    if (!(await requireRole("admin", "admin-login.html"))) return;

    function fetchRooms() {
        apiFetch("/api/rooms/")
            .then(response => {
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json();
            })
            .then(data => {
                roomList.innerHTML = "";
                if (data.length === 0) {
                    roomList.innerHTML = '<tr><td colspan="5">No rooms added yet.</td></tr>';
                    return;
                }
                data.forEach(room => {
                    let row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${escapeHtml(room.number)}</td>
                        <td>${escapeHtml(room.type || "-")}</td>
                        <td>${escapeHtml(room.capacity)}</td>
                        <td>${escapeHtml(room.occupied ?? "-")}</td>
                        <td>
                            <!-- Edit/Delete can be implemented if needed -->
                        </td>
                    `;
                    roomList.appendChild(row);
                });
            })
            .catch(error => {
                roomList.innerHTML = '<tr><td colspan="5">Failed to load rooms.</td></tr>';
                console.error("Error fetching rooms:", error);
            });
    }

    document.getElementById("add-room-form").addEventListener("submit", function (event) {
        event.preventDefault();

        let roomNumber = document.getElementById("room-number").value.trim();
        let roomType = document.getElementById("room-type").value;
        let capacity = document.getElementById("capacity").value;

        if (roomNumber && capacity) {
            apiFetch("/api/rooms/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ number: roomNumber, type: roomType, capacity: Number(capacity) })
            })
            .then(response => readJson(response).then(data => ({ ok: response.ok, data })))
            .then(({ ok, data }) => {
                alert(data.message || data.error || (ok ? "Room added." : "Failed to add room."));
                if (ok) {
                    document.getElementById("add-room-form").reset();
                    closeAddRoomModal();
                    fetchRooms();
                }
            })
            .catch(error => {
                console.error("Error adding room:", error);
                alert("Could not reach the server. Please try again.");
            });
        }
    });

    fetchRooms();
});
