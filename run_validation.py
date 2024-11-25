# run_validation.py

import os
import logging
from datetime import datetime
import time
from tqdm import tqdm
import traceback
import sys
import colorama
from colorama import Fore, Style

from utils.url_validator import URLValidator
from utils.report_handler import ReportHandler


class ValidationRunner:
    def __init__(self):
        """Initialize the validation runner"""
        colorama.init()  # Initialize colorama for colored output
        self.start_time = datetime.now()
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f'logs/validation_{self.start_time.strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )

    def print_header(self):
        """Print colorful header information"""
        print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}URL Validation Process{Style.RESET_ALL}".center(80))
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Log File: logs/validation_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log{Style.RESET_ALL}\n")

    def print_summary(self, results):
        """Print validation summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        success_count = sum(1 for r in results if r['status'] == 'Success')
        fail_count = len(results) - success_count
        success_rate = (success_count / len(results) * 100) if results else 0

        print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Validation Summary{Style.RESET_ALL}".center(80))
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}Duration: {duration}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Total URLs Processed: {len(results)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Successful: {success_count}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {fail_count}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Success Rate: {success_rate:.2f}%{Style.RESET_ALL}\n")

        if fail_count > 0:
            print(f"{Fore.RED}Failed URLs:{Style.RESET_ALL}")
            for result in results:
                if result['status'] != 'Success':
                    print(f"{Fore.RED}- {result['url']}: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")

    def validate_urls(self):
        """Run the URL validation process"""
        try:
            self.print_header()

            # Initialize validator
            logging.info("Initializing URL validator...")
            URLValidator.setup_logging()
            URLValidator.ensure_directories()

            # Load configuration
            logging.info("Loading configuration...")
            config = URLValidator.load_config()
            paths = URLValidator.get_project_paths()

            # Read URLs from Excel
            logging.info("Reading URLs from Excel...")
            urls = URLValidator.read_excel_urls(paths["excel_path"], config["sheet_name"])

            if not urls:
                logging.error("No URLs found in Excel file")
                print(f"\n{Fore.RED}Error: No URLs found in Excel file{Style.RESET_ALL}")
                return

            print(f"\n{Fore.YELLOW}Found {len(urls)} URLs to process{Style.RESET_ALL}\n")

            # Process URLs
            results = []
            wait_time = config.get("wait_between_urls", 2)

            with tqdm(total=len(urls), desc="Processing URLs",
                      bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Style.RESET_ALL)) as pbar:
                for url, row_number in urls:
                    try:
                        # Process URL
                        result = URLValidator.process_url(url, row_number)
                        results.append(result)

                        # Update progress bar
                        status = f"Success" if result[
                                                   'status'] == 'Success' else f"Failed: {result.get('error', 'Unknown error')}"
                        pbar.set_postfix_str(status, refresh=True)
                        pbar.update(1)

                        # Wait between URLs
                        if urls.index((url, row_number)) < len(urls) - 1:  # Don't wait after last URL
                            time.sleep(wait_time)

                    except Exception as e:
                        logging.error(f"Error processing URL {url}: {str(e)}")
                        results.append({
                            'url': url,
                            'status': 'Failed',
                            'error': str(e),
                            'load_time': 0
                        })
                        pbar.update(1)

            # Generate reports
            print(f"\n{Fore.YELLOW}Generating reports...{Style.RESET_ALL}")

            try:
                excel_report = URLValidator.generate_excel_report(results)
                print(f"{Fore.GREEN}Excel report generated: {excel_report}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Error generating Excel report: {str(e)}")
                print(f"{Fore.RED}Error generating Excel report: {str(e)}{Style.RESET_ALL}")

            try:
                html_report = ReportHandler.generate_detailed_html_report(results, paths["reports"])
                print(f"{Fore.GREEN}HTML report generated: {html_report}{Style.RESET_ALL}")
            except Exception as e:
                logging.error(f"Error generating HTML report: {str(e)}")
                print(f"{Fore.RED}Error generating HTML report: {str(e)}{Style.RESET_ALL}")

            # Print summary
            self.print_summary(results)

        except Exception as e:
            logging.error(f"Validation process failed: {str(e)}")
            print(f"\n{Fore.RED}Error: Validation process failed{Style.RESET_ALL}")
            print(f"{Fore.RED}Details: {str(e)}{Style.RESET_ALL}")
            print(f"\n{Fore.RED}Stack trace:{Style.RESET_ALL}")
            print(traceback.format_exc())

        finally:
            colorama.deinit()


def main():
    """Main entry point"""
    runner = ValidationRunner()
    runner.validate_urls()


if __name__ == "__main__":
    main()