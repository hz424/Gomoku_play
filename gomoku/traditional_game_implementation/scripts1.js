(function($) {

    "use strict";

    $.gomoku = function(el, options) {

        var defaults = {
                board_size: 20,
                ai_first: null,
                endgame: null
            },

            game = this, 
            board = [], 
            board_size, 
            cells, 
            is_player_turn = false, 
            moveHistory = [];

        function init() {

            game.settings = $.extend({}, defaults, options);
            game.board = el;
            board_size = game.settings.board_size;

            var table = $('<table id="zebraGomoku">').on('click', 'td', function() {

                if (!is_player_turn || board[cells.index(this)]) return false;

                // show player's move on the board
                show_move(cells.index(this), 2);

                // let the computer make its move
                computer_move();

            }), i, row;

            for (i = 0; i < board_size * board_size; i++) {

                board[i] = 0;

                if (!(i % board_size)) table.append(row = $('<tr>'));

                row.append($('<td>'));

            }

            game.board.append(table);

            cells = $('td', game.board);

            if (game.settings.ai_first || (null === game.settings.ai_first && Math.random()+.5|0)) {

                game.settings.ai_first = 1;
                show_move(~~(board_size / 2) * (1 + board_size), 1);

            } else {
                game.settings.ai_first = 2;
            }

            is_player_turn = true;

        }

        function show_move(index, type) {
            board[index] = type;

            // Add the move to the move history
            moveHistory.push({ index: index, type: type });

            $(cells[index]).addClass('p' + Math.abs(type - game.settings.ai_first));
        }

        function computer_move() {

            var i, j, k, l, m, n, position, type, line, total_cells, consecutive_cells, empty_sides, best_score,
                cell_score, direction_score, score;

            is_player_turn = false;

            for (i = board_size * board_size; i--;) {

                if (board[i] == 1) continue;

                else if (!board[i] && undefined === best_score) best_score = [i, 0, 0];

                cell_score = [0, 0];

                for (j = 4; j--;) {

                    direction_score = [0, 0];

                    for (k = (!board[i] ? 5 : 1); k--;) {

                        type = board[i] || undefined; line = [];

                        for (l = 7; l--;) {

                            m = -5 + k + l;
                            n = i % board_size;

                            if (

                                ((j === 0 &&
                                (position = i + (board_size * m)) !== false &&
                                n == position % board_size) ||

                                (j == 1 &&
                                (position = i + m) !== false &&
                                ~~(position / board_size) == ~~(i / board_size)) ||

                                (j == 2 &&
                                (position = i - (board_size * m) + m) !== false &&
                                ((position > i && position % board_size < n) ||
                                (position < i && position % board_size > n) ||
                                position == i)) ||

                                (j == 3 &&
                                (position = i + (board_size * m) + m) !== false &&
                                ((position < i && position % board_size < n) ||
                                (position > i && position % board_size > n)) ||
                                position == i)) &&

                                position >= 0 && position < board_size * board_size &&

                                (board[position] == type || (!board[i] && (!board[position] || undefined === type)) ||

                                !l || l == 6)

                            ) {

                                line.push(position);

                                if (l && l ^ 6 && undefined === type && board[position]) type = board[position];

                            } else if (!l || l == 6) line.push(undefined);

                            else break;

                        }

                        if (line.length == 7 && undefined !== type) {

                            m = (board[i] ? true : false);

                            board[i] = type;

                            consecutive_cells = 0; total_cells = 0; empty_sides = 0;

                            for (l = 5; l--;) if (board[line[l + 1]] == type) total_cells++;

                            for (l = line.indexOf(i) - 1; l >= 0; l--)

                                if (board[line[l]] == type) consecutive_cells++;

                                else {

                                    if (board[line[l]] === 0) empty_sides++;

                                    break;

                                }

                            for (l = line.indexOf(i); l < line.length; l++)

                                if (board[line[l]] == type) consecutive_cells++;

                                else {

                                    if (board[line[l]] === 0) empty_sides++;

                                    break;

                                }

                            score = [[0, 1], [2, 3], [4, 12], [10, 64], [256, 256]][consecutive_cells >= total_cells ? Math.min(consecutive_cells, 5) - 1 : total_cells - 1][consecutive_cells >= total_cells ? (empty_sides ? empty_sides - 1 : 0) : 0];

                            if (!m) board[i] = 0;

                            else if (score >= 256) score = 1024;

                            if (score > direction_score[type - 1]) direction_score[type - 1] = score;

                        }

                    }

                    for (k = 2; k--;) cell_score[k] += direction_score[k];

                }

                j = cell_score[0] + cell_score[1];
                k = best_score[1] + best_score[2];

                if (

                    (j > k ||

                    (j == k && cell_score[0] >= best_score[1])) &&

                    (!board[i] || cell_score[1] >= 1024)

                ) best_score = [i, cell_score[0], cell_score[1]];

            }

            if (best_score[2] < 1024) show_move(best_score[0], 1);

            if ((best_score[1] >= 256 || best_score[2] >= 1024) && typeof game.settings.endgame == 'function')

                return game.settings.endgame.apply(null, [best_score[2] < 1024]);

            is_player_turn = true;

        }

        // Function to undo the last move
        game.regretLastMove = function() {
            if (moveHistory.length >= 2) {
                // Undo the last two moves (player and computer)
                for (let i = 0; i < 2; i++) {
                    let lastMove = moveHistory.pop();
                    if (lastMove) {
                        let index = lastMove.index;
                        board[index] = 0;
                        $(cells[index]).removeClass('p0 p1');
                    }
                }
            } else {
                alert('No moves to regret!');
            }
        };        
        
        // Initialize the game on load
        init();

    };

})(jQuery);
