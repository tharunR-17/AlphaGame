from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Game rooms storage
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    session['name'] = request.form.get('name')
    room_id = str(uuid.uuid4())[:8]
    session['room'] = room_id
    
    # Initialize room
    rooms[room_id] = {
        'players': [],
        'started': False,
        'hands': {},
        'turn_index': 0,
        'alphabets': ['A', 'B', 'C']  # Default alphabets
    }
    
    return redirect(url_for('lobby', room=room_id))

@app.route('/join', methods=['POST'])
def join():
    session['name'] = request.form.get('name')
    room_id = request.form.get('room')
    
    if room_id not in rooms:
        return render_template('index.html', error="Room not found")
    
    if rooms[room_id]['started']:
        return render_template('index.html', error="Game already in progress")
        
    session['room'] = room_id
    return redirect(url_for('lobby', room=room_id))

@app.route('/lobby/<room>')
def lobby(room):
    if room not in rooms:
        return redirect(url_for('index'))
    
    return render_template('lobby.html', room=room)

@app.route('/game/<room>')
def game(room):
    if room not in rooms or 'name' not in session:
        return redirect(url_for('index'))
    
    if not rooms[room]['started']:
        return redirect(url_for('lobby', room=room))
        
    return render_template('game.html', room=room)

@socketio.on('join_room')
def on_join(data):
    room = data['room']
    name = data['name']

    if room not in rooms:
        return

    join_room(room)
    player_id = request.sid

    # Look for existing player by name
    existing_player = None
    for p in rooms[room]['players']:
        if p['name'] == name:
            existing_player = p
            break

    if existing_player:
        old_id = existing_player['id']
        existing_player['id'] = player_id
        # Always move hand to new socket id if it exists
        if old_id in rooms[room]['hands']:
            rooms[room]['hands'][player_id] = rooms[room]['hands'].pop(old_id)
    else:
        rooms[room]['players'].append({'id': player_id, 'name': name})

    # Always send hand if game has started and player has a hand
    if rooms[room]['started'] and player_id in rooms[room]['hands']:
        emit('update_hand', {
            'hand': rooms[room]['hands'][player_id],
            'current_turn': rooms[room]['players'][rooms[room]['turn_index']]['name']
        }, to=player_id)

    emit('update_players', {'players': [p['name'] for p in rooms[room]['players']]}, to=room)



@socketio.on('start_game')
def on_start_game(data):
    room = data['room']
    
    if room not in rooms:
        return
    
    # Need at least 2 players to start
    if len(rooms[room]['players']) < 2:
        emit('error', {'message': 'Need at least 2 players'}, to=room)
        return
    
    # Create and shuffle deck
    alphabets = rooms[room]['alphabets'][:len(rooms[room]['players'])]  # One alphabet per player
    deck = []
    for alpha in alphabets:
        deck.extend([alpha] * 4)  # 4 cards of each alphabet
    
    random.shuffle(deck)
    
    # Deal cards to players
    players = rooms[room]['players']
    for i, player in enumerate(players):
        rooms[room]['hands'][player['id']] = deck[i*4:(i+1)*4]
    
    rooms[room]['started'] = True
    rooms[room]['turn_index'] = 0
    
    # Notify all players that the game has started
    emit('game_started', to=room)
    
    # Send initial hands to each player
    for player in players:
        emit('update_hand', {
            'hand': rooms[room]['hands'][player['id']],
            'current_turn': players[rooms[room]['turn_index']]['name']
        }, to=player['id'])

@socketio.on('pass_card')
def on_pass_card(data):
    room = data['room']
    card = data['card']

    print(f"Card pass attempt: {card} in room {room}")

    if room not in rooms:
        print(f"Room {room} not found")
        return

    players = rooms[room]['players']
    current_player_id = request.sid
    current_player_name = None

    for player in players:
        if player['id'] == current_player_id:
            current_player_name = player['name']
            break

    print(f"Current player: {current_player_name} (ID: {current_player_id})")
    print(f"Turn index: {rooms[room]['turn_index']}")
    print(f"Expected player: {players[rooms[room]['turn_index']]['name']}")

    if not current_player_name:
        emit('error', {'message': 'Player not found'}, to=current_player_id)
        return

    current_turn_name = players[rooms[room]['turn_index']]['name']

    if current_player_name != current_turn_name:
        emit('error', {'message': 'Not your turn'}, to=current_player_id)
        return

    # Check hand exists for this player
    if current_player_id not in rooms[room]['hands']:
        emit('error', {'message': 'Hand not found for this player'}, to=current_player_id)
        return

    if card not in rooms[room]['hands'][current_player_id]:
        emit('error', {'message': 'You don\'t have that card'}, to=current_player_id)
        return

    # Remove card from current player
    rooms[room]['hands'][current_player_id].remove(card)

    # Move to next player
    next_turn_index = (rooms[room]['turn_index'] + 1) % len(players)
    next_player_id = players[next_turn_index]['id']

    # Add card to next player
    rooms[room]['hands'][next_player_id].append(card)

    # Update turn
    rooms[room]['turn_index'] = next_turn_index

    print(f"Turn passed to: {players[rooms[room]['turn_index']]['name']}")

    # Check for winner
    winner = None
    rankings = []
    
    for player in players:
        player_id = player['id']
        hand = rooms[room]['hands'][player_id]
        
        # Count occurrences of each letter
        counts = {}
        for letter in hand:
            if letter in counts:
                counts[letter] += 1
            else:
                counts[letter] = 1
        
        max_count = max(counts.values()) if counts else 0
        
        if max_count == 4:  # Player has all 4 of a letter
            winner = player['name']
            break
    
    # Update all players
    for player in players:
        emit('update_hand', {
            'hand': rooms[room]['hands'][player['id']],
            'current_turn': players[rooms[room]['turn_index']]['name'],
            'winner': winner
        }, to=player['id'])
    
    # If game is over, calculate rankings
    if winner:
        # Calculate rankings based on most matched letters
        player_matches = []
        for player in players:
            player_id = player['id']
            hand = rooms[room]['hands'][player_id]
            
            # Count occurrences of each letter
            counts = {}
            for letter in hand:
                if letter in counts:
                    counts[letter] += 1
                else:
                    counts[letter] = 1
            
            max_count = max(counts.values()) if counts else 0
            player_matches.append({
                'name': player['name'],
                'max_matches': max_count
            })
        
        # Sort by max_matches (descending)
        player_matches.sort(key=lambda x: x['max_matches'], reverse=True)
        
        # Assign ranks
        rankings = []
        current_rank = 1
        current_matches = -1
        
        for i, player in enumerate(player_matches):
            if player['max_matches'] != current_matches:
                current_rank = i + 1
                current_matches = player['max_matches']
            
            rankings.append({
                'name': player['name'],
                'rank': current_rank,
                'matches': current_matches
            })
        
        emit('game_over', {'rankings': rankings}, to=room)


if __name__ == '__main__':
    socketio.run(app, debug=False)
