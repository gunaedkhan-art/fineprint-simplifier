document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const button = form.querySelector('button');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        button.disabled = true;
        button.textContent = 'Analyzing...';
        resultsDiv.innerHTML = '<p class="loading">Analyzing PDF, please wait...</p>';

        const formData = new FormData(form);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                resultsDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
                return;
            }

            const risks = data.analysis?.risks || {};
            const goodPoints = data.analysis?.good_points || {};
            const rating = data.analysis?.contract_rating || {};
            const pages = data.pages || [];

            resultsDiv.innerHTML = "";

            // === Contract Score ===
            if (rating.rating && typeof rating.score_out_of_10 === 'number') {
                const ratingDiv = document.createElement('div');
                ratingDiv.className = 'rating';
                ratingDiv.innerHTML = `
                    <h2>Contract Rating:</h2>
                    <p><strong>${rating.rating}</strong> (${rating.score_out_of_10}/10)</p>
                `;
                resultsDiv.appendChild(ratingDiv);
            }

            // === Good Points ===
            if (Object.keys(goodPoints).length > 0) {
                const gpTitle = document.createElement('h2');
                gpTitle.textContent = "Good Points Found:";
                resultsDiv.appendChild(gpTitle);

                for (const [tag, matches] of Object.entries(goodPoints)) {
                    const tagHeader = document.createElement('h3');
                    tagHeader.textContent = tag;
                    resultsDiv.appendChild(tagHeader);

                    matches.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'match good';
                        div.innerHTML = `
                            <strong>Page ${item.page}</strong><br>${item.match}
                        `;
                        resultsDiv.appendChild(div);
                    });
                }
            }

            // === Risks ===
            if (Object.keys(risks).length > 0) {
                const riskTitle = document.createElement('h2');
                riskTitle.textContent = "Risks Found:";
                resultsDiv.appendChild(riskTitle);

                for (const [tag, matches] of Object.entries(risks)) {
                    const tagHeader = document.createElement('h3');
                    tagHeader.textContent = tag;
                    resultsDiv.appendChild(tagHeader);

                    matches.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'match risk';
                        div.innerHTML = `
                            <strong>Page ${item.page}</strong><br>${item.match}
                        `;
                        resultsDiv.appendChild(div);
                    });
                }
            }

            // === No Results Case ===
            if (!Object.keys(risks).length && !Object.keys(goodPoints).length) {
                resultsDiv.innerHTML += "<p>No risks or good points found in this contract.</p>";
            }

            // === PDF Text for Pattern Selection ===
            if (Array.isArray(pages) && pages.length > 0) {
                const pagesContainer = document.createElement('div');
                pagesContainer.className = 'pages-container';
                pagesContainer.innerHTML = '<h2>Full PDF Text (click to add pattern)</h2>';

                pages.forEach(page => {
                    const pageDiv = document.createElement('div');
                    pageDiv.className = 'page-text';
                    pageDiv.innerHTML = `<h3>Page ${page.page_number}</h3>`;

                    const words = page.text.split(/\s+/);
                    words.forEach(word => {
                        if (!word.trim()) return; // skip empty

                        const span = document.createElement('span');
                        span.textContent = word + ' ';
                        span.className = 'clickable-word';

                        span.addEventListener('click', () => {
                            fetch('/add_pattern', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    category: 'Manual', // default category
                                    phrase: word,
                                    type: 'risk' // default to risk, can make toggle later
                                })
                            })
                            .then(r => r.json())
                            .then(res => {
                                span.style.backgroundColor = 'lightgreen';
                            })
                            .catch(err => {
                                console.error('Error adding pattern:', err);
                                span.style.backgroundColor = 'red';
                            });
                        });

                        pageDiv.appendChild(span);
                    });

                    pagesContainer.appendChild(pageDiv);
                });

                resultsDiv.appendChild(pagesContainer);
            }

        } catch (err) {
            resultsDiv.innerHTML = `<p style="color:red;">Request failed: ${err.message}</p>`;
        } finally {
            button.disabled = false;
            button.textContent = 'Analyze';
        }
    });
});