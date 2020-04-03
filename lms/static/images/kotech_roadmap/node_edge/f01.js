var nodes = [
  { id: 0, label: "Introduction Programming for Everyone\n(프로그래밍 개론)\nPython 프로그래밍 기초 외 3건", shape: VIS_SHAPE, level: 0, color: MATCH_COLOR, link: [["Python 프로그래밍 기초(한국능률협회)", "http://www.dataedu.kr/course/1%ea%b3%bc%eb%aa%a9-python-%ed%94%84%eb%a1%9c%ea%b7%b8%eb%9e%98%eb%b0%8d-%ea%b8%b0%ec%b4%88/"], ['Python 프로그래밍 심화 (한국능률협회)', 'http://www.dataedu.kr/course-cat/매치업_딥러닝/'], ['머신러닝을 위한 파이썬 기초 (포항공과대학교)', 'https://iclass.postech.ac.kr/courses/5d6cdd4ec5728b2c694db285'], ['파이썬을 활용한 딥러닝 1 (코리아헤럴드)', 'http://www.abedu.co.kr/AI/?info_seq=4']] },
  { id: 1, label: "Introduction to CS and Programming\n(컴퓨터과학 개론 및 프로그래밍)\n파이썬 프로그래밍 외 1건", shape: VIS_SHAPE, level: 1, color: NORMAL_COLOR, link: [['파이썬 프로그래밍', 'HGUk+HGU02'], ['AI 기초프로그래밍(전남대학교)', 'https://sleonline.jnu.ac.kr/Course/Course100.aspx']] },
  { id: 2, label: "Understanding Artificial Intelligence\n(인공지능의 이해)\nICBM+AI개론(일부 유사 강좌)", shape: VIS_SHAPE, level: 2, color: NULL_COLOR, link: "KoreaUnivK+ku_eng_004" },
  { id: 3, label: "Introduction to Artificial Intelligence\n(인공지능 개론)\n인공지능의 기초", shape: VIS_SHAPE, level: 3, color: NORMAL_COLOR, link: "SNUk+SNU048_011k" },
];
var edges = [
  { from: 0, to: 1, color: { opacity: OP_MID } },
  { from: 1, to: 2, color: { opacity: OP_HIGH } },
  { from: 2, to: 3, color: { opacity: OP_HIGH } },
];
