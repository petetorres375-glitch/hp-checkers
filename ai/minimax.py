from copy import deepcopy


def minimax(position, depth, max_player):
    if depth == 0 or position.winner() is not None:
        return position.evaluate(), position

    if max_player:
        max_eval = float("-inf")
        best_move = None

        for move in get_all_moves(position, position.o_color):
            evaluation = minimax(move, depth - 1, False)[0]
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move

        return max_eval, best_move

    else:
        min_eval = float("inf")
        best_move = None

        for move in get_all_moves(position, position.p_color):
            evaluation = minimax(move, depth - 1, True)[0]
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move

        return min_eval, best_move


def simulate_move(piece, move, board, skipped):
    row, col = move
    board.move(piece, row, col)

    if skipped:
        board.remove(skipped)

    return board


def get_all_moves(board, color):
    all_piece_moves = []
    for piece in board.get_all_pieces(color):
        for move, skipped in board.get_valid_moves(piece).items():
            all_piece_moves.append((piece, move, skipped))

    if not all_piece_moves:
        return []

    max_captures = max(len(s) for _, _, s in all_piece_moves)

    result = []
    for piece, move, skipped in all_piece_moves:
        if max_captures > 0 and len(skipped) < max_captures:
            continue
        temp_board = deepcopy(board)
        temp_piece = temp_board.get_piece(piece.row, piece.col)
        result.append(simulate_move(temp_piece, move, temp_board, skipped))

    return result
