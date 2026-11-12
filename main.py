from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
import random


hide_debug_information()
set_website_title("Blackjack vs. Dealer")
set_website_framed(False)
set_site_information(
    "Your Name",
    "A blackjack game where one player plays against a computer dealer.",
    "Drafter documentation and course materials.",
    "Week 10 brainstorming worksheet and Week 11 design worksheet.",
    []
)


@dataclass
class Card:
    """Represent one card in a standard deck."""
    rank: str
    suit: str
    value: int


@dataclass
class GameRecord:
    """Store the final totals, result, and points change for a round."""
    player_total: int
    dealer_total: int
    result: str
    credits_change: int


@dataclass
class State:
    """Store player information, the current round, points, and game history."""
    player_name: str
    wins: int
    losses: int
    ties: int
    history: list[GameRecord]
    deck: list[Card]
    player_hand: list[Card]
    dealer_hand: list[Card]
    game_active: bool
    message: str
    show_hints: bool
    credits: int
    bonus_credits: int
    round_multiplier: int
    double_down_used: bool


def make_deck() -> list[Card]:
    """Create and shuffle a standard 52-card deck."""
    deck = []
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = [
        ("Ace", 11), ("2", 2), ("3", 3), ("4", 4), ("5", 5),
        ("6", 6), ("7", 7), ("8", 8), ("9", 9), ("10", 10),
        ("Jack", 10), ("Queen", 10), ("King", 10)
    ]
    for suit in suits:
        for rank, value in ranks:
            deck.append(Card(rank, suit, value))
    random.shuffle(deck)
    return deck


def draw_card(deck: list[Card]) -> Card:
    """Remove and return the next card from the shuffled deck."""
    return deck.pop()


def hand_total(hand: list[Card]) -> int:
    """Calculate a hand total, counting aces as 1 when needed."""
    total = 0
    aces = 0
    for card in hand:
        total += card.value
        if card.rank == "Ace":
            aces += 1

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def show_card(card: Card) -> str:
    """Show only the card rank; suits are not used in this game."""
    return card.rank


def show_hand(hand: list[Card]) -> str:
    """Return all cards in a hand using their full rank and suit names."""
    names = []
    for card in hand:
        names.append(show_card(card))
    return ", ".join(names)


def start_new_round(state: State) -> None:
    """Shuffle a new deck, deal both hands, and reset round options."""
    state.deck = make_deck()
    state.player_hand = []
    state.dealer_hand = []
    state.player_hand.append(draw_card(state.deck))
    state.dealer_hand.append(draw_card(state.deck))
    state.player_hand.append(draw_card(state.deck))
    state.dealer_hand.append(draw_card(state.deck))
    state.game_active = True
    state.round_multiplier = 1
    state.double_down_used = False
    state.message = "Your cards have been dealt."

    if (hand_total(state.player_hand) == 21
            or hand_total(state.dealer_hand) == 21):
        dealer_play(state)

def finish_round(state: State) -> None:
    """Compare totals, update credits and statistics, and save the result."""
    player_total = hand_total(state.player_hand)
    dealer_total = hand_total(state.dealer_hand)

    if player_total > 21:
        result = "Loss"
        state.losses += 1
        state.message = "You went over 21. The dealer wins."
        credit_change = -10 * state.round_multiplier
    elif dealer_total > 21:
        result = "Win"
        state.wins += 1
        state.message = "The dealer went over 21. You win!"
        credit_change = 10 * state.round_multiplier
    elif player_total > dealer_total:
        result = "Win"
        state.wins += 1
        state.message = "Your total is higher. You win!"
        credit_change = 10 * state.round_multiplier
    elif player_total < dealer_total:
        result = "Loss"
        state.losses += 1
        state.message = "The dealer has the higher total."
        credit_change = -10 * state.round_multiplier
    else:
        result = "Tie"
        state.ties += 1
        state.message = "Both totals match. The round is a tie."
        credit_change = 0

    if result == "Win" and player_total == 21 and len(state.player_hand) == 2:
        credit_change += 5
        state.bonus_credits += 5

    state.credits += credit_change
    state.history.append(
        GameRecord(player_total, dealer_total, result, credit_change)
    )
    state.game_active = False


def dealer_play(state: State) -> None:
    """Make the dealer draw until reaching 17 or more, then finish the round."""
    while hand_total(state.dealer_hand) < 17:
        state.dealer_hand.append(draw_card(state.deck))
    finish_round(state)


def navigation() -> list:
    """Return the links shared by the website pages."""
    return [
        Button("Home", "index"),
        Button("Game", "game"),
        Button("Statistics", "stats"),
        Button("History", "history"),
        Button("Card Guide", "card_guide"),
        Button("Rules", "rules")
    ]


def game_page(state: State) -> Page:
    """Build the game page with the player's hand and dealer's visible card."""
    content = [
        Header("Blackjack Table"),
        Text("Player: " + state.player_name),
        Text("Game credits: " + str(state.credits)),
        Text("Your cards: " + show_hand(state.player_hand)),
        Text("Your total: " + str(hand_total(state.player_hand))),
        Text("Dealer's visible card: " + show_card(state.dealer_hand[0])),
        Text(state.message)
    ]

    if state.show_hints:
        content.append(Text(
            "Hint: try to get as close to 21 as possible without going over."
        ))

    if state.game_active:
        content.append(Button("Hit", "hit"))
        content.append(Button("Stand", "stand"))
        if (len(state.player_hand) == 2
                and hand_total(state.player_hand) <= 11
                and not state.double_down_used):
            content.append(Button("Double Down", "double_down"))
            content.append(Text(
                "Double Down is available because your first two cards total "
                "less than 11. It doubles the points gained or lost for this round."
            ))
    else:
        content.append(Text(
            "Dealer's cards: " + show_hand(state.dealer_hand)
        ))
        content.append(Text(
            "Dealer total: " + str(hand_total(state.dealer_hand))
        ))
        content.append(Button("Play Another Round", "new_game"))

    content.extend(navigation())
    return Page(state, content)


@route
def index(state: State) -> Page:
    """Show the home page and collect the player's name and hint preference."""
    return Page(state, [
        Header("Blackjack vs. Dealer"),
        Text(
            "Play blackjack against a computer dealer. Cards are dealt "
            "randomly from a shuffled standard deck. You start with 100 game "
            "credits. Wins add credits and losses subtract credits."
        ),
        Text("Your name:"),
        TextBox("player_name", state.player_name),
        Text("Show playing hints:"),
        CheckBox("show_hints", state.show_hints),
        Text("Current game credits: " + str(state.credits)),
        Button("Start Game", "start_game"),
        Text(state.message),
        *navigation()
    ])


@route
def start_game(state: State, player_name: str,
               show_hints: bool) -> Page:
    """Save the player's settings, deal cards, and show the game."""
    if player_name.strip() != "":
        state.player_name = player_name.strip()
    state.show_hints = show_hints
    start_new_round(state)
    return game_page(state)


@route
def game(state: State) -> Page:
    """Show the current game or explain how to start one."""
    if len(state.player_hand) == 0:
        return Page(state, [
            Header("Blackjack Table"),
            Text("You do not have an active round yet."),
            Button("Start a Game", "index"),
            *navigation()
        ])
    return game_page(state)


@route
def hit(state: State) -> Page:
    """Deal one card to the player and finish the round if they bust."""
    if state.game_active:
        state.player_hand.append(draw_card(state.deck))
        if hand_total(state.player_hand) > 21:
            state.message = "You went over 21."
            finish_round(state)
        else:
            state.message = "You drew another card."
    return game_page(state)


@route
def stand(state: State) -> Page:
    """End the player's turn and let the dealer play."""
    if state.game_active:
        state.message = "You stand. The dealer is playing."
        dealer_play(state)
    return game_page(state)


@route
def double_down(state: State) -> Page:
    """Double the round's points, draw exactly one card, and end the turn."""
    if (state.game_active
            and len(state.player_hand) == 2
            and hand_total(state.player_hand) <= 11
            and not state.double_down_used):
        state.round_multiplier = 2
        state.double_down_used = True
        state.player_hand.append(draw_card(state.deck))

        if hand_total(state.player_hand) > 21:
            state.message = "You doubled down and went over 21."
            finish_round(state)
        else:
            state.message = "You doubled down. The dealer will now play."
            dealer_play(state)
    else:
        state.message = (
            "You can only double down on your first two cards when their "
            "total is below 11."
        )
    return game_page(state)


@route
def new_game(state: State) -> Page:
    """Start another round using the saved player preferences."""
    start_new_round(state)
    return game_page(state)


@route
def stats(state: State) -> Page:
    """Show wins, losses, ties, total rounds, and current credits."""
    rounds = state.wins + state.losses + state.ties
    return Page(state, [
        Header("Statistics"),
        Text("Player: " + state.player_name),
        Text("Rounds played: " + str(rounds)),
        Text("Wins: " + str(state.wins)),
        Text("Losses: " + str(state.losses)),
        Text("Ties: " + str(state.ties)),
        Text("Game credits: " + str(state.credits)),
        Text("Bonus credits earned: " + str(state.bonus_credits)),
        Text("A normal win adds 10 credits. A loss subtracts 10 credits."),
        Text("A two-card blackjack adds 5 bonus credits."),
        Text("Double Down doubles the points gained or lost in that round."),
        *navigation()
    ])


@route
def history(state: State) -> Page:
    """Show previous round results and credit changes."""
    content: list = [Header("Game History")]
    if len(state.history) == 0:
        content.append(Text("You have not completed a round yet."))

    for number, record in enumerate(state.history, start=1):
        content.append(Text(
            "Round " + str(number)
            + ": You had " + str(record.player_total)
            + ", dealer had " + str(record.dealer_total)
            + ". Result: " + record.result
            + ". Credits change: " + str(record.credits_change)
        ))

    content.extend(navigation())
    return Page(state, content)


@route
def card_guide(state: State) -> Page:
    """Explain card values and how aces are counted."""
    return Page(state, [
        Header("Card Guide"),
        Text("Cards 2 through 10 are worth their number."),
        Text("Jack, Queen, and King are worth 10."),
        Text("An ace is worth 11, or 1 if 11 would make the hand go over 21."),
        Text("Cards are displayed by rank only. Suits do not affect the game."),
        *navigation()
    ])


@route
def rules(state: State) -> Page:
    """Explain blackjack rules and the game's points system."""
    return Page(state, [
        Header("How to Play"),
        Text("You play against a computer dealer."),
        Text("You and the dealer each receive two cards."),
        Text("You can see one of the dealer's cards while it is your turn."),
        Text("Choose Hit to receive another card."),
        Text("Choose Stand when you want to stop drawing cards."),
        Text("The dealer draws until reaching at least 17."),
        Text("A hand over 21 loses. The higher total up to 21 wins."),
        Text("An equal total is a tie."),
        Text("An ace counts as 11 or 1, whichever keeps the hand at 21 or below."),
        Text("You start with 100 game credits."),
        Text("A win adds 10 credits. A loss subtracts 10 credits. A tie changes nothing."),
        Text("A two-card blackjack earns 5 bonus credits."),
        Text("Double Down is available on the first two cards when their total is below 11."),
        Text("Double Down gives one more card and doubles the round's points gained or lost."),
        Text("Credits are game points only and have no real-money value."),
        *navigation()
    ])


@route
def reset_statistics(state: State) -> Page:
    """Reset statistics, history, and credits to their starting values."""
    state.wins = 0
    state.losses = 0
    state.ties = 0
    state.credits = 100
    state.bonus_credits = 0
    state.history = []
    state.game_active = False
    state.player_hand = []
    state.dealer_hand = []
    state.round_multiplier = 1
    state.double_down_used = False
    state.message = "Your statistics and credits have been reset."
    return stats(state)


# Tests use fixed cards so the expected results do not depend on randomness.
test_hand = [
    Card("Ace", "Spades", 11),
    Card("9", "Hearts", 9)
]
assert_equal(hand_total(test_hand), 20)

test_ace_hand = [
    Card("Ace", "Spades", 11),
    Card("9", "Hearts", 9),
    Card("5", "Clubs", 5)
]
assert_equal(hand_total(test_ace_hand), 15)

test_face_hand = [
    Card("King", "Spades", 10),
    Card("Queen", "Hearts", 10)
]
assert_equal(hand_total(test_face_hand), 20)

assert_equal(len(make_deck()), 52)
assert_equal(show_card(Card("9", "Diamonds", 9)), "9")
assert_equal(show_card(Card("King", "Hearts", 10)), "King")

test_state = State(
    "Test Player", 0, 0, 0, [], [], [], [], True,
    "", False, 100, 0, 1, False
)
test_state.player_hand = [
    Card("King", "Spades", 10),
    Card("Queen", "Hearts", 10)
]
test_state.dealer_hand = [
    Card("9", "Clubs", 9),
    Card("8", "Diamonds", 8)
]
finish_round(test_state)
assert_equal(test_state.wins, 1)
assert_equal(test_state.credits, 110)
assert_equal(test_state.game_active, False)
assert_equal(len(test_state.history), 1)

# Verify that a loss removes credits.
loss_state = State(
    "Test Player", 0, 0, 0, [], [], [], [], True,
    "", False, 100, 0, 1, False
)
loss_state.player_hand = [
    Card("King", "Spades", 10),
    Card("Queen", "Hearts", 10)
]
loss_state.dealer_hand = [
    Card("Ace", "Clubs", 11),
    Card("8", "Diamonds", 8)
]
finish_round(loss_state)
assert_equal(loss_state.losses, 1)
assert_equal(loss_state.credits, 90)

# Verify that doubling the points doubles a loss.
double_loss_state = State(
    "Test Player", 0, 0, 0, [], [], [], [], True,
    "", False, 100, 0, 2, True
)
double_loss_state.player_hand = [
    Card("King", "Spades", 10),
    Card("Queen", "Hearts", 10)
]
double_loss_state.dealer_hand = [
    Card("Ace", "Clubs", 11),
    Card("8", "Diamonds", 8)
]
finish_round(double_loss_state)
assert_equal(double_loss_state.credits, 80)

# Shuffled dealing is random, so it is not tested against fixed card orders.

start_server(State(
    "Player", 0, 0, 0, [], make_deck(), [], [], False,
    "Welcome! Start a game to receive your cards.",
    False, 100, 0, 1, False
))

