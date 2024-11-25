# setup_project.py
import os
import json
import shutil
from datetime import datetime


class ProjectSetup:
    @staticmethod
    def create_directory_structure():
        """Create the project directory structure"""
        # Project root is the current directory
        project_root = os.path.dirname(os.path.abspath(__file__))

        # Define the directory structure
        directories = {
            "resources": [
                "drivers"  # For chromedriver
            ],
            "reports": [
                "screenshots",
                "validation-reports",
                "excel-reports",
                "backups",
                "allure-results"
            ],
            "logs": [],
            "tests": [],
            "utils": []
        }

        print("\nCreating project directory structure...")

        # Create directories
        for dir_name, subdirs in directories.items():
            dir_path = os.path.join(project_root, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")

            # Create subdirectories
            for subdir in subdirs:
                subdir_path = os.path.join(dir_path, subdir)
                if not os.path.exists(subdir_path):
                    os.makedirs(subdir_path)
                    print(f"Created subdirectory: {subdir_path}")

    @staticmethod
    def create_config_file():
        """Create the configuration file"""
        config = {
            "excel_path": "resources/links.xlsx",
            "chrome_driver_path": "resources/drivers/chromedriver.exe",
            "sheet_name": "Sheet1",
            "page_load_timeout": 60,
            "max_retries": 2,
            "retry_delay": 2,
            "wait_between_urls": 2,
            "paths": {
                "screenshots_dir": "reports/screenshots",
                "reports_dir": "reports/validation-reports",
                "logs_dir": "logs",
                "output_excel_dir": "reports/excel-reports",
                "backup_dir": "reports/backups"
            },
            "reporting": {
                "generate_excel": True,
                "generate_html": True,
                "include_screenshots": True,
                "detailed_report": True
            },
            "logging": {
                "level": "INFO",
                "file_format": "validation_%Y%m%d.log",
                "console_output": True
            },
            "validation": {
                "check_ssl": True,
                "verify_content": True,
                "capture_performance": True,
                "check_broken_links": False
            }
        }

        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"\nCreated configuration file: {config_path}")

    @staticmethod
    def create_requirements_file():
        """Create the requirements file"""
        requirements = """selenium>=4.16.0
webdriver-manager>=4.0.1
pytest>=7.4.3
allure-pytest>=2.13.2
openpyxl>=3.1.2
pandas>=2.1.1
pillow>=10.1.0
requests>=2.31.0
urllib3>=2.0.7
python-dateutil>=2.8.2
colorama>=0.4.6
tqdm>=4.66.1
beautifulsoup4>=4.12.2
lxml>=4.9.3
cryptography>=41.0.7
pytest-html>=4.1.1
pytest-xdist>=3.5.0
pytest-rerunfailures>=12.0"""

        req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
        with open(req_path, 'w') as f:
            f.write(requirements)
        print(f"\nCreated requirements file: {req_path}")

    @staticmethod
    def create_sample_excel():
        """Create a sample Excel file for URLs"""
        try:
            import pandas as pd

            sample_data = {
                'URL': [
                    'https://www.google.com',
                    'https://www.github.com',
                    'https://www.python.org'
                ]
            }

            df = pd.DataFrame(sample_data)
            excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'resources', 'links.xlsx')
            df.to_excel(excel_path, index=False, sheet_name='Sheet1')
            print(f"\nCreated sample Excel file: {excel_path}")
        except ImportError:
            print("\nWarning: pandas not installed. Skipping sample Excel creation.")

    @staticmethod
    def create_python_files():
        """Create the main Python files"""
        project_root = os.path.dirname(os.path.abspath(__file__))

        # Create __init__.py files
        init_files = [
            os.path.join(project_root, 'tests', '__init__.py'),
            os.path.join(project_root, 'utils', '__init__.py')
        ]

        for init_file in init_files:
            with open(init_file, 'w') as f:
                f.write('# Initialize package\n')
            print(f"Created file: {init_file}")

        # Create main script file
        main_content = '''import os
import logging
from datetime import datetime
from url_validator import URLValidator
from report_handler import HTMLReportHandler

def main():
    try:
        # Initialize the validator
        URLValidator.setup_logging()
        URLValidator.ensure_directories()

        # Load configuration
        config = URLValidator.load_config()
        paths = URLValidator.get_project_paths()

        # Read and process URLs
        urls = URLValidator.read_excel_urls(paths["excel_path"], config["sheet_name"])
        results = []

        print(f"\\nStarting URL validation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Found {len(urls)} URLs to process\\n")

        for i, (url, row_number) in enumerate(urls, 1):
            print(f"Processing URL {i}/{len(urls)}: {url}")
            result = URLValidator.process_url(url, row_number)
            results.append(result)

        # Generate reports
        excel_report = URLValidator.generate_excel_report(results)
        html_report = HTMLReportHandler.generate_detailed_html_report(
            results, 
            paths["reports"]
        )

        print(f"\\nValidation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Excel report: {excel_report}")
        print(f"HTML report: {html_report}")

    except Exception as e:
        logging.error(f"Validation process failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
'''

        main_path = os.path.join(project_root, 'run_validation.py')
        with open(main_path, 'w') as f:
            f.write(main_content)
        print(f"\nCreated main script file: {main_path}")

    @staticmethod
    def create_readme():
        """Create README.md file"""
        readme_content = '''# URL Validator

A robust tool for validating URLs and generating detailed reports.

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Download ChromeDriver and place it in `resources/drivers/`
4. Update URLs in `resources/links.xlsx`

## Usage

Run the validation:
```
python run_validation.py
```

Reports will be generated in:
- Excel: `reports/excel-reports/`
- HTML: `reports/validation-reports/`
- Screenshots: `reports/screenshots/`

## Configuration

Update `config.json` to customize:
- Timeouts and delays
- Report generation options
- Validation settings
- File paths

## Project Structure

```
├── config.json
├── requirements.txt
├── run_validation.py
├── resources/
│   ├── drivers/
│   └── links.xlsx
├── reports/
│   ├── screenshots/
│   ├── validation-reports/
│   ├── excel-reports/
│   └── backups/
├── logs/
├── tests/
└── utils/
```

## Features

- URL validation with detailed error checking
- Screenshot capture
- Performance monitoring
- Detailed HTML and Excel reports
- Configurable validation options
- Comprehensive logging
'''

        readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"\nCreated README file: {readme_path}")

    @staticmethod
    def setup_project():
        """Run the complete project setup"""
        print("Starting project setup...")

        try:
            ProjectSetup.create_directory_structure()
            ProjectSetup.create_config_file()
            ProjectSetup.create_requirements_file()
            ProjectSetup.create_sample_excel()
            ProjectSetup.create_python_files()
            ProjectSetup.create_readme()

            print("\nProject setup completed successfully!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Download ChromeDriver and place it in resources/drivers/")
            print("3. Update URLs in resources/links.xlsx")
            print("4. Run the validator: python run_validation.py")

        except Exception as e:
            print(f"\nError during project setup: {str(e)}")
            raise


if __name__ == "__main__":
    ProjectSetup.setup_project()