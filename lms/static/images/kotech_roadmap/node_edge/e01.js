var nodes = [
  { id: 0, label: "CoreElecAI 1\nUnderstanding Artificial Intelligence", shape: VIS_SHAPE, level: 0, color: NULL_COLOR, link: "" },
  { id: 1, label: "CoreElecAI 3\nCKUk+CORE_CKU03k\n인격과 로봇\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 0, color: EXIST_COLOR, link: "CKUk+CORE_CKU03k" },

  { id: 2, label: "CoreEssAI 1\nSNUk+SNU048_011k\n인공지능의 기초", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 3, label: "SpcElecEcon 2\nSNUk+SNU200_105k\n경제학원론 – 미시경제학", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "SNUk+SNU200_105k" },

  { id: 4, label: "SpcElecEcon 3\nMachine Learning for Trading", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },
  { id: 5, label: "SpcElecBsn 1\nArtificial Intelligence for Business", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },
  { id: 6, label: "SpcElecEcon 1\nJEJUk+KOCW_JEJU01\n계량경제학", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: "JEJUk+KOCW_JEJU01" },
];
var edges = [
  { from: 0, to: 2, color: { opacity: OP_HIGH } },

  { from: 2, to: 4, color: { opacity: OP_MID } },

  { from: 2, to: 5, color: { opacity: OP_HIGH } },

  { from: 2, to: 6, color: { opacity: OP_MID } },
  { from: 1, to: 6, color: { opacity: OP_MID } },
  { from: 3, to: 6, color: { opacity: OP_HIGH } },
];