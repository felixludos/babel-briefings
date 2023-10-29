
const prompt_path = `prompts.jsonl`;

let currentIndex = 0;

let fullPromptData = [];
let currentIDs = [];

const statusline = document.getElementById('statusline');
const playbutton = document.getElementById('automatic');

let numRows = 1;
let numColumns = 1;
let numDisplayedRecords = 0;
let statusName = 'Paused';
let interval;
let isPlaying = false;



function loadPrompts() {
    fetch(prompt_path)
        .then(response => response.text())
        .then(data => {
            fullPromptData = data.split('\n').map(line => JSON.parse(line));
            displayRecords();
        })
        .catch(error => {
            console.error('Error loading prompts:', error);
        });
}

function displayRecords() {
    numRows = parseInt(document.getElementById('numRows').value);
    numColumns = parseInt(document.getElementById('numColumns').value);


    const tableHead = document.getElementById('tableHead');
    tableHead.innerHTML = '';  // Clear existing header
    
    const headerRow = tableHead.insertRow(-1);
    
    // for (let i = 0; i < numColumns; i++) {
        // const headerCell = headerRow.insertCell(-1);
        // headerCell.textContent = `Column ${i + 1}`;
    // }

    const tableBody = document.getElementById('tableBody');

    // Clear the table body
    tableBody.innerHTML = '';

    if (currentIndex >= fullPromptData.length) {
        i = 0;
        alert('No more records to display!');

        if (isPlaying) {
            isPlaying = false;
            clearInterval(interval);
            playbutton.textContent = 'Play';
            statusName = 'Done';
            statusline.textContent = `${statusName}: showing ${i} - completed ${currentIndex}/${fullPromptData.length} (${fullPromptData.length - currentIndex} records left)`;
        }

        return;
    }
    
    // Display one record per row and column

    let remainingRecords = numRows * numColumns;
    if (fullPromptData.length - currentIndex < remainingRecords) {
        remainingRecords = fullPromptData.length - currentIndex;
    }

    statusline.textContent = `${statusName}: showing ${remainingRecords} - completed ${currentIndex}/${fullPromptData.length} (${fullPromptData.length - currentIndex} records left)`;

    while (remainingRecords > 0) {

        const row = tableBody.insertRow(-1);

        for (let i = 0; i < numColumns && remainingRecords > 0; i++) {
            const cell = row.insertCell(-1);
            const record = fullPromptData[currentIndex];
            cell.textContent = record.prompt;
            currentIDs.push(record.id);
            currentIndex++;
            remainingRecords--;
        }
    }
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

        statusline.textContent = `${statusName}: showing ${i} - completed ${currentIndex}/${fullPromptData.length} (${fullPromptData.length - currentIndex} records left)`;

    } else {
        isPlaying = false;
        clearInterval(interval);
        playbutton.textContent = 'Play';
        statusName = 'Paused';

        statusline.textContent = `${statusName}: showing ${i} - completed ${currentIndex}/${fullPromptData.length} (${fullPromptData.length - currentIndex} records left)`;

    }
});

function saveCurrentRecords() {
    // Save the currently displayed records to a local file
    const tableBody = document.getElementById('tableBody');
    const rows = tableBody.rows;

    let recordsToSave = [];

    for (let i = 0; i < currentIDs.length; i++) {
        const cells = rows[Math.floor(i / numColumns)].cells;
        const result = cells[i % numColumns].textContent;

        recordsToSave.push({
            id: currentIDs[i],
            result: result
        });
    }
    
    currentIDs = [];

    const blob = new Blob([recordsToSave.map(record => JSON.stringify(record)).join('\n')], {type: "text/plain;charset=utf-8"});
    
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `results.jsonl`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Display the next set of records
    displayRecords();
}


document.addEventListener('keydown', function(event) {
    if (event.key === ' ') {
        // console.log('Spacebar was pressed!');
        saveCurrentRecords();
    }
});


document.getElementById('saveAndNext').addEventListener('click', saveCurrentRecords);



loadPrompts();



