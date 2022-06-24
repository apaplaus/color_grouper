#!/usr/bin/python

import logging
import random

SUITS = {
    "S" : "Spades",
    "H" : "Hearts",
    "D" : "Diamonds",
    "C" : "Clubs",
}

VALUES_MAP = {
    1 :  "Ace",
    11 : "Jack",
    12 : "Queen",
    13 : "King",
}

# It's a little bit confusing, but rank is a number [1..13] and value is actually a suit ["S"..."C"]
class Card:
    """
    Class representing a card
    """
    def __init__(self, rank, value):
        if rank < 1 or rank > 13:
            raise RuntimeError(f"Wrong card rank: {rank}")
        if SUITS.get(value) is None:
            raise RuntimeError(f"Wrong card value: {value}")
        self._suit = value
        self._value = rank

    def suit(self):
        return self._suit

    def value(self):
        return self._value

    def suitAsString(self):
        return SUITS.get(self._suit)

    def valueAsString(self):
        string_value = VALUES_MAP.get(self._value, None)
        if string_value is None:
            string_value = str(self._value)
        return string_value

    def toString(self):
        return f"{self.valueAsString()} of {self.suitAsString()}"

    # helper method
    def __str__(self):
        return f"{self.value()}-{self.suit()}"


class Deck:
    """
    Class representing a deck
    """
    def __init__(self):
        self._cards = []
        for suit in SUITS:
            for val in range(1,14):
                self._cards.append(Card(val, suit))
        random.shuffle(self._cards)

    def shuffle(self, used=[]):
        self._cards.extend(used)
        random.shuffle(self._cards)

    def remaining(self):
        return len(self._cards)

    def deal(self):
        if len(self._cards) == 0:
            raise RuntimeError("There are no cards left in the deck")
        return self._cards.pop()


class Hand():
    """
    Class representing a hand
    """
    def __init__(self):
        self.cards = []

    def addCard(self, card):
        self.cards.append(card)

    def removeCard(self, card):
        card_index = self.cards.index(card)
        return self.cards.pop(card_index)

    def sortBySuit(self):
        self.cards = sorted(self.cards, key=lambda x: (x.suit(), x.value()))

    def sortByValue(self):
        self.cards = sorted(self.cards, key=lambda x: (x.value(), x.suit()))

    

def testCard():
    cards = [Card(1, "S"), Card(3, "H"), Card(10, "D"), Card(13, "C")]
    for number, card in enumerate(cards):
        logging.debug(f"card #{number}:")
        logging.debug(f"suit: {card._suit}  value: {card._value}")
        logging.debug(f"suitAsString:{card.suitAsString()} valueAsString: {card.valueAsString()}")
        logging.debug(f"toString: {card.toString()}\n")

def testDeck():
    deck = Deck()
    logging.debug(f"deck size is: {deck.remaining()}")
    logging.debug(f"deck first 5 cards are:")
    for i in range(5):
        logging.debug(f"#{i}: {deck._cards[i].toString()}")
    
    deck.shuffle()
    logging.debug(f"deck first 5 cards after shuffle:")
    for i in range(5):
        logging.debug(f"#{i}: {deck._cards[i].toString()}")

    used_cards = []
    for i in range(3):
        card = deck.deal()
        used_cards.append(card)
        logging.debug(f"dealing card #{i}: {card.toString()}")

    logging.debug(f"remaining after 3 deals: {deck.remaining()}")

    logging.debug(f"shuffling back 3 cards")
    deck.shuffle(used_cards)
    logging.debug(f"remaining after shuffle: {deck.remaining()}")


def testHand():
    hand = Hand()
    cards = [Card(3, "S"), Card(3, "H"), Card(5, "H"), Card(1, "S"), Card(4, "H"), Card(3, "D"), Card(13, "C")]
    for card in cards:
        hand.addCard(card)
    for card in hand.cards:
        logging.debug(str(card))
    
    logging.debug("Sorting by value")
    hand.sortByValue()
    for card in hand.cards:
        logging.debug(str(card))    

    logging.debug("Sorting by suit")
    hand.sortBySuit()
    for card in hand.cards:
        logging.debug(str(card))

    logging.debug("removing 2 cards")
    hand.removeCard(cards[1])
    hand.removeCard(cards[4])
    logging.debug("Sorting by value")
    hand.sortByValue()
    for card in hand.cards:
        logging.debug(str(card))    


def run_tests():
    logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
    logging.debug("="*25)
    logging.debug("Runninge Card test")
    testCard()
    logging.debug("="*25)
    logging.debug("Runninge Deck test")
    testDeck()
    logging.debug("="*25)
    logging.debug("Runninge Hand test")
    testHand()

if __name__ == "__main__":
    run_tests()
    