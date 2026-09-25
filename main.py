import threading
import settings
import bfs
from game import Game

def main():
    threading.Thread(target=bfs.warm_up, args=(settings.MAX_PANCAKES,), daemon=True).start()
    Game().run()

if __name__ == "__main__":
    main()