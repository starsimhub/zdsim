# Getting your environment ready: Windows Users

## Step 1: Install Visual Studio Code

**Instructions:**

1. **Download VS Code:**
   - Navigate to the [official VS Code download page](https://code.visualstudio.com/Download).
   - Click on the Windows download button to get the installer.

2. **Run the Installer:**
   - Locate the downloaded `VSCodeSetup.exe` file and double-click to run it.

3. **Follow the Setup Wizard:**
   - Accept the license agreement.
   - Choose the installation location or leave it as default.
   - **Important:** On the "Select Additional Tasks" screen, ensure you check:
     - `Add to PATH` (allows you to open VS Code from the Command Prompt)
     - `Register Code as an editor for supported file types`
     - `Add "Open with Code" action to Windows Explorer file context menu`
   - Proceed with the installation.

4. **Launch VS Code:**
   - Once installed, open VS Code to ensure it's working correctly.

---

## Step 2: Install Git


**Instructions:**

1. **Download Git:**
   - Visit the [official Git website](https://git-scm.com/download/win).
   - The download should start automatically for Windows.

2. **Run the Installer:**
   - Open the downloaded `Git-*.exe` file.

3. **Follow the Setup Wizard:**
   - Use the default settings unless you have specific preferences.
   - Ensure that the option to add Git to your system PATH is selected.

4. **Verify Installation:**
   - Open the Command Prompt:
     - Press `Windows + R`, type `cmd`, and press Enter.
   - In the terminal, type:
     ```bash
     git --version
     ```
     - You should see the installed Git version displayed.

---

## Step 3: Install Python 3.12

**Instructions:**

1. **Download Python:**
   - Go to the [official Python website](https://www.python.org/downloads/).
   - Click on the latest Python 3.12 version for Windows to download the installer.

2. **Run the Installer:**
   - Open the downloaded `python-3.12.*.exe` file.

3. **Follow the Setup Wizard:**
   - **Important:** Before clicking "Install Now," check the box that says:
     - `Add Python 3.12 to PATH`
   - Click on "Install Now" to proceed.

4. **Verify Installation:**
   - Open the Command Prompt.
   - Type:
     ```bash
     python --version
     pip --version
     ```
     - Both commands should display the installed versions of Python and pip.

---

## Step 4: Clone the `zdsim` GitHub Repository

Cloning the repository downloads the project's source code to your local machine, allowing you to work on it. 
**Instructions:**

1. **Open Command Prompt:**
   - Press `Windows + R`, type `cmd`, and press Enter.

2. **Navigate to Your Desired Directory:**
   - For example, to go to your Documents folder:
     ```bash
     cd C:\Users\YourName\Documents
     ```

3. **Clone the Repository:**
   - Run:
     ```bash
     git clone https://github.com/starsimhub/zdsim.git
     ```

4. **Navigate into the Project Folder:**
   - Run:
     ```bash
     cd zdsim
     ```

---

## Step 5: Create a Virtual Environment

**Why?**  
A virtual environment isolates your project's dependencies, preventing conflicts with other Python projects on your system.

**Instructions:**

1. **Create the Virtual Environment:**
   - In the `zdsim` directory, run:
     ```bash
     python -m venv venv
     ```
   - This creates a new folder named `venv` containing the virtual environment.

---

## Step 6: Activate the Virtual Environment

**Why?**  
Activating the virtual environment ensures that any Python packages you install are contained within this environment.

**Instructions:**

1. **Activate the Environment:**
   - Run:
     ```bash
     venv\Scripts\activate.bat
     ```
   - After activation, your command prompt will show `(venv)` at the beginning, indicating that the virtual environment is active.

---

## Step 7: Install the Project in Editable Mode

**Why?**  
Installing the project in editable mode allows you to make changes to the source code and have them reflected immediately without reinstalling the package.

**Instructions:**

1. **Ensure the Virtual Environment is Active:**
   - Your command prompt should display `(venv)`.

2. **Install the Project:**
   - Run:
     ```bash
     pip install -e .
     ```
   - This command tells pip to install the current directory (`.`) in editable mode.

---

## Step 8: Open the Project in Visual Studio Code

**Why?**  
Opening the project in VS Code provides a user-friendly interface for editing, running, and debugging your code.

**Instructions:**

1. **Launch VS Code from the Project Directory:**
   - In the command prompt, run:
     ```bash
     code .
     ```
   - This opens the current folder in VS Code.

2. **Select the Python Interpreter:**
   - In VS Code, press `Ctrl + Shift + P` to open the Command Palette.
   - Type and select `Python: Select Interpreter`.
   - Choose the interpreter located at `.\venv\Scripts\python.exe`.

3. **Install Recommended Extensions:**
   - If prompted, install the Python extension for VS Code to enhance your development experience.

---

## You're All Set!

You now have a fully functional Python development environment set up on your Windows machine, ready for working on the `zdsim` project. Happy coding!

---

**Note:** For a visual walkthrough with screenshots, please refer to the following resources:

- [Visual Studio Code Setup Guide](https://code.visualstudio.com/docs/setup/setup-overview)
- [Python Virtual Environments in VS Code](https://code.visualstudio.com/docs/python/environments)


Questions?
Please let me know: Minerva.
