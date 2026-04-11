# Insurance Quote Automator

A Python automation tool that fills out insurance quote forms on Irish insurance websites using Playwright. This project currently supports An Post Insurance and is designed to save time by automatically populating forms with personal and vehicle information.

## Features

- **Automated Form Filling**: Automatically fills out insurance quote forms with predefined personal and vehicle information
- **Multiple Insurers Support**: Currently supports An Post Insurance with extensible architecture for additional insurers
- **Data Validation**: Includes helper functions for data formatting and validation (mileage formatting, no-claims discount calculation)
- **Async Execution**: Uses asyncio for efficient browser automation
- **Configurable Personal Data**: Easy-to-modify personal information dictionary

## Supported Insurers

- **An Post Insurance** - Fully automated quote generation

## Requirements

- Python 3.7+
- Playwright
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd insurance-quote-automator
```

2. Install dependencies:

```bash
pip install playwright
playwright install
```

## Usage

1. **Configure Personal Information**:

   Edit the `PERSONAL_INFO` dictionary in `main.py` with your personal and vehicle details:

   ```python
   PERSONAL_INFO = {
       "title": "mr",
       "first_name": "your_name",
       "last_name": "your_surname",
       "email": "your@email.com",
       # ... other fields
   }
   ```

2. **Run the Automation**:

   ```bash
   python main.py
   ```

   This will:
   - Launch a browser
   - Navigate to An Post Insurance
   - Fill out the quote form with your information
   - Submit the form and display the results

## Configuration

### Personal Information Fields

The `PERSONAL_INFO` dictionary supports the following fields:

**Personal Details:**

- `title`, `first_name`, `last_name`, `email`, `phone`, `date_of_birth`, `occupation`

**Vehicle Information:**

- `car_registration`, `car_value`, `car_purchase_date`, `estimated_mileage`
- `right_hand_drive`, `registered_in_ireland`, `is_imported`, `registered_owner`, `car_usage`

**Address:**

- `address.street`, `address.city`, `address.county`, `address.country`, `address.postal_code`

**License & Insurance:**

- `licence_type`, `licence_duration`, `has_penalty_points`
- `driving_experience`, `no_claims_discount`, `country_of_most_recent_ncd`
- `previous_insurer`, `policy_start_date`, `same_as_current_policy_end_date`, `payment_type`

**Additional Options:**

- `add_additional_driver`, `marketing_consent`, `accept_terms`

## Project Structure

```
insurance-quote-automator/
|-- main.py                 # Main entry point with personal info configuration
|-- companies/
|   |-- an_post.py         # An Post Insurance automation logic
|-- helper_functions/
|   |-- general.py         # General utility functions
|   |-- an_post.py         # An Post-specific helper functions
|-- data_maps/
|   |-- an_post.py         # Form field mappings for An Post
|-- README.md
|-- .gitignore
```

## Adding New Insurers

To add support for a new insurance company:

1. Create a new file in `companies/` (e.g., `new_insurer.py`)
2. Implement the automation functions following the pattern in `an_post.py`
3. Create corresponding helper functions in `helper_functions/`
4. Add form field mappings in `data_maps/`
5. Update `main.py` to include the new insurer

## Important Notes

- **Legal Compliance**: Ensure you have the right to automate form submissions on target websites
- **Data Privacy**: Be cautious with personal information and follow data protection regulations
- **Rate Limiting**: The tool includes reasonable delays to avoid overwhelming websites
- **Testing**: Test with non-production environments when possible

## Troubleshooting

- **Browser Issues**: Ensure Playwright browsers are installed with `playwright install`
- **Form Changes**: Insurance websites frequently update their forms - updates may be required
- **Network Issues**: Check your internet connection if forms fail to load

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add support for new insurers or improve existing functionality
4. Submit a pull request

## License

This project is provided for educational purposes. Users are responsible for ensuring compliance with website terms of service and applicable laws.

## Disclaimer

This tool is intended for legitimate quote comparison purposes only. Users must ensure they comply with all applicable laws, regulations, and website terms of service. The authors are not responsible for any misuse of this software.
