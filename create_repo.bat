@echo off
echo Setting up GitHub repository for Atlas Data Scraper...

:: Initialize Git repository
git init

:: Create necessary directories if they don't exist
if not exist data\raw mkdir data\raw
if not exist data\processed mkdir data\processed
if not exist logs mkdir logs
if not exist debug mkdir debug

:: Create .gitkeep files to preserve empty directories
type nul > data\raw\.gitkeep
type nul > data\processed\.gitkeep
type nul > logs\.gitkeep
type nul > debug\.gitkeep

:: Add files to Git
git add .

:: Make initial commit
git commit -m "Initial commit: Atlas Data Scraper project"

:: Instructions for connecting to GitHub
echo.
echo Repository initialized locally.
echo.
echo To connect to GitHub, follow these steps:
echo 1. Create a new private repository on GitHub (https://github.com/new)
echo 2. Name it 'atlas-data-scraper' and mark it as Private
echo 3. Do not initialize with README, .gitignore, or license
echo.
echo After creating the repository, run these commands:
echo    git remote add origin https://github.com/YOUR-USERNAME/atlas-data-scraper.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Replace 'YOUR-USERNAME' with your GitHub username.
echo.
pause 