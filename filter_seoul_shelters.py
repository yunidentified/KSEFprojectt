"""공공대피소(이재민 임시주거시설) 데이터에서 서울특별시 데이터만 남기는 스크립트.

사용법:
    python filter_seoul_shelters.py                      # 기본: data/shelter_sample.csv
    python filter_seoul_shelters.py 입력.csv 출력.csv

CSV 구조:
    1행: 영문 컬럼명 (ARCD, ACMDFCLTY_SN, ...)
    2행: 한글 컬럼명 (지역코드, 수용시설일련번호, ...)
    3행~: 실제 데이터
"""
import sys

import pandas as pd

INPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/shelter_sample.csv"
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "data/shelter_seoul.csv"


def read_csv(path):
    # 공공데이터 파일은 UTF-8(BOM) 또는 CP949로 배포되는 경우가 많아 둘 다 시도
    for encoding in ("utf-8-sig", "cp949"):
        try:
            # dtype=str: 지역코드 등 숫자처럼 보이는 코드 값이 변형되지 않도록 문자열로 읽음
            return pd.read_csv(path, dtype=str, keep_default_na=False, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"인코딩을 알 수 없습니다: {path}")


df = read_csv(INPUT_PATH)

# 2행(한글 컬럼명)은 데이터가 아니므로 분리해 두었다가 저장할 때 다시 붙임
korean_header = df.iloc[[0]]
data = df.iloc[1:]

# 서울특별시 판별:
#  - 지역코드(ARCD)가 '11'로 시작 (서울특별시 행정구역 코드)
#  - 또는 지진옥외대피장소주소 / 도로명상세주소가 '서울'로 시작
# 도로명상세주소는 비어 있는 행이 있어서 여러 기준을 함께 사용
is_seoul = (
    data["ARCD"].str.startswith("11")
    | data["EQK_ACMDFCLTY_ADRES"].str.strip().str.startswith("서울")
    | data["RN_DTL_ADRES"].str.strip().str.startswith("서울")
)
seoul = data[is_seoul]

pd.concat([korean_header, seoul]).to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print(f"전체 {len(data)}건 중 서울특별시 {len(seoul)}건을 {OUTPUT_PATH}에 저장했습니다.")
print(seoul[["VT_ACMDFCLTY_NM", "EQK_ACMDFCLTY_ADRES"]].to_string(index=False))
