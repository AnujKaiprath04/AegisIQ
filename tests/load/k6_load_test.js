import http from 'k6/http';
import { check, sleep } from 'k6';

// ==============================================================================
// AegisIQ High-Concurrency K6 Load Test Suite
// Concurrency: Up to 500 Virtual Users (VUs)
// SLA Thresholds: P99 < 500ms, Error Rate < 1%
// ==============================================================================

export const options = {
  stages: [
    { duration: '30s', target: 50 },  // Ramp-up to 50 VUs
    { duration: '1m', target: 100 },  // Scale to 100 VUs
    { duration: '30s', target: 500 },  // Spike test to 500 VUs
    { duration: '30s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(99)<500', 'p(95)<200', 'p(50)<50'], // Latency SLAs
    http_req_failed: ['rate<0.01'],                              // < 1% error rate
  },
};

const BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000';

export default function () {
  // 1. Health Probe
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'Health status is 200': (r) => r.status === 200,
  });

  // 2. Metrics Scraping
  const metricsRes = http.get(`${BASE_URL}/metrics`);
  check(metricsRes, {
    'Metrics status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
