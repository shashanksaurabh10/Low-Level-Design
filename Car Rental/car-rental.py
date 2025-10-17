# Requirements

# 1. The car rental system should allow customers to browse and reserve available cars for specific dates
# 2. Each car should have details like model, make, year, license plate number and rental price perday
# 3. customers should be able to search for cars based on various criteria, such as type, price range and availability
# 4. The system should handle reservations, including creating, modifying and cancelling reservations.
# 5. The system should keep track of availability of cars and update their status accordingly
# 6. The system should handle customer information, including name, correct details and drivers license information
# 7. The system should handle payment processing for reservations.
# 8. The system should be able to handle concurrent reservations and ensure data consistency.

from abc import ABC, abstractmethod
from datetime import timedelta, date
import uuid
from typing import Dict, List

class Car:
    def __init__(self, make: str, model:str, year:str, license_plate:str, rental_price_per_day:str):
        self.make = make
        self.model = model
        self.year = year
        self.license_plate = license_plate
        self.rental_price_per_day = rental_price_per_day
        self.available = True

    def get_rental_price_per_day(self):
        return self.rental_price_per_day
    
    def get_make(self):
        return self.make
    
    def get_model(self):
        return self.get_model
    
    def get_license_plate(self):
        return self.license_plate
    
    def is_available(self):
        return self.available
    
    def set_available(self, available):
        self.available = available

class Customer:
    def __init__(self, name: str, contact_info: str, drivers_license_number: str):
        self.name = name
        self.contact_info = contact_info
        self.drivers_license_number = drivers_license_number

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

class CreditCardPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount):
        # Process credit card payment
        # ...
        return True

class PayPalPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount):
        # Process PayPal payment
        # ...
        return True
    
class Reservation:
    def __init__(self, reservation_id: str, customer_id: str, car: Car, start_date: date, end_date: date):
        self.reservation_id = reservation_id
        self.customer = customer_id
        self.start_date = start_date
        self.end_date = end_date
        self.car = car
        self.total_price = self.calculate_total_price()

    def calculate_total_price(self):
        days_rented = (self.end_date - self.start_date).days + 1
        return self.car.rental_price_per_day * days_rented
    
    def get_start_date(self):
        return self.start_date
    
    def get_end_date(self):
        return self.end_date
    
    def get_car(self):
        return self.car
    
    def get_total_price(self):
        return self.total_price
    
    def get_reservation_id(self):
        return self.reservation_id
    
class RentalSystem:
    _instance = None
    def __init__(self):
        if RentalSystem._instance is not None:
            raise Exception("This class is Singleton!!")
        
        else:
            RentalSystem._instance = self
            self.cars: Dict[str, Car] = {}
            self.reservations: Dict[str, Reservation] = {}
            self.payment_processor = CreditCardPaymentProcessor()

    @staticmethod
    def get_instance():
        if RentalSystem._instance is None:
            RentalSystem()
        return RentalSystem._instance
    
    def add_car(self, car: Car):
        self.cars[car.license_plate] = car

    def remove_car(self, license_plate):
        self.cars.pop(license_plate, None)

    def search_cars( self, make: str, model: str, start_date, end_date):
        available_cars = []
        for car in self.cars.values():
            if car.make.lower() == make.lower() and car.model.lower() == model.lower() and car.is_available():
                if self.is_car_available(car, start_date, end_date):
                    available_cars.append(car)
        return available_cars
    
    def is_car_available(self, car: Car, start_date, end_date):
        for reservation in self.reservations.values():
            if reservation.get_car() == car:
                if start_date < reservation.get_start_date() and end_date < reservation.get_end_date():
                    return False
        return True
    
    def make_reservation(self, customer, car: Car, start_date, end_date):
        if self.is_car_available(car, start_date, end_date):
            reservation_id = self.generate_reservation_id()
            reservation = Reservation(reservation_id, customer, car, start_date, end_date)
            self.reservations[reservation_id] = reservation
            car.set_available(False)
            return reservation
        return None
    
    def cancel_reservation(self, reservation_id):
        reservation = self. reservations.pop(reservation_id, None)
        if reservation is not None:
            reservation.get_car().set_available(True)

    def process_payment(self, reservation: Reservation):
        return self.payment_processor.process_payment(reservation.get_total_price())
    
    def generate_reservation_id(self):
        return "RES" + str(uuid.uuid4())[:8].upper()
    
class CarRentalSystemDemo:
    @staticmethod
    def run():
            rental_system = RentalSystem.get_instance()

            # Add cars to the rental system
            rental_system.add_car(Car("Toyota", "Camry", 2022, "ABC123", 50.0))
            rental_system.add_car(Car("Honda", "Civic", 2021, "XYZ789", 45.0))
            rental_system.add_car(Car("Ford", "Mustang", 2023, "DEF456", 80.0))

            # Create customers
            customer1 = Customer("John Doe", "john@example.com", "DL1234")
            customer2 = Customer("Jane Smith", "jane@example.com", "DL5678")

            # Make reservations
            start_date = date.today()
            end_date = start_date + timedelta(days=3)
            available_cars = rental_system.search_cars("Toyota", "Camry", start_date, end_date)

            if available_cars:
                selected_car = available_cars[0]
                reservation = rental_system.make_reservation(customer1, selected_car, start_date, end_date)
                if reservation is not None:
                    payment_success = rental_system.process_payment(reservation)
                    if payment_success:
                        print(f"Reservation successful. Reservation ID: {reservation.get_reservation_id()}")
                    else:
                        print("Payment failed. Reservation canceled.")
                        rental_system.cancel_reservation(reservation.get_reservation_id())
                else:
                    print("Selected car is not available for the given dates.")
            else:
                print("No available cars found for the given criteria.")

if __name__ == "__main__":
    CarRentalSystemDemo.run()
