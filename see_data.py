from utils import load_infos

if __name__ == "__main__":
    infos = load_infos("24SideEffect")
    if len(infos) == 0:
        print("No data found!")
    infos[-1].print()
