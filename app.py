from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import uuid
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'summer-fun-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    session['name'] = request.form.get('name')
    room_id = str(uuid.uuid4())[:8]
    session['room'] = room_id
    rooms[room_id] = {
        'players': [],
        'started': False,
        'hands': {},
        'turn_index': 0
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
    if room not in rooms: return redirect(url_for('index'))
    return render_template('lobby.html', room=room)

@app.route('/game/<room>')
def game(room):
    if room not in rooms or 'name' not in session: return redirect(url_for('index'))
    return render_template('game.html', room=room)

@socketio.on('join_room')
def on_join(data):
    room, name = data['room'], data['name']
    if room not in rooms: return
    
    join_room(room)
    player_id = request.sid

    # RECONNECTION LOGIC: Check if player already exists in the room
    existing_player = next((p for p in rooms[room]['players'] if p['name'] == name), None)

    if existing_player:
        old_id = existing_player['id']
        existing_player['id'] = player_id
        if old_id in rooms[room]['hands']:
            rooms[room]['hands'][player_id] = rooms[room]['hands'].pop(old_id)
    else:
        rooms[room]['players'].append({'id': player_id, 'name': name})

    emit('update_players', {'players': [p['name'] for p in rooms[room]['players']]}, to=room)

    # Push state to reconnected player
    if rooms[room]['started'] and player_id in rooms[room]['hands']:
        emit('update_hand', {
            'hand': rooms[room]['hands'][player_id],
            'current_turn': rooms[room]['players'][rooms[room]['turn_index']]['name']
        }, to=player_id)

@socketio.on('start_game')
def on_start_game(data):
    room = data['room']
    if room not in rooms or len(rooms[room]['players']) < 2:
        emit('error', {'message': 'Need at least 2 players'}, to=request.sid)
        return
    
    # DYNAMIC DECK SCALING
    num_players = len(rooms[room]['players'])
    game_letters = list(string.ascii_uppercase)[:num_players]
    deck = []
    for char in game_letters: deck.extend([char] * 4)
    random.shuffle(deck)
    
    for i, player in enumerate(rooms[room]['players']):
        rooms[room]['hands'][player['id']] = deck[i*4:(i+1)*4]
    
    rooms[room]['started'] = True
    rooms[room]['turn_index'] = 0
    emit('game_started', to=room)
    
    for player in rooms[room]['players']:
        emit('update_hand', {
            'hand': rooms[room]['hands'][player['id']],
            'current_turn': rooms[room]['players'][0]['name']
        }, to=player['id'])

@socketio.on('pass_card')
def on_pass_card(data):
    room, card = data['room'], data['card']
    if room not in rooms: return
    
    players = rooms[room]['players']
    curr_idx = rooms[room]['turn_index']
    
    # Validation
    if request.sid != players[curr_idx]['id']: return
    if card not in rooms[room]['hands'][request.sid]: return

    # Move logic
    rooms[room]['hands'][request.sid].remove(card)
    next_idx = (curr_idx + 1) % len(players)
    rooms[room]['hands'][players[next_idx]['id']].append(card)
    rooms[room]['turn_index'] = next_idx

    # Win Check
    winner = None
    for p in players:
        hand = rooms[room]['hands'].get(p['id'], [])
        if any(hand.count(letter) == 4 for letter in set(hand)):
            winner = p['name']
            break

    # Broadcast updates
    for p in players:
        emit('update_hand', {
            'hand': rooms[room]['hands'][p['id']],
            'current_turn': players[rooms[room]['turn_index']]['name'],
            'winner': winner
        }, to=p['id'])

    if winner:
        # Simplified ranking: sorting by max matches
        ranks = []
        for p in players:
            h = rooms[room]['hands'][p['id']]
            max_m = max([h.count(l) for l in set(h)]) if h else 0
            ranks.append({'name': p['name'], 'matches': max_m})
        ranks.sort(key=lambda x: x['matches'], reverse=True)
        emit('game_over', {'rankings': ranks}, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)