SELECT *
FROM
dn_fact_aggr_prd_usage
WHERE day_id = TRUNC(SYSDATE) - 1



SELECT /*+ PARALLEL(4) */ 
  TRUNC(fact.end_date) AS day_id,
  f.fleet_id AS category_id,
  COALESCE(SUM(fact.income_netto), 0) AS income_netto,
  COALESCE(SUM(fact.net_amount_eur), 0) AS income_netto_eur,
  COALESCE(SUM(fact.is_drive), 0) AS drives
FROM dn_fact_prd_usage_details_v2 fact
INNER JOIN dn_dim_fleet_view f ON fact.return_city = f.city_id
WHERE
    1 = 1
    -- from drivelineitem logic
    AND fact.fact_type = 'CHARGE'
    -- by date
    AND fact.end_date BETWEEN ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -24) AND TRUNC(SYSDATE, 'MM') - INTERVAL '1' SECOND
    AND fact.booking_date >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -24)
  GROUP BY  
    TRUNC(fact.end_date),
    f.fleet_id
