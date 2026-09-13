"""Units 2-10 vocabulary curation pass: turn verified vocab_grammar
`ContentBlock` rows into DRAFT `Vocabulary` rows.

Same precedent as `curate_unit1.py`: every row created here is
`CurationStatus.DRAFT` and `proposed_by="assistant:curate_units_2_10"`.
Nothing here ever sets HUMAN_APPROVED/CANONICAL.

Every (korean, english, example) triple below is copied verbatim from a
specific, cited `ContentBlock` (source_key="vocab_grammar", page, block
index) - nothing is invented. Scope is vocabulary only (Part 1 "1부 어휘와
표현" pages), matching the product's pivot to a vocab-only Memory Lab - no
grammar/textbook/workbook/additional_activities content is curated here.

Run with backend/.venv active, after content_pipeline.seed_vocab_units has
imported the ContentBlock rows for units 2-10:
    cd backend && source .venv/bin/activate && cd ..
    python -m content_pipeline.curate_units_2_10
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROPOSED_BY = "assistant:curate_units_2_10"

# (korean, english, example_ko, page_number, word_block_index)
# Source: data/verified/vocab_grammar/page_0NN.json for each unit's
# VOCAB_GRAMMAR_PART1_RANGES pages (see content_pipeline/config.py).
VOCABULARY_BY_UNIT: dict[int, list[tuple[str, str, str, int, int]]] = {
    2: [
        ("한자어", "Sino-Korean word", "일은 한자어 수예요", 10, 8),
        ("수", "number", "팔은 한자어 수예요", 10, 11),
        ("영/공", "zero", "제 전화번호는공일공일이일삼칠오공삼이에요.", 10, 14),
        ("일", "one", "카페는일 층이에요", 10, 17),
        ("이", "two", "식당은 이 층이에요", 10, 20),
        ("삼", "three", "영화관은삼 층이에요", 10, 23),
        ("사", "four", "노래방은사 층이에요.", 10, 26),
        ("오", "five", "PC방은오 층이에요", 10, 29),
        ("육", "six", "카페는 육 층이에요", 10, 32),
        ("칠", "seven", "식당은칠 층이에요", 10, 35),
        ("팔", "eight", "영화관은 팔 층이에요.", 10, 38),
        ("구", "nine", "노래방은 구 층이에요", 10, 41),
        ("십", "ten", "PC방은 십 층이에요", 10, 44),
        ("십일", "eleven", "십일 쪽이에요", 10, 47),
        ("십이", "twelve", "십이 쪽이에요", 10, 50),
        ("십삼", "thirteen", "십삼 쪽이에요", 10, 53),
        ("십사", "fourteen", "십사 쪽이에요", 10, 56),
        ("십오", "fifteen", "십오 쪽이에요", 10, 59),
        ("십육", "sixteen", "십육 쪽이에요", 10, 62),
        ("십칠", "seventeen", "십칠 쪽이에요", 10, 65),
        ("십팔", "eighteen", "십팔 쪽이에요", 10, 68),
        ("십구", "nineteen", "십구 쪽이에요", 11, 0),
        ("이십", "twenty", "이십 번 버스예요", 11, 3),
        ("삼십", "thirty", "삼십번 버스예요", 11, 6),
        ("사십", "forty", "사십번 버스예요", 11, 9),
        ("오십", "fifty", "오십 번 버스예요", 11, 12),
        ("육십", "sixty", "육십 번 버스예요", 11, 15),
        ("칠십", "seventy", "칠십번버스예요", 11, 18),
        ("팔십", "eighty", "팔십번 버스예요", 11, 21),
        ("구십", "ninety", "구십번 버스예요", 11, 24),
        ("백", "one hundred", "백번 버스예요", 11, 27),
        ("층", "floor", "카페는3층이에요.", 11, 30),
        ("월", "month", "7월이에요", 11, 33),
        ("쪽", "page", "몇 쪽이에요?", 11, 36),
        ("번", "number", "8번버스예요", 11, 39),
        ("호", "number", "203호예요", 11, 42),
        ("원", "won; Korean currency", "백원이에요", 11, 45),
        ("몇", "which", "몇월이에요?", 11, 48),
        ("얼마", "how much", "우유는 얼마예요?", 11, 51),
        ("전화번호", "phone number", "전화번호가 뭐예요?", 11, 54),
        ("카페", "cafe", "카페가 어디예요?", 11, 57),
        ("식당", "restaurant", "식당이 몇 층이에요?", 11, 60),
        ("영화관", "movie theater", "영화관은 2층이에요", 11, 63),
        ("노래방", "karaoke", "노래방이에요", 11, 66),
        ("PC방", "internet cafe", "PC방은 4층이에요", 12, 0),
        ("지하", "basement", "노래방은지하1층이에요", 12, 3),
        ("형", "older brother", "형이에요", 12, 6),
        ("교실", "classroom", "교실이 203호예요?", 12, 9),
        ("물", "water", "물이에요?", 12, 12),
        ("주스", "juice", "주스예요", 12, 15),
        ("컴퓨터", "computer", "컴퓨터예요?", 12, 18),
        ("텔레비전", "television", "텔레비전이에요.", 12, 21),
        ("남자", "boy", "마리 씨 남자 친구예요?", 12, 24),
        ("의자", "chair", "의자예요?", 12, 27),
        ("맞다", "right", "맞아요?", 12, 30),
        ("두", "two", "교실에두사람이있어요", 12, 33),
        ("무슨", "what", "무슨 이야기를 해요?", 12, 36),
        ("세종학당", "King Sejong Institute", "세종학당 전화번호가 몇 번이에요?", 12, 39),
        ("이메일", "e-mail", "이메일 주소가 뭐예요?", 12, 42),
        ("주소", "address", "이메일 주소가 뭐예요?", 12, 45),
    ],
    3: [
        ("물건", "thing", "물건이 많아요", 13, 8),
        ("책상", "desk", "책상이에요", 13, 11),
        ("가방", "bag", "가방이에요", 13, 14),
        ("필통", "pencil case", "리사씨 필통이에요", 13, 17),
        ("시계", "clock", "유진 씨 시계예요", 13, 20),
        ("앞", "in front of", "유진 씨가 칠판 앞에 있어요", 13, 23),
        ("뒤", "behind", "가방이 의자 뒤에 있어요?", 13, 26),
        ("위", "on top of", "책상 위에 책이 있어요", 13, 29),
        ("아래/밑", "under", "필통이 칠판 아래/밑에 있어요.", 13, 32),
        ("옆", "next to", "카페가 식당 옆에 있어요", 13, 35),
        ("오른쪽", "right", "마리씨는 주노 씨 오른쪽에 있어요.", 13, 38),
        ("왼쪽", "left", "왼쪽 사람이 제 동생이에요", 13, 41),
        ("사이", "between", "제가방이 의자사이에있어요", 13, 44),
        ("집", "house", "수지 씨가 집에 있어요?", 13, 47),
        ("안", "inside", "필통이 가방 안에 있어요", 13, 50),
        ("밖", "outside", "안나 씨는 집 밖에 있어요", 13, 53),
        ("어디", "where", "가방이 어디에 있어요?", 13, 56),
        ("핸드폰", "cell phone", "저 핸드폰은 주노 씨핸드폰이에요?", 13, 59),
        ("학교", "school", "저는 학교에 가요", 13, 62),
        ("칠판", "blackboard", "칠판이 교실에 있어요?", 13, 65),
        ("피아노", "piano", "피아노가 교실에 없어요", 13, 68),
        ("그럼", "then", "그럼 누구 가방이에요?", 14, 0),
        ("펜", "pen", "제 펜은 필통 속에 있어요.", 14, 3),
        ("우산", "umbrella", "가방 안에 우산이 있어요", 14, 6),
        ("방", "room", "책상이 방 안에 있어요?", 14, 9),
        ("무엇", "what", "오늘 무엇을 사요?", 14, 12),
        ("침대", "bed", "침대 위에 책이 있어요", 14, 15),
    ],
    4: [
        ("먹다", "eat", "불고기를 먹어요", 15, 7),
        ("읽다", "read", "책을읽어요", 15, 11),
        ("보다", "see", "오늘 영화를 봐요", 15, 14),
        ("마시다", "drink", "우유를 마셔요", 15, 17),
        ("듣다", "listen", "한국음악을들어요", 15, 20),
        ("만나다", "meet", "오늘친구를 만나요", 15, 23),
        ("자다", "sleep", "재민 씨가 자요", 15, 26),
        ("일하다", "work", "마리 씨가 일해요", 15, 29),
        ("요리하다", "cook", "유진 씨는 요리해요", 15, 32),
        ("공부하다", "study", "안나 씨는 공부해요", 15, 35),
        ("영화", "movie", "저는 한국영화를 좋아해요.", 15, 38),
        ("한국어", "Korean language", "유진 씨는한국어를 공부해요.", 15, 41),
        ("오늘", "today", "저는오늘 친구를 만나요", 15, 44),
        ("불고기", "bulgogi", "불고기가 맛있어요?", 15, 47),
        ("정말", "really", "한국 영화를 정말 좋아해요", 15, 50),
        ("맛있다", "tasty", "김치가 맛있어요", 15, 53),
        ("지금", "now", "지금 음악을 들어요?", 15, 56),
        ("피자", "pizza", "피자가 맛있어요", 15, 59),
        ("좋아하다", "like", "한국 음악을 좋아해요?", 15, 62),
        ("꽃", "flower", "마리 씨는 꽃을 좋아해요?", 15, 65),
        ("고양이", "cat", "제친구는 고양이를좋아해요", 15, 68),
        ("음악", "music", "재민 씨는 음악을 들어요", 16, 0),
        ("게임", "game", "유진 씨는 게임을 좋아해요?", 16, 3),
        ("쇼핑", "shopping", "오늘은 쇼핑을 해요", 16, 6),
        ("김치", "kimchi", "김치예요", 16, 9),
        ("옷", "clothes", "옷을 사요", 16, 12),
        ("사다", "buy", "주노씨가 옷을 사요", 16, 15),
        ("공원", "park", "유진 씨가 공원에 있어요", 16, 18),
        ("운동하다", "exercise", "수지 씨는 운동해요", 16, 21),
    ],
    5: [
        ("장소", "place", "장소가 어디예요?", 17, 7),
        ("식품", "food", "마트에서 식품을 사요", 17, 10),
        ("회사", "company", "재민씨가 회사에 가요.", 17, 14),
        ("마트", "mart", "유진 씨는 마트에 있어요", 17, 17),
        ("빵", "bread", "오늘 빵을사요", 17, 20),
        ("라면", "ramyeon", "라면을 먹어요", 17, 23),
        ("과일", "fruit", "과일이마트에 있어요", 17, 26),
        ("차", "tea", "주노 씨가 차를 마셔요", 17, 29),
        ("우유", "milk", "마트에서 우유를 사요", 17, 32),
        ("과자", "snack", "과자를 사요", 17, 35),
        ("아이스크림", "ice cream", "아이스크림을 먹어요", 17, 38),
        ("여기", "here", "여기가 세종학당이에요", 17, 41),
        ("백화점", "department store", "백화점이 어디예요?", 17, 44),
        ("구두", "shoes", "가방하고구두를사요", 17, 47),
        ("누가", "who", "교실에 누가 있어요?", 17, 50),
        ("사과", "apple", "사과예요", 17, 53),
        ("포도", "grape", "사과하고 포도를 사요", 17, 56),
        ("케이크", "cake", "케이크하고 빵을 먹어요", 17, 59),
        ("김밥", "gimbap", "저는 김밥을 좋아해요", 17, 62),
        ("신발", "shoes", "수지 씨는 신발하고 옷을 사요", 17, 65),
        ("영어", "English", "영어하고 한국어를 배워요", 17, 68),
        ("화장품", "cosmetics", "유진 씨는 화장품하고 가방을 사요.", 17, 71),
    ],
    6: [
        ("고유어", "native Korean word", "하나는 고유어수예요.", 18, 7),
        ("하나/한", "one", "사과 하나 주세요", 18, 10),
        ("둘/두", "two", "동생이 두명이에요", 18, 13),
        ("셋/세", "three", "동생은 세 살이에요", 18, 17),
        ("넷/네", "four", "동생은 네살이에요", 18, 20),
        ("다섯", "five", "동생은 다섯살이에요", 18, 23),
        ("여섯", "six", "동생은 여섯살이에요", 18, 26),
        ("일곱", "seven", "동생은 일곱 살이에요.", 18, 29),
        ("여덟", "eight", "동생은 여덟 살이에요", 18, 32),
        ("아홉", "nine", "동생은 아홉살이에요", 18, 35),
        ("열", "ten", "동생은 열살이에요", 18, 38),
        ("열하나/열한", "eleven", "동생은 열한 살이에요", 18, 41),
        ("열둘/열두", "twelve", "동생은 열두살이에요", 18, 44),
        ("스물/스무", "twenty", "형은스무살이에요", 18, 47),
        ("서른", "thirty", "누나는 서른 살이에요.", 18, 50),
        ("마흔", "forty", "언니는 마흔 살이에요.", 18, 53),
        ("쉰", "fifty", "사과를 쉰개사요", 18, 56),
        ("예순", "sixty", "사과를 예순개 사요", 18, 59),
        ("일흔", "seventy", "사과를일혼개사요", 18, 62),
        ("여든", "eighty", "사과를여든개 사요", 18, 65),
        ("아흔", "ninety", "사과를 아혼개 사요", 18, 68),
        ("백", "hundred", "사과를백개사요", 19, 0),
        ("개", "gae (counter for objects)", "우산을 한개 사요", 19, 4),
        ("공", "ball", "공이 몇 개 있어요?", 19, 8),
        ("지우개", "eraser", "지우개가 없어요", 19, 11),
        ("계란", "egg", "계란이 아홉 개 있어요.", 19, 14),
        ("명", "myeong (counter for persons)", "학생이 몇 명 있어요?", 19, 18),
        ("마리", "mari (counter for animals)", "고양이가 세마리있어요.", 19, 23),
        ("잔", "cup", "주스가 몇 잔 있어요?", 19, 27),
        ("병", "bottle", "물이 몇 병 있어요?", 19, 30),
        ("권", "book (counter)", "책이 몇 권 있어요?", 19, 33),
        ("장", "piece, sheet", "카드가 다섯장있어요", 19, 36),
        ("살", "years old", "제동생은 열여덟 살이에요", 19, 39),
        ("창문", "window", "창문이두개 있어요", 19, 42),
        ("앉다", "sit", "여기 앉으세요", 19, 45),
        ("고맙다", "thank", "고마워요", 19, 48),
        ("주다", "give", "라면세 개 주세요", 19, 51),
        ("쓰다", "write", "쓰세요", 19, 54),
        ("대답하다", "answer", "대답하세요", 19, 57),
        ("펴다", "open", "책을펴세요", 19, 60),
        ("내일", "tomorrow", "저는 내일일찍 학교에 가요.", 19, 63),
        ("일찍", "early", "내일 일찍 오세요", 20, 0),
        ("오다", "come", "친구가 집에와요", 20, 3),
        ("버스", "bus", "8번 버스를 타요", 20, 6),
        ("타다", "ride", "친구하고자전거를 타요", 20, 9),
        ("가게", "store", "과일가게에서 과일을 사요", 20, 12),
        ("어서", "please (used to welcome someone)", "어서 오세요", 20, 16),
        ("모두", "all", "모두 얼마예요?", 20, 20),
        ("바나나", "banana", "바나나를 좋아해요", 20, 23),
        ("편의점", "convenience store", "저는편의점에 가요", 20, 26),
        ("치약", "toothpaste", "치약한 개 주세요", 20, 29),
        ("칫솔", "toothbrush", "칫솔이 없어요", 20, 32),
        ("그리고", "and", "빵한개 주세요.그리고우유두개주세요.", 20, 35),
    ],
    7: [
        ("날짜", "date", "날짜가 언제예요?", 21, 7),
        ("요일", "day of the week", "일요일에친구를 만나요", 21, 10),
        ("달력", "calendar", "달력을 보세요", 21, 13),
        ("일월", "January", "일월이에요", 21, 16),
        ("이월", "February", "이월이에요", 21, 20),
        ("삼월", "March", "삼월이에요", 21, 23),
        ("사월", "April", "사월이에요", 21, 26),
        ("오월", "May", "오월이에요", 21, 29),
        ("유월", "June", "유월이에요", 21, 32),
        ("칠월", "July", "칠월이에요", 21, 35),
        ("팔월", "August", "팔월이에요", 21, 38),
        ("구월", "September", "구월이에요", 21, 41),
        ("시월", "October", "시월이에요", 21, 44),
        ("십일월", "November", "십일월이에요", 21, 47),
        ("십이월", "December", "십이월이에요", 21, 50),
        ("일요일", "Sunday", "오늘은 일요일이에요", 21, 53),
        ("월요일", "Monday", "오늘은 월요일이에요", 21, 56),
        ("화요일", "Tuesday", "오늘은 화요일이에요", 21, 59),
        ("수요일", "Wednesday", "오늘은 수요일이에요", 21, 62),
        ("목요일", "Thursday", "오늘은 목요일이에요", 21, 65),
        ("금요일", "Friday", "오늘은 금요일이에요", 21, 68),
        ("토요일", "Saturday", "오늘은 토요일이에요", 22, 0),
        ("일일", "1st day of the month", "오늘은일월 일일이에요", 22, 3),
        ("이일", "2nd day of the month", "오늘은일월이일이에요", 22, 6),
        ("삼일", "3rd day of the month", "오늘은일월삼일이에요.", 22, 9),
        ("사일", "4th day of the month", "오늘은일월사일이에요", 22, 12),
        ("오일", "5th day of the month", "오늘은일월 오일이에요", 22, 15),
        ("육일", "6th day of the month", "오늘은일월 육일이에요", 22, 18),
        ("칠일", "7th day of the month", "오늘은일월칠일이에요", 22, 21),
        ("팔일", "8th day of the month", "오늘은일월 팔일이에요.", 22, 24),
        ("구일", "9th day of the month", "오늘은일월 구일이에요", 22, 27),
        ("십일", "10th day of the month", "오늘은일월 십일이에요.", 22, 30),
        ("십일일", "11th day of the month", "오늘은일월 십일일이에요", 22, 33),
        ("십이일", "12th day of the month", "오늘은일월십이일이에요", 22, 36),
        ("십삼일", "13th day of the month", "오늘은일월 십삼일이에요", 22, 39),
        ("십사일", "14th day of the month", "오늘은일월 십사일이에요", 22, 42),
        ("십오일", "15th day of the month", "오늘은일월 십오일이에요", 22, 45),
        ("십육일", "16th day of the month", "오늘은일월십육일이에요.", 22, 48),
        ("십칠일", "17th day of the month", "오늘은일월 십칠일이에요", 22, 51),
        ("십팔일", "18th day of the month", "오늘은일월 십팔일이에요", 22, 54),
        ("십구일", "19th day of the month", "오늘은일월 십구일이에요", 22, 57),
        ("이십일", "20th day of the month", "오늘은일월이십일이에요.", 22, 60),
        ("이십일일", "21st day of the month", "오늘은일월 이십일일이에요.", 22, 63),
        ("이십이일", "22nd day of the month", "오늘은일월이십이일이에요.", 22, 66),
        ("이십삼일", "23rd day of the month", "오늘은일월 이십삼일이에요", 23, 0),
        ("이십사일", "24th day of the month", "오늘은일월 이십사일이에요", 23, 3),
        ("이십오일", "25th day of the month", "오늘은일월 이십오일이에요", 23, 6),
        ("이십육일", "26th day of the month", "오늘은일월 이십육일이에요.", 23, 9),
        ("이십칠일", "27th day of the month", "오늘은일월 이십칠일이에요.", 23, 12),
        ("이십팔일", "28th day of the month", "오늘은일월 이십팔일이에요.", 23, 15),
        ("이십구일", "29th day of the month", "오늘은일월이십구일이에요", 23, 18),
        ("삼십일", "30th day of the month", "오늘은일월삼십일이에요", 23, 21),
        ("삼십일일", "31st day of the month", "오늘은일월삼십일일이에요", 23, 24),
        ("생일", "birthday", "생일이 언제예요?", 23, 27),
        ("언제", "when", "언제 유진 씨를 만나요?", 23, 30),
        ("주말", "weekend", "주말에 만나요", 23, 33),
        ("수업", "class", "한국어 수업이 있어요.", 23, 36),
        ("여행", "travel", "언제 여행을 가요?", 23, 39),
        ("며칠", "what day", "며칠에 사진을 찍어요?", 23, 42),
        ("사진", "photo", "사진을 찍으세요", 23, 45),
        ("찍다", "take", "오늘사진을 찍어요", 23, 48),
        ("배우다", "learn", "언제 수영을 배워요?", 23, 51),
        ("도서관", "library", "도서관에 가요", 23, 54),
        ("아르바이트", "part-time job", "목요일에 아르바이트를 해요", 23, 57),
        ("수영", "swimming", "금요일에수영을 배워요", 23, 60),
        ("점심", "lunch", "언제 점심을 먹어요?", 23, 63),
        ("식사", "meal", "같이 식사를 해요", 23, 66),
        ("회의", "meeting", "몇시에 회의를 해요?", 24, 0),
        ("저녁", "evening", "저녁에 운동을해요", 24, 3),
        ("오후", "afternoon", "오늘 오후에 뭐 해요?", 24, 6),
        ("드라마", "TV drama", "드라마를 봐요", 24, 9),
        ("시작하다", "begin", "수업은 몇 시에 시작해요?", 24, 12),
        ("아침", "morning", "아침열시에아르바이트를 해요", 24, 15),
        ("하루", "day", "주노씨의하루", 24, 18),
        ("다니다", "commute, work for", "주노씨는 회사에 다녀요.", 24, 21),
        ("매일", "every day", "매일일곱 시에 아침을먹어요", 24, 24),
        ("일어나다", "get up", "매일 여섯 시에 일어나요", 24, 27),
        ("파티", "party", "친구생일 파티가 있어요.", 24, 30),
        ("하고", "with", "동생하고산책을했어요", 24, 33),
        ("밥", "meal", "같이 밥을 먹어요", 24, 36),
        ("같이", "together", "언제 밥을 먹어요?", 24, 39),
    ],
    8: [
        ("날씨", "weather", "날씨가 어때요?", 25, 7),
        ("계절", "season", "무슨 계절을 좋아해요?", 25, 10),
        ("맑다", "clear", "날씨가 맑아요", 25, 13),
        ("흐리다", "cloudy", "날씨가 흐려요", 25, 16),
        ("바람", "wind", "바람이 불어요", 25, 19),
        ("불다", "blow", "바람이 불어요", 25, 23),
        ("비", "rain", "비가 와요", 25, 26),
        ("눈", "snow", "눈이 와요", 25, 29),
        ("따뜻하다", "warm", "봄은 따뜻해요", 25, 32),
        ("덥다", "hot", "날씨가 더워요", 25, 35),
        ("시원하다", "cool", "바람이 시원해요", 25, 38),
        ("쌀쌀하다", "chilly", "날씨가 쌀쌀해요.", 25, 41),
        ("춥다", "cold", "날씨가 추워요", 25, 44),
        ("사계절", "four seasons", "한국은 사계절이 있어요", 25, 47),
        ("봄", "spring", "저는 봄을 좋아해요", 25, 50),
        ("여름", "summer", "여름은 더워요", 25, 53),
        ("가을", "fall", "가을은 시원해요", 25, 56),
        ("겨울", "winter", "겨울을 좋아해요", 25, 59),
        ("이번", "this", "이번 금요일에 날씨가 어때요?", 25, 62),
        ("어떻다", "how", "이번 주말에 날씨가 어때요?", 25, 65),
        ("서울", "Seoul", "서울은 날씨가 좋아요?", 25, 68),
        ("좋다", "good", "날씨가 안 좋아요", 26, 0),
        ("바쁘다", "busy", "오늘 바빠요?", 26, 3),
        ("딸기", "strawberry", "바나나하고딸기를사요", 26, 6),
        ("좀", "a little", "좀 추워요", 26, 9),
        ("무겁다", "heavy", "가방이무거워요", 26, 12),
        ("가볍다", "light", "가방이 가벼워요", 26, 15),
        ("요즘", "recently", "요즘 날씨가 어때요?", 26, 18),
        ("쉽다", "easy", "공부가 쉬워요", 26, 21),
        ("어렵다", "difficult", "책이 아주 어려워요", 26, 24),
        ("그런데", "but", "김치가 맛있어요. 그런데 좀 매워요.", 26, 27),
        ("맵다", "spicy", "김치가 매워요", 26, 30),
        ("아주", "very", "가방이 아주무거워요.", 26, 33),
        ("고향", "hometown", "이번 주말에 고향에 가요", 26, 36),
        ("부산", "Busan", "부산은 날씨가 더워요?", 26, 39),
        ("잘", "well", "지은 씨, 잘 지내요?", 26, 42),
        ("지내다", "be (doing)", "잘 지내요", 26, 45),
        ("자주", "often", "요즘 비가 자주 와요", 26, 48),
        ("거기", "there", "거기는 날씨가 어때요?", 26, 51),
        ("많이", "a lot", "바람이 많이 불어요", 26, 54),
        ("도시", "town", "그도시는 어느 나라에 있어요?", 26, 57),
        ("하노이", "Hanoi", "하노이는 아주더워요.", 26, 60),
        ("시드니", "Sydney", "시드니는 어때요?", 26, 63),
        ("모스크바", "Moscow", "모스크바는 더워요", 26, 66),
        ("자카르타", "Jakarta", "자카르타는 비가 오고 더워요", 27, 0),
        ("제주도", "Jeju-do", "제고향은 제주도예요", 27, 3),
        ("바다", "sea", "바다에 가요", 27, 6),
        ("한라산", "Hallasan Mountain", "한라산 단풍이 예뻐요.", 27, 9),
        ("단풍", "autumn foliage", "단풍이 아주 예뻐요", 27, 12),
        ("예쁘다", "pretty", "꽃이 예뻐요", 27, 15),
        ("그렇지만", "however", "많이 안 추워요. 그렇지만 바람이 많이 불어요.", 27, 18),
        ("아름답다", "beautiful", "제주도는 정말 아름다워요", 27, 21),
    ],
    9: [
        ("활동", "activity", "주말활동", 28, 7),
        ("미용실", "hair shop, beauty shop, hairdresser's", "주말에 미용실에 가요", 28, 11),
        ("놀이공원", "amusement park", "놀이공원에서 친구하고놀았어요", 28, 15),
        ("박물관", "museum", "박물관에서 구경해요", 28, 18),
        ("수영장", "swimming pool", "수영장에서 수영해요", 28, 21),
        ("산책하다", "walk", "공원에서 산책해요", 28, 25),
        ("구경하다", "look around", "박물관을 구경해요.", 28, 28),
        ("자전거", "bicycle", "자전거를 타요", 28, 31),
        ("청소하다", "clean", "집에서 청소해요", 28, 34),
        ("어제", "yesterday", "어제 수영을 했어요?", 28, 37),
        ("쉬다", "rest", "집에서 쉬었어요", 28, 40),
        ("만들다", "make", "친구하고같이 김밥을 만들었어요", 28, 43),
        ("재미있다", "fun", "아주 재미있었어요", 28, 46),
        ("우리", "our", "친구가우리집에놀러왔어요.", 28, 49),
        ("놀다", "play", "친구하고 놀아요", 28, 52),
        ("기분", "mood", "기분이 아주 좋았어요", 28, 55),
    ],
    10: [
        ("약속", "appointment, engagement", "특별한 약속이 있어요", 29, 7),
        ("시간", "time", "오늘 시간이 있어요?", 29, 11),
        ("특별하다", "special", "특별한 일이 없어요", 29, 14),
        ("일", "work, business, matter", "특별한 일이 있어요", 29, 18),
        ("다르다", "other, different", "다른 약속이 있어요", 29, 22),
        ("콘서트", "concert", "콘서트를 봤어요", 29, 26),
        ("축구", "soccer", "주말에 축구를했어요", 29, 29),
        ("경기", "game", "축구경기를 봐요", 29, 32),
        ("농구", "basketball", "친구하고농구를했어요", 29, 35),
        ("음료수", "beverage", "마트에서 음료수를샀어요", 29, 38),
        ("등산", "hiking", "친구하고 등산을갔어요.", 29, 41),
        ("하다", "do", "어제친구하고게임을했어요", 29, 44),
        ("반", "class", "반친구하고영화를 봤어요.", 29, 47),
        ("한강", "Hangang River", "한강공원에서산책을 했어요", 29, 50),
        ("음식", "food", "한국음식을 먹고 싶어요", 29, 53),
        ("운동화", "sneakers", "저는 운동화를사고싶어요", 29, 56),
        ("방학", "school break, vacation", "방학에 어디에 가고 싶어요?", 29, 59),
        ("비빔밥", "bibimbap", "저는 비빔밥을 먹고싶어요", 29, 63),
        ("낚시", "fishing", "주말에낚시를 하고싶어요", 30, 0),
        ("태권도", "taekwondo", "태권도를 배우고싶어요", 30, 3),
        ("다", "all", "밥 다 먹었어요?", 30, 6),
        ("걷다", "walk", "우리 밖에서 좀 걸을까요?", 30, 9),
        ("쇼핑몰", "shopping mall", "쇼핑몰에 가고 싶어요", 30, 12),
        ("내용", "content", "약속 내용을메모해 보세요", 30, 15),
        ("메모", "note", "메모해 보세요", 30, 18),
        ("주", "week", "이번 주 금요일에 만날까요?", 30, 21),
        ("다음", "next", "다음 주에 만나요", 30, 24),
        ("케이팝(K-POP)", "K-POP", "우리 같이 케이팝(K-POP) 콘서트를 볼까요?", 30, 27),
    ],
}


def _load_backend_models():
    from app.db.session import SessionLocal
    from app.models.content_source import ContentBlock, ContentSource
    from app.models.curriculum import Lesson, Unit, Vocabulary
    from app.models.enums import CurationStatus, SourceType

    return {
        "SessionLocal": SessionLocal,
        "ContentBlock": ContentBlock,
        "ContentSource": ContentSource,
        "Lesson": Lesson,
        "Unit": Unit,
        "Vocabulary": Vocabulary,
        "CurationStatus": CurationStatus,
        "SourceType": SourceType,
    }


def curate_unit(unit_number: int) -> int:
    """Create DRAFT Vocabulary rows for one unit. Returns count created."""
    m = _load_backend_models()
    db = m["SessionLocal"]()
    try:
        number = f"{unit_number:02d}"
        unit = db.query(m["Unit"]).filter_by(number=number).one()
        lesson = db.query(m["Lesson"]).filter_by(unit_id=unit.id).order_by(m["Lesson"].created_at).first()
        vg_source = db.query(m["ContentSource"]).filter_by(source_type=m["SourceType"].VOCAB_GRAMMAR).one()

        def block_id(page: int, index: int):
            block = (
                db.query(m["ContentBlock"])
                .filter_by(source_id=vg_source.id, page_number=page, block_index=index)
                .one()
            )
            return block.id

        created = 0
        for korean, english, example, page, idx in VOCABULARY_BY_UNIT[unit_number]:
            existing = (
                db.query(m["Vocabulary"]).filter_by(lesson_id=lesson.id, korean=korean, english=english).one_or_none()
            )
            if existing is not None:
                continue
            row = m["Vocabulary"](
                lesson_id=lesson.id,
                korean=korean,
                english=english,
                notes=example,
                source_block_id=block_id(page, idx),
                curation_status=m["CurationStatus"].DRAFT,
                proposed_by=PROPOSED_BY,
            )
            db.add(row)
            created += 1

        db.commit()
        return created
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    for unit_number in range(2, 11):
        created = curate_unit(unit_number)
        print(f"unit {unit_number}: {created} vocabulary rows created")


if __name__ == "__main__":
    main()
