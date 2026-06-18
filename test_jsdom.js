const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const html = fs.readFileSync('/Users/nitinaggarwal/Documents/learning/langgraph_deep_agents/learned_stuff/json_viewer.html', 'utf8');

const dom = new JSDOM(html, { runScripts: "dangerously", resources: "usable" });
const window = dom.window;
const document = window.document;

window.onload = () => {
    try {
        const input = document.getElementById('input');
        input.value = `[
            {"id": 1, "html_bio": "<b>Bold</b>\\nNew line", "md_bio": "# Header\\nText"}
        ]`;
        
        // Mock DOMPurify and marked
        window.DOMPurify = { sanitize: (text) => text };
        window.marked = { parse: (text) => text };
        window.JSON5 = require('json5'); // We'll need to install json5 or mock it

        // Call formatJSON
        window.formatJSON();
        
        console.log("Tree innerHTML length:", document.getElementById('output').innerHTML.length);
        
        // Find buttons
        const buttons = document.querySelectorAll('.action-btn');
        console.log(`Found ${buttons.length} action buttons.`);
        
        let previewBtn = null;
        buttons.forEach(b => {
            if (b.textContent.includes('Preview')) {
                previewBtn = b;
                console.log("Preview button found with onclick:", b.getAttribute('onclick'));
            }
        });
        
        if (previewBtn) {
            previewBtn.click();
            console.log("Modal active class:", document.getElementById('mdModal').classList.contains('active'));
            console.log("Modal body innerHTML:", document.getElementById('mdBody').innerHTML);
        } else {
            console.log("No Preview buttons generated!");
        }
    } catch (err) {
        console.error("Error during test:", err);
    }
};
