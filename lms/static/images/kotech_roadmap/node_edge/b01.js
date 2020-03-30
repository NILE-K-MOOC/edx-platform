var nodes = [
  { id: 0, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "HGUk+HGU02" },
  { id: 1, label: "Math for Artificial Intelligence\n(인공지능을 위한 수학)\n머신 러닝을 위한 기초 수학 및 통계\n(코리아헤럴드)", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "http://www.abedu.co.kr/AI/lecture/ps/1/is/4" },
  { id: 2, label: "AI Ethics(인공지능 윤리)\n인격과 로봇(일부 유사 강좌)", shape: VIS_SHAPE, level: 0, color: EXIST_COLOR, link: "CKUk+CORE_CKU03k" },

  { id: 3, label: "Object-Oriented Programming\n(객체지향프로그래밍)\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "YeungnamUnivK+YU217001" },
  { id: 4, label: "Data Structures\n(데이터구조)\n자료구조", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "SMUk+SMU2018_01" },

  { id: 5, label: "Algorithms(알고리즘)\n자료구조(일부 유사 강좌)", shape: VIS_SHAPE, level: 2, color: EXIST_COLOR, link: "YeungnamUnivK+YU216002" },
  { id: 6, label: "Foundations of Data Science\n(데이터사이언스의 기초)\nR 데이터 분석 입문", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: "DKUK+DKUK0003" },

  { id: 7, label: "Data Analysis(데이터분석)\n파이썬을 이용한 빅데이터 분석", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SejonguniversityK+SJKMOOC05k" },

  { id: 8, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론(일부 유사 강좌)", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 9, label: "Big Data Analytics\n(빅 데이터 분석)\n빅 데이터 첫 걸음", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "POSTECHk+CSED490k" },

  { id: 10, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 11, label: "Introduction to Machine Learning\n(기계학습 개론)\n머신러닝", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SNUk+SNU050_011k" },

  { id: 12, label: "Introduction to Deep Learning\n(딥러닝 개론)\n딥러닝 개론", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: "DGUk+DGU_006k+DGU_006k" },
  { id: 13, label: "Advanced Machine Learning\n(고급 기계학습)\n매칭강좌없음", shape: VIS_SHAPE, level: 6, color: NULL_COLOR, link: "" },

  { id: 14, label: "Deep Learning Application and Practice\n(딥러닝 응용 및 실습)\n파이썬으로 배우는 기계학습 입문", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: "HGUk+HGU05" },
  { id: 15, label: "Topics in Artificial Intelligence\n(인공지능 연구)\n4차 산업혁명과 경영혁신(일부 유사 강좌)", shape: VIS_SHAPE, level: 7, color: EXIST_COLOR, link: "SSUk+SSMOOC10K" },
  { id: 16, label: "Topics in Machine Learning\n(기계학습 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 7, color: NULL_COLOR, link: "" },

  { id: 17, label: "Reinforcement Learning\n(강화학습) 해당강좌없음", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },

  { id: 18, label: "Computer Vision\n(컴퓨터비전)\n영상 처리 및 실습(전남대학교)", shape: VIS_SHAPE, level: 9, color: MATCH_COLOR, link: "002_002_007" },
  { id: 19, label: "Natural Language Processing\n(자연어처리)\n자연어처리 및 실습(전남대학교)", shape: VIS_SHAPE, level: 9, color: MATCH_COLOR, link: "https://sleonline.jnu.ac.kr/Course/Course100.aspx" },
  { id: 20, label: "Applied Artificial Intelligence\n(인공지능 응용)\n빅데이터와 인공지능의 응용", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: "SNUk+SNU052_011k" },
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