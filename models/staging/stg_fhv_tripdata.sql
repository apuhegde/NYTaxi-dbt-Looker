{{ config(materialized='view') }}
 
with tripdata as 
(
  select *,
    row_number() over(partition by dispatching_base_num, pickup_datetime, dropOff_datetime) as rn
  from {{ source('staging','fhv_tripdata_2019') }}
  where pickup_datetime is not null and dropOff_datetime is not null 
)
select
    -- identifiers
    {{ dbt_utils.surrogate_key(['dispatching_base_num', 'pickup_datetime','dropOff_datetime']) }} as tripid,
    cast(dispatching_base_num as string) as dispatching_base_num,
    cast(PUlocationID as integer) as  pickup_locationid,
    cast(DOlocationID as integer) as dropoff_locationid,
    
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropOff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    cast(SR_Flag as integer) as sr_flag,
    cast(Affiliated_base_number as string) as affiliated_base_number,
from tripdata
where rn = 1

-- dbt build --m <model.sql> --var 'is_test_run: false'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}