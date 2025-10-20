import random
import time

# -------------------------------
# Node та двозв’язний список
# -------------------------------
class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        node = Node(key, value)
        node.next = self.head
        if self.head:
            self.head.prev = node
        else:
            self.tail = node
        self.head = node
        return node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        if node != self.head:
            self.remove(node)
            node.next = self.head
            self.head.prev = node
            self.head = node

    def remove_last(self):
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None


# -------------------------------
# LRUCache
# -------------------------------
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # ключ -> вузол
        self.list = DoublyLinkedList()

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node


# -------------------------------
# Функції без кешу
# -------------------------------
def range_sum_no_cache(array, left, right):
    return sum(array[left:right+1])

def update_no_cache(array, index, value):
    array[index] = value


# -------------------------------
# Функції з кешем
# -------------------------------
def range_sum_with_cache(array, left, right, cache: LRUCache):
    key = (left, right)
    result = cache.get(key)
    if result == -1:
        result = sum(array[left:right+1])
        cache.put(key, result)
    return result

def update_with_cache(array, index, value, cache: LRUCache):
    array[index] = value
    keys_to_delete = [key for key in cache.cache.keys()
                      if key[0] <= index <= key[1]]
    for key in keys_to_delete:
        del cache.cache[key]


# -------------------------------
# Генератор запитів
# -------------------------------
def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries


# -------------------------------
# Основна функція тестування
# -------------------------------
def run_test(n=100_000, q=50_000):
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    # --- Без кешу ---
    arr_no_cache = array.copy()
    t1 = time.time()
    for query in queries:
        if query[0] == "Range":
            _, l, r = query
            range_sum_no_cache(arr_no_cache, l, r)
        else:
            _, i, v = query
            update_no_cache(arr_no_cache, i, v)
    t2 = time.time()
    no_cache_time = t2 - t1

    # --- З кешем ---
    arr_cache = array.copy()
    cache = LRUCache(capacity=1000)
    t3 = time.time()
    for query in queries:
        if query[0] == "Range":
            _, l, r = query
            range_sum_with_cache(arr_cache, l, r, cache)
        else:
            _, i, v = query
            update_with_cache(arr_cache, i, v, cache)
    t4 = time.time()
    cache_time = t4 - t3

    # --- Результати ---
    speedup = no_cache_time / cache_time if cache_time > 0 else float("inf")
    print(f"Без кешу : {no_cache_time:6.2f} c")
    print(f"LRU-кеш  : {cache_time:6.2f} c  (прискорення ×{speedup:.2f})")



if __name__ == "__main__":
    run_test()