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
import time
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
    def pay(self, amount: float) -> Payment:
        pass

class CreditCardPaymentStrategy(PaymentStrategy):
    def __init__(self, card_number: str, cvv: str):
        self.card_number = card_number
        self.cvv = cvv

    def pay(self, amount: float) -> Payment:
        print(f"Processing credit card payment of ${amount:.2f}")
        # Simulate payment gateway interaction
        payment_success = random.random() > 0.05  # 95% success rate
        return Payment(
            amount,
            PaymentStatus.SUCCESS if payment_success else PaymentStatus.FAILURE,
            f"TXN_{uuid.uuid4()}"
        )
    
class SeatLockManager:
    def __init__(self):
        self.locked_seats: Dict[Show, Dict[Seat, str]] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.LOCK_TIMEOUT_SECONDS = 0.5

    def lock_seats(self, show: Show, seats: List[Seat], user_id: str):
        show_lock = getattr(show, '_lock', None)
        if show_lock is None:
            show._lock = threading.Lock()
            show_lock = show._lock

        with show_lock:
            for seat in seats:
                if seat.get_status() != SeatStatus.AVAILABLE:
                    print(f"Seat {seat.get_id()} is not available.")
                    return
            
            for seat in seats:
                seat.set_status(SeatStatus.LOCKED)

            if show not in self.locked_seats:
                self.locked_seats[show] = {}

            for seat in seats:
                self.locked_seats[show[seat]] = user_id

            self.executor.submit(self._unlock_after_timeout, show, seats, user_id)
            print(f"Locked seats: {[seat.get_id() for seat in seats]} for user {user_id}")
    
    def _unlock_after_timeout(self, show: Show, seats: List[Seat], user_id: str):
        time.sleep(self.LOCK_TIMEOUT_SECONDS)
        self.unlock_seats(show, seats, user_id)

    def unlock_seats(self, show: Show, seats: List[Seat], user_id: str):
        show_lock = getattr(show, '_lock', None)
        if show_lock is None:
            return
        
        with show_lock:
            show_locks = self.locked_seats.get(show)
            if show_lock is not None:
                for seat in seats:
                    if seat in show_locks and show_locks[seat] == user_id:
                        del show_lock[seat]
                        if seat.get_status() == SeatStatus.LOCKED:
                            seat.set_status(SeatStatus.AVAILABLE)
                            print(f"Unlocked seat: {seat.get_id()} due to timeout.")
                        else:
                            print(f"Unlocked seat: {seat.get_id()} due to booking completion.")
                if not show_locks:
                    del self.lock_seats[show]

    def shutdown(self):
        print("Shutting down SeatLockProvider scheduler.")
        self.executor.shutdown(wait=True)

class Booking:
    def __init__(self, booking_id: str, user: User, show: Show, seats: List[Seat], total_amount: float, payment: Payment):
        self.id = booking_id
        self.user = user
        self.show = show
        self.seats = seats
        self.total_amount = total_amount
        self.payment = payment

    def confirm_booking(self):
        for seat in self.seats:
            seat.set_status(SeatStatus.BOOKED)
    
    def get_id(self):
        return self.id
    
    def get_user(self) -> User:
        return self.user

    def get_show(self) -> Show:
        return self.show

    def get_seats(self) -> List[Seat]:
        return self.seats

    def get_total_amount(self) -> float:
        return self.total_amount

    def get_payment(self) -> Payment:
        return self.payment
    
    class BookingBuilder:
        def __init__(self):
            self.id: Optional[str] = None
            self.user: Optional[User] = None
            self.show: Optional[Show] = None
            self.seats: Optional[List[Seat]] = None
            self.total_amount: Optional[float] = None
            self.payment: Optional[Payment] = None

        def set_id(self, booking_id: str) -> 'Booking.BookingBuilder':
            self.id = booking_id
            return self

        def set_user(self, user: User) -> 'Booking.BookingBuilder':
            self.user = user
            return self

        def set_show(self, show: Show) -> 'Booking.BookingBuilder':
            self.show = show
            return self

        def set_seats(self, seats: List[Seat]) -> 'Booking.BookingBuilder':
            self.seats = seats
            return self

        def set_total_amount(self, total_amount: float) -> 'Booking.BookingBuilder':
            self.total_amount = total_amount
            return self

        def set_payment(self, payment: Payment) -> 'Booking.BookingBuilder':
            self.payment = payment
            return self
        
        def build(self) -> 'Booking':
            return Booking(self.id, self.user, self.show, self.seats, self.total_amount, self.payment)
        
class BookingManager:
    def __init__(self, seat_lock_manager: SeatLockManager):
        self.seat_lock_manager = seat_lock_manager

    def create_booking(self, user: User, show: Show, seats: List[Seat], payment_strategy: PaymentStrategy):
        self.seat_lock_manager.lock_seats(show, seats, user.get_id())
        total_amount = show.get_pricing_strategy().calculate_price(seats)
        payment = payment_strategy.pay(total_amount)
        if payment.get_status() == PaymentStatus.SUCCESS:
            booking = Booking.BookingBuilder() \
            .set_user(user) \
            .set_show(show) \
            .set_seats(seats) \
            .set_total_amount(total_amount) \
            .set_payment(payment) \
            .build()

            booking.confirm_booking()
            self.seat_lock_manager.unlock_seats(show, seats, user.get_id())
            return booking
        else:
            print("Payment failed. Please try again.")
            return None
        
class MovieBookingService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'Initialized'):
            return
        self.cities: Dict[str, City] = {}
        self.cinemas: Dict[str, Cinema] = {}
        self.movies: Dict[str, Movie] = {}
        self.users: Dict[str, User] = {}
        self.show: Dict[str, Show] = {}

        self.seat_lock_manager = SeatLockManager()
        self.booking_manager = BookingManager(self.seat_lock_manager)
        self.initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
    
    def get_booking_manager(self):
        return self.booking_manager
    
    def add_city(self, city_id: str, name: str):
        city = City(city_id, name)
        self.cities[city.get_id()] = city
        return city