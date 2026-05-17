// Frontend constants — shared across components

// Alert types
export const ALERT_TYPES = {
  fall: { label: 'Fall Detected', color: '#ef4444' },
  sos: { label: 'SOS Triggered', color: '#dc2626' },
  no_movement: { label: 'No Movement', color: '#f59e0b' },
  impact: { label: 'High Impact', color: '#f97316' },
};

// Alert statuses
export const ALERT_STATUSES = {
  active: { label: 'Active', color: '#ef4444' },
  resolved: { label: 'Resolved', color: '#22c55e' },
  cancelled: { label: 'Cancelled', color: '#6b7280' },
};

// Severity levels
export const SEVERITY_LEVELS = {
  low: { label: 'Low', color: '#3b82f6' },
  medium: { label: 'Medium', color: '#f59e0b' },
  high: { label: 'High', color: '#f97316' },
  critical: { label: 'Critical', color: '#ef4444' },
};

// Device statuses
export const DEVICE_STATUSES = {
  online: { label: 'Online', color: '#22c55e' },
  offline: { label: 'Offline', color: '#6b7280' },
  pairing: { label: 'Pairing', color: '#3b82f6' },
};
