import time
from collections import deque
from typing import Dict

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        Ініціалізація лімітеру.
        :param window_size: розмір вікна у секундах
        :param max_requests: максимальна кількість повідомлень у вікні
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_windows: Dict[str, deque] = {}  # історія повідомлень для кожного користувача

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Очищує застарілі повідомлення користувача із поточного вікна.
        Якщо після очищення deque пустий, видаляє користувача з історії.
        """
        if user_id not in self.user_windows:
            return

        window = self.user_windows[user_id]
        # Видаляємо всі повідомлення, що старіші за window_size
        while window and current_time - window[0] >= self.window_size:
            window.popleft()

        # Якщо повідомлень не залишилося, видаляємо користувача
        if not window:
            del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи можна відправити повідомлення у поточному вікні.
        :return: True, якщо можна; False, якщо ліміт перевищено
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_windows:
            return True  # перше повідомлення завжди дозволено

        return len(self.user_windows[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Записує нове повідомлення користувача, якщо дозволено.
        :return: True, якщо повідомлення записане, False — якщо перевищено ліміт
        """
        if self.can_send_message(user_id):
            current_time = time.time()
            if user_id not in self.user_windows:
                self.user_windows[user_id] = deque()
            self.user_windows[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Обчислює час очікування до наступного дозволеного повідомлення.
        :return: час у секундах
        """
        current_time = time.time()
        if user_id not in self.user_windows or not self.user_windows[user_id]:
            return 0.0

        oldest_time = self.user_windows[user_id][0]
        wait_time = self.window_size - (current_time - oldest_time)
        return max(wait_time, 0.0)


# -------------------------------
# Тестування
# -------------------------------
import random

def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()