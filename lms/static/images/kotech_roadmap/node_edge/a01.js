var nodes = [
  { id: 0, label: "CoreEssAI 1\nSNUk+SNU048_011k\n인공지능의 기초", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 1, label: "CoreEssAI 3\nSNUk+SNU050_011k\n머신러닝", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "SNUk+SNU050_011k" },
  { id: 2, label: "CoreElecAI 3\nCKUk+CORE_CKU03\n인격과 로봇\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 0, color: EXIST_COLOR, link: "CKUk+CORE_CKU03" },

  { id: 3, label: "CoreEssAI 2\nDGUk+DGU_006k+DGU_006k\n딥러닝 개론", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "DGUk+DGU_006k+DGU_006k" },
  { id: 4, label: "CoreEssAI 4\nAdvanced Machine Learning", shape: VIS_SHAPE, level: 1, color: NULL_COLOR, link: "" },

  { id: 5, label: "CoreElecAI 2\nHGUk+HGU05\n파이썬으로 배우는 기계학습 입문", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: "HGUk+HGU05" },
  { id: 6, label: "CoreElecAdv 1\nTopics in Artificial Intelligence", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },
  { id: 7, label: "CoreElecAdv 2\nTopics in Machine Learning", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },

  { id: 8, label: "SpcElecRB 1\nSNUk+SKP.M2794.000100k\nFun-MOOC\n기계는 영원하다!", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SNUk+SKP.M2794.000100k" },
  { id: 9, label: "CoreEssAI 5\nReinforcement Learning", shape: VIS_SHAPE, level: 3, color: NULL_COLOR, link: "" },
  { id: 10, label: "SpcElecAdv 3\n007_001_041\n추론응용 모델링\n(코리아헤럴드)\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 3, color: EXIST_COLOR, link: "007_001_041" },
  { id: 11, label: "SpcElecEcon 1\nJEJUk+KOCW_JEJU01\n계량경제학", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "JEJUk+KOCW_JEJU01" },
  { id: 12, label: "SpcElecCog 1\nSNUk+SNU047_019k\n인간 뇌의 이해", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SNUk+SNU047_019k" },

  { id: 13, label: "SpcElecBio 1\nSoongsilUnivK+soongsilmooc03K\n바이오메디컬비전 및 응용", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "SoongsilUnivK+soongsilmooc03K" },
  { id: 14, label: "SpcElecRB 2\nSEOULTECHk+SMOOC04k\nMobile Robot Perception and Navigation", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "SEOULTECHk+SMOOC04k" },
  { id: 15, label: "CoreEssAI 6\n003_002_038\n딥러닝 영상분석\n(코리아헤럴드)", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "003_002_038" },
  { id: 16, label: "CoreEssAI 7\n002_004_006\n자연어처리 및 실습\n(전남대학교)", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "002_004_006" },
  { id: 17, label: "SpcElecNLP 1\nSNUk+CORE_SNU041_040k\n언어와 인간", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "SNUk+CORE_SNU041_040k" },
  { id: 18, label: "SpcElecAdv 1\nProbabilistic Graphical\nModels", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 19, label: "SpcElecBsn 1\nArtificial Intelligence\nfor Business", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 20, label: "SpcElecCog 2\nComputational Cognitive Science", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },

  { id: 21, label: "SpcElecAdv 2\nSMUk+FD_SMU03\n영상처리와 패턴인식\n(일부 유사 강좌)", shape: VIS_SHAPE, level: 5, color: EXIST_COLOR, link: "SMUk+FD_SMU03" },
  { id: 22, label: "SpcElecCV 1\nSMUk+FD_SMU03\n영상처리와 패턴인식", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SMUk+FD_SMU03" },
  { id: 23, label: "CoreElecAdv 4\nSNUk+SNU052_011k\n빅데이터와 인공지능의 응용", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SNUk+SNU052_011k" },
  { id: 24, label: "SpcElecGame 1\nSejonguniversityK+SJKMOOC04k\n게임인공지능", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SejonguniversityK+SJKMOOC04k" },
  { id: 25, label: "SpcElecNLP 2\n002_003_008\n음성 인식 및 실습\n(전남대학교)", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "002_003_008" },
];
var edges = [
  { from: 0, to: 1, color: { opacity: OP_HIGH } },

  { from: 0, to: 3, color: { opacity: OP_LOW } },
  { from: 1, to: 3, color: { opacity: OP_HIGH } },
  { from: 4, to: 3, color: { opacity: OP_LOW } },

  { from: 1, to: 4, color: { opacity: OP_MID } },

  { from: 0, to: 5, color: { opacity: OP_HIGH } },
  { from: 3, to: 5, color: { opacity: OP_HIGH } },

  { from: 1, to: 6, color: { opacity: OP_MID } },
  { from: 4, to: 6, color: { opacity: OP_LOW } },

  { from: 4, to: 7, color: { opacity: OP_MID } },

  { from: 6, to: 8, color: { opacity: OP_MID } },

  { from: 5, to: 9, color: { opacity: OP_HIGH } },
  { from: 1, to: 9, color: { opacity: OP_HIGH } },
  { from: 4, to: 9, color: { opacity: OP_HIGH } },

  { from: 0, to: 10, color: { opacity: OP_HIGH } },

  { from: 0, to: 11, color: { opacity: OP_MID } },
  { from: 1, to: 11, color: { opacity: OP_MID } },

  { from: 8, to: 13, color: { opacity: OP_MID } },
  { from: 9, to: 13, color: { opacity: OP_MID } },

  { from: 8, to: 14, color: { opacity: OP_MID } },
  { from: 0, to: 14, color: { opacity: OP_MID } },
  { from: 1, to: 14, color: { opacity: OP_MID } },
  { from: 23, to: 14, color: { opacity: OP_MID } },

  { from: 5, to: 15, color: { opacity: OP_HIGH } },
  { from: 3, to: 15, color: { opacity: OP_MID } },
  { from: 0, to: 15, color: { opacity: OP_MID } },
  { from: 1, to: 15, color: { opacity: OP_MID } },

  { from: 6, to: 16, color: { opacity: OP_MID } },
  { from: 0, to: 16, color: { opacity: OP_HIGH } },
  { from: 1, to: 16, color: { opacity: OP_MID } },
  { from: 7, to: 16, color: { opacity: OP_HIGH } },
  { from: 17, to: 16, color: { opacity: OP_HIGH } },

  { from: 10, to: 18, color: { opacity: OP_MID } },

  { from: 11, to: 19, color: { opacity: OP_MID } },

  { from: 1, to: 20, color: { opacity: OP_MID } },
  { from: 12, to: 20, color: { opacity: OP_MID } },

  { from: 8, to: 22, color: { opacity: OP_MID } },
  { from: 15, to: 22, color: { opacity: OP_MID } },

  { from: 5, to: 23, color: { opacity: OP_HIGH } },
  { from: 0, to: 23, color: { opacity: OP_MID } },
  { from: 1, to: 23, color: { opacity: OP_HIGH } },

  { from: 0, to: 24, color: { opacity: OP_MID } },

  { from: 1, to: 25, color: { opacity: OP_MID } },
];