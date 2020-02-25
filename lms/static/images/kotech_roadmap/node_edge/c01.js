var nodes = [
  { id: 0, label: "CoreElecCS 2\n010_008_029\nPython 프로그래밍 기초\n(한국능률협회)", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR },
  { id: 1, label: "CoreElecMath 1\nBasic (Highschool) Mathematics", shape: VIS_SHAPE, level: 0, color: NULL_COLOR },
  { id: 2, label: "CoreElecAI 3\nCKUk+CORE_CKU03k\n인격과 로봇\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 0, color: EXIST_COLOR },

  { id: 3, label: "CoreEssCS 1\nHGUk+HGU02\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR },
  { id: 4, label: "CoreElecMath 5\nSookmyungK+SM_sta_004k\n통계학의 이해 I", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR },
  { id: 5, label: "CoreElecMath 4\n002_002_002\nAI 기초수학Ⅱ\n(확률 및 통계)\n(전남대학교)", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR },
  { id: 6, label: "CoreElecMath 2\nPOSTECHk+MATH311\n알고 보면 쉬운 미적분 이론", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR },
  { id: 7, label: "CoreElecMath 3\nSKKUk+SKKU_2017_01\n선형대수학", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR },

  { id: 8, label: "CoreEssMath 1\n003_002_009\n머신 러닝을 위한 기초 수학 및 통계\n(코리아헤럴드)", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR },

  { id: 9, label: "CoreElecCS 3\nYeungnamUnivK+YU217001\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR },
  { id: 10, label: "CoreElecCS 4\nSMUk+SMU2018_01\n자료구조", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR },
  { id: 11, label: "CoreElecDS 1\nDKUK+DKUK0003\nR 데이터 분석 입문", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR },

  { id: 12, label: "CoreElecDS 2\nSejonguniversityK+SJKMOOC05k\n파이썬을 이용한 빅데이터 분석", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR },

  { id: 13, label: "CoreElecCS 5\nYeungnamUnivK+YU216002\n자료구조(일부 유사 강좌)", shape: VIS_SHAPE, level: 5, color: EXIST_COLOR },
  { id: 14, label: "CoreElecDS 3\nPOSTECHk+CSED490k\n빅 데이터 첫 걸음", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR },

  { id: 15, label: "CoreElecAI 1\nUnderstanding Artificial Intelligence", shape: VIS_SHAPE, level: 6, color: NULL_COLOR },

  { id: 16, label: "CoreEssAI 1\nSNUk+SNU048_011k\n인공지능의 기초", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR },
  { id: 17, label: "CoreEssAI 3\nSNUk+SNU050_011k\n머신러닝", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR },

  { id: 18, label: "CoreEssAI 2\nDGUk+DGU_006k+DGU_006k\n딥러닝 개론", shape: VIS_SHAPE, level: 8, color: NORMAL_COLOR },
  { id: 19, label: "CoreEssAI 4\nAdvanced Machine Learning", shape: VIS_SHAPE, level: 8, color: NULL_COLOR },

  { id: 20, label: "CoreElecAI 2\nHGUk+HGU05\n파이썬으로 배우는 기계학습 입문", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR },
  { id: 21, label: "CoreElecAdv 1\nTopics in Artificial Intelligence", shape: VIS_SHAPE, level: 9, color: NULL_COLOR },
  { id: 22, label: "CoreElecAdv 2\nTopics in Machine Learning", shape: VIS_SHAPE, level: 9, color: NULL_COLOR },

  { id: 23, label: "CoreEssAI 5\nReinforcement Learning", shape: VIS_SHAPE, level: 10, color: NULL_COLOR },

  { id: 24, label: "CoreEssAI 6\n003_002_038\n딥러닝 영상분석\n(코리아헤럴드)", shape: VIS_SHAPE, level: 11, color: NORMAL_COLOR },
  { id: 25, label: "CoreEssAI 7\n002_004_006\n자연어처리 및 실습\n(전남대학교)", shape: VIS_SHAPE, level: 11, color: NORMAL_COLOR },
  { id: 26, label: "CoreElecAdv 4\nSNUk+SNU052_011k\n빅데이터와 인공지능의 응용", shape: VIS_SHAPE, level: 11, color: NORMAL_COLOR },
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
  { from: 10, to: 9, color: { opacity: OP_HIGH } },

  { from: 9, to: 10, color: { opacity: OP_HIGH } },
  { from: 3, to: 10, color: { opacity: OP_HIGH } },
  { from: 5, to: 10, color: { opacity: OP_HIGH } },

  { from: 3, to: 11, color: { opacity: OP_HIGH } },
  { from: 4, to: 11, color: { opacity: OP_HIGH } },

  { from: 10, to: 12, color: { opacity: OP_MID } },
  { from: 3, to: 12, color: { opacity: OP_HIGH } },
  { from: 11, to: 12, color: { opacity: OP_HIGH } },

  { from: 9, to: 13, color: { opacity: OP_MID } },
  { from: 3, to: 13, color: { opacity: OP_MID } },
  { from: 10, to: 13, color: { opacity: OP_HIGH } },
  { from: 5, to: 13, color: { opacity: OP_HIGH } },

  { from: 13, to: 14, color: { opacity: OP_MID } },
  { from: 10, to: 14, color: { opacity: OP_MID } },
  { from: 12, to: 14, color: { opacity: OP_HIGH } },

  { from: 3, to: 15, color: { opacity: OP_MID } },

  { from: 15, to: 16, color: { opacity: OP_MID } },
  { from: 9, to: 16, color: { opacity: OP_HIGH } },
  { from: 3, to: 16, color: { opacity: OP_HIGH } },
  { from: 10, to: 16, color: { opacity: OP_HIGH } },
  { from: 14, to: 16, color: { opacity: OP_HIGH } },

  { from: 16, to: 17, color: { opacity: OP_HIGH } },
  { from: 9, to: 17, color: { opacity: OP_HIGH } },
  { from: 13, to: 17, color: { opacity: OP_HIGH } },
  { from: 10, to: 17, color: { opacity: OP_HIGH } },
  { from: 14, to: 17, color: { opacity: OP_HIGH } },
  { from: 8, to: 17, color: { opacity: OP_HIGH } },

  { from: 3, to: 18, color: { opacity: OP_HIGH } },
  { from: 13, to: 18, color: { opacity: OP_MID } },
  { from: 12, to: 18, color: { opacity: OP_HIGH } },
  { from: 16, to: 18, color: { opacity: OP_MID } },
  { from: 17, to: 18, color: { opacity: OP_HIGH } },
  { from: 19, to: 18, color: { opacity: OP_MID } },

  { from: 17, to: 19, color: { opacity: OP_HIGH } },

  { from: 18, to: 20, color: { opacity: OP_HIGH } },
  { from: 16, to: 20, color: { opacity: OP_HIGH } },

  { from: 15, to: 21, color: { opacity: OP_HIGH } },
  { from: 17, to: 21, color: { opacity: OP_HIGH } },
  { from: 19, to: 21, color: { opacity: OP_MID } },

  { from: 19, to: 22, color: { opacity: OP_HIGH } },

  { from: 20, to: 23, color: { opacity: OP_HIGH } },
  { from: 17, to: 23, color: { opacity: OP_HIGH } },
  { from: 19, to: 23, color: { opacity: OP_HIGH } },

  { from: 20, to: 24, color: { opacity: OP_HIGH } },
  { from: 18, to: 24, color: { opacity: OP_MID } },
  { from: 16, to: 24, color: { opacity: OP_MID } },
  { from: 17, to: 24, color: { opacity: OP_MID } },

  { from: 18, to: 25, color: { opacity: OP_MID } },
  { from: 16, to: 25, color: { opacity: OP_HIGH } },
  { from: 17, to: 25, color: { opacity: OP_MID } },
  { from: 22, to: 25, color: { opacity: OP_HIGH } },

  { from: 20, to: 26, color: { opacity: OP_HIGH } },
  { from: 16, to: 26, color: { opacity: OP_MID } },
  { from: 22, to: 26, color: { opacity: OP_HIGH } },
];