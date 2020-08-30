# WeCha Backend
영화 평가 및 추천 사이트 [왓챠피디아](https://pedia.watcha.com/ko-KR) 클로닝 프로젝트 **위챠**의 백엔드 깃허브에요. _**장고**_로 만들어졌어요.<br/>
프론트 깃허브는 [이곳](https://github.com/wecode-bootcamp-korea/11-WeCha-frontend)을 방문해주세요 😉

### 개발자
- 위코드 11기 [이충희](https://github.com/choonghee-lee)
- 위코드 11기 [이용민](https://github.com/eymin1259)

### 프로젝트 기간
20.08.18 ~ 20.08.28 (10일)

# Demo
![Demo](https://images.velog.io/images/choonghee-lee/post/0dcc8e6e-5cb7-49d4-8341-c5a7e84e6dc8/demo.png)

# 🤔 어떤 기능을 클로닝 했나요?
## 🎬 영화
- 넷플릭스와 같은 서비스 제공자와 평균 별점으로 영화 랭킹을 제공해요. 서버에서 모두 정렬해서 보내줘요.
- 사용자의 평가를 기반으로 장르, 국가, 인물별 영화들을 추천해줘요. _**쿼리 스트링**_ 으로 고르면 되요!
- 영화 상세 정보를 조회할 수 있어요.
- 사용자들의 영화 컬렉션 리스트를 조회할 수 있어요.
- 영화 컬렉션의 상세 정보를 조회할 수 있어요. _**페이지네이션**_을 구현하여 프론트엔드에서 무한 스크롤을 구현할 수 있게 도와줘요.

## 👩🏻‍💻 사용자
- 이메일로 회원가입을 해요. _**bcrypt**_를 사용한 암호화는 필수! 
- _**JWT**_ 로그인을 구현했어요. 데코레이터를 이용한 _**validation**은 필수!
- 사용자는 영화를 평가하고 _**코멘트**_를 등록할 수 있고 _**좋아요**_까지 가능해요.
- 마이 페이지에서 사용자 정보를 보여줄 수 있어요. 
- 전체 리뷰 개수를 카운팅할 수 있어요.
 
# 데이터베이스 모델링
_**AQueryTool**_을 이용하여 엔티티간의 관계를 그려봤어요. 사이트가 요구하는 정도까지만 정규화를 했다는 점을 기억해주세요 🙇🏻‍♂️
![위챠 모델링](https://images.velog.io/images/choonghee-lee/post/7a11a8b4-0e52-4d46-a3aa-4a558f79dcc6/image.png)


# ✅ 사용 기술
- _**Django**_ 웹 프레임워크로만 API를 구현했어요. **`select_related()`, `prefetch_related()`** 와 같은 메서드로 DB hit를 줄이기 위해 고민했어요.
- _**Selenium**_을 통해 영화 데이터를 크롤링했어요.
- 크롤링한 csv 파일을 **MySQL**에 저장해 두었어요.
- _**AWS EC2**_ 서버에 _**RDS**_ 인스턴스를 연결하여 서비스 하였어요.

# API 문서 📑
프론트와 백엔드 구분없이 _**소통하기 위해**_ 포스트맨을 통해 API 문서를 작성했어요.
- [영화 API 문서](https://documenter.getpostman.com/view/12235507/T1LV8PVD)
- [사용자 API 문서](https://documenter.getpostman.com/view/8738620/T1LV9PdQ)
