var nodes = [
  { id: 0, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "KoreaUnivK+ku_eng_004" },
  { id: 1, label: "AI Ethics(인공지능 윤리)\n인격과 로봇 외 2건", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: [['인격과 로봇', 'CKUk+CORE_CKU03k'], ['포스트휴먼 인문학', 'EwhaK+CORE_EW17002C'], ['인공지능 윤리(서울사이버대, 개발예정)', '']] },

  { id: 2, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 3, label: "Economics(경제학 개론)\n경제학원론-미시경제학", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "SNUk+SNU200_105k" },

  { id: 4, label: "Machine Learning for Trading\n(거래를 위한 기계학습)\n금융 AI(Financial Artificial Intelligence)(중앙대, 개발예정)", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },
  { id: 5, label: "Artificial Intelligence for Business\n(비즈니스를 위한 인공지능)\n비즈니스를 위한 인공지능(성신여대, 개발예정)", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },
  { id: 6, label: "Economics and Computation\n(계량경제학)\n계량경제학", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: "JEJUk+KOCW_JEJU01" },
];
var edges = [
  { from: 0, to: 2, color: { opacity: OP_HIGH } },

  { from: 2, to: 4, color: { opacity: OP_MID } },

  { from: 2, to: 5, color: { opacity: OP_HIGH } },

  { from: 2, to: 6, color: { opacity: OP_MID } },
  { from: 1, to: 6, color: { opacity: OP_MID } },
  { from: 3, to: 6, color: { opacity: OP_HIGH } },
];