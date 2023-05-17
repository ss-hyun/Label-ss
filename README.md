# Label-ss
한국 공공 데이터 셋(AI-hub 등)에는 라벨의 Meta Data 및 라벨 정보들이 제대로 기재되어 있지 않다.  
때문에 AI 모델 학습 용도 및 라벨링 툴(lebelme 등) 사용 용도로 데이터를 변환할 때 다양한 오류(*, 듣도 보도 못한)를 마주한다.  
이런 문제를 보다 쉽게 해결하기 위해 간단한 백본 코드를 만들었다.  
Meta Data and label information of labels are not properly described in Korean public data sets (AI-hub, etc.).  
Therefore, we face various errors when converting data to AI model learning applications and labeling tools (such as lebelme).  
So, I create a simple backbone code to solve these problems more easily.  


문제점과 개선사항이 보인다면 의견 전달 부탁드립니다.  
If you see any problems and improvements, please let me know your opinion.


### (*) 데이터 변환 시 마주치는 다양한 오류 예시

#### [[AI-Hub] 교통문제 해결을 위한 CCTV 교통 영상(고속도로)](https://aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=realm&dataSetSn=164)
* 데이터 설명서 및 라벨 내부 이미지 이름에는 이미지 포맷이 png라고 적혀있지만, jpg 포맷을 가지는 데이터가 존재한다.
* 메타 데이터 라벨 내부의 이름은 라벨 파일 이름과 같아야한다. 하지만 두 값이 다른 메타 라벨이 존재한다.
* 메타 데이터에는 해당 라벨이 정보를 가진 이미지들의 개수가 기록되어있다. 하지만 실제 이미지의 정보 개수와 일치하지 않는다.
* 메타 라벨 파일에 포함된 각 이미지는 그에 대응하는 이미지 파일 폴더에 반드시 존재해야 한다. 하지만 존재하지 않는 이미지도 있다.(?)


