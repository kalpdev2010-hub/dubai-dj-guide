document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("gear-container");
    if (!container) return; 

    const targetCategory = container.getAttribute("data-category");

    fetch("dj_gear.json")
        .then(response => response.json())
        .then(data => {
            const categoryData = data.find(cat => cat.categoryId === targetCategory);
            if (!categoryData) return;

            // 1. Create the Filter Navigation at the top
            const filterNav = document.createElement('div');
            filterNav.className = 'filter-nav';
            filterNav.style.cssText = "display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 2rem; justify-content: center;";
            
            const allBtn = document.createElement('button');
            allBtn.className = 'filter-btn active';
            allBtn.innerText = 'All Gear';
            filterNav.appendChild(allBtn);
            container.appendChild(filterNav);

            const sectionsArray = [];

            // 2. Build the Sections
            categoryData.tiers.forEach((tier, index) => {
                const section = document.createElement("section");
                section.dataset.filter = 'tier-' + index;
                
                const tierTitle = document.createElement("h2");
                tierTitle.textContent = tier.tierName;
                section.appendChild(tierTitle);

                // FIX: Add the "grid" class here so cards sit side-by-side on desktop
                const gridDiv = document.createElement("div");
                gridDiv.className = "grid"; 

                tier.items.forEach(item => {
                    const card = document.createElement("div");
                    card.className = "card"; 

                    card.innerHTML = `
                        <span class="tagline" style="background: #ffcc00; color: #121212; padding: 5px 15px; font-size: 0.8rem; border-radius: 50px; margin-bottom: 15px; font-weight: bold; align-self: flex-start;">${item.badge}</span>
                        <span class="brand" style="color: #ffcc00; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; margin-bottom: 15px; display: block;">${item.brand}</span>
                        <h3 style="margin: 0 0 10px 0; font-size: 1.4rem;">${item.model}</h3>
                        <p style="color: #cccccc; font-size: 0.95rem; flex-grow: 1;">${item.description}</p>
                        <a href="https://www.amazon.ae/s?k=${encodeURIComponent(item.searchQuery)}&tag=dubaicinema-21" 
                           target="_blank" class="btn-amazon" 
                           style="margin-top: 20px; padding: 12px 25px; background-color: #28a745; color: #fff; text-decoration: none; font-weight: bold; border-radius: 50px; text-align: center; display: block;">
                           Check Amazon UAE
                        </a>
                    `;
                    gridDiv.appendChild(card);
                });

                section.appendChild(gridDiv);
                container.appendChild(section);
                sectionsArray.push(section);

                // Add Button to Filter Nav
                const btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.innerText = tier.tierName.replace(/^\d+\.\s*/, ''); 
                btn.onclick = () => {
                    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    sectionsArray.forEach(sec => {
                        sec.style.display = (sec === section) ? 'block' : 'none';
                    });
                };
                filterNav.appendChild(btn);
            });

            // All Gear Button Logic
            allBtn.onclick = () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                allBtn.classList.add('active');
                sectionsArray.forEach(sec => sec.style.display = 'block');
            };
        })
        .catch(error => console.error("Vault connection failed:", error));
});
