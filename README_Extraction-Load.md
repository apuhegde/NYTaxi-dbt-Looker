# Upload data to GCS using Airflow (CeleryExecutor) run via Docker

This project is part of a data pipeline that I've built to download NYC Taxi and Limousine Commission data from their website, upload it to a data lake (GCS), transform the data using dbt, store it in a data warehouse (BigQuery) and analyze it (using Looker Studio).

This repo contains the first portion of the pipeline (how to run Airflow in a Docker container to upload data to GCS). 
The second part of the pipeline (transformation and analysis) can be found here: [https://github.com/apuhegde/NYTaxi-dbt-Looker](https://github.com/apuhegde/NYTaxi-dbt-Looker). 

A lot of the original code has been used from the Data Engineering Zoomcamp course on GitHub [https://github.com/DataTalksClub/data-engineering-zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) and Alvaro Navas Peire's notes [https://github.com/ziritrion/dataeng-zoomcamp](https://github.com/ziritrion/dataeng-zoomcamp).
