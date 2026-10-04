import os
from flask import Flask, render_template
import requests

app = Flask(__name__)


def fetch_labour_metric(dataset_code, params):
    query_params = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset_code}?format=JSON&lang=EN&geo=EA21&{query_params}&sinceTimePeriod=2024"

    labels = []
    values = []
    last_updated = "N/A"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        if "updated" in data:
            last_updated = data["updated"]

        dimensions = data.get("dimension", {})
        time_dim = dimensions.get("time", {}).get("category", {})
        time_indices = time_dim.get("index", {})

        sorted_times = sorted(time_indices.keys(), key=lambda t: time_indices[t])
        raw_values = data.get("value", {})

        for t in sorted_times:
            idx = time_indices[t]
            val = (
                raw_values.get(str(idx))
                if str(idx) in raw_values
                else raw_values.get(idx)
            )
            if val is not None:
                labels.append(t)
                values.append(float(val))

        return labels, values, last_updated, None
    except Exception as e:
        error_msg = f"Failed to fetch {dataset_code} ({query_params}): {e}"
        print(error_msg)
        return [], [], "N/A", error_msg


@app.route("/")
def index():
    # Harmonised Unemployment Rate (Monthly, Seasonally Adjusted)
    labels_un, un_vals, updated_un, err_un = fetch_labour_metric(
        "une_rt_m", {"unit": "PC_ACT", "s_adj": "SA", "age": "TOTAL", "sex": "T"}
    )

    return render_template(
        "index.html",
        labels=labels_un,
        unemployment_values=un_vals,
        error=err_un,
        last_updated=updated_un,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5021))
    app.run(debug=True, host="0.0.0.0", port=port)