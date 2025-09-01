"""
Health monitoring for the news automation system
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .logger import get_logger

logger = get_logger(__name__)

class HealthMonitor:
    def __init__(self, state_file: str = "health_state.json"):
        self.state_file = state_file
        self.state = self._load_state()
        
    def _load_state(self) -> Dict[str, Any]:
        """Load health state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading health state: {str(e)}")
        
        return {
            'status': 'initializing',
            'last_check': None,
            'last_success': None,
            'consecutive_failures': 0,
            'total_success': 0,
            'total_failures': 0,
            'component_status': {}
        }
        
    def _save_state(self):
        """Save health state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving health state: {str(e)}")
            
    def update_component(self, component: str, status: str, error: Optional[str] = None):
        """Update status of a specific component."""
        self.state['component_status'][component] = {
            'status': status,
            'last_update': datetime.now().isoformat(),
            'error': error
        }
        self._save_state()
        
    def record_health_check(self, success: bool, details: Optional[Dict[str, Any]] = None):
        """Record the result of a health check."""
        now = datetime.now()
        self.state['last_check'] = now.isoformat()
        
        if success:
            self.state['last_success'] = now.isoformat()
            self.state['consecutive_failures'] = 0
            self.state['total_success'] += 1
        else:
            self.state['consecutive_failures'] += 1
            self.state['total_failures'] += 1
            
        # Update overall status
        if self.state['consecutive_failures'] == 0:
            self.state['status'] = 'healthy'
        elif self.state['consecutive_failures'] <= 3:
            self.state['status'] = 'degraded'
        else:
            self.state['status'] = 'failing'
            
        # Store check details
        if details:
            self.state['last_check_details'] = details
            
        self._save_state()
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            'status': self.state['status'],
            'lastCheck': self.state['last_check'],
            'lastSuccess': self.state['last_success'],
            'consecutiveFailures': self.state['consecutive_failures'],
            'uptime': self._calculate_uptime(),
            'components': self.state['component_status'],
            'metrics': {
                'totalSuccess': self.state['total_success'],
                'totalFailures': self.state['total_failures'],
                'successRate': self._calculate_success_rate()
            }
        }
        
    def _calculate_uptime(self) -> float:
        """Calculate system uptime percentage."""
        total = self.state['total_success'] + self.state['total_failures']
        if total == 0:
            return 100.0
        return round((self.state['total_success'] / total) * 100, 2)
        
    def _calculate_success_rate(self) -> float:
        """Calculate success rate for the last hour."""
        try:
            with open('logs/backend.log', 'r') as f:
                lines = f.readlines()
                
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            # Count successes and failures in the last hour
            success = sum(1 for line in lines if 'SUCCESS' in line and 
                        datetime.fromisoformat(line.split()[0]) > hour_ago)
            failure = sum(1 for line in lines if 'ERROR' in line and 
                        datetime.fromisoformat(line.split()[0]) > hour_ago)
                        
            total = success + failure
            return round((success / total) * 100, 2) if total > 0 else 100.0
            
        except Exception as e:
            logger.error(f"Error calculating success rate: {str(e)}")
            return 0.0
