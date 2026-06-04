# My First Project: Beginner Coding Projects

A beginner-friendly practice repository for learning HTML, CSS, JavaScript, Python, PowerShell, and Jupyter Notebook through small, runnable projects.

The repository includes a published GitHub Pages site, browser projects, Python practice scripts, PowerShell utilities, and Tkinter-based Jupyter notebooks. The current featured notebook is a multifunction scientific calculator with a graphical interface, input validation, arithmetic operations, powers, square roots, clear controls, and a support link to the project repository.

## Live Website

This repository is hosted with GitHub Pages:

[https://error-cracker-1.github.io/My-First-Project/](https://error-cracker-1.github.io/My-First-Project/)

The hosted site is served from the `docs` folder and starts at `docs/index.html`.

## Overview

This repo contains a mix of learning exercises and small experiments. The current GitHub Pages site provides one landing page with links to the browser projects, while the repository also keeps the original project folders and beginner scripting practice files.

## Current Structure

| Path | Description |
| --- | --- |
| `docs/index.html` | Main GitHub Pages landing page with links to the hosted projects. |
| `docs/styles.css` | Stylesheet for the GitHub Pages landing page. |
| `docs/Game Pong/Game 1.html` | Hosted copy of the Pong game. |
| `docs/Web 1/Web.html` | Hosted copy of the Web 1 page. |
| `docs/Web 1/styles.css` | Stylesheet for the hosted Web 1 page. |
| `Game Pong/Game 1.html` | Original browser-based Pong game file. |
| `Web 1/Web.html` | Original Web 1 HTML experiment. |
| `Python/subtractor.py` | Simple subtractor script. |
| `Python/MultiFunctional Calculator.py` | Tkinter calculator with arithmetic, powers, and square roots. |
| `Python/To Add Three Numbers.py` | Adds three numbers entered by the user. |
| `Python/To Do All Maths Calculations.py` | Basic calculator with add, subtract, multiply, and divide functions. |
| `Python/To Find Area of Rectangle.py` | Rectangle area calculator. |
| `Python/To Find Even And Odd Numbers.py` | Even/odd number checker. |
| `Python/To Find Perimeter Of Rectangle.py` | Rectangle perimeter calculator. |
| `Python/To Multiply Three Numbers.py` | Multiplies three input numbers. |
| `Jupyter/Calculator.ipynb` | Jupyter notebook version of the Tkinter multifunction scientific calculator with a title, usage notes, styled controls, and validation. |
| `Jupyter/Test.ipynb` | Jupyter notebook with Tkinter practice apps for launching the site, calculating square roots, and guessing numbers. |
| `Requirements.txt` | Python and Jupyter dependencies for running the notebook and scripts. |
| `Powershell/Test.ps1` | Age-based greeting script. |
| `Powershell/Test 1.ps1` | Backup script with a number guessing game. |
| `Powershell/Test 2.ps1` | System information dashboard. |

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

### Jupyter Notebook Practice

Path: `Jupyter/Test.ipynb`

Highlights:

- Includes small Tkinter GUI examples
- Opens the hosted project website from a desktop app button
- Demonstrates a square-root calculator with input validation
- Includes a simple number guessing game
- Uses message boxes for GUI feedback in the welcome and guessing examples

### Multifunction Calculator

Paths:

- `Python/MultiFunctional Calculator.py`
- `Jupyter/Calculator.ipynb`

Highlights:

- Tkinter desktop calculator interface
- Supports addition, subtraction, multiplication, division, powers, and square roots
- Includes validation for invalid numbers, division by zero, and negative square roots
- The notebook version includes a clear title, usage description, feature list, input notes, styled operation buttons, and a clear button

## Getting Started

### Open the Hosted Site

Visit:

[https://error-cracker-1.github.io/My-First-Project/](https://error-cracker-1.github.io/My-First-Project/)

### Run the HTML Projects Locally

Open these files in your browser:

- `docs/index.html`
- `Game Pong/Game 1.html`
- `Web 1/Web.html`

### Run a Python Script

From the project root:

```powershell
python "Python\To Do All Maths Calculations.py"
```

You can replace that filename with any other script in the `Python` folder.

To run the Tkinter multifunction calculator:

```powershell
python "Python\MultiFunctional Calculator.py"
```

### Run the Jupyter Notebook

Install the Python dependencies, then start Jupyter:

```powershell
pip install -r Requirements.txt
jupyter notebook
```

Open `Jupyter/Calculator.ipynb` for the multifunction calculator or `Jupyter/Test.ipynb` for the practice apps.

### Run a PowerShell Script

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File "Powershell\Test.ps1"
```

## Python Practice Scripts

- `Python/subtractor.py` — subtracts two numbers from user input.
- `Python/MultiFunctional Calculator.py` — Tkinter calculator for arithmetic operations, powers, and square roots.
- `Python/To Add Three Numbers.py` — adds three numbers entered by the user.
- `Python/To Do All Maths Calculations.py` — basic calculator that adds, subtracts, multiplies, and divides two numbers.
- `Python/To Find Area of Rectangle.py` — calculates the area of a rectangle.
- `Python/To Find Even And Odd Numbers.py` — checks whether a number is even or odd.
- `Python/To Find Perimeter Of Rectangle.py` — calculates the perimeter of a rectangle.
- `Python/To Multiply Three Numbers.py` — multiplies three numbers entered by the user.

## PowerShell Practice Scripts

- `Powershell/Test.ps1` — prompts for name and age, then indicates if the user is an adult or minor.
- `Powershell/Test 1.ps1` — copies a folder to a backup location and includes a small number guessing game.
- `Powershell/Test 2.ps1` — displays system information, disk usage, network adapter details, BIOS version, and recent Windows updates.

## Jupyter Practice Notebook

- `Jupyter/Calculator.ipynb` — contains a Tkinter multifunction calculator with arithmetic, power, and square-root operations.
- `Jupyter/Test.ipynb` — contains Tkinter examples for a welcome app, a square-root calculator, and a number guessing game.

## Recent Updates

- Added a title and detailed description to `Jupyter/Calculator.ipynb`.
- Improved the notebook calculator layout with styled controls, a clear button, and usage notes.
- Updated `README.md` with a stronger project description and calculator documentation.
- Added `Python/MultiFunctional Calculator.py` and `Jupyter/Calculator.ipynb` with a Tkinter multifunction calculator.
- Updated `Jupyter/Test.ipynb` to show GUI message boxes for welcome and guessing-game feedback.
- Added `Jupyter/Test.ipynb` with Tkinter practice apps.
- Expanded `Requirements.txt` with Jupyter Notebook, JupyterLab, widgets, and server dependencies.
- Added a `docs` folder for GitHub Pages hosting.
- Added `docs/index.html` as a clean landing page for project links.
- Separated CSS for the hosted pages where needed.
- Added distinct favicons to website pages.
- Kept original project folders alongside the hosted `docs` copies.

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

- This is a practice repository, so some files are small exercises rather than complete applications.
- The `docs` folder is the public GitHub Pages version of the site.
- The Pong game is the most substantial browser project in the repository.
- The Jupyter notebook uses Tkinter, so GUI examples should be run on a desktop Python environment.

## Future Improvements

Possible next steps for this repo:

- add screenshots or GIFs for the Pong game and website pages
- keep the original and `docs` versions in sync
- add short descriptions for each Python and PowerShell script
- add more markdown notes inside the Jupyter notebook
- move more shared styling into separate CSS files
