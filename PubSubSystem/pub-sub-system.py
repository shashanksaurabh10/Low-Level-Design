#  REquirenments

# 1. The pub - sub syatem should allow publishers to publish messages to specific topics
# 2. Subscribers should be able to subscribe to topics of interest and recieve messages published to those topics.
# 3. the system should support multiple publishers and subscribers
# 4. Message should be delivered to all subscribers of a topic in real-time
# 5. The system should handle concurrent access and ensure thread safety
# 6. The pub - sub system should be scalable and efficeint in terms of message delivery

from datetime import datetime
from abc import ABC, abstractmethod
from typing import Set, Dict
from concurrent.futures import ThreadPoolExecutor
import threading

class Message:
    def __init__(self, payload: str):
        self.payload = payload
        self.timestamp = datetime.now()

    def get_payload(self):
        return self.payload
    
    def __str__(self):
        return f"Message{{payload='{self.payload}'}}"
    
class Subscriber(ABC):
    @abstractmethod
    def get_id(self):
        pass

    def on_message(self, message: Message):
        pass

class AlertSubscriber(Subscriber):
    def __init__(self, subscriber_id):
        self.id = subscriber_id

    def get_id(self):
        return self.id
    
    def on_message(self, message: Message):
        print(f"!!! [Alert - {self.id} : {message.get_payload()}]!!!")

class NewsSubscriber(Subscriber):
    def __init__(self, subscriber_id):
        self.id = subscriber_id

    def get_id(self):
        return self.id
    
    def on_message(self, message):
        print(f"[Subscriber {self.id}] received message '{message.get_payload()}'")


class Topic:
    def __init__(self, name: str, delivery_executor: ThreadPoolExecutor):
        self.name = name
        self.delivery_executor = delivery_executor
        self.subscribers: Set[Subscriber] = set()

    def get_name(self):
        self.name

    def add_subscribers(self, subscriber: Subscriber):
        self.subscribers.add(subscriber)

    def remove_subscribers(self, subscriber: Subscriber):
        self.subscribers.discard(subscriber)

    def _deliver_message(self, subscriber: Subscriber, message: Message):
        try:
            subscriber.on_message(message)
        except Exception as e:
            print(f"Error delivering message to subscriber {subscriber.get_id()}: {str(e)}")

    def broadcast(self, message: Message):
        for subscriber in self.subscribers:
            self.delivery_executor.submit(self._deliver_message , subscriber, message)

        
class PubSubService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.topic_registry: Dict[str, Topic] = {}
        self.delivery_executor = ThreadPoolExecutor()
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
    
    def create_topic(self, topic_name: str):
        if topic_name not in self.topic_registry:
            self.topic_registry[topic_name] = Topic(topic_name, self.delivery_executor)
        print(f"Topic {topic_name} created")

    def subscribe(self, topic_name: str, subscriber: Subscriber):
        topic = self.topic_registry.get(topic_name, None)
        if topic is None:
            raise ValueError(f"Topic not found: {topic_name}")
        topic.add_subscribers(subscriber)

    def unsubscribe(self, topic_name: str, subscriber: Subscriber):
        topic = self.topic_registry.get(topic_name, None)
        if topic is not None:
            topic.remove_subscribers(subscriber)
        print(f"Subscriber '{subscriber.get_id()}' unsubscribed from topic: {topic_name}")

    def publish(self, topic_name: str, message: Message):
        print(f"Publishing message to topics:{topic_name}")
        topic = self.topic_registry.get(topic_name, None)
        if topic is None:
            raise ValueError(f"Topic not found {topic_name}")
        topic.broadcast(message)

    def shutdown(self):
        print("pubSubService shutting down")
        self.delivery_executor.shutdown(wait=True)
        print("PubSubService shutdown complete")