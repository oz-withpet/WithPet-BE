import json
import os
from django.conf import settings
from typing import List, Dict, Optional


class LocationService:
    _provinces = None
    _districts = None
    _neighborhoods = None

    @classmethod
    def _get_data_path(cls, filename: str) -> str:

        base_dir = settings.BASE_DIR
        return os.path.join(base_dir, 'apps', 'maps', 'utils', filename)

    @classmethod
    def _load_json(cls, filename: str) -> List[Dict]:

        file_path = cls._get_data_path(filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def get_provinces(cls) -> List[Dict]:

        if cls._provinces is None:
            cls._provinces = cls._load_json('1_provinces.json')
        return cls._provinces

    @classmethod
    def get_districts(cls, province_code: Optional[int] = None) -> List[Dict]:

        if cls._districts is None:
            cls._districts = cls._load_json('2_districts.json')

        if province_code is None:
            return cls._districts

# province_code 필터링
        return [
            district for district in cls._districts
            if district['province_code'] == province_code
        ]

    @classmethod
    def get_neighborhoods(cls, province_code: Optional[int] = None,
                          district_code: Optional[int] = None) -> List[Dict]:

        if cls._neighborhoods is None:
            cls._neighborhoods = cls._load_json('3_neighborhoods.json')

        result = cls._neighborhoods

# province_code 필터링
        if province_code is not None:
            result = [
                neighborhood for neighborhood in result
                if neighborhood['province_code'] == province_code
            ]

# district_code 필터링
        if district_code is not None:
            result = [
                neighborhood for neighborhood in result
                if neighborhood['district_code'] == district_code
            ]

        return result

    @classmethod
    def get_province_by_code(cls, province_code: int) -> Optional[Dict]:

        provinces = cls.get_provinces()
        for province in provinces:
            if province['province_code'] == province_code:
                return province
        return None

    @classmethod
    def get_district_by_code(cls, district_code: int) -> Optional[Dict]:

        districts = cls.get_districts()
        for district in districts:
            if district['district_code'] == district_code:
                return district
        return None