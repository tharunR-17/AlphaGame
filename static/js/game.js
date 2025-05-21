let socket;
let myHand = [];
let isMyTurn = false;
let gameRoom;
let playerName;

function initGame(room, name) {
    gameRoom = room;
    playerName = name;
    
    socket = io();
    
    socket.on('connect', () => {
        console.log("Connected to server, joining room:", gameRoom);
        socket.emit('join_room', {room: gameRoom, name: playerName});
    });
    
    socket.on('update_hand', (data) => {
        console.log("Received hand update:", data);
        myHand = data.hand;
        updateHandDisplay();
        
        document.getElementById('current-turn').textContent = data.current_turn;
        isMyTurn = (data.current_turn === playerName);
        
        updateGameMessage();
        
        if (data.winner) {
            document.getElementById('game-message').textContent = `${data.winner} has won the game!`;
        }
    });
    
    socket.on('game_over', (data) => {
        showGameOver(data.rankings);
    });
    
    socket.on('error', (data) => {
        alert(data.message);
    });
}

function updateHandDisplay() {
    const handContainer = document.getElementById('player-hand');
    handContainer.innerHTML = '';
    
    myHand.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        cardElement.textContent = card;
        handContainer.appendChild(cardElement);
    });
    
    // If it's my turn, also update the selectable cards
    if (isMyTurn) {
        document.getElementById('card-selection').classList.remove('hidden');
        updateSelectableCards();
    } else {
        document.getElementById('card-selection').classList.add('hidden');
    }
}

function updateSelectableCards() {
    const selectableContainer = document.getElementById('selectable-cards');
    selectableContainer.innerHTML = '';
    
    // Count occurrences of each letter
    const counts = {};
    myHand.forEach(card => {
        counts[card] = (counts[card] || 0) + 1;
    });
    
    // Find the letter with the most occurrences
    let maxLetter = '';
    let maxCount = 0;
    for (const [letter, count] of Object.entries(counts)) {
        if (count > maxCount) {
            maxCount = count;
            maxLetter = letter;
        }
    }
    
    // Make all cards selectable when it's your turn
    myHand.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card selectable';
        cardElement.textContent = card;
        
        // Add click event to all cards
        cardElement.addEventListener('click', () => {
            console.log("Card clicked:", card);  // Debug log
            passCard(card);
        });
        
        selectableContainer.appendChild(cardElement);
    });
}

function passCard(card) {
    if (!isMyTurn) {
        console.log("Not your turn!");
        return;
    }
    
    console.log("Passing card:", card, "Room:", gameRoom);
    
    socket.emit('pass_card', {
        room: gameRoom,
        card: card
    });
}

function updateGameMessage() {
    const messageElement = document.getElementById('game-message');
    
    if (isMyTurn) {
        messageElement.textContent = "It's your turn! Select a card to pass.";
    } else {
        messageElement.textContent = "Waiting for other player's move...";
    }
}

function showGameOver(rankings) {
    const gameBoard = document.querySelector('.game-board');
    if (gameBoard) gameBoard.classList.add('hidden');
    
    const gameOver = document.getElementById('game-over');
    if (gameOver) gameOver.classList.remove('hidden');
    
    const rankingsContainer = document.getElementById('rankings');
    if (rankingsContainer) {
        rankingsContainer.innerHTML = '';
        
        rankings.forEach(player => {
            const rankItem = document.createElement('div');
            rankItem.className = `rank-item rank-${player.rank}`;
            rankItem.textContent = `${player.rank}. ${player.name} - ${player.matches} matches`;
            rankingsContainer.appendChild(rankItem);
        });
    }
}

