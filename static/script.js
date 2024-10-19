document.addEventListener('DOMContentLoaded', function () {
    const newSectionBtn = document.getElementById('new-section-btn');
    const modal = document.getElementById('modal');
    const modalOverlay = document.getElementById('modal-overlay');
    const closeModalBtn = document.getElementById('close-modal');
    const localBtn = document.getElementById('local-btn');
    const localChoicesContainer = document.getElementById('local-choices-container');
    const localChoices = document.getElementById('local-choices');
    const searchBar = document.getElementById('search-bar');
    const seeMoreBtn = document.getElementById('see-more-btn');

    const datasetModal = document.getElementById('dataset-modal');
    const closeDatasetModalBtn = document.getElementById('close-dataset-modal');
    const selectedDatasetSpan = document.getElementById('selected-dataset');
    const columnSelector = document.getElementById('column-selector');
    const confirmSelectionBtn = document.getElementById('confirm-selection');
    const forecastContainer = document.getElementById('forecast-container');
    const forecastPlot = document.getElementById('forecast-plot');

    let allCsvFiles = [];
    let displayedCsvFiles = [];
    let selectedFile = null;
    let columns = [];
    let currentPage = 1;
    const pageSize = 6;

    // Show the modal when "+" button is clicked
    newSectionBtn.addEventListener('click', function () {
        modal.classList.remove('hidden');
        modalOverlay.classList.remove('hidden');
    });

    // Close modal
    closeModalBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);

    function closeModal() {
        modal.classList.add('hidden');
        modalOverlay.classList.add('hidden');
        localChoices.innerHTML = '';
        localChoicesContainer.classList.add('hidden');
        currentPage = 1;
        searchBar.value = '';
    }

    // Fetch and display CSV files when "Local" is clicked
    localBtn.addEventListener('click', function () {
        fetch('/list_csv_files')
            .then(response => response.json())
            .then(csvFiles => {
                allCsvFiles = csvFiles;
                displayedCsvFiles = csvFiles;
                localChoicesContainer.classList.remove('hidden');
                showCsvFiles();
            })
            .catch(error => console.error('Error fetching CSV files:', error));
    });

    // Show CSV files with pagination
    function showCsvFiles() {
        const paginatedFiles = displayedCsvFiles.slice((currentPage - 1) * pageSize, currentPage * pageSize);
        localChoices.innerHTML = ''; // Clear previous choices

        paginatedFiles.forEach(file => {
            const button = document.createElement('button');
            button.className = 'choice';
            button.textContent = file;
            button.addEventListener('click', () => selectFile(file));
            localChoices.appendChild(button);
        });

        if (currentPage * pageSize < displayedCsvFiles.length) {
            seeMoreBtn.classList.remove('hidden');
        } else {
            seeMoreBtn.classList.add('hidden');
        }
    }

    function selectFile(file) {
        selectedFile = file;
        modal.classList.add('hidden');
        datasetModal.classList.remove('hidden');
        selectedDatasetSpan.textContent = file;

        fetch(`/get_columns?file=${file}`)
            .then(response => response.json())
            .then(data => {
                columns = data.columns;
                if (columns.length === 2 && columns.includes('ds') && columns.includes('y')) {
                    columnSelector.innerHTML = '<option value="y">y</option>';
                } else {
                    populateColumnSelector(columns);
                }
            })
            .catch(error => console.error('Error fetching columns:', error));
    }

    function populateColumnSelector(columns) {
        columnSelector.innerHTML = '';
        columns.forEach(column => {
            const option = document.createElement('option');
            option.value = column;
            option.textContent = column;
            columnSelector.appendChild(option);
        });
    }

    confirmSelectionBtn.addEventListener('click', function () {
        const selectedColumn = columnSelector.value;
        const selectedQualityCheck = document.querySelector('input[name="quality-check"]:checked').value;

        fetch('/process_quality_check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dataset: selectedFile,
                column: selectedColumn,
                quality_check: selectedQualityCheck,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.forecast_plot_url && data.components_plot_url) {
                // Display the forecast plot
                const forecastPlot = document.getElementById('forecast-plot');
                forecastPlot.src = data.forecast_plot_url;

                // Display the components plot
                const componentsPlot = document.getElementById('components-plot');
                componentsPlot.src = data.components_plot_url;

                // Unhide the forecast and components container
                const forecastContainer = document.getElementById('forecast-container');
                forecastContainer.classList.remove('hidden');
            } else {
                console.error('Error in forecast response:', data);
            }
        })
        .catch(error => {
            console.error('Error processing forecast:', error);
        });

        datasetModal.classList.add('hidden');
        modalOverlay.classList.add('hidden');
    });



    searchBar.addEventListener('input', function () {
        const searchTerm = searchBar.value.toLowerCase();
        displayedCsvFiles = allCsvFiles.filter(file => file.toLowerCase().includes(searchTerm));
        currentPage = 1;
        showCsvFiles();
    });
});
