# My First Project: Beginner Coding Projects and AI Review Application

This repository serves as a versatile learning environment, combining beginner-friendly projects in HTML, CSS, JavaScript, Python, PowerShell, and Jupyter Notebook, with a more advanced Python Flask web application for daily AI code reviews.

## Live Website

This repository is hosted with GitHub Pages:

https://error-cracker-1.github.io/My-First-Project/

The hosted site is served from the `docs` folder, with `docs/index.html` as the entry point, providing links to browser projects and a dashboard for AI review reports.

## Overview

This repository combines learning exercises with a functional web application. It features beginner-friendly HTML, CSS, JavaScript, Python, PowerShell, and Jupyter Notebook projects, alongside a Python Flask web application designed for daily AI code reviews. The GitHub Pages site serves as a landing page for browser projects and an AI review dashboard, while the repository also maintains original project folders and scripting practice files.

## Repository Contents

| Path | Description |
|---|---|
| `.devcontainer/` | Configuration for a development container. |
| `AI_REPORT.md` | Generated AI review reports. |
| `app/applet/` | Files for a daily AI review applet, including `package.json` and `metadata.json`. |
| `docs/` | Static files for GitHub Pages, including the main landing page, dashboard, and hosted browser projects. |
| `docs/Web 1/Web.html` | Hosted copy of the Web 1 page. |
| `docs/Web 1/styles.css` | Stylesheet for the hosted Web 1 page. |
| `docs/dashboard.html` | Hosted dashboard for AI review reports. |
| `docs/index.html` | Main GitHub Pages landing page. |
| `docs/styles.css` | Stylesheet for the GitHub Pages landing page. |
| `Game Pong/Game 1.html` | Original browser-based Pong game file. |
| `Jupyter/Calculator.ipynb` | Jupyter notebook for multifunction and modern scrollable calculators. |
| `Powershell/` | Contains PowerShell practice scripts (`Test 1.ps1`, `Test 2.ps1`, `Test.ps1`). |
| `prompts/` | Text files containing prompts for the AI review system. |
| `Python/` | Contains various Python practice scripts and a Tkinter calculator. |
| `requirements.txt` | Python and Jupyter dependencies for the project. |
| `scripts/` | Backend Python scripts supporting the AI review application. |
| `Web 1/Web.html` | Original Web 1 HTML experiment. |
| `web/` | Python Flask web application for daily AI reviews. |
| `web/static/` | Static assets (CSS, JS) for the Flask application. |
| `web/templates/` | HTML templates for the Flask application. |
| `package.json` | Project manifest for the Daily AI Review web application. |
| `package-lock.json` | Dependency lock file for the web application. |
| `generate_mocks.py` | Script for generating mock data. |
| `metadata.json` | Project metadata file. |

## Featured Projects

### GitHub Pages Landing Page

Path: `docs/index.html`

The landing page serves as the public entry point for the repository. It includes quick links to the Pong game, the Web 1 page, and useful learning resources for HTML, CSS, and JavaScript.

### Pong Game

Paths:

- `docs/index.html` (links to)
- `Game Pong/Game 1.html` (original)

Highlights:

- Runs directly in the browser
- Features a scoreboard and canvas-based gameplay
- Offers difficulty/game controls and sound options
- Uses HTML, CSS, and JavaScript

### Web 1 Page

Paths:

- `docs/Web 1/Web.html` (hosted version)
- `Web 1/Web.html` (original)

Highlights:

- Browser-based HTML, CSS, and JavaScript experiment
- Utilizes a separate CSS file in the hosted `docs/Web 1` version
- Includes visual effects, sound, and on-page controls

### Multifunction & Modern Scrollable Calculators

Paths:

- `Python/MultiFunctional Calculator.py` (Standalone Tkinter application)
- `Jupyter/Calculator.ipynb` (Jupyter notebook)

Highlights:

-   **Classic Scientific Calculator**: Supports addition, subtraction, multiplication, division, powers, and square roots, with full input validation.
-   **Modern Scrollable Calculator**: Features custom deep slate dark and Nord Light themes, dynamic theme toggling, hover effects, and a canvas-based scrollable layout.
-   The notebook version includes both calculator implementations, each with clear usage notes, styled controls, and error handling.

### Daily AI Review Web Application

Path: `web/app.py` (main entry point)
Hosted Dashboard: `docs/dashboard.html`

Highlights:

-   Python Flask-based web application providing a daily AI code review interface.
-   Utilizes an AI model (e.g., Google Gemini) for generating code reviews.
-   Generates AI reports, viewable through the web interface and as `AI_REPORT.md`.
-   Supports review of various file types, driven by configuration in the `prompts/` directory.
-   Includes a dedicated dashboard for visualizing review results.

## Getting Started

### Open the Hosted Site

Visit:

https://error-cracker-1.github.io/My-First-Project/

### Run the HTML Projects Locally

Open these files in your browser:

- `Game Pong/Game 1.html`
- `Web 1/Web.html`
- `docs/index.html`

### Run a Python Script

From the project root:

```bash
python "Python\To Do All Maths Calculations.py"
```

You can replace that filename with any other script in the `Python` folder.

To run the Tkinter multifunction calculator:

```bash
python "Python\MultiFunctional Calculator.py"
```

### Run the Jupyter Notebook

Install the Python dependencies, then start Jupyter:

```bash
pip install -r requirements.txt
jupyter notebook
```

Open `Jupyter/Calculator.ipynb` to run the classic scientific calculator or the modern themed scrollable calculator.

### Run a PowerShell Script

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File "Powershell\Test.ps1"
```

### Run the Daily AI Review Web Application

1.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start the Flask application:**
    ```bash
    npm start
    # or directly:
    PORT=3000 python3 -m web.app
    ```
    Access the application in your browser, typically at `http://localhost:3000`.

## Learning Focus

This repository is useful for practicing:

-   HTML, CSS, and JavaScript
-   Browser-based project structure
-   Beginner game development
-   Python fundamentals
-   Jupyter Notebook experiments
-   PowerShell scripting
-   Publishing a static site with GitHub Pages
-   Python Flask web development
-   Integrating with AI APIs (e.g., Google Gemini)
-   Building web dashboards
-   Containerization with Dev Containers

## Repository Notes

- This is a practice repository; therefore, some files are small exercises rather than complete applications.
- The `docs` folder hosts the public GitHub Pages version of the site, including browser projects and the AI review dashboard.
- The Pong game is currently the most substantial browser project in the repository.
- The Jupyter notebook utilizes Tkinter, meaning that GUI examples should be run in a desktop Python environment.
- The "Daily AI Review" application is a more advanced project compared to the beginner exercises and requires Python dependencies listed in `requirements.txt`.
