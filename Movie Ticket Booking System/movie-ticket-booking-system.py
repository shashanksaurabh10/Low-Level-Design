# Requirements

# 1. The system should allow users to view the list of movies playing in different theaters.
# 2. Users should be able to select a movie, theater and show timing to book tickets
# 3. The system should allow the seating arrangment of the selected show and allow users to choose seats.
# 4. Users should be able to make payments and confirm thier booking.
# 5. The system should handle concurrent bookings and ensure seat availability is updated in real time.
# 6. The system should support different types of seats (e.g. normal, premium) and pricing.
# 7. The system should allow theater admin to add, update and remove movies, show, and seating arrangements.
# 8. Th e system should be scalable to handle a large number of concurrent users and bookings.

import uuid
from enum import Enum
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import random
import threading
from concurrent.futures import ThreadPoolExecutor 

class PaymentStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"

class SeatStatus(Enum):
    AVAILABLE = "AVAILABLE"
    LOCKED = "LOCKED"
    BOOKED = "BOOKED"

class SeatType(Enum):
    REGULAR = 50.0
    PREMIUM = 60.0
    RECLINER = 120.0

    def get_price(self):
        return self.value

class User:
    def __init__(self, name: str, email: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
class Seat:
    def __init__(self, seat_id: str, row: int, col: int, seat_type: SeatType):
        self.id = seat_id
        self.row = row
        self.col = col
        self.type = seat_type
        self.status = SeatStatus.AVAILABLE

    def get_id(self):
        return self.id
    
    def get_row(self):
        return self.row
    
    def get_col(self):
        return self.col
    
    def get_type(self):
        return self.type

    def get_status(self):
        return self.status
    
    def set_status(self, status: SeatStatus):
        self.status = status

class City:
    def __init__(self, city_id: str, name: str):
        self.id = city_id
        self.name = name

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name

class Screen:
    def __init__(self, screen_id: str):
        self.id = screen_id
        self.seats: List[Seat] = []

    def add_seat(self, seat: Seat):
        self.seats.append(seat)

    def get_id(self):
        return self.id
    
    def get_seats(self):
        return self.seats
    
class Cinema:
    def __init__(self, cinema_id: str, name: str, city: City, screens: List[Screen]):
        self.id = cinema_id
        self.name = name
        self.city = city
        self.screens = screens

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def get_city(self):
        return self.city
    
    def get_screen(self):
        return self.screens
    
class MovieObserver(ABC):
    @abstractmethod
    def update(self, movie: 'Movie'):
        pass

class MovieSubject:
    def __init__(self):
        self.observers: List[MovieObserver] = []

    def add_observer(self, observer: MovieObserver):
        self.observers.append(observer)

    def remove_observer(self, observer: MovieObserver):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observer(self):
        for observer in self.observers:
            observer.update(self)

class UserObserver(MovieObserver):
    def __init__(self, user: User):
        self.user = user

    def update(self, movie: 'Movie'):
        print(f"Notification for {self.user.get_name()} ({self.user.get_id()}): Movie '{movie.get_title()}' is now available for booking!")

class Movie(MovieSubject):
    def __init__(self, movie_id: str, title: str, duration_in_minutes: int):
        super().__init__()
        self.id = movie_id
        self.title = title
        self.duration_in_minutes = duration_in_minutes

    def get_id(self):
        return self.id
    
    def get_title(self):
        return self.title

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, seats: List[Seat]):
        pass

class WeekdayPricingStartegy(PricingStrategy):
    def calculate_price(self, seats: List[Seat]):
        return sum(seat.get_type().get_price() for seat in seats)
    
class WeekendPricingStartegy(PricingStrategy):
    WEEKEND_SURCHARGE = 1.2
    def calculate_price(self, seats: List[Seat]):
        base_price = sum(seat.get_type().get_price() for seat in seats)
        return base_price * self.WEEKEND_SURCHARGE

class Show:
    def __init__(self, show_id: str, movie: Movie, screen: Screen, start_time: datetime, pricing_strategy: PricingStrategy):
        self.id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time
        self.pricing_strategy = pricing_strategy

    def get_id(self):
        return self.id

    def get_movie(self):
        return self.movie

    def get_screen(self):
        return self.screen

    def get_start_time(self):
        return self.start_time

    def get_pricing_strategy(self):
        return self.pricing_strategy

class Payment:
    def __init__(self, amount: float, status: PaymentStatus, transaction_id: str):
        self.id = str(uuid.uuid4())
        self.amount = amount
        self.status = status
        self.transaction_id = transaction_id

    def get_status(self):
        return self.status

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float):
        pass

class CreditCardPaymentStrategy(PaymentStrategy):
    def __init__(self, card_number: str, cvv: str):
        self.card_number = card_number
        self.cvv = cvv

    def pay(self, amount: float):
        print(f"Processing credit card payment of ${amount:.2f}")
        # Simulate payment gateway interaction
        payment_success = random.random() > 0.05  # 95% success rate
        return Payment(
            amount,
            PaymentStatus.SUCCESS if payment_success else PaymentStatus.FAILURE,
            f"TXN_{uuid.uuid4()}"
        )