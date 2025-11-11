from enum import Enum
from abc import ABC, abstractmethod
import uuid
from typing import Dict, Collection, List

class OrderStatus(Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PLACED = "PLACED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"

class ProductCategory(Enum):
    ELECTRONICS = "ELECTRONICS"
    BOOKS = "BOOKS"
    CLOTHING = "CLOTHING"
    HOME_GOODS = "HOME_GOODS"
    GROCERY = "GROCERY"

class OutOfStockException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class Product(ABC):
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.price: float = 0.0
        self.category: ProductCategory = None

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_category(self):
        pass

    class BaseProduct:
        def __init__(self, product_id: str, name: str, description: str, price: float, category: ProductCategory):
            self.id = product_id
            self.name = name
            self.description = description
            self.price = price
            self.category = category

        def get_id(self):
            return self.id

        def get_name(self):
            return self.name

        def get_description(self):
            return self.description

        def get_price(self):
            return self.price

        def get_category(self):
            return self.category
        
    class Builder:
        def __init__(self, name: str, price: float):
            self.name = name
            self.price = price
            self.description = ""
            self.category = None

        def with_description(self, description: str):
            self.description = description
            return self
        
        def with_category(self, category: ProductCategory):
            self.category = category
            return self
        
        def build(self):
            return Product.BaseProduct(str(uuid.uuid4()), self.name, self.description, self.price, self.category)
        
class ProductDecorator(Product):
    def __init__(self, decorated_product: Product):
        super().__init__()
        self.decorated_product = decorated_product

    def get_id(self):
        return self.decorated_product.get_id()
    
    def get_name(self):
        return self.decorated_product.get_name()
    
    def get_price(self):
        return self.decorated_product.get_price()
    
    def get_description(self):
        return self.decorated_product.get_description()
    
    def get_category(self):
        return self.decorated_product.get_category()
    
class GiftWrapDecorator(ProductDecorator):
    GIFT_WRAP_COST = 5.0
    def __init__(self, product: Product):
        super().__init__(product)

    def get_price(self):
        return super().get_price() + self.GIFT_WRAP_COST
    
    def get_description(self):
        return super().get_description() + "(Gift Wrapped)"
    
class SearchService:
    def __init__(self, product_catalog: Collection[Product]):
        self.product_catalog = product_catalog

    def search_by_name(self, name: str):
        return [p for p in self.product_catalog if name.lower() in p.get_name().lower()]
    
    def search_by_category(self, category: ProductCategory):
        return [p for p in self.product_catalog if p.get_category() == category]

class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

    def get_product(self):
        return self.product
    
    def get_quantity(self):
        return self.quantity
    
    def increment_quantity(self, amount: int):
        self.quantity +=amount

    def get_price(self):
        return self.product.get_price() * self.quantity
    
class ShoppingCart:
    def __init__(self):
        self.items: Dict[str, CartItem] = {}

    def add_item(self, product: Product, quantity: int):
        if product.get_id() in self.items:
            self.items[product.get_id()].increment_quantity(quantity)
        else:
            self.items[product.get_id()] = CartItem(product, quantity)

    def remove_item(self, product_id: str):
        if product_id in self.items:
            del self.items[product_id]

    def get_items(self):
        return self.items.copy()
    
    def calculate_total(self):
        return sum(item.get_price() for item in self.items.values())
    
    def clear_cart(self):
        self.items.clear()

class Address:
    def __init__(self, street: str, city: str, state: str, zip_code: str):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"
    
class Account:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.cart = ShoppingCart()

    def get_cart(self):
        return self.cart
    
class OrderObserver(ABC):
    @abstractmethod
    def update(self, order: 'Order'):
        pass

class Subject:
    def __init__(self):
        self.observers: List[OrderObserver] = []

    def add_observer(self, observer: OrderObserver):
        self.observers.append(observer)

    def remove_observer(self, observer: OrderObserver):
        if observer in self.observers:
            self.observers.remove(observer)
        
    def notify_observer(self, order: 'Order'):
        for observer in self.observers:
            observer.update(order)

class OrderLineItem:
    def __init__(self, product_id: str, product_name: str, quantity: int, price_at_purchase: float):
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.price_at_purchase = price_at_purchase

    def get_product_id(self):
        return self.product_id
    
    def get_quantity(self):
        return self.quantity
    
class OrderState(ABC):
    @abstractmethod
    def ship(self, order: 'Order'):
        pass

    @abstractmethod
    def deliver(self, order: 'Order'):
        pass

    @abstractmethod
    def cancel(self, order: 'Order'):
        pass

class PlacedState(OrderState):
    def ship(self, order: 'Order'):
        print(f"Shipping order {order.get_id()}")
        order.set_status(OrderStatus.SHIPPED)
        order.set_state(ShippedState())

    def deliver(self, order: 'Order'):
        print(f"Cannot deliver an order that has not been shipped.")

    def cancel(self, order: 'Order'):
        print(f"Cancelling order {order.get_id()}")
        order.set_status(OrderStatus.CANCELLED)
        order.set_state(CancelledState())

class ShippedState(OrderState):
    def ship(self, order: 'Order') -> None:
        print("Order is already shipped.")

    def deliver(self, order: 'Order') -> None:
        print(f"Delivering order {order.get_id()}")
        order.set_status(OrderStatus.DELIVERED)
        order.set_state(DeliveredState())

    def cancel(self, order: 'Order') -> None:
        print("Cannot cancel a shipped order.")

class DeliveredState(OrderState):
    def ship(self, order: 'Order') -> None:
        print("Order already delivered.")

    def deliver(self, order: 'Order') -> None:
        print("Order already delivered.")

    def cancel(self, order: 'Order') -> None:
        print("Cannot cancel a delivered order.")

class CancelledState(OrderState):
    def ship(self, order: 'Order') -> None:
        print("Cannot ship a cancelled order.")

    def deliver(self, order: 'Order') -> None:
        print("Cannot deliver a cancelled order.")

    def cancel(self, order: 'Order') -> None:
        print("Order is already cancelled.")

class Order(Subject):
    def __init__(self):
        super().__init__()