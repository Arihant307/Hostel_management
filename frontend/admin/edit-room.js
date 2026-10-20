document.addEventListener("DOMContentLoaded", function () {
    // Simulated room data (Replace with backend data)
    const roomData = {
        type: "Single",
        capacity: 1,
        price: 500
    };

    document.getElementById("room-type").value = roomData.type.toLowerCase();
    document.getElementById("capacity").value = roomData.capacity;
    document.getElementById("price").value = roomData.price;

    document.getElementById("edit-room-form").addEventListener("submit", function (event) {
        event.preventDefault();

        let updatedType = document.getElementById("room-type").value;
        let updatedCapacity = document.getElementById("capacity").value;
        let updatedPrice = document.getElementById("price").value;

        if (!updatedCapacity || !updatedPrice) {
            alert("All fields are required!");
            return;
        }

        console.log("Room Updated:", {
            type: updatedType,
            capacity: updatedCapacity,
            price: updatedPrice
        });

        alert("Room details updated successfully!");
    });
});
