PROVINCE_MAP = {
    'seoul': '서울특별시',
    'busan': '부산광역시',
    'daegu': '대구광역시',
    'incheon': '인천광역시',
    'gwangju': '광주광역시',
    'daejeon': '대전광역시',
    'ulsan': '울산광역시',
    'sejong': '세종특별자치시',
    'gyeonggi': '경기도',
    'gangwon': '강원도',
    'chungbuk': '충청북도',
    'chungnam': '충청남도',
    'jeonbuk': '전북특별자치도',
    'jeonnam': '전라남도',
    'gyeongbuk': '경상북도',
    'gyeongnam': '경상남도',
    'jeju': '제주특별자치도',
}

PROVINCE_REVERSE_MAP = {v: k for k, v in PROVINCE_MAP.items() if k not in ['gyeonggido']}

DISTRICT_MAP = {
    'suwon': '수원시',
    'suwon-si': '수원시',

    # 서울 구들
    'gangnam': '강남구',
    'gangnam-gu': '강남구',
    'seocho': '서초구',
    'seocho-gu': '서초구',
    'songpa': '송파구',
    'songpa-gu': '송파구',
    'gangdong': '강동구',
    'mapo': '마포구',
    'mapo-gu': '마포구',
    'yongsan': '용산구',

    # 필요한 구들 추가...
}

DISTRICT_REVERSE_MAP = {v: k for k, v in DISTRICT_MAP.items() if not k.endswith('-gu') and not k.endswith('-si')}


def to_korean_province(eng_name):
    return PROVINCE_MAP.get(eng_name.lower(), eng_name)


def to_english_province(kor_name):
    return PROVINCE_REVERSE_MAP.get(kor_name, kor_name)


def to_korean_district(eng_name):
    return DISTRICT_MAP.get(eng_name.lower(), eng_name)


def to_english_district(kor_name):
    return DISTRICT_REVERSE_MAP.get(kor_name, kor_name)