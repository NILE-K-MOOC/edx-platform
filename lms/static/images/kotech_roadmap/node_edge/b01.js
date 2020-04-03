var nodes = [
  { id: 0, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍 외 1건", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: [['파이썬 프로그래밍', 'HGUk+HGU02'], ['AI 기초프로그래밍(전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai']] },
  { id: 1, label: "Math for Artificial Intelligence\n(인공지능을 위한 수학)\n머신 러닝을 위한 기초 수학 및 통계\n(코리아헤럴드) 외 3건", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: [['머신 러닝을 위한 기초 수학 및 통계', 'http://www.abedu.co.kr/AI/lecture/ps/1/is/4'], ['머신러닝을 위한 수학적 기초(고려사이버대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['AI 기초수학 I(선형대수) (전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['AI 기초수학II(확률 및 통계) (전남대학교)', 'https://sleonline.jnu.ac.kr/Course/Course100.aspx']] },
  { id: 2, label: "AI Ethics(인공지능 윤리)\n인격과 로봇(일부 유사 강좌) 외 1건", shape: VIS_SHAPE, level: 0, color: EXIST_COLOR, link: [['인격과 로봇', 'CKUk+CORE_CKU03k'], ['포스트휴먼 인문학', 'EwhaK+CORE_EW17002C']] },

  { id: 3, label: "Object-Oriented Programming\n(객체지향프로그래밍)\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "YeungnamUnivK+YU217001" },
  { id: 4, label: "Data Structures\n(데이터구조)\n자료구조 외 1건", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: [['자료구조(K-MOOC 상명대)', 'SMUk+SMU2018_01'], ['자료구조(K-MOOC 영남대)', 'YeungnamUnivK+YU216002']] },

  { id: 5, label: "Algorithms(알고리즘)\n자료구조(일부 유사 강좌)", shape: VIS_SHAPE, level: 2, color: EXIST_COLOR, link: "YeungnamUnivK+YU216002" },
  { id: 6, label: "Foundations of Data Science\n(데이터사이언스의 기초)\nR 데이터 분석 입문 외 2건", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: [['R 데이터 분석 입문', 'DKUK+DKUK0003'], ['디지털 시대의 커뮤니케이션', 'PTUk+SF_PMOOC01k'], ['My Major & Big Data', 'SMUk+ACE_SMU01']] },

  { id: 7, label: "Data Analysis(데이터분석)\n파이썬을 이용한 빅데이터 분석 외 1건", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: [['파이썬을 이용한 빅데이터 분석', 'SejonguniversityK+SJKMOOC05k'], ['예측 및 분류를 위한 데이터 애널리틱스 기법', 'POSTECHk+IMEN472']] },

  { id: 8, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론(일부 유사 강좌)", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 9, label: "Big Data Analytics\n(빅 데이터 분석)\n빅 데이터 첫 걸음 외 9건", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: [['빅 데이터 첫 걸음', 'POSTECHk+CSED490k'], ['빅데이터의 세계 원리와 응용', 'EwhaK+EW11237K'], ['빅데이터 플랫폼 구축 절차와 요소기술(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['빅데이터 분석기획 및 방법론(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['데이터 분석을 위한 분산처리 프레임워크(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['빅데이터와 인공지능의 응용', 'SNUk+SNU052_011k'], ['빅데이터와 머신러닝 소프트웨어', 'SNUk+SNU051_011k'], ['빅데이터와 텍스트마이닝', 'SejonguniversityK+SJMOOC10K'], ['(개발중) 빅데이터 분석 및 처리 기술', ''], ['(개발중) AWS 기반 IoT 빅데이터 실습 및 활용', '']] },

  { id: 10, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 11, label: "Introduction to Machine Learning\n(기계학습 개론)\n머신러닝 외 9건", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: [['머신러닝', 'SNUk+SNU050_011k'], ['Machine Learning for Data Science', 'KoreaUnivK+ku_eng_003'], ['자율주행을 위한 머신러닝', 'SKKUk+SKKU_30'], ['머신러닝-지도학습(고려사이버대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['머신러닝-비지도학습(고려사이버대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['지도학습:회귀(포항공과대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['지도학습:분류(포항공과대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['비지도학습:군집화와 차원축소(포항공과대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['기계학습 입문(전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['R을 활용한 머신러닝(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai']] },

  { id: 12, label: "Introduction to Deep Learning\n(딥러닝 개론)\n딥러닝 개론 외 1건", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: [['딥러닝 개론', 'DGUk+DGU_006k+DGU_006k'], ['심층학습(전남대학교)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai']] },
  { id: 13, label: "Advanced Machine Learning\n(고급 기계학습)\n매칭강좌없음", shape: VIS_SHAPE, level: 6, color: NULL_COLOR, link: "" },

  { id: 14, label: "Deep Learning Application and Practice\n(딥러닝 응용 및 실습)\n파이썬으로 배우는 기계학습 입문 외 7건", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: [['파이썬으로 배우는 기계학습 입문', 'HGUk+HGU05'], ['TensorFlow(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['Basic Definition for Deep Learning(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['Deep Learning(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['Deep Learning with TensorFlow(한국능률협회)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['파이썬을 활용한 딥러닝 2(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['파이썬을 활용한 딥러닝 3(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['(개발중)딥러닝개론 및 응용', '']] },
  { id: 15, label: "Topics in Artificial Intelligence\n(인공지능 연구)\n4차 산업혁명과 경영혁신(일부 유사 강좌) 외 2건", shape: VIS_SHAPE, level: 7, color: EXIST_COLOR, link: [['산업혁명과 경영혁신', 'SSUk+SSMOOC10K'], ['제4차 산업혁명 기반 기술의 이해', 'DCUk+CK_DCU_03'], ['4차 산업혁명과 수학', 'CNUk+ACE_CNU05']] },
  { id: 16, label: "Topics in Machine Learning\n(기계학습 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 7, color: NULL_COLOR, link: "" },

  { id: 17, label: "Reinforcement Learning\n(강화학습) 해당강좌없음", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },

  { id: 18, label: "Computer Vision\n(컴퓨터비전)\n영상 처리 및 실습(전남대학교) 외 1건", shape: VIS_SHAPE, level: 9, color: MATCH_COLOR, link: [['딥러닝 영상분석(코리아헤럴드)', 'https://www.matchup.kr/comm/pageView.do?page=biz/field/ai'], ['영상처리와 패턴인식', 'SMUk+FD_SMU03']] },
  { id: 19, label: "Natural Language Processing\n(자연어처리)\n자연어처리 및 실습(전남대학교) 외 2건", shape: VIS_SHAPE, level: 9, color: MATCH_COLOR, link: [['자연어처리 및 실습(전남대학교)', 'https://sleonline.jnu.ac.kr/Course/Course100.aspx'], ['텍스트 마이닝 실전 및 분석', 'YSUk+FD_YSU_LIS01k'], ['빅데이터와 텍스트마이닝', 'SejonguniversityK+SJMOOC10K']] },
  { id: 20, label: "Applied Artificial Intelligence\n(인공지능 응용)\n빅데이터와 인공지능의 응용 외 5건", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: [['빅데이터와 인공지능의 응용', 'SNUk+SNU052_011k'], ['바이오헬스 빅데이터 마이닝', 'KKUk+CK_KKUkbio002'], ['경영데이터마이닝', 'HYUk+HYUBUS3099k'], ['빅데이터와 머신러닝 소프트웨어', 'SNUk+SNU051_011k'], ['클라우드 컴퓨팅과 인공지능', 'KoreaUnivK+ku_eng_006'], ['ICBM+AI 기술을 접목한 리빙랩 설계 입문', 'KoreaUnivK+ku_eng_007']] },
];
var edges = [
  { from: 0, to: 3, color: { opacity: OP_HIGH } },
  { from: 4, to: 3, color: { opacity: OP_HIGH } },

  { from: 0, to: 4, color: { opacity: OP_HIGH } },
  { from: 3, to: 4, color: { opacity: OP_HIGH } },

  { from: 3, to: 5, color: { opacity: OP_MID } },
  { from: 0, to: 5, color: { opacity: OP_MID } },
  { from: 4, to: 5, color: { opacity: OP_HIGH } },

  { from: 0, to: 6, color: { opacity: OP_HIGH } },

  { from: 4, to: 7, color: { opacity: OP_LOW } },
  { from: 0, to: 7, color: { opacity: OP_HIGH } },
  { from: 6, to: 7, color: { opacity: OP_HIGH } },

  { from: 0, to: 8, color: { opacity: OP_HIGH } },

  { from: 5, to: 9, color: { opacity: OP_MID } },
  { from: 4, to: 9, color: { opacity: OP_MID } },
  { from: 7, to: 9, color: { opacity: OP_HIGH } },

  { from: 8, to: 10, color: { opacity: OP_LOW } },
  { from: 3, to: 10, color: { opacity: OP_HIGH } },
  { from: 0, to: 10, color: { opacity: OP_HIGH } },
  { from: 4, to: 10, color: { opacity: OP_HIGH } },
  { from: 1, to: 10, color: { opacity: OP_HIGH } },

  { from: 10, to: 11, color: { opacity: OP_HIGH } },
  { from: 3, to: 11, color: { opacity: OP_HIGH } },
  { from: 5, to: 11, color: { opacity: OP_HIGH } },
  { from: 0, to: 11, color: { opacity: OP_HIGH } },
  { from: 9, to: 11, color: { opacity: OP_HIGH } },
  { from: 1, to: 11, color: { opacity: OP_HIGH } },

  { from: 0, to: 12, color: { opacity: OP_HIGH } },
  { from: 5, to: 12, color: { opacity: OP_MID } },
  { from: 1, to: 12, color: { opacity: OP_HIGH } },
  { from: 10, to: 12, color: { opacity: OP_MID } },
  { from: 11, to: 12, color: { opacity: OP_HIGH } },
  { from: 13, to: 12, color: { opacity: OP_MID } },

  { from: 11, to: 13, color: { opacity: OP_HIGH } },

  { from: 12, to: 14, color: { opacity: OP_HIGH } },
  { from: 10, to: 14, color: { opacity: OP_HIGH } },

  { from: 8, to: 15, color: { opacity: OP_HIGH } },
  { from: 11, to: 15, color: { opacity: OP_HIGH } },
  { from: 13, to: 15, color: { opacity: OP_MID } },

  { from: 13, to: 16, color: { opacity: OP_HIGH } },

  { from: 14, to: 17, color: { opacity: OP_HIGH } },
  { from: 11, to: 17, color: { opacity: OP_HIGH } },
  { from: 13, to: 17, color: { opacity: OP_MID } },

  { from: 14, to: 18, color: { opacity: OP_HIGH } },
  { from: 12, to: 18, color: { opacity: OP_MID } },
  { from: 10, to: 18, color: { opacity: OP_MID } },
  { from: 11, to: 18, color: { opacity: OP_MID } },

  { from: 12, to: 19, color: { opacity: OP_MID } },
  { from: 10, to: 19, color: { opacity: OP_HIGH } },
  { from: 11, to: 19, color: { opacity: OP_MID } },
  { from: 16, to: 19, color: { opacity: OP_HIGH } },

  { from: 14, to: 20, color: { opacity: OP_HIGH } },
  { from: 10, to: 20, color: { opacity: OP_MID } },
  { from: 16, to: 20, color: { opacity: OP_HIGH } },
];