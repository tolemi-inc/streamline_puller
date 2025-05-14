# Streamline Puller

A Python package for pulling data from the Streamline API.

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/streamline_puller.git
cd streamline_puller
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv env
source env/bin/activate

# On Windows
python -m venv env
.\env\Scripts\activate
```

3. Install dependencies:
```bash
# Install production dependencies only
pip install -r requirements.txt

# Or install with development dependencies
pip install -r requirements.txt
pip install pre-commit black flake8 flake8-docstrings isort mypy types-requests
```

4. (Optional) Set up pre-commit hooks for development:
```bash
pre-commit install
```

## Usage

The package provides two versions of the Streamline puller:

### V1 Puller

The V1 puller is the original implementation that uses the Streamline API v1 endpoints. It provides methods for:
- Getting occupancies
- Getting inspections
- Getting violations
- Getting permits
- Creating inspection reports
- Creating violations reports
- Creating permits reports

Example usage:
```python
from streamline_puller import StreamlineV1

# Initialize the puller with your credentials
puller = StreamlineV1(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tenant_id="your_tenant_id",
    subscription_key="your_subscription_key"
)

# Get occupancies
occupancies = puller.get_occupancies()

# Create an inspection report
puller.create_inspection_report("inspections.csv")
```

However, we do all of this from swarm, so you'll put your secrets there and specify the report and it will do all this for you.


### V2 Puller

The V2 puller is a newer implementation that uses the Streamline API v2 endpoints. Right now, it only supports Occupancies and Inspections.

Example usage:
```python
from streamline_puller import StreamlineV2

# Initialize the puller with your credentials
puller = StreamlineV2(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tenant_id="your_tenant_id",
    subscription_key="your_subscription_key"
)

# Get occupancies
occupancies = puller.get_occupancies()

# Create an inspection report
puller.create_inspection_report("inspections.csv")
```

## Development

This project uses pre-commit hooks for code quality. The hooks will run automatically before each commit and include:
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)

To set up the development environment:
```bash
# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=streamline_puller
```

### Code Quality Tools
```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8

# Run type checker
mypy .
```

## Configuration


The package requires the following configuration:
- `client_id`: Your Streamline API client ID
- `client_secret`: Your Streamline API client secret
- `tenant_id`: Your Azure tenant ID
- `subscription_key`: Your Streamline API subscription key

For local development, throw them in a config.json file and you can load them as an argument to test locally.

Config.json

```
{
    "config": {
      "version": "v2",
      "client_id": "<client_id>",
      "subscription_key": "<sub_key>",
      "username": "<username>",
      "password": "<password>",
      "report_name": "Occupancies",
      "include_historical_data": "No"
    },
    "dataFilePath": "output.csv"
  }
```

Then you'd run `python streamline_puller/main.py --config streamline_puller/config_v2.json`


## License

This project is licensed under the MIT License - see the LICENSE file for details.
