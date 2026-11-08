# Railway Crossing Intelligence System

A Streamlit-based project that tracks trains passing through Bichpuri Railway Station (BCP), Agra, and estimates railway gate closing and reopening times using train information.

## Project Overview

The Railway Crossing Intelligence System aims to help commuters understand approaching train movements and estimated waiting times near a railway crossing.

It uses train schedule data and live train information to estimate when the railway gate may close and reopen.

## Features

- Live train status tracking using the RailRadar API
- Multiple train tracking for Bichpuri Station
- Train arrival time and delay information
- Estimated train arrival countdown
- Predicted railway gate closing and reopening times
- Streamlit dashboard
- CSV-based train schedule management

## Technologies Used

- Python
- Streamlit
- Pandas
- Requests
- Plotly
- RailRadar API

## Project Structure

```text
Railway-Crossing-Intelligence/
├── app.py
├── data/
│   └── train_schedule.csv
├── database/
├── prediction/
├── railway_api/
├── requirements.txt
├── test_train_api.py
└── verify_bichpuri_trains.py
```

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/divi1111/Railway-Crossing-Intelligence.git
```

2. Navigate to the project folder:

```bash
cd Railway-Crossing-Intelligence
```

3. Create and activate a virtual environment.

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root and add your RailRadar API key:

```env
RAILRADAR_API_KEY=your_api_key_here
```

6. Run the application:

```bash
streamlit run app.py
```

## Important Note

Gate closing and reopening times are estimates based on configurable timing assumptions and train information. They are not confirmed railway gate status or safety instructions.

Live train information depends on the availability and rate limits of the third-party RailRadar API.

## Future Improvements

- Improve arrival-time estimation
- Validate gate timing assumptions using real observations
- Improve dashboard design and usability
- Add more reliable train data sources

## Author

Developed as a Python and data-driven railway intelligence project.
