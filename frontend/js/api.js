/**
 * Frontend API Client - Shared utility functions for all dashboards
 * Provides abstraction layer for backend API calls
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// ============================================================================
// SENSOR OPERATIONS
// ============================================================================

async function getSensors() {
    return fetch(`${API_BASE_URL}/sensors`).then(r => r.json());
}

async function getActiveSensors() {
    return fetch(`${API_BASE_URL}/sensors/active`).then(r => r.json());
}

async function getSensorById(sensorId) {
    return fetch(`${API_BASE_URL}/sensors/by-id/${sensorId}`).then(r => r.json());
}

async function getSensorReadings(sensorId, limit = 100) {
    return fetch(`${API_BASE_URL}/sensors/${sensorId}/readings?limit=${limit}`).then(r => r.json());
}

async function getLatestReadings() {
    return fetch(`${API_BASE_URL}/sensors/latest`).then(r => r.json());
}

// ============================================================================
// MEASUREMENT OPERATIONS
// ============================================================================

async function getMeasurements(params = {}) {
    const query = new URLSearchParams(params);
    return fetch(`${API_BASE_URL}/measurements/paginated?${query}`).then(r => r.json());
}

async function getLatestMeasurements() {
    return fetch(`${API_BASE_URL}/measurements/latest`).then(r => r.json());
}

async function getTimeSeries(params = {}) {
    const query = new URLSearchParams(params);
    return fetch(`${API_BASE_URL}/measurements/timeseries?${query}`).then(r => r.json());
}

async function compareSensors(sensorIds, measurementTypeId) {
    const params = new URLSearchParams({
        sensor_ids: sensorIds.join(','),
        measurement_type_id: measurementTypeId
    });
    return fetch(`${API_BASE_URL}/measurements/compare?${params}`).then(r => r.json());
}

async function getSensorStatistics(sensorId) {
    return fetch(`${API_BASE_URL}/measurements/statistics/${sensorId}`).then(r => r.json());
}

// ============================================================================
// STATISTICS OPERATIONS
// ============================================================================

async function getDashboardOverview() {
    return fetch(`${API_BASE_URL}/statistics/overview`).then(r => r.json());
}

async function getDistribution(params = {}) {
    const query = new URLSearchParams(params);
    return fetch(`${API_BASE_URL}/statistics/distribution?${query}`).then(r => r.json());
}

async function getCorrelation(typeId, sensor1Id, sensor2Id, days = 7) {
    const params = new URLSearchParams({
        measurement_type_id: typeId,
        sensor1_id: sensor1Id,
        sensor2_id: sensor2Id,
        days: days
    });
    return fetch(`${API_BASE_URL}/statistics/correlation?${params}`).then(r => r.json());
}

async function detectAnomalies(sensorId, params = {}) {
    const query = new URLSearchParams(params);
    return fetch(`${API_BASE_URL}/statistics/anomalies/${sensorId}?${query}`).then(r => r.json());
}

async function getTrendAnalysis(sensorId, days = 7) {
    const params = new URLSearchParams({ days: days });
    return fetch(`${API_BASE_URL}/statistics/trend/${sensorId}?${params}`).then(r => r.json());
}

// ============================================================================
// ALERT OPERATIONS
// ============================================================================

async function getAlerts() {
    return fetch(`${API_BASE_URL}/alerts`).then(r => r.json());
}

async function getActiveAlerts() {
    return fetch(`${API_BASE_URL}/alerts/active`).then(r => r.json());
}

async function createAlert(data) {
    return fetch(`${API_BASE_URL}/alerts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(r => r.json());
}

async function resolveAlert(alertId) {
    return fetch(`${API_BASE_URL}/alerts/${alertId}/resolve`, {
        method: 'PATCH'
    }).then(r => r.json());
}

// ============================================================================
// HISTORY OPERATIONS
// ============================================================================

async function getHistory(params = {}) {
    const query = new URLSearchParams(params);
    return fetch(`${API_BASE_URL}/sensors/history?${query}`).then(r => r.json());
}

async function getSensorHistory(sensorId, days = 30) {
    return fetch(`${API_BASE_URL}/sensors/statistics/${sensorId}?days=${days}`).then(r => r.json());
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format timestamp to readable date string
 */
function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

/**
 * Format timestamp to time only
 */
function formatTime(dateString) {
    return new Date(dateString).toLocaleTimeString();
}

/**
 * Format value with unit
 */
function formatValue(value, unit = '') {
    const num = parseFloat(value);
    if (isNaN(num)) return '-';
    return `${num.toFixed(2)} ${unit}`.trim();
}

/**
 * Get color based on value thresholds
 */
function getStatusColor(value, min, max) {
    if (value < min || value > max) return 'text-red-500';
    if (value < min + (max - min) * 0.25) return 'text-blue-500';
    if (value > max - (max - min) * 0.25) return 'text-orange-500';
    return 'text-green-500';
}

/**
 * Get trend icon based on values
 */
function getTrendIcon(previous, current) {
    if (current > previous) return '📈';
    if (current < previous) return '📉';
    return '→';
}

/**
 * Populate select element with options
 */
async function populateSelect(selectId, fetchFn, valueKey, labelKey) {
    try {
        const data = await fetchFn();
        const select = document.getElementById(selectId);
        if (!select) return;
        
        const items = Array.isArray(data) ? data : Object.values(data);
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item[valueKey];
            option.textContent = item[labelKey];
            select.appendChild(option);
        });
    } catch (error) {
        console.error(`Error populating select ${selectId}:`, error);
    }
}

/**
 * Handle API errors with user-friendly messages
 */
function handleError(error, context = '') {
    console.error(`API Error (${context}):`, error);
    
    let message = 'An error occurred';
    if (error.message) message = error.message;
    if (error.response?.statusText) message = error.response.statusText;
    
    showNotification(`Error: ${message}`, 'error');
    return null;
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-600' : type === 'success' ? 'bg-green-600' : 'bg-blue-600';
    toast.className = `fixed bottom-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

/**
 * Fetch with error handling
 */
async function fetchWithError(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        handleError(error, url);
        throw error;
    }
}

/**
 * Debounce function for search/filter inputs
 */
function debounce(fn, delay = 300) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

/**
 * Auto-refresh data at regular interval
 */
function autoRefresh(fn, intervalMs = 30000) {
    fn(); // Run immediately
    const intervalId = setInterval(fn, intervalMs);
    
    // Return function to stop refresh
    return () => clearInterval(intervalId);
}

// ============================================================================
// EXPORT FOR MODULES
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        // Sensors
        getSensors,
        getActiveSensors,
        getSensorById,
        getSensorReadings,
        getLatestReadings,
        // Measurements
        getMeasurements,
        getLatestMeasurements,
        getTimeSeries,
        compareSensors,
        getSensorStatistics,
        // Statistics
        getDashboardOverview,
        getDistribution,
        getCorrelation,
        detectAnomalies,
        getTrendAnalysis,
        // Alerts
        getAlerts,
        getActiveAlerts,
        createAlert,
        resolveAlert,
        // History
        getHistory,
        getSensorHistory,
        // Utilities
        formatDate,
        formatTime,
        formatValue,
        getStatusColor,
        getTrendIcon,
        populateSelect,
        handleError,
        showNotification,
        fetchWithError,
        debounce,
        autoRefresh
    };
}
