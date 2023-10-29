
const loc_code = 'ph';
const prompt_path = `prompts/prompts-${loc_code}.jsonl`;
// const completed_path = `completed/completed_${loc_code}.jsonl`;

let currentIndex = 0;

let pastData = [];
let currentData = [];

const statusline = document.getElementById('statusline');
const playbutton = document.getElementById('automatic');

let statusName = 'Paused';
let interval;
let isPlaying = false;
let i;


// function loadPastHeadlines() {
//     return fetch(completed_path)
//         .then(response => response.text())
//         .then(data => {
//             pastData = data.split('\n').map(line => JSON.parse(line));
//         })
//         .catch(error => {
//             pastData = [];
//             // console.error('Error loading past headlines:', error);
//         });
// }


function loadAndFilterHeadlines() {
    fetch(prompt_path)
        .then(response => response.text())
        .then(data => {
            const rawData = data.split('\n').map(line => JSON.parse(line));
            const pastIDs = pastData.flatMap(record => record.ID);

            // console.log(pastIDs);

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

    if (currentIndex >= currentData.length) {
        i = 0;
        alert('No more records to display!');

        if (isPlaying) {
            isPlaying = false;
            clearInterval(interval);
            playbutton.textContent = 'Play';
            statusName = 'Done';
            statusline.textContent = `${statusName}: showing ${i} - completed ${currentIndex}/${currentData.length} (${currentData.length - currentIndex} records left)`;
        }

        return;
    }

    // Display the records
    for (i = 0; i < numRecords && currentIndex + i < currentData.length; i++) {
        const record = currentData[currentIndex + i];
        // console.log(currentIndex + i, record);
        
        const row = tableBody.insertRow(-1);
        
        const idCell = row.insertCell(0);
        idCell.textContent = record.ids.join(', ');

        const headlineCell = row.insertCell(1);
        headlineCell.textContent = record.title;

        const descriptionCell = row.insertCell(2);
        descriptionCell.textContent = record.description || ''; // Use empty string if description is not available
    }

    statusline.textContent = `${statusName}: showing ${i} - completed ${currentIndex}/${currentData.length} (${currentData.length - currentIndex} records left)`;

    currentIndex += i;
}


document.getElementById('automatic').addEventListener('click', function() {
    if (!isPlaying) {
        isPlaying = true;
        // Start the interval
        interval = setInterval(function() {
            document.getElementById('saveAndNext').click();
        }, parseInt(document.getElementById('autotimer').value)); // Change 5000 to your desired interval (in milliseconds)
        playbutton.textContent = 'Pause';
        statusName = 'Running';

        statusline.textContent = `${statusName}: showing ${i} - completed ${currentIndex}/${currentData.length} (${currentData.length - currentIndex} records left)`;

    } else {
        isPlaying = false;
        clearInterval(interval);
        playbutton.textContent = 'Play';
        statusName = 'Paused';

        statusline.textContent = `${statusName}: showing ${i} - completed ${currentIndex}/${currentData.length} (${currentData.length - currentIndex} records left)`;

    }
});


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
            ids: id,
            title: headline,
            description: description || undefined
        });
    }

    const blob = new Blob([recordsToSave.map(record => JSON.stringify(record)).join('\n')], {type: "text/plain;charset=utf-8"});
    
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `saved_records_${loc_code}.jsonl`; // loc
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Display the next set of records
    displayRecords();
});



loadAndFilterHeadlines();



