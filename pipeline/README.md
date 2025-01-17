# Automation Pipeline

This project automates a multi-step process for monitoring and visualizing system performance data. The pipeline runs multiple scripts in sequence to collect, process, and visualize data.

## Prerequisites

1. **Python 3.8 or higher**.
2. Required Python libraries:
   - `dash`
   - `plotly`
   - `pandas`
   - `numpy`
   - `scipy`
3. `turbostat` utility installed on the system.

## Setup Instructions

### Install Dependencies

Install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

### File Structure

Ensure the following files are in the same directory:

- `pipeline.py`: The main script to run the pipeline.
- `code1.py`: Script to process turbostat logs.
- `code2.py`: Script to filter processed data.
- `code3.py`: Script to visualize the data.

## Usage

1. Run the main pipeline script:

    ```bash
    python3 automation_pipeline.py
    ```

   The script will:
   - Start `turbostat` to collect system performance data.
   - Process the data using `code1.py`.
   - Filter and save the processed data using `code2.py`.
   - Visualize the results in a web-based dashboard using `code3.py`.

2. To stop the pipeline, terminate the running script using `Ctrl+C`.

## Notes

- The pipeline uses the `sudo turbostat` command, which requires administrative privileges. Make sure to run the pipeline with the necessary permissions.
- Output files such as `TURBOSTAT_log.csv` and `filtered_turbolog.csv` will be generated in the working directory.

## Troubleshooting

- **File Not Found**: Ensure that the required scripts and input files (`t1_log`) are in the correct directory.
- **Dependency Errors**: Double-check that all dependencies are installed correctly using `pip install -r requirements.txt`.
- **Permission Issues**: Ensure you have the necessary permissions to run `turbostat`.

## License

This project is licensed under the MIT License.

