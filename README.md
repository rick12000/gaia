# GAIA - Voice Command Assistant

GAIA allows you to control your computer using voice commands. Speak the commands listed below to perform various actions.

## Getting Started

1.  **Dependencies:** Ensure you have Python and the necessary libraries installed (e.g., `vosk`, `sounddevice`, `pyautogui`, `pyperclip`). You might use a `requirements.txt` file (not provided here) and `pip install -r requirements.txt`.
2.  **Vosk Model:** Download a Vosk speech recognition model (e.g., `vosk-model-small-en-us-0.15` is recommended for a balance of performance and accuracy). Unzip it and place the model folder (e.g., `vosk-model-small-en-us-0.15`) inside the GAIA project directory. The `.gitignore` file is set up to ignore folders matching `vosk-model-*`.
3.  **Configuration:** Spot locations are saved in `spots.json` (ignored by git). Some command names might be protected (defined in `config.py`, if present).
4.  **Run:** Execute the main Python script for GAIA.

## Available Commands

Commands are generally spoken in lowercase. `<parameter>` indicates where you need to substitute a value (like a number or a spot name).

### Dictation Mode

Toggle a mode where your speech is typed out directly.

*   **`start dictation`**: Activates dictation mode. Spoken words will be typed out.
*   **`stop dictation`**: Deactivates dictation mode and pastes any remaining buffered text.

### Navigation & Mouse Control

Control the mouse pointer, perform clicks, and navigate using arrow keys or page keys.

*   **`<spot_name>`**: Moves the mouse to the saved spot and clicks. (e.g., "`address bar`")
*   **`double click <spot_name>`**: Moves to the spot and double-clicks.
*   **`click`** / **`left click`**: Performs a left mouse click at the current cursor position.
*   **`right click`**: Performs a right mouse click.
*   **`double click`**: Performs a double left click.
*   **`triple click`**: Performs a triple left click.
*   **`<number> up`** / **`<number> down`**: Presses the up/down arrow key `<number>` times (1-100). Add "`enter`" at the end to press Enter afterwards (e.g., "`five down enter`").
*   **`left`**: Presses the left arrow key.
*   **`right`**: Presses the right arrow key.
*   **`p up`**: Presses the Page Up key.
*   **`p down`**: Presses the Page Down key.
*   **`press down`**: Holds the down arrow key. Use "`stop`" to release.
*   **`press up`**: Holds the up arrow key. Use "`stop`" to release.
*   **`press left`**: Holds the left arrow key. Use "`stop`" to release.
*   **`press right`**: Holds the right arrow key. Use "`stop`" to release.
*   **`press page down`**: Holds the Page Down key (simulates slow scroll). Use "`stop`" to release.
*   **`press page up`**: Holds the Page Up key (simulates slow scroll). Use "`stop`" to release.
*   **`previous`**: Navigates back (simulates Alt + Left).
*   **`next`**: Navigates forward (simulates Alt + Right).
*   **`search bar`**: Activates the browser's address/search bar (simulates Ctrl+L, F6, Ctrl+F).
*   **`goto line <number>`**: In editors like VS Code, goes to the specified line number (simulates Ctrl+G).
*   **`file down`**: Moves the current line/item down (simulates Alt + Down, common in IDEs).
*   **`file up`**: Moves the current line/item up (simulates Alt + Up, common in IDEs).
*   **`next edit`**: Jumps to the next edit location (simulates Alt + F5, common in IDEs).
*   **`previous edit`**: Jumps to the previous edit location (simulates Shift + Alt + F5, common in IDEs).

### Window & Tab Management

Control application windows and browser tabs.

*   **`minimize window`**: Minimizes the active window.
*   **`maximize window`**: Maximizes/restores the active window.
*   **`fullscreen`**: Toggles fullscreen mode for the active window (simulates F11).
*   **`close window`**: Closes the active window (simulates Alt+F4).
*   **`new tab`**: Opens a new browser tab (simulates Ctrl+T).
*   **`close tab`**: Closes the current browser tab (simulates Ctrl+W).
*   **`reopen tab`**: Reopens the last closed browser tab (simulates Ctrl+Shift+T).
*   **`next tab`**: Switches to the next browser tab (simulates Ctrl+Tab).
*   **`previous tab`**: Switches to the previous browser tab (simulates Ctrl+Shift+Tab).
*   **`<next|previous> <number> tabs`**: Switches `<number>` tabs forward or backward (1-10). Add "`enter`" at the end to press Enter afterwards (e.g., "`next three tabs`").

### Editing & Keyboard Actions

Perform common editing tasks and press individual keys.

*   **`stop`**: Releases any currently held key (like arrow keys or page keys being held by `press ...` commands).
*   **`faster`**: Increases the repeat speed for held keys.
*   **`slower`**: Decreases the repeat speed for held keys.
*   **`enter`**: Presses the Enter key.
*   **`delete`**: Presses the Delete key.
*   **`escape`**: Presses the Escape key.
*   **`tab`**: Presses the Tab key.
*   **`space`**: Presses the Space key.
*   **`save`**: Saves the current file (simulates Ctrl+S).
*   **`copy`**: Copies selected text/item (simulates Ctrl+C).
*   **`paste`**: Pastes content from the clipboard (simulates Ctrl+V).
*   **`select all`**: Selects all content (simulates Ctrl+A).
*   **`undo`**: Undoes the last action (simulates Ctrl+Z).
*   **`redo`**: Redoes the last undone action (simulates Ctrl+Shift+Z).
*   **`zoom`**: Zooms in (simulates Ctrl + Plus).
*   **`zoom out`**: Zooms out (simulates Ctrl + Minus).
*   **`select from`**: Holds Shift and presses Down arrow repeatedly. Use "`stop`" to release.
*   **`select until`**: Holds Shift and presses Up arrow repeatedly. Use "`stop`" to release.
*   **`look for <text>`**: Opens the find dialog (simulates Ctrl+F) and pastes `<text>` into it.
*   **`type <text>`**: Pastes `<text>` directly using the clipboard.

### Application Specific

These commands often trigger shortcuts specific to certain applications (like VS Code).

*   **`mode`**: Toggles specific mode (simulates Ctrl + .). (e.g., VS Code Copilot Chat context)
*   **`microphone`**: Toggles microphone (simulates Alt + N). (Application specific)
*   **`context`**: Shows context menu (simulates Ctrl + /). (Application specific)
*   **`save all code`**: Saves all open files (simulates Ctrl+K, S). (Primarily for VS Code)

### Spot Management (Mouse Position Bookmarks)

Save and recall specific mouse cursor positions on the screen. Spots are saved in `spots.json`.

*   **`mark <name>`**: Saves the current mouse cursor position with the given `<name>`. Avoid protected names (defined in `config.py`).
*   **`mark delete <name>`** / **`unmark <name>`**: Deletes the spot with the given `<name>`.
*   **`list spots`**: Prints the names of all saved spots to the console.
*   **`reset spots`**: Deletes all saved spots (requires confirmation via `yes`/`no`).
*   **`visualize marks`**: Briefly shows visual indicators for all saved spots on the screen.

### System & Utility

General system-level actions.

*   **`screenshot`**: Opens the OS's screen capture tool (simulates Win + Shift + S on Windows).
*   **`exit`** / **`quit`**: Stops the GAIA application.

### Confirmation

Respond to prompts from GAIA.

*   **`yes`**: Confirms a pending action (e.g., `reset spots`).
*   **`no`**: Cancels a pending action.
