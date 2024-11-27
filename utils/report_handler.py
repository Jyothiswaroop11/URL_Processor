import os
import base64
import time
import shutil
import logging
from datetime import datetime

# Global status variables - matching with URL_validator.py
STATUS_SUCCESS = "Success"
STATUS_FAILED = "Failed"
STATUS_WARNING = "Warning"
STATUS_SKIP = "Skip"

# Level Variables - DISPLAY in LOGS
LEVEL_PASS = "PASS"
LEVEL_FAIL = "FAIL"
LEVEL_WARNING = "WARNING"
LEVEL_SKIP = "SKIP"
LEVEL_ERROR = "ERROR"
LEVEL_INFO = "INFO"

class ReportHandler:
    @staticmethod
    def get_project_paths():
        """Get project paths"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return {
            "reports": os.path.join(project_root, "reports"),
            "html_reports": os.path.join(project_root, "reports", "validation-reports"),
            "backup_reports": os.path.join(project_root, "reports", "backups")
        }

    @staticmethod
    def backup_previous_reports():
        """Backup previous reports"""
        try:
            paths = ReportHandler.get_project_paths()
            report_dir = paths["html_reports"]
            backup_dir = paths["backup_reports"]

            if not os.path.exists(report_dir) or not os.listdir(report_dir):
                return

            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for filename in os.listdir(report_dir):
                if filename.endswith('.html'):
                    src_path = os.path.join(report_dir, filename)
                    backup_filename = f"Previous-{filename.replace('.html', '')}_{timestamp}.html"
                    dst_path = os.path.join(backup_dir, backup_filename)
                    shutil.move(src_path, dst_path)
                    print(f"Backed up report: {dst_path}")

        except Exception as e:
            print(f"Error during report backup: {str(e)}")

    @staticmethod
    def ensure_report_directory():
        """Ensure report directory exists"""
        paths = ReportHandler.get_project_paths()
        for path in paths.values():
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def calculate_stats(results):
        """Calculate test statistics"""
        total = len(results)
        passed = sum(1 for r in results if r['status'] == STATUS_SUCCESS)
        failed = sum(1 for r in results if r['status'] == STATUS_FAILED)
        warnings = sum(1 for r in results if r['status'] == STATUS_WARNING)
        skipped = sum(1 for r in results if r['status'] == STATUS_SKIP)

        effective_total = total - skipped
        pass_rate = (passed / effective_total * 100) if effective_total > 0 else 0

        return {
            'total': total,
            'passed': passed,
            'failed': failed + warnings,
            'skipped': skipped,
            'warnings': warnings,
            'pass_rate': pass_rate,
            'total_duration': sum(result.get('load_time', 0) for result in results)
        }

    @staticmethod
    def format_duration(ms):
        """Format duration in milliseconds to human-readable string"""
        total_seconds = ms / 1000
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((ms % 1000))
        return f"{hours}h {minutes}m {seconds}s+{milliseconds:03d}ms"

    @staticmethod
    def format_validation_result(url, status, title, redirected_url, duration, error=None, category=None):
        """Format validation result"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        result = {
            'url': url,
            'status': status,
            'category': category if category else (LEVEL_ERROR if status == STATUS_FAILED else STATUS_SUCCESS),
            'load_time': round(duration, 2),
            'test_logs': []
        }

        if status == STATUS_WARNING:
            log_entries = [
                {
                    'timestamp': timestamp,
                    'level': LEVEL_WARNING,
                    'message': f"Launching URL Is ==> {url}"
                },
                {
                    'timestamp': timestamp,
                    'level': LEVEL_WARNING,
                    'message': "Page Is Blocked By PaloAlto"
                }
            ]
        elif status == STATUS_SKIP:
            log_entries = [
                {
                    'timestamp': timestamp,
                    'level': LEVEL_SKIP,
                    'message': f"Launching URL Is ==> {url}"
                },
                {
                    'timestamp': timestamp,
                    'level': LEVEL_SKIP,
                    'message': "Web Access Blocked"
                }
            ]
        elif status == STATUS_FAILED:
            log_entries = [
                {
                    'timestamp': timestamp,
                    'level': LEVEL_FAIL,
                    'message': f"Launching URL Is ==> {url}"
                },
                {
                    'timestamp': timestamp,
                    'level': LEVEL_FAIL,
                    'message': "Page is failing"
                }
            ]
        else:  # SUCCESS case
            log_entries = [
                {
                    'timestamp': timestamp,
                    'level': LEVEL_PASS,
                    'message': f"Launching URL Is ==> {url}"
                },
                {
                    'timestamp': timestamp,
                    'level': LEVEL_INFO,
                    'message': f"Title Of The Page Is ==> {title}"
                },
                {
                    'timestamp': timestamp,
                    'level': LEVEL_INFO,
                    'message': f"Redirected URL Is ==> {redirected_url}"
                },
                {
                    'timestamp': timestamp,
                    'level': LEVEL_INFO,
                    'message': f"Time Taken to Launch Application - {url} is ==> {duration:.2f} Milliseconds"
                }
            ]

        result['test_logs'] = log_entries
        return result

    @staticmethod
    def generate_content_section(result, index):
        """Generate HTML content for a test result"""
        try:
            def format_timestamp(timestamp):
                if not timestamp:
                    return ""
                try:
                    time_obj = datetime.strptime(timestamp, '%H:%M:%S')
                    return time_obj.strftime('%I:%M:%S %p')
                except:
                    return timestamp

            content = f"""
                        <div id="content-{index}" class="url-content" style="display: none;">
                            <div class="logs-section">
                                <div class="log-container">
                                    <div class="log-table-container">
                                        <table class="log-table">
                                            <thead>
                                                <tr>
                                                    <th>Status</th>
                                                    <th>Timestamp</th>
                                                    <th>Details</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                    """

            for log in result.get('test_logs', []):
                message = log.get('message', '')

                # Skip Message row for Failed status
                if result['status'] == STATUS_FAILED and 'Message:' in message:
                    continue

                level = log.get('level', LEVEL_INFO)
                if "Launching URL Is ==>" in message:
                    if result['status'] == STATUS_FAILED:
                        level = LEVEL_FAIL
                    elif result['status'] == STATUS_WARNING:
                        level = LEVEL_WARNING
                    elif result['status'] == STATUS_SUCCESS:
                        level = LEVEL_PASS
                    elif result['status'] == STATUS_SKIP:
                        level = LEVEL_SKIP

                timestamp = log['timestamp'].split()[1] if log.get('timestamp') else ''
                level_class = level.lower()

                content += f"""
                            <tr class="log-entry {level_class}" data-level="{level}">
                                <td class="log-level">
                                    <span class="level-badge {level_class}">{level}</span>
                                </td>
                                <td class="log-timestamp">{format_timestamp(timestamp)}</td>
                                <td class="log-message">{message}</td>
                            </tr>
                        """

            content += """
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
            """

            content += f"""
                <div class="screenshot-section">
                    <h3>Screenshot</h3>
                    <div class="screenshot-container">
                        <button id="screenshot-btn-{index}" 
                                onclick="toggleScreenshot({index})" 
                                class="screenshot-btn">
                            <i class="fas fa-image"></i> Show Screenshot
                        </button>
                        <div id="screenshot-container-{index}" class="screenshot-wrapper" style="display: none;">
            """

            if result.get('screenshot_base64'):
                content += f"""
                                <img src="data:image/png;base64,{result['screenshot_base64']}"
                                     alt="Test Screenshot"
                                     class="screenshot-image"
                                     onclick="showFullScreenImage(this)" />
                """
            else:
                content += """
                                <div class="no-screenshot">
                                    <i class="fas fa-image-slash"></i>
                                    <p>No screenshot available</p>
                                </div>
                """

            content += """
                        </div>
                    </div>
                </div>
            </div>
            """

            return content

        except Exception as e:
            logging.error(f"Error generating content section: {str(e)}")
            return f"""
                <div id="content-{index}" class="url-content" style="display: none;">
                    <div class="error-section">
                        <h3>Error Generating Content</h3>
                        <pre>{str(e)}</pre>
                    </div>
                </div>
            """

    @staticmethod
    def get_styles():
        """Get complete CSS styles for the HTML report"""
        return """
            * { 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }

            body { 
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                font-size: 11px;
                background: #f8f9fa;
                color: #333;
                overflow: hidden;
                height: 100vh;
            }

            .layout {
                display: flex;
                flex-direction: column;
                height: 100vh;
                overflow: hidden;
            }

            .stats-bar {
                display: flex;
                justify-content: space-evenly;
                background: #658de6;
                padding: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                gap: 10px;
            }

            .stat-item {
                text-align: center;
                padding: 0px 15px;
                border-radius: 6px;
                min-width: 120px;
                transition: transform 0.3s ease;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .stat-item:hover {
                transform: translateY(-2px);
            }

            .stat-item.total {
                background: linear-gradient(145deg, #3b82f6, #2563eb);
                box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
            }
            .stat-item.total .stat-value {
                color: #ffffff;
                font-size: 1.5rem;
                font-weight: 700;
            }
            .stat-item.total .stat-label {
                color: #bfdbfe;
            }

            .stat-item.passed {
                background: linear-gradient(145deg, #22c55e, #16a34a);
                box-shadow: 0 2px 4px rgba(34, 197, 94, 0.2);
            }
            .stat-item.passed .stat-value {
                color: #ffffff;
                font-size: 1.5rem;
                font-weight: 700;
            }
            .stat-item.passed .stat-label {
                color: #bbf7d0;
            }

            .stat-item.failed {
                background: linear-gradient(145deg, #ef4444, #dc2626);
                box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
            }
            .stat-item.failed .stat-value {
                color: #ffffff;
                font-size: 1.5rem;
                font-weight: 700;
            }
            .stat-item.failed .stat-label {
                color: #fecaca;
            }

            .stat-item.pass-rate {
                background: linear-gradient(145deg, #8b5cf6, #7c3aed);
                box-shadow: 0 2px 4px rgba(139, 92, 246, 0.2);
            }
            .stat-item.pass-rate .stat-value {
                color: #ffffff;
                font-size: 1.5rem;
                font-weight: 700;
            }
            .stat-item.pass-rate .stat-label {
                color: #ddd6fe;
            }

            .stat-item.duration {
                background: linear-gradient(145deg, #f59e0b, #d97706);
                box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
            }
            .stat-item.duration .stat-value {
                color: #ffffff;
                font-size: 1.25rem;
                font-weight: 700;
            }
            .stat-item.duration .stat-label {
                color: #fef3c7;
            }

            .stat-label {
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .content-wrapper {
                display: flex;
                flex: 1;
                overflow: hidden;
            }

            .left-panel {
                width: 400px;
                background: white;
                border-right: 1px solid #ddd;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }

            /* Updated Warning Styles */
            .url-item.warning {
                background-color: rgba(255, 152, 0, 0.1);
            }
            .status-badge.warning { 
                background-color: #fff3e0; 
                color: #ef6c00;
            }
            .level-badge.warning {
                background: linear-gradient(145deg, #ff9800, #f57c00);
                color: white;
                box-shadow: 0 2px 4px rgba(255, 152, 0, 0.2);
            }

            .filter-bar {
                padding: 15px;
                border-bottom: 1px solid #ddd;
                background: #f8f9fa;
            }

            .filter-controls {
                display: flex;
                gap: 8px;
                margin-bottom: 8px;
            }

            .filter-input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.9rem;
                outline: none;
            }

            .filter-input:focus {
                border-color: #2193b0;
                box-shadow: 0 0 0 2px rgba(33, 147, 176, 0.2);
            }

            .filter-button {
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                background: #2193b0;
                color: white;
                cursor: pointer;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 5px;
                transition: background 0.3s ease;
            }

            .filter-button:hover {
                background: #1a7b93;
            }

            .url-list {
                list-style: none;
                overflow-y: auto;
                flex: 1;
            }

            .url-item {
                padding: 15px;
                border-bottom: 1px solid #eee;
                cursor: pointer;
                transition: all 0.3s ease;
                background: white;
            }

            .url-item:hover {
                background: #f5f5f5;
            }

            .url-item.active {
                background: #e3f2fd;
                border-left: 3px solid #2193b0;
            }

            .url-item.success {
                background-color: #FFFFFF;
            }

            .url-item.failed {
                background-color: rgba(220, 53, 69, 0.1);
            }

            .url-item.skip {
                background-color: rgba(71, 85, 105, 0.1);
            }

            .url-item-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
            }

            .url-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                gap: 10px;
                font-size: 10px;
            }

            .url-title {
                flex: 1;
                text-align: left;
                font-size: 0.9rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                color: #333333;
            }

            .status-container {
                flex-shrink: 0;
                text-align: right;
            }

            .right-panel {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #fff;
            }

            .status-badge {
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                display: inline-block;
                min-width: 70px;
                text-align: center;
            }

            .status-badge.success,
            .status-badge.pass { 
                background-color: #e8f5e9; 
                color: #2e7d32;
            }

            .status-badge.failed,
            .status-badge.fail { 
                background-color: #ffebee; 
                color: #c62828;
            }

            .status-badge.warning { 
                background-color: #fff3e0; 
                color: #ef6c00;
            }

            .status-badge.skip { 
                background-color: #e2e8f0; 
                color: #475569;
            }

            .level-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
                min-width: 70px;
                text-align: center;
                text-transform: uppercase;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .level-badge.pass,
            .level-badge.success {
                background: linear-gradient(145deg, #22c55e, #16a34a);
                color: white;
            }

            .level-badge.fail,
            .level-badge.error,
            .level-badge.failed {
                background: linear-gradient(145deg, #ef4444, #dc2626);
                color: white;
            }

            .level-badge.warning {
                background: linear-gradient(145deg, #ff9800, #f57c00);
                color: white;
            }

            .level-badge.info {
                background: linear-gradient(145deg, #3b82f6, #2563eb);
                color: white;
            }

            .level-badge.skip {
                background: linear-gradient(145deg, #6b7280, #4b5563);
                color: white;
            }

            .screenshot-section {
                margin-top: 20px;
            }

            .screenshot-container {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
            }

            .screenshot-btn {
                background: #2196f3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 15px;
                transition: background-color 0.3s ease;
            }

            .screenshot-btn:hover {
                background: #1976d2;
            }

            .screenshot-wrapper {
                background: white;
                border-radius: 4px;
                padding: 20px;
                text-align: center;
            }

            .screenshot-image {
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
                transition: transform 0.2s ease;
            }

            .screenshot-image:hover {
                transform: scale(1.02);
            }

            .no-screenshot {
                padding: 40px;
                color: #666;
                font-style: italic;
                text-align: center;
            }

            .no-screenshot i {
                font-size: 2rem;
                margin-bottom: 10px;
            }

            .screenshot-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.9);
                z-index: 1000;
                overflow: hidden;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .screenshot-modal.active {
                display: flex;
                justify-content: center;
                align-items: center;
                opacity: 1;
            }

            .screenshot-modal img {
                max-width: 90%;
                max-height: 90vh;
                object-fit: contain;
                margin: auto;
                border: 2px solid white;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
                transform: scale(0.9);
                transition: transform 0.3s ease;
            }

            .screenshot-modal.active img {
                transform: scale(1);
            }

            .close-modal {
                position: absolute;
                top: 20px;
                right: 30px;
                color: #f1f1f1;
                font-size: 35px;
                font-weight: bold;
                cursor: pointer;
                z-index: 1001;
                transition: color 0.3s ease;
            }

            .close-modal:hover {
                color: #ff4444;
            }

            /* Log container styles */
            .log-container {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
                margin-bottom: 20px;
                background: #ffffff;
            }

            .log-table-container {
                max-height: 400px;
                overflow-y: auto;
            }

            .log-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9rem;
            }

            .log-table th {
                position: sticky;
                top: 0;
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                border-bottom: 2px solid #ddd;
                font-weight: 600;
                color: #333;
            }

            .log-table td {
                padding: 10px 12px;
                vertical-align: middle;
                border-bottom: 1px solid #eee;
            }

            .log-message {
                font-family: 'Consolas', monospace;
                white-space: pre-wrap;
                word-break: break-word;
            }

            .log-timestamp {
                white-space: nowrap;
                color: #666;
                font-family: 'Consolas', monospace;
            }

            /* Scrollbar Styles */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }

            ::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #666;
            }

            /* Responsive Styles */
            @media screen and (max-width: 1200px) {
                .left-panel {
                    width: 350px;
                }
            }

            /* Responsive Styles Continued */
        @media screen and (max-width: 768px) {
            .stat-item {
                min-width: 120px;
                padding: 8px 15px;
            }

            .stat-value {
                font-size: 1.2rem;
            }
        }

        /* Log Entry Styles */
        .log-entry {
            transition: background-color 0.2s ease;
        }

        .log-entry:nth-child(even) {
            background-color: #f8f9fa;
        }

        .log-entry:hover {
            background-color: #f0f4f8;
        }

        /* Updated PaloAlto Message Styles */
        .paloalto-message {
            color: #f57c00;  /* Orange color for warning */
            font-weight: bold;
            font-size: 14px;
        }

        /* Entry Status Colors */
        .log-entry.warning {
            background-color: rgba(255, 152, 0, 0.1);
        }

        .log-entry.error,
        .log-entry.fail {
            background-color: rgba(239, 68, 68, 0.1);
        }

        .log-entry.success,
        .log-entry.pass {
            background-color: rgba(34, 197, 94, 0.05);
        }

        .log-entry.skip {
            background-color: rgba(107, 114, 128, 0.1);
        }

        /* Custom Scrollbar for Firefox */
        * {
            scrollbar-width: thin;
            scrollbar-color: #888 #f1f1f1;
        }

        /* URL Content Styles */
        .url-content {
            padding: 20px;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Log Section Styles */
        .logs-section {
            margin-bottom: 30px;
        }

        /* Custom Table Scrollbar */
        .log-table-container::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        .log-table-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        .log-table-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        .log-table-container::-webkit-scrollbar-thumb:hover {
            background: #666;
        }

        /* Modal Animation */
        @keyframes modalFade {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        .screenshot-modal.active {
            animation: modalFade 0.3s ease-out forwards;
        }

        /* Warning Specific Styles - Enhanced */
        .url-item.warning:hover {
            background-color: rgba(255, 152, 0, 0.15);
        }

        .status-badge.warning {
            background: #fff3e0;
            color: #ef6c00;
            border: 1px solid #ffb74d;
        }

        .level-badge.warning {
            background: linear-gradient(145deg, #ff9800, #f57c00);
            color: white;
            box-shadow: 0 2px 4px rgba(255, 152, 0, 0.2);
            border: none;
        }

        /* Status Transition Effects */
        .status-badge {
            transition: all 0.3s ease;
        }

        .status-badge:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Additional Warning Indicators */
        .warning-icon::before {
            content: '⚠';
            margin-right: 4px;
            color: #f57c00;
        }

        /* Log Message Formatting */
        .log-message {
            font-family: 'Consolas', monospace;
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.5;
        }

        .log-message.warning {
            color: #f57c00;
            font-weight: 500;
        }

        /* Screenshot Button States */
        .screenshot-btn {
            transition: all 0.3s ease;
        }

        .screenshot-btn:hover {
            background: #1976d2;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        .screenshot-btn.active {
            background: #dc3545;
        }

        /* Enhanced Modal Styles */
        .screenshot-modal.active .screenshot-image {
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            border: 3px solid white;
        }

        /* Additional Accessibility Features */
        .status-badge:focus,
        .screenshot-btn:focus,
        .filter-button:focus {
            outline: 2px solid #2196f3;
            outline-offset: 2px;
        }

        /* Print Styles */
        @media print {
            .screenshot-btn,
            .filter-bar {
                display: none;
            }

            .url-item {
                break-inside: avoid;
            }

            .screenshot-image {
                max-width: 100% !important;
                page-break-inside: avoid;
            }
        }
    """

    @staticmethod
    def get_scripts():
        """Get JavaScript for the HTML report"""
        return """
                document.addEventListener('DOMContentLoaded', function() {
                    const modal = document.createElement('div');
                    modal.className = 'screenshot-modal';
                    modal.innerHTML = `
                        <span class="close-modal">&times;</span>
                        <img src="" alt="Full Screen Screenshot">
                    `;
                    document.body.appendChild(modal);

                    modal.addEventListener('click', function(e) {
                        if (e.target === modal || e.target.className === 'close-modal') {
                            modal.classList.remove('active');
                        }
                    });

                    document.addEventListener('keydown', function(e) {
                        if (e.key === 'Escape') {
                            modal.classList.remove('active');
                        }
                    });
                });

                function toggleScreenshot(index) {
                    const container = document.getElementById(`screenshot-container-${index}`);
                    const button = document.getElementById(`screenshot-btn-${index}`);

                    if (container && button) {
                        if (container.style.display === 'none') {
                            container.style.display = 'block';
                            button.innerHTML = '<i class="fas fa-times"></i> Hide Screenshot';
                            button.classList.add('active');
                            button.style.backgroundColor = '#dc3545';
                        } else {
                            container.style.display = 'none';
                            button.innerHTML = '<i class="fas fa-image"></i> Show Screenshot';
                            button.classList.remove('active');
                            button.style.backgroundColor = '#2196f3';
                        }
                    }
                }

                function showFullScreenImage(img) {
                    const modal = document.querySelector('.screenshot-modal');
                    const modalImg = modal.querySelector('img');
                    modalImg.src = img.src;
                    modal.classList.add('active');
                }

                function filterItems() {
                    const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
                    const urlItems = document.querySelectorAll('.url-item');

                    urlItems.forEach(item => {
                        const statusBadge = item.querySelector('.status-badge');
                        const status = statusBadge ? statusBadge.textContent.trim().toLowerCase() : '';

                        if (statusFilter === 'all' || status === statusFilter) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                }

                function resetFilters() {
                    document.getElementById('statusFilter').value = 'all';
                    const urlItems = document.querySelectorAll('.url-item');
                    urlItems.forEach(item => {
                        item.style.display = 'block';
                    });
                }

                function showContent(index) {
                    document.querySelectorAll('.url-content').forEach(content => {
                        content.style.display = 'none';
                    });

                    const selectedContent = document.getElementById(`content-${index}`);
                    if (selectedContent) {
                        selectedContent.style.display = 'block';
                    }

                    document.querySelectorAll('.url-item').forEach(item => {
                        item.classList.remove('active');
                    });

                    const selectedItem = document.querySelector(`[onclick="showContent(${index})"]`);
                    if (selectedItem) {
                        selectedItem.classList.add('active');
                    }
                }

                window.onload = function() {
                    const firstItem = document.querySelector('.url-item');
                    if (firstItem) {
                        firstItem.click();
                    }

                    // Initialize modal with zoom effect
                    const modal = document.querySelector('.screenshot-modal');
                    if (modal) {
                        const modalImg = modal.querySelector('img');
                        modalImg.style.transform = 'scale(0.9)';
                        modalImg.style.transition = 'transform 0.3s ease';

                        modal.addEventListener('click', function(e) {
                            if (e.target === modal) {
                                modal.classList.remove('active');
                            }
                        });

                        const closeBtn = modal.querySelector('.close-modal');
                        if (closeBtn) {
                            closeBtn.addEventListener('click', function() {
                                modal.classList.remove('active');
                            });
                        }

                        modal.addEventListener('transitionend', function() {
                            if (!modal.classList.contains('active')) {
                                modalImg.style.transform = 'scale(0.9)';
                            }
                        });

                        modal.addEventListener('click', function(e) {
                            if (e.target === modal || e.target.className === 'close-modal') {
                                modal.classList.remove('active');
                            }
                        });
                    }
                };

                // Add keyboard navigation
                document.addEventListener('keydown', function(e) {
                    const urlItems = Array.from(document.querySelectorAll('.url-item'));
                    const activeItem = document.querySelector('.url-item.active');

                    if (!activeItem) return;

                    const currentIndex = urlItems.indexOf(activeItem);
                    let nextIndex;

                    if (e.key === 'ArrowDown') {
                        nextIndex = Math.min(currentIndex + 1, urlItems.length - 1);
                        urlItems[nextIndex].click();
                        urlItems[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    } else if (e.key === 'ArrowUp') {
                        nextIndex = Math.max(currentIndex - 1, 0);
                        urlItems[nextIndex].click();
                        urlItems[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                });

                // Custom scroll behavior for log table
                document.querySelectorAll('.log-table-container').forEach(container => {
                    container.addEventListener('wheel', function(e) {
                        if (e.deltaY !== 0) {
                            e.preventDefault();
                            this.scrollTop += e.deltaY;
                        }
                    });
                });
            """

    @staticmethod
    def generate_html_report(results):
        """Generate HTML report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ReportHandler.backup_previous_reports()
            ReportHandler.ensure_report_directory()

            paths = ReportHandler.get_project_paths()
            report_path = os.path.join(paths["html_reports"], "Automation-Report.html")

            stats = ReportHandler.calculate_stats(results)

            url_list_items = ''.join(
                f'''
                    <li class="url-item {result['status'].lower()}" onclick="showContent({i})">
                        <div class="url-item-content">
                            <div class="url-header">
                                <div class="url-title">Validating URL: <b>{result.get('formatted_url', result['url'])}</b></div>
                                <div class="status-container">
                                    <span class="status-badge {result['status'].lower()}">{result['status']}</span>
                                </div>
                            </div>
                        </div>
                    </li>
                ''' for i, result in enumerate(results)
            )

            html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>URL Validation Report - {timestamp}</title>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                    <style>{ReportHandler.get_styles()}</style>
                </head>
                <body>
                    <div class="layout">
                        <div class="stats-bar">
                            <div class="stat-item total">
                                <div class="stat-label">Total Tests</div>
                                <div class="stat-value">{stats['total']}</div>
                            </div>
                            <div class="stat-item passed">
                                <div class="stat-label">Passed</div>
                                <div class="stat-value">{stats['passed']}</div>
                            </div>
                            <div class="stat-item failed">
                                <div class="stat-label">Failed</div>
                                <div class="stat-value">{stats['failed']}</div>
                            </div>
                            <div class="stat-item pass-rate">
                                <div class="stat-label">Pass Rate</div>
                                <div class="stat-value">{stats['pass_rate']:.1f}%</div>
                            </div>
                            <div class="stat-item duration">
                                <div class="stat-label">Duration</div>
                                <div class="stat-value">{ReportHandler.format_duration(stats['total_duration'])}</div>
                            </div>
                        </div>
                        <div class="content-wrapper">
                            <div class="left-panel">
                                <div class="filter-bar">
                                    <div class="filter-controls">
                                        <select id="statusFilter" class="filter-input" onchange="filterItems()">
            <option value="all">All Status</option>
                                                        <option value="success">Success</option>
                                                        <option value="failed">Failed</option>
                                                        <option value="warning">Warning</option>
                                                        <option value="skip">Skipped</option>
                                                    </select>
                                                    <button class="filter-button" onclick="resetFilters()" title="Clear Filters">
                                                        <i class="fas fa-times"></i> Clear
                                                    </button>
                                                </div>
                                            </div>

                                            <ul class="url-list">{url_list_items}</ul>
                                        </div>

                                        <div class="right-panel">
                                            {''.join(ReportHandler.generate_content_section(result, i) for i, result in enumerate(results))}
                                        </div>
                                    </div>
                                </div>
                                <script>{ReportHandler.get_scripts()}</script>
                            </body>
                            </html>
                        """

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return report_path

        except Exception as e:
            logging.error(f"Error generating HTML report: {str(e)}")
            raise

    @staticmethod
    def generate_detailed_html_report(results, output_dir=None):
        """Generate detailed HTML report"""
        try:
            if output_dir:
                paths = ReportHandler.get_project_paths()
                paths["html_reports"] = output_dir
            return ReportHandler.generate_html_report(results)
        except Exception as e:
            logging.error(f"Error generating detailed HTML report: {str(e)}")
            raise

if __name__ == "__main__":
    print("This module should be imported, not run directly.")
