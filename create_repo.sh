#!/bin/bash

# Initialize Git repository
git init

# Create necessary directories if they don't exist
mkdir -p data/raw data/processed logs debug

# Create .gitkeep files to preserve empty directories
touch data/raw/.gitkeep data/processed/.gitkeep logs/.gitkeep debug/.gitkeep

# Add files to Git
git add .

# Make initial commit
git commit -m "Initial commit: Atlas Data Scraper project"

# Instructions for connecting to GitHub
echo "Repository initialized locally."
echo ""
echo "To connect to GitHub, follow these steps:"
echo "1. Create a new private repository on GitHub (https://github.com/new)"
echo "2. Name it 'atlas-data-scraper' and mark it as Private"
echo "3. Do not initialize with README, .gitignore, or license"
echo ""
echo "After creating the repository, run these commands:"
echo "   git remote add origin https://github.com/YOUR-USERNAME/atlas-data-scraper.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Replace 'YOUR-USERNAME' with your GitHub username." 