document.addEventListener('DOMContentLoaded', () => {
    const scrapeBtn = document.getElementById('scrape-btn');
    const categoryInput = document.getElementById('category');
    const locationInput = document.getElementById('location');
    const limitInput = document.getElementById('limit');
    const loader = document.getElementById('loader');
    const resultsSection = document.getElementById('results-section');
    const resultsBody = document.getElementById('results-body');
    const countSpan = document.getElementById('count');

    scrapeBtn.addEventListener('click', async () => {
        const category = categoryInput.value.trim();
        const location = locationInput.value.trim();
        const limit = limitInput.value;

        if (!category || !location) {
            alert('Please enter both category and location!');
            return;
        }

        // UI State: Loading
        scrapeBtn.disabled = true;
        loader.style.display = 'flex';
        resultsSection.style.display = 'none';
        resultsBody.innerHTML = '';

        try {
            const response = await fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ category, location, limit })
            });

            const result = await response.json();

            if (result.status === 'success') {
                renderResults(result.data);
            } else {
                alert('Error: ' + (result.message || 'Unknown error occurred'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during extraction.');
        } finally {
            scrapeBtn.disabled = false;
            loader.style.display = 'none';
        }
    });

    function renderResults(data) {
        if (data.length === 0) {
            resultsBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem;">No results found.</td></tr>';
        } else {
            data.forEach(item => {
                const row = document.createElement('tr');
                const isValid = item.wa_status === 'Valid';
                const waClass = isValid ? 'status-active' : 'status-inactive';
                const waIcon = isValid ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-times-circle"></i>';
                
                row.innerHTML = `
                    <td>${item.id}</td>
                    <td style="font-weight: 600; color: var(--primary);">${item.nama}</td>
                    <td>${item.alamat}</td>
                    <td><span class="phone-badge">${item.telepon}</span></td>
                    <td><span class="status-badge ${waClass}">${waIcon} ${item.wa_status}</span></td>
                `;
                resultsBody.appendChild(row);
            });
        }
        
        countSpan.innerText = data.length;
        resultsSection.style.display = 'block';
    }
});
