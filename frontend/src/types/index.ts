/**
 * TypeScript type definitions for Pharma Digital Twin
 */

export interface BioreactorStatus {
  bioreactor_id: string;
  name: string;
  status: 'Operational' | 'Warning' | 'Critical' | 'Offline';
  current_batch_id?: string;
  start_time?: string;
  estimated_harvest?: string;
  phase?: 'lag' | 'exponential' | 'stationary' | 'death';
  working_volume: number;
  last_updated: string;
}

export interface SensorData {
  timestamp: string;
  bioreactor_id: string;
  temperature: number;
  ph: number;
  dissolved_oxygen: number;
  agitation_rpm: number;
  pressure: number;
  cell_density: number;
  viable_cell_count: number;
  glucose?: number;
  lactate?: number;
}

export interface BatchRecord {
  batch_id: string;
  product_name: string;
  product: string;
  start_date: string;
  end_date?: string;
  status: 'In Progress' | 'QC Review' | 'QA Review' | 'Released' | 'Rejected';
  target_yield: number;
  actual_yield?: number;
  yield_percent?: number;
  quality_score?: number;
  purity_percent?: number;
  potency_percent?: number;
  bioreactor_id: string;
  manufacturing_site: string;
  responsible_person: string;
  deviations: Deviation[];
}

export interface Deviation {
  deviation_id: string;
  description: string;
  severity: 'Minor' | 'Major';
  investigation_required: boolean;
}

export interface EquipmentHealth {
  equipment_id: string;
  name: string;
  type: string;
  health_score: number;
  status: 'Operational' | 'Warning' | 'Critical';
  last_maintenance: string;
  next_maintenance: string;
  total_runtime_hours: number;
  manufacturer: string;
}

export interface ContaminationAlert {
  alert_id: string;
  timestamp: string;
  bioreactor: string;
  risk_score: number;
  status: 'Low' | 'Medium' | 'High';
  action: string;
  alert_type: string;
  confidence: number;
  model_version: string;
}

export interface DigitalTwin {
  bioreactor_id: string;
  physical_model: {
    working_volume: number;
    max_pressure: number;
    max_temperature: number;
    heating_cooling_capacity_kw: number;
    agitation_system: string;
    sparger_type: string;
    vessel_material: string;
    sensor_count: number;
    manufacturer: string;
    model: string;
  };
  process_state: {
    current_batch: string;
    inoculation_date: string;
    estimated_harvest: string;
    phase: string;
    current_volume: number;
    cell_line: string;
    product: string;
  };
  maintenance_history: {
    last_cip: string;
    last_sip: string;
    impeller_replacement: string;
    ph_probe_calibration: string;
    do_probe_calibration: string;
    next_validation: string;
  };
  current_sensors: Partial<SensorData>;
  health_score: number;
  alerts: Array<{
    severity: string;
    message: string;
    timestamp: string;
  }>;
  predictions: {
    estimated_peak_density: number;
    estimated_peak_time: string;
    predicted_yield_percent: number;
    contamination_risk: number;
  };
}

export interface AuditLog {
  audit_id: string;
  timestamp: string;
  user_name: string;
  action: 'CREATE' | 'READ' | 'UPDATE' | 'DELETE' | 'APPROVE' | 'REJECT' | 'ELECTRONIC_SIGNATURE';
  entity_type: string;
  entity_id: string;
  old_value?: Record<string, any>;
  new_value?: Record<string, any>;
  change_reason?: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
}
