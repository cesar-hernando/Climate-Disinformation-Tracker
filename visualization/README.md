# Visualization Module

## Overview
The `visualization` module is responsible for creating interactive dashboards to visualize the results of claim analysis. It uses Dash to build dynamic and user-friendly visualizations based on the processed data.

## Features
- **Dynamic Dashboards**: Generate dashboards for specific claims and datasets.
- **Interactive Visualizations**: Includes time-series graphs, bubble charts, and user engagement metrics.
- **Customizable Layouts**: Modular design for easy extension and customization.

## File Structure
```
visualization/
├── app.py            # Entry point for creating and running Dash apps
├── callbacks.py      # Dash callbacks for interactivity
├── layout.py         # Layout definitions for Dash apps
├── figures.py        # Helper functions for creating visualizations
├── utils.py          # Utility functions for data processing
├── assets/           # Static assets (e.g., CSS files)
│   └── style.css     # Custom styles for Dash apps
```

## Key Components
### 1. `app.py`
- Contains the `create_app` function to dynamically generate Dash apps based on input parameters (e.g., filename, claim).
- Example usage:
  - Adjust filepath and claim accordingly in the file. Then run:
  ```bash
  python -m visualization.app
  ```

### 2. `callbacks.py`
- Defines all Dash callbacks to handle user interactions.
- Example: Updating graphs based on user input or selections.

### 3. `layout.py`
- Defines the layout structure of the Dash app.
- Example: Arranging graphs, filters, and other UI components.

### 4. `figures.py`
- Contains helper functions to generate visualizations (e.g., time-series plots, bubble charts).

### 5. `utils.py`
- Utility functions for data processing and transformation.
- Example: Formatting timestamps or filtering datasets.

### 6. `assets/style.css`
- Custom CSS for styling the Dash app.

## Usage
1. Import the `create_app` function from `app.py`.
2. Pass the required parameters (e.g., filename, claim) to generate a Dash app.
3. Run the app using `app.run()` or mount it to a FastAPI application using `WSGIMiddleware`.

## Example Integration with FastAPI
```python
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from visualization.app import create_app

app = FastAPI()

# Create and mount the Dash app
dash_app = create_app("data.csv", "Example Claim")
app.mount("/dashboard", WSGIMiddleware(dash_app.server))
```
