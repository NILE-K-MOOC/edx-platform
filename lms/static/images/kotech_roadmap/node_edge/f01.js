var nodes = [
  { id: 0, label: "CoreElecCS 2\n010_008_029\nPython 프로그래밍 기초\n(한국능률협회)", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "010_008_029" },
  { id: 1, label: "CoreEssCS 1\nHGUk+HGU02\n파이썬 프로그래밍", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "HGUk+HGU02" },
  { id: 2, label: "CoreElecAI 1\nUnderstanding Artificial Intelligence", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },
  { id: 3, label: "CoreEssAI 1\nSNUk+SNU048_011k\n인공지능의 기초", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
];
var edges = [
  { from: 0, to: 1, color: { opacity: OP_MID } },
  { from: 1, to: 2, color: { opacity: OP_HIGH } },
  { from: 2, to: 3, color: { opacity: OP_HIGH } },
];
