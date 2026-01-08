# Instacart 데이터 분석 계획

이 문서는 Instacart 데이터셋의 탐색적 데이터 분석(EDA)을 위한 계획을 정의합니다.

## 1. 분석 목표
- Instacart 고객의 주문 패턴을 이해하고, 서비스 개선을 위한 인사이트를 도출합니다.
- 주요 분석 질문:
    - 고객들은 주로 언제 주문하는가? (시간, 요일)
    - 어떤 상품이 가장 인기가 많은가?
    - 재주문율이 높은 상품은 무엇인가?
    - 고객들은 한번에 몇 개의 상품을 주문하는가?

## 2. 데이터셋
- `aisles.csv`: 상품 카테고리 정보
- `departments.csv`: 상품 부서 정보
- `order_products__prior.csv`: 이전 주문 내역
- `order_products__train.csv`: 훈련 데이터 주문 내역
- `orders.csv`: 주문 정보
- `products.csv`: 상품 정보

## 3. 분석 절차
1.  **데이터 로드 및 병합**: 모든 CSV 파일을 Pandas DataFrame으로 로드하고, `order_id`, `product_id` 등을 기준으로 병합하여 분석에 용이한 단일 데이터셋을 생성합니다.
2.  **주문 시간 분석**:
    - `orders` 데이터의 `order_hour_of_day`, `order_dow`를 사용하여 시간대별, 요일별 주문량 분포를 시각화합니다.
3.  **상품 분석**:
    - `order_products__*` 데이터를 분석하여 가장 많이 팔린 상품 TOP 20을 집계합니다.
    - 재주문(`reordered` == 1)이 가장 많이 된 상품 TOP 20을 집계합니다.
4.  **주문 규모 분석**:
    - `orders`와 `order_products__*`를 조인하여 주문당 상품 개수 분포를 분석합니다.

## 4. 기대 결과
- 분석 결과를 시각화(막대 그래프, 라인 그래프 등)하여 `instacart/EDA_Report.md` 파일에 정리하고, 각 분석에 대한 해석을 추가합니다.
- 생성된 그래프는 `instacart/images/` 디렉토리에 저장합니다.
