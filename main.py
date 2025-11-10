from src.align_subtitles import process_folder
from src.add_context import add_context
import os

def main():
    input_dir = "data/raw"
    # output files
    aligned_tsv = "data/processed/aligned_subtitles.tsv"
    context_tsv = "data/processed/aligned_with_context.tsv"

    if not os.path.exists("data/processed"):
        os.makedirs("data/processed")

    # 자막 매칭
    process_folder(input_dir, aligned_tsv, max_diff=1000)

    # 문맥 추가
    add_context(aligned_tsv, context_tsv)

if __name__ == "__main__":
    main()
