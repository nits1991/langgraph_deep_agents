from playwright.sync_api import sync_playwright
import json

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Listen for console errors
        def handle_console(msg):
            if msg.type == 'error':
                print(f"Browser Error: {msg.text}")
            else:
                print(f"Browser Log: {msg.text}")
        
        page.on("console", handle_console)
        page.on("pageerror", lambda err: print(f"Page Error: {err.message}"))
        
        page.goto("http://localhost:8000/learned_stuff/json_viewer.html")
        
        test_payload = """[
            {"id": 1, "html_bio": "<b>Bold</b>\\nNew line", "md_bio": "# Header\\nText"}
        ]"""
        
        # Type into input
        page.fill("#input", test_payload)
        page.click("text=Format & Repair")
        
        # Try to click the first Preview button in tree view
        preview_btns = page.locator("button:has-text('Preview')").all()
        print(f"Found {len(preview_btns)} preview buttons in Tree View.")
        if preview_btns:
            print("Clicking first preview button...")
            preview_btns[0].click()
            print("Is modal active?", page.locator("#mdModal").evaluate("el => el.classList.contains('active')"))
        
        # Try in grid view
        page.click("text=Grid View")
        page.wait_for_timeout(500)
        grid_preview_btns = page.locator("button:has-text('View')").all()
        print(f"Found {len(grid_preview_btns)} view buttons in Grid View.")
        if grid_preview_btns:
            print("Clicking first view button in grid...")
            grid_preview_btns[0].click()
            print("Is modal active?", page.locator("#mdModal").evaluate("el => el.classList.contains('active')"))

        browser.close()

if __name__ == "__main__":
    run()
