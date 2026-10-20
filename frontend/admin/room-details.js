document.addEventListener("DOMContentLoaded", function () {
    const roomList = document.getElementById("room-list");

    // Example room data (can be replaced with dynamic backend data)
    const rooms = [
        { type: "Single", capacity: "1 Person", price: "$500" },
        { type: "Double", capacity: "2 Persons", price: "$350" },
        { type: "Shared", capacity: "4 Persons", price: "$250" }
    ];

    rooms.forEach(room => {
        let row = document.createElement("tr");
        row.innerHTML = `
            <td>${room.type}</td>
            <td>${room.capacity}</td>
            <td>${room.price}</td>
        `;
        roomList.appendChild(row);
    });
});
