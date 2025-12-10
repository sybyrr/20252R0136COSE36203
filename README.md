# COSE36203
Repository for COSE362 Final Report, ML Team6  
Assignment, Korae University  



It is recommended to run this in a Google Colab environment.


# 프로젝트 설명 / Project Overview

본 저장소는 데이터 전처리 단계부터 모델 학습 단계까지의 전체 워크플로우를 포함하고 있습니다.  
채점 환경에 따라 다음 항목들을 적절히 수정해야 합니다.

- **DataPreprocessing.ipynb** 상단의 `drive mount` 설정  
- **ModelTraining.ipynb** 상단의 `drive mount` 설정  
- **ModelTraining.ipynb** 하단의 `!pip install optuna` 주석 처리 여부  

This repository contains the complete workflow from data preprocessing to model training.  
Depending on the evaluation environment, you must appropriately modify the following:

- `drive mount` configuration at the top of **DataPreprocessing.ipynb**  
- `drive mount` configuration at the top of **ModelTraining.ipynb**  
- Whether to comment out `!pip install optuna` at the bottom of **ModelTraining.ipynb**

---

## 구성 요소 / Repository Structure

### 1. DataPreprocessing.ipynb
**KR:**  
데이터셋을 기반으로 전처리를 수행하는 노트북입니다. 결측값 처리, 라벨 인코딩, 데이터 분할 등 모델 학습을 위한 사전 작업을 포함합니다.  
채점 환경에 따라 Google Drive 연동이 불가능할 수 있으므로, 상단의 `drive mount` 설정을 필요에 따라 활성화하거나 주석 처리하십시오.

**EN:**  
This notebook performs data preprocessing based on the provided dataset. It includes tasks such as handling missing values, label encoding, and dataset splitting.  
Since Google Drive access may not be available in some evaluation environments, enable or disable the `drive mount` section at the top as appropriate.

---

### 2. ModelTraining.ipynb
**KR:**  
전처리된 데이터를 활용하여 실제 모델 학습을 수행하는 노트북입니다. Optuna를 사용한 하이퍼파라미터 최적화 기능이 포함되어 있습니다.  
채점 환경에서 패키지 설치가 제한될 수 있으므로, 하단의 `!pip install optuna` 구문은 필요에 따라 주석 처리해야 합니다. Drive 연동 역시 환경에 맞게 수정하십시오.

**EN:**  
This notebook trains the actual model using the preprocessed data. It includes hyperparameter optimization via Optuna.  
Because some evaluation environments restrict package installation, comment out the `!pip install optuna` line when necessary. Also adjust the drive-mount settings according to the environment.

---

### 3. dataset/
**KR:**  
모델 학습에 사용된 전처리 전 데이터셋이 포함되어 있습니다.  
실행 환경에 따라 상대 경로나 절대 경로를 적절히 설정하여 노트북에서 로딩할 수 있도록 해야 합니다.

**EN:**  
Contains the raw dataset used for model training.  
Ensure appropriate path configuration (relative or absolute) so the notebooks can load the dataset correctly in the given execution environment.

---

### 4. zips/
**KR:**  
데이터셋의 원본 압축 파일이 저장된 디렉토리입니다. 필요 시 전처리 단계에서 활용되며, 채점 환경에서는 해당 경로를 직접 사용하는 경우도 있습니다.

**EN:**  
Directory containing the original compressed data files. These may be used during preprocessing and might be required directly depending on the evaluation environment.

---

### 5. environment.yml
**KR:**  
Conda 환경 실행 시 필요한 패키지 및 버전 정보를 정의하는 파일입니다.  
채점 환경이 conda 기반이라면 이 파일을 활용해 동일한 환경을 재구성할 수 있습니다.

**EN:**  
Defines the packages and version requirements for running the project in a conda environment.  
Use this file to reproduce the environment in conda-based evaluation systems.

---

## 채점 환경에 따른 설정 안내 / Notes for Evaluation Environment

### KR
채점 시스템마다 제공되는 파일 접근 방식, 외부 저장소(Google Drive 등) 사용 가능 여부, 패키지 설치 권한이 다를 수 있습니다.  
따라서 다음 항목들을 반드시 확인 후 실행 환경에 맞게 수정하십시오.

1. **drive mount 코드 활성화 또는 비활성화**
2. **경로(Path) 설정이 로컬 환경에 맞는지 확인**
3. **`!pip install optuna` 구문 주석 처리 여부 결정**
4. **데이터셋 및 zip 파일 경로가 올바르게 설정되었는지 확인**

### EN
Different evaluation systems may vary in their support for file access, external storage (e.g., Google Drive), or package installation permissions.  
Review and modify the following items before running the notebooks:

1. Enable or disable the **drive mount code** as needed  
2. Ensure **path configurations** align with the local environment  
3. Decide whether to **comment out** the `!pip install optuna` line  
4. Confirm the dataset and zip file paths are correctly set

---

## 실행 순서 / Execution Order

**KR:**  
1. `DataPreprocessing.ipynb` 실행 → 전처리 결과 생성  
2. `ModelTraining.ipynb` 실행 → 모델 학습 및 평가 수행

**EN:**  
1. Run `DataPreprocessing.ipynb` → Generate preprocessed data  
2. Run `ModelTraining.ipynb` → Train and evaluate the model

---
