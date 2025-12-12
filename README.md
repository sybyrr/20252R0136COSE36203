# COSE36203
Repository for COSE362 Final Report, ML Team6  
Assignment, Korea University  

It is recommended to run this in a Google Colab environment.

---

## 프로젝트 개요

본 저장소는 데이터 수집, 전처리 단계부터 모델 학습 단계까지의 전체 워크플로우를 포함하고 있습니다.  
채점 환경에 따라 다음 항목들을 확인 및 수정해주시면 감사하겠습니다.

- **DataPreprocessing.ipynb** 상단의 `drive mount` 설정  
- **ModelTraining.ipynb** 상단의 `drive mount` 설정  
- **ModelTraining.ipynb** 하단의 `!pip install optuna` 주석 처리 여부  

---

## 파일 구성

### 0. gathering/
KBO 공식 홈페이지로부터 데이터를 수집하고, 초기 전처리를 수행하는 .py 파일이 포함되어 있습니다. 수집 및 초기 전처리가 완료된 파일이 dataset/ 에 저장되어 있으나, 참고용으로 첨부하였습니다.

### 1. DataPreprocessing.ipynb
데이터셋을 기반으로 전처리를 수행하는 노트북입니다. 결측값 처리, 라벨 인코딩, 데이터 분할 등 모델 학습을 위한 사전 작업을 포함합니다.  

채점 환경이 Google Colab 환경이 아닐 경우, 상단의 `drive mount` 설정을 주석 처리해주시면 됩니다.

### 2. ModelTraining.ipynb
전처리된 데이터를 활용하여 실제 모델 학습을 수행하는 노트북입니다. Optuna를 사용한 하이퍼파라미터 최적화 기능이 포함되어 있습니다.  

채점 환경이 Google Colab 환경이 아닐 경우, 하단의 `!pip install optuna` 구문을 주석 처리해주시면 됩니다. Drive 연동 역시 환경에 맞게 조정 부탁드립니다.

### 3. dataset/
모델 학습에 사용된 전처리 전 데이터셋이 포함되어 있습니다.
실행 환경에 따라 상대 경로나 절대 경로를 적절히 설정하여 노트북에서 로딩할 수 있도록 구성되어 있습니다.  
dataset/processed/ 디렉토리에는 DataPreprocessing.ipynb를 통해 생성된 전처리 후 데이터가 저장되며, ModelTraining.ipynb는 이 전처리된 파일들을 불러와 학습을 수행합니다.

### 4. zips/
데이터셋의 원본 압축 파일이 저장된 디렉토리입니다. 코드와 직접 상호작용하지 않습니다.

### 5. environment.yml
Conda 환경 실행 시 필요한 패키지 및 버전 정보를 정의하는 파일입니다.  
채점 환경이 conda 기반이라면 이 파일을 활용해 동일한 환경을 재구성하실 수 있습니다.  
DataPreprocessing.ipynb과 ModelTraining.ipynb의 실행을 위한 환경이며, 기타 크롤링 코드 등의 실행을 지원하지 않습니다.

---

## 채점 환경 관련 안내

채점 시스템마다 파일 접근 방식, 외부 저장소(Google Drive 등) 사용 가능 여부, 패키지 설치 권한이 다를 수 있습니다.  
다음 항목들을 확인해주시면 감사하겠습니다.

1. **drive mount 코드 활성화 또는 비활성화**
2. **경로(Path) 설정이 환경에 맞는지 확인**
3. **`!pip install optuna` 구문 주석 처리 여부**
4. **데이터셋 및 zip 파일 경로 확인**

---

## 실행 순서

1. `DataPreprocessing.ipynb` 실행 → 전처리 결과 생성  
2. `ModelTraining.ipynb` 실행 → 모델 학습 및 평가 수행

---
