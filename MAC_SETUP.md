# Mac Setup - No Command Line Required!

There are 3 easy ways to run Easy AALM on Mac without using Terminal:

## Option 1: Double-Click the Shell Script (Easiest)

1. After downloading, locate `run.sh` in Finder
2. Right-click on `run.sh` → "Open With" → "Terminal"
3. The first time, you may need to go to System Preferences → Security & Privacy to allow it
4. After the first time, you can just double-click `run.sh`!

## Option 2: Create a Clickable App (Recommended)

1. Open **Automator** (found in Applications/Utilities)
2. Click "New Document"
3. Choose **"Application"** as the type
4. In the search bar on the left, type "Run Shell Script"
5. Drag "Run Shell Script" action to the right panel
6. Replace the text with:
   ```bash
   cd "$HOME/Downloads/easy-aalm"
   source venv/bin/activate
   streamlit run app.py
   ```
   (Adjust the path if you put easy-aalm somewhere else)

7. File → Save → Save to Desktop as "Easy AALM"
8. Now you have a double-clickable app on your Desktop!

## Option 3: Create an Alfred/Spotlight Command

1. Follow Option 2 to create the Automator app
2. Move "Easy AALM.app" to your Applications folder
3. Now you can launch it with Spotlight:
   - Press Cmd+Space
   - Type "Easy AALM"
   - Press Enter

## After Setup

No matter which option you choose, the app will:
- Open Terminal automatically
- Start the Easy AALM web server
- Open your browser to http://localhost:8501

To stop the app, just close the Terminal window.

## Troubleshooting

**"Permission denied" error:**
- Run setup.sh first by right-clicking → Open With → Terminal
- Or run: `chmod +x run.sh` in Terminal

**"Python not found":**
- Install Python from python.org
- Or use Homebrew: `brew install python3`

**"Wine not found":**
- Install Wine: `brew install --cask wine-stable`
- Or use the Windows AALM executable path if Wine doesn't work
