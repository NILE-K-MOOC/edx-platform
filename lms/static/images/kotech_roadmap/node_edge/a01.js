var nodes = [
  { id: 0, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
  { id: 1, label: "Introduction to Machine Learning\n(기계학습 개론)\n머신러닝 외 5건", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: [['머신러닝', 'SNUk+SNU050_011k'], ['Machine Learning for Data Science', 'KoreaUnivK+ku_eng_003'], ['자율주행을 위한 머신러닝', 'SKKUk+SKKU_30'], ['지도학습:회귀(Match業 강좌)', 'https://iclass.postech.ac.kr/courses/5d6db0eec5728b505b13d593'], ['지도학습:분류(Match業 강좌)', 'https://iclass.postech.ac.kr/courses/5d6db194c5728b50b04d5fb3'], ['비지도학습:군집화와 차원축소(Match業 강좌)', 'https://iclass.postech.ac.kr/courses/5d6db210c5728b5081032723']] },
  { id: 2, label: "CoreElecAI 3\nCKUk+CORE_CKU03\n인격과 로봇\n 외 1건", shape: VIS_SHAPE, level: 0, color: NORMAL_COLOR, link: [['인격과 로봇', 'CKUk+CORE_CKU03k'], ['포스트휴먼 인문학', 'EwhaK+CORE_EW17002C']] },

  { id: 3, label: "Introduction to Deep Learning\n(딥러닝 개론)\n딥러닝 개론", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: "DGUk+DGU_006k+DGU_006k" },
  { id: 4, label: "Advanced Machine Learning\n(고급 기계학습)\n개발예정강좌", shape: VIS_SHAPE, level: 1, color: NULL_COLOR, link: "" },

  { id: 5, label: "Deep Learning Application and Practice\n(딥러닝 응용 및 실습)\n파이썬으로 배우는 기계학습 입문 외 1건", shape: VIS_SHAPE, level: 2, color: NORMAL_COLOR, link: [['파이썬으로 배우는 기계학습 입문', 'HGUk+HGU05'], ['딥러닝개론 및 응용', '']] },
  { id: 6, label: "Topics in Artificial Intelligence\n(인공지능 연구)\n개발예정강좌", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },
  { id: 7, label: "Topics in Machine Learning\n(기계학습 연구)\n개발예정강좌", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "" },

  { id: 8, label: "Introduction to Robotics\n(로봇공학 개론)\nFun-MOOC - 기계는 영원하다!", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SNUk+SKP.M2794.000100k" },
  { id: 9, label: "Reinforcement Learning\n(강화학습) 개발예정강좌", shape: VIS_SHAPE, level: 3, color: NULL_COLOR, link: "" },
  { id: 10, label: "Knowledge-Based AI(지식기반 인공지능)\n추론응용 모델링 (Match業 강좌)\n", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "http://www.abedu.co.kr/AI/lecture/ps/7/is/16" },
  { id: 11, label: "Economics and Computation\n(계량경제학)\n계량경제학", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "JEJUk+KOCW_JEJU01" },
  { id: 12, label: "Introduction to Cognitive\nScience(인지과학 개론)\n인간 뇌의 이해", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SNUk+SNU047_019k" },

  { id: 13, label: "Biomedical Computing\n(생의학 컴퓨팅)\n바이오메디컬비전 및 응용 외 2건", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: [['바이오메디컬비전 및 응용', 'SoongsilUnivK+soongsilmooc03K'], ['생명정보개론', 'SoongsilUnivK+soongsilmooc01K'], ['의공학-생명과 공학의 만남', 'POSTECHk+CITE241']] },
  { id: 14, label: "Artificial Intelligence for Robotics\n(로봇공학을 위한 인공지능)\nMobile Robot Perception and Navigation", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "SEOULTECHk+SMOOC04k" },
  { id: 15, label: "Computer Vision\n(컴퓨터비전)\n딥러닝 영상분석(Match業 강좌) 외 1건", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: [['딥러닝 영상분석(Match業 강좌)', 'http://www.abedu.co.kr/AI_MF/lecture/ps/4/is/6'], ['영상처리와 패턴인식', 'SMUk+FD_SMU03']] },
  { id: 16, label: "Natural Language Processing\n(자연어처리)\n텍스트 마이닝 실전 및 분석 외 1건", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: [['텍스트 마이닝 실전 및 분석', 'YSUk+FD_YSU_LIS01k'], ['빅데이터와 텍스트마이닝', 'SejonguniversityK+SJMOOC10K']] },
  { id: 17, label: "Linguistics(언어학)\n언어와 인간", shape: VIS_SHAPE, level: 4, color: NORMAL_COLOR, link: "SNUk+CORE_SNU041_040k" },
  { id: 18, label: "Probabilistic Graphical Models\n(확률적 그래픽 모델)\n개발예정강좌", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 19, label: "Artificial Intelligence for Business\n(비즈니스를 위한 인공지능)\n개발예정강좌", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },
  { id: 20, label: "Computational Cognitive Science\n(전산 인지과학)\n개발예정강좌", shape: VIS_SHAPE, level: 4, color: NULL_COLOR, link: "" },

  { id: 21, label: "Computer Graphics\n(컴퓨터그래픽)\n영상처리와 패턴인식\n", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SMUk+FD_SMU03" },
  { id: 22, label: "Computer Graphics\n(컴퓨터그래픽)\n영상처리와 패턴인식", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SMUk+FD_SMU03" },
  { id: 23, label: "Applied Artificial Intelligence\n(인공지능 응용)\n빅데이터와 인공지능의 응용", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SNUk+SNU052_011k" },
  { id: 24, label: "Game AI(게임인공지능)\n게임인공지능", shape: VIS_SHAPE, level: 5, color: NORMAL_COLOR, link: "SejonguniversityK+SJKMOOC04k" },
  { id: 25, label: "Speech Recognition(음성 인식)\n개발예정강좌", shape: VIS_SHAPE, level: 5, color: NULL_COLOR, link: "" },
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