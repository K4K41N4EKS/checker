import { fetchOperations } from '../api/backendApi.js';

export async function loadDashboard() {
  // Placeholder: can show stats from operations
  try {
    await fetchOperations();
  } catch (e) {
    console.error('Dashboard load error:', e);
  }
}

