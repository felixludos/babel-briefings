
// let currentData = mockData.split('\n').map(line => JSON.parse(line));
let currentIndex = 0;

let pastData = [];
let currentData = [];

function loadPastHeadlines() {
    return fetch('completed/completed_hk.jsonl')
        .then(response => response.text())
        .then(data => {
            pastData = data.split('\n').map(line => JSON.parse(line));
        });
}

// // Load headlines from the local "headlines.jsonl" file
// function loadHeadlines() {
//     fetch('prompts/demo-prompts.jsonl')
//         .then(response => response.text())
//         .then(data => {
//             currentData = data.split('\n').map(line => JSON.parse(line));
//             // Initial display after data is loaded
//             displayRecords();
//         })
//         .catch(error => {
//             console.error('Error loading headlines:', error);
//         });
// }

function loadAndFilterHeadlines() {
    fetch('prompts/demo-prompts.jsonl')
        .then(response => response.text())
        .then(data => {
            const rawData = data.split('\n').map(line => JSON.parse(line));
            const pastIDs = pastData.flatMap(record => record.ID);

            console.log(pastIDs)

            // Filter out headlines that have any ID present in the past headlines
            currentData = rawData.filter(record => {
                return !record.ids.some(id => pastIDs.includes(id));
            });

            // Initial display after data is loaded and filtered
            displayRecords();
        })
        .catch(error => {
            console.error('Error loading and filtering headlines:', error);
        });
}

function displayRecords() {
    const numRecords = parseInt(document.getElementById('numRecords').value);
    const tableBody = document.getElementById('tableBody');

    // Clear the table body
    tableBody.innerHTML = '';

    // Display the records
    for (let i = 0; i < numRecords && currentIndex + i < currentData.length; i++) {
        const record = currentData[currentIndex + i];
        console.log(currentIndex + i, record);
        
        const row = tableBody.insertRow(-1);
        
        const idCell = row.insertCell(0);
        idCell.textContent = record.ids.join(', ');

        const headlineCell = row.insertCell(1);
        headlineCell.textContent = record.title;

        const descriptionCell = row.insertCell(2);
        descriptionCell.textContent = record.description || ''; // Use empty string if description is not available
    }

    currentIndex += numRecords;
}

document.getElementById('saveAndNext').addEventListener('click', function() {
    // Save the currently displayed records to a local file
    const tableBody = document.getElementById('tableBody');
    const rows = tableBody.rows;

    let recordsToSave = [];

    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].cells;
        const id = cells[0].textContent.split(', ').map(Number);
        const headline = cells[1].textContent;
        const description = cells[2].textContent;

        recordsToSave.push({
            ID: id,
            headline: headline,
            description: description || undefined
        });
    }

    const blob = new Blob([recordsToSave.map(record => JSON.stringify(record)).join('\n')], {type: "text/plain;charset=utf-8"});
    
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "saved_records_demo.jsonl";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Display the next set of records
    displayRecords();
});



loadPastHeadlines().then(loadAndFilterHeadlines);



// Load the headlines
// loadHeadlines();



// function displayRecords() {
//     const numRecords = parseInt(document.getElementById('numRecords').value);
//     const tableBody = document.getElementById('tableBody');

//     // Clear the table body
//     tableBody.innerHTML = '';

//     // Display the records
//     for (let i = 0; i < numRecords && currentIndex + i < currentData.length; i++) {
//         const record = currentData[currentIndex + i];
//         const row = tableBody.insertRow(-1);
        
//         const idCell = row.insertCell(0);
//         idCell.textContent = record.ID.join(', ');

//         const headlineCell = row.insertCell(1);
//         headlineCell.textContent = record.headline;

//         const descriptionCell = row.insertCell(2);
//         descriptionCell.textContent = record.description || ''; // Use empty string if description is not available
//     }

//     currentIndex += numRecords;
// }


