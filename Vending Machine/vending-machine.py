# Requirements

# 1. The vending machine should support multiple products with different prices and quantities
# 2. The machine should accept coins and notes of different denominations
# 3. The machine should dispense the selected product and return chnage if necessary
# 4. The machine should keep track of the avilable products and thier quantities.
# 5. The machine should handle multiple transactions concurrently and ensure data consistency
# 6. The machine should provide an interface for restocking products and collecting money.
# 7. The machine should handle exceptions scenerios, such as insufficient funds or out-of-stock products

from typing import Dict
from abc import ABC, abstractmethod
from enum import Enum

class Item:
    def __init__(self, code: str, name: str, price: int):
        self.code = code
        self.name = name
        self.price = price

    def get_name(self):
        return self.name
    
    def get_price(self):
        return self.price
    
class Inventory:
    def __init__(self):
        self.item_map: Dict[str, Item] = {}
        self.stock_map: Dict[str, int] = {}

    def add_item(self, code: str, item: Item, quantity: int):
        self.item_map[code] = item
        self.stock_map[code] = quantity

    def get_item(self, code: str):
        return self.item_map.get(code)
    
    def is_available(self, code: str):
        return self.stock_map[code] > 0
    
    def reduce_stock(self, code: str):
        self.stock_map[code] = self.stock_map[code] - 1

class Coin(Enum):
    PENNY = 1
    NICKEL = 5
    DIME = 10
    QUARTER = 25

    def get_value(self):
        return self.value
    
class VendingMachineState(ABC):
    def __init__(self, machine: 'VendingMachine'):
        self.machine = machine

    @abstractmethod
    def insert_coin(self, coin: Coin):
        pass

    @abstractmethod
    def select_item(self, code: str):
        pass

    @abstractmethod
    def dispense(self):
        pass

    @abstractmethod
    def refund(self):
        pass

class IdleState(VendingMachineState):
    def insert_coin(self, coin):
        print("Please select an item before inserting money")

    def select_item(self, code):
        if not self.machine.get_inventory().is_available(code):
            print("Item not available")
            return
        self.machine.set_selected_item_code(code)
        self.machine.set_state(ItemSelectedState(self.machine))
        print(f"Item selected: {code}")

    def dispense(self):
        print("No Item selected.")

    def refund(self):
        print("No money to refund")

class ItemSelectedState(VendingMachineState):
    def insert_coin(self, coin: Coin):
        self.machine.add_balance(coin.get_value())
        print(f"Coin inserted: ${coin.get_value()}: ({coin.name})")

        selected_item = self.machine.get_selected_item()
        if selected_item and self.machine.get_balance() >= selected_item.get_price():
            print("Sufficient money received")
            self.machine.set_state(HasMoneyState(self.machine))

    def select_item(self, code: str):
        print("Item already selected. Please insert money or request refund to select a different item.")

    def dispense(self):
         print("Please insert sufficient money.")

    def refund(self):
        self.machine.refund_balance()
        self.machine.reset()
        self.machine.set_state(IdleState(self.machine))

class HasMoneyState(VendingMachineState):
    def insert_coin(self, coin: Coin):
        self.machine.add_balance(coin.get_value())
        print(f"Additional coin inserted: ${coin.get_value()} ({coin.name}) - will be returned as change")

    def select_item(self, code: str):
        print("Item already selected. Please dispense or request refund to select a different item.")

    def dispense(self):
        self.machine.set_state(DispenseState(self.machine))
        self.machine.dispense_item()

    def refund(self):
        self.machine.refund_balance()
        self.machine.reset()
        self.machine.set_state(IdleState(self.machine))

class DispenseState(VendingMachineState):
    def insert_coin(self, coin: Coin):
         print("Currently dispensing. Please wait.")

    def select_item(self, code: str):
         print("Currently dispensing. Please wait.")

    def dispense(self):
        print("Dispensing in progress...")

    def refund(self):
        print("Dispensing in progress. Refund not allowed.")

class VendingMachine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VendingMachine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            self.inventory = Inventory()
            self.current_state = IdleState(self)
            self.balance = 0
            self.selected_item_code = None
            self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
    
    def insert_coin(self, coin: Coin):
        self.current_state.insert_coin(coin)

    def add_item(self, code: str, name: str, price: int, quantity: int):
        item = Item(code, name, price)
        self.inventory.add_item(code, item, quantity)
        return item
    
    def select_item(self, code: str):
        self.current_state.select_item(code)

    def dispense(self):
        self.current_state.dispense()

    def dispense_item(self):
        item = self.inventory.get_item(self.selected_item_code)
        if self.balance >= item.get_price():
            self.inventory.reduce_stock(self.selected_item_code)
            self.balance -=item.get_price()
            print(f"Dispensed: {item.get_name()}")
            if self.balance > 0:
                print(f"Returning change: {self.balance}")
            self.reset()
            self.set_state(IdleState(self))

    def refund_balance(self):
        print(f"Refunding: {self.balance}")
        self.balance = 0

    def reset(self):
        self.selected_item_code = None
        self.balance = 0

    def add_balance(self, value: int):
        self.balance += value

    def get_selected_item(self):
        return self.inventory.get_item(self.selected_item_code)
    
    def set_selected_item_code(self, code: str):
        self.selected_item_code = code

    def set_state(self, state: VendingMachineState):
        self.current_state = state

    def get_inventory(self):
        return self.inventory
    
    def get_balance(self):
        return self.balance

class VendingMachineDemo:
    @staticmethod
    def main():
        vending_machine = VendingMachine.get_instance()

        # Add products to the inventory
        vending_machine.add_item("A1", "Coke", 25, 3)
        vending_machine.add_item("A2", "Pepsi", 25, 2)
        vending_machine.add_item("B1", "Water", 10, 5)

        # Select a product
        print("\n--- Step 1: Select an item ---")
        vending_machine.select_item("A1")

         # Insert coins
        print("\n--- Step 2: Insert coins ---")
        vending_machine.insert_coin(Coin.DIME)  # 10
        vending_machine.insert_coin(Coin.DIME)  # 10
        vending_machine.insert_coin(Coin.NICKEL)  # 5

        # Dispense the product
        print("\n--- Step 3: Dispense item ---")
        vending_machine.dispense()  # Should dispense Coke

        # Select another item
        print("\n--- Step 4: Select another item ---")
        vending_machine.select_item("B1")

        # Insert more amount
        print("\n--- Step 5: Insert more than needed ---")
        vending_machine.insert_coin(Coin.QUARTER)  # 25

         # Try to dispense the product
        print("\n--- Step 6: Dispense and return change ---")
        vending_machine.dispense()

if __name__ == "__main__":
    VendingMachineDemo.main()