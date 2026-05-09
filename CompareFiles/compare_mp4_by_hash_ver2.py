from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import hashlib
import time

def get_sha256(file_path, block_size=65536):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(block_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def collect_mp4_files(root_dir):
    """폴더 내 모든 .mp4 파일의 절대 경로를 리스트로 반환"""
    mp4_files = []
    for root, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.mp4'):
                mp4_files.append(os.path.join(root, filename))
    return mp4_files

def calculate_hashes_with_threads(file_list, folder_name, max_workers=4):
    """스레드를 사용하여 파일 리스트에서 해시값을 계산하며 남은 시간을 분:초 단위로 표시"""
    file_hashes = {}
    total_files = len(file_list)
    start_time = time.time()  # 시작 시간 기록

    # ThreadPoolExecutor를 사용하여 병렬 처리
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(get_sha256, file_path): file_path for file_path in file_list}
        for idx, future in enumerate(as_completed(future_to_file), start=1):
            file_path = future_to_file[future]
            try:
                file_hash = future.result()
                if file_hash:
                    file_hashes[file_hash] = file_path
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

            # 진행률 및 남은 시간 계산
            elapsed_time = time.time() - start_time
            avg_time_per_file = elapsed_time / idx
            remaining_files = total_files - idx
            estimated_remaining_time = avg_time_per_file * remaining_files

            # 남은 시간을 분:초 형식으로 변환
            minutes, seconds = divmod(int(estimated_remaining_time), 60)

            # 진행률 및 남은 시간 출력
            print(
                f"🔄 [{folder_name}] 해시 계산 중: {idx}/{total_files} "
                f"({(idx / total_files) * 100:.2f}%) - "
                f"남은 시간: {minutes}분 {seconds}초", end='\r'
            )
    print()  # 진행률 출력 완료 후 줄바꿈
    return file_hashes

def compare_hashes(hash_dict_A, hash_dict_B):
    """두 딕셔너리를 비교하여 일치/불일치 파일을 반환"""
    unmatched_in_A = {h: path for h, path in hash_dict_A.items() if h not in hash_dict_B}
    unmatched_in_B = {h: path for h, path in hash_dict_B.items() if h not in hash_dict_A}
    matched_files = {h: (hash_dict_A[h], hash_dict_B[h]) for h in hash_dict_A if h in hash_dict_B}
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

    print("\n📦 폴더 A의 .mp4 파일 수집 중...")
    filesA = collect_mp4_files(folderA)
    print(f"폴더 A에서 발견된 .mp4 파일 수: {len(filesA)}개")

    print("📦 폴더 B의 .mp4 파일 수집 중...")
    filesB = collect_mp4_files(folderB)
    print(f"폴더 B에서 발견된 .mp4 파일 수: {len(filesB)}개")

    print("\n🔑 폴더 A의 해시값 계산 중...")
    hash_dict_A = calculate_hashes_with_threads(filesA, "폴더 A")

    print("\n🔑 폴더 B의 해시값 계산 중...")
    hash_dict_B = calculate_hashes_with_threads(filesB, "폴더 B")

    print("\n📊 파일 비교 중...")
    unmatched_A, unmatched_B, matched_files = compare_hashes(hash_dict_A, hash_dict_B)

    output_file = "unmatched_files_both_sides.txt"
    save_results(unmatched_A, unmatched_B, matched_files, output_file)

    print("\n✅ 비교 완료! 결과가 'unmatched_files_both_sides.txt'에 저장되었습니다.")
    print(f"📁 A에는 있고 B에는 없는 파일 수: {len(unmatched_A)}개")
    print(f"📁 B에는 있고 A에는 없는 파일 수: {len(unmatched_B)}개")
    print(f"📁 A와 B에서 일치하는 파일 수: {len(matched_files)}개")

if __name__ == "__main__":
    main()
