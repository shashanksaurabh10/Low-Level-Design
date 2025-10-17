from typing import Dict

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cacpacity = capacity
        self.cache: Dict[str, Node] = {}
        self.head = Node(-1, -1)
        self.tail = Node(-1,-1)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add(self, node: Node):
        next_node = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = next_node
        next_node.prev = node

    def _remove(self, node: Node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def get(self, key:int):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add(node)
        return node.value
    
    def put(self, key:int, value:int):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            del self.cache[key]

        if len(self.cache) >= self.cacpacity:
            node = self.tail.prev
            del self.cache[node.key]
            self._remove(node)

        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add(new_node)
