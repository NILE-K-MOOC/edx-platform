var nodes = [
  { id: 0, label: "CoreEssCS 1\nHGUk+HGU02\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "" },
  { id: 1, label: "CoreEssMath 1\n003_002_009\n머신 러닝을 위한 기초 수학 및 통계\n(코리아헤럴드)", shape: VIS_SHAPE, level: 0, color: FEED_COLOR, link: "" },
  { id: 2, label: "CoreElecAI 3\nCKUk+CORE_CKU03k\n인격과 로봇\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 0, color: EXIST_COLOR, link: "" },

  { id: 3, label: "CoreElecCS 3\nYeungnamUnivK+YU217001\n객체지향형 프로그래밍과 자료구조", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "" },
  { id: 4, label: "CoreElecCS 4\nSMUk+SMU2018_01\n자료구조", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "" },

  { id: 5, label: "CoreElecCS 5\nYeungnamUnivK+YU216002\n자료구조\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 2, color: EXIST_COLOR, link: "" },
  { id: 6, label: "CoreElecDS 1\nDKUK+DKUK0003\nR 데이터 분석 입문", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: "" },

  { id: 7, label: "CoreElecDS 2\nSejonguniversityK+SJKMOOC05k\n파이썬을 이용한 빅데이터 분석", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "" },

  { id: 8, label: "CoreElecAI 1\nUnderstanding Artificial Intelligence", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 9, label: "CoreElecDS 3\nPOSTECHk+CSED490k\n빅 데이터 첫 걸음", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "" },

  { id: 10, label: "CoreEssAI 1\nSNUk+SNU048_011k\n인공지능의 기초", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "" },
  { id: 11, label: "CoreEssAI 3\nSNUk+SNU050_011k\n머신러닝", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "" },

  { id: 12, label: "CoreEssAI 2\nDGUk+DGU_006k+DGU_006k\n딥러닝 개론", shape: VIS_SHAPE, level: 6, color: NORMAL_COLOR, link: "" },
  { id: 13, label: "CoreEssAI 4\nAdvanced Machine Learning", shape: VIS_SHAPE, level: 6, color: NULL_COLOR, link: "" },

  { id: 14, label: "CoreElecAI 2\nHGUk+HGU05\n파이썬으로 배우는 기계학습 입문", shape: VIS_SHAPE, level: 7, color: NORMAL_COLOR, link: "" },
  { id: 15, label: "CoreElecAdv 1\nSSUk+SSMOOC10K\n4차 산업혁명과 경영혁신\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 7, color: EXIST_COLOR, link: "" },
  { id: 16, label: "CoreElecAdv 2\nTopics in Machine Learning", shape: VIS_SHAPE, level: 7, color: NULL_COLOR, link: "" },

  { id: 17, label: "CoreEssAI 5\nReinforcement Learning", shape: VIS_SHAPE, level: 8, color: NULL_COLOR, link: "" },

  { id: 18, label: "CoreEssAI 6\n002_002_007\n영상 처리 및 실습\n(전남대학교)", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: "" },
  { id: 19, label: "CoreEssAI 7\n002_004_006\n자연어처리 및 실습\n(전남대학교)", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: "" },
  { id: 20, label: "CoreElecAdv 4\nSNUk+SNU052_011k\n빅데이터와 인공지능의 응용", shape: VIS_SHAPE, level: 9, color: NORMAL_COLOR, link: "" },
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