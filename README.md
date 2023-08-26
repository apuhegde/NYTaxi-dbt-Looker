# Analysis of NYC Taxi and Limousine Commission's For-Hire-Vehicle trips

This is an ELT pipeline I built to download NYC Taxi and Limousine Commission data from their website ([NYC TLC raw data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)), upload it to a data lake (GCS), transform the data using dbt, store it in a data warehouse (BigQuery) and analyze it (using Looker Studio).

The major portion of this project has been done under the guidance of the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) course on GitHub and Alvaro Navas Peire's [notes](https://github.com/ziritrion/dataeng-zoomcamp).

