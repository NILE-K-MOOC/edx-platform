var nodes = [
  { id: 0, label: "Introduction Programming for Everyone\n(프로그래밍 개론)\nPython 프로그래밍 기초", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "010_008_029" },
  { id: 1, label: "Basic(Highschool)\nMathematics(기초 수학)\n매칭강좌없음", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "" },

  { id: 2, label: "Introduction to Statistics\n(통계학 개론)\n통계학의 이해 I", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "SookmyungK+SM_sta_004k" },
  { id: 3, label: "Probability and Discrete Mathematics\n(확률과 이산수학)\nAI 기초수학Ⅱ(확률 및 통계)\n(전남대학교)", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "002_002_002" },
  { id: 4, label: "Calculus(미적분학)\n알고 보면 쉬운 미적분 이론", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "POSTECHk+MATH311" },
  { id: 5, label: "CoreElecMath 3\nSKKUk+SKKU_2017_01\n선형대수", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "SKKUk+SKKU_2017_01" },
  { id: 6, label: "AI Ethics(인공지능 윤리)\n인격과 로봇(일부 유사 강좌)", shape: VIS_SHAPE, level: 1, color: EXIST_COLOR, link: "CKUk+CORE_CKU03k" },

  { id: 7, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: "HGUk+HGU02" },
  { id: 8, label: "Math for Artificial Intelligence\n(인공지능을 위한 수학)\n머신 러닝을 위한 기초 수학 및 통계\n(코리아헤럴드)", shape: VIS_SHAPE, level: 2, color: MATCH_COLOR, link: "003_002_009" },

  { id: 9, label: "Object-Oriented Programming\n(객체지향프로그래밍)\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "YeungnamUnivK+YU217001" },
  { id: 10, label: "Data Structures\n(데이터구조)\n자료구조", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SMUk+SMU2018_01" },
  { id: 11, label: "Foundations of Data Science\n(데이터사이언스의 기초)\nR 데이터 분석 입문", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "DKUK+DKUK0003" },

  { id: 12, label: "Algorithms(알고리즘)\n자료구조(일부 유사 강좌)", shape: VIS_SHAPE, level: 4, color: EXIST_COLOR, link: "YeungnamUnivK+YU216002" },
  { id: 13, label: "Data Analysis(데이터분석)\n파이썬을 이용한 빅데이터 분석", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "SejonguniversityK+SJKMOOC05k" },

  { id: 14, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론(일부 유사 강좌)", shape: VIS_SHAPE, level: 5, color: NULL_COLOR, link: "" },
  { id: 15, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 16, label: "Big Data Analytics\n(빅 데이터 분석)\n빅 데이터 첫 걸음", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "POSTECHk+CSED490k" },

  { id: 17, label: "Introduction to Deep Learning\n(딥러닝 개론)\n딥러닝 개론", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: "DGUk+DGU_006k+DGU_006k" },
  { id: 18, label: "Introduction to Machine Learning\n(기계학습 개론)\n머신러닝", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: "SNUk+SNU050_011k" },

  { id: 19, label: "Deep Learning Application and Practice\n(딥러닝 응용 및 실습)\n파이썬으로 배우는 기계학습 입문", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: "HGUk+HGU05" },
  { id: 20, label: "Advanced Machine Learning\n(고급 기계학습)\n매칭강좌없음", shape: VIS_SHAPE, level: 7, color: NULL_COLOR, link: "" },

  { id: 21, label: "Reinforcement Learning\n(강화학습) 해당강좌없음", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },
  { id: 22, label: "Topics in Machine Learning\n(기계학습 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },
  { id: 23, label: "Topics in Artificial Intelligence\n(인공지능 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },

  { id: 24, label: "Computer Vision\n(컴퓨터비전)\n딥러닝 영상분석(코리아헤럴드)", shape: VIS_SHAPE, level: 9, color: MATCH_COLOR, link: "003_002_038" },
  { id: 25, label: "Human Intelligence and AI\n(인간지능과 인공지능)\n매칭강좌없음", shape: VIS_SHAPE, level: 9, color: NULL_COLOR, link: "" },
  { id: 26, label: "Introduction to Cognitive\nScience(인지과학 개론)\n인간 뇌의 이해", shape: VIS_SHAPE, level: 9, color: FEED_COLOR, link: "SNUk+SNU047_019k" },

  { id: 27, label: "Natural Language Processing\n(자연어처리)\n자연어처리 및 실습(전남대학교)", shape: VIS_SHAPE, level: 10, color: MATCH_COLOR, link: "002_004_006" },
  { id: 28, label: "Probabilistic Graphical Models\n(확률적 그래픽 모델)\n매칭강좌없음", shape: VIS_SHAPE, level: 10, color: NULL_COLOR, link: "" },

  { id: 29, label: "Computational Perception\n(계산 인식)\n매칭강좌없음", shape: VIS_SHAPE, level: 11, color: NULL_COLOR, link: "" },
  { id: 30, label: "Neural Computation\n(신경 계산)\n매칭강좌없음", shape: VIS_SHAPE, level: 11, color: NULL_COLOR, link: "" },
  { id: 31, label: "Computational Cognitive Science\n(전산 인지과학)\n매칭강좌없음", shape: VIS_SHAPE, level: 11, color: NULL_COLOR, link: "" },
  { id: 32, label: "Inference and Information\nTheory\n(추론 및 정보이론)\n매칭강좌없음", shape: VIS_SHAPE, level: 11, color: NULL_COLOR, link: "" },
];
var edges = [
  { from: 1, to: 3, color: { opacity: OP_HIGH } },
  { from: 4, to: 3, color: { opacity: OP_HIGH } },

  { from: 1, to: 4, color: { opacity: OP_HIGH } },

  { from: 1, to: 5, color: { opacity: OP_HIGH } },
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
  { from: 8, to: 11, color: { opacity: OP_HIGH } },

  { from: 9, to: 12, color: { opacity: OP_MID } },
  { from: 7, to: 12, color: { opacity: OP_MID } },
  { from: 10, to: 12, color: { opacity: OP_HIGH } },
  { from: 3, to: 12, color: { opacity: OP_HIGH } },

  { from: 10, to: 13, color: { opacity: OP_MID } },
  { from: 7, to: 13, color: { opacity: OP_MID } },
  { from: 11, to: 13, color: { opacity: OP_MID } },

  { from: 7, to: 14, color: { opacity: OP_HIGH } },

  { from: 14, to: 15, color: { opacity: OP_HIGH } },
  { from: 9, to: 15, color: { opacity: OP_HIGH } },
  { from: 7, to: 15, color: { opacity: OP_HIGH } },
  { from: 10, to: 15, color: { opacity: OP_HIGH } },
  { from: 8, to: 15, color: { opacity: OP_HIGH } },

  { from: 12, to: 16, color: { opacity: OP_MID } },
  { from: 10, to: 16, color: { opacity: OP_MID } },
  { from: 13, to: 16, color: { opacity: OP_MID } },

  { from: 7, to: 17, color: { opacity: OP_HIGH } },
  { from: 14, to: 17, color: { opacity: OP_HIGH } },
  { from: 15, to: 17, color: { opacity: OP_MID } },
  { from: 18, to: 17, color: { opacity: OP_HIGH } },
  { from: 20, to: 17, color: { opacity: OP_MID } },

  { from: 15, to: 18, color: { opacity: OP_HIGH } },
  { from: 9, to: 18, color: { opacity: OP_HIGH } },
  { from: 12, to: 18, color: { opacity: OP_HIGH } },
  { from: 7, to: 18, color: { opacity: OP_HIGH } },
  { from: 8, to: 18, color: { opacity: OP_HIGH } },
  { from: 11, to: 18, color: { opacity: OP_HIGH } },

  { from: 17, to: 19, color: { opacity: OP_HIGH } },
  { from: 15, to: 19, color: { opacity: OP_HIGH } },

  { from: 18, to: 20, color: { opacity: OP_MID } },

  { from: 19, to: 21, color: { opacity: OP_HIGH } },
  { from: 18, to: 21, color: { opacity: OP_HIGH } },
  { from: 20, to: 21, color: { opacity: OP_HIGH } },

  { from: 20, to: 22, color: { opacity: OP_MID } },

  { from: 14, to: 23, color: { opacity: OP_HIGH } },
  { from: 20, to: 23, color: { opacity: OP_MID } },
  { from: 18, to: 23, color: { opacity: OP_MID } },

  { from: 19, to: 24, color: { opacity: OP_HIGH } },
  { from: 17, to: 24, color: { opacity: OP_MID } },
  { from: 15, to: 24, color: { opacity: OP_MID } },
  { from: 18, to: 24, color: { opacity: OP_MID } },

  { from: 15, to: 25, color: { opacity: OP_MID } },

  { from: 17, to: 27, color: { opacity: OP_MID } },
  { from: 15, to: 27, color: { opacity: OP_HIGH } },
  { from: 22, to: 27, color: { opacity: OP_MID } },
  { from: 18, to: 27, color: { opacity: OP_MID } },

  { from: 20, to: 28, color: { opacity: OP_MID } },
  { from: 3, to: 28, color: { opacity: OP_MID } },

  { from: 25, to: 29, color: { opacity: OP_HIGH } },
  { from: 18, to: 29, color: { opacity: OP_MID } },
  { from: 26, to: 29, color: { opacity: OP_HIGH } },

  { from: 7, to: 30, color: { opacity: OP_MID } },
  { from: 26, to: 30, color: { opacity: OP_MID } },
  { from: 8, to: 30, color: { opacity: OP_HIGH } },

  { from: 30, to: 31, color: { opacity: OP_MID } },
  { from: 26, to: 31, color: { opacity: OP_MID } },
  { from: 15, to: 31, color: { opacity: OP_MID } },
  { from: 22, to: 31, color: { opacity: OP_MID } },

  { from: 28, to: 32, color: { opacity: OP_MID } },
];