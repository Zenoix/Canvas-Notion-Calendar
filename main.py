from src.canvas import CanvasAPIInterface
from src.notion import NotionAPIInterface


def main() -> None:
    c = CanvasAPIInterface()
    c.run()
    assignments = c.assignments

    n = NotionAPIInterface()
    n.assignments = assignments
    n.run()


if __name__ == "__main__":
    main()
