var nodes = [
  { id: 0, label: "Introduction Programming for Everyone\n(프로그래밍 개론)\n머신러닝을 위한 파이썬 기초(Match業 강좌)", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: [['머신러닝을 위한 파이썬 기초(Match業 강좌)', 'https://iclass.postech.ac.kr/courses/5d6cdd4ec5728b2c694db285']] },
  { id: 1, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "HGUk+HGU02" },
  { id: 2, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: "KoreaUnivK+ku_eng_004" },
  { id: 3, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
];
var edges = [
  { from: 0, to: 1, color: { opacity: OP_MID } },
  { from: 1, to: 2, color: { opacity: OP_HIGH } },
  { from: 2, to: 3, color: { opacity: OP_HIGH } },
];
