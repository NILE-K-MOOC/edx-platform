var nodes = [
  { id: 0, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "HGUk+HGU02" },
  { id: 1, label: "Math for Artificial Intelligence\n(인공지능을 위한 수학)\n머신 러닝을 위한 기초 수학 및 통계\n(Match業 강좌)", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "http://www.abedu.co.kr/AI/lecture/ps/1/is/4" },
  { id: 2, label: "AI Ethics(인공지능 윤리)\n인격과 로봇 외 2건", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: [['인격과 로봇', 'CKUk+CORE_CKU03k'], ['포스트휴먼 인문학', 'EwhaK+CORE_EW17002C'], ['인공지능 윤리(, 개발예정)', '']] },

  { id: 3, label: "Object-Oriented Programming\n(객체지향프로그래밍)\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "YeungnamUnivK+YU217001" },
  { id: 4, label: "Data Structures\n(데이터구조)\n자료구조 외 1건", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: [['자료구조(K-MOOC 상명대)', 'SMUk+SMU2018_01'], ['자료구조(K-MOOC 영남대)', 'YeungnamUnivK+YU216002']] },

  { id: 5, label: "Algorithms(알고리즘)\n자료구조 외 1건", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: [['자료구조', 'YeungnamUnivK+YU216002'],['인공지능을 위한 알고리즘과 자료구조: 이론, 코딩, 그리고 컴퓨팅 사고(성균관대, 개발예정)','']] },
  { id: 6, label: "Foundations of Data Science\n(데이터사이언스의 기초)\nR 데이터 분석 입문 외 2건", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: [['R 데이터 분석 입문', 'DKUK+DKUK0003'], ['디지털 시대의 커뮤니케이션', 'PTUk+SF_PMOOC01k'], ['My Major & Big Data', 'SMUk+ACE_SMU01']] },

  { id: 7, label: "Data Analysis(데이터분석)\n파이썬을 이용한 빅데이터 분석 외 1건", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: [['파이썬을 이용한 빅데이터 분석', 'SejonguniversityK+SJKMOOC05k'], ['예측 및 분류를 위한 데이터 애널리틱스 기법', 'POSTECHk+IMEN472']] },

  { id: 8, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "KoreaUnivK+ku_eng_004" },
  { id: 9, label: "Big Data Analytics\n(빅 데이터 분석)\n빅 데이터 첫 걸음 외 6건", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: [['빅 데이터 첫 걸음', 'POSTECHk+CSED490k'], ['빅데이터의 세계 원리와 응용', 'EwhaK+EW11237K'], ['빅데이터와 인공지능의 응용', 'SNUk+SNU052_011k'], ['빅데이터와 머신러닝 소프트웨어', 'SNUk+SNU051_011k'], ['빅데이터와 텍스트마이닝', 'SejonguniversityK+SJMOOC10K'], ['빅데이터 분석 및 처리 기술', ''], ['AWS 기반 IoT 빅데이터 실습 및 활용', '']] },

  { id: 10, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 11, label: "Introduction to Machine Learning\n(기계학습 개론)\n머신러닝 외 5건", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: [['머신러닝', 'SNUk+SNU050_011k'], ['Machine Learning for Data Science', 'KoreaUnivK+ku_eng_003'], ['자율주행을 위한 머신러닝', 'SKKUk+SKKU_30'], ['지도학습:회귀(Match業 강좌)', 'https://iclass.postech.ac.kr/courses/5d6db0eec5728b505b13d593'], ['지도학습:분류(Match業 강좌)', 'https://iclass.postech.ac.kr/courses/5d6db194c5728b50b04d5fb3'], ['비지도학습:군집화와 차원축소(Match業 강좌)', 'https://iclass.postech.ac.kr/courses/5d6db210c5728b5081032723']] },

  { id: 12, label: "Introduction to Deep Learning\n(딥러닝 개론)\n딥러닝 개론", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: "DGUk+DGU_006k+DGU_006k" },
  { id: 13, label: "Advanced Machine Learning\n(고급 기계학습)\n딥러닝 시대에도 필요한 고급 기계학습(성균관대, 개발예정)", shape: VIS_SHAPE, level: 6, color: NULL_COLOR, link: "" },

  { id: 14, label: "Deep Learning Application and Practice\n(딥러닝 응용 및 실습)\n파이썬으로 배우는 기계학습 입문 외 1건", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: [['파이썬으로 배우는 기계학습 입문', 'HGUk+HGU05'], ['딥러닝개론 및 응용', '']] },
  { id: 15, label: "Topics in Artificial Intelligence\n(인공지능 연구)\n4차 산업혁명과 경영혁신 외 2건", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: [['산업혁명과 경영혁신', 'SSUk+SSMOOC10K'], ['제4차 산업혁명 기반 기술의 이해', 'DCUk+CK_DCU_03'], ['4차 산업혁명과 수학', 'CNUk+ACE_CNU05']] },
  { id: 16, label: "Topics in Machine Learning\n(기계학습 연구)\n개발예정강좌", shape: VIS_SHAPE, level: 7, color: NULL_COLOR, link: "" },

  { id: 17, label: "Reinforcement Learning\n(강화학습) 개발예정강좌", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },

  { id: 18, label: "Computer Vision\n(컴퓨터비전)\n딥러닝 영상분석(Match業 강좌) 외 1건", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: [['딥러닝 영상분석(Match業 강좌)', 'http://www.abedu.co.kr/AI_MF/lecture/ps/4/is/6'], ['영상처리와 패턴인식', 'SMUk+FD_SMU03']] },
  { id: 19, label: "Natural Language Processing\n(자연어처리)\n텍스트 마이닝 실전 및 분석 외 1건", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: [['텍스트 마이닝 실전 및 분석', 'YSUk+FD_YSU_LIS01k'], ['빅데이터와 텍스트마이닝', 'SejonguniversityK+SJMOOC10K']] },
  { id: 20, label: "Applied Artificial Intelligence\n(인공지능 응용)\n빅데이터와 인공지능의 응용 외 6건", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: [['빅데이터와 인공지능의 응용', 'SNUk+SNU052_011k'], ['바이오헬스 빅데이터 마이닝', 'KKUk+CK_KKUkbio002'], ['경영데이터마이닝', 'HYUk+HYUBUS3099k'], ['빅데이터와 머신러닝 소프트웨어', 'SNUk+SNU051_011k'], ['클라우드 컴퓨팅과 인공지능', 'KoreaUnivK+ku_eng_006'], ['ICBM+AI 기술을 접목한 리빙랩 설계 입문', 'KoreaUnivK+ku_eng_007'], ['자율주행 자동차용 인공지능 시스템(현대 NGV, 개발예정)', '']] },
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