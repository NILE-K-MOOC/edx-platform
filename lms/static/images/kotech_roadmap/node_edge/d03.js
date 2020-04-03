var nodes = [
  { id: 0, label: "Introduction Programming for Everyone\n(프로그래밍 개론)\nPython 프로그래밍 기초 외 3건", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: [["Python 프로그래밍 기초(한국능률협회)", "http://www.dataedu.kr/course/1%ea%b3%bc%eb%aa%a9-python-%ed%94%84%eb%a1%9c%ea%b7%b8%eb%9e%98%eb%b0%8d-%ea%b8%b0%ec%b4%88/"], ['Python 프로그래밍 심화 (한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['머신러닝을 위한 파이썬 기초 (포항공과대학교)', 'https://iclass.postech.ac.kr/courses/5d6cdd4ec5728b2c694db285'], ['파이썬을 활용한 딥러닝 1 (코리아헤럴드)', 'http://www.abedu.co.kr/AI/?info_seq=4']] },
  { id: 1, label: "Basic(Highschool)\nMathematics(기초 수학)\n매칭강좌없음", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "" },

  { id: 2, label: "Introduction to Statistics\n(통계학 개론)\n통계학의 이해 I 외 3건", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: [['통계학의 이해 I', 'SookmyungK+SM_sta_004k'], ['통계학의 이해 II', 'SookmyungK+SM_sta_009k'], ['[A.I. SERIES] R을 활용한 통계학개론', 'PNUk+RS_C01'], ['머신러닝을 위한 R기초와 통계(고려사이버대학교)', 'http://future.cuk.edu/local/paid/application_intro.php?id=3']] },
  { id: 3, label: "Probability and Discrete Mathematics\n(확률과 이산수학)\nAI 기초수학Ⅱ(확률 및 통계)\n(전남대학교) 외 1건", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: [['AI 기초수학Ⅱ(확률 및 통계)(전남대학교)', 'https://sleonline.jnu.ac.kr/Course/Course100.aspx'], ['Mathematical Fundamentals for Data Science', 'KoreaUnivK+ku_eng_002']] },
  { id: 4, label: "Calculus(미적분학)\n알고 보면 쉬운 미적분 이론 외 2건", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: [['알고 보면 쉬운 미적분 이론', 'POSTECHk+MATH311'], ['미적분학 I - 활용을 중심으로', 'SKKUk+SKKU_EXGB506_01K'], ['미적분학 II-다변수 미적분학', 'SKKUk+SKKU_2017_05-01']] },
  { id: 5, label: "Linear Algebra(선형대수)\n선형대수학 외 3건", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: [['선형대수학', 'SKKUk+SKKU_2017_01'], ['쉽게 시작하는 기초선형대수학', 'UOSk+ACE_UOS06'], ['Mathematical Fundamentals for Data Science', 'KoreaUnivK+ku_eng_002'], ['머신러닝을 위한 선형대수와 최적화(포항공과대학교)', 'https://iclass.postech.ac.kr/courses/5d6cde23c5728b29054d5094']] },
  { id: 6, label: "AI Ethics(인공지능 윤리)\n인격과 로봇(일부 유사 강좌) 외 1건", shape: VIS_SHAPE, level: 1, color: EXIST_COLOR, link: [['인격과 로봇', 'CKUk+CORE_CKU03k'], ['포스트휴먼 인문학', 'EwhaK+CORE_EW17002C']] },

  { id: 7, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍 외 1건", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: [['파이썬 프로그래밍', 'HGUk+HGU02'], ['AI 기초프로그래밍(전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai']] },
  { id: 8, label: "Math for Artificial Intelligence\n(인공지능을 위한 수학)\n머신 러닝을 위한 기초 수학 및 통계\n(코리아헤럴드) 외 3건", shape: VIS_SHAPE, level: 2, color: MATCH_COLOR, link: [['머신 러닝을 위한 기초 수학 및 통계', 'http://www.abedu.co.kr/AI/lecture/ps/1/is/4'], ['머신러닝을 위한 수학적 기초(고려사이버대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['AI 기초수학 I(선형대수) (전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['AI 기초수학II(확률 및 통계) (전남대학교)', 'https://sleonline.jnu.ac.kr/Course/Course100.aspx']] },

  { id: 9, label: "Object-Oriented Programming\n(객체지향프로그래밍)\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "YeungnamUnivK+YU217001" },
  { id: 10, label: "Data Structures\n(데이터구조)\n자료구조 외 1건", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: [['자료구조(K-MOOC 상명대)', 'SMUk+SMU2018_01'], ['자료구조(K-MOOC 영남대)', 'YeungnamUnivK+YU216002']] },
  { id: 11, label: "Foundations of Data Science\n(데이터사이언스의 기초)\nR 데이터 분석 입문 외 2건", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: [['R 데이터 분석 입문', 'DKUK+DKUK0003'], ['디지털 시대의 커뮤니케이션', 'PTUk+SF_PMOOC01k'], ['My Major & Big Data', 'SMUk+ACE_SMU01']] },

  { id: 12, label: "Algorithms(알고리즘)\n자료구조(일부 유사 강좌)", shape: VIS_SHAPE, level: 4, color: EXIST_COLOR, link: "YeungnamUnivK+YU216002" },
  { id: 13, label: "Data Analysis(데이터분석)\n파이썬을 이용한 빅데이터 분석 외 1건", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: [['파이썬을 이용한 빅데이터 분석', 'SejonguniversityK+SJKMOOC05k'], ['예측 및 분류를 위한 데이터 애널리틱스 기법', 'POSTECHk+IMEN472']] },

  { id: 14, label: "Big Data Analytics\n(빅 데이터 분석)\n빅 데이터 첫 걸음 외 9건", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: [['빅 데이터 첫 걸음', 'POSTECHk+CSED490k'], ['빅데이터의 세계 원리와 응용', 'EwhaK+EW11237K'], ['빅데이터 플랫폼 구축 절차와 요소기술(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['빅데이터 분석기획 및 방법론(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['데이터 분석을 위한 분산처리 프레임워크(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['빅데이터와 인공지능의 응용', 'SNUk+SNU052_011k'], ['빅데이터와 머신러닝 소프트웨어', 'SNUk+SNU051_011k'], ['빅데이터와 텍스트마이닝', 'SejonguniversityK+SJMOOC10K'], ['(개발중) 빅데이터 분석 및 처리 기술', ''], ['(개발중) AWS 기반 IoT 빅데이터 실습 및 활용', '']] },

  { id: 15, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론(일부 유사 강좌)", shape: VIS_SHAPE, level: 6, color: NULL_COLOR, link: "KoreaUnivK+ku_eng_004" },

  { id: 16, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 17, label: "Introduction to Machine Learning\n(기계학습 개론)\n머신러닝 외 9건", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: [['머신러닝', 'SNUk+SNU050_011k'], ['Machine Learning for Data Science', 'KoreaUnivK+ku_eng_003'], ['자율주행을 위한 머신러닝', 'SKKUk+SKKU_30'], ['머신러닝-지도학습(고려사이버대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['머신러닝-비지도학습(고려사이버대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['지도학습:회귀(포항공과대학교)', 'https://iclass.postech.ac.kr/courses/5d6db0eec5728b505b13d593'], ['지도학습:분류(포항공과대학교)', 'https://iclass.postech.ac.kr/courses/5d6db194c5728b50b04d5fb3'], ['비지도학습:군집화와 차원축소(포항공과대학교)', 'https://iclass.postech.ac.kr/courses/5d6db210c5728b5081032723'], ['기계학습 입문(전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['R을 활용한 머신러닝(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai']] },

  { id: 18, label: "Introduction to Deep Learning\n(딥러닝 개론)\n딥러닝 개론 외 1건", shape: VIS_SHAPE, level: 8, color: NORMAL_COLOR, link: [['딥러닝 개론', 'DGUk+DGU_006k+DGU_006k'], ['심층학습(전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai']] },
  { id: 19, label: "Advanced Machine Learning\n(고급 기계학습)\n매칭강좌없음", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },

  { id: 20, label: "Deep Learning Application and Practice\n(딥러닝 응용 및 실습)\n파이썬으로 배우는 기계학습 입문 외 7건", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: [['파이썬으로 배우는 기계학습 입문', 'HGUk+HGU05'], ['TensorFlow(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['Basic Definition for Deep Learning(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['Deep Learning(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['Deep Learning with TensorFlow(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['파이썬을 활용한 딥러닝 2(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['파이썬을 활용한 딥러닝 3(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['(개발중)딥러닝개론 및 응용', '']] },
  { id: 21, label: "Topics in Machine Learning\n(기계학습 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 9, color: NULL_COLOR, link: "" },
  { id: 22, label: "Topics in Artificial Intelligence\n(인공지능 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 9, color: NULL_COLOR, link: "" },

  { id: 23, label: "Reinforcement Learning\n(강화학습) 해당강좌없음", shape: VIS_SHAPE, level: 10, color: NULL_COLOR, link: "" },

  { id: 24, label: "Computer Graphics\n(컴퓨터그래픽)\n영상처리와 패턴인식", shape: VIS_SHAPE, level: 11, color: EXIST_COLOR, link: "SMUk+FD_SMU03" },
  { id: 25, label: "Computer Vision\n(컴퓨터비전)\n딥러닝 영상분석(코리아헤럴드) 외 1건", shape: VIS_SHAPE, level: 11, color: MATCH_COLOR, link: [['딥러닝 영상분석(코리아헤럴드)', 'http://www.abedu.co.kr/AI_MF/lecture/ps/4/is/6'], ['영상처리와 패턴인식', 'SMUk+FD_SMU03']] },
  { id: 26, label: "Biomedical Computing\n(생의학 컴퓨팅)\n바이오메디컬비전 및 응용 외 2건", shape: VIS_SHAPE, level: 11, color: NORMAL_COLOR, link: [['바이오메디컬비전 및 응용', 'SoongsilUnivK+soongsilmooc03K'], ['생명정보개론', 'SoongsilUnivK+soongsilmooc01K'], ['의공학-생명과 공학의 만남', 'POSTECHk+CITE241']] },
  { id: 27, label: "Applied Artificial Intelligence\n(인공지능 응용)\n바이오헬스 빅데이터 마이닝", shape: VIS_SHAPE, level: 11, color: NORMAL_COLOR, link: "KKUk+CK_KKUkbio002" },
];
var edges = [
  { from: 1, to: 3, color: { opacity: OP_HIGH } },
  { from: 4, to: 3, color: { opacity: OP_HIGH } },

  { from: 1, to: 4, color: { opacity: OP_HIGH } },

  { from: 1, to: 5, color: { opacity: OP_MID } },
  { from: 4, to: 5, color: { opacity: OP_HIGH } },

  { from: 0, to: 7, color: { opacity: OP_MID } },

  { from: 2, to: 8, color: { opacity: OP_MID } },
  { from: 3, to: 8, color: { opacity: OP_MID } },
  { from: 4, to: 8, color: { opacity: OP_MID } },
  { from: 5, to: 8, color: { opacity: OP_MID } },

  { from: 7, to: 9, color: { opacity: OP_HIGH } },
  { from: 10, to: 9, color: { opacity: OP_HIGH } },

  { from: 9, to: 10, color: { opacity: OP_HIGH } },
  { from: 7, to: 10, color: { opacity: OP_HIGH } },
  { from: 3, to: 10, color: { opacity: OP_HIGH } },

  { from: 7, to: 11, color: { opacity: OP_HIGH } },
  { from: 2, to: 11, color: { opacity: OP_HIGH } },
  { from: 8, to: 11, color: { opacity: OP_HIGH } },

  { from: 9, to: 12, color: { opacity: OP_MID } },
  { from: 7, to: 12, color: { opacity: OP_MID } },
  { from: 10, to: 12, color: { opacity: OP_HIGH } },
  { from: 3, to: 12, color: { opacity: OP_HIGH } },

  { from: 10, to: 13, color: { opacity: OP_MID } },
  { from: 7, to: 13, color: { opacity: OP_MID } },
  { from: 11, to: 13, color: { opacity: OP_HIGH } },

  { from: 12, to: 14, color: { opacity: OP_MID } },
  { from: 10, to: 14, color: { opacity: OP_MID } },
  { from: 13, to: 14, color: { opacity: OP_HIGH } },

  { from: 7, to: 15, color: { opacity: OP_HIGH } },

  { from: 15, to: 16, color: { opacity: OP_MID } },
  { from: 9, to: 16, color: { opacity: OP_HIGH } },
  { from: 7, to: 16, color: { opacity: OP_HIGH } },
  { from: 12, to: 16, color: { opacity: OP_HIGH } },
  { from: 8, to: 16, color: { opacity: OP_HIGH } },

  { from: 16, to: 17, color: { opacity: OP_HIGH } },
  { from: 9, to: 17, color: { opacity: OP_HIGH } },
  { from: 12, to: 17, color: { opacity: OP_HIGH } },
  { from: 10, to: 17, color: { opacity: OP_HIGH } },
  { from: 14, to: 17, color: { opacity: OP_HIGH } },

  { from: 7, to: 18, color: { opacity: OP_HIGH } },
  { from: 12, to: 18, color: { opacity: OP_MID } },
  { from: 8, to: 18, color: { opacity: OP_HIGH } },
  { from: 16, to: 18, color: { opacity: OP_MID } },
  { from: 17, to: 18, color: { opacity: OP_HIGH } },
  { from: 19, to: 18, color: { opacity: OP_MID } },

  { from: 17, to: 19, color: { opacity: OP_MID } },

  { from: 18, to: 20, color: { opacity: OP_HIGH } },
  { from: 16, to: 20, color: { opacity: OP_HIGH } },

  { from: 19, to: 21, color: { opacity: OP_HIGH } },

  { from: 16, to: 22, color: { opacity: OP_HIGH } },
  { from: 19, to: 22, color: { opacity: OP_HIGH } },
  { from: 17, to: 22, color: { opacity: OP_HIGH } },

  { from: 20, to: 23, color: { opacity: OP_HIGH } },
  { from: 17, to: 23, color: { opacity: OP_HIGH } },
  { from: 19, to: 23, color: { opacity: OP_HIGH } },

  { from: 7, to: 24, color: { opacity: OP_MID } },
  { from: 12, to: 24, color: { opacity: OP_MID } },
  { from: 16, to: 24, color: { opacity: OP_HIGH } },

  { from: 20, to: 25, color: { opacity: OP_HIGH } },
  { from: 18, to: 25, color: { opacity: OP_MID } },
  { from: 16, to: 25, color: { opacity: OP_MID } },
  { from: 17, to: 25, color: { opacity: OP_MID } },

  { from: 16, to: 26, color: { opacity: OP_MID } },
  { from: 17, to: 26, color: { opacity: OP_MID } },

  { from: 20, to: 27, color: { opacity: OP_HIGH } },
  { from: 16, to: 27, color: { opacity: OP_MID } },
  { from: 14, to: 27, color: { opacity: OP_HIGH } },
  { from: 19, to: 27, color: { opacity: OP_HIGH } },
];