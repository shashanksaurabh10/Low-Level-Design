#Requirements

# 1. The hotel management system should allow guests to book rooms, check-in and check out.
# 2. The system should manage different types of room. such as single, double, deluxe, and suite
# 3. The system should handle room availabilty and reservation status
# 4. The system should allow hotel staff to manage guest information, room assignments and billing
# 5. The system should support multiple payment methods such as cash, credit card and online payment
# 6. The system should handle concurrent bookings and ensure data consistency.
# 7. The system should provide reporting and analytics features for hotel management.
# 8. The system should be scalable and handle a large number of rooms and guests.

from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import date
from typing import Dict, Optional
import uuid

class Guest:
    def __init__(self, guest_id: str, name: str, email: str, phone_number: str):
        self._id = guest_id
        self._name = name
        self._email = email
        self._phone_number = phone_number

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    
    @property
    def email(self):
        return self._email
    
    @property
    def phone_number(self):
        return self._phone_number
    
class Roomtype(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    DELUXE = "DELUXE"
    SUITE = "SUITE"

class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    OCCUPIED = "OCCUPIED"

class Room:
    def __init__(self, id: str, type: Roomtype, price: float):
        self.id = id
        self.type = type
        self.price = price
        self.status = RoomStatus.AVAILABLE
        self.lock = threading.Lock()

    def book(self):
        with self.lock:
            if self.status == RoomStatus.AVAILABLE:
                self.status = RoomStatus.BOOKED
            else:
                raise ValueError("Room is not available for booking")
            
    def check_in(self):
        with self.lock:
            if self.status == RoomStatus.BOOKED:
                self.status = RoomStatus.OCCUPIED
            else:
                raise ValueError("Room is not booked")
            
    def check_out(self):
        with self.lock:
            if self.status == RoomStatus.OCCUPIED:
                self.status = RoomStatus.AVAILABLE
            else:
                raise ValueError("Room is not occupied")

class ReservationStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Reservation:
    def __init__(self, id: str, guest: Guest, room: Room, check_in_date: date, check_out_date: date):
        self.id = id
        self.guest = guest
        self.room = room
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.status = ReservationStatus.CONFIRMED
        self.lock = threading.Lock()

    def cancel(self):
        with self.lock:
            if self.status == ReservationStatus.CONFIRMED:
                self.status = ReservationStatus.CANCELLED
                self.room.check_out()
            else:
                raise ValueError("Reservation is not confirmed")
            
class Payment(ABC):
    @abstractmethod
    def process_payment(self, amount: float):
        pass

class CashPayment(Payment):
    def process_payment(self, amount: float):
        return True
    
class CreditcardPayment(Payment):
    def process_payment(self, amount: float):
        return True
    
