/**
 * API service for communicating with FastAPI backend
 */
import axios, { AxiosInstance } from 'axios';
import type {
  BioreactorStatus,
  SensorData,
  BatchRecord,
  EquipmentHealth,
  ContaminationAlert,
  DigitalTwin,
  AuditLog,
} from '@types/index';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api/v1',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Name': 'Demo User',
        'X-User-Role': 'Manufacturing Specialist',
      },
    });
  }

  // Bioreactor endpoints
  async getBioreactorList(): Promise<BioreactorStatus[]> {
    const response = await this.client.get<BioreactorStatus[]>('/bioreactor/list');
    return response.data;
  }

  async getSensorData(bioreactorId: string, hours = 24): Promise<SensorData[]> {
    const response = await this.client.get<SensorData[]>(
      `/bioreactor/${bioreactorId}/sensors`,
      { params: { hours } }
    );
    return response.data;
  }

  async getDigitalTwin(bioreactorId: string): Promise<DigitalTwin> {
    const response = await this.client.get<DigitalTwin>(
      `/bioreactor/${bioreactorId}/digital-twin`
    );
    return response.data;
  }

  async getCurrentStatus(bioreactorId: string) {
    const response = await this.client.get(`/bioreactor/${bioreactorId}/current`);
    return response.data;
  }

  // Batch endpoints
  async getBatchList(params?: { status?: string; limit?: number }): Promise<BatchRecord[]> {
    const response = await this.client.get<BatchRecord[]>('/batch/list', { params });
    return response.data;
  }

  async getBatchDetails(batchId: string): Promise<BatchRecord> {
    const response = await this.client.get<BatchRecord>(`/batch/${batchId}`);
    return response.data;
  }

  async getBatchYieldPrediction(batchId: string) {
    const response = await this.client.get(`/batch/${batchId}/yield-prediction`);
    return response.data;
  }

  async getYieldTrends(days = 90) {
    const response = await this.client.get('/batch/analytics/yield-trends', {
      params: { days },
    });
    return response.data;
  }

  // Equipment endpoints
  async getEquipmentList(params?: { status?: string }): Promise<EquipmentHealth[]> {
    const response = await this.client.get<EquipmentHealth[]>('/equipment/list', { params });
    return response.data;
  }

  async getEquipmentHealth(equipmentId: string) {
    const response = await this.client.get(`/equipment/${equipmentId}/health`);
    return response.data;
  }

  async getMaintenanceAlerts() {
    const response = await this.client.get('/equipment/predictive-maintenance/alerts');
    return response.data;
  }

  // Contamination endpoints
  async getContaminationAlerts(params?: {
    status?: string;
    limit?: number;
  }): Promise<ContaminationAlert[]> {
    const response = await this.client.get<ContaminationAlert[]>('/contamination/alerts', {
      params,
    });
    return response.data;
  }

  async getRealtimeRisk(bioreactorId: string) {
    const response = await this.client.get(`/contamination/realtime-risk/${bioreactorId}`);
    return response.data;
  }

  async getContaminationSummary(days = 30) {
    const response = await this.client.get('/contamination/analytics/summary', {
      params: { days },
    });
    return response.data;
  }

  // Audit endpoints
  async getAuditLogs(params?: {
    entity_type?: string;
    limit?: number;
  }): Promise<AuditLog[]> {
    const response = await this.client.get<AuditLog[]>('/audit/logs', { params });
    return response.data;
  }

  async getEntityAuditTrail(entityType: string, entityId: string): Promise<AuditLog[]> {
    const response = await this.client.get<AuditLog[]>(
      `/audit/entity/${entityType}/${entityId}`
    );
    return response.data;
  }

  async getComplianceReport(days = 30) {
    const response = await this.client.get('/audit/compliance/report', {
      params: { days },
    });
    return response.data;
  }

  // EBR endpoints
  async getElectronicBatchRecord(batchId: string) {
    const response = await this.client.get(`/ebr/${batchId}/record`);
    return response.data;
  }

  async signBatchRecord(batchId: string, signatureMeaning: string, reason: string) {
    const response = await this.client.post(`/ebr/${batchId}/sign`, {
      signature_meaning: signatureMeaning,
      reason,
    });
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
