# KPI Tree 상세 설계: Total Payment Value 최적화를 위한 지표 분석

## 1. KPI Hierarchy Decomposition Summary

이 KPI Tree는 최상위 지표인 **총 결제 금액 (Total Payment Value)**을 중심으로, 비즈니스 성과를 구성하는 핵심 하위 지표들이 어떻게 상호작용하는지 수학적 관계로 표현합니다. 각 지표는 [Input Metric] 또는 [Output Metric]으로 분류되어, 어떤 지표가 최종 결과에 영향을 미치는지 직관적으로 파악할 수 있도록 돕습니다.

-   **L0: 총 결제 금액 (Total Payment Value)** $[Output Metric]$
    -   $L0 = L1_{총 주문 건수} \times L1_{평균 주문 금액}$

-   **L1: 총 주문 건수 (Total Orders)** $[Input Metric]$
    -   $L1_{총 주문 건수} = L2_{신규 고객 주문 건수} + L2_{재구매 고객 주문 건수}$

-   **L1: 평균 주문 금액 (Average Order Value, AOV)** $[Output Metric]$
    -   $L1_{평균 주문 금액} = L2_{평균 상품 가격} + L2_{평균 배송비} - L2_{평균 할인 금액}$ (할인 금액이 데이터에 명시적으로 있다면)

-   **L2: 신규 고객 주문 건수 (New Customer Orders)** $[Input Metric]$

-   **L2: 재구매 고객 주문 건수 (Repeat Customer Orders)** $[Input Metric]$
    -   $L2_{재구매 고객 주문 건수} = L3_{총 고객 수} \times L3_{재구매율}$

-   **L2: 평균 상품 가격 (Average Product Price)** $[Input Metric]$

-   **L2: 평균 배송비 (Average Freight Value)** $[Input Metric]$

-   **L2: 평균 할인 금액 (Average Discount Value)** $[Input Metric]$ (데이터에 따라)

## 2. Detailed Metric Tree & Definition

### # L0: 총 결제 금액 (Total Payment Value) [Output Metric]
-   **정의**: 일정 기간 동안 모든 고객이 결제한 총 금액. 이커머스 비즈니스의 최종적인 재무 성과를 나타내는 최상위 지표.
-   **산출 로직**: SUM(payment_value)
-   **유형**: Output
-   **디테일**:
    -   ## L1: 총 주문 건수 (Total Orders) [Input Metric]
        -   **정의**: 일정 기간 동안 발생한 전체 주문의 수. 비즈니스의 활동량과 고객 유입 규모를 나타냄.
        -   **산출 로직**: COUNT(DISTINCT order_id)
        -   **유형**: Input
        -   **디테일**:
            -   ### L2: 신규 고객 주문 건수 (New Customer Orders) [Input Metric]
                -   **정의**: 해당 기간에 처음으로 주문을 발생시킨 고객들의 총 주문 건수. 고객 획득 채널의 효율성을 평가.
                -   **산출 로직**: COUNT(DISTINCT order_id) WHERE customer_unique_id NOT IN (과거 주문 이력)
                -   **유형**: Input
                -   **디테일**:
                    -   #### L3: 신규 고객 수 (New Customers) [Input Metric]
                        -   **정의**: 해당 기간 동안 서비스를 처음 이용한 고객의 수.
                        -   **산출 로직**: COUNT(DISTINCT customer_unique_id) WHERE customer_unique_id NOT IN (과거 주문 이력)
                        -   **유형**: Input
                    -   #### L3: 신규 고객 전환율 (New Customer Conversion Rate) [Output Metric]
                        -   **정의**: 신규 방문자 중 실제 주문으로 이어진 비율.
                        -   **산출 로직**: (신규 고객 수 / 총 신규 방문자 수) x 100 (총 신규 방문자 수는 외부 데이터 필요)
                        -   **유형**: Output
            -   ### L2: 재구매 고객 주문 건수 (Repeat Customer Orders) [Input Metric]
                -   **정의**: 해당 기간에 2회 이상 주문을 발생시킨 고객들의 총 주문 건수. 고객 유지 전략의 성공 여부를 나타냄.
                -   **산출 로직**: COUNT(DISTINCT order_id) WHERE customer_unique_id IN (과거 주문 이력)
                -   **유형**: Input
                -   **디테일**:
                    -   #### L3: 재구매 고객 수 (Repeat Customers) [Input Metric]
                        -   **정의**: 해당 기간에 2회 이상 서비스를 이용한 고객의 수.
                        -   **산출 로직**: COUNT(DISTINCT customer_unique_id) WHERE customer_unique_id IN (과거 주문 이력)
                        -   **유형**: Input
                    -   #### L3: 재구매율 (Repeat Purchase Rate) [Output Metric]
                        -   **정의**: 특정 기간 동안 재구매한 고객의 비율.
                        -   **산출 로직**: (재구매 고객 수 / 총 고객 수) x 100
                        -   **유형**: Output
                        -   **디테일**:
                            -   ##### L4: 총 고객 수 (Total Customers) [Input Metric]
                                -   **정의**: 일정 기간 동안 서비스를 이용한 전체 고객의 수.
                                -   **산출 로직**: COUNT(DISTINCT customer_unique_id)
                                -   **유형**: Input

    -   ## L1: 평균 주문 금액 (Average Order Value, AOV) [Output Metric]
        -   **정의**: 단일 주문당 평균적으로 결제되는 금액. 고객의 구매력을 나타냄.
        -   **산출 로직**: SUM(payment_value) / COUNT(DISTINCT order_id)
        -   **유형**: Output
        -   **디테일**:
            -   ### L2: 평균 상품 가격 (Average Product Price) [Input Metric]
                -   **정의**: 판매된 상품 하나의 평균 가격.
                -   **산출 로직**: SUM(price) / COUNT(order_item_id)
                -   **유형**: Input
                -   **디테일**:
                    -   #### L3: 상품별 평균 가격 (Average Price per Product) [Input Metric]
                        -   **정의**: 개별 상품의 평균 판매 가격.
                        -   **산출 로직**: SUM(price) / COUNT(product_id)
                        -   **유형**: Input
                    -   #### L3: 상품 카테고리별 평균 가격 (Average Price per Product Category) [Input Metric]
                        -   **정의**: 특정 상품 카테고리에 속하는 상품들의 평균 가격.
                        -   **산출 로직**: SUM(price) WHERE product_category_name_english = [Category Name] / COUNT(product_id) WHERE product_category_name_english = [Category Name]
                        -   **유형**: Input
            -   ### L2: 평균 배송비 (Average Freight Value) [Input Metric]
                -   **정의**: 주문당 평균 배송료.
                -   **산출 로직**: SUM(freight_value) / COUNT(DISTINCT order_id)
                -   **유형**: Input
                -   **디테일**:
                    -   #### L3: 배송 거리별 평균 배송비 (Average Freight Value per Distance) [Input Metric]
                        -   **정의**: 배송 거리에 따른 평균 배송비 (거리 정보는 `olist_geolocation_dataset` 필요)
                        -   **산출 로직**: SUM(freight_value) / COUNT(DISTINCT order_id) (단, 배송 거리 정보 필요)
                        -   **유형**: Input
            -   ### L2: 평균 할인 금액 (Average Discount Value) [Input Metric]
                -   **정의**: 주문당 평균 할인 금액.
                -   **산출 로직**: (데이터에 할인 금액이 명시적으로 존재한다면) SUM(discount_value) / COUNT(DISTINCT order_id)
                -   **유형**: Input
                -   **디테일**:
                    -   #### L3: 할인율 (Discount Rate) [Input Metric]
                        -   **정의**: 총 판매액 대비 할인 금액의 비율.
                        -   **산출 로직**: (SUM(discount_value) / SUM(price)) x 100
                        -   **유형**: Input

## 3. Data Implementation Strategy

`olist_merged_dataset_deduped.csv` 데이터를 활용하여 위에서 정의된 복합 지표들을 구현하기 위한 전략은 다음과 같습니다.

1.  **신규/재구매 고객 분류**:
    -   `customer_unique_id`와 `order_purchase_timestamp` 컬럼을 활용합니다.
    -   각 `customer_unique_id`별로 `order_purchase_timestamp`의 최소값을 찾아 고객의 첫 구매 시점을 정의합니다.
    -   특정 분석 기간(예: 월별, 분기별) 내의 모든 `order_purchase_timestamp`를 기준으로, 해당 기간 내 첫 구매가 발생한 `customer_unique_id`를 '신규 고객'으로 분류합니다.
    -   반대로, 분석 기간 이전에 이미 `order_purchase_timestamp`가 존재했던 `customer_unique_id`는 '재구매 고객'으로 분류합니다.
    -   이 로직을 통해 `신규 고객 주문 건수`와 `재구매 고객 주문 건수`, `재구매 고객 수`를 산출할 수 있습니다. `총 고객 수`는 `customer_unique_id`의 고유값 개수로 쉽게 산출됩니다.

2.  **배송 효율 지표**:
    -   `order_purchase_timestamp`, `order_delivered_customer_date`, `order_estimated_delivery_date` 컬럼을 활용합니다.
    -   **평균 배송 시간**: `order_delivered_customer_date` - `order_purchase_timestamp`를 계산하여 각 주문의 실제 배송 시간을 산출하고, 이들의 평균을 구합니다.
    -   **배송 지연율**: `order_delivered_customer_date`가 `order_estimated_delivery_date`보다 늦은 경우를 '지연'으로 판단하여, 전체 배송 완료 건수 대비 지연된 주문 건수의 비율을 계산합니다.
    -   **배송 완료율**: `order_status`가 'delivered'인 주문 건수를 전체 주문 건수로 나누어 산출합니다.

3.  **상품별/카테고리별 지표**:
    -   `product_id`, `product_category_name_english`, `price`, `order_item_id` 컬럼을 활용합니다.
    -   `product_id`를 기준으로 `price`의 평균을 내어 `상품별 평균 가격`을 산출할 수 있습니다.
    -   `product_category_name_english`를 기준으로 그룹화하여 `price`의 평균을 내면 `상품 카테고리별 평균 가격`을 얻을 수 있습니다.
    -   `SUM(price) / COUNT(order_item_id)`는 `merged_df`에서 `order_item_id`가 각 상품 라인 아이템을 나타내므로, `평균 상품 가격`으로 해석할 수 있습니다.

4.  **할인 금액**:
    -   현재 `olist_merged_dataset_deduped.csv` 데이터에는 `discount_value`와 같은 명시적인 할인 금액 컬럼이 보이지 않습니다. 만약 할인 금액을 반영해야 한다면, 주문별 `payment_value`와 `price` 및 `freight_value`의 합계를 비교하여 차액을 할인 금액으로 간주하거나, 별도의 할인 관련 데이터셋(`olist_order_payments_dataset.csv` 등)에서 바우처 사용 내역을 자세히 분석해야 합니다. 현재 데이터셋만으로는 직접적인 `평균 할인 금액` 산출이 어렵습니다. (요구사항 명시)

이러한 전략을 통해 `payment_value_sum`을 중심으로 한 KPI Tree의 모든 지표를 `olist_merged_dataset_deduped.csv` 데이터를 기반으로 구현할 수 있습니다. 각 지표는 비즈니스 의사결정에 중요한 통찰을 제공할 것입니다.
