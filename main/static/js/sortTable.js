let currentSortColumn; // Default column is Trophies (index 4)
let sortDirection; // Default sort direction is descending (highest first)

// Define role hierarchy (Leader > Co-Leader > Elder > Member)
const roleHierarchy = {
    'leader': 1,
    'co-leader': 2,
    'elder': 3,
    'member': 4
};

// Function to sort the table
function sortTable(sortingType, row, tableName = "sortableTable", directon="desc") {
    console.log(tableName);
    const table = document.getElementById(tableName);
    let rows, switching, i, x, y, shouldSwitch;

    switching = true;
    let dir = sortDirection; // Use current sort direction

    if (sortingType === "role") { 
        if (row === currentSortColumn) {
            if (dir === 'asc') {
                dir = 'desc'; // Change to descending
            } else if (dir === 'desc') {
                dir = 'default'; // Change to default
            } else {
                dir = 'asc'; // Change back to ascending
            }
        } else {
            dir = 'asc'; // Reset direction to ascending for a new column
        }
    } else if (sortingType != "none") { 
        if (row === currentSortColumn) {
            if (dir === 'desc') {
                dir = 'asc'; // Change to ascending
            } else if (dir === 'asc') {
                dir = 'default'; // Change to default
            } else {
                dir = 'desc'; // Change back to descending
            }
        } else {
            dir = 'desc'; // Reset direction to descending for a new column
        }
    } 

    sortDirection = dir;
    currentSortColumn = row; // Update the current column index

    // Reset arrows before sorting
    resetArrows();

    // Add the current sorting direction arrow to the header
    addArrow(tableName, row, dir);

    while (switching) {
        switching = false;
        rows = table.rows;

        // Loop through all table rows (except the first row with headers)
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[row];
            y = rows[i + 1].getElementsByTagName("TD")[row];

            // Custom sorting logic for the Role column (index 3)
            if (sortingType === "role") { // Role column (index 3)
                let xRole = roleHierarchy[x.innerHTML.trim().toLowerCase()];
                let yRole = roleHierarchy[y.innerHTML.trim().toLowerCase()];

                if (dir === "asc") {
                    if (xRole > yRole) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir === "desc") {
                    if (xRole < yRole) {
                        shouldSwitch = true;
                        break;
                    }
                }
            } else if (sortingType === "string") {
                // For other columns, use the default string-based comparison
                let xText = x.textContent.trim().toLowerCase(); // Use textContent and trim to clean up
                let yText = y.textContent.trim().toLowerCase();

                if (dir === "asc") {
                    if (xText > yText) {
                        shouldSwitch = true;
                        break; // Once you've determined a switch, no need to keep comparing
                    }
                } else if (dir === "desc") {
                    if (xText < yText) {
                        shouldSwitch = true;
                        break;
                    }
                }
            } else if (sortingType === "int") { // Integer comparison
                let xInt = parseFloat(x.innerHTML.trim());
                let yInt = parseFloat(y.innerHTML.trim());

                if (dir === "asc") {
                    if (xInt > yInt) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir === "desc") {
                    if (xInt < yInt) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }

    if (dir === 'default') {
        resetTableToDefault(tableName, directon);
    }
}

function resetTableToDefault(tableName = "sortableTable", direction="desc") {
    console.log(tableName)
    /*
    if (mode === "general") {
        defaultRow = 2;
        defaultRowType = "role"
    }
    else if (mode === "home_village"){
        defaultRow = 3;
        defaultRowType = "int"
    }
    else if (mode === "builder_base"){
        defaultRow = 1;
        defaultRowType = "int"
    }
    else if (mode === "all"){
        defaultRow = 7;
        defaultRowType = "int"
    }
        */
       
    const table = document.getElementById(tableName);
    let rows = table.rows;

    // Sort the table
    if(defaultRowType === "int"){
        let sortedRows = Array.from(rows).slice(1).sort((a, b) => {
            let x = parseFloat(a.cells[defaultRow].innerText, 10); 
            let y = parseFloat(b.cells[defaultRow].innerText, 10);
            if (direction === "desc"){
                return y - x; // Descending order
            }
            return x - y
        });
        sortedRows.forEach(row => table.appendChild(row));
    } else if (defaultRowType === "role"){
        let sortedRows = Array.from(rows).slice(1).sort((a, b) => {
            let x = a.cells[defaultRow].innerText
            let y = b.cells[defaultRow].innerText
            let xVal = roleHierarchy[x.toLowerCase()];
            let yVal = roleHierarchy[y.toLowerCase()];
            if (direction === "asc"){
                return xVal - yVal;
            }
            return yVal - xVal;
        });
        sortedRows.forEach(row => table.appendChild(row));
    }
}

// Reset arrows
function resetArrows() {
    const arrows = document.querySelectorAll('.sort-arrow');
    arrows.forEach(arrow => {
        arrow.innerHTML = ''; // Remove any arrows
    });
}

// Add the sorting arrow
function addArrow(tableName, n, dir) {
    const table = document.getElementById(tableName); // Get the table by its ID
    const header = table.querySelectorAll('th')[n]; // Select the nth header in the table
    const arrow = header.querySelector('.sort-arrow'); // Find the element with the class 'sort-arrow' inside that header
    if (dir === 'asc') {
        arrow.innerHTML = '▲'; // Ascending arrow
    } else if (dir === 'desc') {
        arrow.innerHTML = '▼'; // Descending arrow
    }
}
