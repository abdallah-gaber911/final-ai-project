"""
Dialogue and witty commentary for the cheeky robot opponent.
Clean, lighthearted, and humorous lines for each in-game situation.
"""

import random

MESSAGES = {
    "game_start_human": [
        "You get the first drop! Don't be shy.",
        "Your turn first. Let's see your grand opening.",
        "Red goes first! Make it count.",
        "A fresh grid awaits! Show me what you've got.",
        "The board is clean. Your move, human friend!",
        "Lead the way! I am taking careful notes.",
        "First turn advantage is yours. Let's play!"
    ],
    "game_start_ai": [
        "I get to move first! Allow me to demonstrate.",
        "Computer starts! Watch and learn.",
        "Yellow goes first! Securing my favorite column.",
        "I shall open today's festivities.",
        "Starting up my algorithms. Beep boop, here I go!",
        "First move claimed! The center is calling my name.",
        "Let the battle of minds begin with my opening!"
    ],
    "thinking_easy": [
        "Depth 1 search: looking at the immediate horizon.",
        "Glancing one step ahead. Nothing too fancy!",
        "Easy mode engaged. Keeping my gears in low gear.",
        "Just a quick check of the board.",
        "Simple calculations, high hopes!",
        "One move lookahead running. Piece of cake."
    ],
    "thinking_medium": [
        "Searching 3 moves ahead. Weighing my options!",
        "Calculating your counter-moves... interesting.",
        "Looking 3 plies deep. Plotting a clever maneuver.",
        "Analyzing board windows... defense or attack?",
        "Medium difficulty: time to play some real Connect 4.",
        "Foreseeing the next 3 turns in silicon clarity."
    ],
    "thinking_hard": [
        "Calculating 5 moves ahead. Please hold your breath.",
        "Hard mode active! Exploring thousands of futures.",
        "Simulating 20,000 branch realities right now...",
        "Searching depth 5! My cooling fans are spinning.",
        "Consulting deep heuristics. No mistakes allowed.",
        "Five plies deep into the matrix. Finding the optimal line."
    ],
    "ai_good_move": [
        "Oh, I really like how that turned out!",
        "Look at that positioning. Pure geometric elegance.",
        "That felt like a textbook move.",
        "My heuristics approve of this placement.",
        "Step by step, my strategy takes shape.",
        "A delightfully tactical choice, if I say so myself."
    ],
    "human_blocked": [
        "Hey! That was my winning slot!",
        "Sharp eyes! You spotted my sneaky setup.",
        "Well played... I thought I had that one.",
        "Denied! Respect where respect is due.",
        "Ouch, ruined my master plan. Back to the drawing board.",
        "Fine, you blocked it. But I have backup plans!"
    ],
    "human_weak_move": [
        "An intriguing choice! Not the one I expected.",
        "Giving me an opening? How generous of you!",
        "I see what you did there... or maybe I don't?",
        "Bold strategy! Let's see how that pays off.",
        "My sensors detect an opportunity for Yellow.",
        "A curious placement. Time to capitalize!"
    ],
    "human_wins": [
        "System overload! You outplayed my silicon brain.",
        "Four in a row! I bow to your superior organic intellect.",
        "GG! You found the winning line. Rematch soon?",
        "A well-deserved victory. I will study this game.",
        "You win! My algorithms need a quick reboot.",
        "Defeated fair and square. Congratulations, champion!"
    ],
    "ai_wins": [
        "Connect 4! Silicon triumph! Thanks for a great match.",
        "Victory for Yellow! Those diagonal lines never lie.",
        "And that makes four! Don't worry, you played well.",
        "Checkmate... wait, wrong game. Four in a row!",
        "Beep boop! That is a win for the robot squad.",
        "Victory achieved! Hit 'New Game' and let's go again!"
    ],
    "draw": [
        "All 42 slots filled! A perfect standoff.",
        "A draw! Neither of us yielded an inch.",
        "Gridlock! Our brains were evenly matched today.",
        "42 coins and no victor! Truly a clash of titans.",
        "Stalemate on the grid! That was intense.",
        "Full board! Honors are even."
    ],
    "hint_used": [
        "Okay, I will share some wisdom. Just this once!",
        "Whispering the optimal column to you...",
        "Here is a tactical pointer. Go for the glow!",
        "Checking my search tree for your best angle...",
        "A little silicon assistance never hurt anyone.",
        "Try this column! You can thank me later."
    ],
    "undo_used": [
        "Rewinding time. Nothing happened. We never talk about it.",
        "Time travel initiated! Back to your previous turn.",
        "Take-backs allowed! Let's try an alternative timeline.",
        "Zapping that move from memory. What move?",
        "Erasing the record. Second chances for everyone!",
        "Temporal rewind complete. Choose wisely this time!"
    ],
    "compare_ai": [
        "Let the nodes battle begin! Minimax vs Alpha-Beta.",
        "Benchmarking search algorithms side-by-side!",
        "Watching Alpha-Beta prune the dead branches...",
        "A live tournament between brute force and pruning efficiency.",
        "Crunching tree statistics on the current position!",
        "Evaluating pruning gains. Prepare to see nodes saved."
    ],
    "idle": [
        "Still thinking? Take your time, my circuits are patient.",
        "The board isn't going anywhere, but I am curious!",
        "Staring intensely at column 4... or will you pick column 3?",
        "My clock cycles are idling! Whenever you're ready.",
        "Planning a 10-step trap, or just sipping coffee?",
        "Whenever you are ready, the grid awaits your move!"
    ]
}


def get_message(category):
    """Retrieve a random dialogue line for a given gameplay situation."""
    lines = MESSAGES.get(category, ["Your move!"])
    return random.choice(lines)


def get_pruning_message(nodes_saved, percentage):
    """Generate dynamic witty commentary based on Alpha-Beta pruning results."""
    templates = [
        f"Skipped {nodes_saved:,} nodes ({percentage:.1f}%). Efficiency is my love language.",
        f"Pruned {nodes_saved:,} branches! Why search what doesn't matter?",
        f"Saved {percentage:.1f}% search effort ({nodes_saved:,} nodes pruned). Smooth and clean.",
        f"Alpha-Beta eliminated {nodes_saved:,} unnecessary evaluations. Pure math magic."
    ]
    return random.choice(templates)
