import random


class Card:
    """Represents a standard playing card."""
    
    suit_names = ['Clubs', 'Diamonds', 'Hearths', 'Spades']
    rank_names = [None, None, '2', '3', '4', '5', '6', '7',
                  '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    
    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank
        
    def __str__(self):
        if self.suit is not None:
            return '%s of %s' % (Card.rank_names[self.rank],
                             Card.suit_names[self.suit])
        else: return 'no trump'
        
    def __lt__(self, other):
        t1 = self.rank, self.suit
        t2 = other.rank, other.suit
        return t1 < t2
    
    def has_lead_suit(self, lead_suit):
        return self.suit == lead_suit
    
    def is_trump(self, trump_suit):
        return self.suit == trump_suit


class Deck:
    """Represents a deck of 52 playing cards. Cards can be moved to or
    from a deck. The deck can also be shuffled or sorted."""
    
    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(2, 15):
                card = Card(suit, rank)
                self.cards.append(card)
                
    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def sort(self):
        self.cards.sort()
            
    def pop_card(self, i=-1):
        return self.cards.pop(i)
    
    def add_card(self, card):
        self.cards.append(card)
        
    def move_cards(self, hand, num, i=-1):
        for j in range(num):
            hand.add_card(self.pop_card(i))
            
    def move_a_card(self, hand, i =-1):
        self.move_cards(hand, 1, i=-1)
        
    def move_specific_card(self, hand, card):
        self.move_cards(hand, 1, i = self.cards.index(card))            
                

class Hand(Deck):
    """Represents a hand, is like a deck, but is labeled as the player it
    belongs to. The cards can be seperated on playability."""
    
    def __init__(self, label):
        """lists to group the cards in the hand. Lists are re-used.
        self.label is the label of the player(int).
        """ 
        self.label = label
        self.cards = []
        self.playable = []
        self.unplayable = []
        self.trumps = []
        self.leads = []
        
    def __str__(self):
        res = []
        res.append(str(self.label))
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)
        
    def playable_cards(self, lead_suit, trump_suit):
        """Returns a list with the cards that the player can play. 
        It depends on the current lead suit and trump suit of the trick. 
        These cards can be picked by the player.
        """
        self.leads[:] = self.filter_suit(lead_suit)
        self.trumps[:] = self.filter_suit(trump_suit)
        if self.leads:          
            if self.trumps and lead_suit != trump_suit:
                self.playable[:] = self.leads + self.trumps 
            else: 
                self.playable[:] = self.leads[:]
        else: 
            self.playable[:] = self.cards[:]
        return self.playable
    
    def unplayable_cards(self):
        """Returns a list of forbidden to play cards."""
        self.unplayable[:] = list(set(self.cards) - set(self.playable))
        return self.unplayable
    
    def filter_suit(self, suit):
        """Returns a list of cards of a certain suit."""
        return [card for card in self.cards if card.suit == suit]            


class Trick(Deck):
    """Represents the trick that is being played(the cards on the table).
    Is like a deck, but also has a method to find the highest card. 
    It also has a trump suit and a lead suit."""
    
    def __init__(self):
        """The label corresponds to the player who's turn it is.(int)"""
        self.cards = []
        self.lead_suit = None
        self.trump_suit = None
        self.label = None
    
    def highest_card(self):
        self.sort()
        return self.cards[-1]          
    
    def sort(self):
        """Sorting is done in three steps: sorting based on the __lt__ method
        of the cards (first rank, then suit), if they have the lead suit
        and if they have the trump suit.
        """
        self.cards.sort()
        self.cards.sort(key=lambda x: x.has_lead_suit(self.lead_suit))
        self.cards.sort(key=lambda x: x.is_trump(self.trump_suit))
   
    
class Player:
    """Represents the model player and is not to be confused with the real
    player."""
    
    def __init__(self, label, name=''):
        """The label is an integer in the range(4) so the player can be
        identified. In fact all labels being used in the game stand for a
        certain player. A player has a hand and can have a card it played.
        The difference between their bids and their actual wins of tricks
        decides the score.
        """
        self.label = label
        self.name = name
        self.hand = Hand(self.label)
        self.played_card = None
        self.tricks_won = 0
        self.bids = 0
        self.score = 0

    def start(self, lead_suit, trump_suit):
        
        playable = self.hand.playable_cards(lead_suit, trump_suit)
        unplayable = self.hand.unplayable_cards()
        self.played_card = playable[0]
        self.played_card.label = self.label
        for card in playable:
            print(str(card) + ' playable')
        for card in unplayable:
            print(str(card) + ' unplayable')
        print('\n')
    
            
class Score:
    """Represents the score of each player."""
    def __init__(self, players):
        self.players = players
        
    def adjust(self):
        for player in self.players:
            if player.tricks_won == player.bids:
                player.score += player.tricks_won*2 + 5
            else: 
                player.score -= abs(player.tricks_won - player.bids)*2
                    

class Game:
    """Represents the game model of boerenbridge. All games have 4 players
    and a list of the number of cards that are dealt each round(index of the list)."""
    
    noc = [i for i in range(1,14)] + [j for j in range(13,0,-1)]
    nop = 4
    
    def __init__(self):
        """Instance of a Game has a Deck, a Trick, Players and their 
        Score and Bidding(work in progress). The label is to determine 
        the leading player at the start of every round.
        """
        self.deck = Deck()
        self.players = [Player(i) for i in range(self.nop)]
        self.trick = Trick()
        self.score = Score(self.players)
        self.round = 1
        self.label = self.dealer()
        
    def dealer(self):
        """Determines the starting dealer of the game
        by giving all players a card. Highest card wins.
        """
        self.deck.shuffle()
        self.deck.move_cards(self.trick, Game.nop)
        ranked = sorted( enumerate(self.trick.cards), key=lambda x : x[1] )
        self.trick.move_cards(self.deck, Game.nop)
        return ranked[-1][0] 
    
    def starting_player(self):
        """Sets the leading player at the start of every round. It is 
        the player after the dealer. The starting position rotates clockwise. 
        Sets the label of the game accordingly.
        """ 
        player = self.next_player(self.label)
        self.label = player.label
        
    def deal_hands(self):
        """Deals a number of cards from the deck to all hands in the game.
        """
        for player in self.players:
            self.deck.move_cards(player.hand, self.noc[self.round - 1])
            
    def pull_trump(self):
        """Every even round there is a random trump suit. 
        Cards with trump suit can always be played and are highest.
        """
        if self.round % 2 == 0 :
            self.trick.trump_suit = self.deck.cards[-1].suit
            self.deck.shuffle()
        else: self.trick.trump_suit = None
        if self.trick.trump_suit:
            print('trump is' + Card.suit_names[self.trick.trump_suit])
     
    def next_player(self, label):
        """Returns the next player given the label of the last
        player. Sets the label of the trick accordingly.
        """
        player = self.players[label - (self.nop - 1)]
        self.trick.label = player.label
        return player
        
    def leading_player(self):
        """Determines the next leading player at the end of a trick. 
        Sets the label of the trick accordingly.
        """
        card = self.trick.highest_card()
        print('highest card is ' + str(card)) 
        player = self.players[card.label]
        self.trick.label = player.label
        return player
    
    def trick_complete(self):
        """Wraps up the trick. Resets the lead suit, moves the cards back
        to the deck. (they are not used anymore till a new round.)
        """
        player = self.leading_player()
        player.tricks_won += 1
        self.trick.lead_suit = None
        self.trick.move_cards(self.deck, self.nop)
        
    def play(self):
        """The main mechanics of the game. It loops as long as someone still
        holds cards. Players play clockwise. If the trick has as many cards in it 
        as there are players, it is complete. The next leading player is decided with
        the highest card. 
        """
        while any(player.hand.cards for player in self.players):  
            
            for player in self.players:
                if player.label == self.trick.label:
                    player.start(self.trick.lead_suit, self.trick.trump_suit)
                    card = player.played_card
                    player.hand.move_specific_card(self.trick, card)
            
            if len(self.trick.cards) == 1:
                self.trick.lead_suit = card.suit        
            if len(self.trick.cards) == self.nop:
                self.trick_complete()
            else:
                self.next_player(self.trick.label)
                
    def run(self):
        """The main loop of the game model, each loop is a round in the game. 
        """
        while self.round <= len(self.noc):
             
             self.starting_player()
             self.deck.shuffle()
             self.pull_trump()
             self.deal_hands()
             self.play()
             self.score.adjust()
             self.round += 1  
             
def main():
    
    game = Game()
    game.run()
    
if __name__=="__main__":
    main()
      

        

    

        