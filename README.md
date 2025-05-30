# Alphabet Matching Game

A real-time multiplayer card game where players compete to collect all four cards of the same letter. Perfect for summer fun with friends, this web-based game allows players to join from different locations.

---

## Game Overview

**Objective:** Be the first player to collect all four cards of the same alphabet letter (e.g., all A's, all B's, or all C's).

**Players:** 2-3 players (can be expanded for more)

---

**Game Flow:**
1. Players join a shared room using a unique code
2. Each player receives 4 random cards
3. On their turn, players pass a card they don't want to the next player
4. Play continues until someone collects 4 matching cards

---

## Features

- **Real-time Multiplayer:** Play with friends from anywhere
- **Unique Room Codes:** Easily create and join private game rooms
- **Responsive Design:** Works on desktop and mobile devices
- **Visual Card Interface:** Intuitive drag-and-drop card selection
- **Automatic Scoring:** Tracks player rankings at game end

---
## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python with Flask
- **Real-time Communication:** Socket.IO
- **Deployment:** Compatible with Render, PythonAnywhere, and other hosting platforms

---

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/tharunR-17/AlphaGame.git
   cd AlphaGame
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

---

## Deployment

### Deploying to Render

1. Push your code to GitHub
2. Create a new Web Service in Render
3. Connect your GitHub repository
4. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 app:app`

### Deploying to PythonAnywhere

1. Create a PythonAnywhere account
2. Upload your code or clone from GitHub
3. Set up a virtual environment and install dependencies
4. Configure a web app with Flask
5. Set the WSGI configuration file to use your app

---

## How to Play

1. **Create a Game:**
   - Enter your name and click "Create Game"
   - Share the generated room code with friends

2. **Join a Game:**
   - Enter your name and the room code
   - Click "Join Game"

3. **Start the Game:**
   - Once all players have joined, the creator clicks "Start Game"
   - Each player receives 4 random cards

4. **Gameplay:**
   - On your turn, select a card you don't want to pass
   - Try to collect 4 cards of the same letter
   - First player to get 4 matching cards wins!

---

## Game Rules

- Each player aims to collect 4 cards of the same letter
- Players take turns passing one card to the next player
- You can only pass cards on your turn
- The game ends when a player collects 4 matching cards
- Players are ranked based on how many matching cards they have
---

## Proprietary License

This project is proprietary and confidential. All rights reserved.

Unauthorized copying, distribution, modification, public display, or public performance of this software is strictly prohibited.

---

## Acknowledgments

- Inspired by classic card matching games
- Built with Flask and Socket.IO for real-time gameplay
- Special thanks to all contributors and testers

---

## Contact

Feel free to reach out for questions, suggestions, or collaborations!

**Maintainer:** Tharun R

**Email:** [tharunravi71@gmail.com](mailto:tharunravi71@gmail.com)

**LinkedIn:** https://www.linkedin.com/in/tharun-r-a7bba7271
