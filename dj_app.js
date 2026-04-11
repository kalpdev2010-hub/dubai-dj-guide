document.addEventListener("DOMContentLoaded", () => {
    // 1. Find the empty container on whatever page the user is looking at
    const container = document.getElementById("gear-container");
    if (!container) return; 

    // 2. Read the secret tag (e.g., "turntables" or "mixers")
    const targetCategory = container.getAttribute("data-category");

    // 3. Open the DJ Vault
    fetch("dj_gear.json")
        .then(response => response.json())
        .then(data => {
            // Find only the gear for this specific page
            const categoryData = data.find(cat => cat.categoryId === targetCategory);
            
            if (!categoryData) {
                console.warn("No gear found for this category.");
                return;
            }

            // 4. Build the page dynamically!
            categoryData.tiers.forEach(tier => {
                
                // Create the Section Title (e.g., "Direct Drive Turntables")
                const section = document.createElement("section");
                section.className = "category-section";
                
                const tierTitle = document.createElement("h2");
                tierTitle.textContent = tier.tierName;
                section.appendChild(tierTitle);

                // Create a Card for each piece of gear
                tier.items.forEach(item => {
                    const card = document.createElement("div");
                    card.className = "card"; 
                    // Fallback styles to ensure it looks good immediately
                    card.style.cssText = "background: #1a1a1a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #333;";

                    const badge = document.createElement("span");
                    badge.style.cssText = "background: #ffcc00; color: #121212; padding: 4px 10px; font-size: 0.8rem; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 12px;";
                    badge.textContent = item.badge;

                    const title = document.createElement("h3");
                    title.style.cssText = "color: #ffffff; margin-top: 0;";
                    title.textContent = `${item.brand} ${item.model}`;

                    const desc = document.createElement("p");
                    desc.style.cssText = "color: #cccccc;";
                    desc.textContent = item.description;

                    const btn = document.createElement("a");
                    // Automatically generates the safe Amazon UAE search link
                    btn.href = `https://www.amazon.ae/s?k=${encodeURIComponent(item.searchQuery)}`;
                    btn.target = "_blank";
                    btn.style.cssText = "display: inline-block; background: #28a745; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 15px; transition: 0.2s;";
                    btn.textContent = "Check Amazon UAE";

                    card.append(badge, title, desc, btn);
                    section.appendChild(card);
                });

                container.appendChild(section);
            });
        })
        .catch(error => console.error("Vault connection failed:", error));
});
