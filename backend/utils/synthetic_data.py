"""
Synthetic data generator for pharmaceutical manufacturing
Uses Faker library for realistic test data
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker
import pandas as pd
import numpy as np

fake = Faker()


class PharmaDataGenerator:
    """Generate realistic pharmaceutical manufacturing data"""

    def __init__(self, seed: int = 42):
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)

    def generate_bioreactor_timeseries(
        self,
        bioreactor_id: str,
        hours: int = 168,  # 1 week
        interval_minutes: int = 5,
        add_anomalies: bool = False
    ) -> pd.DataFrame:
        """Generate realistic bioreactor sensor timeseries"""

        num_points = (hours * 60) // interval_minutes
        timestamps = [
            datetime.now() - timedelta(minutes=interval_minutes * i)
            for i in range(num_points, 0, -1)
        ]

        data = []
        for i, ts in enumerate(timestamps):
            # Simulate cell growth phases
            growth_phase_hours = i * interval_minutes / 60
            if growth_phase_hours < 24:
                phase = "lag"
                growth_factor = 0.1
            elif growth_phase_hours < 96:
                phase = "exponential"
                growth_factor = (growth_phase_hours - 24) / 72
            elif growth_phase_hours < 144:
                phase = "stationary"
                growth_factor = 1.0
            else:
                phase = "death"
                growth_factor = 1.0 - ((growth_phase_hours - 144) / 24) * 0.3

            # Critical Process Parameters with realistic variations
            temperature = 37.0 + np.random.normal(0, 0.05)
            ph = 7.0 + np.random.normal(0, 0.02) - (growth_factor * 0.1)  # pH drifts down
            dissolved_oxygen = 45 + np.random.normal(0, 2) - (growth_factor * 5)
            agitation_rpm = 120 + np.random.randint(-3, 3)
            pressure = 1.2 + np.random.normal(0, 0.005)

            # Critical Quality Attributes
            cell_density = growth_factor * 4.5 + np.random.normal(0, 0.1)
            viable_cell_count = growth_factor * 1.2e7 + np.random.normal(0, 1e5)

            # Nutrients
            glucose = 10.0 - (growth_factor * 8.5) + np.random.normal(0, 0.2)
            lactate = growth_factor * 3.2 + np.random.normal(0, 0.1)

            # Add anomalies occasionally
            if add_anomalies and random.random() < 0.01:
                if random.random() < 0.5:
                    temperature += random.uniform(0.5, 1.0)  # Temperature spike
                else:
                    ph += random.uniform(0.3, 0.5)  # pH upset

            data.append({
                'timestamp': ts,
                'bioreactor_id': bioreactor_id,
                'temperature': round(temperature, 2),
                'ph': round(ph, 2),
                'dissolved_oxygen': round(dissolved_oxygen, 1),
                'agitation_rpm': int(agitation_rpm),
                'pressure': round(pressure, 3),
                'cell_density': round(max(0, cell_density), 2),
                'viable_cell_count': int(max(0, viable_cell_count)),
                'glucose': round(max(0, glucose), 2),
                'lactate': round(max(0, lactate), 2),
                'phase': phase
            })

        return pd.DataFrame(data)

    def generate_batch_records(self, num_batches: int = 50) -> List[Dict]:
        """Generate synthetic batch manufacturing records"""

        products = [
            ("mAb-A", "Monoclonal Antibody"),
            ("mAb-B", "Monoclonal Antibody"),
            ("Vaccine-X", "Vaccine"),
            ("Vaccine-Y", "Vaccine"),
            ("Insulin-Pro", "Insulin"),
            ("Biosimilar-Z", "Biosimilar"),
        ]

        sites = ["Site-Boston", "Site-SanFrancisco", "Site-Singapore", "Site-Ireland"]
        statuses = ["In Progress", "QC Review", "QA Review", "Released", "Released"]
        bioreactors = ["BR-01", "BR-02", "BR-03", "BR-04", "BR-05"]

        batches = []
        for i in range(num_batches):
            product_name, product_type = random.choice(products)
            start_date = fake.date_time_between(start_date="-6M", end_date="now")

            # Realistic yield distribution (normal around 92%)
            yield_percent = np.random.normal(92, 4)
            yield_percent = max(75, min(98, yield_percent))  # Clamp

            # Quality metrics
            quality_score = np.random.normal(95, 3)
            quality_score = max(85, min(100, quality_score))

            purity = np.random.normal(98, 1)
            purity = max(95, min(100, purity))

            potency = np.random.normal(100, 5)
            potency = max(90, min(110, potency))

            # Deviations (10% of batches have deviations)
            deviations = []
            if random.random() < 0.1:
                deviations.append({
                    "deviation_id": f"DEV-{fake.random_int(1000, 9999)}",
                    "description": random.choice([
                        "Temperature excursion for 15 minutes",
                        "pH drift outside specification",
                        "Delayed sampling due to equipment issue",
                        "Power fluctuation during run"
                    ]),
                    "severity": random.choice(["Minor", "Major"]),
                    "investigation_required": True
                })

            batches.append({
                "batch_id": f"B2024-{str(i+1).zfill(3)}",
                "product_name": product_name,
                "product": product_type,
                "start_date": start_date.isoformat(),
                "end_date": (start_date + timedelta(days=random.randint(10, 21))).isoformat(),
                "status": random.choice(statuses),
                "target_yield": round(random.uniform(40, 100), 1),
                "actual_yield": round(random.uniform(35, 95), 1),
                "yield_percent": round(yield_percent, 1),
                "quality_score": round(quality_score, 1),
                "purity_percent": round(purity, 2),
                "potency_percent": round(potency, 1),
                "bioreactor_id": random.choice(bioreactors),
                "manufacturing_site": random.choice(sites),
                "responsible_person": fake.name(),
                "deviations": deviations,
                "capa_required": len(deviations) > 0 and deviations[0]["severity"] == "Major"
            })

        return batches

    def generate_equipment_health(self, num_equipment: int = 15) -> List[Dict]:
        """Generate equipment health monitoring data"""

        equipment_types = [
            ("Bioreactor", "BR"),
            ("Chromatography", "HPLC"),
            ("Centrifuge", "CENT"),
            ("Lyophilizer", "LYO"),
            ("Filtration Unit", "TFF"),
            ("Fermentation Tank", "FERM"),
            ("Mixing Tank", "MIX"),
        ]

        equipment = []
        for i in range(num_equipment):
            eq_type, prefix = random.choice(equipment_types)

            # Health score influenced by time since last maintenance
            days_since_maintenance = random.randint(0, 180)
            base_health = 100 - (days_since_maintenance / 180) * 40
            health_score = max(60, min(100, base_health + np.random.normal(0, 5)))

            # Status based on health score
            if health_score >= 85:
                status = "Operational"
            elif health_score >= 70:
                status = "Warning"
            else:
                status = "Critical"

            next_maintenance = datetime.now() + timedelta(days=random.randint(5, 90))

            equipment.append({
                "equipment_id": f"{prefix}-{str(i+1).zfill(2)}",
                "name": f"{eq_type}-{str(i+1).zfill(2)}",
                "type": eq_type,
                "health_score": round(health_score, 1),
                "status": status,
                "last_maintenance": (datetime.now() - timedelta(days=days_since_maintenance)).isoformat(),
                "next_maintenance": next_maintenance.isoformat(),
                "total_runtime_hours": random.randint(1000, 50000),
                "cycles_completed": random.randint(100, 5000),
                "location": random.choice(["Building-A", "Building-B", "Building-C"]),
                "manufacturer": random.choice(["Sartorius", "GE Healthcare", "Thermo Fisher", "Merck"]),
            })

        return equipment

    def generate_contamination_alerts(self, num_alerts: int = 20) -> List[Dict]:
        """Generate contamination detection alerts"""

        bioreactors = ["BR-01", "BR-02", "BR-03", "BR-04", "BR-05"]
        alert_types = [
            "Microbial contamination detected",
            "Elevated endotoxin levels",
            "Unusual cell morphology",
            "Abnormal metabolite profile",
            "Sensor drift detected"
        ]

        alerts = []
        for i in range(num_alerts):
            # Risk score distribution (most are low, few are high)
            risk_score = np.random.beta(2, 5)  # Skewed toward low values

            if risk_score < 0.3:
                status = "Low"
                action = "Monitor"
            elif risk_score < 0.7:
                status = "Medium"
                action = "Investigate"
            else:
                status = "High"
                action = "Immediate Action"

            alerts.append({
                "alert_id": f"CONT-{str(i+1).zfill(4)}",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                "bioreactor": random.choice(bioreactors),
                "risk_score": round(risk_score, 2),
                "status": status,
                "action": action,
                "alert_type": random.choice(alert_types),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "model_version": "contamination-detector-v2.1"
            })

        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)

    def generate_audit_trail(self, num_entries: int = 100) -> List[Dict]:
        """Generate 21 CFR Part 11 compliant audit trail"""

        actions = ["CREATE", "READ", "UPDATE", "DELETE", "APPROVE", "REJECT", "ELECTRONIC_SIGNATURE"]
        entities = ["batch", "bioreactor", "equipment", "test_result", "deviation"]
        roles = ["Manufacturing Specialist", "QC Analyst", "QA Manager", "Production Supervisor"]

        audit_entries = []
        for i in range(num_entries):
            action = random.choice(actions)
            entity_type = random.choice(entities)

            entry = {
                "audit_id": f"AUD-2024-{str(i+1).zfill(6)}",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 720))).isoformat(),
                "user_id": f"USR-{str(random.randint(1, 50)).zfill(3)}",
                "user_name": fake.name(),
                "user_role": random.choice(roles),
                "action": action,
                "entity_type": entity_type,
                "entity_id": f"{entity_type.upper()}-{str(random.randint(1, 100)).zfill(3)}",
                "change_reason": fake.sentence(),
                "ip_address": fake.ipv4_private(),
                "session_id": f"sess_{fake.uuid4()[:8]}",
                "severity": random.choice(["INFO", "WARNING", "CRITICAL"]),
                "retention_until": (datetime.now() + timedelta(days=3650)).isoformat(),  # 10 years
                "hash_signature": fake.sha256()
            }

            # Add old/new values for UPDATE actions
            if action == "UPDATE":
                entry["old_value"] = {"temperature": 36.9, "status": "In Progress"}
                entry["new_value"] = {"temperature": 37.0, "status": "QC Review"}

            audit_entries.append(entry)

        return sorted(audit_entries, key=lambda x: x['timestamp'], reverse=True)


# Create singleton instance
pharma_data_generator = PharmaDataGenerator()
