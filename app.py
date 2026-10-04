import os
from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/")
def index():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m?format=JSON&lang=EN&geo=EA21&unit=PC_ACT&s_adj=SA&age=TOTAL&sex=T&sinceTimePeriod=2026"

    labels = []
    values = []
    last_updated = "N/A"
    error_msg = None

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
            if t.startswith("2026"):
                idx = time_indices[t]
                val = (
                    raw_values.get(str(idx))
                    if str(idx) in raw_values
                    else raw_values.get(idx)
                )
                if val is not None:
                    labels.append(t)
                    values.append(float(val))

    except Exception as e:
        error_msg = f"Failed to fetch Eurostat data: {e}"
        print(error_msg)

    return render_template(
        "index.html",
        labels=labels,
        unemployment_values=values,
        error=error_msg,
        last_updated=last_updated,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5021))
    app.run(debug=True, host="0.0.0.0", port=port)