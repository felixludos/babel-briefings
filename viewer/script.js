// import JSONFormatter from 'json-formatter-js'

const location_clusters = {"en": ["au", "ca", "gb", "ie", "in", "my", "ng", "nz", "ph", "sa", "sg", "us", "za"], "es": ["ar", "co", "cu", "mx", "ve"], "de": ["at", "ch", "de"], "fr": ["be", "fr", "ma"], "zh": ["cn", "hk", "tw"], "ar": ["ae", "eg"], "pt": ["br", "pt"], "bg": ["bg"], "cs": ["cz"], "el": ["gr"], "he": ["il"], "hu": ["hu"], "id": ["id"], "it": ["it"], "ja": ["jp"], "ko": ["kr"], "lt": ["lt"], "lv": ["lv"], "nl": ["nl"], "no": ["no"], "pl": ["pl"], "ro": ["ro"], "ru": ["ru"], "sv": ["se"], "sl": ["si"], "sk": ["sk"], "sr": ["rs"], "th": ["th"], "tr": ["tr"], "uk": ["ua"]};
const location_names = {"gb": "United Kingdom", "ar": "Argentina", "pl": "Poland", "sk": "Slovakia", "us": "United States", "eg": "Egypt", "no": "Norway", "ph": "Philippines", "at": "Austria", "rs": "Serbia", "tw": "Taiwan", "be": "Belgium", "cu": "Cuba", "sa": "Saudi Arabia", "th": "Thailand", "id": "Indonesia", "ru": "Russian Federation", "ch": "Switzerland", "fr": "France", "lt": "Lithuania", "tr": "Turkey", "de": "Germany", "cz": "Czechia", "pt": "Portugal", "ae": "United Arab Emirates", "it": "Italy", "cn": "China", "lv": "Latvia", "nl": "Netherlands", "hk": "Hong Kong", "ca": "Canada", "br": "Brazil", "hu": "Hungary", "kr": "Korea", "si": "Slovenia", "au": "Australia", "my": "Malaysia", "ie": "Ireland", "ua": "Ukraine", "in": "India", "ma": "Morocco", "bg": "Bulgaria", "ng": "Nigeria", "il": "Israel", "se": "Sweden", "za": "South Africa", "ve": "Venezuela", "nz": "New Zealand", "jp": "Japan", "sg": "Singapore", "gr": "Greece", "mx": "Mexico", "co": "Colombia", "ro": "Romania"};
const language_names = {"en": "English", "ko": "Korean", "ru": "Russian", "es": "Spanish", "pt": "Portuguese", "cs": "Czech", "tr": "Turkish", "nl": "Dutch", "ar": "Arabic", "fr": "French", "bg": "Bulgarian", "id": "Indonesian", "sk": "Slovak", "el": "Greek", "he": "Hebrew", "sr": "Serbian", "hu": "Hungarian", "th": "Thai", "zh": "Chinese", "no": "Norwegian", "sl": "Slovenian", "sv": "Swedish", "de": "German", "lv": "Latvian", "pl": "Polish", "it": "Italian", "ro": "Romanian", "lt": "Lithuanian", "ja": "Japanese", "uk": "Ukrainian"};
const category_names = {"general": "General", "business": "Business", "entertainment": "Entertainment", "health": "Health", "science": "Science", "sports": "Sports", "technology": "Technology"};


document.addEventListener('DOMContentLoaded', function() {
    // Simulate loading sample data
    fetch('sample_articles_locs.json')
        .then(response => response.json())
        .then(data => {
            const samples = data;
            function displaySamples(sampleData) {

                let viz = document.getElementById('visualization');

                
                if (sampleData.language) {
                    let block = document.createElement('div');
                    block.classList.add('sample-item');
                    
                    let tag = document.createElement('span');
                    tag.classList.add('sample-key');
                    tag.textContent = 'language';
                    block.appendChild(tag);

                    let value = document.createElement('span');
                    value.classList.add('sample-value');
                    value.textContent = language_names[sampleData.language];
                    block.appendChild(value);

                    viz.appendChild(block);
                }

                // viz.appendChild(document.createElement('hr'));



                // viz.appendChild(document.createElement('div'));


                // let viz = "";
                
                // <div class="sample-item">
                //     <span class="sample-key">title</span>
                //     <span class="sample-value" id="sampleTitle"></span>
                // </div>
                // <div class="sample-item">
                //     <span class="sample-key">Key:</span>
                //     <span class="sample-value" id="sampleMeta"></span>
                // </div>
                // <div class="sample-item">
                //     <span class="sample-key">Key:</span>
                //     <span class="sample-value" id="sampleDescription"></span>
                // </div>
                // <div class="sample-item">
                //     <span class="sample-key">Key:</span>
                //     <a href="" class="sample-value" id="sampleLink">Read Full Article</a>
                // </div>

                // if (sampleData.language) {
                //     viz += `<div class="sample-item"><span class="sample-key">language</span><span class="sample-value" id="sampleTitle">${language_names[sampleData.language]}</span></div>`;
                // }
                // if (sampleData.title) {
                //     viz += `<div class="sample-item"><span class="sample-key">title</span><h3 class="sample-value" id="sampleTitle">${sampleData.title}</h3></div>`;
                // }
                // if (sampleData['en-title']) {
                //     viz += `<span class="sample-key">en-title</span><span class="sample-value" id="sampleTitle">${sampleData['en-title']}</span>`;
                // }
                
                // document.getElementsByClassName('sample-container')[0].innerHTML = viz;

                // document.getElementById('sampleTitle').textContent = sampleData.title;
                // document.getElementById('sampleDescription').textContent = sampleData.description;
                // document.getElementById('sampleLink').href = sampleData.url;
                // if (sampleData.urlToImage) {
                //     document.getElementById('sampleImage').src = sampleData.urlToImage;
                // }
                // document.getElementById('sampleMeta').textContent = `Published at: ${sampleData.publishedAt} | Language: ${sampleData.language}`;
        
                // document.getElementById('jsonDataContainer').textContent = JSON.stringify(sampleData, null, 2);
                
                
                const config = {
                    hoverPreviewEnabled: true,
                    hoverPreviewArrayCount: 100,
                    hoverPreviewFieldCount: 5,
                    theme: '',
                    animateOpen: true,
                    animateClose: true,
                    useToJSON: true
                  };
                const formatter = new JSONFormatter(sampleData, 3, config);
                
                var container = document.getElementById('jsonDataContainer');
                container.innerHTML = '';
                container.appendChild(formatter.render());
            }
            
            function resample(location, language, category) {
                let filteredSamples = samples;

                if (location) {
                    filteredSamples = filteredSamples.filter(sample => sample.instances.some(instance => instance.location === location));
                }

                if (language) {
                    filteredSamples = filteredSamples.filter(sample => sample.language === language);
                }

                if (category) {
                    filteredSamples = filteredSamples.filter(sample => sample.instances.some(instance => instance.category === category));
                }

                let index = Math.floor(Math.random() * filteredSamples.length);
                let sample = filteredSamples[index];
                displaySamples(sample);
            }
            
            const languageButtonContainer = document.getElementById('languageButtons');
            Object.keys(location_clusters).sort((a, b) => {
                if (location_clusters[a].length === location_clusters[b].length) {
                    return a.localeCompare(b);
                }
                return location_clusters[b].length - location_clusters[a].length;
            }).forEach(language => {
                let locations = location_clusters[language].sort((a, b) => location_names[a].localeCompare(location_names[b]));

                // create button group: first by language, then list one button for each location

                let group = document.createElement("span");
                group.classList.add("language-group");
                let languageButton = document.createElement("button");
                languageButton.classList.add("language-button");
                languageButton.textContent = language_names[language];
                languageButton.addEventListener('click', function() {
                    resample(null, language, null);
                });

                let locs = document.createElement("span");
                locs.classList.add("language-group-locs");

                group.appendChild(languageButton);
                locations.forEach(location => {
                    let button = document.createElement("button");
                    button.textContent = location_names[location];
                    button.classList.add("location-button");
                    button.addEventListener('click', function() {
                        resample(location, null, null);
                    });
                    locs.appendChild(button);
                })
                languageButtonContainer.appendChild(group);
                group.appendChild(locs);
            });

            const categoryButtons = Object.keys(category_names).map(category => {
                const button = document.createElement('button');
                button.classList.add("category-button");
                button.textContent = category_names[category];
                button.addEventListener('click', function() {
                    resample(null, null, category);
                });
                return button;
            });
            const categoryButtonContainer = document.getElementById('categoryButtons');
            categoryButtons.forEach(button => {
                categoryButtonContainer.appendChild(button);
            });

            resample();

            document.getElementById('resampleButton').addEventListener('click', function() {
                resample();
            });



        })
        .catch(error => {
            console.error('Error loading samples:', error);
        });

});