import pandas as pd

# -----------------------------
# 이전 두 문장과 현재 문장을 포함한 문맥 추가 함수
# -----------------------------
def add_context(input_tsv, output_tsv):
    df = pd.read_csv(input_tsv, sep='\t')

    en_contexts, ko_contexts = [], []

    for i in range(len(df)):
        prev_en_2 = df.iloc[i-2]["en_XX"] if i >= 2 else "NULL"
        prev_en_1 = df.iloc[i-1]["en_XX"] if i >= 1 else "NULL"
        prev_ko_2 = df.iloc[i-2]["ko_KR"] if i >= 2 else "NULL"
        prev_ko_1 = df.iloc[i-1]["ko_KR"] if i >= 1 else "NULL"

        en_context = f"{prev_en_2}\\n{prev_en_1}\\n{df.iloc[i]['en_XX']}"
        ko_context = f"{prev_ko_2}\\n{prev_ko_1}\\n{df.iloc[i]['ko_KR']}"

        en_contexts.append(en_context)
        ko_contexts.append(ko_context)

    df["en_XX"] = en_contexts
    df["ko_KR"] = ko_contexts
    df.to_csv(output_tsv, sep='\t', index=False, encoding="utf-8-sig")

    print(f"문맥 추가 완료: {output_tsv} ({len(df)} 문장)")
