import sys
from chess import pgn, Board
from math import log2

def get_pgn_games(pgn_path):
    games = []
    with open(pgn_path, "r") as pgn_file:
        while True:
            game = pgn.read_game(pgn_file)
            if game is None:
                break
            games.append(game)
    return games

def decode(pgn_path: str, output_file_path: str):
    games = get_pgn_games(pgn_path)
    output_bits = ""

    for game_index, game in enumerate(games):
        board = Board()
        moves = list(game.mainline_moves())

        for move_index, move in enumerate(moves):
            legal_moves = list(board.legal_moves)
            legal_move_ucis = [m.uci() for m in legal_moves]

            # Get index of the move played
            move_idx = legal_move_ucis.index(move.uci())

            # Calculate number of bits needed to encode legal moves count
            max_bits_len = int(log2(len(legal_moves)))
            if max_bits_len == 0:
                max_bits_len = 1  # fallback

            # Convert move index to binary, padded to max_bits_len
            move_bits = bin(move_idx)[2:].rjust(max_bits_len, "0")

            output_bits += move_bits
            board.push(move)

    # Now convert bits to bytes
    all_bytes = bytearray()

    # Process output_bits 8 bits at a time
    for i in range(0, len(output_bits), 8):
        byte_chunk = output_bits[i:i+8]
        if len(byte_chunk) < 8:
            # Ignore incomplete byte at end (could be padding)
            break
        all_bytes.append(int(byte_chunk, 2))

    # Write bytes to output file
    with open(output_file_path, "wb") as f:
        f.write(all_bytes)

    print(f"Decoded {len(games)} game(s), wrote {len(all_bytes)} bytes to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python decoder.py input.pgn output_file")
    else:
        decode(sys.argv[1], sys.argv[2])
