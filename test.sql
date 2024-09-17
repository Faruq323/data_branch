Test case 1)
Select count(*) from target table 
where trans_dt='2024-09-17'-- check count for different dates

Select count(*) target_view 
where trans_dt='2024-09-17'-- check count for different dates

Test case2)
select * from target_view
where trans_dt is not null ---check hw many rows data its having and time taken for running and note it down in excel sheet

Test case3)
select metric_value,fqdn from target table
where transdt='------' and metric_name='-----' and fqdn ='-----' 
group by metric_value,fqdn,trans_dt

select metric_value,fqdn from target_view
where transdt='------' and metric_name='-----' and fqdn ='-----' 
group by metric_value,fqdn,trans_dt  ---compare both the query output for discrepancies
