"""
Test suite for synthetic data generators
"""
import pytest
import pandas as pd
from backend.utils.synthetic_data import PharmaDataGenerator

generator = PharmaDataGenerator(seed=42)


class TestBioreactorDataGeneration:
    """Test bioreactor timeseries data generation"""

    def test_basic_generation(self):
        """Test basic bioreactor data generation"""
        df = generator.generate_bioreactor_timeseries("BR-01", hours=24, interval_minutes=5)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "timestamp" in df.columns
        assert "temperature" in df.columns
        assert "ph" in df.columns
        assert "dissolved_oxygen" in df.columns

    def test_data_ranges(self):
        """Test that generated data is within valid ranges"""
        df = generator.generate_bioreactor_timeseries("BR-01", hours=48)

        # Temperature should be around 37°C
        assert df["temperature"].min() >= 30.0
        assert df["temperature"].max() <= 42.0

        # pH should be around 7.0
        assert df["ph"].min() >= 5.0
        assert df["ph"].max() <= 9.0

        # DO should be 0-100%
        assert df["dissolved_oxygen"].min() >= 0
        assert df["dissolved_oxygen"].max() <= 100

    def test_cell_growth_phases(self):
        """Test that cell growth follows expected phases"""
        df = generator.generate_bioreactor_timeseries("BR-01", hours=168, interval_minutes=60)

        phases = df["phase"].unique()
        assert "lag" in phases
        assert "exponential" in phases or "stationary" in phases

        # Cell density should generally increase
        early_density = df["cell_density"].iloc[:10].mean()
        late_density = df["cell_density"].iloc[-10:].mean()
        assert late_density > early_density

    def test_anomaly_injection(self):
        """Test anomaly injection in data"""
        df_normal = generator.generate_bioreactor_timeseries(
            "BR-01", hours=100, add_anomalies=False
        )
        df_anomalies = generator.generate_bioreactor_timeseries(
            "BR-01", hours=100, add_anomalies=True
        )

        # With anomalies should have higher variance
        assert df_anomalies["temperature"].std() >= df_normal["temperature"].std()


class TestBatchDataGeneration:
    """Test batch records generation"""

    def test_batch_records(self):
        """Test batch record generation"""
        batches = generator.generate_batch_records(num_batches=20)

        assert len(batches) == 20
        assert all("batch_id" in b for b in batches)
        assert all("yield_percent" in b for b in batches)
        assert all("status" in b for b in batches)

    def test_yield_distribution(self):
        """Test yield distribution is realistic"""
        batches = generator.generate_batch_records(num_batches=100)
        yields = [b["yield_percent"] for b in batches]

        avg_yield = sum(yields) / len(yields)
        assert 85 < avg_yield < 95  # Realistic pharmaceutical yields

    def test_deviations(self):
        """Test that some batches have deviations"""
        batches = generator.generate_batch_records(num_batches=100)
        batches_with_deviations = [b for b in batches if len(b["deviations"]) > 0]

        # Around 10% should have deviations
        assert 5 <= len(batches_with_deviations) <= 20


class TestEquipmentDataGeneration:
    """Test equipment health data generation"""

    def test_equipment_generation(self):
        """Test equipment data generation"""
        equipment = generator.generate_equipment_health(num_equipment=10)

        assert len(equipment) == 10
        assert all("equipment_id" in e for e in equipment)
        assert all("health_score" in e for e in equipment)
        assert all(60 <= e["health_score"] <= 100 for e in equipment)

    def test_health_status_correlation(self):
        """Test that status correlates with health score"""
        equipment = generator.generate_equipment_health(num_equipment=50)

        for eq in equipment:
            if eq["health_score"] >= 85:
                assert eq["status"] == "Operational"
            elif eq["health_score"] >= 70:
                assert eq["status"] == "Warning"
            else:
                assert eq["status"] == "Critical"


class TestContaminationDataGeneration:
    """Test contamination alert generation"""

    def test_contamination_alerts(self):
        """Test contamination alert generation"""
        alerts = generator.generate_contamination_alerts(num_alerts=30)

        assert len(alerts) == 30
        assert all("risk_score" in a for a in alerts)
        assert all(0 <= a["risk_score"] <= 1 for a in alerts)
        assert all("status" in a for a in alerts)

    def test_risk_distribution(self):
        """Test that most alerts are low risk"""
        alerts = generator.generate_contamination_alerts(num_alerts=100)

        low_risk = len([a for a in alerts if a["status"] == "Low"])
        high_risk = len([a for a in alerts if a["status"] == "High"])

        # Most should be low risk
        assert low_risk > high_risk


class TestAuditTrailGeneration:
    """Test audit trail generation"""

    def test_audit_trail(self):
        """Test audit trail generation"""
        logs = generator.generate_audit_trail(num_entries=50)

        assert len(logs) == 50
        assert all("audit_id" in log for log in logs)
        assert all("user_name" in log for log in logs)
        assert all("action" in log for log in logs)
        assert all("hash_signature" in log for log in logs)

    def test_audit_timestamp_ordering(self):
        """Test that audit logs are in reverse chronological order"""
        logs = generator.generate_audit_trail(num_entries=100)

        # Should be sorted in reverse chronological order
        timestamps = [log["timestamp"] for log in logs]
        assert timestamps == sorted(timestamps, reverse=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
