var nodes = [
  { id: 0, label: "Introduction Programming for Everyone\n(프로그래밍 개론)\nPython 프로그래밍 기초", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "http://www.dataedu.kr/course/1%ea%b3%bc%eb%aa%a9-python-%ed%94%84%eb%a1%9c%ea%b7%b8%eb%9e%98%eb%b0%8d-%ea%b8%b0%ec%b4%88/" },
  { id: 1, label: "Basic(Highschool)\nMathematics(기초 수학)\n매칭강좌없음", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "" },
  { id: 2, label: "AI Ethics(인공지능 윤리)\n인격과 로봇(일부 유사 강좌)", shape: VIS_SHAPE, level: 0, color: EXIST_COLOR, link: "CKUk+CORE_CKU03k" },

  { id: 3, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "HGUk+HGU02" },
  { id: 4, label: "Introduction to Statistics\n(통계학 개론)\n통계학의 이해 I", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "SookmyungK+SM_sta_004k" },
  { id: 5, label: "Probability and Discrete Mathematics\n(확률과 이산수학)\nAI 기초수학Ⅱ(확률 및 통계)\n(전남대학교)", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "https://sleonline.jnu.ac.kr/Course/Course100.aspx" },
  { id: 6, label: "Calculus(미적분학)\n알고 보면 쉬운 미적분 이론", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "POSTECHk+MATH311" },
  { id: 7, label: "Linear Algebra(선형대수)\n선형대수학", shape: VIS_SHAPE, level: 1, color: FEED_COLOR, link: "SKKUk+SKKU_2017_01" },

  { id: 8, label: "Math for Artificial Intelligence\n(인공지능을 위한 수학)\n머신 러닝을 위한 기초 수학 및 통계\n(코리아헤럴드)", shape: VIS_SHAPE, level: 2, color: MATCH_COLOR, link: "http://www.abedu.co.kr/AI/lecture/ps/1/is/4" },

  { id: 9, label: "Object-Oriented Programming\n(객체지향프로그래밍)\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "YeungnamUnivK+YU217001" },
  { id: 10, label: "Data Structures\n(데이터구조)\n자료구조", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SMUk+SMU2018_01" },

  { id: 11, label: "Logic Programming\n(논리 프로그래밍)\n매칭강좌없음", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 12, label: "Foundations of Data Science\n(데이터사이언스의 기초)\nR 데이터 분석 입문", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "DKUK+DKUK0003" },

  { id: 13, label: "Signals and Circuit Systems\n(신호 및 회로시스템) 전자회로", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "YeungnamUnivK+KOCW.YU215001" },
  { id: 14, label: "Data Analysis(데이터분석)\n파이썬을 이용한 빅데이터 분석", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SejonguniversityK+SJKMOOC05k" },

  { id: 15, label: "Computer Structures(컴퓨터구조)\n컴퓨터구조", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: "SMUCk+CK.SMUC03k" },
  { id: 16, label: "Algorithms(알고리즘)\n자료구조(일부 유사 강좌)", shape: VIS_SHAPE, level: 6, color: EXIST_COLOR, link: "YeungnamUnivK+YU216002" },
  { id: 17, label: "Big Data Analytics\n(빅 데이터 분석)\n빅 데이터 첫 걸음", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: "POSTECHk+CSED490k" },

  { id: 18, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론(일부 유사 강좌)", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: "" },

  { id: 19, label: "Hardware Systems\n(하드웨어 시스템)\n매칭강좌없음", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },
  { id: 20, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 8, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 21, label: "Introduction to Machine Learning\n(기계학습 개론)\n머신러닝", shape: VIS_SHAPE, level: 8, color: NORMAL_COLOR, link: "SNUk+SNU050_011k" },

  { id: 22, label: "Introduction to Deep Learning\n(딥러닝 개론)\n딥러닝 개론", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: "DGUk+DGU_006k+DGU_006k" },
  { id: 23, label: "Advanced Machine Learning\n(고급 기계학습)\n매칭강좌없음", shape: VIS_SHAPE, level: 9, color: NULL_COLOR, link: "" },

  { id: 24, label: "Deep Learning Application and Practice\n(딥러닝 응용 및 실습)\n파이썬으로 배우는 기계학습 입문", shape: VIS_SHAPE, level: 10, color: NORMAL_COLOR, link: "HGUk+HGU05" },
  { id: 25, label: "Computer Vision\n(컴퓨터비전)\n딥러닝 영상분석\n(코리아헤럴드)", shape: VIS_SHAPE, level: 10, color: MATCH_COLOR, link: "http://www.abedu.co.kr/AI_MF/lecture/ps/4/is/6" },
  { id: 26, label: "Natural Language Processing\n(자연어처리)\n자연어처리 및 실습(전남대학교)", shape: VIS_SHAPE, level: 10, color: MATCH_COLOR, link: "https://sleonline.jnu.ac.kr/Course/Course100.aspx" },
  { id: 27, label: "Topics in Artificial Intelligence\n(인공지능 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 10, color: NULL_COLOR, link: "" },
  { id: 28, label: "Topics in Machine Learning\n(기계학습 연구)\n매칭강좌없음", shape: VIS_SHAPE, level: 10, color: NULL_COLOR, link: "" },

  { id: 29, label: "Reinforcement Learning\n(강화학습) 해당강좌없음", shape: VIS_SHAPE, level: 11, color: NULL_COLOR, link: "" },
  { id: 30, label: "Introduction to Robotics\n(로봇공학 개론)\nFun-MOOC - 기계는 영원하다!", shape: VIS_SHAPE, level: 11, color: FEED_COLOR, link: "SNUk+SKP.M2794.000100k" },
  { id: 31, label: "Applied Artificial Intelligence\n(인공지능 응용)\n빅데이터와 인공지능의 응용", shape: VIS_SHAPE, level: 11, color: NORMAL_COLOR, link: "SNUk+SNU052_011k" },

  { id: 32, label: "Computer Graphics\n(컴퓨터그래픽)\n영상처리와 패턴인식", shape: VIS_SHAPE, level: 12, color: NORMAL_COLOR, link: "SMUk+FD_SMU03" },

  { id: 33, label: "Robot Kinematics and Dynamics(로봇 운동학 및 역학)\nRobot Manipulator and\nUnderwater Robot Application", shape: VIS_SHAPE, level: 13, color: FEED_COLOR, link: "SEOULTECHk+SMOOC03k" },
  { id: 34, label: "Human-Robot Interaction\n(휴먼-로봇 상호작용)\n매칭강좌없음", shape: VIS_SHAPE, level: 13, color: NULL_COLOR, link: "" },
  { id: 35, label: "Autonomous Agents\n(자율 에이젠트)\n매칭강좌없음", shape: VIS_SHAPE, level: 13, color: NULL_COLOR, link: "" },

  { id: 36, label: "Advanced Robotics Planning\n(고급로봇공학)\nHumanoid Robot", shape: VIS_SHAPE, level: 14, color: NORMAL_COLOR, link: "SEOULTECHk+SMOOC05k" },
  { id: 37, label: "Artificial Intelligence for Robotics\n(로봇공학을 위한 인공지능)\nMobile Robot Perception and Navigation", shape: VIS_SHAPE, level: 14, color: NORMAL_COLOR, link: "SEOULTECHk+SMOOC04k" },
];
var edges = [
  { from: 0, to: 3, color: { opacity: OP_MID } },

  { from: 1, to: 5, color: { opacity: OP_HIGH } },
  { from: 6, to: 5, color: { opacity: OP_HIGH } },

  { from: 1, to: 6, color: { opacity: OP_HIGH } },

  { from: 1, to: 7, color: { opacity: OP_MID } },
  { from: 6, to: 7, color: { opacity: OP_HIGH } },

  { from: 4, to: 8, color: { opacity: OP_MID } },
  { from: 5, to: 8, color: { opacity: OP_MID } },
  { from: 6, to: 8, color: { opacity: OP_MID } },
  { from: 7, to: 8, color: { opacity: OP_MID } },

  { from: 3, to: 9, color: { opacity: OP_HIGH } },

  { from: 9, to: 10, color: { opacity: OP_HIGH } },
  { from: 3, to: 10, color: { opacity: OP_HIGH } },
  { from: 5, to: 10, color: { opacity: OP_HIGH } },

  { from: 3, to: 12, color: { opacity: OP_HIGH } },
  { from: 4, to: 12, color: { opacity: OP_HIGH } },

  { from: 9, to: 13, color: { opacity: OP_MID } },
  { from: 3, to: 13, color: { opacity: OP_MID } },
  { from: 11, to: 13, color: { opacity: OP_MID } },

  { from: 10, to: 14, color: { opacity: OP_MID } },
  { from: 12, to: 14, color: { opacity: OP_MID } },

  { from: 9, to: 15, color: { opacity: OP_HIGH } },
  { from: 13, to: 15, color: { opacity: OP_MID } },

  { from: 13, to: 16, color: { opacity: OP_MID } },
  { from: 11, to: 16, color: { opacity: OP_MID } },
  { from: 10, to: 16, color: { opacity: OP_HIGH } },
  { from: 5, to: 16, color: { opacity: OP_HIGH } },

  { from: 16, to: 17, color: { opacity: OP_MID } },
  { from: 10, to: 17, color: { opacity: OP_MID } },
  { from: 14, to: 17, color: { opacity: OP_HIGH } },

  { from: 3, to: 18, color: { opacity: OP_HIGH } },

  { from: 15, to: 19, color: { opacity: OP_MID } },
  { from: 3, to: 19, color: { opacity: OP_HIGH } },
  { from: 13, to: 19, color: { opacity: OP_HIGH } },

  { from: 15, to: 20, color: { opacity: OP_HIGH } },
  { from: 9, to: 20, color: { opacity: OP_HIGH } },
  { from: 13, to: 20, color: { opacity: OP_MID } },
  { from: 3, to: 20, color: { opacity: OP_HIGH } },
  { from: 11, to: 20, color: { opacity: OP_MID } },
  { from: 10, to: 20, color: { opacity: OP_HIGH } },
  { from: 8, to: 20, color: { opacity: OP_HIGH } },

  { from: 20, to: 21, color: { opacity: OP_HIGH } },
  { from: 16, to: 21, color: { opacity: OP_HIGH } },
  { from: 9, to: 21, color: { opacity: OP_HIGH } },
  { from: 3, to: 21, color: { opacity: OP_HIGH } },
  { from: 14, to: 21, color: { opacity: OP_HIGH } },
  { from: 8, to: 21, color: { opacity: OP_HIGH } },

  { from: 3, to: 22, color: { opacity: OP_HIGH } },
  { from: 8, to: 22, color: { opacity: OP_HIGH } },
  { from: 16, to: 22, color: { opacity: OP_MID } },
  { from: 20, to: 22, color: { opacity: OP_MID } },
  { from: 21, to: 22, color: { opacity: OP_HIGH } },
  { from: 23, to: 22, color: { opacity: OP_MID } },

  { from: 21, to: 23, color: { opacity: OP_MID } },

  { from: 22, to: 24, color: { opacity: OP_HIGH } },
  { from: 20, to: 24, color: { opacity: OP_HIGH } },

  { from: 24, to: 25, color: { opacity: OP_HIGH } },
  { from: 22, to: 25, color: { opacity: OP_HIGH } },
  { from: 15, to: 25, color: { opacity: OP_HIGH } },
  { from: 20, to: 25, color: { opacity: OP_HIGH } },
  { from: 21, to: 25, color: { opacity: OP_HIGH } },

  { from: 22, to: 26, color: { opacity: OP_MID } },
  { from: 20, to: 26, color: { opacity: OP_HIGH } },
  { from: 21, to: 26, color: { opacity: OP_MID } },
  { from: 27, to: 26, color: { opacity: OP_HIGH } },

  { from: 18, to: 27, color: { opacity: OP_HIGH } },
  { from: 21, to: 27, color: { opacity: OP_HIGH } },
  { from: 23, to: 27, color: { opacity: OP_HIGH } },

  { from: 23, to: 28, color: { opacity: OP_HIGH } },

  { from: 24, to: 29, color: { opacity: OP_HIGH } },
  { from: 21, to: 29, color: { opacity: OP_HIGH } },
  { from: 23, to: 29, color: { opacity: OP_HIGH } },

  { from: 3, to: 30, color: { opacity: OP_HIGH } },
  { from: 10, to: 30, color: { opacity: OP_HIGH } },
  { from: 21, to: 30, color: { opacity: OP_MID } },

  { from: 24, to: 31, color: { opacity: OP_HIGH } },
  { from: 20, to: 31, color: { opacity: OP_HIGH } },
  { from: 17, to: 31, color: { opacity: OP_HIGH } },
  { from: 21, to: 31, color: { opacity: OP_HIGH } },

  { from: 25, to: 32, color: { opacity: OP_HIGH } },
  { from: 30, to: 32, color: { opacity: OP_HIGH } },

  { from: 34, to: 33, color: { opacity: OP_MID } },

  { from: 30, to: 34, color: { opacity: OP_MID } },
  { from: 26, to: 34, color: { opacity: OP_MID } },

  { from: 20, to: 35, color: { opacity: OP_MID } },
  { from: 31, to: 35, color: { opacity: OP_MID } },
  { from: 23, to: 35, color: { opacity: OP_MID } },

  { from: 33, to: 36, color: { opacity: OP_HIGH } },
  { from: 30, to: 36, color: { opacity: OP_HIGH } },
  { from: 31, to: 36, color: { opacity: OP_HIGH } },
  { from: 20, to: 36, color: { opacity: OP_HIGH } },

  { from: 36, to: 37, color: { opacity: OP_MID } },
  { from: 30, to: 37, color: { opacity: OP_MID } },
  { from: 20, to: 37, color: { opacity: OP_MID } },
  { from: 27, to: 37, color: { opacity: OP_MID } },
  { from: 31, to: 37, color: { opacity: OP_MID } },
];