# requirenments

# 1. the system will manage different type of vehicles (car, truck, motorcycle)
# 2. Vechiles will enter and exit after making payment only
# 3. Ap parking lot is assigned upon enter and freed upon exit
# 4. Payemnet must be completed before exiting
# 5. The system should handle different vechile size and slot allocation efficiently
# 6. Allows mulltiple payent methods

# iDentifying Key Components
from abc import ABC, abstractmethod
from enum import Enum
import uuid
import time
import threading
from collections import defaultdict
from typing import Dict, Optional, List

class VechileSize(Enum):
    SMALL = "SMALL"
    MEDUIM = "MEDUIM"
    LARGE = "LARGE"

class Vechile(ABC):
    def __init__(self, license_number: str, size: VechileSize):
        self.license_number = license_number
        self.size = size

    def get_license_number(self):
        return self.license_number
    
    def get_vechile_size(self):
        return self.size
    
class Bike(Vechile):
    def __init__(self, license_number: str):
        super().__init__(license_number, VechileSize.SMALL)

class Car(Vechile):
    def __init__(self, license_number):
        super().__init__(license_number, VechileSize.MEDUIM)

class Truck(Vechile):
    def __init__(self, license_number):
        super().__init__(license_number, VechileSize.LARGE)

class ParkingSpot:
    def __init__(self, spot_id: str, spot_size: VechileSize):
        self.spot_id = spot_id
        self.spot_size = spot_size
        self.is_occupied = False
        self.parked_vechile = None
        self._thread = threading.Lock()

    def get_spot_id(self):
        return self.spot_id

    def get_spot_size(self):
        return self.spot_size
        
    def is_occupied_spot(self):
        return self.is_occupied
    
    def park_vechile(self, vechile: Vechile):
        with self._thread:
            self.parked_vechile = vechile
            self.is_occupied = True

    def unpark_vechile(self):
        with self._thread:
            self. parked_vechile = None
            self.is_occupied = False

    def can_fit_vechle(self, vechile: Vechile):
        if self.is_occupied:
            return False
        if vechile.get_vechile_size() == VechileSize.SMALL:
            return self.spot_size == VechileSize.SMALL
        elif vechile.get_vechile_size() == VechileSize.MEDUIM:
            return self.spot_size == VechileSize.MEDUIM or self.spot_size == VechileSize.LARGE
        elif vechile.get_vechile_size() == VechileSize.LARGE:
            return self.spot_size == VechileSize.LARGE
        else:
            return False

class ParkingTicket:
    def __init__(self, vechile: Vechile, spot: ParkingSpot):
        self.ticket_id = str(uuid.uuid4())
        self.vechile = vechile
        self.spot = spot
        self.entry_timestamp = int(time.time() * 1000)
        self.exit_timestamp = 0

    def get_ticket_id(self):
        return self.ticket_id
    
    def get_vechile(self):
        return self.vechile
    
    def get_spot(self):
        return self.spot
    
    def get_entry_timestamp(self):
        return self.entry_timestamp
    
    def get_exit_timestamp(self):
        return self.exit_timestamp
    
    def set_exit_timestamp(self):
        self.exit_timestamp = int(time.time() * 1000)


class ParkingFloor:
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots: Dict[str, ParkingSpot] = {}
        self._lock = threading.Lock()

    def add_spot(self, spot: ParkingSpot):
        self.spots[spot.get_spot_id()] = spot

    def find_available_spot(self, vechile: Vechile):
        with self._lock:
            available_spots = [ spot for spot in self.spots.values() if not spot.is_occupied_spot() and spot.can_fit_vechle(vechile)]
            if available_spots:
                available_spots.sort(key=lambda x: x.get_spot_size().value)
                return available_spots[0]
            return None
    
    def display_availability(self):
        print(f"--- Floor {self.floor_number} Availability ---")
        available_counts = defaultdict()
        for spot in self.spots.values():
            if not spot.is_occupied_spot():
                available_counts[spot.get_spot_size()]+=1

        for size in VechileSize:
            print(f"  {size.value} spots: {available_counts[size]}")

class ParkingStrategy(ABC):
    @abstractmethod
    def find_spot(self, floors: List[ParkingFloor], vechile: Vechile):
        pass

class NearestFirstStrategy(ParkingStrategy):
    def find_spot(self, floors: List[ParkingFloor], vechile: Vechile):
        for floor in floors:
            spot = floor.find_available_spot(vechile)
            if spot is not None:
                return spot
        return None
    
class FarthestFirstStrategy(ParkingStrategy):
    def find_spot(self, floors: List[ParkingFloor], vechile: Vechile):
        reversed_floors = list(reversed(floors))
        for floor in reversed_floors:
            spot = floor.find_available_spot(vechile)
            if spot is not None:
                return spot
        return None
    

class FeeStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, parking_ticket: ParkingTicket):
        pass

class FlatRateFeeStrategy(FeeStrategy):
    RATE_PER_HOUR = 10.0
    def calculate_fee(self, parking_ticket: ParkingTicket):
         duration = parking_ticket.get_exit_timestamp() - parking_ticket.get_entry_timestamp()
         hours = (duration//(1000*60*60)) + 1
         return hours * self.RATE_PER_HOUR
    
class VechileBasedFeeStrategy(FeeStrategy):
    HOURLY_RATES = {
        VechileSize.SMALL: 10.0,
        VechileSize.MEDUIM: 20.0,
        VechileSize.LARGE: 30.0
    }

    def calculate_fee(self, parking_ticket: ParkingTicket):
        duration = parking_ticket.get_exit_timestamp() = parking_ticket.get_entry_timestamp()
        hours = (duration//(1000*60*60)) + 1
        return hours * self.HOURLY_RATES[parking_ticket.get_vechile().get_vechile_size()]
    

class ParkingLot:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if ParkingLot._instance is not None:
            raise Exception("This class is singleton")
        self. floors: List[ParkingFloor] = []
        self.active_tickets: Dict[str, ParkingTicket]= {}
        self.fee_strategy = FlatRateFeeStrategy()
        self.parking_strategy = NearestFirstStrategy()
        self._main_lock = threading.Lock()

    @staticmethod
    def get_instance():
        if ParkingLot._instance is None:
            with ParkingLot._lock:
                if ParkingLot._instance is None:
                    ParkingLot._instance = ParkingLot()
        return ParkingLot._instance
    
    def add_floor(self, floor: ParkingFloor):
        self.floors.append(floor)

    def set_fee_strategy(self, fee_strategy: FeeStrategy):
        self.fee_strategy = fee_strategy

    def set_parking_strategy(self, parking_strategy: ParkingStrategy):
        self.parking_strategy = parking_strategy

    def park_vechile(self, vehicle: Vechile):
        with self._main_lock:
            spot = self.parking_strategy.find_spot(self.floors, vehicle)
            if spot is not None:
                spot.park_vechile(vehicle)
                ticket = ParkingTicket(vehicle, spot)
                self.active_tickets[vehicle.get_license_number()] = ticket
                print(f"Vehicle {vehicle.get_license_number()} parked at spot {spot.get_spot_id()}")
                return ticket
            else:
                print(f"No available spot for vehicle {vehicle.get_license_number()}")
                return None
            
    def unpark_vechile(self, license_number: str):
        with self._main_lock:
            ticket = self.active_tickets.pop(license_number, None)
            if ticket is None:
                print(f"Ticket not found for vehicle {license_number}")
                return None
            ticket.get_spot().unpark_vechile()
            ticket.set_exit_timestamp()
            fee = self.fee_strategy.calculate_fee(ticket)
            print(f"Vehicle {license_number} unparked from spot {ticket.get_spot().get_spot_id()}")
            return fee