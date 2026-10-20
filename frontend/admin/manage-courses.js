// document.addEventListener("DOMContentLoaded", function () {
//     const courseList = document.getElementById("course-list");

//     // Example Course Data (Replace with backend data)
//     let courses = [
//         { name: "Computer Science", description: "Learn programming and algorithms" },
//         { name: "Mechanical Engineering", description: "Explore machine design and thermodynamics" },
//         { name: "Business Administration", description: "Develop management and leadership skills" }
//     ];

//     function displayCourses() {
//         courseList.innerHTML = "";
//         courses.forEach((course, index) => {
//             let row = document.createElement("tr");
//             row.innerHTML = `
//                 <td>${course.name}</td>
//                 <td>${course.description}</td>
//                 <td>
//                     <button onclick="editCourse(${index})">Edit</button>
//                     <button onclick="deleteCourse(${index})" style="background: red;">Delete</button>
//                 </td>
//             `;
//             courseList.appendChild(row);
//         });
//     }

//     function openAddCourseModal() {
//         document.getElementById("addCourseModal").style.display = "block";
//     }

//     function closeAddCourseModal() {
//         document.getElementById("addCourseModal").style.display = "none";
//     }

//     document.getElementById("add-course-form").addEventListener("submit", function (event) {
//         event.preventDefault();

//         let courseName = document.getElementById("course-name").value.trim();
//         let courseDesc = document.getElementById("course-desc").value.trim();

//         if (courseName && courseDesc) {
//             courses.push({ name: courseName, description: courseDesc });
//             displayCourses();
//             closeAddCourseModal();
//         }
//     });

//     function deleteCourse(index) {
//         if (confirm("Are you sure you want to delete this course?")) {
//             courses.splice(index, 1);
//             displayCourses();
//         }
//     }

//     function editCourse(index) {
//         let newName = prompt("Enter new course name:", courses[index].name);
//         let newDesc = prompt("Enter new description:", courses[index].description);

//         if (newName && newDesc) {
//             courses[index].name = newName;
//             courses[index].description = newDesc;
//             displayCourses();
//         }
//     }

//     displayCourses();
// });


document.addEventListener("DOMContentLoaded", async function () {
    const courseList = document.getElementById("course-list");
    let courses = [];

    function openAddCourseModal() {
        document.getElementById("addCourseModal").style.display = "block";
    }

    function closeAddCourseModal() {
        document.getElementById("addCourseModal").style.display = "none";
    }

    // Inline onclick="..." handlers in the HTML need these on window.
    window.openAddCourseModal = openAddCourseModal;
    window.closeAddCourseModal = closeAddCourseModal;

    if (!(await requireRole("admin", "admin-login.html"))) return;

    function handleResult(response) {
        return readJson(response).then(data => {
            alert(data.message || data.error || (response.ok ? "Done." : "Request failed."));
            return response.ok;
        });
    }

    function fetchCourses() {
        apiFetch("/get_courses")
            .then(response => {
                if (!response.ok) throw new Error("HTTP " + response.status);
                return response.json();
            })
            .then(data => {
                courses = data;
                courseList.innerHTML = "";
                if (data.length === 0) {
                    courseList.innerHTML = '<tr><td colspan="3">No courses added yet.</td></tr>';
                    return;
                }
                data.forEach(course => {
                    let row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${escapeHtml(course.name)}</td>
                        <td>${escapeHtml(course.description)}</td>
                        <td>
                            <button onclick="editCourse(${Number(course.id)})">Edit</button>
                            <button onclick="deleteCourse(${Number(course.id)})" style="background: red;">Delete</button>
                        </td>
                    `;
                    courseList.appendChild(row);
                });
            })
            .catch(error => {
                courseList.innerHTML = '<tr><td colspan="3">Failed to load courses.</td></tr>';
                console.error("Error fetching courses:", error);
            });
    }

    document.getElementById("add-course-form").addEventListener("submit", function (event) {
        event.preventDefault();

        let courseName = document.getElementById("course-name").value.trim();
        let courseDesc = document.getElementById("course-desc").value.trim();

        if (courseName && courseDesc) {
            apiFetch("/add_course", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: courseName, description: courseDesc })
            })
            .then(handleResult)
            .then(ok => {
                if (ok) {
                    document.getElementById("add-course-form").reset();
                    closeAddCourseModal();
                    fetchCourses();
                }
            })
            .catch(error => console.error("Error adding course:", error));
        }
    });

    function deleteCourse(id) {
        if (confirm("Are you sure you want to delete this course?")) {
            apiFetch(`/delete_course/${id}`, {
                method: "DELETE"
            })
            .then(handleResult)
            .then(() => fetchCourses())
            .catch(error => console.error("Error deleting course:", error));
        }
    }

    function editCourse(id) {
        const current = courses.find(c => c.id === id) || {};
        let newName = prompt("Enter new course name:", current.name || "");
        let newDesc = prompt("Enter new description:", current.description || "");

        if (newName && newDesc) {
            apiFetch(`/edit_course/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: newName, description: newDesc })
            })
            .then(handleResult)
            .then(() => fetchCourses())
            .catch(error => console.error("Error updating course:", error));
        }
    }

    window.editCourse = editCourse;
    window.deleteCourse = deleteCourse;

    fetchCourses();
});
