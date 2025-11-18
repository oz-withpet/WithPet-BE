# 🐾 1팀 떼껄룩 [BE] - WithPet

반려동물과 함께하는 삶을 더 편리하고 풍요롭게 만드는 서비스 **WithPet**의 백엔드 레포지토리입니다.

## 🚀 프로젝트 소개

**WithPet**은 반려동물 관련 정보와 서비스를 한곳에 모은 통합 플랫폼입니다.
지도 기반으로 병원, 미용실, 식당 등 반려동물 친화 장소를 쉽게 찾을 수 있으며,
관련 용품을 구매할 수 있는 쇼핑 기능과 유저간의 소통을 위한 커뮤니티 기능을 함께 제공합니다.

---

## 🌐 배포 링크

> **https://oz-withpet.kro.kr/**

---

## 🛠️ 사용 스택 (Tech Stack)

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white"/>
  <br/>
  <img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white"/>
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"/>
  <img src="https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyCharm-000000?style=for-the-badge&logo=pycharm&logoColor=white"/>
  <img src="https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white"/>
</p>

---

## 🧑‍💻 팀 동료 (BE)

| 이름 | GitHub |
| :---: | :---: |
| 서웅비 | [@UNGBI78](https://github.com/UNGBI78) |
| 김지선 | [@summer5](https://github.com/summer5) |
| 최선구 | [@dothebest9](https://github.com/dothebest9) |
| 박재현 | [@chdan-hub](https://github.com/chdan-hub) |

---

## 📜 프로젝트 규칙

### 1. Branch Strategy

-   브랜치 이름 형식: `[작업사항]/[폴더이름 or 기능이름]/[순서번호]`
-   `[작업사항]`: `feature`, `fix`, `chore` 등 작업의 성격
-   `[폴더이름 or 기능이름]`: 해당 작업이 영향을 주는 영역 혹은 기능
-   `[순서번호]`: `01`부터 시작
-   **예시:**
    ```
    feature/model/01
    test/api/02
    fix/auth/03
    ```

### 2. Git Commit Convention

커밋 시 아래 키워드 + 간결한 설명 형식을 사용합니다.

-   `update`: 해당 파일에 새로운 기능이 생김
-   `add`: 없던 파일을 생성함 / 초기 설정
-   `bugfix`: 버그 수정
-   `refactor`: 코드 리팩토링 (기능 변경 없음, 코드 구조만 개선)
-   `fix`: 코드 수정 (기능이나 동작이 잘못된 부분 수정)
-   `move`: 파일을 옮김／정리
-   `del`: 기능／파일을 삭제
-   `test`: 테스트 코드를 작성
-   `style`: CSS 변경／스타일 관련 작업
-   `gitfix`: `.gitignore` 수정 등 Git 관련 설정 수정
-   `comment`: 주석 변경
-   `script`: 스크립트 변경 (예: 빌드 스크립트, 셸 스크립트 등)

### 3. Code Convention

1.  PK 필드명은 `user_id`가 아닌 `id` 로 통일합니다. (테이블 이름에 명시되어 있으면 수식어 제거, 예: `user_name` -> `name`)
2.  **SOFT DELETE** 사용을 기본으로 합니다. (개인 정보 보호 등)
3.  필드의 `null` 상태 허용 여부를 명확히 정의합니다. (`nullable`: 값이 없어도 가능, `required`: 반드시 존재)
4.  문자량이 많아질 것이 예상되는 필드는 `VARCHAR` 대신 `TEXT` 타입 사용을 권장합니다.
5.  PK 데이터 타입은 `BIGINT`로 통일하는 것을 권장합니다.

### 4. Communication Rules

1.  매일 정해진 시간에 데일리 스크럼을 작성합니다.
2.  FE & BE 파트 간 적극적으로 소통합니다.
3.  작업 진척도를 상시 확인하고 공유합니다.
4.  본인 작업물에 대한 테스트 (Postman 등)를 반드시 확인합니다.

---

## 📚 Documents

-   🔗 [**ERD (Entity Relationship Diagram)**](https://www.erdcloud.com/d/YEtRvPCbE3xHLDx95)
-   📋 [**테이블 명세서**](https://docs.google.com/spreadsheets/d/1y_kZm5qi8s7Xj7CxmQe8LfxRHSI3OcSoT_1y8mf8QRA/edit?usp:sharing)
-   📑 [**사용자 요구사항 정의서**](https://docs.google.com/spreadsheets/d/1eA8W5ui6Hi7UqFa8Pxi7xmMB2SO13jFUsfD0VAg65as/edit?usp:sharing)
-   📡 [**API 명세서**](https://docs.google.com/spreadsheets/d/10wZIDo5xuyMk-vQmqqz3vU_DS1V-9BNb5ObgflVCHJ4/edit?gid=1760576691#gid=1760576691)
-   🚀 [**API Hub (Swagger)**](https://app.swaggerhub.com/apis/pet_api/pet_API/1.0.0)
