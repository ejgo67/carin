import argparse

def print_gugudan(start=2, end=9):
    for i in range(start, end + 1):
        print(f"{i}단:")
        for j in range(1, 10):
            print(f"{i} x {j} = {i * j}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="구구단을 출력하는 스크립트입니다.")
    parser.add_argument("--start", type=int, default=2, help="시작 단을 지정합니다 (기본값: 2)")
    parser.add_argument("--end", type=int, default=9, help="끝 단을 지정합니다 (기본값: 9)")
    args = parser.parse_args()
    print_gugudan(start=args.start, end=args.end)
