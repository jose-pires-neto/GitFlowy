import sys
from gitflowy.main_app import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAssistente encerrado.")
        sys.exit(0)