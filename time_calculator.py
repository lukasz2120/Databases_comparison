"""Kontekst menadzera czasu"""

from contextlib import contextmanager
import time

@contextmanager
def time_tracker(operation):
    start_time = time.time()
    yield 
    end_time = time.time()
    print(f"Polecenie {operation} trwało: {end_time - start_time:.4f} sekund")

