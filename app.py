from flask import Flask, request, render_template
from time import time
from math import log2
from chess import pgn, Board
from util import to_binary_string, get_pgn_games

app = Flask(__name__)

# Encode function
def encode(input_string: str):
    start_time = time()

    file_bytes = list(input_string.encode('utf-8'))
    file_bits_count = len(file_bytes) * 8

    output_pgns = []
    file_bit_index = 0
    chess_board = Board()

    while True:
        legal_moves = list(chess_board.generate_legal_moves())

        move_bits = {}
        max_binary_length = min(
            int(log2(len(legal_moves))),
            file_bits_count - file_bit_index
        )

        for index, legal_move in enumerate(legal_moves):
            move_binary = to_binary_string(index, max_binary_length)
            if len(move_binary) > max_binary_length:
                break
            move_bits[legal_move.uci()] = move_binary

        closest_byte_index = file_bit_index // 8
        file_chunk_pool = "".join([
            to_binary_string(byte, 8)
            for byte in file_bytes[closest_byte_index: closest_byte_index + 2]
        ])

        next_file_chunk = file_chunk_pool[
            file_bit_index % 8: file_bit_index % 8 + max_binary_length
        ]

        for move_uci in move_bits:
            move_binary = move_bits[move_uci]
            if move_binary == next_file_chunk:
                chess_board.push_uci(move_uci)
                break

        file_bit_index += max_binary_length
        eof_reached = file_bit_index >= file_bits_count

        if (
            chess_board.legal_moves.count() <= 1
            or chess_board.is_insufficient_material()
            or chess_board.can_claim_draw()
            or eof_reached
        ):
            pgn_board = pgn.Game()
            pgn_board.add_line(chess_board.move_stack)
            output_pgns.append(str(pgn_board))
            chess_board.reset()

        if eof_reached:
            break

    #print(f"\nSuccessfully converted string to PGN with {len(output_pgns)} game(s) ({round(time() - start_time, 3)}s).")
    return "\n\n".join(output_pgns)

# Decode function 
def decode(pgn_string: str):
    start_time = time()
    total_move_count = 0
    output_data = ""

    games = get_pgn_games(pgn_string)

    for game_index, game in enumerate(games):
        chess_board = Board()
        game_moves = list(game.mainline_moves())
        total_move_count += len(game_moves)

        for move_index, move in enumerate(game_moves):
            legal_move_ucis = [
                legal_move.uci()
                for legal_move in list(chess_board.generate_legal_moves())
            ]

            move_binary = bin(legal_move_ucis.index(move.uci()))[2:]

            if (
                game_index == len(games) - 1 
                and move_index == len(game_moves) - 1
            ):
                max_binary_length = min(
                    int(log2(len(legal_move_ucis))),
                    8 - (len(output_data) % 8)
                )
            else:
                max_binary_length = int(log2(len(legal_move_ucis)))

            required_padding = max(0, max_binary_length - len(move_binary))
            move_binary = ("0" * required_padding) + move_binary

            chess_board.push_uci(move.uci())
            output_data += move_binary

    byte_array = [
        chr(int(output_data[i * 8: i * 8 + 8], 2))
        for i in range(len(output_data) // 8)
    ]
    decoded_string = "".join(byte_array)

    #print(f"\nSuccessfully decoded PGN with {len(games)} game(s), {total_move_count} total move(s).")
    return decoded_string

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode_string():
    input_string = request.form['input_string']
    encoded_pgn = encode(input_string)
    return render_template('result.html', original=input_string, result=encoded_pgn, action="Encoded")

@app.route('/decode', methods=['POST'])
def decode_string():
    input_pgn = request.form['input_pgn']
    decoded_string = decode(input_pgn)
    return render_template('result.html', original=input_pgn, result=decoded_string, action="Decoded")

if __name__ == '__main__':
    app.run(debug=True)
