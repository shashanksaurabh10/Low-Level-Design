# Requirenments
# 1. The ATM system should support some basic operations such as inquiry, cash withdrawl and cash deposit
# 2. Users should be authentic themselves using card and a PIN
# 3. The system should interact with bank's backend system to validate user accounts and perform transactions
# 4. The ATM should have a card dispenser to dispense cash to users
# 5. The system should handle concurrent access and ensure data consistency

from enum import Enum
import threading
from typing import Dict
from abc import ABC, abstractmethod

class OperationType(Enum):
    CHECK_BALANCE = "CHECK_BALANCE"
    WITHDRAW_CASH = "WITHDRAW_CASH"
    DEPOSIT_CASH = "DEPOSIT_CASH"

class Card:
    def __init__(self, card_number: str, pin: str):
        self._card_number = card_number
        self._pin = pin

    def get_card_number(self):
        return self._card_number
    
    def get_pin(self):
        return self._pin
    
class Account:
    def __init__(self, account_number: str, balance: float):
        self._account_number = account_number
        self._balance = balance
        self._cards = Dict[str, Card] = {}
        self._lock = threading.Lock()

    def get_account_number(self):
        return self._account_number
    
    def get_balance(self):
        return self._balance
    
    def get_cards(self):
        return self._cards
    
    def deposit(self, amount):
        with self._lock:
            self._balance += amount

    def withdrawl(self, amount):
        with self._lock:
            if self._balance >= amount:
                self._balance -= amount
                return True
            return False
        
class DispenseChain(ABC):
    @abstractmethod
    def set_next_chain(self, next_chain: 'DispenseChain'):
        pass

    @abstractmethod
    def dispense_cash(self, amount: int):
        pass

    @abstractmethod
    def can_dispense(self, amount:int):
        pass

class CashDispenser:
    def __init__(self, chain: DispenseChain):
        self._chain = chain
        self._lock = threading.Lock()

    def dispense_cash(self, amount: int):
        with self._lock:
            self._chain.dispense_cash(amount)

    def can_dispense(self, amount):
        with self._lock:
            if amount % 10 != 0:
                return False
            return self._chain.can_dispense(amount)
        
class NoteDispenser(DispenseChain):
    def __init__(self, note_value: int, num_notes: int):
        self._note_value = note_value
        self._num_notes = num_notes
        self._next_chain = None
        self._lock = threading.Lock()

    def set_next_chain(self, next_chain: DispenseChain):
        self._next_chain = next_chain

    def dispense_cash(self, amount: int):
        with self._lock:
            if amount >= self._note_value:
                num_to_dispense = min(amount//self._note_value, self._num_notes)
                remaining_amount = amount - (num_to_dispense * self._note_value)
                if num_to_dispense > 0:
                    print(f"Dispensing {num_to_dispense} x ${self._note_value} note(s)")
                    self._num_notes -= num_to_dispense

                if remaining_amount > 0 and self._next_chain is not None:
                    self._next_chain.dispense_cash(remaining_amount)

            elif self._next_chain is not None:
                self._next_chain.dispense_cash(amount)

    def can_dispense(self, amount):
        with self._lock:
            if amount< 0:
                return False
            if amount == 0:
                return True
            
            num_to_use = min(amount//self._note_value, self._num_notes)
            remaining_amount = amount - (num_to_use* self._note_value)

            if remaining_amount ==0:
                return True
            
            if self._next_chain is not None:
                return self._next_chain.can_dispense(remaining_amount)
            return False
        
class NoteDispenser20(NoteDispenser):
    def __init__(self, num_notes):
        super().__init__(20, num_notes)

class NoteDispenser50(NoteDispenser):
    def __init__(self, num_notes):
        super().__init__(50, num_notes)

class NoteDispenser100(NoteDispenser):
    def __init__(self, num_notes):
        super().__init__(100, num_notes)


class BankService:
    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._cards : Dict[str, Card] = {}
        self._card_account_mapping: Dict[Card, Account] = {}

    def create_account(self, account_number, initial_balance):
        account = Account(account_number, initial_balance)
        self._accounts[account_number] = account
        return account
    
    def create_card(self, card_number: str, pin: str):
        card = Card(card_number, pin)
        self._cards[card_number] = card
        return card
    
    def authenticate(self, card: Card, pin: str):
        return card.get_pin() == pin
    
    def authenticate_card(self, card_number: str):
        return self._cards.get(card_number)
    
    def get_balance(self, card: Card):
        return self._card_account_mapping[card].get_balance()

    def withdraw_money(self, card: Card, amount: float):
        self._card_account_mapping[card].withdrawl(amount)

    def deposit_money(self, card: Card, amount: float):
        self._card_account_mapping[card].deposit(amount)

    def link_card_with_account(self, card: Card, account: Account):
        account.get_cards()[card.get_card_number()] = card
        self._card_account_mapping[card] = account


class ATM:
    def __init__(self):
        self._current_state = IdleState()
        self._bank_service = BankService()
        self._current_card = None
        self._transaction_counter = 0
        c1 = NoteDispenser20(10)
        c2 = NoteDispenser50(20)
        c3 = NoteDispenser100(30)
        c1.set_next_chain(c2)
        c2.set_next_chain(c3)
        self._cash_dispenser = CashDispenser(c1)

    def get_current_card(self):
        return self._current_card
    
    def get_bank_service(self):
        return self._bank_service

    def change_state(self, new_state):
        self.current_state = new_state

    def set_current_card(self, card: Card):
        self._current_card = card

    def insert_card(self,card_number):
        self._current_state.insert_card(self, card_number)

    def enter_pin(self, pin):
        self._current_state.enter_pin(self, pin)

    def select_operation(self, op: OperationType, *args):
        self._current_state.select_operation(self, op, *args)

    def check_balance(self):
        balance = self._bank_service.get_balance(self._current_card)
        print(f"Your current account balance is: ${balance:.2f}")

    def withdraw_cash(self, amount: int):
        if not self._cash_dispenser.can_dispense(amount):
            raise RuntimeError("Insufficient cash available in the ATM.")
        
        self._bank_service.withdraw_money(self._current_card, amount)
        
        try:
            self._cash_dispenser.dispense_cash(amount)
        except Exception as e:
            self._bank_service.deposit_money(self._current_card, amount)  # Deposit back if dispensing fails
            raise e
    
    def deposit_cash(self, amount: int):
        self._bank_service.deposit_money(self._current_card, amount)

class ATMState(ABC):
    @abstractmethod
    def insert_card(self, atm: 'ATM', card_number: str):
        pass
    
    @abstractmethod
    def enter_pin(self, atm: 'ATM', pin: str):
        pass
    
    @abstractmethod
    def select_operation(self, atm: 'ATM', op: OperationType, *args):
        pass
    
    @abstractmethod
    def eject_card(self, atm: 'ATM'):
        pass

class IdleState(ATMState):
    def insert_card(self, atm: 'ATM', card_number: str):
        print("\nCard has been inserted.")
        card = atm.get_bank_service().authenticate_card(card_number)
        
        if card is None:
            self.eject_card(atm)
        else:
            atm.set_current_card(card)
            atm.change_state(HasCardState())
    
    def enter_pin(self, atm: 'ATM', pin: str):
        print("Error: Please insert a card first.")
    
    def select_operation(self, atm: 'ATM', op: OperationType, *args):
        print("Error: Please insert a card first.")
    
    def eject_card(self, atm: 'ATM'):
        print("Error: Card not found.")

class HasCardState(ATMState):
    def insert_card(self, atm: 'ATM', card_number: str):
        print("Error: A card is already inserted. Cannot insert another card.")
    
    def enter_pin(self, atm: 'ATM', pin: str):
        print("Authenticating PIN...")
        card = atm.get_current_card()
        is_authenticated = atm.get_bank_service().authenticate(card, pin)
        
        if is_authenticated:
            print("Authentication successful.")
            atm.change_state(AuthenticatedState())
        else:
            print("Authentication failed: Incorrect PIN.")
            self.eject_card(atm)
    
    def select_operation(self, atm: 'ATM', op: OperationType, *args):
        print("Error: Please enter your PIN first to select an operation.")
    
    def eject_card(self, atm: 'ATM'):
        print("Card has been ejected. Thank you for using our ATM.")
        atm.set_current_card(None)
        atm.change_state(IdleState())

class AuthenticatedState(ATMState):
    def insert_card(self, atm: 'ATM', card_number: str):
        print("Error: A card is already inserted and a session is active.")
    
    def enter_pin(self, atm: 'ATM', pin: str):
        print("Error: PIN has already been entered and authenticated.")
    
    def select_operation(self, atm: 'ATM', op: OperationType, *args):
        if op == OperationType.CHECK_BALANCE:
            atm.check_balance()
        elif op == OperationType.WITHDRAW_CASH:
            if len(args) == 0 or args[0] <= 0:
                print("Error: Invalid withdrawal amount specified.")
                return
            
            amount_to_withdraw = args[0]
            account_balance = atm.get_bank_service().get_balance(atm.get_current_card())
            
            if amount_to_withdraw > account_balance:
                print("Error: Insufficient balance.")
                return
            
            print(f"Processing withdrawal for ${amount_to_withdraw}")
            atm.withdraw_cash(amount_to_withdraw)
        elif op == OperationType.DEPOSIT_CASH:
            if len(args) == 0 or args[0] <= 0:
                print("Error: Invalid deposit amount specified.")
                return
            
            amount_to_deposit = args[0]
            print(f"Processing deposit for ${amount_to_deposit}")
            atm.deposit_cash(amount_to_deposit)
        else:
            print("Error: Invalid operation selected.")
            return
        
        # End the session after one transaction
        print("Transaction complete.")
        self.eject_card(atm)
    
    def eject_card(self, atm: 'ATM'):
        print("Ending session. Card has been ejected. Thank you for using our ATM.")
        atm.set_current_card(None)
        atm.change_state(IdleState())