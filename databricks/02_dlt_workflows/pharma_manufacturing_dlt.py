"""
Delta Live Tables Pipeline for Pharmaceutical Manufacturing
Bronze → Silver → Gold medallion architecture
"""
# Databricks notebook source
# MAGIC %md
# MAGIC # Pharmaceutical Manufacturing DLT Pipeline
# MAGIC
# MAGIC **Architecture**: Bronze → Silver → Gold
# MAGIC
# MAGIC - **Bronze**: Raw sensor data, batch records, equipment logs
# MAGIC - **Silver**: Cleaned, validated, deduplicated data
# MAGIC - **Gold**: Business-ready aggregations and analytics
# MAGIC
# MAGIC **Data Sources**:
# MAGIC - Bioreactor sensors (Zerobus/Kafka streams)
# MAGIC - LIMS (Laboratory Information Management System)
# MAGIC - MES (Manufacturing Execution System)
# MAGIC - Equipment monitoring systems

# COMMAND ----------

import dlt
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze Layer - Raw Data Ingestion

# COMMAND ----------

@dlt.table(
    comment="Raw bioreactor sensor data from IoT devices",
    table_properties={"quality": "bronze", "pipelines.autoOptimize.managed": "true"}
)
def bronze_bioreactor_sensors():
    """
    Ingest raw sensor data from bioreactors
    In production, this would read from Kafka/Zerobus
    """
    # Synthetic stream for demo
    # In production: spark.readStream.format("kafka").option("topic", "bioreactor_sensors").load()

    return (
        spark.readStream
            .format("rate")
            .option("rowsPerSecond", 100)
            .load()
            .select(
                col("timestamp").alias("sensor_timestamp"),
                lit("BR-01").alias("bioreactor_id"),
                (37.0 + (rand() - 0.5) * 0.2).alias("temperature"),
                (7.0 + (rand() - 0.5) * 0.1).alias("ph"),
                (45.0 + (rand() - 0.5) * 10).alias("dissolved_oxygen"),
                (120 + (rand() * 10).cast("int")).alias("agitation_rpm"),
                (1.2 + (rand() - 0.5) * 0.04).alias("pressure"),
                (3.5 + rand() * 1.5).alias("cell_density"),
                ((8.5e6 + rand() * 2e6).cast("long")).alias("viable_cell_count")
            )
    )


@dlt.table(
    comment="Raw batch manufacturing records",
    table_properties={"quality": "bronze"}
)
def bronze_batch_records():
    """
    Batch records from MES system
    """
    # In production: read from MES database or file drop
    schema = StructType([
        StructField("batch_id", StringType(), False),
        StructField("product", StringType(), False),
        StructField("start_date", TimestampType(), False),
        StructField("bioreactor_id", StringType(), False),
        StructField("status", StringType(), False),
        StructField("ingestion_timestamp", TimestampType(), False)
    ])

    # Simulated data
    return spark.createDataFrame([
        ("B2024-001", "mAb-A", datetime(2024, 12, 1), "BR-01", "In Progress", datetime.now()),
        ("B2024-002", "Vaccine-X", datetime(2024, 11, 15), "BR-02", "Released", datetime.now()),
    ], schema)


@dlt.table(
    comment="Raw equipment sensor data",
    table_properties={"quality": "bronze"}
)
def bronze_equipment_sensors():
    """
    Equipment health monitoring data
    """
    return (
        spark.readStream
            .format("rate")
            .option("rowsPerSecond", 20)
            .load()
            .select(
                col("timestamp").alias("sensor_timestamp"),
                lit("BR-01").alias("equipment_id"),
                lit("Bioreactor").alias("equipment_type"),
                (rand() * 1000).alias("runtime_hours"),
                (rand() * 5).alias("vibration_level"),
                (25 + rand() * 10).alias("equipment_temperature")
            )
    )


# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Layer - Cleaned & Validated Data

# COMMAND ----------

@dlt.table(
    comment="Validated bioreactor sensor data with quality checks",
    table_properties={"quality": "silver", "pipelines.autoOptimize.managed": "true"}
)
@dlt.expect_or_drop("valid_temperature", "temperature BETWEEN 30 AND 42")
@dlt.expect_or_drop("valid_ph", "ph BETWEEN 5 AND 9")
@dlt.expect_or_drop("valid_do", "dissolved_oxygen BETWEEN 0 AND 100")
def silver_bioreactor_sensors():
    """
    Cleaned bioreactor data with data quality checks
    Drops invalid sensor readings
    """
    return (
        dlt.read_stream("bronze_bioreactor_sensors")
            .withColumn("validation_timestamp", current_timestamp())
            .withColumn("within_spec_temp",
                       when((col("temperature") >= 36.9) & (col("temperature") <= 37.1), True).otherwise(False))
            .withColumn("within_spec_ph",
                       when((col("ph") >= 6.95) & (col("ph") <= 7.05), True).otherwise(False))
            .withColumn("within_spec_do",
                       when((col("dissolved_oxygen") >= 40) & (col("dissolved_oxygen") <= 50), True).otherwise(False))
            .withColumn("all_specs_met",
                       col("within_spec_temp") & col("within_spec_ph") & col("within_spec_do"))
    )


@dlt.table(
    comment="Bioreactor digital twin with real-time process state",
    table_properties={"quality": "silver"}
)
def silver_bioreactor_digital_twin():
    """
    Complete digital twin model combining sensors, batch info, and predictions
    """
    sensors = dlt.read_stream("silver_bioreactor_sensors")
    batches = dlt.read("bronze_batch_records")

    return (
        sensors
            .join(batches, sensors.bioreactor_id == batches.bioreactor_id, "left")
            .select(
                sensors["*"],
                batches["batch_id"],
                batches["product"],
                batches["status"].alias("batch_status")
            )
            .withColumn("health_score",
                       when(col("all_specs_met"), 95.0 + rand() * 5).otherwise(70.0 + rand() * 10))
    )


@dlt.table(
    comment="Equipment health metrics",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_vibration", "vibration_level < 10")
def silver_equipment_health():
    """
    Validated equipment sensor data
    """
    return (
        dlt.read_stream("bronze_equipment_sensors")
            .withColumn("health_score",
                       100 - (col("vibration_level") * 10) - (col("runtime_hours") / 500))
            .withColumn("status",
                       when(col("health_score") >= 85, "Operational")
                       .when(col("health_score") >= 70, "Warning")
                       .otherwise("Critical"))
    )


# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer - Business Analytics

# COMMAND ----------

@dlt.table(
    comment="Hourly bioreactor performance aggregations",
    table_properties={"quality": "gold"}
)
def gold_bioreactor_hourly_metrics():
    """
    Hourly aggregations for dashboard and reporting
    """
    return (
        dlt.read_stream("silver_bioreactor_sensors")
            .withWatermark("sensor_timestamp", "1 hour")
            .groupBy(
                window("sensor_timestamp", "1 hour"),
                "bioreactor_id"
            )
            .agg(
                avg("temperature").alias("avg_temperature"),
                stddev("temperature").alias("std_temperature"),
                avg("ph").alias("avg_ph"),
                stddev("ph").alias("std_ph"),
                avg("dissolved_oxygen").alias("avg_do"),
                avg("cell_density").alias("avg_cell_density"),
                max("cell_density").alias("max_cell_density"),
                count("*").alias("reading_count"),
                sum(when(col("all_specs_met"), 1).otherwise(0)).alias("in_spec_count")
            )
            .select(
                col("window.start").alias("hour_start"),
                col("window.end").alias("hour_end"),
                "*"
            )
            .drop("window")
            .withColumn("spec_compliance_percent",
                       (col("in_spec_count") / col("reading_count") * 100))
    )


@dlt.table(
    comment="Batch analytics summary",
    table_properties={"quality": "gold"}
)
def gold_batch_analytics():
    """
    Batch-level aggregations and KPIs
    """
    sensors = dlt.read("silver_bioreactor_sensors")
    batches = dlt.read("bronze_batch_records")

    batch_sensor_agg = (
        sensors
            .groupBy("bioreactor_id")
            .agg(
                max("cell_density").alias("max_cell_density_achieved"),
                avg("temperature").alias("avg_temperature"),
                avg("ph").alias("avg_ph"),
                avg("all_specs_met").alias("process_compliance_rate")
            )
    )

    return (
        batches
            .join(batch_sensor_agg, "bioreactor_id", "left")
            .withColumn("predicted_yield",
                       lit(90) + (col("max_cell_density_achieved") - 4) * 5 + rand() * 3)
            .withColumn("batch_duration_days",
                       datediff(current_date(), col("start_date")))
    )


@dlt.table(
    comment="Contamination risk monitoring",
    table_properties={"quality": "gold"}
)
def gold_contamination_risk():
    """
    Real-time contamination risk scores by bioreactor
    """
    return (
        dlt.read_stream("silver_bioreactor_sensors")
            .withWatermark("sensor_timestamp", "30 minutes")
            .groupBy(
                window("sensor_timestamp", "30 minutes"),
                "bioreactor_id"
            )
            .agg(
                stddev("ph").alias("ph_instability"),
                stddev("temperature").alias("temp_instability"),
                avg("dissolved_oxygen").alias("avg_do")
            )
            .select(
                col("window.end").alias("assessment_time"),
                col("bioreactor_id"),
                # Risk score based on instability
                ((col("ph_instability") * 2) +
                 (col("temp_instability") * 5) +
                 when(col("avg_do") < 40, 0.3).otherwise(0.05)).alias("contamination_risk_score"),
                when(((col("ph_instability") * 2) + (col("temp_instability") * 5)) > 0.5, "High")
                    .when(((col("ph_instability") * 2) + (col("temp_instability") * 5)) > 0.2, "Medium")
                    .otherwise("Low").alias("risk_level")
            )
    )


@dlt.table(
    comment="Equipment predictive maintenance scores",
    table_properties={"quality": "gold"}
)
def gold_predictive_maintenance():
    """
    Predictive maintenance alerts and recommendations
    """
    return (
        dlt.read_stream("silver_equipment_health")
            .filter(col("health_score") < 85)
            .withColumn("days_until_maintenance",
                       when(col("health_score") < 70, 7)
                       .when(col("health_score") < 85, 30)
                       .otherwise(90))
            .withColumn("maintenance_urgency",
                       when(col("health_score") < 70, "High")
                       .when(col("health_score") < 85, "Medium")
                       .otherwise("Low"))
            .withColumn("alert_id",
                       concat(lit("PM-"), col("equipment_id"), lit("-"),
                             date_format(col("sensor_timestamp"), "yyyyMMdd")))
    )


# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Monitoring

# COMMAND ----------

@dlt.table(
    comment="Data quality metrics for monitoring",
    table_properties={"quality": "monitoring"}
)
def monitoring_data_quality():
    """
    Track data quality metrics for all tables
    """
    return (
        dlt.read_stream("bronze_bioreactor_sensors")
            .withWatermark("sensor_timestamp", "1 hour")
            .groupBy(window("sensor_timestamp", "1 hour"))
            .agg(
                count("*").alias("total_records"),
                sum(when((col("temperature").isNull()) |
                        (col("temperature") < 30) |
                        (col("temperature") > 42), 1).otherwise(0)).alias("invalid_temp_count"),
                sum(when((col("ph").isNull()) |
                        (col("ph") < 5) |
                        (col("ph") > 9), 1).otherwise(0)).alias("invalid_ph_count")
            )
            .select(
                col("window.start").alias("hour_start"),
                "*"
            )
            .drop("window")
            .withColumn("data_quality_score",
                       ((col("total_records") - col("invalid_temp_count") - col("invalid_ph_count")) /
                        col("total_records") * 100))
)
