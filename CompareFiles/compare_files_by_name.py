import os

def collect_files_by_name(root_dir, extensions):
    """폴더 내 특정 확장자를 가진 파일의 이름과 경로를 딕셔너리로 반환"""
    files = {}
    for root, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in extensions):
                full_path = os.path.join(root, filename)
                files[filename] = full_path
    return files

def compare_files_by_name(filesA, filesB):
    """두 딕셔너리를 비교하여 일치/불일치 파일을 반환"""
    unmatched_in_A = {name: path for name, path in filesA.items() if name not in filesB}
    unmatched_in_B = {name: path for name, path in filesB.items() if name not in filesA}
    matched_files = {name: (filesA[name], filesB[name]) for name in filesA if name in filesB}
    return unmatched_in_A, unmatched_in_B, matched_files

def save_results(unmatched_A, unmatched_B, matched_files, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        # A에만 있는 파일
        f.write("=== 📁 폴더 A에는 있지만 B에는 없는 파일 ===\n")
        for path in unmatched_A.values():
            f.write(f"{path}\n")
        f.write(f"총 {len(unmatched_A)}개\n\n")

        # B에만 있는 파일
        f.write("=== 📁 폴더 B에는 있지만 A에는 없는 파일 ===\n")
        for path in unmatched_B.values():
            f.write(f"{path}\n")
        f.write(f"총 {len(unmatched_B)}개\n\n")

        # 일치하는 파일
        f.write("=== 📁 폴더 A와 B에서 일치하는 파일 ===\n")
        for pathA, pathB in matched_files.values():
            f.write(f"{pathA} ↔ {pathB}\n")
        f.write(f"총 {len(matched_files)}개\n")

def main():
    print("🔎 비교할 두 개의 폴더 경로를 입력하세요.")
    folderA = input("📁 폴더 A 경로: ").strip('" ')
    folderB = input("📁 폴더 B 경로: ").strip('" ')

    if not os.path.exists(folderA):
        print(f"[오류] 폴더 A를 찾을 수 없습니다: {folderA}")
        return
    if not os.path.exists(folderB):
        print(f"[오류] 폴더 B를 찾을 수 없습니다: {folderB}")
        return

    # 비교할 확장자 설정
    extensions = ['.mp4', '.zip', '.txt', '.jpg']

    print("\n📦 폴더 A의 파일 수집 중...")
    filesA = collect_files_by_name(folderA, extensions)
    print(f"폴더 A에서 발견된 파일 수: {len(filesA)}개")

    print("📦 폴더 B의 파일 수집 중...")
    filesB = collect_files_by_name(folderB, extensions)
    print(f"폴더 B에서 발견된 파일 수: {len(filesB)}개")

    print("\n📊 파일 이름 비교 중...")
    unmatched_A, unmatched_B, matched_files = compare_files_by_name(filesA, filesB)

    output_file = "unmatched_files_by_name.txt"
    save_results(unmatched_A, unmatched_B, matched_files, output_file)

    print("\n✅ 비교 완료! 결과가 'unmatched_files_by_name.txt'에 저장되었습니다.")
    print(f"📁 A에는 있고 B에는 없는 파일 수: {len(unmatched_A)}개")
    print(f"📁 B에는 있고 A에는 없는 파일 수: {len(unmatched_B)}개")
    print(f"📁 A와 B에서 일치하는 파일 수: {len(matched_files)}개")

if __name__ == "__main__":
    main()