import sys
from math import log2
from chess import Board, pgn

def encode(input_file_path: str, output_pgn_path: str):
    # Read raw bytes from input file
    with open(input_file_path, "rb") as f:
        data = f.read()

    board = Board()
    game = pgn.Game()
    node = game

    bits_buffer = ""

    # Helper to write bits as moves
    def bits_to_moves(bits):
        moves = []
        while len(bits) > 0:
            legal_moves = list(board.legal_moves)
            if len(legal_moves) == 0:
                print("No legal moves left on the board — stopping encoding.")
                break

            max_index = len(legal_moves) - 1
            max_bits_len = int(log2(len(legal_moves)))
            if max_bits_len == 0:
                max_bits_len = 1  # safety fallback

            # Take chunk of bits up to max_bits_len
            chunk = bits[:max_bits_len]
            bits = bits[max_bits_len:]

            # Pad chunk if shorter than max_bits_len
            if len(chunk) < max_bits_len:
                chunk = chunk.ljust(max_bits_len, "0")

            idx = int(chunk, 2)
            if idx > max_index:
                idx = max_index  # safety fallback

            move = legal_moves[idx]
            moves.append(move)
            board.push(move)
        return moves, bits

    # Convert bytes to bits string
    for byte in data:
        bits_buffer += f"{byte:08b}"

    # Encode bits buffer to moves
    moves, _ = bits_to_moves(bits_buffer)

    # Add moves to PGN game
    for move in moves:
        node = node.add_variation(move)

    # Write PGN file
    with open(output_pgn_path, "w") as f:
        exporter = pgn.FileExporter(f)
        game.accept(exporter)

    print(f"Encoding complete! Saved {len(moves)} moves to {output_pgn_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python encoder.py input_file output.pgn")
    else:
        encode(sys.argv[1], sys.argv[2])
