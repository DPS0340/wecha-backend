from django.test import TestCase, Client

from .models     import (
    Country,
    FilmCountry,
    Genre,
    FilmGenre,
    ServiceProvider,
    FilmServiceProvider,
    Film,
    FilmURLType,
    FilmURL,
    Person,
    Cast
)
from user.models import (
    User,
    Collection,
    FilmCollection,
    ReviewType,
    Review   
)


class FilmTest(TestCase):
    def setUp(self):
        cleint = Client()

        film_url_type    = FilmURLType.objects.create(name = "B")
        review_type      = ReviewType.objects.create(name = 'R')
        service_provider = ServiceProvider.objects.create(name = "watcha")
        country          = Country.objects.create(name = "미국")
        genre            = Genre.objects.create(name = "로맨스")
        user             = User.objects.create(
            email       = "test@watcha.com",
            password    = "bonjour",
            name        = "tester",
            description = "테스터입니다."
        )

        person1           = Person.objects.create(name = "엠마 왓슨")
        film1            = Film.objects.create(
            korean_title   = "라라랜드",
            original_title = "La La Land",
            release_date   = "2016-01-03",
            running_time   = "02:06:00",
            avg_rating     = 4.2,
            description    = "황홀한 사랑, 순수한 희망, 격렬한 열정… 이 곳에서 모든 감정이 폭발한다.\
                            꿈을 꾸는 사람들을 위한 별들의 도시 ‘라라랜드’\
                            재즈 피아니스트 ‘세바스찬’(라이언 고슬링)과 성공을 꿈꾸는 배우 지망생 ‘미아’(엠마 스톤)\
                            인생에서 가장 빛나는 순간 만난 두 사람은 미완성인 서로의 무대를 만들어가기 시작한다.",
            poster_url     = "https://dhgywazgeek0d.cloudfront.net/watcha/image/upload/c_fill,h_400,q_80,w_280/v1480382093/ha1knjr9iilixtwkltpw.jpg"   
        )
        Review.objects.create(
            score       = 4.5,
            comment     = "눈과 귀가 모두 즐거운 영화",
            review_type = review_type,
            film        = film1,
            user        = user
        )
        FilmURL.objects.create(
            url           = "https://dhgywazgeek0d.cloudfront.net/watcha/image/upload/c_fill,h_720,q_80,w_1280/v1574318600/s4q4hyux7tfq5wuybfcp.jpg",
            film_url_type = film_url_type,
            film          = film1
        )
        FilmServiceProvider.objects.create(film = film1, service_provider = service_provider)
        FilmCountry.objects.create(film = film1, country = country)
        FilmGenre.objects.create(film = film1, genre = genre)
        Cast.objects.create(film = film1, person = person1, role = "주연")

        person2            = Person.objects.create(name="아담 샌들러")
        film2             = Film.objects.create(
            korean_title   = "첫 키스만 50번째",
            original_title = "50 First Dates",
            release_date   = "2004-07-14",
            running_time   = "01:39:00",
            avg_rating     = 4.4,
            description    = "그녀에겐 매일이 첫 데이트, 첫 키스, 첫 사랑!? 로맨틱 아일랜드 하와이에서 펼쳐지는 본격 하루 리셋 로맨스. ‘헨리’(아담 샌들러)는 낮에는 하와이 수족관에서 동물들을 돌보고, 밤에는 여행객들과의 화끈한 하룻밤을 즐기는 노련한 작업남. 우연히 ‘루시’(드류 베리모어)를 만나게 된 그는 사랑스러운 그녀에게 첫 눈에 반해 다가간다. 그러나 헨리의 화려한 입담에 넘어온 줄로만 알았던 루시는 다음 날 그를 파렴치한 취급하며 기억조차 하지 못한다. 헨리는 그녀가 단기 기억상실증에 걸렸으며, 매일 아침이면 모든 기억이 10월 13일 일요일 교통사고 당일로 돌아가버린다는 사실을 알게 된다. 매일이 자신과의 첫 만남인 루시의 마음을 사로잡기 위해 헨리는 매번 기상천외한 작업을 시도하고, 하루 하루 달콤한 첫 데이트를 만들어가던 어느 날, 루시는 자신이 단기 기억상실증에 걸렸다는 사실을 깨닫고 충격을 받게 되는데... 과연, 두 사람의 사랑은 이뤄질 수 있을까?",
            poster_url     = "https://dhgywazgeek0d.cloudfront.net/watcha/image/upload/c_fill,h_400,q_80,w_280/v1495505289/aqgvaoo2ycyqchwxfzyx.jpg"   
        )
        Review.objects.create(
            score       = 4.2,
            comment     = "모두 사랑스러운 영화!",
            review_type = review_type,
            film        = film2,
            user        = user
        )
        FilmURL.objects.create(
            url           = "https://dhgywazgeek0d.cloudfront.net/watcha/image/upload/c_fill,h_720,q_80,w_1280/v1530510457/s1jwl0eldilklaccpdys.jpg",
            film_url_type = film_url_type,
            film          = film2
        )
        FilmServiceProvider.objects.create(film = film2, service_provider = service_provider)
        FilmCountry.objects.create(film = film2, country = country)
        FilmGenre.objects.create(film = film2, genre = genre)
        Cast.objects.create(film = film2, person = person2, role = "주연")

        
        film3            = Film.objects.create(
            korean_title   = "이지 A",
            original_title = "Easy A",
            release_date   = "2010-12-23",
            running_time   = "01:32:00",
            avg_rating     = 3.8,
            description    = "살아오면서 자신의 존재감을 알리지 못한 채 평범한 삶을 살아온 올리브는 친구에게 조지라는 남자랑 비밀스러운 관계(?)가 있었다고 거짓말 한다. 순식간에 학교에 이야기가 퍼지고 올리브는 루머에 시달리게 되지만 유명세를 타게 됐다는 사실에 오히려 그 시선을 즐기기 시작한다. 하지만 올리브 눈앞에 정말 사랑하는 남자가 나타나게 되고 올리브는 사랑을 위해서라도 그 소문을 바로 잡아야겠다는 결심에 고군분투하기 시작하는데...",
            poster_url     = "https://dhgywazgeek0d.cloudfront.net/watcha/image/upload/c_fill,h_400,q_80,w_280/v1466068162/lrryaw98xylrvesoegmv.jpg"   
        )
        Review.objects.create(
            score       = 5.0,
            comment     = "적당히 재미있는 하이틴 영화",
            review_type = review_type,
            film        = film3,
            user        = user
        )
        FilmURL.objects.create(
            url           = "https://dhgywazgeek0d.cloudfront.net/watcha/image/upload/c_fill,h_720,q_80,w_1280/v1574318600/s4q4hyux7tfq5wuybfcp.jpg",
            film_url_type = film_url_type,
            film          = film3
        )
        FilmServiceProvider.objects.create(film = film3, service_provider = service_provider)
        FilmCountry.objects.create(film = film3, country = country)
        FilmGenre.objects.create(film = film3, genre = genre)
        Cast.objects.create(film = film3, person = person1, role = "주연")

        collection = Collection.objects.create(
            name        = "가슴 설레는 로맨틱 코미디 영화들",
            description = "다시보고 싶은 로코",
            user        = user
        )
        FilmCollection.objects.create(
            film       = film1,
            collection = collection,
        )
        FilmCollection.objects.create(
            film       = film2,
            collection = collection
        )
        FilmCollection.objects.create(
            film       = film3,
            collection = collection
        )

    def tearDown(self):
        ServiceProvider.objects.all().delete()

    def test_watcha_ranking_view(self):
        response = self.client.get('/film/ranking?sp=watcha')
        self.assertEqual(response.status_code, 200)
        
        films = response.json()['films']
        self.assertEqual(films[0]['title'], "첫 키스만 50번째")
        self.assertEqual(films[1]['title'], "라라랜드")
        self.assertGreater(films[0]['avg_rating'], films[1]['avg_rating'])

    def test_film_detail_view(self):
        response = self.client.get('/film/1')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        film = data['film']
        self.assertEqual(film['id'], 1)
        self.assertEqual(film['korean_title'], '라라랜드')
        self.assertEqual(film['countries'][0]['name'], '미국')
        self.assertEqual(film['genres'][0]['name'], '로맨스')
        self.assertEqual(film['service_providers'][0]['name'], 'watcha')
        self.assertEqual(data['casts'][0]['name'], '엠마 왓슨')
        self.assertEqual(data['collections'][0]['name'], '가슴 설레는 로맨틱 코미디 영화들')
        self.assertEqual(data['reviews'][0]['comment'], '눈과 귀가 모두 즐거운 영화')
        self.assertEqual(data['reviews'][0]['user']['name'], 'tester')