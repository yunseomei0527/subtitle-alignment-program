import re
import os
import pysrt
import pandas as pd

# -----------------------------
# 텍스트 정제 함수
# - re: 파이썬의 정규표현식 모듈
# -----------------------------
def clean_text(text):
  text = re.sub(r"<[^>]+>", "", text) # HTML 태그 제거
  text = re.sub(r"[♪♫♩♬♭♯\"\'-]", "", text) # 음표, 따옴표, 하이픈 제거
  text = re.sub(r'\[.*?\]', '', text) # 대괄호 안의 내용 제거
  text = re.sub(r'^\s*\[.*?\]\s*$', '', text, flags=re.MULTILINE) # 줄 전체가 대괄호로 둘러싸인 설명일 경우 제거
  text = re.sub(r'\s+', ' ', text)  # 여러 공백 및 줄바꿈 제거
  text = text.strip()

  return text


# -----------------------------
# 자막 시간의 중점 찾는 함수
# -----------------------------
def midpoint(start, end):
  return (start.ordinal + end.ordinal) / 2


# -----------------------------
# 영-한 자막 매칭 함수
# -----------------------------
def align(en_path, ko_path, max_diff):  # max_diff 단위: 밀리초
  en_subs = pysrt.open(en_path)
  ko_subs = pysrt.open(ko_path)

  temp_pairs = []

  for en_sub in en_subs:
    en_mid = midpoint(en_sub.start, en_sub.end)

    # 한국어 자막 중 가장 가까운 중간 시간 찾기
    closest_ko = min(ko_subs, key=lambda ko: abs(midpoint(ko.start, ko.end) - en_mid))
    ko_mid = midpoint(closest_ko.start, closest_ko.end)

    # 시간 차이가 max_diff 이상이면 매칭 제외
    if abs(en_mid - ko_mid) <= max_diff:
      ko_text = clean_text(closest_ko.text)
    else:
      ko_text = ""  

    en_text = clean_text(en_sub.text)
    temp_pairs.append((en_text, ko_text))

  # 빈 문장 제거
  temp_pairs = [(en, ko) for en, ko in temp_pairs if en and ko]

  # 같은 한국어 문장에 여러 영어 문장 병합
  merged_dict = {}
  for en_text, ko_text in temp_pairs:
    if ko_text in merged_dict:
      merged_dict[ko_text] += " " + en_text
    else:
      merged_dict[ko_text] = en_text

  aligned_pairs = [(en, ko) for ko, en in merged_dict.items()]
  df = pd.DataFrame(aligned_pairs, columns=["en_XX", "ko_KR"])

  return df


# -----------------------------
# srt 파일 처리 함수
# -----------------------------
def process_srt_file(sub_dir, output_file, max_diff):
  all_dfs = []

  # 영어 srt 파일 목록
  en_files = [f for f in os.listdir(sub_dir) if f.endswith(".en.srt")]

  for en_file in en_files:
    title_name = en_file[:-7]  # ".en.srt" 제외
    ko_file = f"{title_name}.ko.srt"
    en_path = os.path.join(sub_dir, en_file)
    ko_path = os.path.join(sub_dir, ko_file)

    if not os.path.exists(ko_path):
      print(f"한국어 파일 없음: {title_name}")
      continue

    print(f"처리 중: {title_name}")
    # align 함수에 max_diff 전달
    df = align(en_path, ko_path, max_diff=max_diff)
    all_dfs.append(df)

  if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.drop_duplicates(inplace=True)
    final_df.to_csv(output_file, sep='\t', index=False, encoding="utf-8-sig")
    print(f"총 {len(final_df)} 문장 쌍 → {output_file}")
    

# -----------------------------
# main 함수
# -----------------------------
def main():
  subtitles_dir = "/content/drive/MyDrive/넷플 영화 자막 데이터"
  # tsv파일로 저장
  output_tsv = "./aligned_subtitles.tsv"

  # 폴더 없을 시
  if not os.path.exists(subtitles_dir):
    print(f"폴더가 존재하지 않습니다: {subtitles_dir}")
    return

  process_srt_file(subtitles_dir, output_tsv, max_diff = 1000)

  print("모든 파일 처리 완료!")

if __name__ == "__main__":
  main()