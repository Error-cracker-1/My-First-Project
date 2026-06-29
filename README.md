# My First Project: Beginner Coding Projects

A beginner-friendly practice repository for learning HTML, CSS, JavaScript, Python, PowerShell, and Jupyter Notebook through small, runnable projects.

This repository features a published GitHub Pages site, browser projects, Python practice scripts, PowerShell utilities, and Jupyter notebooks, including Tkinter-based applications. The current highlight is a multifunction scientific calculator, available as both a standalone Python Tkinter application and within a Jupyter notebook, offering a graphical interface, input validation, arithmetic operations, powers, square roots, clear controls, and a support link to the project repository.

## Live Website

This repository is hosted with GitHub Pages:

https://error-cracker-1.github.io/My-First-Project/

The hosted site is served from the `docs` folder and starts at `docs/index.html`.

## Overview

This repository contains a mix of learning exercises and small experiments. The current GitHub Pages site provides a landing page with links to the browser projects, while the repository also retains the original project folders and beginner scripting practice files.

## Repository Contents

| Path | Description |
| --- | --- |
| `docs/Game Pong/Game 1.html` | Hosted copy of the Pong game. |
| `docs/google83549bbb7ae16ebb.html` | Google Site Verification file. |
| `docs/index.html` | Main GitHub Pages landing page with links to the hosted projects. |
| `docs/robots.txt` | Robots Exclusion Protocol (REP) file for web crawlers. |
| `docs/sitemap.xml` | XML sitemap for search engine indexing. |
| `docs/styles.css` | Stylesheet for the GitHub Pages landing page. |
| `docs/Web 1/styles.css` | Stylesheet for the hosted Web 1 page. |
| `docs/Web 1/Web.html` | Hosted copy of the Web 1 page. |
| `Game Pong/Game 1.html` | Original browser-based Pong game file. |
| `Jupyter/Calculator.ipynb` | Jupyter notebook featuring a multifunction scientific calculator and a modern scrollable calculator. |
| `Powershell/Test 1.ps1` | Backup script with a number guessing game. |
| `Powershell/Test 2.ps1` | System information dashboard. |
| `Powershell/Test.ps1` | Age-based greeting script. |
| `Python/MultiFunctional Calculator.py` | Tkinter calculator with arithmetic, powers, and square roots. |
| `Python/subtractor.py` | Simple subtractor script. |
| `Python/To Add Three Numbers.py` | Adds three numbers entered by the user. |
| `Python/To Do All Maths Calculations.py` | Basic calculator with add, subtract, multiply, and divide functions. |
| `Python/To Find Area of Rectangle.py` | Rectangle area calculator. |
| `Python/To Find Even And Odd Numbers.py` | Even/odd number checker. |
| `Python/To Find Perimeter Of Rectangle.py` | Rectangle perimeter calculator. |
| `Python/To Multiply Three Numbers.py` | Multiplies three input numbers. |
| `Requirements.txt` | Python and Jupyter dependencies for running the notebook and scripts. |
| `Web 1/Web.html` | Original Web 1 HTML experiment. |

## Featured Projects

### GitHub Pages Landing Page

Path: `docs/index.html`

The landing page acts as the public entry point for the repository. It includes quick links to the Pong game, the Web 1 page, and useful learning resources for HTML, CSS, and JavaScript.

### Pong Game

Paths:

- `docs/Game Pong/Game 1.html`
- `Game Pong/Game 1.html`

Highlights:

- Runs directly in the browser
- Includes a scoreboard and canvas-based gameplay
- Includes difficulty/game controls and sound options
- Uses HTML, CSS, and JavaScript

### Web 1 Page

Paths:

- `docs/Web 1/Web.html`
- `Web 1/Web.html`

Highlights:

- Browser-based HTML, CSS, and JavaScript experiment
- Uses a separated CSS file in the hosted `docs/Web 1` version
- Includes visual effects, sound, and on-page controls

### Multifunction & Modern Scrollable Calculators

Paths:

- `Python/MultiFunctional Calculator.py` (Standalone Tkinter application)
- `Jupyter/Calculator.ipynb` (Jupyter notebook)

Highlights:

- **Classic Scientific Calculator**: Supports addition, subtraction, multiplication, division, powers, and square roots with full validation, including a project support link.
- **Modern Scrollable Calculator**: Features custom deep slate dark and nord light themes, dynamic theme toggling, hover effects, and a canvas-based scrollable layout.
- The notebook version contains both calculator implementations, each with clear usage notes, styled controls, and error handling.

## Getting Started

### Open the Hosted Site

Visit:

https://error-cracker-1.github.io/My-First-Project/

### Run the HTML Projects Locally

Open these files in your browser:

- `docs/index.html`
- `Game Pong/Game 1.html`
- `Web 1/Web.html`

### Run a Python Script

From the project root:

python "Python\To Do All Maths Calculations.py"

You can replace that filename with any other script in the `Python` folder.

To run the Tkinter multifunction calculator:

python "Python\MultiFunctional Calculator.py"

### Run the Jupyter Notebook

Install the Python dependencies, then start Jupyter:

pip install -r Requirements.txt
jupyter notebook

Open `Jupyter/Calculator.ipynb` to run the classic scientific calculator or the modern themed scrollable calculator.

### Run a PowerShell Script

From the project root:

powershell -ExecutionPolicy Bypass -File "Powershell\Test.ps1"

## Recent Updates

- Deleted `Jupyter/Test.ipynb`.
- Added the Modern Scrollable Calculator cell to `Jupyter/Calculator.ipynb`, featuring custom dark/light themes, dynamic theme switching, and scrollbar support.
- Updated package dependencies in `Requirements.txt`.
- Added a title and detailed description to `Jupyter/Calculator.ipynb`.
- Improved the notebook calculator layout with styled controls, a clear button, and usage notes.
- Updated `README.md` with a stronger project description and calculator documentation.
- Introduced `Python/MultiFunctional Calculator.py` and `Jupyter/Calculator.ipynb` with a Tkinter multifunction calculator.
- Updated `Jupyter/Test.ipynb` to show GUI message boxes for welcome and guessing-game feedback.
- Added `Jupyter/Test.ipynb` with Tkinter practice applications.
- Expanded `Requirements.txt` with Jupyter Notebook, JupyterLab, widgets, and server dependencies.
- Created a `docs` folder for GitHub Pages hosting.
- Added `docs/index.html` as a clean landing page for project links.
- Separated CSS for hosted pages where needed.
- Added distinct favicons to website pages.
- Retained original project folders alongside the hosted `docs` copies.

## Learning Focus

This repository is useful for practicing:

- HTML, CSS, and JavaScript
- browser-based project structure
- beginner game development
- Python fundamentals
- Jupyter Notebook experiments
- PowerShell scripting
- publishing a static site with GitHub Pages

## Repository Notes

- This is a practice repository; therefore, some files are small exercises rather than complete applications.
- The `docs` folder hosts the public GitHub Pages version of the site.
- The Pong game is currently the most substantial browser project in the repository.
- The Jupyter notebook utilizes Tkinter, meaning GUI examples should be run in a desktop Python environment.

## Future Improvements

Possible next steps for this repo:

- add screenshots or GIFs for the Pong game and website pages
- keep the original and `docs` versions in sync
- add short descriptions for each Python and PowerShell script
- add more markdown notes inside the Jupyter notebook
- move more shared styling into separate CSS files