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

class RoomType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    DELUXE = "DELUXE"
    SUITE = "SUITE"

class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    OCCUPIED = "OCCUPIED"

class Room:
    def __init__(self, id: str, type: RoomType, price: float):
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
    
class CreditCardPayment(Payment):
    def process_payment(self, amount: float):
        return True
    
class HotelManagementSystem:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.guests: Dict[str, Guest] = {}
            self.rooms: Dict[str, Room] = {}
            self.reservations: Dict[str, Reservation] = {}
            self.lock = threading.Lock()
            self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
    
    def add_guest(self, guest: Guest):
        self.guests[guest.id] = guest

    def get_guest(self, guest_id: str) -> Optional[Guest]:
        return self.guests.get(guest_id)

    def add_room(self, room: Room):
        self.rooms[room.id] = room

    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)
    
    def book_room(self, guest: Guest, room: Room, check_in_date: date, check_out_date: date) -> Optional[Reservation]:
        with self.lock:
            if room.status == RoomStatus.AVAILABLE:
                room.book()
                reservation_id = self._generate_reservation_id()
                reservation = Reservation(reservation_id, guest, room, check_in_date, check_out_date)
                self.reservations[reservation_id] = reservation
                return reservation
            return None
        
    def cancel_reservation(self, reservation_id: str):
        with self.lock:
            reservation = self.reservations.get(reservation_id)
            if reservation:
                reservation.cancel()
                del self.reservations[reservation_id]

    def check_in(self, reservation_id: str):
        with self.lock:
            reservation = self.reservations.get(reservation_id)
            if reservation and reservation.status == ReservationStatus.CONFIRMED:
                reservation.room.check_in()
            else:
                raise ValueError("Invalid reservation or reservation not confirmed.")
            
    def check_out(self, reservation_id: str, payment: Payment):
        with self.lock:
            reservation = self.reservations.get(reservation_id)
            if reservation and reservation.status == ReservationStatus.CONFIRMED:
                room = reservation.room
                amount = room.price * (reservation.check_out_date - reservation.check_in_date).days
                if payment.process_payment(amount):
                    room.check_out()
                    del self.reservations[reservation_id]
                else:
                    raise ValueError("Payment failed.")
            else:
                raise ValueError("Invalid reservation or reservation not confirmed.")

    def _generate_reservation_id(self) -> str:
        return f"RES{uuid.uuid4().hex[:8].upper()}"
    
class HotelManagementSystemDemo:
    @staticmethod
    def run():
        hotel_management_system = HotelManagementSystem.get_instance()

        # Create guests
        guest1 = Guest("G001", "John Doe", "john@example.com", "1234567890")
        guest2 = Guest("G002", "Jane Smith", "jane@example.com", "9876543210")
        hotel_management_system.add_guest(guest1)
        hotel_management_system.add_guest(guest2)

        # Create rooms
        room1 = Room("R001", RoomType.SINGLE, 100.0)
        room2 = Room("R002", RoomType.DOUBLE, 200.0)
        hotel_management_system.add_room(room1)
        hotel_management_system.add_room(room2)

        # Book a room
        check_in_date = date.today()
        check_out_date = check_in_date.replace(day=check_in_date.day + 3)
        reservation1 = hotel_management_system.book_room(guest1, room1, check_in_date, check_out_date)
        if reservation1:
            print(f"Reservation created: {reservation1.id}")
        else:
            print("Room not available for booking.")

        # Check-in
        hotel_management_system.check_in(reservation1.id)
        print(f"Checked in: {reservation1.id}")

        # Check-out and process payment
        payment = CreditCardPayment()
        hotel_management_system.check_out(reservation1.id, payment)
        print(f"Checked out: {reservation1.id}")

        # Cancel a reservation
        hotel_management_system.cancel_reservation(reservation1.id)
        print(f"Reservation cancelled: {reservation1.id}")

if __name__ == "__main__":
    HotelManagementSystemDemo.run()
