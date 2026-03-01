let socket;
let myHand = [];
let isMyTurn = false;
let gameRoom, playerName;

function initGame(room, name) {
    gameRoom = room;
    playerName = name;
    socket = io();

    const overlay = document.getElementById('reconnect-overlay');

    socket.on('connect', () => {
        overlay.classList.add('hidden');
        socket.emit('join_room', {room: gameRoom, name: playerName});
    });

    socket.on('disconnect', () => {
        overlay.classList.remove('hidden');
    });

    socket.on('update_hand', (data) => {
        myHand = data.hand;
        isMyTurn = (data.current_turn === playerName);
        document.getElementById('current-turn').textContent = data.current_turn;
        updateHandDisplay();
        
        const msg = document.getElementById('game-message');
        if (data.winner) {
            msg.textContent = `🎉 ${data.winner} won the game!`;
        } else {
            msg.textContent = isMyTurn ? "🌟 Your turn! Pick a card." : "⏳ Waiting...";
        }
    });

    socket.on('game_over', (data) => showGameOver(data.rankings));
}

function updateHandDisplay() {
    const container = document.getElementById('player-hand');
    container.innerHTML = '';
    
    myHand.forEach((card, i) => {
        const div = document.createElement('div');
        div.className = `card letter-${card} ${isMyTurn ? 'selectable' : ''}`;
        div.textContent = card;
        div.id = `card-slot-${i}`;
        
        if (isMyTurn) {
            div.onclick = () => {
                isMyTurn = false; // Prevent double-tap
                div.classList.add('passing');
                setTimeout(() => {
                    socket.emit('pass_card', { room: gameRoom, card: card });
                }, 450);
            };
        }
        container.appendChild(div);
    });
}

// ... include your showGameOver function from the previous version ...

function passCard(card) {
    if (!isMyTurn) return;

    // Visual feedback: disable the cards immediately after clicking
    document.querySelectorAll('.card').forEach(el => el.style.pointerEvents = 'none');
    
    socket.emit('pass_card', {
        room: gameRoom,
        card: card
    });
}

function updateGameMessage() {
    const msg = document.getElementById('game-message');
    msg.textContent = isMyTurn ? "🌟 Your turn! Click a card to pass it." : "⏳ Waiting for the other player...";
}

function showGameOver(rankings) {
    // 1. Hide the game board and show the results screen
    const gameBoard = document.querySelector('.game-board');
    if (gameBoard) gameBoard.classList.add('hidden');
    
    const gameOver = document.getElementById('game-over');
    if (gameOver) gameOver.classList.remove('hidden');
    
    const rankingsContainer = document.getElementById('rankings');
    if (rankingsContainer) {
        rankingsContainer.innerHTML = ''; // Clear old data
        
        // 2. Loop through rankings and build the UI
        rankings.forEach((player, index) => {
            const rankNumber = index + 1; // 1st, 2nd, 3rd...
            const rankItem = document.createElement('div');
            
            // Apply a specific class for the winner (Rank 1)
            rankItem.className = `rank-item rank-${rankNumber}`;
            
            // FIX: Use the 'matches' key from Python and the local rankNumber
            rankItem.innerHTML = `
                <span class="rank-badge">${rankNumber}</span>
                <span class="player-name">${player.name}</span>
                <span class="match-count">${player.matches} matches</span>
            `;
            
            rankingsContainer.appendChild(rankItem);
        });
    }
}

